"""Sharada Peeth as a roofless monument, following the survey and field plan."""
import math
import random

import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene
from common_materials import create_granite_stone
from present_day_sites import anchor, box, finish, material


COURT = 15.75
GATE_Y = -4.0
WEST = -17.5
EAST = 17.5
NORTH = 13.0
SOUTH = -13.0
STAIR_START = -47.79
STAIR_END = -20.70


def mesh(name, vertices, faces, surface):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(surface)
    return obj


def stair(name, start, end, y, width, base, rise, count, palette):
    tread = (end - start) / count
    for index in range(count):
        top = base + rise * (index + 1) / count
        box(f'{name}_{index+1:02d}-renderonly',
            (start + (index + .5) * tread, y, top - .14),
            (tread + .016, width, .28), palette[index % len(palette)], .025)
    # Continuous physics surface for the documented 25 cm high stone treads.
    near, far = y - width / 2, y + width / 2
    vertices = [(start, near, base), (end, near, base + rise),
                (end, far, base + rise), (start, far, base)]
    mesh(name + '_Ramp-colonly', vertices, [(0, 1, 2, 3)], palette[0])


def wall(name, a, b, base, height, width, palette, seed, decay=0):
    rng = random.Random(seed)
    length = (Vector(b) - Vector(a)).length
    direction = (Vector(b) - Vector(a)).normalized()
    angle = math.atan2(direction.y, direction.x)
    rows = max(1, round(height / .49))
    course = height / rows
    for row in range(rows):
        columns = max(1, round(length / (1.48 if row % 2 else 1.75)))
        cuts = [0] + [length * i / columns + rng.uniform(-.26, .26)
                      for i in range(1, columns)] + [length]
        for start, end in zip(cuts, cuts[1:]):
            if row == rows - 1 and rng.random() < decay:
                continue
            x, y = Vector(a) + direction * ((start + end) / 2)
            h = course * rng.uniform(.94, 1.02)
            obj = box(name, (x, y, base + row * course + h/2),
                      (end-start-.012, width*rng.uniform(.97, 1.02), h),
                      rng.choice(palette), rng.uniform(.036, .075))
            for vertex in obj.data.vertices:
                vertex.co += Vector((rng.uniform(-.018,.018),rng.uniform(-.025,.025),
                                     rng.uniform(-.026,.026)))
            obj.rotation_euler.z = angle + rng.uniform(-.013,.013)


def ornament(name, center, normal, outline, depth, surface):
    """Extruded relief band expressed in the face's horizontal/vertical plane."""
    origin = Vector(center)
    outward = Vector(normal)
    along = Vector((-normal[1], normal[0], 0))
    vertices = [origin + along*u + Vector((0, 0, z)) + outward*d
                for d in [0, depth] for u, z in outline]
    n = len(outline)
    area = sum(outline[i][0]*outline[(i+1) % n][1] - outline[(i+1) % n][0]*outline[i][1]
               for i in range(n))
    rim = list(range(n)) if area > 0 else list(reversed(range(n)))
    faces = [tuple(reversed(rim)), tuple(i+n for i in rim)]
    faces += [(a,b,b+n,a+n) for a,b in zip(rim,rim[1:]+rim[:1])]
    mesh(name + '-renderonly', vertices, faces, surface)


def relief(name, center, normal, scale, trim, shadow):
    # Survey figures 12–14. Three lobes sit beneath the stepped triangular
    # mouldings. The backing is stone and the recess is blind.
    trefoil = [(-.86, .05), (-.86, .88), (-1.07, 1.23), (-1.02, 1.61),
               (-.76, 1.84), (-.49, 1.83), (-.45, 2.14), (-.27, 2.42),
               (0, 2.55), (.27, 2.42), (.45, 2.14), (.49, 1.83),
               (.76, 1.84), (1.02, 1.61), (1.07, 1.23), (.86, .88), (.86, .05)]
    ornament(name + '_Blind_Field', center, normal, [(u*scale, z*scale)
             for u, z in trefoil], .032, shadow)
    ornament(name + '_Trefoil_Border', Vector(center)+Vector(normal)*.03, normal,
             [(u*scale*1.12, z*scale*1.09) for u,z in trefoil] +
             [(u*scale, z*scale) for u,z in reversed(trefoil)], .11, trim)
    for index, (w, base, top) in enumerate([(1.27, 1.52, 3.28), (1.52, 1.46, 3.68)]):
        points = [(-w,base),(0,top),(w,base),(w-.11,base),
                  (0,top-.19),(-w+.11,base)]
        ornament(name + f'_Pediment_{index}', Vector(center)+Vector(normal)*(.10-index*.045),
                 normal, [(u*scale, z*scale) for u,z in points], .105, trim)


