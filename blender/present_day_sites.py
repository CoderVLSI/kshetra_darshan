"""Geometry shared by reference-led studies of previously missing destinations.

These are present-condition architectural blockouts, not measured replicas.
No photographed inscriptions, unknown idols or lost roofs are invented.
Sources and specific limits ship in each site's reference_notes entry.
"""
from pathlib import Path
import bpy

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


def linga(name, p, height, mat):
    x,y,z=p
    a=anchor(name,p)
    for o in [cylinder(name+'_Yoni',(x,y,z+.16),height*.40,.32,mat),
              box(name+'_Spout',(x+.45*height,y,z+.22),(height*.9,height*.23,.18),mat,.04),
              cylinder(name+'_Shaft',(x,y,z+height*.50),height*.21,height*.70,mat),
              sphere(name+'_Crown',(x,y,z+height*.85),(height*.21,height*.21,height*.19),mat)]:
        keep_parent(o,a)
    return a


def finish(site):
    target=ROOT/'godot/assets/models'/f'{site}_kshetra_full.glb'
    bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',export_apply=True,export_yup=True,export_cameras=False,export_lights=False)
    print('PRESENT_DAY_STUDY',site)
