"""Present-day Jawala Ji compound from aerial and temple photographs.

Coordinates are in metres. The court and terraces follow observed relative
positions. Interior recess positions other than the central jyoti are studies.
"""
import math
import random

import bpy
from mathutils import Matrix

from common_geometry import clear_scene
from common_materials import create_granite_stone
from deity_detail import Sculpture
from present_day_sites import anchor, box, finish, linga, material


WEST, EAST = -20.9, 25.6
SOUTH, NORTH = -37.0, 6.6
PIT_Y = 13.0


def mesh(name, vertices, faces, surface):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(surface)
    return obj


def surface(name, x0, x1, y0, y1, z, mat):
    return mesh(name, [(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)], [(0,1,2,3)], mat)


def tile_field(name, bounds, z, step, mats):
    x0,x1,y0,y1 = bounds
    grid = [([],[]) for mat in mats]
    for i in range(math.ceil((x1-x0)/step)):
        for j in range(math.ceil((y1-y0)/step)):
            a,b = x0+i*step,y0+j*step
            points, faces = grid[(i+j)%2]
            k = len(points)
            points.extend([(a,b,z),(min(a+step,x1),b,z),
                           (min(a+step,x1),min(b+step,y1),z),(a,min(b+step,y1),z)])
            faces.append((k,k+1,k+2,k+3))
    for index,(points,faces) in enumerate(grid):
        mesh(name+f'_{index}-renderonly',points,faces,mats[index])


def rings(name, center, profile, surface_mat, lobes=0, squareness=0.0):
    x,y,z = center
    vertices, faces = [], []
    n = 96 if lobes else 48
    for h,r in profile:
        for i in range(n):
            a = math.tau*i/n
            cs,sn = math.cos(a),math.sin(a)
            reed = 1 + (.032*math.cos(lobes*a) if lobes else 0)
            reed *= (abs(cs)**(2+squareness)+abs(sn)**(2+squareness))**(-1/(2+squareness))
            vertices.append((x+r*reed*cs,y+r*reed*sn,z+h))
    for j in range(len(profile)-1):
        for i in range(n):
            a = j*n+i
            b = j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    faces += [tuple(reversed(range(n))),tuple(range(len(vertices)-n,len(vertices)))]
    obj = mesh(name,vertices,faces,surface_mat)
    for poly in obj.data.polygons[:-2]:
        poly.use_smooth = True
    return obj


def cupola(name, x, y, z, r, h, m, gold=True, square=False):
    profile = [(0,.93),(.07,1.0),(.14,1.032),(.28,1.00),(.44,.94),(.63,.80),
               (.79,.60),(.91,.39),(.97,.23),(1,.16)]
    mat = m['gold' if gold else 'white']
    rings(name+'_Ribbed_Dome', (x,y,z), [(a*h,b*r) for a,b in profile],
          mat, 24 if r>2 else 12, 1.4 if square else 0)
    r = max(.19,r*.22)
    neck = [(0,.77),(.19,1),(.32,.62),(.41,.38),(.54,.66),(.67,.72),
            (.75,.44),(.84,.69),(.94,.55),(1,.052)]
    finial_h = h * (.83 if square else .58)
    rings(name+'_Kalash_And_Crown',(x,y,z+h-.012),[(a*finial_h,b*r) for a,b in neck],
          m['gold' if gold else 'brass'])
    if square:
        box(name+'_Finial_Square_Base',(x,y,z+h+.08),(1.42*r*2,1.42*r*2,.23),mat,.055)


def arch_points(width, spring, rise, cusps=7):
    return [(width*.5*math.cos(math.pi*i/56) *
             (1+.038*math.sin(cusps*math.pi*i/56)**2),
             spring+rise*math.sin(math.pi*i/56) *
             (1-.10*abs(math.sin(cusps*math.pi*i/56))))
            for i in range(57)]