def terrace(soil, grass, palette):
    # The SW corner and south wall are lost to the Madhumati ravine.
    polygon = [(WEST,GATE_Y-3),(-14,-11),(-10,SOUTH),(EAST,SOUTH),(EAST,NORTH),(WEST,NORTH)]
    lower = [(-26,-9),(-23,-20),(-11,-22),(28,-21),(35,27),(-26,29)]
    bottom = [(-35,-13),(-30,-30),(-9,-32),(36,-32),(48,38),(-39,41)]
    vertices = [(x,y,COURT-.04) for x,y in polygon]
    vertices += [(x,y,COURT-h) for (x,y), h in zip(lower,[10,12,13,10,3,6])]
    vertices += [(x,y,-.11) for x,y in bottom]
    faces = [(i+6, (i+1)%6+6, (i+1)%6, i) for i in range(6)]
    faces += [(i+12,(i+1)%6+12,(i+1)%6+6,i+6) for i in range(6)]
    mesh('Terrain_Madhumati_Bank', vertices, faces, soil)
    mesh('Ground_Court_Surface', [(x,y,COURT) for x,y in polygon], [tuple(range(6))], grass)
    box('Ground_Valley', (0, 0, -.20), (178,137,.4), grass)
    wall('Northern_Retaining_Face', (WEST, NORTH-.3),(EAST,NORTH-.3),
         COURT-3.0, 3, 1.5, palette, 12)
    wall('East_Terrace_Retaining_Face', (EAST-.35,SOUTH),(EAST-.35,NORTH),
         COURT-1.5, 1.5, 1.6, palette, 22)


def approach(palette, trim, shadow):
    stair('Approach_Step', STAIR_START, STAIR_END, GATE_Y, 3.0, 0, COURT, 63, palette)
    box('West_Entrance_Podium', ((STAIR_END+WEST)/2,GATE_Y,COURT-.21),
        (WEST-STAIR_END+.24,6,.42), trim, .04)
    for side in (-1,1):
        side_y = GATE_Y + side*2.43
        # Five surviving stepped lengths, each with its own horizontal coping.
        for index in range(5):
            start = STAIR_START + (STAIR_END-STAIR_START)*index/5
            end = STAIR_START + (STAIR_END-STAIR_START)*(index+1)/5
            base = COURT*index/5
            top = COURT*(index+1)/5 + .48
            wall('Stair_Flanking_Wall',(start,side_y),(end,side_y),base,
                 top-base,1.92,palette,30+index+10*side)
            box('Stair_Wall_Coping', ((start+end)/2,side_y,top), (end-start+.04,2.02,.22),trim,.06)
    # Most of the south half of the double porch and its roof are lost.
    wall('West_Portal_North_Standing_Pier', (-20.1,-2.69),(-16.5,-2.69),
         COURT, 4.62, 1.12,palette,61,.2)
    wall('West_Portal_South_Stump', (-19.8,-5.61),(-16.6,-5.61),
         COURT, .94, 1.21,palette,66,.28)
    # The projecting upper courses of the remaining portal shoulder are
    # visible in the May 2026 entry photograph.
    for level, projection in [(4.01,.17),(4.20,.37),(4.39,.58),(4.57,.76)]:
        box('West_Portal_Broken_Corbel',(-19.4,-2.88-projection/2,COURT+level),
            (.96,1.02+projection,.24),palette[2],.07)
    for index, (x,y) in enumerate([(-19.93,-3.16),(-17.48,-3.13)]):
        box('Portal_Pilaster_Base',(x,y,COURT+.16),(.62,.68,.32),trim,.04)
        box('Portal_Pilaster',(x,y,COURT+1.9),(.41,.43,3.6),trim,.055)
        for level,width in [(3.67,.54),(3.86,.62),(4.11,.78)]:
            box('Portal_Pilaster_Capital',(x,y,COURT+level),(width,width,.22),trim,.035)
    relief('West_Portal_Geometric_Panel',(-20.15,-2.51,COURT+.51),(-1,0,0),.38,trim,shadow)
    anchor('West_Gateway_Remains',(-16.9,-2.90,COURT+1.42))
    anchor('Landing_West_Gateway',(-14.05,GATE_Y-.10,COURT+.03))
    anchor('Western_Steps_View',(STAIR_START+1.7,GATE_Y,1.1))
    anchor('Landing_Western_Steps',(STAIR_START-2.7,GATE_Y,.03))
    anchor('Spawn_Point',(STAIR_START-10.6,GATE_Y,.03))
    anchor('Arrival_Facing',(WEST,GATE_Y,COURT))


