"""Bhasmakut hilltop and low Mangala Gauri sanctum, from the published site views."""
import math
import random

import bpy
from mathutils import Matrix

from common_geometry import clear_scene, create_deepam
from common_materials import create_granite_stone, create_white_marble
from deity_detail import Sculpture, garland, palette
from present_day_sites import anchor, box, cylinder, finish, linga, material, sphere


def roof(name, x, y, z, width, depth, rise, surface):
    w,d=width/2,depth/2
    vertices=[(x-w,y-d,z),(x+w,y-d,z),(x+w,y+d,z),(x-w,y+d,z),
              (x,y-d*.25,z+rise),(x,y+d*.25,z+rise)]
    faces=[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(3,2,1,0)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(surface)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)


def hill(top, dirt, rock, court, stairs):
    # Platform and the eastern ascent appear together on the hill shoulder.
    box('Ground_Bhasmakut_Base',(0,6,-.7),(144,133,.8),dirt)
    box('Bhasmakut_Summit_Retaining_Block',(0,3.4,top*.49),(19.4,22.5,top*.98),rock)
    box('Summit_Court',(0,3.4,top-.09),(19.43,22.5,.18),court)
    outline=[(-9.65,-7.85),(-9.65,14.65),(9.65,14.65),(9.65,-7.85)]
    skirt=[(-28,-21),(-31,38),(25,36),(26,-21)]
    for index in range(3):
        j=index+1
        name='Terrain_Bhasmakut_Slope_'+str(index)
        points=[]
        faces=[]
        divisions=10
        for row in range(6):
            t=row/5
            for col in range(divisions+1):
                u=col/divisions
                x=(outline[index][0]*(1-u)+outline[j][0]*u)*(1-t)+(skirt[index][0]*(1-u)+skirt[j][0]*u)*t
                y=(outline[index][1]*(1-u)+outline[j][1]*u)*(1-t)+(skirt[index][1]*(1-u)+skirt[j][1]*u)*t
                z=(top-.16)*(1-t)**1.24-.28*t+.80*math.sin(t*math.pi)*math.sin(x*.59+y*.26)
                points.append((x,y,z))
                if row and col:
                    last=row*(divisions+1)+col
                    faces.append((last-divisions-2,last-divisions-1,last,last-1))
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata(points,[],faces)
        mesh.materials.append(rock)
        mesh.update()
        obj=bpy.data.objects.new(name,mesh)
        bpy.context.collection.objects.link(obj)
    for i in range(54):
        z=(i+1)*top/54
        y=-27.83+i*.37
        tread=.77 if i==53 else .373
        box('East_Stair_Tread_RenderOnly',(0,y+(tread-.373)/2,z/2),(3.44,tread,z),stairs,.008)
        if i%6==0:
            for side in [-1,1]:
                box('Stair_Handrail_Pier',(side*1.79,y,z+.55),(.16,.22,1.1),rock,.016)
    # An imported collision-only ramp keeps the stairs walkable without
    # rendering an extra surface through the individual masonry risers.
    name='East_Stair_Walk_Surface-colonly'
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(-1.71,-28.02,0),(1.71,-28.02,0),(1.71,-7.85,top),(-1.71,-7.85,top)],[],
                     [(0,1,2,3)])
    mesh.update()
    bpy.context.collection.objects.link(bpy.data.objects.new(name,mesh))
    box('East_Approach_Road',(0,-34,-.12),(11.5,13.7,.24),stairs)
    anchor('Spawn_Point',(0,-32.1,.075))
    anchor('Arrival_Facing',(0,-18,.09))
    anchor('Eastern_Stairs_Reference',(0,-10.2,top-1.0))
    anchor('Eastern_Stairs_Landing',(0,-29.6,.075))


def canopy_range(name,x,y,z,width,depth,orange,tile,steel):
    box(name+'_Outer_Wall',(x,y+depth/2-.10,z+1.58),(width,.20,3.16),orange,.027)
    for col in range(5):
        px=x+(col-2)*(width-1.25)/4
        box(name+'_Canopy_Pillar',(px,y-depth/2+.26,z+1.81),(.17,.18,3.62),steel,.012)
    for off in [-1,1]:
        box(name+'_Roof_Edge',(x,y+off*(depth/2-.12),z+3.68),(width+.32,.17,.22),steel,.022)
    box(name+'_Corrugated_Roof',(x,y,z+3.73),(width+.31,depth+.25,.13),tile,.012)
    for row in range(10):
        box(name+'_Roof_Seam',(x,y+(row-4.5)*depth/10,z+3.806),(width+.24,.044,.034),steel)


