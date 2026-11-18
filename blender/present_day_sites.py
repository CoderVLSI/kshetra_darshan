"""Original, reference-led studies of three previously missing destinations.

These are present-condition architectural blockouts, not measured replicas.
No photographed inscriptions, unknown idols or lost roofs are invented.
Sources and specific limits ship in each site's reference_notes entry.
"""
import math
import random
from pathlib import Path
import bpy
from common_geometry import clear_scene, create_pillar, create_garbhagriha, create_gopuram
from common_materials import create_granite_stone, create_white_marble, create_gold_metal

ROOT = Path(__file__).resolve().parent.parent


def material(name, color, roughness=.8, metal=0, emission=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    s = m.node_tree.nodes.get('Principled BSDF')
    s.inputs['Base Color'].default_value = (*color, 1)
    s.inputs['Roughness'].default_value = roughness
    s.inputs['Metallic'].default_value = metal
    if emission:
        s.inputs['Emission Color'].default_value = (*color, 1)
        s.inputs['Emission Strength'].default_value = emission
    return m


def box(name, p, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Worn edges', 'BEVEL')
        b.width = bevel
        b.segments = 2
    return o


def sphere(name, p, scale, mat, segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=16, radius=1, location=p)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    for poly in o.data.polygons:
        poly.use_smooth = True
    return o


def cylinder(name, p, radius, height, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=height, location=p)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o


def anchor(name, p):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = p
    return o


def keep_parent(o, parent):
    matrix = o.matrix_world.copy()
    o.parent = parent
    o.matrix_world = matrix
    return o


def enclosure(name, center, w, d, h, mat, gates=True):
    x,y,z=center
    gap=4.0 if gates else 0
    for sign in [-1,1]:
        for side in [-1,1]:
            span=(w-gap)/2
            box(f'{name}_NS_{sign}_{side}',(x+side*(gap/2+span/2),y+sign*d/2,z+h/2),(span,.65,h),mat,.025)
            span=(d-gap)/2
            box(f'{name}_EW_{sign}_{side}',(x+sign*w/2,y+side*(gap/2+span/2),z+h/2),(.65,span,h),mat,.025)


def linga(name, p, height, mat):
    x,y,z=p
    a=anchor(name,p)
    for o in [cylinder(name+'_Yoni',(x,y,z+.16),height*.40,.32,mat),
              box(name+'_Spout',(x+.45*height,y,z+.22),(height*.9,height*.23,.18),mat,.04),
              cylinder(name+'_Shaft',(x,y,z+height*.50),height*.21,height*.70,mat),
              sphere(name+'_Crown',(x,y,z+height*.85),(height*.21,height*.21,height*.19),mat)]:
        keep_parent(o,a)
    return a


def dome(name,p,r,h,mat):
    # Lathed profile reproduces the visible bulbous dome silhouette, not a cone.
    profile=[(0,1),(.10,1.06),(.25,1.13),(.42,1.08),(.60,.91),(.75,.64),(.88,.34),(1,.03)]
    verts=[]; faces=[]; rings=64
    for t,rad in profile:
        for k in range(rings):
            a=math.tau*k/rings
            verts.append((p[0]+r*rad*math.cos(a),p[1]+r*rad*math.sin(a),p[2]+h*t))
    for row in range(len(profile)-1):
        for k in range(rings):
            a=row*rings+k;b=row*rings+(k+1)%rings
            faces.append((a,b,b+rings,a+rings))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
    for f in mesh.polygons:f.use_smooth=True
    cylinder(name+'_Finial',(p[0],p[1],p[2]+h+.27),.08,.55,mat)
    sphere(name+'_FinialBead',(p[0],p[1],p[2]+h+.25),(.14,.14,.12),mat)


def arch(name, x,y,z,w,h,thick,mat):
    # Voussoirs leave the passage genuinely open.
    radius=w/2
    for sign in [-1,1]:
        box(name+'_Jamb',(x+sign*(radius+.12),y,z+(h-radius)/2),(.24,thick,h-radius),mat,.025)
    for k in range(20):
        t=math.pi*(k+.5)/20
        o=box(name+'_Voussoir',(x+(radius+.12)*math.cos(t),y,z+h-radius+(radius+.12)*math.sin(t)),(.24,thick,math.pi*(radius+.12)/20+.025),mat,.012)
        o.rotation_euler.y=-t


def finish(site):
    target=ROOT/'godot/assets/models'/f'{site}_kshetra_full.glb'
    bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',export_apply=True,export_yup=True,export_cameras=False,export_lights=False)
    print('PRESENT_DAY_STUDY',site)


def build_sharada():
    clear_scene();rng=random.Random(617)
    grass=material('Sharada_ValleyGrass',(.19,.25,.12))
    stone=[create_granite_stone('Sharada_LocalStone_'+str(i),(.31+i*.018,.30+i*.015,.25+i*.012,1)) for i in range(6)]
    box('Ground_Valley',(0,0,-.20),(105,120,.4),grass)
    top=10.08
    # Grass court and a hillock rather than a fabricated paved fort terrace.
    # The northern retaining face is documented; the slope is contextual art.
    box('Hill_Base',(0,1,top/2),(44,30,top),grass)
    box('Enclosure_Floor',(0,1,top-.1),(43,29,.2),grass)
    box('Northern_Retaining_Wall',(0,-13.78,top/2),(43,.55,top),stone[2])
    vertices=[];faces=[];count=96
    for ring in range(3):
        for k in range(count):
            a=math.tau*k/count
            # Superellipse keeps the court flat while softening the hill edges.
            x=math.copysign(abs(math.cos(a))**.40,math.cos(a))
            y=math.copysign(abs(math.sin(a))**.40,math.sin(a))
            scale=[1,1.37,1.8][ring]
            vertices.append((x*22*scale,y*15*scale+1,[top-.08,top*.35,-.12][ring]))
    for ring in range(2):
        for k in range(count):
            n=(k+1)%count
            faces.append((ring*count+k,(ring+1)*count+k,(ring+1)*count+n,ring*count+n))
    mesh=bpy.data.meshes.new('Context_Hillock');mesh.from_pydata(vertices,[],faces);mesh.update()
    hill=bpy.data.objects.new('Hill_Base_ContextSlope',mesh);bpy.context.collection.objects.link(hill);hill.data.materials.append(grass)
    # 63 approached stone-slab steps are documented by DOAM. Rise and tread
    # here are navigable design dimensions; they are not a survey of each slab.
    for k in range(63):
        h=(k+1)*.16
        box(f'Approach_Step_{k+1:02}',(0,-34.16+(k+.5)*.32,h/2),(2.7,.32,h),stone[k%6],.012)
    anchor('Spawn_Point',(0,-37,.05))
    # DOAM documents a northern gateway. Close the other three breaks
    # inherited from the generic four-gate enclosure helper.
    enclosure('Enclosing_Quadrangle',(0,1,top),43,29,1.65,stone[1])
    box('South_Enclosure_Continuation',(0,15.5,top+.825),(4,.65,1.65),stone[1])
    for side in [-1,1]:
        box('Side_Enclosure_Continuation',(side*21.5,1,top+.825),(.65,4,1.65),stone[1])
    # The preserved entrance masonry and recessed cell, not a new gopuram.
    for x in [-2.1,2.1]:
        box('Entrance_Stone_Pier',(x,-13.5,top+1.9),(1.15,1.1,3.8),stone[2],.07)
    arch('Entrance_Trefoil_Lower',0,-13.5,top,2.65,3.4,.75,stone[4])
    # Central roofless sanctuary: jointed masonry and surviving pilasters.
    court_objects=set(bpy.context.scene.objects)
    cy=3.8;base=top+.48
    box('Sanctuary_Platform',(0,cy,top+.24),(10,10,.48),stone[3],.05)
    for k in range(3):
        box('Sanctuary_Step_'+str(k),(0,cy-5.9+k*.40,top+(k+1)*.16/2),(3.2,.4,(k+1)*.16),stone[4],.025)
    ruin=anchor('Sanctuary_Ruins',(0,cy,base))
    floor=box('Sanctuary_Ruins_Floor',(0,cy,base-.04),(6.4,6.4,.08),stone[2]);keep_parent(floor,ruin)
    # Individual irregular stones retain joints and a broken upper silhouette.
    for face in range(4):
        for row in range(11):
            for col in range(6):
                along=-3.45+(col+.5)*1.15
                if face==0 and abs(along)<1.2 and row<7:continue
                if row>8 and rng.random()<.27:continue
                z=base+(row+.5)*.48
                p=(along,cy-3.45,z) if face==0 else ((3.45,cy+along,z) if face==1 else ((along,cy+3.45,z) if face==2 else (-3.45,cy+along,z)))
                size=(1.12,.74,.46) if face%2==0 else (.74,1.12,.46)
                o=box('Sanctuary_Masonry',p,size,rng.choice(stone),.045);keep_parent(o,ruin)
    for sx in [-1,1]:
        for sy in [-1,1]:
            for level,sz in [(0,.18),(.25,.18),(4.6,.18),(4.85,.20)]:
                box('Surviving_Pilaster_Course',(sx*3.5,cy+sy*3.5,base+level+.12),(1.15,1.15,sz),stone[3],.03)
            create_pillar('Surviving_Pilaster',(sx*3.5,cy+sy*3.5,base+.35),4.25,.35,mat=stone[1])
    for x in [-1.48,1.48]:
        box('Sanctuary_Door_Jamb',(x,cy-3.7,base+2.5),(.70,.85,5.0),stone[4],.055)
    box('Surviving_Door_Lintel',(0,cy-3.7,base+5.03),(3.8,1.0,.55),stone[2],.06)
    # Recessed false-door motifs on three sides; no invented inscription text.
    for face in [1,2,3]:
        for sign in [-1,1]:
            p=(3.87,cy+sign*1.30,base+2.05) if face==1 else ((sign*1.30,cy+3.87,base+2.05) if face==2 else (-3.87,cy+sign*1.30,base+2.05))
            box('Recessed_Niche_Pilaster',p,(.22,.36,3.4) if face!=2 else (.36,.22,3.4),stone[4],.025)
    for k in range(22):
        x=rng.choice([-1,1])*rng.uniform(4.7,8); y=cy+rng.uniform(-6,6)
        o=box('Fallen_Masonry',(x,y,top+.12),(rng.uniform(.4,1),rng.uniform(.35,.8),.24),rng.choice(stone),.06);o.rotation_euler.z=rng.random()*3
    # No roof and no presumed original idol: the surviving sanctuary is the
    # destination. Current Teetwal and Sringeri sculptures are different sites.
    # DOAM records the west door at a right angle to the north entry.
    # Local north points toward -Y, so local west points toward +X.
    from mathutils import Matrix
    pivot=Matrix.Translation((0,cy,0))
    quarter_turn=pivot @ Matrix.Rotation(math.pi/2,4,'Z') @ pivot.inverted()
    bpy.context.view_layer.update()
    for obj in set(bpy.context.scene.objects)-court_objects:
        if obj.parent is None:
            obj.matrix_world=quarter_turn @ obj.matrix_world
    finish('kashmir_sharada')


def build_jwala():
    clear_scene()
    white=create_white_marble('Jwala_Whitewashed_Stone',(.83,.81,.75,1),.65)
    dark=material('Jwala_Dark_Paving',(.20,.22,.23));gold=create_gold_metal('Jwala_Gilded_Domes')
    rock=create_granite_stone('Jwala_Rock',(.14,.13,.12,1));red=material('Jwala_Red_Trim',(.45,.065,.035))
    box('Ground_Courtyard',(0,0,-.12),(44,38,.24),white)
    # Alternating marble paving appears in the inspected courtyard photograph.
    for i in range(40):
        for j in range(30):
            if (i+j)%2:box('Courtyard_Checker',(i-19.5,j-14.5,.006),(.96,.96,.012),dark)
    enclosure('Courtyard_Boundary',(0,0,0),42,36,1.1,white)
    x,y=-9,8
    create_garbhagriha('Jwala_Main_Hall',(x,y,0),width=13,depth=10,wall_height=4.2,wall_thickness=.55,mat=white,door_width=3.2,door_height=3.4)
    box('Jwala_Main_Roof',(x,y,4.25),(13.8,10.8,.35),white,.06)
    for dx in [-6.5,6.5]:
        for dy in [-5,5]:dome('Corner_Gilded_Cupola',(x+dx,y+dy,4.55),.70,.85,gold)
    cylinder('Central_Dome_Drum',(x,y,4.9),2.4,.75,white)
    dome('Central_Gilded_Dome',(x,y,5.25),2.45,2.65,gold)
    # Arcaded entrance veranda has open passages rather than a solid facade.
    box('Veranda_Roof',(x,y-6.0,3.8),(13.7,2.0,.25),white,.04)
    # Courtyard photograph shows a paired front opening and an arcade
    # continuing along the side facing the paved court.
    for dx in [-1.25,1.25]:arch('Veranda_Arch',x+dx,y-6.25,0,2.2,3.65,.45,white)
    box('Side_Gallery_Roof',(x+7.1,y,3.8),(1.5,10.8,.25),white,.04)
    for dy in [-3.6,-1.2,1.2,3.6]:
        for side in [-1,1]:
            box('Court_Gallery_Pier',(x+7.65,y+dy+side*1.05,1.35),(.32,.20,2.7),white,.02)
        for i in range(14):
            a=math.pi*(i+.5)/14
            block=box('Court_Gallery_Arch',(x+7.65,y+dy+1.05*math.cos(a),2.70+1.05*math.sin(a)),(.32,.20,.25),white,.01)
            block.rotation_euler.x=a
    # Modest blue/gold flames in rock recesses, not nine anthropomorphic idols.
    blue=material('Jwala_Blue_Flame',(.07,.25,1),.35,emission=3)
    tip=material('Jwala_Golden_Flame',(1,.48,.08),.35,emission=2)
    names=['Mahakali','Annapurna','Chandi','Hinglaj','Vindhyavasini','Mahalakshmi','Saraswati','Ambika','Anjana']
    for k,name in enumerate(names):
        px=x-4+(k%5)*2;py=y+1.5+(k//5)*1.65
        a=anchor('SacredFlame_'+name,(px,py,.50))
        for o in [box('Rock_Fissure',(px,py,.28),(1.2,.65,.56),rock,.12),
                  sphere('SacredFlame_'+name+'_Blue',(px,py-.15,.61),(.07,.055,.19),blue),
                  sphere('SacredFlame_'+name+'_Tip',(px,py-.15,.78),(.028,.026,.11),tip)]:keep_parent(o,a)
    for px,py,n in [(9,8,'Gorakh_Dibbi'),(10,-5,'Shaiya_Bhawan')]:
        create_garbhagriha(n,(px,py,0),width=4.5,depth=4.5,wall_height=2.6,mat=white,door_width=1.8,door_height=2.3)
        box(n+'_Roof',(px,py,2.7),(5,5,.25),white)
        dome(n+'_Dome',(px,py,2.85),1.4,1.5,white)
        anchor(n+'_Reference',(px,py,.5))
    # Akbar's chhatra is an associated object, not another deity statue.
    a=anchor('Akbar_Chhatra_Reference',(0,-4,.12))
    keep_parent(cylinder('Chhatra_Reference_Canopy',(0,-4,.10),1.2,.09,dark),a)
    for px in [-17,17]:
        cylinder('Flagpole',(px,-10,4.5),.055,9,gold)
        box('Flag',(px+.55,-10,8.35),(1.1,.025,.65),red)
    anchor('Spawn_Point',(0,-14,.05))
    finish('jwalamukhi_vaishnavi')
