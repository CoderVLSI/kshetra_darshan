"""Exportable, deterministic stone detail and metre-scaled planar UVs.

These are authored game materials, not photographic evidence of a temple.
No Blender-only procedural shader nodes are required at runtime.
"""
from pathlib import Path
import hashlib
import math
import bpy
import numpy as np


def add_stone_detail(mat, bsdf, color):
    mat['kshetra_surface'] = True
    name = mat.name.lower()
    paving = any(tag in name for tag in ('paving', 'floor', 'courtyard'))
    signature = repr((tuple(color), paving)).encode()
    key = hashlib.sha256(signature).hexdigest()[:12]
    directory = Path(__file__).resolve().parent.parent / 'godot/assets/textures/stone'
    directory.mkdir(parents=True, exist_ok=True)
    albedo_path = directory / f'{key}_albedo.png'
    normal_path = directory / f'{key}_normal.png'
    n = 256
    yy, xx = np.mgrid[:n, :n] / n
    rng = np.random.default_rng(112)
    height = np.zeros((n, n))
    # Integer frequencies keep both texture axes periodic.
    for frequency, amplitude in [(1, .12), (3, .09), (9, .06), (27, .025), (63, .012)]:
        phase = rng.uniform(0, 2 * math.pi, 2)
        height += amplitude * np.sin(xx * frequency * 2 * math.pi + phase[0]) * np.cos(yy * frequency * 2 * math.pi + phase[1])
    grain = rng.uniform(-.035, .035, (n, n))
    shade = 1 + height * .35 + grain
    if paving:
        # 2m repeat: four rows of .5m slabs, staggered 1m joints.
        row = np.floor(yy * 4).astype(int)
        x_joint = np.mod(xx * 2 + .5 * (row % 2), 1)
        y_joint = np.mod(yy * 4, 1)
        joint = (x_joint < .006) | (y_joint < .012)
        shade[joint] *= .58
        height[joint] -= .10
    # Blender stores pixel channels in linear space; PNG export handles sRGB.
    rgba = np.ones((n, n, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(np.asarray(color[:3])[None, None, :] * shade[:, :, None], 0, 1)
    dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 2
    dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 2
    normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    normal_rgba = np.ones_like(rgba)
    normal_rgba[:, :, :3] = normal * .5 + .5
    for path, pixels, colorspace in [(albedo_path, rgba, 'sRGB'), (normal_path, normal_rgba, 'Non-Color')]:
        if not path.exists():
            img = bpy.data.images.new(path.stem, width=n, height=n)
            img.colorspace_settings.name = colorspace
            img.pixels.foreach_set(pixels.ravel())
            img.filepath_raw = str(path)
            img.file_format = 'PNG'
            img.save()
            bpy.data.images.remove(img)
    tree = mat.node_tree
    albedo = tree.nodes.new('ShaderNodeTexImage')
    albedo.image = bpy.data.images.load(str(albedo_path), check_existing=True)
    albedo.extension = 'REPEAT'
    tree.links.new(albedo.outputs['Color'], bsdf.inputs['Base Color'])
    tex_normal = tree.nodes.new('ShaderNodeTexImage')
    tex_normal.image = bpy.data.images.load(str(normal_path), check_existing=True)
    tex_normal.image.colorspace_settings.name = 'Non-Color'
    tex_normal.extension = 'REPEAT'
    normal_node = tree.nodes.new('ShaderNodeNormalMap')
    normal_node.inputs['Strength'].default_value = .32
    tree.links.new(tex_normal.outputs['Color'], normal_node.inputs['Color'])
    tree.links.new(normal_node.outputs['Normal'], bsdf.inputs['Normal'])


def prepare_scene():
    """Planar projection per stone face; preserves non-stone deity/cloth UVs."""
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not any(m and m.get('kshetra_surface') for m in obj.data.materials):
            continue
        mesh = obj.data
        uv = mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        for poly in mesh.polygons:
            if poly.material_index >= len(mesh.materials):
                continue
            material = mesh.materials[poly.material_index]
            if not material or not material.get('kshetra_surface'):
                continue
            normal = normal_matrix @ poly.normal
            axis = max(range(3), key=lambda i: abs(normal[i]))
            axes = ((1, 2), (0, 2), (0, 1))[axis]
            for li in poly.loop_indices:
                point = obj.matrix_world @ mesh.vertices[mesh.loops[li].vertex_index].co
                uv.data[li].uv = (point[axes[0]] * .5, point[axes[1]] * .5)
        # Small edge bevel catches sunlight without changing the silhouette.
        if len(mesh.polygons) <= 24 and min(obj.dimensions) > .08 and max(obj.dimensions) < 60:
            bevel = obj.modifiers.new('Stone edge wear', 'BEVEL')
            bevel.width = min(.018, min(obj.dimensions) * .06)
            bevel.segments = 2
            bevel.limit_method = 'ANGLE'
