"""Headless Blender regression checks for connected architecture dimensions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector
import common_geometry as g


def bounds(obj):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    return tuple(min(p[i] for p in points) for i in range(3)), tuple(max(p[i] for p in points) for i in range(3))


def close(a, b):
    assert abs(a - b) < 0.0001, (a, b)


g.clear_scene()
pillar = g.create_pillar(height=3.0, radius=.2)
lo, hi = bounds(pillar)
close(lo[2], 0)
close(hi[2], 3)
platform = g.create_platform(size=(10, 8, .6), steps=3)
lo, hi = bounds(platform)
for actual, expected in zip(hi, (5, 4, .6)): close(actual, expected)
steps = [bpy.data.objects[f"Platform_Step_{i}"] for i in range(1, 4)]
for first, second in zip(steps, steps[1:]): close(bounds(first)[1][1], bounds(second)[0][1])
close(bounds(steps[-1])[1][1], -4)
close(bounds(steps[-1])[1][2], .6)

walls = g.create_garbhagriha(width=5, depth=6, wall_height=4, door_width=1.6)
left = bpy.data.objects['Garbhagriha_Wall_Front_L']
right = bpy.data.objects['Garbhagriha_Wall_Front_R']
close(bounds(right)[0][0] - bounds(left)[1][0], 1.6)
close(bounds(left)[0][0], -2.5)
close(bounds(right)[1][0], 2.5)
g.create_mandapa(width=8, depth=6, height=3.5)
close(bounds(bpy.data.objects['Mandapa_Roof'])[0][2], 3.45)
close(bounds(bpy.data.objects['Mandapa_Pillar_0_0'])[1][2], 3.5)
g.create_prakara_wall(width=30, depth=25, gate_width=3)
close(bounds(bpy.data.objects['Prakara_S_R'])[0][0] - bounds(bpy.data.objects['Prakara_S_L'])[1][0], 3)
g.create_kunda(size=(10, 12, 1.8))
lo, hi = bounds(bpy.data.objects['Kunda_Water'])
close(hi[0] - lo[0], 9.4)
close(hi[1] - lo[1], 11.4)
g.create_gopuram()
lo, hi = bounds(bpy.data.objects['Gopuram_Gateway_Jamb_L'])
close(lo[2], 0)
close(hi[2], 3)
assert hi[0] < -1
print('GEOMETRY REGRESSION: PASS (pillar, platform, steps, sanctum doorway, hall, enclosure, tank, gateway)')
