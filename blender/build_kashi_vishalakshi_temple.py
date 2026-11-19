"""Mir Ghat's Vishalakshi temple, based on the VKM field survey and ground photographs."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene
from deity_detail import Sculpture, garland, palette
from present_day_sites import anchor, box, cylinder, finish, linga, material, sphere
from surface_detail import add_stone_detail, prepare_scene


def skin(name, vertices, faces, surface):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(surface)
    return obj


def sign(name, words, x, y, z, size, surface):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = words
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.space_line = .86
    curve.size = size
    curve.extrude = .001
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = (x,y,z)
    obj.rotation_euler.x = math.pi/2
    curve.materials.append(surface)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')


def wall_inscription(y):
    surface = material('Vishalakshi original Tamil lettering', (.28,.07,.03))
    shader = surface.node_tree.nodes.get('Principled BSDF')
    tex = surface.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str(Path(__file__).parent/'references/kashi_tamil_wall_lettering.png'))
    surface.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    surface.node_tree.links.new(tex.outputs['Alpha'], shader.inputs['Alpha'])
    surface.surface_render_method = 'DITHERED'
    obj = skin('Nagarathar_Tamil_Wall_Inscription-ornamentdetail',
               [(2.27,y,.71),(4.80,y,.71),(4.80,y,2.26),(2.27,y,2.26)],[(0,1,2,3)],surface)
    uv = obj.data.uv_layers.new().data
    for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):
        uv[i].uv = p


def add_lotus(s, x, y, z, radius, color, rim, n=8):
    for i in range(n):
        a = i*math.tau/n
        dx, dz = math.cos(a), math.sin(a)
        s.tube([(x,y,z),(x+.48*radius*dx,y-.018,z+.48*radius*dz),
                (x+radius*dx,y,z+radius*dz)], radius*.14,color,8)
    s.ellipsoid((x,y-.025,z),(radius*.23,.021,radius*.23),rim,12,8)


def animal(name, position, color, form, scale=1, trim=None, rotation=0.0):
    s = Sculpture()
    p = palette(s)
    s.materials.append(color)
    col = len(s.materials)-1
    contrast = col
    if trim:
        s.materials.append(trim)
        contrast = len(s.materials)-1
    s.ellipsoid((0,.05,.20),(.185,.345,.157),col)
    if form == 'elephant':
        for sx in [-1,1]:
            for sy in [-1,1]:
                s.tube([(sx*.110,sy*.212,.245),(sx*.103,sy*.244,.035)],.048,col,9)
            s.ellipsoid((sx*.104,-.243,.301),(.08,.041,.086),col)
        s.ellipsoid((0,-.234,.302),(.114,.108,.113),col)
        s.tube([(0,-.294,.3),(0,-.390,.225),(0,-.399,.361),(0,-.353,.432)],.035,col,9)
        for sx in [-1,1]:
            s.tube([(sx*.064,-.298,.275),(sx*.074,-.369,.217)],.014,p['white'],8)
    else:
        s.ellipsoid((0,-.17,.326),(.176,.162,.176),contrast)
        s.ellipsoid((0,-.277,.366),(.114,.100,.123),col)
        for sx in [-1,1]:
            s.ellipsoid((sx*.086,-.28,.445),(.032,.029,.040),contrast)
            s.ellipsoid((sx*.046,-.367,.375),(.014,.011,.012),p['black'])
            s.ellipsoid((sx*.112,-.287,.051),(.074,.143,.046),col)
            if form=='nandi':
                s.tube([(sx*.075,-.295,.405),(sx*.082,-.306,.491),(sx*.057,-.296,.524)],.022,p['white'],9)
            else:
                s.tube([(sx*.102,-.155,.274),(sx*.107,-.258,.073)],.056,col,10)
        s.ellipsoid((0,-.36,.315),(.084,.051,.055),col)
        if form=='lion':
            s.tube([(-.056,-.402,.30),(0,-.418,.286),(.056,-.402,.30)],.009,p['black'],8)
            for i in range(17):
                a = i*math.tau/17
                s.tube([(.11*math.cos(a),-.277,.36+.118*math.sin(a)),
                        (.173*math.cos(a),-.200,.35+.177*math.sin(a))],.018,contrast,8)
    s.tube([(.143,.25,.113),(.249,.33,.079),(.288,.13,.077)],.024,col,9)
    obj = s.finish(name,position,scale)
    obj.rotation_euler.z = rotation


def figure(name, position, form, scale=1, relief=False):
    s = Sculpture()
    p = palette(s)
    dark = p['black']
    skin_color = p['white'] if relief or form=='acharya' else dark
    dress = p['orange'] if form=='acharya' else p['gold'] if relief else p['red']
    s.ellipsoid((0,.022,.55),(.163,.078,.256),dress)
    s.ellipsoid((0,.023,.727),(.145,.074,.142),skin_color)
    s.ellipsoid((0,-.015,.938),(.105,.087,.129),skin_color)
    s.ellipsoid((0,.006,1.073),(.066,.060,.105),p['gold'] if relief or form=='devi' else dark)
    if form=='ganesha':
        s.ellipsoid((0,-.014,.940),(.135,.103,.118),skin_color)
        for side in [-1,1]:
            s.ellipsoid((side*.123,.003,.940),(.072,.048,.096),skin_color)
        s.tube([(0,-.10,.94),(0,-.155,.845),(.075,-.148,.805),(.102,-.12,.836)],.044,skin_color,10)
    else:
        s.ellipsoid((0,-.101,.924),(.018,.021,.026),skin_color)
    seated = form in ['acharya','ganesha','seated']
    for side in [-1,1]:
        s.tube([(side*.116,.007,.775),(side*.187,-.015,.646),(side*.15,-.071,.535)],
               .039,skin_color,10)
        s.ellipsoid((side*.145,-.076,.535),(.035,.031,.044),skin_color)
        if seated:
            s.tube([(side*.095,0,.37),(side*.18,-.018,.206),(side*.035,-.092,.159)],.073,dress,12)
        else:
            s.tube([(side*.08,.018,.431),(side*.063,.023,.20),(side*.064,-.035,.10)],.055,dress,12)
            s.ellipsoid((side*.065,-.058,.082),(.047,.060,.040),skin_color)
        if relief and form in ['ganesha','devi']:
            s.tube([(side*.116,.024,.8),(side*.238,.006,.820),(side*.224,-.028,.962)],.029,skin_color,9)
        if form!='ganesha':
            s.ellipsoid((side*.037,-.09,.955),(.024,.014,.013),dark if relief else p['white'],16,8)
    if form=='bhairava':
        s.tube([(.225,-.026,.101),(.225,-.026,1.06)],.014,p['silver'])
        for side in [-1,0,1]:
            s.tube([(.225,-.026,.99),(.225+side*.057,-.026,1.064),
                    (.225+side*.065,-.026,1.119)],.01,p['silver'],8)
    if form=='acharya':
        s.tube([(-.226,-.04,.097),(-.226,-.04,1.03)],.013,p['gold'],10)
    if not relief:
        garland(s,p,.137,.786,.245,-.102,31)
    return s.finish(name,position,scale)


def decorated_darshan(position):
    s = Sculpture()
    p = palette(s)
    s.ellipsoid((0,.022,.75),(.281,.131,.479),p['red'],40,28)
    s.ellipsoid((0,-.069,1.176),(.138,.106,.118),p['black'],42,26)
    # The flower-covered mantle continues to the platform in the field photo.
    for fold in range(13):
        t=(fold-6)/6
        s.tube([(t*.19,-.041,.81),(t*.225,-.101,.48),(t*.29,-.173,.19),
                (t*.36,-.277,.044)],.044,p['red'],12)
        s.tube([(t*.29,-.208,.19),(t*.36,-.316,.049)],
               .007,p['gold'] if fold%3==0 else p['orange'],8)
    for side in [-1,1]:
        s.ellipsoid((side*.054,-.164,1.195),(.046,.015,.028),p['eye'],24,12)
        s.ellipsoid((side*.054,-.178,1.195),(.018,.009,.018),p['black'],20,10)
        s.tube([(side*.082,-.163,1.24),(side*.059,-.172,1.250),(side*.026,-.165,1.234)],
               .013,p['orange'],10)
    s.ellipsoid((0,-.175,1.242),(.014,.014,.016),p['red'])
    for i in range(5):
        z=1.276+i*.066
        s.ellipsoid((0,-.002,z),(.148-i*.017,.095-i*.009,.058),p['red'] if i%2==0 else p['white'],30,14)
        for n in range(12):
            a=n*math.tau/12
            s.ellipsoid((.134*math.cos(a)*(1-i*.095),-.008+.082*math.sin(a),z),
                        (.029,.028,.025),p['red'] if i%2==0 else p['white'],9,7)
    for j in range(5):
        garland(s,p,.212+j*.036,1.22-j*.031,.40+j*.064,-.15+j*.006,56)
    for side in [-1,1]:
        for i in range(15):
            a=i/14
            s.ellipsoid((side*(.31-.14*a),-.11,.90-a*.50),
                        (.045,.037,.081),p['green'],16,10)
    for row in range(3):
        s.tube([(.19*math.cos(a),-.20,.99+(.29+row*.043)*math.sin(a))
                for a in [math.pi+i*math.pi/32 for i in range(33)]],.010,p['gold'],9)
        add_lotus(s,0,-.215,.69-row*.024,.062,p['gold'],p['red'])
    s.finish('Vishalakshi_Clothed_Darshan-renderonly',position)


def portal(facade_y,m):
    gold,red,blue,leaf,plaster = [m[k] for k in ('gold','red','blue','leaf','plaster')]
    for sign_x in [-1,1]:
        x = sign_x*1.10
        for z,w,h,surf in [( .52,.49,.28,blue),(.84,.37,.41,blue),(1.28,.34,.47,m['indigo']),
                            (1.85,.29,.67,gold),(2.24,.40,.18,red),(2.44,.42,.24,red)]:
            box('Carved_Portal_Stile',(x,facade_y-.19,z),(w,.26,h),surf,.035)
        for dx in [-.08,0,.08]:
            box('Portal_Stile_Gold_Reed',(x+dx,facade_y-.337,1.84),(.026,.035,.61),gold,.012)
        box('Portal_Gilt_Door_Jamb',(sign_x*.87,facade_y-.061,1.43),(.14,.20,2.19),gold,.02)
        box('Portal_Lion_Shelf',(sign_x*1.80,facade_y-.20,1.11),(.84,.50,.14),leaf,.03)
        box('Portal_Lion_Console',(sign_x*1.80,facade_y-.15,.95),(.47,.34,.18),leaf,.045)
        animal('Lane_Guardian_Lion-renderonly',(sign_x*1.80,facade_y-.23,1.19),gold,'lion',1.15,
               m['bronze'],sign_x*math.radians(-32))
    box('Portal_Gilt_Lintel',(0,facade_y-.090,2.57),(1.88,.21,.16),gold,.021)
    box('Portal_Blue_Polychrome_Field',(0,facade_y-.11,3.18),(2.33,.24,1.21),blue,.019)
    for x in [-1.29,1.29]:
        box('Portal_Floral_Outer_Border',(x,facade_y-.21,3.17),(.23,.22,1.37),leaf,.016)
    box('Portal_Floral_Top_Border',(0,facade_y-.20,3.86),(2.81,.22,.22),leaf,.013)
    for z,w,h,surf in [(3.95,2.93,.14,red),(4.08,3.03,.12,gold),(4.17,3.15,.11,m['indigo'])]:
        box('Portal_Overdoor_Cornice',(0,facade_y-.224,z),(w,.44,h),surf,.016)

    s=Sculpture()
    for surf in [gold,red,leaf,m['leaf_light'],plaster,m['blue_light']]:
        s.materials.append(surf)
    gold_i,red_i,leaf_i,light_i,white_i,blue_i=range(6)
    front=facade_y-.253
    for radius in range(5):
        points=[]
        for i in range(65):
            t=-1+2*i/64
            z=2.89 + .57*math.cos(t*math.pi/2)**1.13 + .075*math.cos(t*math.pi*3)
            points.append((t*(.995+radius*.028),front-.035,z+radius*.043))
        s.tube(points,.022,gold_i,10)
    for x in [-1.27,1.27]:
        for i in range(7):
            add_lotus(s,x,front-.06,2.65+i*.16,.077,light_i,red_i)
    for i in range(13):
        add_lotus(s,-1.2+i*.20,front-.06,3.85,.081,light_i,red_i)
    for side in [-1,1]:
        s.tube([(side*.64,front,3.20),(side*.85,front-.034,3.42),(side*.94,front,3.74)],.027,light_i)
        for i in range(5):
            a=.45+i*.52
            x=side*(.70+.096*i)
            z=3.43+.105*math.sin(a)
            s.tube([(x,front,z),(x+side*.071,front-.043,z+.106)],.046,leaf_i,10)
        for i in range(3):
            s.ellipsoid((side*(.74+i*.108),front-.04,3.57+i*.056),(.041,.039,.064),red_i)
    for x in [-.91,-.44,0,.44,.91]:
        z=2.96+.54*(1-abs(x))**1.1
        s.ellipsoid((x,front-.099,z+.12),(.054,.038,.079),red_i,16,10)
        add_lotus(s,x,front-.14,z,.071,red_i,gold_i,4)
    for i in range(29):
        s.ellipsoid((-1.48+i*.105,front-.15,4.072),(.035,.031,.031),blue_i if i%2 else red_i,12,8)
    s.finish('Portal_Floral_and_Gilded_Relief-renderonly')
    box('Gajalakshmi_Relief_Plinth',(0,facade_y-.285,2.76),(.81,.18,.092),plaster,.016)
    figure('Door_Lintel_Gajalakshmi-renderonly',(0,facade_y-.34,2.77),'seated',.51,True)
    for side in [-1,1]:
        animal('Gajalakshmi_White_Elephant-renderonly',(side*.27,facade_y-.335,2.80),
               plaster,'elephant',.66,rotation=side*math.radians(-49))

    plaque=box('Nagarathar_Stone_Plaque',(3.36,facade_y-.019,2.56),(1.63,.055,.56),m['stone'],.018)
    plaque['reference_note']='Photo documents this plaque. Its full lettering is untranscribed.'
    box('Earlier_Tamil_Plaque',(-2.43,facade_y-.016,2.66),(.92,.055,.74),m['indigo'],.016)
    wall_inscription(facade_y-.040)

def gateway_superstructure(m):
    blue,red,gold,stone = [m[k] for k in ('blue','red','gold','stone_light')]
    y=.035
    box('Vishalakshi_Gopura_Deep_Blue_Field',(0,y,5.16),(6.9,.46,1.91),blue,.034)
    box('Vishalakshi_English_Name_Panel',(0,y-.255,4.59),(4.04,.065,.53),stone,.017)
    sign('English_Gate_Inscription-ornamentdetail','THE GATE OF VISALAKSHI DEVI\nVARANASI',
         0,y-.299,4.59,.202,m['ink'])
    for x in [-1.91,-.73,.73,1.91]:
        for z in [4.92,6.06]:
            box('Gopura_Column_Trim',(x,y-.284,z),(.23,.26,.13),gold,.017)
        box('Gopura_Column',(x,y-.282,5.51),(.13,.20,1.04),red,.021)
    for x,identity in [(-1.26,'attendant'),(0,'devi'),(1.26,'attendant')]:
        figure('Gopura_Central_'+identity+'-renderonly',(x,y-.39,4.97),identity,.85,True)
    animal('Gopura_Ganesha_Elephant_Mount-renderonly',(-2.70,y-.49,4.88),
           m['indigo'],'elephant',.81,rotation=math.radians(-66))
    for side in [-1,1]:
        x=side*2.67
        s=Sculpture()
        p=palette(s)
        for row in [0,1]:
            s.tube([(x+(.59+row*.042)*math.cos(a),y-.307-row*.02,5.43+.68*math.sin(a))
                    for a in [math.tau*i/60 for i in range(61)]],.034,p['gold'],10)
        s.finish('Gopura_Side_Medallion-renderonly')
        figure('Gopura_Side_Relief-renderonly',(x,y-.40,5.04),'ganesha' if side==-1 else 'devi',.77,True)
    for level,(w,z) in enumerate([(7.0,6.20),(6.55,6.50),(4.45,6.81),(3.31,7.11),(2.32,7.40)]):
        box('Gopura_Tier_Cornice',(0,y+.12,z),(w,1.09-level*.092,.17),
            gold if level%2 else m['indigo'],.029)
        box('Gopura_Tier_Frieze',(0,y+.125,z+.126),(w-.24,1.01-level*.081,.105),stone,.018)
        count=max(3,int(w/.55))
        for i in range(count):
            x=(i-(count-1)/2)*(w-.34)/count
            box('Gopura_Tier_Edicule_Base',(x,y-.37+level*.035,z+.197),(.25,.19,.089),blue,.02)
            sphere('Gopura_Tier_Floral_Fragment-renderonly',(x,y-.45+level*.035,z+.239),
                   (.092,.041,.078),gold if i%3 else red,14)
    for x in [-.85,-.42,0,.42,.85]:
        sphere('Gopura_Finial-renderonly',(x,y+.16,7.60),(.105,.10,.14),gold,18)
    for x in [-2.74,2.74]:
        sphere('Gopura_Lateral_Kuta',(x,y+.11,6.82),(.35,.27,.24),m['indigo'],24)


def silver_frame(x,y,z,width,height,m):
    silver=m['silver']
    box('Darshan_Silver_Engraved_Backplate',(x,y+.20,z+height*.47),
        (width*.91,.11,height*.91),silver,.045)
    for side in [-1,1]:
        px=x+side*width*.46
        box('Darshan_Marble_Column_Plinth',(px,y-.093,z+.095),(.21,.23,.19),m['plaster'],.025)
        cylinder('Darshan_Fluted_Silver_Post',(px,y-.075,z+height*.38),.098,height*.7,silver)
        for ring in [.18,.26,.66,.73]:
            cylinder('Darshan_Post_Stamped_Band',(px,y-.075,z+height*ring),.121,.048,silver)
    s=Sculpture()
    p=palette(s)
    for i in range(4):
        pts=[(x+width*(.43+i*.020)*math.cos(a),y-.100-i*.014,z+height*(.66+(.28+i*.028)*math.sin(a)))
             for a in [math.pi*j/52 for j in range(53)]]
        s.tube(pts,.023,p['silver'],12)
    for j in range(29):
        a=math.pi*j/28
        add_lotus(s,x+width*.48*math.cos(a),y-.158,z+height*(.675+.31*math.sin(a)),
                  .049,p['silver'],p['white'])
    s.finish('Darshan_Raised_Silver_Foliate_Canopy-renderonly')


def shiva_stop(id,x,y,dx,dy,m,landing=None):
    floor=.22
    box(id+'_Linga_Platform',(x,y,floor+.10),(.75,.69,.20),m['stone'],.027)
    linga(id+'_Shiva_Linga',(x,y,floor+.20),.47,m['dark'])
    ox,oy=x+dx*.66,y+dy*.66
    box(id+'_Nandi_Base',(ox,oy,floor+.075),(.365,.365,.15),m['stone'],.019)
    animal(id+'_Nandi-renderonly',(ox,oy,floor+.15),m['dark'],'nandi',.47,
           rotation=math.atan2(-dx,dy))
    anchor(id+'_Anchor',(x,y,floor+.61))
    lx,ly = landing or (x+dx*1.39,y+dy*1.39)
    anchor(id+'_Landing',(lx,ly,floor+.055))


def build():
    clear_scene()
    rng=random.Random(194)
    mat={
        'cream':material('Vishalakshi Yellow Limewash',(.55,.43,.253)),
        'plaster':material('Vishalakshi Aged Warm Plaster',(.67,.61,.50)),
        'blue':material('Vishalakshi Painted Blue',(.041,.27,.46)),
        'blue_light':material('Vishalakshi Blue Highlights',(.077,.47,.54)),
        'indigo':material('Vishalakshi Blue Grey',(.076,.149,.205)),
        'red':material('Vishalakshi Red Painted Relief',(.32,.066,.098)),
        'gold':material('Vishalakshi Gold Paint',(.65,.397,.16),.59,.17),
        'bronze':material('Vishalakshi Ochre Shadow',(.37,.15,.040),.68,.1),
        'leaf':material('Vishalakshi Floral Green',(.16,.273,.106)),
        'leaf_light':material('Vishalakshi Floral Green Highlights',(.25,.41,.154)),
        'stone':material('Vishalakshi Alley Paving',(.29,.205,.157)),
        'stone_light':material('Vishalakshi Aged Slate',(.32,.34,.31)),
        'ink':material('Vishalakshi Engraving',(.13,.06,.064)),
        'dark':material('Vishalakshi Ritual Basalt',(.046,.041,.036),.65),
        'silver':material('Vishalakshi Silver Repousse',(.68,.69,.70),.32,.56),
        'black_tile':material('Vishalakshi Dark Floor Tile',(.020,.024,.021),.49),
        'white_tile':material('Vishalakshi Pale Floor Tile',(.52,.50,.44),.49),
        'brick':material('Mir Ghat Exposed Brick',(.35,.179,.101)),
        'brick_light':material('Mir Ghat Brick Highlights',(.46,.244,.145)),
    }
    m=mat
    shader=m['stone'].node_tree.nodes.get('Principled BSDF')
    add_stone_detail(m['stone'],shader,tuple(shader.inputs['Base Color'].default_value))
    box('Ground_Mir_Ghat',(0,1,-.31),(80,80,.62),m['stone'])
    box('Temple_Continuous_Plinth',(0,6.56,.055),(10.10,13.22,.11),m['blue'],.021)
    box('Temple_Floor_Collision-colonly',(0,6.53,.144),(10.02,12.99,.152),m['stone'])
    tiles=[[],[]]
    for ix in range(20):
        for iy in range(26):
            x,y=-4.95+ix*.496,.091+iy*.495
            t=tiles[(ix+iy)%2]
            t.append([(x,y,.222),(x+.491,y,.222),(x+.491,y+.490,.222),(x,y+.490,.222)])
    for group,key in zip(tiles,['white_tile','black_tile']):
        skin('Temple_Checkerboard_'+key+'-renderonly',[p for quad in group for p in quad],
             [tuple(range(i,i+4)) for i in range(0,len(group)*4,4)],m[key])
    for i in range(2):
        box('Gali_Darshan_Steps',(0,-.64+i*.34,.045+i*.035),(2.12,.35,.09+i*.07),m['stone'],.017)

    wall_front=0
    for x in [-2.95,2.95]:
        box('Gali_Temple_Frontage',(x,.15,2.19),(4.14,.30,4.18),m['cream'],.022)
        box('Gali_Temple_Plinth_Frontage',(x,-.022,.305),(4.13,.20,.25),m['blue'],.026)
    box('Door_Overhead_Fill',(0,.14,3.45),(1.77,.31,1.76),m['cream'],.022)
    for x in [-4.91,4.91]:
        box('Long_Shared_Temple_Wall',(x,6.68,2.27),(.28,13.12,4.10),m['cream'],.022)
    box('Temple_Back_Wall',(0,13.02,2.28),(10,.34,4.12),m['cream'],.022)
    box('Temple_Flat_Roof',(0,6.60,4.37),(10.18,13.23,.23),m['stone_light'],.021)
    for x in [-4.96,4.96]:
        box('Temple_Roof_Parapet',(x,6.75,4.65),(.22,13.06,.42),m['cream'],.018)
    box('Temple_Back_Roof_Parapet',(0,13.08,4.65),(10.13,.22,.42),m['cream'],.018)
    box('Front_Painted_Cornice',(0,.02,4.29),(10.28,.48,.26),m['blue'],.031)
    for k in range(2):
        box('Wall_Vent_Aperture',(4.03,-.026,2.82+k*.39),(1.36,.087,.22),m['ink'],.019)
        for i in range(8):
            box('Wall_Vent_Grille',(3.47+i*.16,-.087,2.82+k*.39),(.036,.047,.22),m['stone_light'])
    portal(wall_front,m)
    gateway_superstructure(m)
    # This is an occupied street façade with a narrow shared gali.
    box('Lane_Front_Brick_Building',(4.43,-5.4,3.0),(5.3,2.23,6.0),m['brick'],.025)
    box('Lane_Front_Plaster_Building',(-4.40,-5.8,2.53),(5.15,2.78,5.06),m['plaster'],.035)
    for px in [-6.5,6.42]:
        for y in [1.85,6.35,10.84,15.24]:
            h=rng.uniform(4.0,6.8)
            box('Lahori_Tola_Adjacent_Roof_Mass',(px,y,h/2),(2.46,4.20,h),
                rng.choice([m['cream'],m['plaster'],m['brick'],m['stone_light']]),.023)
            box('Lahori_Tola_Roof_Parapet',(px,y,h+.10),(2.54,4.34,.21),m['stone_light'],.025)
    for x in [-8.7,-4.0,.15,4.75,9.0]:
        h=rng.uniform(4.25,6)
        box('Lahori_Tola_Back_Roof_Mass',(x,16.34,h/2),(4.0,5.35,h),
            rng.choice([m['cream'],m['brick'],m['stone_light']]),.026)
    for ring_x in [-12.0,12.8]:
        for y in [-8.0,-2.7,2.8,8.0,13.6,19.1]:
            h=rng.uniform(3.15,7.3)
            x=ring_x+rng.uniform(-.48,.48)
            box('Old_City_Party_Wall_Roof_Block',(x,y,h/2),(rng.uniform(3.35,5.2),4.65,h),
                rng.choice([m['cream'],m['brick'],m['stone_light']]),.026)
            box('Old_City_Terrace_Shed',(x+.47,y+.62,h+.43),(1.42,1.23,.86),
                rng.choice([m['plaster'],m['stone_light'],m['indigo']]),.017)
    for px in [-3.85,3.81]:
        for y in [-11.4,-15.4]:
            h=rng.uniform(3.7,6.9)
            box('Mir_Ghat_Lane_Turn_Mass',(px,y,h/2),(4.15,3.9,h),m['brick'],.027)

    # Roof of the inner cell is distinct from the vertical street gateway.
    box('Sanctum_Roof_Upstand',(0,8.48,4.66),(5.05,4.2,.46),m['stone_light'],.036)
    box('Sanctum_Roof_Cap',(0,8.46,4.90),(4.62,3.84,.11),m['plaster'],.021)
    for x in [-2.08,2.08]:
        box('Garbhagriha_Side',(x,8.61,1.87),(.29,4.39,3.29),m['stone_light'],.025)
    box('Garbhagriha_Rear',(0,10.62,1.86),(4.28,.29,3.28),m['stone_light'],.026)
    for x in [-1.57,1.57]:
        box('Garbhagriha_Entrance_Wall',(x,6.54,1.86),(1.12,.33,3.29),m['stone_light'],.023)
        box('Garbhagriha_Brass_Jamb',(x*.625,6.35,1.53),(.128,.195,2.61),m['gold'],.03)
    box('Garbhagriha_Gilt_Header',(0,6.37,2.79),(2.15,.19,.16),m['gold'],.024)
    box('Garbhagriha_Entrance_Header',(0,6.52,3.16),(2.21,.40,.67),m['stone_light'],.024)
    for px in [-2.66,2.66]:
        box('Mandapa_Pillar_Foot',(px,4.88,.37),(.52,.51,.30),m['stone_light'],.031)
        box('Mandapa_Pillar',(px,4.88,1.99),(.35,.35,3.08),m['cream'],.037)
        box('Mandapa_Pillar_Capital',(px,4.88,3.51),(.55,.55,.22),m['stone_light'],.031)
    for x,kind in [(-3.62,'bhairava'),(3.55,'navagraha')]:
        y=3.42
        box(kind+'_Mandapa_Altar',(x,y,.47),(1.83,1.46,.50),m['stone_light'],.031)
        box(kind+'_Mandapa_Altar_Back',(x,y+.63,1.41),(1.83,.19,1.40),m['indigo'],.025)
        if kind=='bhairava':
            figure('Mandapa_Kala_Bhairava_Study-renderonly',(x,y-.11,.72),'bhairava',1.10)
        else:
            for i in range(9):
                px=x+(i%3-1)*.53
                py=y+(i//3-1)*.36
                box('Navagraha_Figure_Pedestal',(px,py,.76),(.28,.24,.08),m['dark'],.015)
                figure('Navagraha_Figure_%d-renderonly'%(i+1),(px,py,.80),
                       'seated' if i in [2,5,7] else 'attendant',.39)
        anchor(kind+'_Anchor',(x,y,.96))
        anchor(kind+'_Landing',(x,y-1.53,.275))

    shiva_stop('Pradakshina_Left',-4.32,7.54,1,0,m)
    shiva_stop('Pradakshina_Right',4.33,7.65,-1,0,m)
    shiva_stop('Pradakshina_Back',.86,12.52,0,-1,m,landing=(1.96,11.47))
    for id,x,y,form in [('Ganapati',-4.16,10.06,'ganesha'),('Shankaracharya',-1.19,12.53,'acharya')]:
        box(id+'_Pedestal',(x,y,.39),(.81,.72,.34),m['stone_light'],.022)
        figure(id+'_Study-renderonly',(x,y-.08,.56),form,.75)
        anchor(id+'_Anchor',(x,y,1.16))
        if form=='ganesha':
            anchor(id+'_Landing',(x+1.17,y-.36,.275))
        else:
            anchor(id+'_Landing',(x-.88,y-1.03,.275))

    box('Vishalakshi_Marble_Darshan_Dais',(0,9.88,.435),(3.52,1.24,.43),m['plaster'],.034)
    box('Vishalakshi_Dais_Red_Textile',(0,9.83,.664),(3.30,1.23,.07),m['red'],.026)
    silver_frame(.29,9.79,.65,2.01,2.33,m)
    decorated_darshan((.27,9.63,.65))
    silver_frame(-.98,10.0,.67,.77,1.37,m)
    figure('Adi_Vishalakshi_Study-renderonly',(-.99,9.87,.72),'devi',.72)
    for side in [-1,1]:
        fabrics=[m['leaf'],m['blue'],m['gold'],m['red']]
        x=side*1.21
        for i in range(5):
            box('Darshan_Folded_Offering_Textile-renderonly',(x,9.30,.715+i*.049),
                (.48+.036*rng.random(),.46,.052),fabrics[(i+side)%4],.022)
    anchor('Deity_Vishalakshi',(.27,9.58,1.85))
    anchor('Vishalakshi_Darshan_Landing',(.27,7.62,.277))
    anchor('Adi_Vishalakshi_Anchor',(-.99,9.84,1.46))
    anchor('Adi_Vishalakshi_Landing',(-.53,8.19,.277))
    anchor('Sanctum_Lamp_Position',(-.62,7.48,2.55))
    anchor('Kashi_Gate_Reference',(0,-.51,3.01))
    anchor('Kashi_Gate_Landing',(0,-3.91,.08))
    anchor('Nagarathar_Lettering_Reference',(3.51,-.22,1.60))
    anchor('Nagarathar_Lettering_Landing',(3.48,-2.25,.08))
    anchor('Spawn_Point',(0,-9.62,.08))
    anchor('Arrival_Facing',(0,-.70,.08))

    # Align the approximate roof axes with the mapped city blocks. The doorway
    # bearing is an inference from the lane and adjoining roof footprint.
    transform=Matrix.Rotation(math.radians(-89),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world=transform @ obj.matrix_world


if __name__=='__main__':
    build()
    if not globals().get('DEFER_GLB_EXPORT',False):
        prepare_scene()
        finish('kashi_vishalakshi')