def niche(name, x, y, axis, width, height, depth, trim, shadow):
    # Geometry reads as a recessed chamber framed by protruding stones.
    if axis == 'north':
        sizes = [(width+.45, .23, .21), (.19, depth, height)]
        box(name+'_Dark_Back',(x,y+.43,COURT+.59+height/2),(width+.03,.13,height),shadow,.025)
        box(name+'_Sill',(x,y,COURT+.55),sizes[0],trim,.04)
        for side in (-1,1):
            box(name+'_Jamb',(x+side*width/2,y+.12,COURT+.61+height/2),sizes[1],trim,.04)
        box(name+'_Lintel',(x,y,COURT+.64+height),(width+.45,.5,.29),trim,.04)
    else:
        box(name+'_Dark_Back',(x+.48,y,COURT+.54+height/2),(.14,width,height),shadow,.025)
        box(name+'_Sill',(x,y,COURT+.49),(.59,width+.4,.23),trim,.035)
        for side in (-1,1):
            box(name+'_Jamb',(x+.07,y+side*width/2,COURT+.58+height/2),(depth,.24,height),trim,.038)


def enclosure(palette, trim, shadow, grass):
    for a,b,seed in [(-2.75,-1.51,101),(-.15,NORTH,102)]:
        wall('West_Enclosure',(WEST+.40,a),(WEST+.40,b),COURT,2.4,1.39,palette,seed,.18)
    box('West_Niche_Outer_Back',(-17.7,-.83,COURT+.95),(.36,1.44,1.9),palette[1],.065)
    wall('West_Enclosure_Fragment',(WEST+.44,-6.98),(WEST+.44,-5.62),COURT,1.22,1.38,palette,102,.36)
    wall('North_Enclosure_West',(WEST,NORTH-.48),(-.65,NORTH-.48),COURT,2.58,1.23,palette,103,.14)
    wall('North_Enclosure_East',(.65,NORTH-.48),(EAST,NORTH-.48),COURT,2.68,1.23,palette,104,.11)
    niche('North_Taqchah',0,12,'north',1.22,1.24,1.12,trim,shadow)
    anchor('North_Taqchah',(0,12.02,COURT+1.27))
    anchor('Landing_North_Taqchah',(0,9.45,COURT+.03))
    for a,b,seed in [(-13,-.61,111),(.91,2.0,112),(3.22,13,113)]:
        wall('East_Enclosure',(EAST-.48,a),(EAST-.48,b),COURT,2.6,1.30,palette,seed,.18)
    niche('East_Taqchah',16.44,2.61,'east',1.2,1.73,1.42,trim,shadow)
    box('East_Postern_Lintel',(17.02,.15,COURT+2.35),(1.92,2.05,.28),trim,.045)
    box('East_Postern_Blocked_Threshold',(17.49,.15,COURT+.39),(.53,1.50,.78),palette[2],.11)
    anchor('East_Postern',(16.87,.15,COURT+1.38))
    anchor('Landing_East_Postern',(13.75,.15,COURT+.03))
    anchor('East_Taqchah',(16.43,2.61,COURT+1.21))
    anchor('Landing_East_Taqchah',(13.89,3.02,COURT+.03))
    wall('South_East_Wall_Remnant',(13.8,SOUTH+.35),(EAST,SOUTH+.35),
         COURT,.94,1.15,palette,115,.21)
    wall('South_Conservation_Courses',(-9.4,SOUTH+.48),(13.8,SOUTH+.48),
         COURT,.59,1.00,[palette[1],palette[3]],117,.08)
    # Surveyed west niche just north of the portal, inset in the projecting face.
    box('West_Taqchah_Sill',(-16.26,-.83,COURT+.38),(.45,1.58,.23),trim,.047)
    box('West_Taqchah_Shadow',(-17.48,-.83,COURT+1.22),(.06,1.23,1.47),shadow,.03)
    for y in (-1.55,-.11):
        box('West_Taqchah_Jamb',(-16.12,y,COURT+1.04),(.55,.26,1.55),trim,.04)
    box('West_Taqchah_Lintel',(-16.15,-.83,COURT+1.89),(.56,1.67,.21),trim,.05)
    anchor('West_Taqchah',(-15.98,-.83,COURT+1.04))
    anchor('Landing_West_Taqchah',(-13.39,-.83,COURT+.03))
    box('East_Sill_Grass', (19.1,.12,COURT-.36),(3.2,3.1,.52),grass)


