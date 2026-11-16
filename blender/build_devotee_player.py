"""Articulated pilgrim: Blender +Y is forward, exported as Godot -Z.
Neutral arms are at the sides. Runtime controller blends the arm joints into prayer.
"""
from pathlib import Path
import sys, math
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_materials as mats


def empty(name, location=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    return obj


def finish(obj, name, mat, parent=None):
    obj.name = name
    if mat: obj.data.materials.append(mat)
    for poly in obj.data.polygons: poly.use_smooth = True
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def sphere(name, loc, size, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=1, location=loc)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, parent)


def cylinder(name, loc, radius, depth, mat, parent=None, radius2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=radius, radius2=radius if radius2 is None else radius2,
                                  depth=depth, location=loc)
    return finish(bpy.context.object, name, mat, parent)


def cloth(name, loc, size, mat, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new('Soft cloth edges', 'BEVEL')
    bevel.width = min(size) * .65
    bevel.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return finish(obj, name, mat, parent)


def tube(name, points, radius, mat, parent=None):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for point, pos in zip(spline.points, points): point.co = (*pos, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def loft(name, rings, mat, parent=None):
    vertices, faces = [], []
    n = 32
    for z, rx, ry in rings:
        for i in range(n):
            a = 2*math.pi*i/n
            vertices.append((rx*math.cos(a), ry*math.sin(a), z))
    for j in range(len(rings)-1):
        for i in range(n): faces.append((j*n+i, j*n+(i+1)%n, (j+1)*n+(i+1)%n, (j+1)*n+i))
    faces.extend([tuple(reversed(range(n))), tuple((len(rings)-1)*n+i for i in range(n))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat, parent)


def create_devotee():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    skin = mats.create_skin('Devotee_Skin', color=(.40, .23, .14, 1))
    cotton = mats.create_white_dhoti('Dhoti_Cotton', color=(.84, .80, .69, 1))
    gold = mats.create_brass_metal('Woven_Zari', color=(.46, .29, .07, 1))
    saffron = mats.create_red_silk('Angavastram', color=(.70, .16, .025, 1))
    hair = mats.create_black_stone('Hair', color=(.018, .013, .010, 1))
    white = mats.create_white_marble('Chandan', color=(.80, .72, .50, 1))
    red = mats.create_kumkum_red('Kumkum')
    root = empty('Devotee_Character')
    loft('Torso', [(1.00,.155,.103),(1.08,.16,.11),(1.18,.175,.12),(1.32,.21,.135),(1.40,.22,.12),(1.44,.15,.10)], skin, root)
    cylinder('Neck', (0,0,1.47), .058,.15,skin,root)
    sphere('Head',(0,.005,1.64),(.105,.105,.14),skin,root)
    sphere('Nose',(0,.105,1.635),(.023,.035,.030),skin,root)
    for s in [-1,1]:
        sphere('Ear',(s*.105,0,1.64),(.020,.023,.041),skin,root)
        sphere('Eye',(s*.039,.097,1.666),(.017,.008,.006),hair,root)
    tube('Mouth',[(-.026,.101,1.595),(0,.108,1.591),(.026,.101,1.595)],.0035,hair,root)
    sphere('HairCap',(0,-.016,1.705),(.103,.094,.075),hair,root)
    sphere('Shikha',(0,-.10,1.71),(.030,.035,.035),hair,root)
    for z in [1.701,1.712,1.723]:
        cloth('Chandan',(0,.088,z),(.030,.003,.003),white,root)
    sphere('Bindi',(0,.097,1.711),(.005,.004,.006),red,root)
    # Closed lofts prevent the open holes in the previous model's torso and dhoti.
    loft('DhotiWaist',[(.81,.22,.145),(.94,.205,.14),(1.05,.165,.112)],cotton,root)
    cylinder('WaistZari',(0,0,1.022),.171,.025,gold,root).scale.y=.70
    for x in [-.060,-.030,0,.030,.060]:
        cloth('FrontPleat',(x,.133,.80),(.016,.012,.23),cotton,root)
    cloth('PleatBorder',(0,.150,.585),(.077,.009,.012),gold,root)
    cloth('ShoulderShawl',(-.167,0,1.385),(.060,.145,.060),saffron,root)
    cloth('ShawlFront',(-.166,.13,1.18),(.055,.014,.21),saffron,root)
    cloth('ShawlBack',(-.166,-.12,1.16),(.055,.014,.23),saffron,root)
    tube('SacredThread',[(-.16,.10,1.42),(-.10,.137,1.32),(0,.135,1.20),(.12,.102,1.06)],.0045,white,root)
    for side,s in [('L',-1),('R',1)]:
        # Independent upper arm and forearm nodes are driven by endpoint IK in Godot.
        sh = (s*.235,0,1.40)
        sphere('Shoulder_'+side,sh,(.066,.065,.066),skin,root)
        upper = empty('UpperArm_'+side,sh,root)
        cylinder('UpperArmMesh_'+side,(sh[0],0,1.26),.040,.28,skin,upper,radius2=.053)
        elbow = (s*.235,0,1.12)
        fore = empty('Forearm_'+side,elbow,root)
        sphere('ElbowMesh_'+side,elbow,(.041,.041,.041),skin,fore)
        cylinder('ForearmMesh_'+side,(elbow[0],0,.985),.027,.27,skin,fore,radius2=.039)
        wrist=(s*.235,0,.85)
        hand=empty('Hand_'+side,wrist,root)
        # Hand geometry points up in bind coordinates. Neutral pose flips it down.
        sphere('Palm_'+side,(wrist[0],0,.895),(.018,.037,.052),skin,hand)
        for f in range(4):
            yy=-.027+f*.017
            cylinder('Finger_'+side+str(f),(wrist[0],yy,.958),.007,.070-(abs(f-1)*.008),skin,hand)
            sphere('FingerTip_'+side+str(f),(wrist[0],yy,.990-abs(f-1)*.004),(.007,.007,.010),skin,hand)
        sphere('Thumb_'+side,(wrist[0]+s*.010,.041,.910),(.010,.015,.028),skin,hand)
        # Leg pivots include the draped cloth, feet and lower legs.
        hip=(s*.105,0,.88)
        leg=empty('Leg_'+side,hip,root)
        cylinder('DhotiLeg_'+side,(hip[0],0,.665),.095,.43,cotton,leg,radius2=.112).scale.y=1.10
        cylinder('Hem_'+side,(hip[0],0,.455),.097,.022,gold,leg).scale.y=1.10
        sphere('Knee_'+side,(hip[0],0,.45),(.053,.055,.058),skin,leg)
        calf = loft('Calf_'+side,[(.065,.035,.036),(.20,.049,.046),(.34,.052,.049),(.45,.045,.045)],skin)
        calf.parent = leg
        calf.location = (0, 0, -.88)
        sphere('Foot_'+side,(hip[0],.064,.046),(.051,.125,.045),skin,leg)
        for f in range(5):
            sphere('Toe_'+side+str(f),(hip[0]+(-.033+f*.016)*s,.176-abs(f-1)*.006,.032),(.010,.023,.018),skin,leg)
    # Set the neutral hand bind orientation only after parenting geometry.
    for side in ['L','R']:
        bpy.data.objects['Hand_'+side].rotation_euler.x=math.pi
    bpy.context.view_layer.update()
    out=Path(__file__).resolve().parent.parent/'godot/assets/models/devotee_player.glb'
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_apply=True,export_yup=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
    print('Articulated devotee exported',out)

if __name__=='__main__':create_devotee()