def gauri(position):
    s=Sculpture()
    p=palette(s)
    # The official description identifies worship of a sacred symbol.
    # The sandstone and sindoor study leaves the covered contour approximate.
    red=s.material('Mangala_Sindoor',(.66,.052,.014),.04,.56)
    rock=s.material('Mangala_Shila',(.092,.073,.054),0,.71)
    s.ellipsoid((0,0,.106),(.66,.44,.16),rock,32,18)
    for x in [-.17,.18]:
        s.ellipsoid((x,-.05,.25),(.25,.23,.24),red,32,22)
        for i in range(12):
            a=math.pi+math.pi*i/11
            s.rosette((x+.23*math.cos(a),-.14,.32+.18*math.sin(a)),.027,p['white'],p['yellow'],6)
    for row in range(3):
        garland(s,p,.47+row*.046,.44,.31+row*.036,-.36-row*.03,39)
    s.finish('Deity_Mangalagauri',position)['has_authored_ornaments']=True


def deity_study(name,x,y,z,form):
    s=Sculpture()
    p=palette(s)
    basalt=p['black']
    if form=='hanuman':
        basalt=p['orange']
    s.ellipsoid((0,.01,.63),(.25,.114,.29),basalt)
    s.ellipsoid((0,-.017,1.01),(.137,.116,.17),basalt)
    s.ellipsoid((0,.01,1.191),(.115,.10,.132),p['gold'])
    for side in [-1,1]:
        s.tube([(side*.076,.013,.14),(side*.097,.019,.41),(side*.10,.022,.60)],.064,basalt,9)
        s.tube([(side*.154,0,.797),(side*.25,-.02,.68),(side*.21,-.145,.57)],.055,basalt,10)
        s.ellipsoid((side*.216,-.113,.61),(.054,.043,.070),basalt)
        arms=3 if form in ['durga','mahishasuramardini'] else 1 if form in ['kali','vishnu'] else 0
        for i in range(arms):
            tx=side*(.27+i*.11)
            tz=1.04-i*.18
            s.tube([(side*.143,.015,.797-i*.076),(tx,-.009,tz-.15),(tx,-.125,tz)],.045,basalt,9)
            s.ellipsoid((tx,-.145,tz+.028),(.048,.037,.065),basalt,14,8)
    if form=='hanuman':
        s.ellipsoid((.032,-.122,1.0),(.112,.066,.064),basalt)
        s.tube([(-.14,.05,.30),(-.32,.049,.49),(-.36,.064,.87),(-.25,.067,1.12)],.025,basalt,9)
        s.tube([(.222,-.17,.24),(.222,-.17,.91)],.019,p['gold'])
        s.ellipsoid((.222,-.17,.28),(.098,.083,.13),p['gold'],22,14)
    elif form=='kali':
        s.ellipsoid((0,-.138,.985),(.044,.026,.063),p['red'])
        s.tube([(-.27,-.13,1.031),(-.29,-.13,1.28),(-.205,-.125,1.39)],.023,p['silver'])
        for i in range(12):
            a=math.pi+math.pi*i/11
            s.ellipsoid((.17*math.cos(a),-.130,.84+.30*math.sin(a)),(.035,.019,.043),p['white'],12,8)
    elif form=='vishnu':
        s.tube([(-.27+.074*math.cos(math.tau*i/32),-.155,1.14+.074*math.sin(math.tau*i/32))
                for i in range(33)],.014,p['gold'])
        s.ellipsoid((.27,-.149,1.13),(.060,.043,.091),p['white'],19,12)
    elif form in ['durga','mahishasuramardini']:
        s.tube([(-.381,-.13,.34),(-.381,-.13,1.38)],.012,p['gold'])
        for side in [-1,0,1]:
            s.tube([(-.381,-.13,1.25),(-.381+side*.06,-.13,1.37)],.012,p['gold'])
        s.rosette((.33,-.15,1.15),.075,p['gold'],p['red'])
        if form=='mahishasuramardini':
            s.ellipsoid((.14,-.14,.12),(.20,.113,.108),basalt,24,14)
            for side in [-1,1]:
                s.tube([(.14+side*.13,-.16,.16),(.14+side*.22,-.17,.22),(.14+side*.26,-.15,.265)],.019,p['gold'])
    garland(s,p,.208,.87,.36,-.15,31)
    s.finish(name,(x,y,z))