def sanctuary(palette, trim, shadow, grass):
    cx, cy = -1.0, .27
    floor = COURT + 1.0
    half = 2.99
    for level, width, height in [(.12,6.78,.24),(.43,6.42,.38),(.79,6.22,.34),(.975,6.31,.05)]:
        box('Sanctuary_Platform',(cx,cy,COURT+level),(width,width,height),palette[1],.055)
    box('Sanctuary_Earth_Floor',(cx,cy,floor+.014),(3.81,3.81,.028),grass,.006)
    x0, x1, y0, y1 = cx-half,cx+half,cy-half,cy+half
    stair('Sanctuary_West_Stair',x0-3.20,x0-.04,cy,1.85,COURT,.99,5,palette)
    wall('Sanctuary_West_Door_North',(x0+.49,cy+.66),(x0+.49,y1),
         floor,5.4,.98,palette,138,.12)
    wall('Sanctuary_West_Door_South',(x0+.49,y0),(x0+.49,cy-.66),
         floor,4.86,.98,palette,139,.19)
    for name,a,b,height,normal,relief_center in [
        ('North',(x0,y1-.48),(x1,y1-.48),5.08,(0,1,0),(cx,y1+.013,floor+.18)),
        ('East',(x1-.48,y0),(x1-.48,y1),4.90,(1,0,0),(x1+.013,cy,floor+.18)),
        ('South',(x0,y0+.48),(x1,y0+.48),4.80,(0,-1,0),(cx,y0-.013,floor+.18)),
    ]:
        wall('Sanctuary_'+name,a,b,floor,height,.96,palette,158+len(name),.13)
        relief('Sanctuary_'+name,relief_center,normal,1.07,trim,shadow)
    for side in (-1,1):
        y = cy + side*.85
        box('West_Door_Jamb',(x0-.16,y,floor+1.82),(.43,.4,3.64),trim,.065)
        for level,width in [(0.13,.57),(3.56,.52),(3.84,.63)]:
            box('West_Door_Pilaster_Course',(x0-.16,y,floor+level),(.6,width,.23),trim,.046)
    box('Surviving_Sanctuary_Door_Lintel',(x0-.15,cy,floor+4.03),(.85,2.64,.45),trim,.064)
    box('Surviving_North_Porch_Pillar',(x0-1.19,cy+.98,floor+2.01),(.67,.64,4.02),trim,.081)
    box('North_Porch_Pillar_Capital',(x0-1.19,cy+.98,floor+4.08),(.83,.83,.34),trim,.045)
    box('Lost_South_Porch_Pillar_Plinth',(x0-1.19,cy-.98,floor+.12),(.78,.78,.24),palette[2],.085)
    anchor('Sanctuary_Ruins',(x0-.75,cy,floor+.66))
    anchor('Landing_Sanctuary_Ruins',(x0-3.72,cy,COURT+.03))
    anchor('Sanctuary_Trefoil_Relief',(x1+.035,cy,floor+2.20))
    anchor('Landing_Sanctuary_Relief',(x1+3.07,cy,COURT+.03))


