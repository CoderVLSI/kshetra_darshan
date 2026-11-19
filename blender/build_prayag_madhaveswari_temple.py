"""Alopibagh precinct: aerial-derived massing, photographed gateways and Alopi darshan."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene
from deity_detail import Sculpture, garland, palette
from present_day_sites import anchor, box, cylinder, finish, linga, material, sphere
from surface_detail import add_stone_detail


def beam(name, start, end, radius, surface):
    delta = Vector(end) - Vector(start)
    post = cylinder(name, (Vector(start) + Vector(end)) / 2, radius, delta.length, surface)
    post.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return post


def mesh(name, vertices, faces, surface):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(surface)
    return obj


def taper(name, x, y, levels, surface):
    vertices = [(x+sx*w/2, y+sy*d/2, z) for z,w,d in levels
                for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    faces = [(3,2,1,0)]
    for i in range(len(levels)-1):
        k = 4*i
        for j in range(4):
            n = (j+1) % 4
            faces.append((k+j,k+n,k+n+4,k+j+4))
    n = len(vertices)
    faces.append(tuple(range(n-4,n)))
    return mesh(name, vertices, faces, surface)


def arch_band(name, y, spring, span, rise, width, surface):
    vertices = []
    for i in range(41):
        t = math.pi * i / 40
        for thick in [0, width]:
            vertices.append(((span/2+thick)*math.cos(t), y, spring+(rise+thick)*math.sin(t)))
    return mesh(name, vertices, [(i,i+2,i+3,i+1) for i in range(0,80,2)], surface)


def arch_cap(y, surface):
    vertices = []
    for i in range(41):
        t = math.pi * i / 40
        x, z = 3.2*math.cos(t), 2.83+2.62*math.sin(t)
        vertices.extend([(x,y-.59,z),(x,y+.59,z)])
    mesh('Alopi_Gateway_Arch_Crown',vertices,[(i,i+1,i+3,i+2) for i in range(0,80,2)],surface)


def gateway_name(y):
    # The gateway photograph shows the name in Hindi and Tamil. The lettering
    # is newly typeset, with the temple name transcribed from the photographed sign.
    surface = material('Alopi Gateway Lettering', (.85,.80,.65))
    nodes = surface.node_tree.nodes
    paint = nodes.new('ShaderNodeTexImage')
    paint.image = bpy.data.images.load(str(Path(__file__).parent/'references/alopi_gateway_name.png'))
    surface.diffuse_color = (.52,.1,.09,1)
    surface.surface_render_method = 'DITHERED'
    shader = nodes.get('Principled BSDF')
    surface.node_tree.links.new(paint.outputs['Color'], shader.inputs['Base Color'])
    surface.node_tree.links.new(paint.outputs['Alpha'], shader.inputs['Alpha'])
    obj = mesh('Alopi_Bilingual_Gateway_Name-ornamentdetail',
               [(-2.12,y,3.35),(2.12,y,3.35),(2.12,y,4.02),(-2.12,y,4.02)],
               [(0,1,2,3)], surface)
    uv = obj.data.uv_layers.new().data
    for i, point in enumerate([(0,0),(1,0),(1,1),(0,1)]):
        uv[i].uv = point


def lion(name, x, y, floor, sun, shadow):
    s = Sculpture()
    s.materials.extend([sun, shadow])
    sun, shadow = 0, 1
    s.ellipsoid((0,.06,.23),(.19,.30,.23),sun)
    s.ellipsoid((0,-.12,.48),(.23,.20,.25),shadow)
    s.ellipsoid((0,-.23,.53),(.146,.135,.15),sun)
    s.ellipsoid((0,-.327,.477),(.105,.075,.055),sun)
    for side in [-1,1]:
        s.ellipsoid((side*.102,-.219,.645),(.047,.038,.053),sun)
        s.ellipsoid((side*.054,-.343,.55),(.019,.012,.014),shadow)
        s.tube([(side*.098,-.11,.33),(side*.118,-.26,.07)],.067,sun,12)
        s.ellipsoid((side*.115,-.304,.052),(.073,.113,.053),sun)
    s.tube([(.09,.27,.05),(.26,.31,.046),(.30,.09,.047)],.031,shadow,10)
    s.finish(name,(x,y,floor))


def shikhara(pink, trim, plaster, brass):
    # Narrow smooth taper and corner kiosks are visible from the Alopibagh street.
    for side in [-1,1]:
        box('Tower_Bhadra_Wall',(side*4.48,.35,6.0),(.31,7.7,4.72),pink,.03)
        for py in [-3.33,.35,4.03]:
            box('Tower_Panel_Stile',(side*4.66,py,6.0),(.15,.23,4.38),trim,.023)
        for px in [-4.26,0,4.26]:
            box('Tower_Front_Panel_Stile',(px,.35+side*3.8,6.05),(.21,.15,4.35),trim,.02)
    for py in [-3.31,4.01]:
        box('Tower_Panel_Wall',(0,py,6.0),(9.0,.26,4.75),pink,.033)
    for z,sx,sy,sz,mat in [(8.22,9.2,7.76,.25,trim),(8.49,9.7,8.12,.31,pink),(8.72,9.28,7.92,.16,trim)]:
        box('Tower_Cornice',(0,.35,z),(sx,sy,sz),mat,.023)
    taper('Alopi_Smooth_Spire',0,.35,[(8.8,9,7.65),(13.75,4.55,3.86),
                                      (17.5,1.16,1.03),(18.27,.47,.43)],plaster)
    for px in [-4.44,4.44]:
        for py in [-3.34,4.03]:
            cylinder('Spire_Corner_Kiosk_Base',(px,py,8.92),.34,.13,trim)
            for j in range(4):
                angle = math.pi*j/2
                cylinder('Spire_Corner_Kiosk_Post',(px+.22*math.cos(angle),py+.22*math.sin(angle),9.26),
                         .041,.57,pink)
            taper('Spire_Corner_Kiosk_Roof',px,py,[(9.51,.64,.64),(9.95,.05,.05)],trim)
    for side in [-1,1]:
        for px,py in [(side*2.72,.35),(0,.35+side*2.39)]:
            box('Spire_Miniature_Edicule',(px,py,12.77),(.78,.74,1.02),pink,.035)
            taper('Spire_Miniature_Edicule_Cap',px,py,[(13.26,.86,.80),(14.0,.06,.06)],trim)
    for i,radius in enumerate([.30,.235,.197,.151,.099,.055]):
        sphere('Spire_Finial',(0,.35,18.24+i*.175),(radius,radius,radius*1.21),brass,16)
    beam('Spire_Pennant_Pole',(0,.35,18.77),(0,.35,20.1),.023,brass)
    mesh('Spire_Saffron_Pennant',[(0,.35,20.08),(.96,.54,19.84),(.11,.35,19.28)],
         [(0,2,1),(0,1,2)],trim)


def cradle(z, silver, steel, stone, plum, cloth, dark, rng):
    anchor('Deity_Madhaveswari',(0,.24,z+1.44))
    anchor('Alopi_Cradle_Landing',(0,-2.58,z+.055))
    anchor('Sanctum_Lamp_Position',(0,-1.52,z+2.30))
    cylinder('Cradle_Round_Platform',(0,.24,z+.255),1.77,.51,stone)
    cylinder('Cradle_Silver_Plate',(0,.24,z+.54),1.75,.095,silver)
    cylinder('Kund_Dark_Recess',(0,.24,z+.601),.49,.018,dark)
    s = Sculpture()
    p = palette(s)
    w, d = .94, .74
    for sx in [-1,1]:
        for sy in [-1,1]:
            x,y = sx*w/2, .24+sy*d/2
            cylinder('Cradle_Corner_Silver_Post',(x,y,z+.92),.062,.61,silver)
            sphere('Cradle_Corner_Cap',(x,y,z+1.255),(.069,.069,.105),silver,20)
            beam('Cradle_Suspension',(x,y,z+1.24),(sx*.21,.24+sy*.14,z+2.84),.014,steel)
            garland_points = [(x+.09*math.cos(i*.8),y-.05+.075*math.sin(i*.8),.87+i*.026)
                              for i in range(15)]
            for i,q in enumerate(garland_points):
                tint = p['yellow'] if i%3 else p['orange']
                s.ellipsoid(q,(.041,.039,.045),tint,12,8)
                for petal in range(6):
                    a = math.tau*petal/6
                    s.ellipsoid((q[0]+.034*math.cos(a),q[1]-.018,q[2]+.034*math.sin(a)),
                                (.021,.023,.021),tint,8,6)
    box('Cradle_Wood_Base',(0,.24,z+.77),(w+.09,d+.09,.10),silver,.025)
    for sy in [-1,1]:
        y = .24+sy*d/2
        box('Cradle_Long_Embossed_Side',(0,y,z+1.02),(w,.05,.34),silver,.017)
        for x in [-.36,-.24,-.12,0,.12,.24,.36]:
            for detail_z in [.916,1.021,1.126]:
                s.rosette((x,y+sy*.028,detail_z),.045,p['silver'],p['silver'],7)
    for sx in [-1,1]:
        box('Cradle_Short_Embossed_End',(sx*w/2,.24,z+1.02),(.045,d,.34),silver,.018)
    box('Cradle_Inner_Fold',(0,.24,z+.86),(.63,.48,.15),cloth,.053)
    for i in range(9):
        x = (i-4)*.055
        box('Cradle_Suspended_Cloth_Fold',(x,.12+.045*math.cos(i*2.14),z+1.83),
            (.071,.095,.73+.06*math.sin(i)),plum,.029)
        for dz in [1.50,1.65,1.96]:
            box('Cradle_Silk_Brocade',(x,.067+.045*math.cos(i*2.14),z+dz),(.071,.012,.018),silver,.005)
    for sx in [-1,1]:
        for sy in [-1,1]:
            beam('Cradle_Cord_Tie',(sx*.21,.24+sy*.14,z+2.84),(0,.24,z+2.96),.014,steel)
    beam('Cradle_Suspension_Hook',(0,.24,z+2.96),(0,.24,z+3.78),.024,steel)
    for i in range(76):
        a, r = rng.random()*math.tau, rng.uniform(.56,1.66)
        s.ellipsoid((r*math.cos(a),.24+r*math.sin(a),.597),
                    (.017,.028,.009),p['yellow'] if i%2 else p['red'],8,6)
    s.finish('Alopi_Marigold_Offerings-renderonly',(0,0,z))
    # Stainless steel rail surrounds three sides of the open darshan approach.
    for px in [-1.96,1.96]:
        for py in [-1.15,.23,1.61]:
            cylinder('Kund_Guard_Post',(px,py,z+.54),.036,1.08,steel)
        for height in [.33,.64,1.08]:
            beam('Kund_Side_Guard',(px,-1.15,z+height),(px,1.91,z+height),.031,steel)
    for height in [.33,.64,1.08]:
        beam('Kund_Back_Guard',(-1.96,1.91,z+height),(1.96,1.91,z+height),.031,steel)


def shiva_study(position):
    # The district lists both forms but does not photograph or locate the installed image.
    s = Sculpture()
    p = palette(s)
    stone = p['black']
    s.ellipsoid((0,.018,.44),(.225,.110,.298),stone)
    s.ellipsoid((0,-.025,.808),(.114,.102,.14),stone)
    s.ellipsoid((0,-.118,.792),(.027,.027,.039),stone,24,14)
    s.ellipsoid((0,.005,.949),(.079,.073,.09),stone)
    for side in [-1,1]:
        s.ellipsoid((side*.104,-.032,.796),(.025,.034,.047),stone)
        s.tube([(side*.022,-.123,.827),(side*.051,-.12,.834),(side*.081,-.103,.827)],
               .01,stone,12)
        s.tube([(side*.16,.008,.58),(side*.23,-.026,.42),(side*.16,-.12,.31)],.052,stone,10)
        s.ellipsoid((side*.156,-.118,.307),(.052,.043,.057),stone)
        s.tube([(side*.10,0,.26),(side*.20,-.075,.13),(side*.063,-.155,.095)],.078,stone,12)
        s.ellipsoid((side*.064,-.148,.089),(.066,.05,.047),stone)
    for dz in [.856,.868,.88]:
        s.tube([(-.048,-.116,dz),(0,-.126,dz),(.048,-.116,dz)],.0036,p['white'],8)
    s.tube([(.28,-.038,.13),(.28,-.038,.91)],.012,p['silver'])
    for side in [-1,0,1]:
        s.tube([(.28,-.038,.85),(.28+side*.05,-.038,.897),(.28+side*.068,-.038,.967)],
               .01,p['silver'],8)
    garland(s,p,.153,.57,.22,-.106,24)
    s.finish('Shiva_Iconographic_Study',position)


def build():
    clear_scene()
    rng = random.Random(205)
    pink = material('Alopi Limewash Pink',(.54,.215,.21))
    rose = material('Alopi Deep Rose',(.45,.082,.090))
    orange = material('Alopi Entrance Vermilion',(.81,.21,.062))
    plaster = material('Alopi Spire Limewash',(.64,.38,.32))
    roof = material('Alopi Covered Court Moss Green',(.11,.21,.17),.54)
    pale = material('Alopi Warm White Plaster',(.63,.55,.46))
    stone = material('Alopi Grey Paving',(.19,.20,.17))
    floor_surface = material('Alopi Stone Floor',(.30,.31,.27))
    slate = material('Alopi Road Asphalt',(.098,.100,.088))
    iron = material('Alopi Painted Iron',(.17,.033,.038),.5,.4)
    brass = material('Alopi Lion Ochre',(.73,.43,.16),.65,.08)
    silver = material('Alopi Engraved Silver',(.66,.67,.66),.29,.46)
    steel = material('Alopi Polished Guard Rail',(.68,.72,.70),.27,.62)
    purple = material('Cradle Purple Brocade',(.27,.035,.19),.72)
    cloth = material('Alopi Red Cloth',(.63,.043,.064),.86)
    dark = material('Alopi Dark Stone',(.047,.052,.048))
    leaves = [material('Alopibagh Leaf Shade '+str(i),c) for i,c in enumerate(
        [(.11,.21,.079),(.15,.25,.079),(.18,.29,.09),(.095,.17,.067)])]
    bark = material('Alopibagh Tree Bark',(.159,.099,.06))
    for surface in [stone,floor_surface]:
        shader = surface.node_tree.nodes.get('Principled BSDF')
        add_stone_detail(surface, shader, tuple(shader.inputs['Base Color'].default_value))

    box('Ground_Urban_Terrain',(0,0,-.32),(113,103,.62),stone)
    box('Alopibagh_Road_NW',(14.6,2,-.01),(8.1,96,.06),slate)
    box('Alopibagh_Road_NE',(-10,-33.1,-.008),(53,8.6,.058),slate)
    box('Alopi_Entry_Paving',(-6,-19,-.08),(31.2,24,.23),floor_surface,.015)
    box('Alopi_Main_Court',(-6,-8,-.056),(33,16,.19),stone,.018)
    box('Alopi_Return_Court',(-13,8,-.054),(22,18,.18),stone,.018)
    for z,dim in [(.015,(22,13.6,.05)),(.097,(21.6,13.1,.13)),(.226,(20.8,12.6,.17))]:
        box('House_Temple_Plinth',(-3.7,1.1,z),dim,pink,.025)
    floor = .44
    box('Alopi_Sanctuary_Floor',(-3.8,1.2,.351),(20.6,12.7,.178),floor_surface,.007)
    for i in range(3):
        box('Alopi_Front_Steps',(0,-6.18+i*.40,.055+i*.060),(4.8,.40,.118+i*.12),stone,.011)
    # Local -Y is the inner darshan entrance; the surviving photos show the outer gate
    # as a separately decorated, broader opening.
    gate_y = -25.3
    for x in [-3.18,3.18]:
        box('Alopi_Gateway_Plinth',(x,gate_y,.20),(1.20,1.44,.36),rose,.046)
        box('Alopi_Gateway_Solid_Pier',(x,gate_y,1.99),(.98,1.16,3.69),rose,.041)
        for h, span, surf in [(2.61,1.28,pink),(2.76,1.35,plaster),(3.84,1.26,pink),
                              (4.09,1.11,rose)]:
            box('Alopi_Gateway_Pier_Moulding',(x,gate_y,h),(span,1.33,.17),surf,.024)
    for dep in [-.59,.59]:
        arch_band('Alopi_Gateway_Rose_Arch',gate_y+dep,2.83,5.62,2.23,.39,rose)
        arch_band('Alopi_Gateway_Pink_Moulding',gate_y+dep-.025,2.86,5.59,2.08,.27,pink)
        arch_band('Alopi_Gateway_Pale_Moulding',gate_y+dep-.044,2.87,5.59,1.98,.12,plaster)
    arch_cap(gate_y,rose)
    vertices = [(-2.78,gate_y-.60,3.295),(2.78,gate_y-.60,3.295)]
    vertices += [(2.78*math.cos(i*math.pi/32),gate_y-.60,3.295+1.64*math.sin(i*math.pi/32))
                 for i in range(1,32)]
    mesh('Alopi_Arch_Tympanum',vertices,[tuple(range(len(vertices)))],rose)
    gateway_name(gate_y-.612)
    for x in [-5.01,5.01]:
        box('Alopi_Lion_Pier',(x,gate_y-.33,.51),(.98,1.11,1.02),rose,.036)
        lion('Alopi_Entry_Lion',x,gate_y-.46,1.04,brass,pink)
    for x,w in [(-12.95,18.3),(7.19,6.9)]:
        box('North_Compound_Wall',(x,gate_y,1.13),(w,.33,2.26),pink,.024)
        box('North_Compound_Wall_Coping',(x,gate_y,2.29),(w,.49,.19),rose,.021)
    for x in [-22.0,10.68]:
        box('Side_Compound_Wall',(x,1.05,1.15),(.38,53,2.3),pink,.022)
        box('Side_Compound_Wall_Coping',(x,1.05,2.37),(.49,53,.19),rose,.018)
    box('Far_Compound_Return',(-5.68,27.5,1.10),(33,.38,2.2),pink,.02)

    # Light metal-covered forecourt and the flat-roofed sanctuary ranges seen from above.
    for px in [-5.5,5.5]:
        for py in [-20.8,-16.7,-12.6,-8.4]:
            box('Forecourt_Column',(px,py,1.83),(.26,.26,3.56),iron,.022)
            box('Forecourt_Column_Platform',(px,py,.25),(.44,.44,.43),pale,.021)
    taper('Alopi_Covered_Forecourt',0,-14.54,[(3.57,11.92,13.60),(3.91,11.72,13.3),
                                            (4.22,7.84,12.74)],roof)
    for i in range(34):
        box('Forecourt_Roof_Rib',(0,-20.92+i*.382,4.222),(7.86,.039,.023),dark)

    for y in [-5.17,7.45]:
        if y < 0:
            for x,w in [(-8.42,8.6),(5.16,6.05)]:
                box('Sanctuary_Front_Wall',(x,y,2.34),(w,.50,3.82),orange,.022)
            box('Sanctuary_Entrance_Lintel',(0,y,3.98),(5.22,.51,.65),orange,.029)
        else:
            box('Sanctuary_Rear_Wall',(-3.84,y,2.37),(20.1,.48,3.84),pink,.028)
    for x in [-13.85,6.12]:
        box('Sanctuary_Long_Wall',(x,1.13,2.35),(.44,12.55,3.83),pink,.022)
    box('Sanctuary_Side_Bay_Front',(6.7,-5.17,2.35),(1.39,.49,3.82),orange,.018)
    for z,w,d,h,mat in [(4.31,20.8,13.21,.20,rose),(4.53,21.04,13.42,.26,pink),
                         (4.76,21.16,13.6,.18,plaster)]:
        box('Sanctuary_Continuous_Flat_Roof',(-3.72,1.17,z),(w,d,h),mat,.025)
    for x in [-2.54,2.33]:
        box('Inner_Entry_Pilaster',(x,-5.44,1.9),(.53,.24,2.93),orange,.037)
        box('Inner_Entry_Geometric_Border',(x,-5.573,2.10),(.074,.02,2.53),roof,.01)
    arch_band('Inner_Scalloped_Entry_Surround-ornamentdetail',-5.48,2.45,4.25,.90,.155,plaster)
    for i in range(9):
        a = math.pi*i/8
        x,z = 2.10*math.cos(a),2.46+.92*math.sin(a)
        sphere('Inner_Entry_Trim_Medallion',(x,-5.529,z),(.092,.032,.092),roof,12)
    for x in [-2.81,2.68]:
        box('Inner_Lion_Stone_Base',(x,-5.73,.19),(.56,.77,.25),pink,.023)
        lion('Alopi_Sanctuary_Lion',x,-5.76,.32,pale,brass)
    for x in [-7.5,3.65]:
        box('Entry_Grille_Frame',(x,-5.48,2.05),(1.36,.09,2.74),rose,.018)
        for i in range(13):
            box('Entry_Grille_Bar',(x-.61+i*.103,-5.54,2.05),(.017,.054,2.68),iron)
    shikhara(pink,rose,plaster,brass)

    # A light stone-lined inner hall, with room to approach and circulate.
    for x in [-4.7,4.7]:
        box('Darshan_Interior_Wall',(x,1.4,2.22),(.28,9.4,3.58),pale,.022)
    box('Darshan_Back_Wall',(0,6.04,2.22),(9.6,.30,3.58),pale,.02)
    for x in [-4.54,4.54]:
        for y in [-2.1,.71,3.52,5.86]:
            box('Darshan_Interior_Pilaster',(x,y,2.08),(.25,.32,3.30),plaster,.025)
    cradle(floor,silver,steel,stone,purple,cloth,dark,rng)
    for sx,name in [(-3.38,'Alopi_Shiva_Image'),(3.38,'Alopi_Shiva_Lingam')]:
        py = 2.94
        box(name+'_Base',(sx,py,floor+.22),(1.43,1.04,.44),stone,.025)
        box(name+'_Back',(sx,py+.42,floor+1.04),(1.34,.19,1.49),plaster,.023)
        for x in [sx-.64,sx+.64]:
            box(name+'_Frame',(x,py-.08,floor+1.11),(.17,.65,1.48),pink,.023)
        box(name+'_Canopy',(sx,py-.08,floor+1.92),(1.45,.91,.17),rose,.03)
        anchor(name+'_Anchor',(sx,py-.20,floor+1.14))
        anchor(name+'_Landing',(sx,py-1.83,floor+.055))
        if sx < 0:
            shiva_study((sx,py-.12,floor+.445))
        else:
            linga(name+'_Linga',(sx,py-.08,floor+.442),.78,dark)

    box('Alopi_Side_Service_Range',(-18.9,13.1,1.68),(5.1,17.1,3.36),pink,.025)
    box('Alopi_Side_Service_Range_Roof',(-18.9,13.1,3.49),(5.7,17.7,.32),plaster,.018)
    for x,y,h in [(-15,-14,8.2),(-15.5,-2,7.7),(-18.8,6.4,7.25),(-10.8,20,7.7),(4.1,19.2,8.5)]:
        beam('Alopi_Court_Tree_Trunk',(x,y,.03),(x+.19,y,h*.77),.31,bark)
        for i in range(28):
            a,r = rng.random()*math.tau,rng.uniform(.12,3.05)
            zz = h+rng.uniform(-2.25,.75)-r*.26
            sphere('Alopi_Court_Canopy-renderonly',(x+r*math.cos(a),y+r*math.sin(a),zz),
                   (rng.uniform(.67,1.67),rng.uniform(.83,1.66),rng.uniform(.69,1.45)),rng.choice(leaves),14)
    for i in range(13):
        for x,y in [(24.0,-27+i*5.0),(-30+i*4.6,-40.3)]:
            h = rng.uniform(3.55,8.0)
            w = rng.uniform(3.7,4.55)
            box('Alopibagh_Urban_Context',(x,y,h/2),(w,4.31,h),
                rng.choice([pale,plaster,stone]),.028)
            box('Alopibagh_Urban_Roof',(x,y,h+.09),(w+.16,4.48,.19),stone,.019)

    anchor('Spawn_Point',(0,-30.0,.09))
    anchor('Arrival_Facing',(0,-21.4,.09))
    anchor('Alopi_Outer_Gate_Reference',(0,-25.93,3.71))
    anchor('Alopi_Outer_Gate_Landing',(0,-28.35,.09))
    anchor('Alopi_Inner_Facade_Reference',(0,-5.58,2.18))
    anchor('Alopi_Inner_Facade_Landing',(0,-9.45,.09))
    # Set the modeled court and street to the approximate bearing of the aerial footprint.
    rotation = Matrix.Rotation(math.radians(150),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world = rotation @ obj.matrix_world


if __name__ == '__main__':
    build()
    if not globals().get('DEFER_GLB_EXPORT', False):
        finish('prayag_madhaveswari')
