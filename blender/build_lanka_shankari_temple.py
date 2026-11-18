"""Present-day Koneswaram compound and the Shankari tradition at Swami Rock."""

import math
import random

import bpy
from mathutils import Vector

from common_geometry import clear_scene, create_deepam, create_hanging_bell, create_pillar, create_tree
from common_materials import (
    create_brass_metal, create_flame_emission, create_granite_stone,
    create_green_foliage, create_sandstone, create_tree_bark,
)
from deity_detail import Sculpture, palette
from present_day_sites import anchor, box, cylinder, finish, linga, material


def swami_rock(stone, surface, ocean, leaves, bark):
    # Trace the coast visible from above. Height changes use the oblique
    # headland photographs as reference, with playable cliff-top elevations.
    outline = [
        (-82,-126), (45,-126), (28,-94), (24,-79), (3,-61), (29,-56), (35,-42), (32,-34), (22,-33), (22,-23), (33,-23),
        (47,-16), (47,4), (39,22), (31,36), (18,51), (6,63),
        (-12,68), (-27,62), (-39,48), (-49,31), (-55,12), (-67,-10),
    ]
    rng = random.Random(19)
    fractured_outline = []
    for edge, ((ax, ay), (bx, by)) in enumerate(zip(outline, outline[1:] + outline[:1])):
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        divisions = max(1, math.ceil(length / 5))
        for step in range(divisions):
            t = step / divisions
            # Keep the carved ledge cut clear of the playable stair flight.
            variation = rng.uniform(-1.0, 1.0) if step and edge not in (6, 7, 8, 9) else 0
            fractured_outline.append((ax + dx*t + dy/length*variation,
                                      ay + dy*t - dx/length*variation))
    outline = fractured_outline
    count = len(outline)
    vertices = [(x,y,0) for x,y in outline]
    for scale, height in [(1.045,-4), (1.08,-16), (1.13,-32)]:
        vertices.extend((x * scale + rng.uniform(-1.2,1.2),
                         y * scale + rng.uniform(-1.2,1.2),
                         height + rng.uniform(-1.6,1.6)) for x,y in outline)
    faces = [tuple(range(count))]
    for ring in range(3):
        for i in range(count):
            j = (i + 1) % count
            faces.append((ring*count+i, (ring+1)*count+i,
                          (ring+1)*count+j, ring*count+j))
    mesh = bpy.data.meshes.new("Swami_Rock_Contours")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    cliff = bpy.data.objects.new("Swami_Rock", mesh)
    bpy.context.collection.objects.link(cliff)
    for mat in [stone, surface, material("Swami_Rock_Ochre_Seams",(.28,.21,.15))]:
        mesh.materials.append(mat)
    mesh.polygons[0].material_index = 1
    for face in mesh.polygons[1:]:
        column = (face.index - 1) % count
        face.material_index = 2 if column % 9 in (1,2,3) else 0
    box("Indian_Ocean_Surface", (50,5,-31.8), (330,330,.08), ocean)

    for index, (x,y,z,w,d,h) in enumerate([(46,76,-29,12,14,5),(56,68,-30,8,10,4),
                                          (50,64,-31,6,9,4),(60,60,-31,5,7,4)]):
        rock = box("Offshore_Rock_" + str(index + 1), (x,y,z), (w,d,h), stone, .45)
        rock.rotation_euler.z = math.radians(index * 21)
    bpy.context.view_layer.update()
    for i in range(68):
        x, y = rng.uniform(-60,44), rng.uniform(-85,63)
        if ((-25 < x < 25 and -43 < y < 35)
                or (-40 < x < -8 and -81 < y < -28)
                or (22 < x and -48 < y < 20)):
            continue
        hit, position, normal, _ = cliff.ray_cast(Vector((x,y,8)), Vector((0,0,-1)))
        if hit and normal.z > .65:
            create_tree("Swami_Rock_Tropical_Canopy_" + str(i), position,
                        height=rng.uniform(3.3,6.5), mat_trunk=bark, mat_leaves=leaves)


def balustrade(name, points, floor, stone, green):
    for index,(a,b) in enumerate(zip(points, points[1:])):
        ax,ay=a
        bx,by=b
        dx,dy=bx-ax,by-ay
        length=math.hypot(dx,dy)
        turn=math.atan2(dy,dx)
        for height, size, mat in [(.11,.22,stone),(.96,.09,green)]:
            bar=box(name+"_Rail",((ax+bx)/2,(ay+by)/2,floor+height),
                    (length,.10,size),mat)
            bar.rotation_euler.z=turn
        posts=max(1,math.ceil(length / 1.15))
        for k in range(posts+1):
            x,y=ax+dx*k/posts,ay+dy*k/posts
            box(name+"_Upright",(x,y,floor+.55),(.065,.065,.91),green)