def build():
    clear_scene()
    rng=random.Random(147)
    top=8.1
    dirt=material('Gaya_Earth',(.39,.31,.21))
    rock=create_granite_stone('Bhasmakut_Hill_Rock',(.29,.27,.22,1))
    stairs=create_granite_stone('Gaya_Stair_Stone',(.51,.45,.35,1))
    court=create_granite_stone('Gaya_Summit_Paving',(.55,.52,.45,1))
    white=create_white_marble('Gaya_White_Marble_Facing')
    red=material('Gaya_Laterite_Mosaic',(.39,.128,.073))
    orange=material('Gaya_Court_Ochre',(.68,.265,.081))
    fabric=material('Gaya_Chatra_Roof_Cloth',(.61,.142,.024))
    shade=material('Gaya_Corrugated_Sheet',(.328,.327,.290),.72,.06)
    steel=material('Gaya_Red_Canopy_Truss',(.31,.084,.044))
    gold=material('Gaya_Brass',(.78,.48,.13),.71,.30)
    flame=material('Gaya_LampWick',(.96,.46,.065),emission=2.3)
    olive=material('Gaya_Hillside_Canopy',(.125,.229,.075))
    hill(top,dirt,rock,court,stairs)

    # The square marble forebody and the rear decorated roof match the low
    # form visible in the tourism department's photograph.
    w,d=4.65,6.80
    x,y=0,2.15
    floor=top+.13
    box('Mangala_Gauri_Sanctum_Platform',(x,y,top+.067),(w+.25,d+.25,.134),white,.022)
    for side in [-1,1]:
        wall_x=side*(w/2-.12)
        box('Sanctum_Terracotta_Side',(wall_x,y,floor+1.10),(.30,d,2.20),red,.022)
        box('Sanctum_Marble_Side_Dado',(wall_x,y,floor+.28),(.34,d,.55),white,.02)
        for i in range(7):
            box('Sanctum_Side_Stone_Joint',(wall_x+side*.17,y+(i-3)*.87,floor+1.19),
                (.035,.058,1.18),rock,.006)
    back=y+d/2-.11
    box('Sanctum_Inner_Back',(0,back,floor+1.13),(w,.31,2.26),red,.022)
    front=y-d/2
    door=1.33
    for side in [-1,1]:
        span=(w-door)/2
        box('Front_Marble_Sanctum_Jamb',(side*(door+span)/2,front,floor+1.11),(span,.38,2.22),white,.022)
        for column in [1.08,1.73]:
            box('Front_Inscribed_Marble_Panel',(side*column,front-.217,floor+1.32),(.58,.055,1.54),white,.014)
            box('Front_Marble_Panel_StoneJoint',(side*(column+.30),front-.247,floor+1.32),(.029,.019,1.56),rock,.006)
    box('Sanctum_East_Door_Lintel',(0,front,floor+2.13),(door,.41,.22),red,.021)
    box('Sanctum_Cornice',(0,y,floor+2.27),(w+.42,d+.30,.24),red,.031)
    for index,ry in enumerate([.05,3.88]):
        roof('Sanctum_Twin_Hipped_Roof',0,ry,floor+2.38,w+.46,3.94,1.68 if index==0 else 1.32,fabric)
        cylinder('Sanctum_Roof_Cloth_Finial',(0,ry,floor+(4.24 if index==0 else 3.85)),.21,.44,fabric)
    adorn=Sculpture()
    p=palette(adorn)
    for ry,rise in [(.05,1.68),(3.88,1.32)]:
        for row in range(5):
            t=.04+row*.162
            z=floor+2.39+rise*t
            depth=1.98*(1-.75*t)
            width=(w+.39)*(1-t)/2
            for side in [-1,1]:
                adorn.tube([(width*math.cos(math.pi*i/44),ry+side*depth,
                             z) for i in range(45)],.012,p['gold'],6)
    adorn.finish('Roof_Cloth_OrnamentDetail')
    box('Stanapitha_Pedestal',(0,4.01,floor+.30),(1.62,1.18,.59),rock,.039)
    gauri((0,4.0,floor+.60))
    for sx in [-1,1]:
        create_deepam('Mangala_Deepam',(sx*.66,3.04,floor+.04),gold,flame)
    anchor('Mangala_Darshan_Landing',(0,1.92,floor+.05))
    anchor('Sanctum_Lamp_Position',(0,2.79,floor+1.69))
    anchor('Mangala_Facade_Panels_Reference',(-1.61,front-.29,floor+1.22))
    anchor('Mangala_Facade_Panels_Landing',(-1.65,front-2.10,top+.07))

    canopy_range('West_Covered_Prakara',0,11.9,top,19.2,4.8,orange,shade,steel)
    for side in [-1,1]:
        before=set(bpy.context.scene.objects)
        canopy_range('Side_Processional_Shelter',0,0,top,19.9,2.70,orange,shade,steel)
        move=Matrix.Translation((side*8.10,3.4,0))@Matrix.Rotation(side*math.pi/2,4,'Z')
        bpy.context.view_layer.update()
        for obj in set(bpy.context.scene.objects)-before:
            obj.matrix_world=move@obj.matrix_world
    # Charcoal and light tiles across the court, explicitly non-colliding.
    pattern=Sculpture()
    tile=pattern.material('Gaya_Court_Diamond_Inlay',(.064,.117,.125),0,.58)
    for iy in range(36):
        for ix in range(31):
            ox=(ix-15)*.60
            oy=-7.50+iy*.60
            start=len(pattern.vertices)
            pattern.vertices.extend([(ox,oy-.239,top+.007),(ox+.239,oy,top+.007),
                                     (ox,oy+.239,top+.007),(ox-.239,oy,top+.007)])
            pattern.faces.append((start,start+1,start+2,start+3))
            pattern.face_materials.append(tile)
    pattern.finish('Courtyard_Tile_OrnamentDetail')

    # Names are placed by documented membership. Individual small shrine
    # locations within the perimeter ranges remain approximate.
    figs=[
        ('Dakshina_Kali',-5.50,10.02,'kali'),
        ('Ganapati',-2.94,10.02,'ganesha'),
        ('Shiva_East',-.28,10.02,'linga'),
        ('Shiva_West',2.37,10.02,'linga'),
        ('Durga',4.93,10.02,'durga'),
        ('Mahishasuramardini',7.14,10.02,'mahishasuramardini'),
        ('Hanuman',5.57,-2.30,'hanuman')]
    for name,sx,sy,form in figs:
        box(name+'_Niche_Back',(sx,sy+.62,top+1.21),(2.0,.25,2.4),orange,.027)
        box(name+'_Niche_Plinth',(sx,sy,top+.24),(1.7,1.2,.46),rock,.019)
        for side in [-1,1]:
            box(name+'_Niche_Jamb',(sx+side*.843,sy,top+1.14),(.17,.99,2.27),red,.016)
        box(name+'_Niche_Lintel',(sx,sy,top+2.36),(1.94,1.11,.22),red,.019)
        if form=='linga':
            linga(name+'_Shiva_Linga',(sx,sy,top+.46),.92,rock)
        elif form!='ganesha':
            deity_study(name+'_Iconographic_Study',sx,sy,top+.46,form)
        anchor(name+'_Anchor',(sx,sy,top-.034 if form=='ganesha' else top+1.06))
        anchor(name+'_Landing',(sx,sy-2.22,top+.06))
    anchor('Janardana_Vishnu_Reference',(5.7,4.94,top+1.30))
    anchor('Janardana_Vishnu_Landing',(5.7,2.48,top+.06))
    box('Janardana_Vishnu_Reference_Platform',(5.7,4.94,top+.22),(1.88,1.31,.42),rock,.025)
    deity_study('Janardana_Vishnu_Iconographic_Study',5.7,4.94,top+.44,'vishnu')

    for i in range(42):
        sx,sy=rng.uniform(-43,40),rng.uniform(-7,30)
        if abs(sx)<12:
            continue
        sphere('Terrain_Bhasmakut_Scrub',(sx,sy,1.05),(1.01,1.25,1.26),olive,14)
    rotation=Matrix.Rotation(math.pi/2,4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world=rotation@obj.matrix_world


if __name__=='__main__':
    build()
    if not globals().get('DEFER_GLB_EXPORT', False):
        finish('gaya_mangalagauri')