def valley_context(soil):
    rng = random.Random(927)
    water = material('Sharada_Madhumati', (.04,.10,.106), .67)
    mesh('Terrain_Madhumati_Water-renderonly',[(-87,-42,.024),(88,-36,.024),(88,-27,.024),
                                      (-87,-34,.024)],[(0,1,2,3)],water)
    # Low scattered fragments along the eroded southern edge.
    for index in range(28):
        x,y = rng.uniform(-12,16),rng.uniform(-12.7,-11.1)
        rock = box('South_Wall_Fallen_Fragment-renderonly',(x,y,COURT+.10),
                   (rng.uniform(.16,.65),rng.uniform(.18,.51),rng.uniform(.13,.32)),soil,.045)
        rock.rotation_euler.z = rng.uniform(-.6,.6)
    patch = material('Sharada_Dry_Grass_And_Earth',(.168,.184,.101))
    vertices, faces = [], []
    for index in range(83):
        x,y = rng.uniform(-14.8,16.7),rng.uniform(-10.7,12.1)
        if x < -11 and y < -8:
            continue
        radius = rng.uniform(.13,.74)
        start = len(vertices)
        for j in range(7):
            angle = j*math.tau/7
            span = radius*rng.uniform(.66,1.1)
            vertices.append((x+span*math.cos(angle),y+span*.65*math.sin(angle),COURT+.009))
        faces.append(tuple(range(start,start+7)))
    mesh('Ground_Dry_Grass_Patches-renderonly',vertices,faces,patch)
    # Context terrain behind the monument, outside the walkable site and map.
    # The ridges are a landscape study of the valley, not elevation survey data.
    ridge_profiles = [
        (-1, 1, 150, 77, .061, (.093,.145,.129)),
        (-1, 1, 230, 137, .037, (.11,.168,.16)),
        (1, 0, 230, 112, .045, (.158,.217,.213)),
        (1, 0, 320, 165, .029, (.173,.229,.23)),
    ]
    for side, phase, radius, height, freq, color in ridge_profiles:
        vertices = []
        count = 33
        for row in range(5):
            fraction = row/4
            for col in range(count):
                x = (col-16)*18.0
                profile = .61 + .18*math.sin(x*freq+phase) + .12*math.sin(x*freq*.41+side) + rng.uniform(-.045,.045)
                y = side*(radius-50+row*25+8*math.sin(x*.044+phase))
                vertices.append((x,y,-.15+height*profile*math.sin(math.pi*fraction)))
        faces = [(row*count+col,row*count+col+1,(row+1)*count+col+1,(row+1)*count+col)
                 for row in range(4) for col in range(count-1)]
        if side == -1:
            faces = [tuple(reversed(face)) for face in faces]
        ridge = mesh('Terrain_Distant_Valley_Ridge-renderonly',vertices,faces,
                     material(f'Sharada_Valley_Ridge_{radius}_{side}',color))
        for poly in ridge.data.polygons:
            poly.use_smooth = True


def build():
    clear_scene()
    grass = material('Sharada_Grassy_Court',(.135,.185,.079))
    soil = create_granite_stone('Sharada_Valley_Soil',(.225,.24,.153,1))
    palette = [create_granite_stone(f'Sharada_Weathered_Stone_{i}',(*tint,1)) for i,tint in enumerate([
        (.29,.268,.208),(.235,.237,.199),(.33,.306,.241),(.36,.297,.226),(.257,.251,.21)])]
    trim = create_granite_stone('Sharada_Chiselled_Stone',(.305,.278,.213,1))
    shadow = material('Sharada_Recess_Weathering',(.125,.113,.084))
    terrace(soil,grass,palette)
    approach(palette,trim,shadow)
    enclosure(palette,trim,shadow,grass)
    sanctuary(palette,trim,shadow,grass)
    valley_context(soil)
    # The field survey reports about five degrees between the enclosure and E–W.
    rotation = Matrix.Rotation(math.radians(5),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        obj.matrix_world = rotation @ obj.matrix_world


build()
if not globals().get('DEFER_GLB_EXPORT', False):
    finish('kashmir_sharada')