def gateway_tower(x, y, floor, stucco, indigo, green, red, gold):
    for side in [-1,1]:
        box("Entrance_Base_Jamb",(x+side*1.55,y,floor+1.47),(.69,.82,2.94),indigo,.05)
        for offset in [-.20,.20]:
            box("Entrance_Gold_Pilaster",(x+side*1.55+offset,y-.46,floor+1.42),
                (.13,.15,2.83),gold,.025)
        for height in [.2,1.1,2.39,2.76]:
            box("Entrance_Jamb_Banding",(x+side*1.55,y-.43,floor+height),
                (.84,.27,.095),gold)
    box("Entrance_Lintel",(x,y,floor+3.03),(4.18,1.02,.35),stucco,.04)
    for i, (width, depth, height) in enumerate([(4.8,2.26,3.33),(4.28,1.95,4.15),
                                               (3.6,1.72,4.97),(2.94,1.49,5.79)]):
        box("Gopuram_Sculpted_Tala",(x,y,floor+height+.29),(width,depth,.62),stucco,.075)
        for band, mat in [(0,indigo),(.11,green),(.21,red),(.27,gold)]:
            box("Gopuram_Painted_Cornice",(x,y,floor+height+band),
                (width+.12,depth+.20,.07),mat,.01)
        relief=Sculpture()
        paint=[relief.material("Gopuram_Stucco_Gold",(.62,.43,.19)),
               relief.material("Gopuram_Stucco_Blue",(.22,.34,.45)),
               relief.material("Gopuram_Stucco_Cream",(.68,.60,.47))]
        for bay in range(5):
            local_x=(bay-2)*width/5
            relief.ellipsoid((local_x,.01,.43),(.11,.06,.15),paint[(bay+i)%3])
            relief.ellipsoid((local_x,-.01,.60),(.059,.047,.067),paint[2])
            relief.ellipsoid((local_x,.02,.28),(.17,.083,.073),paint[(bay+i+1)%3])
        relief.finish("Gopuram_Tala_Relief_Study",(x,y-depth/2-.026,floor+height))
    barrel=box("Gopuram_Crown",(x,y,floor+6.58),(2.58,1.68,.35),stucco,.15)
    for dx in [-.87,0,.87]:
        cylinder("Gopuram_Finial",(barrel.location.x+dx,y,floor+6.92),.09,.43,gold)


def shiva_landmark(p):
    # The large outdoor statue is a separate monument from the sanctum linga.
    s=Sculpture()
    m=palette(s)
    gold=m["gold"]
    shade=s.material("Shiva_Landmark_Shadowed_Gold",(.47,.26,.042),.58,.44)
    for side in [-1,1]:
        s.ellipsoid((side*.47,-.06,.20),(.54,.34,.22),gold,36,22)
        s.ellipsoid((side*.27,-.32,.12),(.38,.17,.12),gold,28,16)
        s.tube([(side*.325,-.015,.96),(side*.47,-.032,.66),
                (side*.55,-.16,.41),(side*.63,-.21,.37)],.125,gold,18)
        s.ellipsoid((side*.64,-.24,.35),(.13,.086,.063),gold)
        for strand in range(4):
            s.tube([(side*(.116+.018*strand),.04,1.52),
                    (side*(.18+.018*strand),.09,1.36),
                    (side*(.17+.016*strand),.04,1.15)],.026,shade,9)
    s.ellipsoid((0,.022,.64),(.34,.24,.44),gold,42,28)
    s.ellipsoid((0,.031,.29),(.46,.29,.20),shade,36,24)
    s.ellipsoid((0,0,1.03),(.14,.12,.16),gold,30,20)
    s.ellipsoid((0,-.013,1.26),(.197,.161,.247),gold,48,32)
    s.ellipsoid((0,-.165,1.249),(.041,.060,.065),gold,26,18)
    s.ellipsoid((0,-.157,1.168),(.071,.033,.023),shade,28,14)
    s.ellipsoid((0,.028,1.54),(.158,.143,.115),shade,32,24)
    s.ellipsoid((0,.03,1.65),(.106,.083,.11),gold,28,16)
    for side in [-1,1]:
        s.ellipsoid((side*.18,-.026,1.232),(.045,.059,.092),gold)
        s.ellipsoid((side*.084,-.159,1.302),(.058,.025,.018),shade)
        s.tube([(side*.064,-.16,1.365),(side*.104,-.15,1.375),
                (side*.145,-.126,1.359)],.012,shade)
        for i in range(4):
            s.ellipsoid((side*(.61+i*.020),-.265,.347),(.020,.048,.020),gold,12,8)
    for row in range(3):
        s.tube([(-.25,-.096,.91),(0,-.25,.71-row*.09),(.25,-.096,.91)],.023,shade,12)
    s.tube([(-.072,-.10,1.65),(-.117,-.095,1.70),(-.101,-.09,1.75)],.017,gold)
    s.finish("Seated_Golden_Shiva_Statue",p,4.75)