def arched_panel(name, x, y, panel_width, height, depth, opening, spring, rise,
                 wall, trim, z=0, filled=False):
    """True open doorway with a sculpted cusped arch and continuous spandrel."""
    outline = arch_points(opening,spring,rise)
    if filled:
        side = opening*.5
        points = [(x-side,y,z+.28),(x+side,y,z+.28)]
        points.extend((x+a,y,z+b) for a,b in outline)
        mesh(name+'_Blind_Field-renderonly',points,[tuple(range(len(points)))],trim)
    else:
        side_width = (panel_width-opening)/2
        for sign in (-1,1):
            box(name+'_Pier',(x+sign*(opening+side_width)/2,y,z+height/2),
                (side_width,depth,height),wall,.016)
        n = len(outline)
        vertices = [(x+a,y+off,z+b) for off in [-depth/2,depth/2]
                    for a,b in outline+[(a,height) for a,b in outline]]
        faces = []
        for i in range(n-1):
            faces.extend([(i,i+1,i+1+n,i+n),(2*n+i+n,2*n+i+n+1,2*n+i+1,2*n+i),
                          (i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
        mesh(name+'_Spandrel',vertices,faces,wall)
    decor = Sculpture()
    decor.materials.append(trim)
    path = [(x+a,y-depth*.56,z+b) for a,b in outline]
    decor.tube(path,.063,0,8)
    decor.tube([(x+a*1.075,y-depth*.59,z+spring+(b-spring)*1.11)
                for a,b in outline],.039,0,8)
    for u in [-opening/2,opening/2]:
        decor.tube([(x+u,y-depth*.58,z+.22),(x+u,y-depth*.58,z+spring)],.053,0)
    decor.finish(name+'_Cusped_Moulding-renderonly')


def column(name, x, y, z, h, trim):
    profile = [(0,.23),(.08,.23),(.13,.18),(.19,.21),(.31,.15),
               (h-.43,.15),(h-.29,.19),(h-.20,.19),(h-.14,.26),(h,.26)]
    rings(name,(x,y,z),profile,trim,8,.5)


def perimeter(name, x0, x1, y0, y1, z, height, m):
    for x in (x0,x1):
        box(name+'_Side',(x,(y0+y1)/2,z+height/2),(.35,y1-y0,height),m,.025)
    box(name+'_Back',((x0+x1)/2,y1,z+height/2),(x1-x0,.38,height),m,.025)


def cornice(name, center, w, d, height, m):
    for level,extent,thickness in [(0,0,.23),(.215,.16,.12),(.345,.21,.16),(.46,.12,.12)]:
        box(name+'_Cornice',(center[0],center[1],height+level),
            (w+extent,d+extent,thickness),m,.025)


def stone_band(name, x0, x1, y, z, mat, accent):
    design = Sculpture()
    design.materials.extend([mat,accent])
    for i in range(math.floor((x1-x0)/.28)):
        x = x0+.14+i*.28
        design.rosette((x,y,z),.105,0,1,petals=6)
    design.finish(name+'-renderonly')


def steps_x(name, x0, x1, y, width, z, rise, count, mat):
    d = (x1-x0)/count
    for i in range(count):
        h = z + rise*(i+1)/count
        box(name+f'_{i+1:02d}-renderonly',(x0+(i+.5)*d,y,h-.10),
            (abs(d)+.012,width,.20),mat,.018)
    points = [(x0,y-width/2,z),(x1,y-width/2,z+rise),
              (x1,y+width/2,z+rise),(x0,y+width/2,z)]
    if x1<x0:
        points.reverse()
    mesh(name+'_Collision-colonly',points,[(0,1,2,3)],mat)


def main_shrine(m):
    x0,x1,y0,y1 = -5.7,5.7,7.3,18.1
    s = m['white']
    floor = .24
    perimeter('Main_Sanctuary',x0,x1,y0,y1,floor,3.84,s)
    arched_panel('Silver_Folding_Door',0,y0,11.4,3.84,.36,2.30,2.05,.78,
                 s,m['silver'],floor)
    # Folded silver leaves stay clear of the visitor route.
    for sign in (-1,1):
        x = sign*1.30
        door = box('Folded_Silver_Door_Leaf',(x,y0+.28,1.48),(.76,.075,2.48),m['silver'],.026)
        door.rotation_euler.z = sign*.47
        stone_band('Door_Small_Repousse_Flowers',x-.29,x+.30,y0+.22,1.41,m['silver'],m['dark_silver'])
    box('Sanctuary_Roof', (0,(y0+y1)/2,4.26),(11.6,11.0,.38),m['charcoal'],.035)
    cornice('Sanctuary_Eaves',(0,(y0+y1)/2),11.75,11.13,4.02,s)
    cupola('Shri_Jawala_Main',0,PIT_Y,4.58,4.29,1.74,m,square=True)
    for x in (-5.12,5.12):
        for y in (7.95,17.38):
            cupola('Main_Corner_Gilded_Spire',x,y,4.58,.63,.72,m)
    for x in (-4.15,-2.90,2.90,4.15):
        arched_panel('Sanctuary_Blind_Side_Arch',x,7.08,1.13,2.35,.15,.78,1.53,.42,
                     s,m['warm'],.43,filled=True)
        marble_jali('Sanctuary_Front_Jali',x,6.94,.74,m)
    stone_band('Main_Front_Eave_Floral_Band',-5.58,5.58,7.11,3.87,s,m['warm'])
    # The small gilded entry canopy in front of the broader main dome.
    box('Main_Entry_Antechamber_Roof',(0,5.52,3.10),(4.51,4.12,.23),m['charcoal'],.035)
    cornice('Main_Entry_Eaves',(0,5.52),4.64,4.22,3.05,s)
    for x in (-2.06,2.06):
        box('Main_Entry_Return',(x,5.67,1.71),(.38,3.64,2.95),s,.027)
    arched_panel('Main_Courtyard_Entrance',0,3.59,4.4,2.91,.32,2.04,1.85,.64,
                 s,m['warm'],.23)
    cupola('Front_Gilded_Antechamber',0,5.39,3.62,1.75,1.05,m,square=True)
    for x in (-1.90,1.90):
        cupola('Entry_Companion_Pinnacle',x,4.02,3.60,.31,.31,m)
    awning('Main_Entry_Striped_Awning',0,3.41,4.24,2.70,m)
    box('Main_Entry_Floor',(0,5.40,.116),(4.36,4.18,.232),s)
    box('Main_Entry_Threshold',(0,3.06,.061),(2.48,.48,.122),s,.018)
    strip = 1.18
    for name,a,b,c,d in [
        ('South',-5.7,5.7,7.30,PIT_Y-strip),
        ('North',-5.7,5.7,PIT_Y+strip,18.12),
        ('West',-5.7,-strip,PIT_Y-strip,PIT_Y+strip),
        ('East',strip,5.7,PIT_Y-strip,PIT_Y+strip)]:
        surface('Ground_Jyoti_Circumambulation_'+name,a,b,c,d,floor,s)
    jyoti(m)
    anchor('Sanctum_Lamp_Position',(1.37,PIT_Y-1.63,.97))
    anchor('Silver_Door_Reference',(0,7.47,1.65))
    anchor('Landing_Silver_Door',(0,5.05,.27))


def jyoti(m):
    y = PIT_Y
    s = m['silver']
    rock = m['rock']
    box('Jyoti_Pit_Stone_Floor',(0,y,-.755),(2.38,2.38,.17),rock,.025)
    for sign in (-1,1):
        box('Fissure_Pit_Stone_Wall',(sign*1.24,y,-.27),(.16,2.58,.96),rock,.045)
        box('Fissure_Pit_Stone_Wall',(0,y+sign*1.24,-.27),(2.38,.16,.96),rock,.045)
        box('Low_Silver_Fissure_Pit_Rim',(sign*1.24,y,.30),(.22,2.61,.17),s,.026)
        box('Low_Silver_Fissure_Pit_Rim',(0,y+sign*1.24,.30),(2.42,.22,.17),s,.026)
    # The temple's Jyoti photograph shows silver arches and a red, floral
    # setting around an open natural fissure. This is an original rendering.
    for x in (-.90,.90):
        column('Repousse_Jyoti_Silver_Column',x,y-.27,-.54,2.23,s)
    box('Jyoti_Red_Backdrop',(0,y+.33,.41),(1.71,.085,1.88),m['deep_red'],.018)
    arched_panel('Mahakali_Silver_Fissure_Surround',0,y-.29,1.87,2.21,.105,1.00,.72,.61,
                 s,m['gold'],-.54)
    for x in (-.72,.72):
        for level in (.03,.24,.45,.66,.87,1.08,1.29,1.50):
            stone_band('Jyoti_Silver_Floral_Work',x-.148,x+.148,y-.36,level,s,m['dark_silver'])
    box('Jyoti_Silver_Cornice',(0,y-.26,1.68),(2.02,.38,.13),s,.023)
    petals = Sculpture()
    petals.materials.extend([m['marigold'],m['deep_red'],m['gold']])
    rng = random.Random(155)
    for j in range(32):
        x = rng.uniform(-.61,.61)
        z = rng.uniform(-.44,-.30)
        dy = rng.uniform(-.46,-.21)
        petals.ellipsoid((x,y+dy,z),(.056,.043,.025),j%3,12,7)
    for sign in (-1,1):
        for j in range(32):
            p = j/31
            petals.ellipsoid((sign*(.34+.51*p),y-.41,.85+.85*p*p),
                             (.052,.052,.054),j%3,12,7)
    petals.finish('Jyoti_Marigold_And_Red_Flower_Garlands-renderonly')
    identities = [
        ('Mahakali',0,-.39,-.37,0,-2.18),
        ('Annapurna',-.87,-.95,-.30,-2.19,-1.11),
        ('Chandi',-1.02,-.34,-.28,-2.27,-.33),
        ('Hinglaj',-1.02,.41,-.32,-2.28,.42),
        ('Vindhyavasini',-.63,.97,-.30,-.81,2.22),
        ('Mahalakshmi',.26,1.02,-.29,.38,2.25),
        ('Saraswati',.99,.82,-.25,2.23,.91),
        ('Ambika',1.02,.18,-.29,2.23,.17),
        ('Anjana',.92,-.84,-.33,2.19,-1.0),
    ]
    for index,(name,x,dy,z,lx,ly) in enumerate(identities):
        flame_y = y+dy
        stone = Sculpture()
        stone.materials.append(rock)
        stone.ellipsoid((x,flame_y,z-.06),(.22,.18,.12),0,14,8)
        stone.finish('Jyoti_Natural_Vent_'+name)
        flame = Sculpture()
        flame.materials.extend([m['blue_fire'],m['amber_fire']])
        scale = .20 if index == 0 else .11 + (index%3)*.018
        flame.ellipsoid((x,flame_y-.025,z+.035),(.049,.036,scale*.48),0)
        flame.ellipsoid((x+.018,flame_y-.026,z+scale*.55),(.026,.022,scale*.47),1)
        flame.finish('Flame_Jyoti_'+name+'-renderonly')
        anchor('SacredFlame_'+name,(x,flame_y,z+scale*.65))
        anchor('Landing_Jyoti_'+name,(lx,y+ly,.27))


def marble_jali(name, x, y, z, m):
    lattice = Sculpture()
    lattice.materials.append(m['warm'])
    for u in range(4):
        for v in range(5):
            center_x = x+(u-1.5)*.135
            center_z = z+v*.138
            diamonds = [(center_x,y,center_z-.067),(center_x+.067,y,center_z),
                        (center_x,y,center_z+.067),(center_x-.067,y,center_z)]
            lattice.tube(diamonds+diamonds[:1],.009,0,6)
    box(name+'_Shadow',(x,y+.021,z+.276),(.55,.052,.703),m['charcoal'],.015)
    lattice.finish(name+'-renderonly')


def awning(name, x, y, width, z, m):
    for index in range(22):
        a = x+width*(index/22-.5)
        b = a+width/22+.011
        vertices = [(a,y-.88,z-.24),(b,y-.88,z-.24),(b,y+.06,z),(a,y+.06,z)]
        mesh(name+f'_{index:02d}-renderonly',vertices,[(0,1,2,3),(3,2,1,0)],
             m['white' if index%2 else 'vermilion'])
    for sign in (-1,1):
        column(name+'_Support',x+sign*(width/2-.08),y-.75,.035,z-.27,m['brass'])


def seja_bhawan(m):
    center = (0,-31.45)
    y0,y1 = -36.9,-25.95
    x0,x1 = -10.8,10.8
    wall = m['rose_marble']
    # The broad paired-arch hall opposite the main temple has its own gilt
    # roof and four corner cupolas. The resting place lies inside.
    mesh('Ground_Seja_Bhawan',[(x0,y0,.17),(x1,y0,.17),(x1,y1,.17),(x0,y1,.17)],[(0,1,2,3)],m['white'])
    for x in (x0,x1):
        box('Seja_Bhawan_Return',(x,center[1],1.95),(.39,y1-y0,3.56),wall,.026)
    box('Seja_Bhawan_Back_Wall',(0,y0,1.95),(21.6,.40,3.56),wall,.026)
    box('Seja_Bhawan_Roof',(0,center[1],3.89),(21.8,11.28,.33),m['charcoal'],.035)
    for i in (-1,1):
        before = set(bpy.context.scene.objects)
        arched_panel('Seja_Bhawan_Paired_Door',i*1.08,-y1,2.16,3.58,.36,1.70,1.97,.68,
              wall,m['warm'],.16)
        turn = Matrix.Rotation(math.pi,4,'Z')
        bpy.context.view_layer.update()
        for obj in set(bpy.context.scene.objects)-before:
            obj.matrix_world = turn @ obj.matrix_world
    for sign in (-1,1):
        box('Seja_Bhawan_Front_Wall',(sign*6.48,y1,1.95),(8.64,.40,3.58),wall,.027)
        for x in (3.10,5.0,6.91,8.83,10.39):
            column('Seja_Facade_Engaged_Pier',sign*x,y1+.22,.17,3.26,m['white'])
        for x in (4.03,5.96,7.89,9.65):
            before = set(bpy.context.scene.objects)
            marble_jali('Seja_Facade_Lattice',sign*x,-y1-.24,.87,m)
            turn = Matrix.Rotation(math.pi,4,'Z')
            bpy.context.view_layer.update()
            for obj in set(bpy.context.scene.objects)-before:
                obj.matrix_world = turn @ obj.matrix_world
        stone_band('Seja_Facade_Rosette_Band',sign*6.5-4.13,sign*6.5+4.13,
                   y1+.245,3.38,m['white'],m['warm'])
    cornice('Seja_Bhawan_Eaves',center,22.1,11.46,3.76,wall)
    cupola('Seja_Main_Dome',0,-32,4.30,3.43,1.89,m)
    for x in (-8.56,8.56):
        for y in (-35.00,-27.45):
            cupola('Seja_Corner_Cupola',x,y,4.30,.99,.83,m)
    box('Seja_Resting_Platform',(0,-33.83,.43),(2.8,1.84,.52),m['brass'],.045)
    box('Seja_Resting_Textile-renderonly',(0,-33.83,.76),(2.56,1.68,.24),m['deep_red'],.072)
    box('Seja_Cushion-renderonly',(0,-34.34,.92),(1.56,.49,.24),m['vermilion'],.081)
    for x in (-1.47,1.47):
        for y in (-34.76,-32.93):
            column('Seja_Canopy_Post',x,y,.17,2.31,m['brass'])
    box('Seja_Canopy_Cloth-renderonly',(0,-33.87,2.53),(3.31,2.26,.21),m['deep_red'],.038)
    anchor('Shaiya_Bhawan_Reference',(0,-33.65,.93))
    anchor('Landing_Shaya_Bhawan',(0,-30.89,.20))

def paduka(m, x, y):
    rings('Charan_Paduka_Marble_Plinth',(x,y,0),
          [(0,1.08),(.08,1.08),(.15,.96),(.28,.90),(.34,.98),(.42,.98)],m['white'],12)
    rings('Charan_Paduka_Embossed_Brass_Plate',(x,y,.41),
          [(0,.84),(.055,.89),(.085,.84),(.125,.73)],m['brass'],14)
    feet = Sculpture()
    feet.materials.extend([m['brass'],m['deep_red'],m['marigold']])
    for sign in (-1,1):
        foot = x+sign*.237
        feet.ellipsoid((foot,y+.11,.566),(.171,.30,.056),0)
        feet.ellipsoid((foot,y+.306,.553),(.129,.21,.041),0)
        for toe in range(5):
            scale = .056-toe*.006
            feet.ellipsoid((foot+sign*(toe-2)*.059,y-.186+toe*.022,.565),
                           (scale,.078-toe*.009,.038),0,12,8)
    for i in range(42):
        ang = math.tau*i/42
        rad = .70+.066*math.sin(i*.8)
        feet.ellipsoid((x+rad*math.cos(ang),y+rad*math.sin(ang),.55),
                       (.067,.069,.034),1+(i%2),10,6)
    feet.finish('Charan_Paduka_Pair_And_Flower_Offerings-renderonly')
    anchor('Charan_Paduka_Reference',(x,y,.55))
    anchor('Landing_Charan_Paduka',(x+1.86,y-.03,.04))


def courtyard_pavilion(name, x, y, r, m):
    box(name+'_Square_Marble_Base',(x,y,.12),(2*r+.34,2*r+.34,.24),m['white'],.045)
    s = m['white']
    for dx in (-r*.80,r*.80):
        for dy in (-r*.78,r*.78):
            column(name+'_Octagonal_Bay_Pier',x+dx,y+dy,.24,2.05,s)
    cornice(name+'_Eaves',(x,y),2*r+.28,2*r+.24,2.25,s)
    cupola(name,x,y,2.82,r*.84,r*.80,m,gold=False)


def branches(name, x, y, r, m):
    rng = random.Random(87)
    canopy = Sculpture()
    canopy.materials.extend(m['leaves'])
    bark = Sculpture()
    bark.materials.append(m['bark'])
    bark.tube([(x,y,.25),(x-.34,y,2.18),(x-.25,y+.31,4.6)],.46,0,11)
    for i in range(12):
        angle = i*math.tau/12
        dx,dy = math.cos(angle),math.sin(angle)
        span = r*rng.uniform(.25,.73)
        h = rng.uniform(3.8,5.3)
        bark.tube([(x-.17,y+.1,2.4),(x+dx*span*.64,y+dy*span*.64,h-.70),
                   (x+dx*span,y+dy*span,h)],.13,0,7)
        for j in range(5):
            a,b = rng.uniform(-1.30,1.30),rng.uniform(-1.30,1.30)
            canopy.ellipsoid((x+dx*span+a,y+dy*span+b,h+rng.uniform(.04,.98)),
                             (rng.uniform(.87,1.65),rng.uniform(.90,1.57),rng.uniform(.65,1.35)),
                             (i+j)%len(m['leaves']),12,7)
    bark.finish(name+'_Tree_Trunk')
    canopy.finish(name+'_Tree_Canopy-renderonly')


def courtyard(m):
    box('Ground_Temple_Courtyard',((WEST+EAST)/2,(SOUTH+NORTH)/2,-.13),
        (EAST-WEST,NORTH-SOUTH,.26),m['ground'])
    tile_field('Ground_Courtyard_Checkered',(WEST,EAST,-25.96,NORTH),.013,.51,
               (m['white'],m['warm_tile']))
    tile_field('Ground_Entrance_Chequer',(WEST,-10.9,SOUTH,-25.96),.013,.49,
               (m['white'],m['warm_tile']))
    tile_field('Ground_East_Chequer',(11.0,EAST,SOUTH,-25.96),.013,.49,
               (m['white'],m['warm_tile']))
    tile_field('Ground_Tree_Chequer',(1.1,10.0,-5.85,3.0),.026,.46,
               (m['white'],m['charcoal']))
    for x in (WEST+.24,EAST-.24):
        box('Court_Retaining_Parapet',(x,-15,.50),(.38,43.8,1.0),m['white'],.03)
    for x,length in [(-13.7,13.8),(16.8,17.5)]:
        box('Southern_Court_Parapet',(x,SOUTH+.21,.55),(length,.46,1.1),m['white'],.025)
    for i in range(11):
        y = -23+i*2.29
        box('West_Open_Colonnade_Pier',(-17.8,y,1.30),(.46,.46,2.60),m['white'],.033)
    box('West_Long_Roofed_Gallery',(-19.32,-11.55,2.72),(3.4,25.65,.28),m['charcoal'],.04)
    # Three small white domed forms stand between the two gold-roofed
    # buildings. Only documented ritual identities receive names.
    courtyard_pavilion('Court_Octagonal_Pavilion_West',-5.8,-13.05,1.52,m)
    courtyard_pavilion('Court_Octagonal_Pavilion_Middle',.08,-14.45,1.72,m)
    courtyard_pavilion('Court_Octagonal_Pavilion_East',6.1,-14.6,1.51,m)
    rings('Court_Tree_Stone_Platform',(5.1,-1.15,0),
          [(0,2.34),(.20,2.34),(.30,2.41),(.43,2.41)],m['white'],0,1.2)
    branches('Jawala_Courtyard',5.1,-1.15,4.2,m)
    box('Seja_Darshan_Red_Aisle',(0,-21.9,.028),(2.21,8.0,.026),m['deep_red'],.015)
    for x in (-4.6,7.2):
        rings('Tall_Temple_Flagpole',(x,-9,0),[(0,.18),(.32,.18),(.38,.05),(13,.04)],m['brass'])
        mesh('Red_Temple_Pennant-renderonly',[(x,-9,13),(x+1.2,-9.15,12.64),
             (x+.13,-8.99,12.41)],[(0,1,2),(2,1,0)],m['vermilion'])
    paduka(m,-16.55,-29.1)
    yogini_kund(m)
    anchor('Spawn_Point',(-15.55,-35.0,.065))
    anchor('Arrival_Facing',(-15.55,-6.0,.3))
    anchor('Courtyard_Approach',(-15.75,-27.25,1.08))
    anchor('Landing_Courtyard_Approach',(-15.57,-31.05,.04))


def yogini_kund(m):
    x,y = -12.75,-28.1
    for side in (-1,1):
        box('Yogini_Kund_Marble_Rim',(x+side*.78,y,.36),(.20,1.72,.72),m['white'],.036)
        box('Yogini_Kund_Marble_Rim',(x,y+side*.78,.36),(1.36,.20,.72),m['white'],.036)
    box('Yogini_Kund_Inner_Basin',(x,y,.19),(1.36,1.36,.14),m['rock'],.036)
    anchor('Yogini_Kund_Reference',(x,y,.48))
    anchor('Landing_Yogini_Kund',(x,y-2.18,.045))


def offering_gallery(m):
    x,y = 14.05, 2.48
    for px in (x-2.78,x+2.78):
        for py in (y-2.72,y+2.72):
            column('Offering_Gallery_Pier',px,py,0,2.70,m['white'])
    box('Offering_Gallery_Roof',(x,y,2.85),(6.0,6.0,.27),m['white'],.052)
    box('Akbar_Chhatra_Display_Plinth',(x,y,.42),(2.54,2.32,.84),m['wood'],.06)
    for px in (x-1.19,x+1.19):
        for py in (y-1.08,y+1.08):
            box('Chhatra_Display_Case_Frame',(px,py,1.11),(.041,.041,.55),m['brass'])
    for py in (y-1.09,y+1.09):
        box('Chhatra_Protective_Display_Edge',(x,py,1.37),(2.44,.043,.043),m['brass'])
    for px in (x-1.20,x+1.20):
        box('Chhatra_Protective_Display_Edge',(px,y,1.37),(.043,2.22,.043),m['brass'])
    # Artifact silhouette recorded in the on-site commons photograph.
    rings('Akbar_Chhatra_Patinated_Canopy',(x,y,.85),
          [(0,1.02),(.050,1.02),(.064,.94),(.083,.76),(.095,.70),
           (.120,.61),(.137,.57),(.164,.35),(.174,.28),(.213,.12),(.216,.08)],m['patina'])
    rings('Akbar_Chhatra_Central_Fitting',(x,y,1.06),
          [(0,.157),(.018,.172),(.038,.116),(.078,.11),(.093,.081)],m['patina'])
    anchor('Akbar_Chhatra_Reference',(x,y,.99))
    anchor('Landing_Akbar_Chhatra',(x,y-2.09,.045))


def radha_krishna_study(m,x,y,base):
    # General Vaishnava iconography. Installed images remain unverified.
    sculpture = Sculpture()
    dark = sculpture.material('Jawala_Krishna_Dark_Stone',(.055,.063,.072))
    light = sculpture.material('Jawala_Radha_Pale_Stone',(.75,.65,.50))
    gold = sculpture.material('Jawala_Paired_Crowns',(.74,.42,.06),.65)
    green = sculpture.material('Jawala_Dhoti_Emerald',(.025,.30,.16))
    pink = sculpture.material('Jawala_Radha_Rose_Drape',(.45,.034,.105))
    for index,(body,cloth) in enumerate([(dark,green),(light,pink)]):
        dx = x+(-.39 if index == 0 else .39)
        sculpture.ellipsoid((dx,y,base+.51),(.183,.11,.26),cloth)
        sculpture.ellipsoid((dx,y,base+.72),(.16,.105,.25),body)
        sculpture.ellipsoid((dx,y,base+.98),(.100,.083,.123),body)
        sculpture.ellipsoid((dx,y,base+1.105),(.118,.089,.089),gold)
        for sign in (-1,1):
            sculpture.tube([(dx+sign*.061,y,base+.18),(dx+sign*.070,y,base+.36),
                            (dx+sign*.078,y,base+.57)],.046,cloth,9)
            end = (dx+sign*(.125 if index==0 else .16),y-.097,base+(.88 if index==0 else .62))
            sculpture.tube([(dx+sign*.12,y,base+.81),(dx+sign*.184,y-.03,base+.69),end],
                           .043,body,8)
        if index == 0:
            sculpture.tube([(dx-.25,y-.105,base+.884),(dx+.27,y-.105,base+.903)],.015,gold,9)
    sculpture.finish('Radha_Krishna_Iconographic_Study-renderonly')


def upper_terrace(m):
    west = 9.45
    y = 13.15
    z = 1.68
    steps_x('Gorakh_Dibbi_Ten_Treads',5.67,west,y,2.70,.04,z-.04,10,m['white'])
    for offset in (-1.48,1.48):
        points = [(5.67,y+offset-.055,.13),(west,y+offset-.055,z+.43),
                  (west,y+offset+.055,z+.43),(5.67,y+offset+.055,.13)]
        mesh('Dibbi_Stair_Side_Rail-renderonly',points,[(0,1,2,3)],m['brass'])
    box('Ground_Upper_Dibbi_Terrace',(16.45,13.72,z-.18),(14.2,11.82,.36),m['white'],.038)
    # Low riser reached from the forecourt around the right side of the sanctum.
    box('Ground_Dibbi_Stair_Start',(6.36,12.89,.015),(2.1,3.17,.03),m['white'])
    perimeter('Gorakh_Dibbi_Walls',11.20,16.38,13.63,19.66,z,3.12,m['rose_marble'])
    arched_panel('Gorakh_Dibbi_Door',(11.20+16.38)/2,13.63,5.18,3.12,.38,1.96,1.91,.56,
                 m['rose_marble'],m['white'],z)
    box('Gorakh_Dibbi_White_Roof',(13.69,16.64,z+3.28),(5.61,6.43,.31),m['white'],.046)
    cupola('Gorakh_Dibbi_Low_Dome',13.80,16.64,z+3.47,1.17,.79,m,gold=False)
    for a in range(4):
        ang=math.pi*a/2
        px,py=13.80+.96*math.cos(ang),17.50+.96*math.sin(ang)
        o=box('Gorakh_Dibbi_Kund_Rim',(px,py,z+.42),(1.77,.23,.25),m['charcoal'],.041)
        o.rotation_euler.z=ang+math.pi/2
    box('Gorakh_Dibbi_Kund_Basin',(13.80,17.50,z+.17),(1.86,1.86,.30),m['rock'],.062)
    surface('Gorakh_Dibbi_Water-renderonly',13.01,14.59,16.71,18.29,z+.343,m['water'])
    bubbles = Sculpture()
    bubbles.materials.append(m['water_ripple'])
    for i in range(13):
        a=math.tau*i/13
        bubbles.ellipsoid((13.80+math.cos(a)*.43,17.50+math.sin(a)*.42,z+.356),
                          (.027,.027,.016+(i%3)*.01),0,9,6)
    bubbles.finish('Gorakh_Dibbi_Water_Bubbles-renderonly')
    anchor('Gorakh_Dibbi_Reference',(13.80,17.50,z+.41))
    anchor('Landing_Gorakh_Dibbi',(13.78,15.30,z+.035))
    perimeter('Radha_Krishna_Temple',17.93,23.24,13.45,19.51,z,2.99,m['rose_marble'])
    arched_panel('Radha_Krishna_Threshold',20.585,13.45,5.31,2.99,.34,2.11,1.87,.69,
                 m['rose_marble'],m['white'],z)
    box('Radha_Krishna_Roof',(20.585,16.47,z+3.19),(5.67,6.50,.30),m['white'],.049)
    cupola('Radha_Krishna_White_Dome',20.585,16.47,z+3.37,1.60,1.10,m,gold=False)
    box('Radha_Krishna_Pedestal',(20.14,17.88,z+.40),(2.16,1.36,.80),m['white'],.061)
    radha_krishna_study(m,20.14,17.83,z+.81)
    anchor('Radha_Krishna_Reference',(20.14,17.82,z+1.51))
    anchor('Landing_Radha_Krishna',(20.14,15.22,z+.04))
    box('Upper_Terrace_East_Guard',(23.55,13.76,z+.52),(.25,11.7,1.04),m['white'],.04)
    box('Upper_Terrace_Front_Guard',(16.80,7.92,z+.48),(13.9,.29,.96),m['white'],.035)
    shiva_shakti(m)


def shiva_shakti(m):
    # This stair continues directly from the Dibbi terrace. The local
    # authority identifies the linga and Jyoti and describes fifteen steps.
    x = 16.91
    lower, upper = 1.68,4.08
    y0,y1 = 15.72,21.20
    for index in range(15):
        t = (index+1)/15
        y = y0+(y1-y0)*(index+.5)/15
        box('Shiva_Shakti_Fifteen_Steps-renderonly',(x,y,lower+(upper-lower)*t-.09),
            (1.54,(y1-y0)/15+.015,.18),m['white'],.017)
    ramp = [(x-.77,y0,lower),(x+.77,y0,lower),(x+.77,y1,upper),(x-.77,y1,upper)]
    mesh('Shiva_Shakti_Stair_Collision-colonly',ramp,[(0,1,2,3)],m['white'])
    box('Ground_Shiva_Shakti_Terrace',(16.86,24.43,upper-.19),(7.84,6.50,.38),m['white'],.039)
    perimeter('Shiva_Shakti_Temple',14.2,19.55,23.2,27.18,upper,3.03,m['rose_marble'])
    arched_panel('Shiva_Shakti_Entrance',16.86,23.20,5.35,3.03,.38,1.97,1.88,.67,
                 m['rose_marble'],m['white'],upper)
    box('Shiva_Shakti_Roof',(16.86,25.17,upper+3.13),(5.68,4.30,.28),m['white'],.041)
    cupola('Shiva_Shakti_Domed_Roof',16.86,25.17,upper+3.32,1.49,1.25,m,gold=False)
    linga('Shiva_Shakti_Linga',(16.86,25.53,upper+.09),.83,m['rock'])
    lamp = Sculpture()
    lamp.materials.extend([m['brass'],m['amber_fire']])
    lamp.ellipsoid((17.60,25.33,upper+.14),(.18,.146,.052),0)
    lamp.ellipsoid((17.60,25.27,upper+.21),(.027,.025,.060),1)
    lamp.finish('Shiva_Shakti_Jyoti_Lamp-renderonly')
    anchor('Shiva_Shakti_Reference',(16.86,25.53,upper+.53))
    anchor('Landing_Shiva_Shakti',(16.86,24.09,upper+.039))


def hillside(m):
    # The hillside backdrop is contextual. The uphill temples shown in
    # the reference panorama are beyond the walkable main compound.
    box('Ground_Processional_Plaza',(-1.30,9.26,-.19),(53.6,5.35,.38),m['ground'])
    box('Ground_Right_Circumambulation',(17.2,11.1,-.16),(24,10.1,.32),m['ground'])
    box('Ground_Hillside_Left',(-12.42,12.21,-.19),(12.7,11.35,.38),m['ground'])
    box('Ground_Hillside_Valley', (0,0,-3.55), (190,150,.33),m['earth'])
    massing = [
        (-10.75,21.0,11,7.1,7.2,m['peach']),
        (2.50,22.94,13.8,7.6,9.4,m['peach']),
        (22.83,28.78,5.05,4.65,7.7,m['white']),
    ]
    for index,(x,y,w,d,h,mat) in enumerate(massing):
        box('North_Hillside_Service_Block',(x,y,h/2),(w,d,h),mat,.061)
        box('Hillside_Service_Block_Eaves',(x,y,h),(w+.45,d+.46,.21),m['charcoal'],.036)
        for level in range(1,math.ceil(h/2.32)):
            z=1.1+level*1.95
            for j in range(2,math.floor(w/1.60)):
                win_x=x-w/2+j*1.60
                box('Context_Hillside_Window-renderonly',(win_x,y-d/2-.059,z),
                    (.71,.09,.94),m['charcoal'],.020)
    contour = [(-75,23,0),(-53,25,1),(-27,26,1),(-10,26,3),(4,28,2),(22,26,2),(42,23,2),(75,19,-1)]
    vertices=[]
    for i in range(6):
        for x,y,z in contour:
            vertices.append((x+(i*1.8 if x>0 else -i*2.1),y+i*10,
                             z+i*(4.2+1.5*math.sin(x*.11)+.8*math.sin(x*.34))))
    n=len(contour)
    faces=[(a*n+i,a*n+i+1,(a+1)*n+i+1,(a+1)*n+i)
           for a in range(5) for i in range(n-1)]
    hill=mesh('Terrain_Kalidhar_Rise-renderonly',vertices,faces,m['foliage'])
    for poly in hill.data.polygons:
        poly.use_smooth=True
    for x,y,r in [(-20.6,20.5,4.2),(-15.6,25.6,4.3),(10.3,29.4,4.1),(26,21.4,3.8),
                  (-22.7,4.3,3.7),(26.9,-15.1,3.2),(-25.3,-32.9,3.5)]:
        branches('Kalidhar_Hillside',x,y,r,m)


def build():
    clear_scene()
    m = {
        'gold': material('Jawala_Hammered_Gilt',(.60,.31,.063),.37,.60),
        'brass': material('Jawala_Brass_Offerings',(.59,.36,.106),.33,.54),
        'silver': material('Jawala_Silver_Repousse',(.54,.55,.54),.26,.62),
        'dark_silver': material('Jawala_Weathered_Silver',(.28,.27,.25),.45,.46),
        'white': material('Jawala_White_Marble',(.49,.455,.391),.60),
        'rose_marble': create_granite_stone('Jawala_Cream_Rose_Marble',(.54,.415,.322,1),.67),
        'warm': material('Jawala_Warm_Mouldings',(.44,.327,.228),.69),
        'warm_tile': material('Jawala_Tan_Marble_Checks',(.215,.144,.081),.72),
        'charcoal': material('Jawala_Dark_Slate',(.13,.15,.15),.77),
        'ground': material('Jawala_Court_Stone',(.48,.42,.34),.79),
        'peach': material('Jawala_Peach_Hillside_Walls',(.57,.37,.28),.89),
        'rock': create_granite_stone('Jawala_Natural_Rock',(.13,.114,.094,1)),
        'earth': material('Jawala_Hillside_Earth',(.122,.167,.076)),
        'foliage': material('Jawala_Forested_Hill',(.112,.213,.075)),
        'bark': material('Jawala_Tree_Bark',(.11,.075,.042)),
        'leaves': [material('Jawala_Foliage_'+str(i),color) for i,color in enumerate([
            (.080,.163,.050),(.11,.205,.061),(.145,.25,.082),(.095,.185,.058)])],
        'water': material('Jawala_Dibbi_Water',(.056,.141,.119),.33),
        'water_ripple': material('Jawala_Dibbi_Bubble',(.19,.35,.29),.29),
        'wood': material('Jawala_Display_Wood',(.13,.063,.033),.67),
        'patina': material('Jawala_Chhatra_Patinated_Metal',(.217,.163,.092),.47,.56),
        'deep_red': material('Jawala_Ritual_Cloth',(.422,.026,.040),.68),
        'vermilion': material('Jawala_Vermilion_Textile',(.57,.041,.028),.65),
        'marigold': material('Jawala_Marigold',(.96,.29,.011),.58),
        'blue_fire': material('Jawala_Flame_Blue',(.025,.105,.68),.35,emission=1.35),
        'amber_fire': material('Jawala_Flame_Amber',(.81,.26,.034),.31,emission=1.36),
    }
    hillside(m)
    courtyard(m)
    main_shrine(m)
    seja_bhawan(m)
    offering_gallery(m)
    upper_terrace(m)
    # North end of the main hall and its court are skewed on the aerial.
    rotation = Matrix.Rotation(math.radians(14),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        obj.matrix_world = rotation @ obj.matrix_world


build()
if not globals().get('DEFER_GLB_EXPORT', False):
    finish('jwalamukhi_vaishnavi')
