"""Kalighat's Bengali aatchala and courtyard, traced from imagery and a published visitor plan."""
import math
import random

import bpy
from mathutils import Matrix

from common_geometry import clear_scene
from common_materials import create_granite_stone, create_white_marble
from deity_detail import Sculpture, crown_band, garland, palette
from present_day_sites import anchor, box, cylinder, finish, linga, material, sphere


def chala(name, x, y, z, w, d, height, roof, edging):
    # Continuous hipped surfaces with arched eaves on all four facades.
    profile = [(0, 1, 0), (.12, .99, .15), (.24, .94, .25), (.40, .82, .20),
               (.59, .65, .14), (.75, .48, .09), (.88, .31, .04), (1, .12, 0)]
    vertices = []
    faces = []
    segments = 20
    count = segments * 4
    for t, scale, arch in profile:
        for side in range(4):
            for i in range(segments):
                u = 2 * i / segments - 1
                a, b = [(u, -1), (1, u), (-u, 1), (-1, -u)][side]
                vertices.append((x + a*w*scale/2, y + b*d*scale/2, z + height*(t + arch*(1-u*u))))
    for row in range(len(profile)-1):
        for i in range(count):
            j = (i+1) % count
            base = row*count
            faces.append((base+i, base+j, base+count+j, base+count+i))
    faces.append(tuple(range((len(profile)-1)*count, len(vertices))))
    skirt = len(vertices)
    vertices.extend((vx,vy,z-.05) for vx,vy,_ in vertices[:count])
    for i in range(count):
        j = (i+1)%count
        faces.append((i,skirt+i,skirt+j,j))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(roof)
    mesh.materials.append(edging)
    mesh.update()
    for face in mesh.polygons:
        face.material_index = int(face.index < count or face.index >= (len(profile)-1)*count+1)
        face.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)


def cornice(name, x, y, z, w, d, mat):
    for offset, inset in [(0, 0), (.13, .11), (.27, .23)]:
        box(name, (x, y, z+offset), (w-inset, d-inset, .14), mat, .022)


def arcade(name, x, y, floor, width, height, depth, mat):
    # Fill the spandrel above a semicircular opening with joint-free masonry.
    radius = width/2
    spring = floor+height-radius-.18
    vertices = []
    for i in range(25):
        a = math.pi * i/24
        ax, az = x+radius*math.cos(a), spring+radius*math.sin(a)
        vertices.extend(((ax,y-depth/2,az), (ax,y+depth/2,az),
                         (ax,y+depth/2,floor+height), (ax,y-depth/2,floor+height)))
    faces = [(3,2,1,0), (96,97,98,99)]
    for i in range(24):
        start = i*4
        for j in range(4):
            k = (j+1)%4
            faces.append((start+j, start+k, start+4+k, start+4+j))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for side in [-1,1]:
        box(name+'_Pier', (x+side*(radius+.22), y, (spring+floor)/2),
            (.44,depth,spring-floor), mat, .028)


def cell(name, x, y, w, d, h, door, wall, floor):
    box(name+'_Floor',(x,y,.065),(w,d,.13),floor,.022)
    box(name+'_Back',(x,y+d/2-.14,h/2),(w,.28,h),wall,.028)
    for side in [-1,1]:
        box(name+'_Side',(x+side*(w/2-.14),y,h/2),(.28,d,h),wall,.028)
        span = (w-door)/2
        box(name+'_Face',(x+side*(door+span)/2,y-d/2+.15,h/2),(span,.30,h),wall,.025)
    box(name+'_Lintel',(x,y-d/2+.15,h-.23),(door,.31,.46),wall,.024)