def ravana_landmark(p):
    s=Sculpture()
    m=palette(s)
    skin=s.material("Ravana_Painted_Copper",(.43,.22,.13),.23)
    blue=s.material("Ravana_Blue_Drape",(.12,.27,.35))
    gold=m["gold"]
    for side in [-1,1]:
        s.ellipsoid((side*.118,-.055,.19),(.107,.12,.17),gold)
        s.tube([(side*.158,.01,1.07),(side*.205,-.10,.85),
                (side*.048,-.226,1.02),(side*.018,-.228,1.105)],.067,skin,12)
        s.ellipsoid((side*.024,-.226,1.097),(.033,.043,.095),skin)
        s.tube([(side*.18,.008,.95),(side*.23,-.041,.62),
                (side*.16,-.059,.42)],.045,blue,11)
        s.ellipsoid((side*.091,-.087,1.23),(.046,.045,.083),m["black"])
    s.ellipsoid((0,.009,.44),(.193,.14,.285),gold)
    s.ellipsoid((0,.01,.86),(.207,.15,.275),skin)
    s.ellipsoid((0,-.007,1.237),(.103,.096,.134),skin,28,18)
    s.tube([(-.07,-.093,1.204),(0,-.114,1.21),(.07,-.093,1.204)],.014,m["black"])
    s.ellipsoid((0,.004,1.385),(.117,.106,.086),m["red"])
    s.rosette((0,-.10,1.395),.045,gold,m["green"])
    return s.finish("Ravana_Prayer_Statue_Study",p,1.52)


def altar_bay(name, x, y, floor, stone, trim):
    box(name+"_Backing",(x,y+.83,floor+1.45),(3.14,.28,2.90),stone)
    for side in [-1,1]:
        box(name+"_Jamb",(x+side*1.47,y-.45,floor+1.37),(.26,1.94,2.74),trim,.04)
    box(name+"_Lintel",(x,y-.47,floor+2.79),(3.10,1.95,.23),trim,.04)
    box(name+"_Altar",(x,y+.07,floor+.22),(2.37,1.56,.44),stone,.035)
    return anchor(name+"_Anchor",(x,y+.05,floor+.44))


