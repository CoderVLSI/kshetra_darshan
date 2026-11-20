"""Kolhapur Ambabai precinct from Esri imagery, the precinct diagram, and
Prabhudesai figures 4.12–4.15 and 4.22–4.23. Local X is the main west–east axis.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bmesh
import bpy
from mathutils import Matrix, Vector

import common_geometry as geom
import common_materials as mats


def round_profile(name, rings, center, material, ripples=0.0):
    segments = 48
    verts=[]
    for z, rx, ry in rings:
        for i in range(segments):
            a = 2*math.pi*i/segments
            fold = 1 + ripples*math.cos(17*a+.85*z) + ripples*.5*math.cos(9*a)
            verts.append((center[0]+rx*fold*math.cos(a),
                          center[1]+ry*fold*math.sin(a),center[2]+z))
    faces=[tuple(reversed(range(segments)))]
    for row in range(len(rings)-1):
        for i in range(segments):
            a=row*segments+i
            b=row*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.append(tuple(range(len(verts)-segments,len(verts))))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for face in mesh.polygons:
        face.use_smooth=len(face.vertices)==4
    return obj


def line(name, points, depth, material):
    path=bpy.data.curves.new(name,"CURVE")
    path.dimensions="3D"
    path.bevel_depth=depth
    path.bevel_resolution=3
    tr=path.splines.new("POLY")
    tr.points.add(len(points)-1)
    for node,point in zip(tr.points,points):
        node.co=(*point,1)
    obj=bpy.data.objects.new(name,path)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def limb(name, start, end, radius, material):
    delta=Vector(end)-Vector(start)
    obj=sphere(name,(Vector(start)+Vector(end))*.5,(radius,radius,delta.length*.5+radius*.45),material)
    obj.rotation_mode="QUATERNION"
    obj.rotation_quaternion=delta.to_track_quat("Z","Y")


def ambabai(m):
    """Sculpted study of the visible black-stone face and documented attributes."""
    stone=mats.create_black_stone("Ambabai_Polished_Dark_Stone",color=(.041,.029,.025,1),roughness=.64)
    cloth=mats.create_red_silk("Ambabai_Vermilion_Folds",color=(.29,.038,.022,1),roughness=.78)
    ochre=mats.create_red_silk("Ambabai_Pitambari_Border",color=(.51,.21,.029,1),roughness=.72)
    kunkum=mats.create_kumkum_red("Ambabai_Kumkum",color=(.68,.043,.024,1))
    brass=m["brass"]
    before=set(bpy.context.scene.objects)
    round_profile("Ambabai_Pedestal",[(0,.65,.35),(.10,.67,.37),(.17,.59,.33),(.23,.61,.33)],(0,0,0),m["base"])
    sphere("Lion_Flank",(-.39,.22,.47),(.30,.22,.26),stone)
    sphere("Lion_Mane",(-.53,.10,.61),(.176,.165,.21),stone)
    sphere("Lion_Muzzle",(-.53,-.031,.575),(.117,.086,.079),stone)
    for side in (-1,1):
        sphere("Lion_Eye",(-.53+side*.078,-.034,.65),(.023,.019,.019),brass)
        sphere("Lion_Ear",(-.53+side*.108,.08,.77),(.045,.041,.046),stone)
        sphere("Lion_Paw",(-.53+side*.13,.012,.31),(.09,.11,.07),stone)
    round_profile("Ambabai_Sari_Folds",[(.23,.38,.175),(.34,.37,.161),(.56,.31,.153),(.77,.29,.146),
                                      (.98,.211,.122),(1.08,.21,.117)],(0,-.03,0),cloth,.055)
    round_profile("Ambabai_Woven_Hem",[(.24,.382,.181),(.275,.39,.183),(.30,.377,.179)],(0,-.03,0),ochre,.049)
    round_profile("Ambabai_Torso",[(.93,.183,.125),(1.09,.185,.133),(1.16,.235,.151),
                                  (1.31,.252,.153),(1.40,.227,.134),(1.46,.126,.091)],
                  (0,0,0),stone)
    for i in range(5):
        line("Sari_Gold_Pleat",[(.06+i*.026,-.160,.37),(.051+i*.019,-.19,.62),
                              (.026+i*.012,-.164,.84),(.01+i*.007,-.152,1.01)],.007,ochre)
    line("Angavastra_Embroidered_Edge",[(-.19,-.08,1.37),(-.16,-.148,1.28),(-.095,-.173,1.15),
                                         (-.02,-.17,1.06),(.055,-.133,1.00)],.033,ochre)
    sphere("Ambabai_Neck",(0,-.01,1.465),(.095,.093,.116),stone)
    round_profile("Ambabai_Sculpted_Face",[(1.465,.045,.052),(1.485,.086,.078),(1.526,.108,.091),
                                          (1.56,.126,.104),(1.625,.136,.116),(1.685,.132,.109),
                                          (1.731,.121,.091),(1.751,.090,.063)],(0,-.026,0),stone)
    for side in (-1,1):
        sphere("Ambabai_Ear",(side*.129,-.036,1.605),(.035,.027,.066),stone)
        sphere("Ambabai_Cheek",(side*.065,-.114,1.574),(.056,.031,.047),stone)
        sphere("Ambabai_Eye",(side*.055,-.138,1.638),(.040,.013,.016),stone)
        line("Ambabai_Lid",[(side*.021,-.148,1.636),(side*.047,-.153,1.650),
                             (side*.075,-.150,1.651),(side*.095,-.138,1.642)],.0055,stone)
        line("Ambabai_Brow",[(side*.020,-.143,1.662),(side*.049,-.147,1.674),
                              (side*.081,-.143,1.677),(side*.100,-.131,1.672)],.0068,stone)
        for i in range(13):
            a=i*2*math.pi/13
            sphere("Ambabai_Earring",(side*.142+math.cos(a)*.029,-.111,1.555+math.sin(a)*.034),(.009,.007,.009),brass)
    sphere("Ambabai_Nose_Bridge",(0,-.145,1.614),(.023,.026,.052),stone)
    sphere("Ambabai_Nose_Tip",(0,-.165,1.582),(.027,.018,.020),stone)
    line("Ambabai_Closed_Lips",[(-.028,-.130,1.541),(-.010,-.143,1.544),(0,-.145,1.542),
                                 (.014,-.142,1.544),(.028,-.128,1.542)],.0068,stone)
    sphere("Ambabai_Forehead_Kumkum",(0,-.137,1.698),(.024,.007,.026),kunkum)
    round_profile("Ambabai_Serrated_Stone_Crown",[(1.73,.147,.113),(1.77,.150,.12),(1.80,.135,.111),
                                                 (1.85,.115,.10),(1.91,.093,.093),(1.98,.066,.076),(2.01,.041,.056)],
                  (0,-.019,0),stone,.035)
    for j in range(18):
        theta=math.pi*j/17
        sphere("Ambabai_Crown_Bead",(math.cos(theta)*.143,-.025-math.sin(theta)*.110,1.774),
               (.011,.010,.012),brass)
    for j in range(5):
        x=(j-2)*.055
        h=1.98+.023*(2-abs(j-2))
        sphere("Cobra_Hood",(x,.070,h),(.043,.021,.077),stone)
        sphere("Cobra_Head",(x,.048,h+.021),(.018,.018,.023),stone)
    round_profile("Ambabai_Crown_Linga",[(1.99,.028,.023),(2.06,.026,.021),
                                           (2.086,.013,.013),(2.091,.005,.005)],(0,-.056,0),stone)
    for tier in range(3):
        for i in range(25):
            t=math.pi*i/24
            sphere("Ambabai_Hara",(math.cos(t)*(.13+.042*tier),-.135-.051*math.sin(t),
                                   1.43-.015*tier-math.sin(t)*(.095+.07*tier)),(.012,.010,.012),brass)
    for side in (-1,1):
        shoulder=(side*.215,-.004,1.338)
        for upper in (False,True):
            elbow=(side*(.38 if upper else .31),-.028,1.24 if upper else 1.10)
            hand=(side*(.441 if upper else .347),-.135,1.41 if upper else 1.04)
            limb("Ambabai_Upper_Arm",shoulder,elbow,.060,stone)
            sphere("Ambabai_Elbow",elbow,(.053,.048,.054),stone)
            limb("Ambabai_Forearm",elbow,hand,.049,stone)
            sphere("Ambabai_Hand",hand,(.048,.031,.052),stone)
            limb("Ambabai_Bangle",Vector(hand)*.90+Vector(elbow)*.10,
                 Vector(hand)*.81+Vector(elbow)*.19,.053,brass)
            for f in range(4):
                sphere("Ambabai_Hand_Finger",(hand[0]+(f-1.5)*.013,hand[1]-.02,hand[2]-.017),
                       (.010,.013,.026),stone)
    sphere("Citron",(-.354,-.179,1.055),(.052,.043,.045),ochre)
    for j in range(12):
        a=j*math.pi/6
        sphere("Citron_Peel",(-.354+.047*math.cos(a),-.181+.039*math.sin(a),1.056),(.005,.005,.005),brass)
    limb("Mace_Shaft",(-.45,-.13,.405),(-.443,-.138,1.49),.022,brass)
    round_profile("Mace_Ribbed_Head",[(.28,.042,.042),(.32,.073,.073),(.40,.092,.091),(.48,.077,.077),(.53,.034,.033)],
                  (-.45,-.13,0),brass,.10)
    sphere("Shield_Circular_Face",(.443,-.146,1.44),(.125,.037,.145),stone)
    sphere("Shield_Boss",(.443,-.185,1.44),(.040,.020,.045),brass)
    for j in range(32):
        a=j*math.pi/16
        sphere("Shield_Rivet",(.443+.105*math.cos(a),-.169,1.44+.117*math.sin(a)),(.006,.008,.006),brass)
    round_profile("Ritual_Bowl",[(1.031,.032,.026),(1.05,.049,.044),(1.09,.064,.053),
                                (1.102,.067,.056),(1.105,.056,.047)],(.354,-.169,0),brass)
    # A dressed surround, festoon and oil lamps convey the current presentation.
    for side in (-1,1):
        for j in range(37):
            z=.55+j*.036
            x=side*(.54+.10*math.sin(j*math.pi/55))
            sphere("OrnamentDetail_Garland", (x,-.116,z),(.054,.047,.039),
                   m["cream"] if (j//4)%3 else ochre)
        for j in range(6):
            t=j*.071
            sphere("Sanctum_Offering_Flower",(side*(.33+t),-.31,.25),(.057,.039,.031),
                   m["cream"] if j%2 else ochre)
    profile=[(-.79,.31,.23),(-.79,.31,1.15),(-.69,.31,1.64),(-.44,.31,2.02),
             (0,.31,2.19),(.44,.31,2.02),(.69,.31,1.64),(.79,.31,1.15),(.79,.31,.23)]
    line("Sanctum_Surround_Moulding",profile,.083,m["base"])
    line("Sanctum_Surround_Metal_Bead",[(a,b-.07,c+.043) for a,b,c in profile],.026,brass)
    bpy.context.view_layer.update()
    offset=Matrix.Translation((.7,0,.44)) @ Matrix.Rotation(-math.pi/2,4,"Z")
    root=bpy.data.objects.new("Deity_Mahalakshmi",None)
    bpy.context.collection.objects.link(root)
    root.location=(.7,0,1.34)
    bpy.context.view_layer.update()
    for obj in set(bpy.context.scene.objects)-before-{root}:
        local=obj.matrix_world.copy()
        obj.parent=root
        obj.matrix_world=offset @ local
    flame=mats.create_flame_emission("Kolhapur_Lamp",strength=3.1)
    for y in (-1.14,1.14):
        geom.create_deepam("Ambabai_Deepam",(-.31,y,.44),mat_brass=brass,mat_flame=flame)


def box(name, center, size, material, bevel=.025):
    hx, hy, hz = (length / 2 for length in size)
    vertices = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
                (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = center
    obj.data.materials.append(material)
    if bevel:
        edge = obj.modifiers.new("Dressed edges", "BEVEL")
        edge.width = bevel
        edge.segments = 2
    return obj


def solid(name, outline, low, high, material):
    n = len(outline)
    vertices = [(x, y, z) for z in (low, high) for x, y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


sphere_meshes = {}


def sphere(name, center, radii, material):
    mesh = sphere_meshes.get(material.name)
    if mesh is None:
        mesh = bpy.data.meshes.new(material.name + "_Round_Detail")
        form = bmesh.new()
        bmesh.ops.create_uvsphere(form, u_segments=16, v_segments=10, radius=1)
        form.to_mesh(mesh)
        form.free()
        mesh.materials.append(material)
        for face in mesh.polygons:
            face.use_smooth = True
        sphere_meshes[material.name] = mesh
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = center
    obj.scale = radii
    return obj


def anchor(name, point, facing=(-1, 0)):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = point
    # Godot iconographic studies face +Z, corresponding to Blender -Y.
    obj.rotation_euler.z = math.atan2(facing[1], facing[0]) + math.pi / 2


def landmark(key, target, landing, facing=(-1,0)):
    anchor("Kolhapur_" + key, target, facing)
    anchor("Landing_" + key, landing)


def slab(name, x0, x1, y0, y1, bottom, top, material):
    return box(name, ((x0+x1)/2, (y0+y1)/2, (bottom+top)/2),
               (x1-x0, y1-y0, top-bottom), material)


def walls(name, x, y, w, d, base, h, doorway, m, front="-x", floor=False):
    turn = {"-x": -math.pi/2, "+x": math.pi/2, "-y": 0, "+y": math.pi}[front]
    lateral, depth = (d,w) if front in ("-x", "+x") else (w,d)
    transform = Matrix.Translation((x, y, base)) @ Matrix.Rotation(turn, 4, "Z")
    objs = geom.create_garbhagriha(name, width=lateral, depth=depth,
                                  wall_height=h, wall_thickness=.42, door_width=doorway,
                                  door_height=min(h-.22, 2.9), mat=m)
    bpy.context.view_layer.update()
    for obj in objs:
        if obj.name.endswith("_Floor") and not floor:
            bpy.data.objects.remove(obj, do_unlink=True)
        else:
            obj.matrix_world = transform @ obj.matrix_world


def offsets(name, x, y, w, d, z, high, m):
    """Stepped ratha offsets around the outer edge of a broken-square cell."""
    for face in range(4):
        along_x = face < 2
        direction = -1 if face % 2 == 0 else 1
        breadth = d if along_x else w
        for i, offset in enumerate((-.36, -.24, .24, .36)):
            along = offset*breadth
            reach = .18 if abs(offset) > .3 else .38
            if along_x:
                center = (x + direction*(w/2 - .1), y+along, z+high*.5)
                size = (reach+.24, breadth*.106, high)
            else:
                center = (x+along, y + direction*(d/2 - .1), z+high*.5)
                size = (breadth*.106, reach+.24, high)
            box(f"{name}_Ratha_{face}_{i}", center, size, m, .04)


def tier_outline(x, y, radius):
    walk = ((1,0),(1,.38),(.83,.38),(.83,.60),(.60,.60),
            (.60,.83),(.38,.83),(.38,1))
    return [(x + radius*(a*math.cos(i*math.pi/2)-b*math.sin(i*math.pi/2)),
             y + radius*(a*math.sin(i*math.pi/2)+b*math.cos(i*math.pi/2)))
            for i in range(4) for a,b in walk]


def tower(name, x, y, base, radius, height, m):
    # Current pale masonry profile and smaller attached towerlets over the basalt.
    for level in range(8):
        t = level/8
        rim = radius*(1-.75*t**1.12)
        z = base + height*t
        solid(f"{name}_Level_{level}", tier_outline(x,y,rim), z, z+height/8,
              m["plaster"])
        solid(f"{name}_Fillet_{level}", tier_outline(x,y,rim*1.035), z, z+.11, m["cream"])
        if level < 6:
            for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                sphere(f"{name}_Miniature_{level}_{dx}_{dy}", (x+dx*rim*.9,y+dy*rim*.9,z+.25),
                       (.25,.25,.43), m["cream"])
    sphere(name+"_Amalaka", (x,y,base+height), (radius*.29,radius*.29,.2), m["cream"])
    sphere(name+"_Kalasha", (x,y,base+height+.27), (.16,.16,.29), m["brass"])


def steps(name, x, y, z, height, count, width, pitch, m, north=False):
    for i in range(count):
        h = height*(i+1)/count
        center = (x, y+pitch*(i+.5), z+h/2) if north else (x+pitch*(i+.5), y, z+h/2)
        size = (width, pitch, h) if north else (pitch, width, h)
        box(f"{name}_{i:02d}", center, size, m, 0)


def garuda_hall(m):
    slab("Garuda_Mandapa_Platform", -50.8,-21.8,-4.8,4.8,0,.44,m["base"])
    steps("Garuda_West_Stair", -52.2,0,0,.44,3,5,.48,m["base"])
    for i, x in enumerate((-49,-45,-41,-37,-33,-29,-25,-22.5)):
        for side in (-1,1):
            y=side*3.8
            box(f"Garuda_Plinth_{i}_{side}",(x,y,.59),(.7,.70,.30),m["stone"])
            box(f"Garuda_Square_Timber_{i}_{side}",(x,y,2.36),(.37,.37,3.2),m["wood"])
            for z, span in ((3.32,.48),(3.58,.64),(3.8,.90)):
                box(f"Garuda_Capital_{i}_{side}_{z}",(x,y,z),(.55,span,.19),m["wood"])
            if i:
                previous=(-49,-45,-41,-37,-33,-29,-25,-22.5)[i-1]
                # Foliated timber arches between bays.
                samples=[(previous+(x-previous)*j/18, y, 3.21+.50*math.sin(math.pi*j/18)+.07*math.sin(7*math.pi*j/18)) for j in range(19)]
                curve=bpy.data.curves.new("Foliated profile", "CURVE")
                curve.dimensions="3D"
                curve.bevel_depth=.075
                spline=curve.splines.new("POLY")
                spline.points.add(len(samples)-1)
                for p,v in zip(spline.points,samples):
                    p.co=(*v,1)
                obj=bpy.data.objects.new(f"Garuda_Foliated_Arch_{i}_{side}",curve)
                bpy.context.collection.objects.link(obj)
                obj.data.materials.append(m["wood"])
    slab("Garuda_Timber_Ceiling",-51,-21.65,-4.75,4.75,3.91,4.09,m["wood"])
    for side in (-1,1):
        solid("Garuda_Red_Tiled_Roof_" + str(side),
              [(-51.25,0),(-21.45,0),(-21.45,side*5.12),(-51.25,side*5.12)][::side],
              4.14,4.26,m["tile"])
        for row in range(13):
            y=side*(row+.5)*.39
            z=5.66-abs(y)*.29
            obj=box(f"Garuda_Tile_Course_{side}_{row}",(-36.35,y,z),(29.8,.43,.14),m["tile"])
            obj.rotation_euler.x=side*-.28
    box("Garuda_Ridge",(-36.35,0,5.69),(30,.25,.18),m["tile"])


def linga(key, x, y, z, m, r=.28):
    box(key+"_Yoni", (x,y,z+.15),(2.85*r,2.23*r,.30),m["base"])
    sphere(key+"_Linga",(x,y,z+.36),(r,r,.36),m["stone"])
    box(key+"_Spout",(x,y+.95*r,z+.23),(.55*r,2*r,.12),m["stone"])


def niche(key, x, y, z, facing, landing, m):
    fx, fy=facing
    for side in (-1,1):
        box(key+"_Niche_Pier",(x-fx*.22-fy*.65*side,y-fy*.22+fx*.65*side,z+.94),(.21,.21,1.88),m["base"])
    box(key+"_Niche_Lintel",(x-fx*.22,y-fy*.22,z+1.99),
        (.34,1.59,.24) if fx else (1.59,.34,.24),m["base"])
    box(key+"_Niche_Sill",(x,y,z+.06),(.76,1.48,.12) if fx else (1.48,.76,.12),m["base"])
    landmark(key,(x,y,z+.14),landing,facing)


def inner(m):
    slab("Trikuta_Plinth", -22.15,6.5,-5.2,5.2,0,.44,m["base"])
    garuda_hall(m)
    for name, start, stop, width in (("Mukha",-22,-16,9.8),("Sabha",-16,-8,10.5),("Antarala",-8,-4.0,8.6)):
        slab(name+"_Slab",start,stop,-width/2,width/2,3.74,4.07,m["base"])
        for x in (start+.45,stop-.38):
            for y in (-width/2+.36,width/2-.36):
                geom.create_pillar(f"{name}_Stone_Pillar_{x}_{y}",(x,y,.44),height=3.30,radius=.33,mat=m["base"],style="octagonal")
    walls("Mahalakshmi_Garbha",.5,0,8.7,7.5,.40,3.25,2.32,m["stone"])
    slab("Mahalakshmi_Upper_Floor",-5.1,6.5,-5.15,5.15,3.62,3.93,m["base"])
    offsets("Mahalakshmi",.6,0,11.0,10.3,.28,6.7,m["stone"])
    # Open outer pradakshina around the lower cell with a three-bay projection.
    for side in (-1,1):
        box("Ambulatory_Wall_"+str(side),(1.18,side*5.05,2.05),(10.6,.45,3.96),m["base"])
        slab("Ambulatory_Platform_"+str(side),-5.1,6.5,side*4.47-.62,side*4.47+.62,0,.44,m["base"])
    slab("Ambulatory_East_Platform",4.7,6.5,-5.1,5.1,0,.44,m["base"])
    box("Ambulatory_East_Wall",(6.37,0,2.12),(.52,10.4,3.95),m["base"])
    for z in (.22,.41,3.53,3.73,6.95):
        for side in (-1,1):
            box(f"Ambulatory_Eave_{side}_{z}",(.8,side*5.06,z),(11.3,.57,.15),m["base"])
    for name,key,y,front,side in (("Mahakali","mahakali",13.1,"-y",1),("Mahasaraswati","mahasaraswati",-11.1,"+y",-1)):
        x=-12.3
        d=7.9 if side==1 else 7.1
        w=8 if side==1 else 6.9
        slab(name+"_Plinth",x-w/2-.32,x+w/2+.32,y-d/2-.3,y+d/2+.3,0,.44,m["base"])
        slab(name+"_Approach",x-2.1,x+2.1,min(y-side*d/2,side*4.4),max(y-side*d/2,side*4.4),0,.44,m["base"])
        walls(name,x,y,w,d,.4,3.22,2.0,m["stone"],front)
        offsets(name,x,y,w,d,.22,3.25,m["base"])
        slab(name+"_Roof",x-w/2-.42,x+w/2+.42,y-d/2-.45,y+d/2+.45,3.52,3.95,m["base"])
        tower(name,x,y,3.95,w*.52,4.2 if side==1 else 3.35,m)
        landmark(key,(x,y+side*1,.46),(x,y-side*2,.44),(0,-side))
    main_tower = (1.05,0)
    walls("Matulinga_Upper_Shrine",.9,0,9.15,7.65,3.89,3.45,2.2,m["base"])
    slab("Matulinga_Roof",-4.5,6.7,-5.4,5.4,7.21,7.52,m["base"])
    tower("Mahalakshmi_Shikhara",*main_tower,7.52,5.2,6.0,m)
    slab("Nandi_Upper_Mandapa",-10.3,-3.3,-2.45,3.22,3.68,3.93,m["base"])
    slab("Nandi_Upper_Roof",-10.45,-3.45,-2.55,3.3,6.97,7.26,m["base"])
    for x in (-10,-4.1):
        for y in (-2.17,2.9):
            geom.create_pillar(f"Upper_Pillar_{x}_{y}",(x,y,3.93),height=3.05,radius=.22,mat=m["base"])
    steps("Matulinga_Stair",-17.20,6.15,0,3.93,22,1.85,.32,m["base"])
    slab("Matulinga_Stair_Landing",-10.16,-8.2,2.75,7.1,3.68,3.93,m["base"])
    linga("Matulinga",2.5,0,3.94,m)
    nandi=geom.create_nandi("Nandi_Upper",(-7.8,.28,3.93),scale=.75,mat=m["stone"])
    nandi.name = "RenderOnly_Nandi_Upper"
    nandi.rotation_euler.z = -math.pi/2
    landmark("upper_shiva",(2.5,0,4.35),(-.35,0,3.93))
    landmark("upper_nandi",(-7.8,.28,4.36),(-10,.28,3.93))
    landmark("upper_ganesha",(2.1,2.3,3.98),(-.5,2.3,3.93))
    sphere("Paduka_Plinth",(2.1,-1.95,4.05),(.36,.28,.10),m["base"])
    for y in (-2.05,-1.85):
        sphere("Foot_Impression",(2.1,y,4.15),(.17,.065,.035),m["brass"])
    landmark("paduka",(2.1,-1.95,4.24),(-.53,-1.95,3.93))
    landmark("matulinga_stair",(-13.3,6.15,2.5),(-18.2,6.15,.0))
    ambabai(m)
    landmark("main",(.7,0,1.23),(-2.9,0,.44))
    anchor("Sanctum_Lamp_Position",(-1.4,-.46,2.14))
    # Pitali threshold, Kasav Chowk, and the flanking approach shrines follow the precinct map.
    box("Pitali_Umbartha",(-11.1,0,.48),(.34,2.2,.10),m["brass"])
    sphere("Kasav_Tortoise_Shell",(-16.3,0,.56),(.57,.46,.18),m["brass"])
    sphere("Kasav_Tortoise_Head",(-15.67,0,.52),(.19,.14,.1),m["brass"])
    for dx in (-.31,.32):
        for dy in (-.36,.36):
            sphere("Kasav_Tortoise_Limb",(-16.3+dx,dy,.52),(.20,.12,.079),m["brass"])
    box("Tortoise_Platform",(-16.3,0,.468),(1.8,1.54,.056),m["base"])
    landmark("kasav",(-16.3,0,.74),(-18.5,-.7,.44))
    landmark("pittali",(-11.1,0,.68),(-12.25,0,.44))
    landmark("garuda_mandapa",(-40,0,2.27),(-44,0,.44))
    # The precinct map identifies the mandapa; the older brass pillar is not retained.
    niche("ganesh",-20.4,3.45,.44,(0,-1),(-20.4,1,.44),m)
    niche("umashankar",-24.6,3.5,.44,(0,-1),(-24.6,1.0,.44),m)
    niche("jay",-10.7,2.38,.44,(0,-1),(-11.9,1,.44),m)
    niche("vijay",-10.7,-2.38,.44,(0,1),(-11.9,-1,.44),m)
    niche("bharata",-14.6,10.4,.46,(0,-1),(-13.7,7.80,.44),m)
    niche("shatrughna",-13.3,18.3,.24,(0,1),(-13.3,20.9,0),m)
    niche("yantra",-13.9,12.9,.45,(1,0),(-11,12.6,.44),m)
    niche("surya",-15.2,8.08,.34,(-1,0),(-17.3,8.08,0),m)
    niche("ravalnath",-15.4,-6.25,.25,(0,-1),(-16.7,-8.2,0),m)
    niche("krushna",-18.2,-6.1,.24,(0,-1),(-18.2,-8.8,0),m)
    niche("gajalakshmi",-22.1,-5.2,.23,(0,-1),(-22.1,-7.95,0),m)
    niche("venkatesha",.3,5.61,.38,(0,1),(.3,8.3,0),m)
    niche("katyayani",6.77,0,.38,(1,0),(9.9,0,0),m)
    niche("gowri_shankar",.3,-5.61,.38,(0,-1),(.3,-8.4,0),m)



# Precinct diagram uses west at the bottom, with north at the left.
# Local metres are tied to the aerial roof footprint and courtyard perimeter.
def diagram(u,v):
    return ((195-v)*.125, (392-u)*.115)


def court_cell(key,x,y,facing,m,study=None,width=2.45):
    fx,fy=facing
    front={(-1,0):"-x",(1,0):"+x",(0,-1):"-y",(0,1):"+y"}[facing]
    walls(key,x,y,width,2.6,0,2.54,1.45,m["stone"],front)
    slab(key+"_Roof",x-width/2-.15,x+width/2+.15,y-1.46,y+1.46,2.53,2.77,m["base"])
    if study == "linga":
        linga(key,x,y,0,m,.21)
    landmark(key,(x,y,.18),(x+2.95*fx,y+2.95*fy,0),facing)


def surrounding_precinct(m):
    # Perimeter, thresholds and street-facing Mahadwar/Nagarkhana.
    west,east,south,north=-71.35,21.50,-24.0,36.0
    gap_x=9.1
    for name,x0,x1,y0,y1 in (
        ("West_N",west-.4,west+.4,2.8,north),("West_S",west-.4,west+.4,south,-2.8),
        ("East_N",east-.4,east+.4,11.9,north),("East_S",east-.4,east+.4,south,5.9),
        ("South_W",west,gap_x-2.5,south-.4,south+.4),
        ("South_E",gap_x+2.5,east,south-.4,south+.4),
    ):
        slab("Prakara_"+name,x0,x1,y0,y1,0,3.08,m["base"])
        slab("Prakara_Coping_"+name,x0-.1,x1+.1,y0-.1,y1+.1,3.08,3.27,m["stone"])
    for x0,x1 in ((west,-13.0),(-7.0,east)):
        slab("Prakara_North",x0,x1,north-.4,north+.4,0,3.08,m["base"])
    for key,x,y,fx,fy in (("mahadwar",west,0,1,0),("ghati", -10,north,0,-1),
                          ("east_gate",east,8.9,-1,0),("south_gate",gap_x,south,0,1)):
        for s in (-1,1):
            box(key+"_Jamb",(x+fy*s*2.62,y+fx*s*2.62,1.65),(1.38,1.38,3.3),m["base"])
        box(key+"_Lintel",(x,y,3.16),(1.7,6.3,.42) if fx else (6.3,1.7,.42),m["base"])
        landmark(key,(x,y,2.3),(x+3.0*fx,y+3.0*fy,0),(fx,fy))
    slab("Nagarkhana_Upper_Storey",west-1.42,west+1.42,-3.7,3.7,3.36,5.55,m["wood"])
    for k in (-2.8,-1.4,0,1.4,2.8):
        box("Nagarkhana_Timber_Pilaster",(west+1.44,k,4.47),(.17,.22,2.09),m["cream"])
    slab("Nagarkhana_Tile_Roof",west-1.66,west+1.66,-3.96,3.96,5.54,5.79,m["tile"])
    # The in-compound arcades and mapped cells follow the diagram. The Kashi
    # and Jyotirlinga structures span the north gate passage in the diagram.
    court_stops=(
        ("siddhivinayak_west",317,743,(1,0),None), ("kanakeshwar",193,744,(1,0),"linga"),
        ("shakambhari",103,744,(1,0),None), ("jyotirlinga",55,335,(0,-1),"linga"),
        ("kartik",58,95,(0,-1),None), ("vitthal_rakhmai",94,193,(0,-1),None),
        ("mudagaleshwar",96,157,(0,-1),"linga"), ("shankaracharya",94,126,(0,-1),None),
        ("swami_samarth",94,76,(0,-1),None), ("dashavatara",85,43,(0,-1),None),
        ("rama_panchayatana",140,44,(-1,0),None), ("maruti",228,44,(-1,0),None),
        ("east_shani",354,46,(-1,0),None), ("courtyard_shiva",423,46,(-1,0),"linga"),
        ("gajanan_maharaj",456,47,(-1,0),None), ("shani_maruti",486,48,(-1,0),None),
        ("lakshmi_narayana",515,48,(-1,0),None), ("khandoba",544,48,(-1,0),None),
        ("nagai",567,48,(-1,0),None), ("atibaleshwar",594,86,(0,1),"linga"),
        ("kala_bhairava",585,174,(0,1),None), ("siddhivinayak_south",585,220,(0,1),None),
        ("mahishasuramardini",585,264,(0,1),None), ("tulja_bhavani",585,310,(0,1),None),
        ("indrasabha",585,352,(0,1),None), ("ekamukhi_datta",585,400,(0,1),None),
    )
    for key,u,v,facing,study in court_stops:
        x,y=diagram(u,v)
        y=max(south+1.9,min(north-1.7,y))
        x=max(west+2.1,min(east-2.3,x))
        # The north gate porch has its own gate-side masonry.
        if key=="jyotirlinga":
            y=north-2.75
            x=-21.0
        court_cell(key,x,y,facing,m,study)
    # Unlike the east-end wall cells, the Sheshashayi relief is recessed in a
    # distinct hall. The adjacent Navagraha Mandapa is named for ceiling panels.
    x,y=diagram(385,43)
    court_cell("courtyard_vishnu",x-1.5,y,(-1,0),m,width=3.30)
    slab("Sheshashayi_Relief_Backing",x-1.0,x-.88,y-.96,y+.96,.35,1.80,m["base"])
    for i in range(5):
        sphere("Sheshashayi_Serpent_Coil",(x-1.16,y,.5+i*.055),(.2,.85,.10),m["stone"])
    sphere("Sheshashayi_Reclining_Vishnu",(x-1.33,y+.10,.95),(.14,.59,.14),m["stone"])
    sphere("Sheshashayi_Crowned_Head",(x-1.34,y+.62,1.07),(.12,.13,.13),m["brass"])
    for i in range(5):
        sphere("Sheshashayi_Cobra_Hood",(x-1.13,y+.49+i*.09,1.16+math.sin(i*math.pi/4)*.14),
               (.10,.073,.17),m["stone"])
    # Replace the navigation anchor at the sculpture face, still inside its cell.
    bpy.data.objects["Kolhapur_courtyard_vishnu"].location=(x-1.36,y,1.04)
    x,y=diagram(94,217)
    slab("Navagraha_Platform",x-2.25,x+2.25,y-1.85,y+1.85,0,.26,m["base"])
    for px in (-1.88,1.88):
        for py in (-1.48,1.48):
            geom.create_pillar(f"Navagraha_Pillar_{px}_{py}",(x+px,y+py,.26),
                               height=2.70,radius=.22,mat=m["stone"],style="octagonal")
    slab("Navagraha_Roof",x-2.27,x+2.27,y-1.89,y+1.89,2.96,3.24,m["base"])
    for i in range(3):
        for j in range(3):
            box(f"Ashtadikpala_Ceiling_Panel_{i}_{j}",(x+(i-1)*.77,y+(j-1)*.72,2.89),(.74,.69,.14),m["cream"])
    landmark("navagrahas",(x,y,2.84),(x,y-2.78,0),(0,-1))
    # Preserve Kashi Vishwanath and its water court as a different site from Manikarnika Kund.
    x,y=-5.9,40.2
    court_cell("visweshwar",x,y,(0,-1),m,"linga",3.65)
    tower("Kashi_Vishweshwar_Vimana",x,y,2.77,1.55,2.77,m)
    x,y=-1.5,40.0
    slab("Kashi_Kund_Rim",x-1.40,x+1.40,y-1.65,y+1.65,0,.40,m["base"])
    slab("Kashi_Kund_Water",x-1.18,x+1.18,y-1.42,y+1.42,.42,.44,m["water"])
    landmark("kashi_kund",(x,y,.46),(x,y-2.2,0),(0,-1))
    slab("Kashi_North_Court_Parapet",-14,1.5,43.7,44.1,0,1.01,m["base"])
    # Five lamp towers and the serpent shrine on the north side of the western court.
    x,y=diagram(276,494)
    for i,(dx,dy) in enumerate(((-1.7,-1.7),(-1.7,1.7),(0,0),(1.7,-1.7),(1.7,1.7))):
        z=0
        for k in range(7):
            side=1.06-k*.105
            box(f"Deepmal_{i}_{k}",(x+dx,y+dy,z+.30),(side,side,.60),m["base"])
            z+=.60
        sphere("Deepmal_Finial",(x+dx,y+dy,z+.11),(.19,.19,.25),m["stone"])
    landmark("deepmals",(x,y,1.9),(x-3.5,y,0))
    court_cell("nagmandir",x+3.7,y,(0,-1),m)
    x,y=diagram(171,432)
    court_cell("gurudev_datta",x,y,(0,-1),m,width=3.9)
    x,y=diagram(183,515)
    court_cell("niranjan_samadhi",x,y,(0,-1),m,width=3.7)
    for x,y,r in ((6,23.8,3.7),(-33,18,2.1)):
        geom.create_tree(f"Courtyard_Tree_{x}",(x,y,0),height=r*2.2,mat_trunk=m["wood"],mat_leaves=m["leaf"])
    landmark("banyan",(6,23.8,1.9),(6,19.5,0),(0,-1))


def roofed_context(m):
    """Low roof strips at the walled compound and surrounding urban blocks."""
    for name, x0, x1, y0, y1 in (
        ("North_Arcade",-4.0,21.1,33.5,35.78),
        ("East_Arcade_N",19.2,21.15,12.1,34.2),
        ("East_Arcade_S",19.2,21.15,-22.1,5.5),
        ("South_Arcade", -32.0,6.15,-23.72,-20.75),
        ("West_Arcade_N",-70.96,-68.65,5.0,31.5),
    ):
        slab(name+"_Coping",x0,x1,y0,y1,3.00,3.21,m["base"])
    # Low nearby roof masses establish the present crowded city edge without
    # attributing the neighboring buildings to the sacred compound.
    for i,(x0,x1,y0,y1,h) in enumerate((
        (-73,-56,39.0,45.3,3.4),(-54.5,-39,39.3,45.6,4.5),
        (-37,-24,39.6,44.7,3.35),(-22,-16,39.8,45.9,4.2),
        (-72,-55,-32,-27.8,3.8),(-53,-42,-31.2,-27,4.15),
        (-39,-20,-33,-27.6,4.0),(-18,3,-33.3,-27.9,3.65),
        (6,23,-33.6,-28.2,3.8),(25.4,31,-20,-7.0,3.5),
        (25.2,31,-4.4,5.2,4.11),(25.7,31,13.7,25.5,3.9),
        (25.3,31,28.6,40,4.1),
    )):
        slab(f"City_Context_{i}",x0,x1,y0,y1,0,h,m["cream"])
        slab(f"City_Context_Roof_{i}",x0-.2,x1+.2,y0-.22,y1+.22,h,h+.22,
             m["tile"] if i%3 else m["base"])


def build():
    geom.clear_scene()
    sphere_meshes.clear()
    m={
        "stone":mats.create_granite_stone("Kolhapur_Dark_Basalt",color=(.115,.103,.087,1),roughness=.93),
        "base":mats.create_granite_stone("Kolhapur_Dressed_Basalt",color=(.16,.145,.122,1),roughness=.93),
        "paving":mats.create_granite_stone("Kolhapur_Courtyard_Stone",color=(.37,.35,.31,1)),
        "plaster":mats.create_white_marble("Kolhapur_Pale_Limewash",color=(.54,.47,.34,1),roughness=.94),
        "cream":mats.create_white_marble("Kolhapur_Offwhite_Trim",color=(.69,.62,.49,1),roughness=.88),
        "tile":mats.create_terracotta("Kolhapur_Terracotta_Tiles",color=(.30,.091,.056,1),roughness=.96),
        "wood":mats.create_wood("Kolhapur_Garuda_Timber",color=(.22,.108,.055,1)),
        "brass":mats.create_brass_metal("Kolhapur_Brass",color=(.75,.46,.135,1)),
        "leaf":mats.create_green_foliage("Kolhapur_Closed_Canopy"),
        "water":mats.create_white_marble("Kolhapur_Kund_Water",color=(.13,.27,.23,1)),
    }
    slab("Ground_Main",-79,32,-34,47,-.35,0,m["paving"])
    inner(m)
    surrounding_precinct(m)
    roofed_context(m)
    anchor("Spawn_Point",(-65.7,0,0))
    anchor("Arrival_Facing",(-49,0,0))
    bpy.context.view_layer.update()
    # The outline and roof ridge in the Esri aerial follow this oblique axis.
    north=Matrix.Rotation(math.radians(19.0),4,"Z")
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world=north @ obj.matrix_world
    path=os.path.join(os.path.dirname(os.path.dirname(__file__)),"godot","assets","models",
                      "kolhapur_mahalakshmi_kshetra_full.glb")
    bpy.ops.export_scene.gltf(filepath=path,export_format="GLB",export_apply=True,
                              export_yup=True,export_materials="EXPORT",export_cameras=False,
                              export_lights=False)
    print(f"Kolhapur exported: {path} ({os.path.getsize(path)} bytes)")


if __name__=="__main__":
    build()