def kali(x, y):
    s = Sculpture()
    p = palette(s)
    s.ellipsoid((0, .06, .69), (.66, .34, .81), p['black'], 48, 30)
    s.ellipsoid((0, -.267, .62), (.115, .105, .19), p['black'],24,16)
    for ex, ez, rx, rz in [(-.32,.87,.235,.095),(.32,.87,.235,.095),(0,1.15,.095,.17)]:
        for off, shrink, color in [(0,1,'gold'),(-.023,.83,'white')]:
            s.ellipsoid((ex,-.30+off,ez),(rx*shrink,.043,rz*shrink),p[color],32,14)
        s.ellipsoid((ex,-.372,ez),(.069,.023,.070),p['orange'])
        s.ellipsoid((ex,-.393,ez),(.042,.019,.052),p['black'])
    s.ellipsoid((0,-.271,.35),(.248,.108,.105),p['red'],36,18)
    def taper(v):
        v.x *= .69+.30*(v.z/.40+1)
        v.y -= .07*max(0, -v.z/.40)
        return v
    s.ellipsoid((0,-.387,.13),(.111,.05,.40),p['gold'],36,24,taper)
    s.tube([(0,-.443,.36),(0,-.455,.15),(0,-.488,-.05),(0,-.504,-.19)],.012,p['yellow'])
    crown_band(s,p,1.27,1.48,-.14,4)
    for sign in [-1,1]:
        s.rosette((sign*.68,-.22,.67),.145,p['gold'],p['red'])
        for n,(hand_x,hand_z) in enumerate([(1.01,.93),(.83,.14)]):
            px = sign*hand_x
            s.ellipsoid((px,-.16,hand_z),(.11,.07,.16),p['gold'])
            for finger in range(4):
                delta = (finger-1.5)*.048
                s.tube([(px+delta,-.175,hand_z+.065),
                        (px+delta*1.29,-.182,hand_z+.18),
                        (px+delta*1.35,-.205,hand_z+.24-.034*abs(finger-1.5))],.024,p['gold'])
            s.tube([(px-sign*.068,-.17,hand_z),(px-sign*.145,-.21,hand_z+.067)],.036,p['gold'])
            if n == 0 and sign < 0:
                s.tube([(px,-.102,hand_z),(px-.10,-.103,hand_z+.42),(px-.02,-.12,hand_z+.69)],.047,p['silver'])
            if n == 0 and sign > 0:
                s.ellipsoid((px+.13,-.10,hand_z-.19),(.105,.065,.13),p['silver'])
    s.ellipsoid((0,.12,-.28),(1.01,.39,.30),p['red'],36,16)
    garland(s,p,.89,.29,.66,-.41,53)
    for i in range(17):
        a = math.pi*i/16
        s.rosette((.72*math.cos(a),-.28,1.16+.55*math.sin(a)),.066,p['red'],p['yellow'])
    s.finish('Deity_Kalika',(x,y,1.39),1.05)