def build_koneswaram():
    clear_scene()
    rock=create_granite_stone("Swami_Rock_Banded_Cliff",(.185,.16,.145,1))
    surface=create_sandstone("Swami_Rock_Soil",(.30,.285,.195,1),.97)
    stone=create_sandstone("Koneswaram_Court_Paving",(.54,.44,.32,1))
    red=create_sandstone("Koneswaram_Red_Stair",(.43,.16,.11,1))
    stucco=material("Koneswaram_Cream_Stucco",(.73,.66,.53))
    silver=material("Koneswaram_Warm_Roof",(.57,.54,.465))
    indigo=material("Koneswaram_Facade_Blue",(.21,.34,.48))
    green=material("Koneswaram_Gallery_Green",(.20,.37,.29))
    gold=create_brass_metal("Koneswaram_Architectural_Brass")
    blue_rock=create_granite_stone("Shiva_Painted_Plinth",(.25,.34,.44,1))
    ocean=material("Trincomalee_Sea",(.045,.20,.27),.30,.11)
    leaves=create_green_foliage("Swami_Rock_Canopy",(.15,.28,.079,1))
    bark=create_tree_bark("Swami_Rock_Trunks")
    flame=create_flame_emission("Koneswaram_Lamp_Flame",strength=7)
    swami_rock(rock,surface,ocean,leaves,bark)

    # The southwest approach opens into the south forecourt. Red steps and
    # the central ramp lead to the entrance with the large Shiva to the east.
    road=box("Headland_Approach_Path",(-19,-54,.045),(7,49,.11),stone)
    road.rotation_euler.z=math.radians(-30)
    box("South_Entry_Court",(0,-20,.075),(46,24,.15),stone)
    upper=1.42
    for index in range(8):
        height=(index+1) * upper / 8
        for x,width in [(-13.7,17.8),(13.7,22.8)]:
            box("Koneswaram_Red_Stair",(x,-12.6+index*.54,height/2),
                (width,.55,height),red,.018)
    ramp=box("Koneswaram_Central_Ramp",(.1,-10.71,upper/2-.06),(4.35,4.70,.20),stone)
    ramp.rotation_euler.x=math.atan2(upper,4.45)
    box("Koneswaram_Upper_Plaza",(0,5,upper-.1),(47,27.4,.2),stone)

    # Broad rectangular, sheet-roofed main hall visible in aerial imagery.
    for x in [-20.0,19.0]:
        box("Koneswaram_Hall_Side",(x,7.2,upper+1.1),(.58,25,2.2),stucco,.045)
    box("Koneswaram_Hall_North_Wall",(-.5,19.6,upper+1.92),(39.5,.58,3.84),stucco,.041)
    for x in range(-19,20,4):
        for y in [-4.6,7.6,18.7]:
            if x == -7 and y == -4.6:
                continue  # Keep the gateway axis open.
            create_pillar("Koneswaram_Hall_Column",(x,y,upper),height=3.72,
                          radius=.21,mat=indigo,style="square")
    for y in [1.4,13.7]:
        cover=box("Koneswaram_Main_Sheet_Roof",(-.35,y,upper+3.95),(41.25,12.55,.24),silver)
        cover.rotation_euler.x=.049 if y<8 else -.049
    box("Koneswaram_Roof_Fascia",(-.35,-4.91,upper+3.64),(41.4,.23,.33),red)
    for index,offset in enumerate([-19,-12,1,7,12,18]):
        box("Koneswaram_Painted_Facade_Panel",(offset,-4.9,upper+.69),
            (2.2,.15,1.34),indigo if index%2 else stucco,.035)
    gateway_tower(-6.8,-5.15,upper,stucco,indigo,green,red,gold)

    # Golden seated Shiva landmark and his separate trident.
    for size,z in [((10.2,7.7,.4),upper+.2),((9.0,6.8,.85),upper+.775)]:
        box("Shiva_Public_Monument_Platform",(15.4,-9.2,z),size,blue_rock,.17)
    shiva_landmark((15.4,-9.2,upper+1.2))
    create_pillar("Shiva_Public_Trident_Shaft",(9.5,-8.8,upper+1.25),height=7.5,radius=.045,mat=gold)
    trident=Sculpture()
    prong=trident.material("Trident_Brass",(.59,.44,.19),.82)
    for side in [-1,1]:
        trident.tube([(0,0,0),(side*.29,0,.34),(side*.33,0,.76),(side*.27,0,.98)],.053,prong)
    trident.tube([(0,0,0),(0,0,1.15)],.045,prong)
    trident.finish("Shiva_Public_Trident_Head",(9.5,-8.8,upper+8.37))
    anchor("Shiva_Public_Monument_Anchor",(15.4,-12.88,upper+1.09))

    # Interior bays communicate present-day worship identities. Their
    # individual coordinates and installed sculptures need a measured survey.
    for name,x in [("Vinayagar",-14.5),("Koneswaram",-5.6),
                   ("Mathumai_Amman",2.7),("Murugan",10.7)]:
        altar_bay(name,x,15.9,upper,rock,gold)
    linga("Koneswaram_Sanctum_Linga",(-5.6,15.9,upper+.45),1.12,rock)
    create_hanging_bell("Ghanta",(-6.8,-4.1,upper+2.82),mat_brass=gold,scale=.78)
    for x in [-7.13,-4.1]:
        create_deepam("Koneswaram_Darshan_Deepam",(x,14.7,upper),mat_brass=gold,mat_flame=flame)
    anchor("Shankari_Tradition_Anchor",(-.25,11.4,upper+1.15))

    # The lower east-side platform is beside the cliff fissure. Ravana faces
    # the little linga on this ledge, as documented in the field study.
    low=-1.15
    box("Ravana_Lower_Lookout",(29,-28,low-.13),(8.5,8.1,.26),stone,.045)
    box("Ravana_Ledge_Retaining_Masonry",(29.0,-28.0,low-2.45),(7.9,7.6,4.6),rock,.09)
    for i in range(8):
        z=(i+1) * -low/8
        box("Ravana_Ledge_Stair",(24.2-i*.43,-28.8,low+z/2),( .44,2.7,z),stone,.014)
    balustrade("Ravana_Lookout",[(24.8,-24),(33.1,-24),(33.1,-32),(24.8,-32)],low,stone,green)
    ravana_statue=ravana_landmark((30.8,-27.1,low+.15))
    ravana_statue.rotation_euler.z=-math.pi/2
    linga("Ravana_Ledge_Linga",(27.45,-27.1,low+.13),.60,rock)
    box("Ravana_Statue_Low_Pedestal",(30.8,-27.1,low+.085),(1.33,1.1,.17),rock)
    anchor("Ravana_Prayer_Anchor",(29.4,-27.75,low+.85))
    anchor("Ravana_Vettu_Anchor",(24.3,-33.18,.95))
    balustrade("South_Cliff_Guard",[(18,-39),(23,-37),(25.5,-34)],.04,stone,green)
    balustrade("East_Cliff_Guard",[(32,-22),(40,-14),(44,0),(38,19)],.04,stone,green)

    anchor("Spawn_Point",(-6.8,-25.2,.18))
    finish("lanka_shankari")


build_koneswaram()
