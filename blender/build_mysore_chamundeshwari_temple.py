"""Reference-led model of the Chamundeshwari temple enclosure on Chamundi Hill."""
import math
import random

import bpy
from mathutils import Matrix

from common_geometry import clear_scene, create_deepam
from common_materials import create_granite_stone
from deity_detail import Sculpture, crown_band, garland, palette
from present_day_sites import anchor, finish, material


def mesh_object(name, position, vertices, faces, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    return obj


def box(name, position, dimensions, mat, bevel=0):
    # Direct mesh creation avoids repeatedly evaluating the sculpted scene.
    x,y,z = (d/2 for d in dimensions)
    vertices = [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
                (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces = [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    obj = mesh_object(name,position,vertices,faces,mat)
    if bevel:
        modifier = obj.modifiers.new('Stone corner bevel','BEVEL')
        modifier.width = bevel
        modifier.segments = 2
    return obj


def cylinder(name, position, radius, height, mat):
    count = 24
    vertices = [(radius*math.cos(math.tau*i/count),radius*math.sin(math.tau*i/count),side*height/2)
                for side in [-1,1] for i in range(count)]
    faces = [(i,(i+1)%count,count+(i+1)%count,count+i) for i in range(count)]
    faces.extend([tuple(reversed(range(count))),tuple(range(count,count*2))])
    obj = mesh_object(name,position,vertices,faces,mat)
    for face in obj.data.polygons[:-2]:
        face.use_smooth = True
    return obj


def sphere(name, position, radii, mat, segments=24):
    rings = 12
    rx,ry,rz = radii
    vertices = [(rx*math.sin(math.pi*r/rings)*math.cos(math.tau*s/segments),
                 ry*math.sin(math.pi*r/rings)*math.sin(math.tau*s/segments),rz*math.cos(math.pi*r/rings))
                for r in range(1,rings) for s in range(segments)]
    north = len(vertices)
    vertices.extend([(0,0,rz),(0,0,-rz)])
    faces = []
    for i in range(segments):
        j = (i+1)%segments
        faces.append((north,i,j))
        for r in range(rings-2):
            k = r*segments
            faces.append((k+i,k+segments+i,k+segments+j,k+j))
        bottom = (rings-2)*segments
        faces.append((bottom+j,bottom+i,north+1))
    obj = mesh_object(name,position,vertices,faces,mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def column(name, x, y, floor, height, width, stone):
    for suffix, z, across, tall in [('Foot',.05,1.53,.10),('Shaft',.477,1,.755),
                                    ('Capital',.925,1.8,.15)]:
        box(name+'_'+suffix,(x,y,floor+z*height),(across*width,across*width,tall*height),stone,.016)


def ledges(name, x, y, z, w, d, mat, scale=1):
    for dz, rim, height in [(0,.03,.16),(.17,.20,.19),(.35,.38,.14),(.50,.32,.09)]:
        box(name,(x,y,z+dz*scale),(w+rim*scale,d+rim*scale,height*scale),mat,.022*scale)


def pitched_roof(name, x, y, z, w, d, h, mat):
    vertices = [(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),
                (x,y-d*.34,z+h),(x,y+d*.34,z+h)]
    faces = [(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(3,2,1,0)]
    mesh_object(name,(0,0,0),vertices,faces,mat)


def portal(name, x, y, w, d, h, opening, height, wall, trim):
    for side in [-1,1]:
        span = (w-opening)/2
        box(name+'_Jamb',(x+side*(opening+span)/2,y,h/2),(span,d,h),wall,.06)
        for j in range(3):
            box(name+'_Pilaster',(x+side*(opening/2+.11+j*.16), y-d/2-.075,h/2),
                (.09,.23,h),trim,.014)
    box(name+'_Lintel',(x,y,(h+height)/2),(opening,d,h-height),trim,.025)


def shala(name, y, z, w, d, h, mat):
    vertices = []
    faces = []
    count = 36
    for side in [-1,1]:
        for i in range(count):
            a = math.tau*i/count
            vertices.append((side*w/2,y+d*math.cos(a)/2,z+h*math.sin(a)/2))
    for i in range(count):
        j = (i+1)%count
        faces.append((i,j,count+j,count+i))
    faces.extend([tuple(reversed(range(count))),tuple(range(count,count*2))])
    obj = mesh_object(name,(0,0,0),vertices,faces,mat)
    for polygon in obj.data.polygons[:-2]:
        polygon.use_smooth = True


def gateway(y, stone, stucco, light, gold, shadow):
    # The lower gateway is an open passage and the upper mass has seven
    # distinctly receding stages and a seven-pot barrel-ridge crown.
    portal('Raja_Gopura_East',0,y-5.20,14.2,.74,4.9,3.55,3.67,stone,light)
    portal('Raja_Gopura_West',0,y+5.20,14.2,.74,4.9,3.55,3.67,stone,light)
    for side in [-1,1]:
        box('Raja_Gopura_PassageWall',(side*4.5,y,2.23),(5.40,10.4,4.46),stone,.052)
        box('Raja_Gopura_PassageDoorpost',(side*1.79,y,1.79),(.29,10.5,3.58),stone,.021)
        ledges('Raja_Gopura_Granite_Plinth',side*4.51,y,.30,5.26,10.92,stone)
        for index in range(5):
            x=side*(2.27+index*.97)
            box('Raja_Gopura_Granite_Facade_Recess',(x,y-5.65,2.45),(.69,.13,2.48),stone,.025)
            box('Raja_Gopura_Facade_Panel_Cap',(x,y-5.72,3.72),(.80,.28,.16),stone,.023)
    box('Raja_Gopura_Vault_Ceiling',(0,y,4.75),(14.2,11.2,.45),stone)
    ledges('Raja_Gopura_BaseCornice',0,y,5,15.25,11.55,light)
    sculpture = Sculpture()
    shades = [sculpture.material('Chamundi_Gopura_Stucco',(.65,.45,.24),0,.82),
              sculpture.material('Chamundi_Gopura_Recess',(.34,.20,.10),0,.83)]
    for i in range(7):
        z = 5.56+i*2.12
        w = 14.5-i*1.16
        d = 11.2-i*.94
        box(f'Raja_Gopura_Tier_{i+1}',(0,y,z+.95),(w-.46,d-.42,1.94),stucco,.065)
        ledges('Raja_Gopura_StoreyCornice',0,y,z+1.76,w,d,light,.63)
        for side in [-1,1]:
            box('Gopura_Axial_Window_Recess',(0,y+side*(d/2-.12),z+.87),
                (1.04-i*.07,.20,1.05-i*.058),shadow,.08)
            box('Gopura_Axial_Window_Sill',(0,y+side*(d/2+.005),z+.36),
                (1.40-i*.07,.28,.17),light,.028)
        # Dense stucco aedicules and relief silhouettes follow the façade
        # rhythm. The individual figures are architectural studies.
        for side in [-1,1]:
            for axis, extent, depth, panels in [('front',w,d,max(5,11-i)),('side',d,w,max(3,8-i))]:
                step = extent/(panels+.2)
                for index in range(panels):
                    offset = (index-(panels-1)/2)*step
                    if axis=='front' and abs(offset) < .70:
                        continue
                    center = (offset,y+side*(depth/2-.02)) if axis=='front' else (side*(depth/2-.02),y+offset)
                    def pos(across, outward, height):
                        x0,y0 = center
                        return (x0+across,y0+side*outward,z+height) if axis=='front' else (x0+side*outward,y0+across,z+height)
                    sculpture.ellipsoid(pos(0,.025,.83),(.30,.18,.70) if axis=='front' else (.18,.30,.70),shades[1],12,8)
                    sculpture.ellipsoid(pos(0,.16,.63),(.137,.135,.40),shades[0],12,8)
                    sculpture.ellipsoid(pos(0,.16,1.13),(.131,.122,.18),shades[0],12,8)
                    for frame_side in [-1,1]:
                        sculpture.tube([pos(frame_side*.30,.20,.18),pos(frame_side*.30,.20,.99),
                                        pos(frame_side*.16,.22,1.33),pos(0,.22,1.43)],.041,shades[0],6)
                    sculpture.ellipsoid(pos(0,.25,1.52),(.26,.25,.12),shades[0],12,8)
    sculpture.finish('Raja_Gopura_Stucco_OrnamentDetail')
    box('Raja_Gopura_Crown_Support',(0,y,20.58),(6.96,3.22,.58),stucco,.03)
    z = 21.88
    shala('Raja_Gopura_Shikhara',y,z,7.25,3.95,2.72,light)
    for i in range(7):
        x = (i-3)*.92
        cylinder('Raja_Gopura_Kalasha_Stem',(x,y,z+1.59),.07,.43,gold)
        sphere('Raja_Gopura_Golden_Kalasha',(x,y,z+1.59),(.168,.168,.205),gold,16)
        sphere('Raja_Gopura_Kalasha_Tip',(x,y,z+1.89),(.085,.085,.11),gold,12)


def human(s, x, h, stone, trim, posture='standing'):
    """Layered sculpture volumes, facing the visitor along local negative Y."""
    if posture == 'seated':
        for side in [-1,1]:
            s.ellipsoid((x+side*h*.18,-h*.075,h*.20),(h*.23,h*.16,h*.117),stone,24,14)
        legs, waist = h*.23, h*.39
    else:
        for side in [-1,1]:
            s.tube([(x+side*h*.085,.018,h*.08),(x+side*h*.12,.014,h*.32),
                    (x+side*h*.09,.03,h*.51)],h*.086,stone,12)
            s.ellipsoid((x+side*h*.085,-h*.047,h*.07),(h*.082,h*.12,h*.056),stone)
        legs, waist = h*.35, h*.51
    s.ellipsoid((x,.023,legs),(h*.18,h*.11,h*.18),trim)
    s.ellipsoid((x,0,waist+h*.106),(h*.15,h*.115,h*.205),stone,26,18)
    s.ellipsoid((x,-h*.027,h*.84),(h*.113,h*.109,h*.141),stone,32,22)
    s.ellipsoid((x,-h*.129,h*.828),(h*.031,h*.039,h*.042),stone)
    s.ellipsoid((x,-.02,h*.952),(h*.092,h*.092,h*.074),trim)
    for side in [-1,1]:
        s.ellipsoid((x+side*h*.10,-h*.04,h*.82),(h*.034,h*.054,h*.065),stone,16,10)
        s.ellipsoid((x+side*h*.044,-h*.122,h*.852),(h*.028,h*.017,h*.013),trim,12,8)
    s.tube([(x-h*.112,-h*.099,h*.684),(x,-h*.129,h*.609),(x+h*.112,-h*.099,h*.684)],h*.015,trim)


def guard(name, position, h, relief=False, pose='standing', adorn=True):
    s = Sculpture()
    stone = s.material('Chamundi_CarvedStone',(.19,.16,.135),0,.63)
    trim = s.material('Chamundi_ReliefBand',(.35,.29,.20),.18,.51)
    human(s,0,h,stone,trim,pose)
    for side in [-1,1]:
        wrist = (side*h*(.05 if relief else .24),-h*.135,h*(.50 if relief else .44))
        s.tube([(side*h*.105,0,h*.68),(side*h*.21,-h*.035,h*.49),wrist],h*.045,stone,12)
        s.ellipsoid(wrist,(h*.046,h*.039,h*.070),stone)
    if adorn:
        s.tube([(-h*.23,.017,h*.11),(-h*.41,.03,h*.35),(-h*.36,.03,h*.69),(-h*.27,.03,h*.81)],h*.025,trim)
    model = s.finish(name,position)
    if relief:
        model.scale.y = .49
    return model


def silver_frame(s, p, width, height):
    silver = p['silver']
    for side in [-1,1]:
        x = side*width*.42
        s.tube([(x,.066,.04),(x,.066,height*.67)],.046,silver,12)
        for z in [.09,.16,height*.24,height*.60,height*.65]:
            s.ellipsoid((x,.062,z),(.103,.075,.042),silver,20,10)
        for index in range(24):
            a=math.pi/2*index/23
            s.rosette((side*width*.43*math.cos(a),.02,height*.64+height*.30*math.sin(a)),.049,silver,None,7)
    for x,z,rx,rz in [(0,height*.90,.145,.085),(-.057,height*.98,.048,.047),(.057,height*.98,.048,.047)]:
        s.ellipsoid((x,.014,z),(rx,.072,rz),silver)


def shrine_garlands(s, p, radius_x, center, radius_z):
    violet = s.material('Chamundi_DeepVioletFlowers',(.24,.08,.53),0,.65)
    for i,color in enumerate([p['white'],violet,p['yellow']]):
        for j in range(51):
            a=math.pi+math.pi*j/50
            x=(radius_x+i*.054)*math.cos(a)
            z=center+(.052*i)+(radius_z+.15*i)*math.sin(a)
            s.rosette((x,-.265-i*.019,z),.029,color,None,6)


def entry_ganesha(position, name, size=1, installed=False):
    s = Sculpture(); p = palette(s)
    metal = p['silver'] if installed else p['black']
    s.ellipsoid((0,0,.43),(.296,.194,.305),metal)
    for side in [-1,1]:
        s.ellipsoid((side*.20,.01,.26),(.222,.178,.126),metal)
        s.ellipsoid((side*.191,-.055,.778),(.144,.063,.196),metal)
        s.tube([(side*.060,-.155,.696),(side*.15,-.176,.632)],.026,p['white'])
        s.tube([(side*.21,.003,.59),(side*.34,-.045,.50),(side*.30,-.126,.56)],.058,metal)
        s.ellipsoid((side*.30,-.121,.561),(.072,.051,.090),metal)
        s.ellipsoid((side*.30,-.26,.41),(.086,.08,.059),p['gold'])
    s.ellipsoid((0,-.044,.776),(.175,.127,.174),metal)
    s.tube([(0,-.145,.741),(-.041,-.23,.63),(-.018,-.242,.53),(.129,-.252,.49),
            (.25,-.264,.55),(.287,-.251,.63),(.34,-.238,.60)],.054,metal,18)
    s.ellipsoid((0,0,.935),(.133,.113,.132),metal if installed else p['gold'])
    if installed:
        silver_frame(s,p,1.18,1.31)
        shrine_garlands(s,p,.35,.91,.59)
        s.ellipsoid((0,-.195,.780),(.032,.013,.029),p['red'])
    else:
        garland(s,p,.248,.63,.32,-.21,28)
    return s.finish(name,position,size)


def nandi(position):
    s = Sculpture(); p = palette(s)
    black = p['black']
    s.ellipsoid((0,-.14,.32),(.30,.49,.28),black,32,20)
    s.ellipsoid((0,.03,.55),(.21,.26,.22),black)
    s.ellipsoid((0,.245,.44),(.165,.243,.228),black)
    s.ellipsoid((0,.465,.40),(.149,.156,.112),black)
    for side in [-1,1]:
        s.ellipsoid((side*.17,.11,.136),(.136,.263,.101),black)
        s.ellipsoid((side*.176,.31,.582),(.133,.085,.066),black)
        s.tube([(side*.103,.349,.575),(side*.142,.319,.675),(side*.122,.305,.756)],.025,p['gold'])
    s.tube([(-.166,.288,.58),(-.111,.41,.336),(0,.432,.292),(.11,.41,.336),(.16,.288,.58)],.025,p['gold'])
    return s.finish('Chamundi_Small_Nandi_Study',position)


def chamundi(position):
    s = Sculpture(); p = palette(s)
    gold = p['gold']
    pink = s.material('Chamundi_Flower_Pink',(.82,.09,.30),0,.68)
    human(s,0,1.92,gold,p['red'],'seated')
    s.ellipsoid((0,.02,.63),(.77,.24,.49),p['red'],48,32)
    for i in range(24):
        crease = (i-11.5)*.061
        s.tube([(crease*.29,-.217,.89),(crease*.71,-.238,.62),
                (crease,-.236,.33)],.012,gold,6)
    for side in [-1,1]:
        for i in range(4):
            height = 1.44-i*.226
            start = (side*.23,.025,1.31-i*.11)
            elbow = (side*(.42+i*.125),.032,height-.13)
            hand = (side*(.57+i*.12),-.115-i*.015,height+.13)
            s.tube([start,elbow,hand],.055,gold,14)
            s.ellipsoid(hand,(.083,.051,.105),gold)
            s.ellipsoid((hand[0],hand[1],hand[2]-.065),(.072,.058,.028),gold)
    for i in range(71):
        a = math.pi*i/70
        px,pz = 1.06*math.cos(a),.60+1.51*math.sin(a)
        s.ellipsoid((px,.144,pz),(.060,.055,.073),gold,12,8)
        if i%4==0:
            s.rosette((px,.11,pz),.078,gold,p['red'])
    crown_band(s,p,.44,1.78,-.15,4)
    for row,color in enumerate([p['white'],pink,p['white'],p['green'],p['orange'],p['white']]):
        for index in range(74):
            angle = math.pi + math.pi*index/73
            x = (.58+row*.086)*math.cos(angle)
            z = 1.37+(.57+row*.135)*math.sin(angle)
            s.rosette((x,-.29-row*.019,z),.041,color,None,6)
    for index in range(56):
        a = math.pi*index/55
        s.rosette((1.015*math.cos(a),-.113,.66+1.40*math.sin(a)),.052,
                  p['white'] if index%7<4 else p['orange'],None,6)
    s.finish('Deity_Chamundeshwari',position)['has_authored_ornaments'] = True


def build():
    clear_scene()
    rng = random.Random(272)
    floor = create_granite_stone('Chamundi_Gray_Courtyard',(.42,.39,.35,1))
    granite = create_granite_stone('Chamundi_Granite_Platform',(.25,.22,.18,1))
    earth = material('Chamundi_ExposedHill',(.30,.259,.16))
    asphalt = material('Chamundi_Road',(.155,.145,.132))
    sand = material('Chamundi_WarmPlaster',(.57,.443,.275))
    ochre = material('Chamundi_DarkOchre',(.36,.242,.138))
    cream = material('Chamundi_PaleMoulding',(.75,.64,.44))
    stone_gold = material('Chamundi_Gopura_Stone',(.68,.48,.255))
    vermilion = material('Chamundi_TerraceTile',(.36,.115,.062))
    corrugated = material('Chamundi_QueueCover',(.30,.40,.49),.52,.2)
    gold = material('Chamundi_BurnishedBrass',(.69,.428,.105),.68,.32)
    silver_doors = material('Chamundi_SilverDoors',(.53,.55,.57),.68,.32)
    white = material('Chamundi_Steps',(.69,.64,.52))
    black = material('Chamundi_DarkInset',(.08,.07,.061))
    bark = material('Chamundi_TreeBark',(.14,.102,.068))
    leaf = [material(f'Chamundi_Canopy_{i}',(.072+i*.016,.126+i*.033,.054+i*.010)) for i in range(5)]

    box('Ground_Chamundi_Hilltop',(0,0,-.55),(186,212,.90),earth)
    box('Ground_East_Arrival_Plaza',(0,-48,-.12),(49,32,.24),floor)
    box('Chamundi_Enclosure_Court',(0,0,-.12),(36.8,62,.24),floor)
    box('Ground_Summit_Road',(0,38,-.16),(63,9.8,.12),asphalt)
    for side in [-1,1]:
        box('Ground_Perimeter_Lane',(side*26,0,-.16),(6.8,80,.12),asphalt)

    # Aerial footprint: long enclosure, eastern gate, surrounding low ranges,
    # the central hall's tile roof, and a much smaller tower at the west end.
    gateway(-25.0,granite,stone_gold,cream,gold,black)
    anchor('Spawn_Point',(0,-40.35,.055))
    for side in [-1,1]:
        box('East_Frontage',(side*12.78,-29.47,1.6),(10.91,.73,3.2),sand,.04)
        box('Prakara_Long_Wall',(side*18,0,1.60),(.63,61,3.2),sand,.035)
        for y in range(-27,32,4):
            box('Prakara_Buttress',(side*17.61,y,1.60),(.52,.56,3.20),ochre,.026)
        box('Prakara_Long_Coping',(side*18,0,3.30),(.91,61.2,.24),cream,.025)
        box('Courtyard_Perimeter_Gallery_Roof',(side*15.30,3.35,3.19),(5.93,52.1,.31),sand,.037)
        pitched_roof('Courtyard_Perimeter_Tile_Roof',side*15.32,3.35,3.31,5.88,51.8,.56,vermilion)
        for y in range(-22,31,3):
            column('Gallery_Granite_Pillar',side*12.73,y,0,3.22,.36,granite)
        for y in range(-28,31,2):
            sphere('Prakara_Miniature_Finial',(side*18,y,3.52),(.18,.17,.25),cream,12)
    box('West_Prakarawall',(0,30.41,1.61),(36.66,.61,3.22),sand,.035)
    box('West_Prakarawall_Coping',(0,30.41,3.29),(36.73,.83,.24),cream,.026)
    box('West_Perimeter_Gallery_Roof',(0,27.52,3.18),(35,5.8,.32),sand,.035)
    for x in range(-14,16,3):
        column('West_Gallery_Pillar',x,25.2,0,3.22,.38,granite)

    # Support a continuous route through the Navaranga and Antarala.
    box('Navaranga_Floor',(0,.10,.05),(19.45,20.45,.10),granite,.02)
    box('Sanctum_Floor',(0,16.35,.075),(12.5,15.9,.15),granite,.024)
    for side in [-1,1]:
        box('Navaranga_External_Wall',(side*9.23,0,2.26),(.49,19.0,4.52),sand,.034)
        box('West_Sanctum_Wall',(side*6.03,16.42,2.66),(.47,13.0,5.32),sand,.025)
        for y in [-7.0,-3.0,1.6,6.1]:
            column('Navaranga_Bay_Pillar',side*3.55,y,.10,4.37,.58,granite)
        for y in [-8.9,-5.2,-1.48,2.25,5.97,9.1]:
            box('Navaranga_Exterior_Pilaster',(side*9.53,y,2.14),(.48,.35,4.28),cream,.028)
    portal('Navaranga_Front',0,-9.70,19.1,.64,4.51,3.45,3.22,sand,cream)
    portal('Antarala',0,8.60,12.5,.54,4.7,3.14,3.32,sand,granite)
    portal('Garbhagriha',0,12.52,12.5,.77,5.31,2.54,3.22,sand,silver_doors)
    box('Garbhagriha_BackWall',(0,22.89,2.66),(12.5,.56,5.32),sand,.032)
    ledges('Navaranga_Cornice',0,0,4.57,19.62,19.9,cream)
    box('Navaranga_RoofSlab',(0,0,5.18),(19.97,20.28,.33),vermilion,.032)
    pitched_roof('Navaranga_Tile_Roof',0,-.30,5.25,20.15,20.65,1.02,vermilion)
    box('Garbhagriha_RoofSlab',(0,16.35,5.31),(13.0,14.05,.33),sand,.03)
    for i in range(4):
        w = 7.75-i*1.45
        z = 5.53+i*.83
        box('Chamundi_Vimana_Storey',(0,18.48,z+.35),(w,w*.95,.70),stone_gold,.035)
        ledges('Chamundi_Vimana_Cornice',0,18.48,z+.58,w,w*.95,gold,.56)
    sphere('Chamundi_Vimana_Shikhara',(0,18.48,9.29),(1.60,1.55,1.07),stone_gold,36)
    sphere('Chamundi_Vimana_Kalasha',(0,18.48,10.52),(.28,.28,.43),gold,24)

    # Gallery vestibule and the two separately documented entrance images.
    for side in [-1,1]:
        box('Entrance_Vestibule_Wall',(side*6.85,-19.42,1.85),(.48,9.3,3.70),sand,.035)
    box('Entrance_Vestibule_Roof',(0,-21.0,3.87),(14.82,7.02,.26),sand,.025)
    for x in [-5.8,5.8]:
        column('Entrance_Hall_Pillar',x,-17.59,0,3.74,.46,granite)
    entry_ganesha((0,-30.72,3.75),'Raja_Gopura_Lintel_Ganesha',.58)
    anchor('Lintel_Ganesha_Reference',(0,-30.77,4.03))
    anchor('Lintel_Ganesha_Landing',(0,-34.45,.05))

    box('Vinayaka_Wall_Bay',(3.95,-19.08,1.68),(2.72,.40,3.36),ochre,.033)
    box('Vinayaka_Sacred_Platform',(3.95,-18.23,.32),(1.74,1.0,.64),granite,.041)
    ganesha = entry_ganesha((3.95,-18.36,.64),'Chamundi_Entrance_Vinayaka',installed=True)
    ganesha.rotation_euler.z = math.pi
    anchor('Entrance_Vinayaka_Anchor',(3.95,-18.10,1.18))
    anchor('Entrance_Vinayaka_Landing',(3.95,-15.65,.05))

    box('Anjaneya_Attached_Wall_Bay',(6.03,-15.67,1.65),(1.00,1.77,3.3),ochre,.035)
    box('Anjaneya_Basalt_Backslab',(5.48,-15.67,1.52),(.15,1.46,2.13),black,.032)
    # Profile and silver covering from the Department's Anjaneya photograph.
    fig = Sculpture(); p = palette(fig)
    silver = p['silver']
    silver_frame(fig,p,1.18,1.71)
    fig.ellipsoid((0,-.065,.83),(.22,.145,.33),silver,28,18)
    fig.ellipsoid((.044,-.117,1.16),(.14,.120,.145),silver,30,20)
    fig.ellipsoid((.144,-.160,1.135),(.094,.077,.061),silver)
    fig.ellipsoid((.024,-.085,1.31),(.127,.097,.10),silver)
    fig.ellipsoid((.090,-.213,1.193),(.014,.012,.014),p['black'])
    fig.tube([(-.04,-.064,.62),(-.23,-.103,.42),(-.32,-.152,.14)],.061,silver,14)
    fig.tube([(.11,-.069,.62),(.224,-.127,.41),(.224,-.156,.131)],.068,silver,14)
    for x in [-.32,.224]:
        fig.ellipsoid((x+.04,-.173,.115),(.087,.077,.043),silver)
    fig.tube([(-.154,-.04,.76),(-.33,-.069,.58),(-.277,-.132,.43)],.051,silver,14)
    fig.tube([(.115,-.053,.93),(.268,-.087,1.03),(.299,-.087,1.22)],.051,silver,14)
    fig.tube([(-.12,.022,.63),(-.34,.025,.78),(-.35,.022,1.17),(-.23,.024,1.43),
              (.10,.023,1.48),(.24,.025,1.60)],.026,silver,12)
    shrine_garlands(fig,p,.30,1.34,.63)
    hanuman = fig.finish('Chamundi_Anjaneya_Wall_Relief',(5.34,-15.67,.61))
    hanuman.scale.y = .55
    hanuman.rotation_euler.z = -math.pi/2
    anchor('Anjaneya_Anchor',(5.26,-15.67,1.51))
    anchor('Anjaneya_Landing',(2.84,-15.67,.06))

    # Flagstaff sequence near the inner hall; keep a walkable line to darshan.
    cylinder('Dhvajastambha_Base',(0,-12.97,.23),.64,.46,granite)
    cylinder('Dhvajastambha_Brass',(0,-12.97,3.11),.125,5.76,gold)
    for i in range(16):
        cylinder('Dhvajastambha_Collars',(0,-12.97,.66+i*.32),.155,.048,gold)
    box('Devi_Paduka_Platform',(-1.46,-12.52,.20),(1.01,.79,.40),granite,.024)
    for sx in [-1,1]:
        sphere('Devi_Footprint_Outline',(-1.46+sx*.15,-12.51,.408),(.093,.236,.021),gold,24)
        for i in range(5):
            sphere('Footprint_Toe',(-1.46+sx*.15+sx*(i-1.7)*.030,-12.31+.015*(4-i),.419),
                   (.021,.028,.013),gold,12)
    anchor('Devi_Footprints_Anchor',(-1.46,-12.53,.44))
    anchor('Devi_Footprints_Landing',(-1.96,-14.26,.06))
    box('Chamundi_Inner_Nandi_Base',(1.52,-11.14,.19),(1.1,1.43,.38),granite,.031)
    nandi((1.52,-11.23,.38))
    anchor('Small_Nandi_Anchor',(1.52,-11.10,.88))
    anchor('Small_Nandi_Landing',(1.54,-13.52,.06))

    for x, name in [(-2.31,'Nandini'),(2.31,'Kamalini')]:
        box(name+'_InnerDoor_Niche',(x,8.22,1.77),(1.26,.37,2.84),black,.035)
        guard(name+'_InnerDoor_Guardian',(x,8.00,.43),1.88,True)
        anchor(name+'_Anchor',(x,7.93,1.39))
        anchor(name+'_Landing',(x,5.65,.13))
    for x, name in [(-2.13,'Left'),(2.13,'Right')]:
        guard('Gopura_'+name+'_Dvarapala',(x,-30.70,.40),2.33,True)
        anchor('Gopura_'+name+'_Dvarapala_Reference',(x,-30.84,1.62))
        anchor('Gopura_'+name+'_Dvarapala_Landing',(x,-33.42,.06))

    # Silver-faced relief leaves flank the open darshan gateway.
    for side in [-1,1]:
        x = side*1.61
        box('Silver_Door_Leaf',(x,12.07,1.59),(.62,.15,2.98),silver_doors,.018)
        for i in range(4):
            box('Silver_Door_Repousse_Frame',(x,11.972,.54+i*.69),(.52,.035,.60),cream,.017)
            guard('Silver_Door_Devi_Relief',(x,11.945,.34+i*.69),.46,True,adorn=False)
    anchor('Silver_Door_Reference',(0,11.98,2.87))
    anchor('Silver_Door_Landing',(0,9.65,.15))
    anchor('Gopura_Inscription_Reference',(-3.29,-30.75,1.25))
    anchor('Gopura_Inscription_Landing',(-3.38,-33.14,.055))
    box('Chamundi_Murti_Pitha',(0,18,.51),(2.73,1.97,.73),granite,.069)
    chamundi((0,17.8,.87))
    anchor('Sanctum_Lamp_Position',(.15,15.45,2.72))
    for side in [-1,1]:
        create_deepam('Chamundi_Deepam',(side*1.23,16.94,.45),gold,material('Chamundi_Wick',(.99,.54,.084),emission=3.0))
    anchor('Chamundeshwari_Darshan_Landing',(0,14.2,.17))

    # Queue-side exterior volumes and forested slope show the real summit
    # setting without moving the independent hill shrines inside the walls.
    box('Context_Queue_Range',(21.16,2.30,1.65),(4.34,55.0,3.3),sand,.042)
    box('Context_Queue_Cover_Roof',(21.16,2.30,3.58),(4.81,55.53,.23),corrugated,.036)
    for i in range(9):
        x,y = rng.uniform(-39,-27),-23+i*7.3
        h = rng.uniform(2.6,5.6)
        box('Context_Service_Range',(x,y,h/2),(rng.uniform(5.2,8.1),6.8,h),sand,.046)
        pitched_roof('Context_Service_Tile_Roof',x,y,h,8.45,7.3,1.12,vermilion)
    for i in range(57):
        x,y = rng.uniform(-71,72),rng.uniform(44,86)
        h = rng.uniform(2.8,8.8)
        cylinder('Terrain_Context_Tree_Trunk',(x,y,h*.31),h*.022,h*.64,bark)
        sphere('Terrain_Context_Tree_Canopy',(x,y,h*.72),(h*.31,h*.27,h*.38),leaf[i%len(leaf)],12)

    # East is 8 degrees north of east in the aerial image.
    rotation = Matrix.Rotation(math.radians(98),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world = rotation @ obj.matrix_world


if __name__ == '__main__':
    build()
    finish('mysore_chamundeshwari')