def build():
    clear_scene()
    rng = random.Random(406)
    paving = create_granite_stone('Kalighat_CourtyardPaving',(.46,.40,.33,1))
    court = create_white_marble('Kalighat_WornMarble')
    lime = create_white_marble('Kalighat_Limewash')
    pink = material('Kalighat_OchrePink',(.59,.33,.29))
    rose = material('Kalighat_DarkRedPlaster',(.31,.087,.06))
    sand = material('Kalighat_Stonework',(.57,.45,.30))
    dark = material('Kalighat_Basalt',(.047,.041,.037),.44)
    gold = material('Kalighat_GildedCrown',(.93,.57,.15),.70,.35)
    sacred = material('Kalighat_Sindoor',(.55,.058,.027))
    water = material('Kalighat_KundupukurWater',(.071,.21,.17),.18,.20)
    leaf = [material('Kalighat_Leaf'+str(i),(.085+i*.025,.19+i*.038,.06+i*.013)) for i in range(4)]
    bark = material('Kalighat_Bark',(.18,.095,.047))
    street = material('Kalighat_UrbanStone',(.26,.24,.21))

    # Local compound axis. Sheet relationships are surveyed visually; building
    # heights and visitor dimensions are playable estimates.
    box('Ground_UrbanContext',(0,0,-.4),(126,118,.64),street)
    box('Court_Paving',(0,0,-.095),(37.6,54.6,.19),paving)
    for x,w in [(-11,16),(10.8,16.4)]:
        box('Compound_SouthWall',(x,-27,1.10),(w,.36,2.20),rose,.028)
    for y,d in [(13.9,26.2),(-14.7,24.5)]:
        box('Compound_WestWall',(-19,y,1.2),(.35,d,2.4),rose,.025)
    for y,d in [(2.9,34.8),(24.2,5.6),(-22.7,8.6)]:
        box('Compound_EastWall',(19,y,1.2),(.35,d,2.4),rose,.025)
    for x,w in [(-15,8),(5.8,26.4)]:
        box('Compound_NorthWall',(x,27,1.2),(w,.36,2.4),rose,.025)
    arcade('South_Entrance',.6,-27,0,3.25,4.10,.78,pink)
    anchor('Spawn_Point',(.65,-23.9,.055))

    x,y = 2.0,9.3
    cell('Kalika_Sanctum',x,y,10.2,7.4,5.45,2.65,pink,court)
    for side in [-1,1]:
        box('Kalika_Jamb',(x+side*1.46,y-3.66,1.75),(.37,.47,3.5),sand,.026)
        for i in range(3):
            box('Kalika_Pilaster',(x+side*(2.25+.98*i),y-3.7,2.48),(.33,.31,4.96),rose,.022)
    box('Kalika_Door_Architrave',(x,y-3.69,3.64),(3.35,.42,.33),gold,.035)
    cornice('Kalika_Main_Cornice',x,y,5.34,10.9,8.2,rose)
    chala('Kalika_Lower_Aatchala_Roof',x,y,5.70,11.45,8.9,4.55,lime,pink)
    chala('Kalika_Upper_Aatchala_Roof',x,y,9.88,4.75,4.10,3.10,lime,gold)
    for i,(radius,height) in enumerate([(.51,.28),(.41,.27),(.28,.49),(.13,.34)]):
        cylinder('Kalika_Gilded_Finial',(x,y,12.96+sum([.28,.27,.49,.34][:i])+height/2),radius,height,gold)
    box('Kalika_Murti_Pedestal',(x,10.93,.46),(2.82,1.34,.66),dark,.05)
    kali(x,10.93)
    anchor('Kalika_Darshan_Landing',(x,7.47,.15))

    # Jor Bangla surrounds the main cell to the front and sides.
    jor_y = 4.2
    box('Jor_Bangla_Floor',(x,jor_y,.052),(13.0,3.75,.104),court,.025)
    for sign in [-1,1]:
        for post_y in [jor_y-1.52,jor_y+1.54,7.6,10.38,13.53]:
            box('Jor_Bangla_Pilaster',(x+sign*6.25,post_y,1.62),(.44,.48,3.25),pink,.025)
        box('Jor_Bangla_Side_Roof',(x+sign*5.89,9.35,3.36),(1.72,8.1,.28),pink,.032)
        chala('Jor_Bangla_Front_Roof',x+sign*3.2,jor_y,3.25,6.65,4.05,1.23,lime,rose)
    for px in [x-3.7,x,x+3.7]:
        arcade('Jor_Bangla_Entrance_Arch',px,jor_y-1.55,0,2.55,3.27,.39,pink)

    # Flat-roofed Natmandir immediately south of the sanctum.
    hall_y = -6.3
    box('Natmandir_Floor',(x,hall_y,.056),(12.35,14.9,.112),court,.018)
    for fy in [hall_y-7.20,hall_y+7.20]:
        for offset in [-3.88,0,3.88]:
            arcade('Natmandir_End_Arcade',x+offset,fy,0,3.44,4.30,.53,pink)
    for sign in [-1,1]:
        for fy in [-11.88,-8.18,-4.48,-.78]:
            before = set(bpy.context.scene.objects)
            arcade('Natmandir_Side_Arcade',x+sign*5.94,fy,0,3.25,4.30,.52,pink)
            origin = Matrix.Translation((x+sign*5.94,fy,0))
            rot = origin @ Matrix.Rotation(math.pi/2,4,'Z') @ origin.inverted()
            bpy.context.view_layer.update()
            for ob in set(bpy.context.scene.objects)-before:
                ob.matrix_world = rot @ ob.matrix_world
    cornice('Natmandir_Flat_Roof',x,hall_y,4.36,12.64,15.32,pink)
    box('Natmandir_Roof_Deck',(x,hall_y,4.61),(12.22,14.90,.22),sand)
    for side in [-1,1]:
        box('Natmandir_Roof_Parapet',(x+side*6.0,hall_y,4.84),(.23,14.9,.34),rose)
        box('Natmandir_Roof_Parapet',(x,hall_y+side*7.38,4.84),(12,.23,.34),rose)

    anchor('Natmandir_Reference',(x,hall_y,1.12))
    anchor('Natmandir_Landing',(x,hall_y-3.4,.13))
    for name,sx,sy,angle in [('North',4.65,23.65,0),('West_Inner',-15.82,-7.32,90),
                             ('West_Outer',-15.82,-15.7,90),('Southeast',15.12,-22.85,180)]:
        before = set(bpy.context.scene.objects)
        cell('Shiva_'+name,sx,sy,3.50,3.58,2.94,1.84,lime,court)
        chala('Shiva_'+name+'_Roof',sx,sy,2.88,3.9,3.95,1.58,lime,pink)
        sphere('Shiva_'+name+'_Finial',(sx,sy,4.55),(.14,.14,.22),gold,16)
        linga('Kalighat_Shiva_'+name,(sx,sy+.40,.16),.85,dark)
        anchor('Kalighat_Shiva_'+name+'_Landing',(sx,sy-2.80,0.05))
        origin = Matrix.Translation((sx,sy,0))
        rotation = origin @ Matrix.Rotation(math.radians(angle),4,'Z') @ origin.inverted()
        bpy.context.view_layer.update()
        for obj in set(bpy.context.scene.objects)-before:
            if obj.parent is None:
                obj.matrix_world = rotation @ obj.matrix_world

    # The three sacred stones share the tree altar at Sosthi Tala.
    sx,sy = -3.48,23.52
    box('Sosthi_Tala_Altar',(sx,sy,.40),(5.25,3.24,.80),rose,.055)
    box('Sosthi_Tala_Ledge',(sx,sy,.86),(5.45,3.45,.18),sand,.045)
    cylinder('Sosthi_Sacred_Tree_Trunk',(sx,sy+.52,2.88),.42,4.15,bark)
    for i in range(22):
        a = rng.random()*math.tau
        radius = rng.uniform(.2,2.25)
        sphere('Sosthi_Sacred_Tree_Crown',(sx+radius*math.cos(a),sy+.52+radius*math.sin(a),rng.uniform(4.6,6.5)),
               (rng.uniform(.92,1.53),1.02,.85),leaf[i%4],16)
    for index, offset in enumerate([-.65,0,.65]):
        sphere(['Sosthi_Stone','Shitala_Stone','Mangal_Chandi_Stone'][index],
               (sx+offset,sy-.75,1.01),(.24,.22,.18),sacred,24)
    anchor('Sosthi_Tala_Anchor',(sx,sy-.90,1.03))
    anchor('Brahmananda_Giri_Reference',(sx-1.8,sy-.95,1.06))
    anchor('Sosthi_Tala_Landing',(sx,sy-2.78,.06))
    anchor('Brahmananda_Giri_Landing',(sx-1.67,sy-2.78,.06))

    rx,ry = -15.28,10.72
    cell('Shyam_Rai_Mandir',rx,ry,4.9,8.2,4.95,2.15,pink,court)
    cornice('Shyam_Rai_Roof',rx,ry,4.98,5.45,8.61,lime)
    chala('Shyam_Rai_Upper_Roof',rx,ry+.25,5.30,3.55,3.95,1.70,lime,pink)
    box('Shyam_Rai_Paired_Altar',(rx,ry+.35,.41),(2.42,1.05,.55),rose,.04)
    icons = Sculpture(); p = palette(icons)
    for sign in [-1,1]:
        fx = sign*.43
        face = p['black'] if sign < 0 else p['gold']
        garment = p['yellow'] if sign < 0 else p['red']
        icons.ellipsoid((fx,.0,.46),(.25,.16,.44),garment,24,18)
        icons.ellipsoid((fx,-.028,1.06),(.125,.110,.155),face,24,18)
        icons.ellipsoid((fx,.02,1.23),(.15,.13,.12),p['gold'])
        icons.tube([(fx-.17,-.04,.74),(fx-.20,-.14,.63),(fx+sign*.15,-.25,.84)],.048,face)
        icons.tube([(fx+.17,-.04,.74),(fx+.20,-.13,.66),(fx-sign*.10,-.26,.84)],.045,face)
        icons.rosette((fx,-.18,.73),.07,p['gold'],p['red'])
        for i in range(14):
            a = math.pi+math.pi*i/13
            icons.rosette((fx+math.cos(a)*.17,-.18,.85+math.sin(a)*.32),.035,p['white'],p['yellow'],6)
    icons.tube([(-.81,-.25,.87),(-.20,-.25,.84)],.022,p['gold'])
    icons.finish('Shyam_Rai_Iconographic_Study',(rx,ry+.35,.65))
    anchor('Shyam_Rai_Anchor',(rx,ry+.17,1.44))
    anchor('Shyam_Rai_Landing',(rx,ry-2.60,.14))
    dx,dy = -10.14,8.91
    box('Swing_Pavilion_Floor',(dx,dy,.12),(3.65,3.66,.24),court)
    for off in [-1.48,1.48]:
        for row in [-1.39,1.39]:
            box('Swing_Pavilion_Pier',(dx+off,dy+row,1.55),(.32,.32,3.10),pink,.025)
    cornice('Swing_Pavilion_Roof',dx,dy,3.10,3.9,3.91,pink)
    box('Swing_Pavilion_Seat',(dx,dy,.92),(1.45,.62,.13),sand,.04)
    for off in [-.64,.64]:
        cylinder('Swing_Pavilion_Hanger',(dx+off,dy,1.93),.022,1.85,gold)
    anchor('Swing_Pavilion_Anchor',(dx,dy,1.13))

    hx,hy = 5.23,-18.30
    box('Harkath_Tala_Platform',(hx,hy,.08),(4.04,3.72,.16),sand,.027)
    for oy in [-.73,.73]:
        box('Harkath_Tala_Stone_Socket',(hx,hy+oy,.19),(1.09,.58,.23),rose,.045)
    anchor('Harkath_Tala_Anchor',(hx,hy,.64))

    # Documented utility ranges and the dense surrounding city are context.
    for label,bx,by,w,d in [('Stores',-14.75,22.16,7.65,8.68),
                             ('West_Kitchen',-10.02,12.42,3.85,3.14),
                             ('East_Kitchen',15.29,5.28,6.11,8.6),
                             ('Tahobil',-15.77,-24.91,5.78,3.88),
                             ('Homa',-6.86,-24.84,4.22,4.02)]:
        box(label,(bx,by,1.48),(w,d,2.96),pink,.04)
        cornice(label+'_Roof',bx,by,3.0,w+.31,d+.31,lime)
    for side, bays in [(-1,[-18.4,-11,-2.8]),(1,[-19.2,-12.8,-7.8,14.25,20.5])]:
        for i, by in enumerate(bays):
            bx = -13.2 if side < 0 else 17.45
            box('Shop_Range',(bx,by,1.23),(2.75,1.90+i%2*.55,2.46),pink,.04)
            cornice('Shop_Range_Roof',bx,by,2.48,2.95,2.10+i%2*.55,sand)
    # Outside the eastern gate, Kundupukur uses its compact rectangular bank.
    wx,wy = 28.37,6.15
    box('Kundupukur_Water',(wx,wy,-.045),(9.15,17.80,.09),water)
    for sign in [-1,1]:
        box('Kundupukur_Bank',(wx+sign*5.27,wy,.23),(1.32,19.1,.46),sand,.035)
        box('Kundupukur_Bank',(wx,wy+sign*9.21,.23),(10.50,1.12,.46),sand,.035)
        box('Kundupukur_Railing',(wx+sign*5.72,wy,.72),(.19,19.1,.56),rose,.02)
    box('Kundupukur_West_Visitor_Path',(22.03,wy,-.043),(2.51,19.4,.095),paving,.02)
    for bx, by, count in [(-27,-18,8),(39,-23,8),(-21,-36,9),(-22,35,9)]:
        for i in range(count):
            sx,sy = (bx,by+i*6.3) if bx in [-27,39] else (bx+i*6.3,by)
            h = rng.uniform(4.1,9.4)
            box('Context_Urban_Terrace',(sx,sy,h/2),(5.65,5.36,h),[sand,pink,street][i%3],.045)
    rotation = Matrix.Rotation(math.radians(8),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world = rotation @ obj.matrix_world


if __name__ == '__main__':
    build()
    finish('kalighat')
