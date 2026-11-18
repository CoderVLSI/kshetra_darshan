"""
Build Script for Mahur Renuka Temple
Shakti Peetha: Mahur / Mahurgad, Maharashtra (Upper lip of Sati)
Architecture: forested ridge, covered approaches, Renuka sanctum and Sabha Mandapa
"""
import sys
import os
import math
import random
import bpy
from mathutils import Matrix, Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from common_materials import (
    create_sandstone, create_black_stone, create_gold_metal, create_brass_metal,
    create_flame_emission, create_skin, create_white_dhoti,
    create_kumkum_red, create_flower_garland, create_white_marble,
    create_green_foliage, create_tree_bark
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_shikhara, create_deepam, create_hanging_bell,
    create_human_figure, create_mandapa, create_tree
)


def export_temple_glb(filepath, apply_modifiers=True):
    """Export scene as GLB compatible with Blender 5.3."""
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_apply=apply_modifiers,
        export_yup=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
    )
    print(f"Exported: {filepath}")


def create_renuka_deity(name, location, mat_sindoor, mat_gold, mat_garland):
    """Stylised Renuka face/head sacred form; no invented torso or arms.

    Reference: research/2026-11-16/deities.json, Mahur Renuka profile.
    This blockout is not a scan of the consecrated image.
    """
    x, y, z = location
    parts = []
    def sphere(label, pos, radius, scale, material):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=radius, location=pos)
        obj = bpy.context.active_object
        obj.name = label
        obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        if material: obj.data.materials.append(material)
        parts.append(obj)
        return obj

    # The broad vermilion face rests above the decorated altar cloth.
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.58, depth=0.16,
        location=(x, y, z + 0.08))
    base = bpy.context.active_object
    base.name = name + "_Altar"
    if mat_gold: base.data.materials.append(mat_gold)
    parts.append(base)
    sphere(name + "_SacredFace", (x, y, z + 0.72), 0.50, (1.0, 0.58, 1.08), mat_sindoor)
    dark = create_black_stone("Renuka_Eye_Detail", color=(0.018, 0.012, 0.01, 1))
    for sign in [-1, 1]:
        sphere(name + "_Eye", (x + sign * 0.17, y - 0.266, z + 0.82), 0.075,
            (1.0, 0.25, 0.53), mat_gold)
        sphere(name + "_Pupil", (x + sign * 0.17, y - 0.285, z + 0.82), 0.035,
            (0.8, 0.35, 1), dark)
        sphere(name + "_Earring", (x + sign * 0.47, y - 0.06, z + 0.58), 0.08,
            (0.75, 0.45, 1.3), mat_gold)
    sphere(name + "_Nose", (x, y - 0.285, z + 0.68), 0.08, (0.45, 0.8, 1.0), mat_sindoor)
    sphere(name + "_Bindi", (x, y - 0.27, z + 1.0), 0.04, (1, 0.3, 1), mat_gold)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.42, radius2=0.13, depth=0.34,
        location=(x, y, z + 1.35))
    crown = bpy.context.active_object
    crown.name = name + "_Crown"
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)
    # Garland frames the face and remains adornment, not a pair of arms.
    for i in range(17):
        angle = math.pi + i * math.pi / 16
        sphere(name + "_Garland", (x + math.cos(angle) * 0.58, y - 0.03,
            z + 0.64 + math.sin(angle) * 0.48), 0.065, (1, 1, 1), mat_garland)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts: obj.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = name
    return base


def marker(name, position):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    return obj


def build_ridge(soil, paving, foliage, bark):
    # The summit footprint follows the satellite roof edges and clearing.
    summit = [(-6,-16), (4,-16), (8,-9), (10,1), (9,13), (5.4,24),
              (-3.0,24), (-7,16), (-9.5,6), (-8.4,-5)]
    rings = [summit, [(x * 1.7, y * 1.13) for x, y in summit],
             [(x * 3.9, y * 1.48) for x, y in summit]]
    count = len(summit)
    vertices = [(x, y, z) for ring, z in zip(rings, [0,-6.0,-18.0]) for x,y in ring]
    faces = [tuple(range(count))]
    for ring in range(len(rings) - 1):
        for index in range(count):
            next_index = (index + 1) % count
            a = ring * count
            faces.append((a + index, a + count + index,
                          a + count + next_index, a + next_index))
    mesh = bpy.data.meshes.new("Mahur_Ridge_Contours")
    mesh.from_pydata(vertices, [], faces)
    terrain = bpy.data.objects.new("Mahur_Forested_Ridge", mesh)
    bpy.context.collection.objects.link(terrain)
    mesh.materials.append(soil)
    mesh.materials.append(paving)
    mesh.polygons[0].material_index = 1
    bpy.context.view_layer.update()

    # Sample the modelled slopes so trunks meet the rock surface.
    rng = random.Random(24)
    for index in range(84):
        side = -1 if index % 2 else 1
        x = side * rng.uniform(9.8, 29.5)
        y = rng.uniform(-26.5, 29.5)
        hit, contact, _, _ = terrain.ray_cast(Vector((x, y, 5)), Vector((0, 0, -1)))
        if hit:
            create_tree("Mahur_Canopy_" + str(index), contact,
                        height=rng.uniform(2.6, 5.4), mat_trunk=bark, mat_leaves=foliage)


def build_approach_slope(name, points, material):
    # Keep the stair flights seated against the hill, with the rock below
    # the tread surfaces and sloping away on both sides.
    offsets = [-9, -4, -1.95, 1.95, 4, 9]
    drops = [8.5, 2.9, .27, .27, 3.5, 9.2]
    vertices = [(x + dx, y, z - dz) for x,y,z in points for dx,dz in zip(offsets,drops)]
    width = len(offsets)
    faces = []
    for row in range(len(points) - 1):
        for col in range(width - 1):
            index = row * width + col
            faces.append((index,index+1,index+width+1,index+width))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    slope = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(slope)
    mesh.materials.append(material)


def build_covered_walk(name, start, end, steps, stone, roof):
    begin, finish = Vector(start), Vector(end)
    direction = finish - begin
    length = math.hypot(direction.x, direction.y)
    yaw = math.atan2(-direction.x, direction.y)
    side = Vector((math.cos(yaw), math.sin(yaw), 0))
    span = length / steps
    for index in range(steps):
        point = begin.lerp(finish, (index + .5) / steps)
        tread = create_platform(name + "_Tread", (0,0,0),
                                size=(3.4, span + .12, .42), mat=stone)
        tread.rotation_euler.z = yaw
        tread.location = (point.x, point.y, point.z - .42)
    for index in range(0, steps, 6):
        point = begin.lerp(finish, index / steps)
        for edge in [-1,1]:
            post = point + side * (1.48 * edge)
            create_pillar(name + "_Post", post, height=2.7, radius=.075, mat=stone)
        middle = begin.lerp(finish, min(index + 3, steps) / steps)
        panel = create_platform(name + "_Sheet_Roof", (0,0,0),
                                size=(3.8, min(6, steps - index) * span + .3, .10), mat=roof)
        panel.rotation_euler.x = math.atan2(direction.z, length)
        panel.rotation_euler.z = yaw
        panel.location = (middle.x, middle.y, middle.z + 2.75)


def build_shrine(name, position, width, stone):
    create_garbhagriha(name, position, width=width, depth=width, wall_height=2.8,
                       door_width=1.45, door_height=2.18, mat=stone)
    x,y,z = position
    create_platform(name + "_Roof", (x,y,z + 2.8), size=(width+.25,width+.25,.22), mat=stone)
    marker(name + "_Anchor", (x,y + width * .2,z + .6))


def build_attendant_study(name, position, hanuman=False):
    from deity_detail import Sculpture, palette

    study = Sculpture()
    colors = palette(study)
    stone = colors["orange"] if hanuman else colors["black"]
    trim = colors["gold"]
    study.ellipsoid((0,0,.12),(.46,.36,.12),colors["black"])
    for side in [-1,1]:
        study.tube([(side*.12,0,.28),(side*.13,.015,.55),(side*.14,0,.83)],.095,stone,12)
        study.ellipsoid((side*.13,-.075,.27),(.12,.17,.055),stone)
    study.ellipsoid((0,.005,.82),(.26,.16,.23),colors["red"])
    study.ellipsoid((0,0,1.09),(.27,.16,.29),stone)
    study.tube([(-.19,-.065,1.23),(0,-.157,1.02),(.19,-.065,1.23)],.026,trim,10)
    study.ellipsoid((0,-.025,1.49),(.144,.127,.18),stone)
    for side in [-1,1]:
        study.ellipsoid((side*.14,-.016,1.49),(.04,.045,.065),stone)
        study.ellipsoid((side*.06,-.131,1.526),(.039,.015,.014),colors["eye"])
        study.ellipsoid((side*.06,-.144,1.526),(.014,.012,.013),colors["black"])
    if hanuman:
        study.ellipsoid((0,-.133,1.434),(.14,.078,.071),stone)
        study.tube([(0,.1,.86),(.25,.16,.72),(.45,.14,.93),(.43,.12,1.28),(.36,.08,1.43)],.039,stone,12)
        study.ellipsoid((0,-.006,1.66),(.139,.12,.09),trim)
        study.tube([(-.21,0,1.25),(-.34,-.06,.96),(-.41,-.105,1.13)],.063,stone,12)
        study.tube([(.21,0,1.25),(.30,-.1,1.04),(.22,-.28,1.18)],.064,stone,12)
        study.tube([(-.42,-.105,.87),(-.42,-.105,1.61)],.035,trim,12)
        study.ellipsoid((-.42,-.105,1.70),(.13,.13,.155),trim,16,10)
    else:
        study.ellipsoid((0,-.096,1.41),(.103,.065,.10),stone)
        study.ellipsoid((0,.015,1.674),(.082,.086,.097),stone)
        study.tube([(-.21,0,1.24),(-.34,-.049,1.05),(-.44,-.092,1.17)],.062,stone,12)
        study.tube([(.21,0,1.23),(.32,-.024,1.03),(.24,-.19,.95)],.061,stone,12)
        study.tube([(-.48,-.09,.45),(-.43,-.09,1.2),(-.38,-.09,1.73)],.031,trim,10)
        study.ellipsoid((-.25,-.09,1.69),(.166,.038,.13),trim)
    return study.finish(name, position)


def build_mahur_renuka():
    clear_scene()

    # Materials
    mat_dark_sandstone = create_sandstone("Dark_Sandstone", color=(0.48, 0.38, 0.28, 1.0), roughness=0.9)
    mat_hill_rock = create_black_stone("Mahurgad_Basalt_Rock", color=(0.14, 0.13, 0.11, 1.0), roughness=0.85)
    mat_gold = create_gold_metal("Temple_Gold")
    mat_brass = create_brass_metal("Temple_Brass")
    mat_flame = create_flame_emission("Deepam_Flame")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_paving = create_sandstone("Mahur_Kota_Paving", color=(.45,.41,.34,1))
    mat_roof = create_sandstone("Mahur_Approach_Terracotta", color=(.46,.18,.12,1))
    mat_sheet = create_sandstone("Mahur_Ritual_Hall_Sheet", color=(.47,.44,.36,1))
    mat_silver = create_brass_metal("Mahur_Silver_Cladding", color=(.77,.78,.81,1))
    mat_marble = create_white_marble("Mahur_Hanuman_Marble")
    mat_soil = create_sandstone("Mahur_Wooded_Slope", color=(.24,.265,.17,1), roughness=.95)
    foliage = create_green_foliage("Mahur_Dry_Forest", color=(.11,.22,.065,1))
    bark = create_tree_bark("Mahur_Forest_Bark")
    mat_sindoor = create_kumkum_red("Renuka_Sindoor", color=(0.92, 0.15, 0.06, 1.0))
    mat_garland = create_flower_garland("Marigold_Garland")

    # The pavilion and sanctum stand on the summit, above the access stairs.
    build_ridge(mat_soil, mat_paving, foliage, bark)

    # 2. Hilltop Plateau / Stepped Terraced Plinth
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 3.5, 0.25))
    hill_plinth = bpy.context.active_object
    hill_plinth.scale = (4.0, 4.0, 0.25)
    hill_plinth.name = "Mahur_Hilltop_Platform"
    bpy.ops.object.transform_apply(scale=True)
    if mat_dark_sandstone: hill_plinth.data.materials.append(mat_dark_sandstone)

    # 3. Garbhagriha (Sanctum)
    gb_parts = create_garbhagriha(
        name="Garbhagriha_Structure",
        location=(0, 4.0, 0.5),
        width=4.4, depth=4.4,
        wall_height=4.0, wall_thickness=0.45,
        mat=mat_dark_sandstone,
        door_width=1.6, door_height=2.6
    )
    bpy.ops.object.select_all(action='DESELECT')
    for p in gb_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = gb_parts[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # Shikhara atop Garbhagriha
    shikhara_objs = create_shikhara(
        name="Mahur_Shikhara",
        location=(0, 4.0, 4.5),
        base_width=4.2, height=7.5,
        tiers=5, mat=mat_dark_sandstone, style="nagara"
    )
    for so in shikhara_objs:
        if "Kalasha" in so.name:
            so.data.materials.clear()
            so.data.materials.append(mat_gold)

    # 4. Deity: Deity_Renuka (face/head, sindoor vermilion swaroop)
    deity = create_renuka_deity(
        name="Deity_Renuka",
        location=(0, 4.8, 0.52),
        mat_sindoor=mat_sindoor,
        mat_gold=mat_gold,
        mat_garland=mat_garland
    )

    # 5. Mandapa: Hilltop stone pillared hall
    mandapa_parts = create_mandapa(
        name="Mandapa_Part",
        location=(0, -1.0, 0.0),
        width=7.6, depth=6.0, height=3.6,
        pillar_count_x=4, pillar_count_y=3,
        mat_stone=mat_dark_sandstone, mat_floor=mat_dark_sandstone,
        pillar_style="square"
    )
    bpy.ops.object.select_all(action='DESELECT')
    for p in mandapa_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_parts[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"

    # 6. Ghanta (Hanging Brass Bell in Mandapa corridor)
    ghanta = create_hanging_bell(
        name="Ghanta",
        location=(0, -1.0, 2.7),
        mat_brass=mat_brass, scale=1.1
    )

    # 7. Deepam_1 and Deepam_2
    deepam_1 = create_deepam(
        name="Deepam_1",
        location=(-1.1, 1.8, 0.5),
        mat_brass=mat_brass, mat_flame=mat_flame
    )
    deepam_2 = create_deepam(
        name="Deepam_2",
        location=(1.1, 1.8, 0.5),
        mat_brass=mat_brass, mat_flame=mat_flame
    )

    # 8. Priest
    priest = create_human_figure(
        name="Priest",
        location=(1.3, 2.5, 0.5),
        height=1.7,
        mat_skin=mat_skin, mat_cloth=mat_dhoti
    )

    # Nanded's district report describes a silver-clad sanctum entrance.
    for x in [-.88,.88]:
        create_platform("Renuka_Silver_Door_Jamb", (x,1.73,.5),
                        size=(.14,.09,2.65), mat=mat_silver)
    create_platform("Renuka_Silver_Door_Lintel", (0,1.73,3.12),
                    size=(1.85,.09,.18), mat=mat_silver)
    for j in range(3):
        create_platform("Renuka_Darshan_Tread", (0,.82 + j * .36,0),
                        size=(1.6,.42,(j+1) * .166), mat=mat_dark_sandstone)

    # The field survey distinguishes the main temple and the sheet-roofed
    # multipurpose hall. The latter stands across the open summit approach.
    create_mandapa("Mahur_Multipurpose_Hall", (-3.4,12.8,0),
                   width=6.3, depth=13.0, height=3.1, pillar_count_x=2,
                   pillar_count_y=5, mat_stone=mat_hill_rock, mat_floor=mat_paving)
    for edge in [-1,1]:
        panel = create_platform("Mahur_Multipurpose_Sheet_Roof", (0,0,0),
                                size=(3.6,13.8,.1), mat=mat_sheet)
        panel.rotation_euler.y = edge * .16
        panel.location = (-3.4 + edge * 1.7,12.8,3.47)

    # The northeast covered approach climbs to the terrace. A separate
    # covered flight continues southwest down to Parashurama.
    build_approach_slope("Mahur_North_Approach_Slope",
                         [(2.4,24,0), (4.3,30.6,-1.65), (6.2,37.2,-3.3),
                          (4.7,44.1,-5.55), (3.2,51,-7.8), (3.2,55,-8.25)], mat_soil)
    build_approach_slope("Mahur_South_Approach_Slope",
                         [(-2.9,-38,-4.65), (-2.9,-29.6,-4.35),
                          (-1.9,-21.9,-2.18), (-.9,-14.2,0)], mat_soil)
    build_covered_walk("Mahur_Upper_Approach_West", (2.4,24,0), (6.2,37.2,-3.3),
                       22, mat_dark_sandstone, mat_roof)
    build_covered_walk("Mahur_Upper_Approach_Bend", (6.2,37.2,-3.3), (3.2,51,-7.8),
                       27, mat_dark_sandstone, mat_roof)
    create_platform("Mahur_North_Arrival_Landing", (3.2,52,-8.35),
                    size=(5.1,4,.55), mat=mat_dark_sandstone)

    build_covered_walk("Parashurama_Descent", (-.9,-14.2,0), (-2.9,-29.6,-4.35),
                       27, mat_dark_sandstone, mat_roof)
    create_platform("Parashurama_Lower_Terrace", (-2.9,-33,-5.05),
                    size=(10.5,9.6,.7), mat=mat_hill_rock)
    build_shrine("Parashurama", (-2.9,-34.5,-4.35), 3.8, mat_dark_sandstone)
    build_shrine("Hanuman", (-4.9,-8.5,0), 3.25, mat_marble)
    build_attendant_study("Parashurama_Sculpture_Study", (-2.9,-33.92,-4.35))
    build_attendant_study("Hanuman_Sculpture_Study", (-4.9,-7.96,0), hanuman=True)

    # The district reports the main doorway's rebuilding in 1464. Keep the
    # historical record beside the entrance while letterforms are researched.
    marker("Renuka_Main_Door_Record", (1.65,-4.1,1.15))
    marker("Spawn_Point", (4.95,20.4,.1))

    # Run the north-south ridge approximately NNE–SSW as seen from above.
    bpy.context.view_layer.update()
    orient = Matrix.Rotation(math.radians(-27),4,'Z')
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world = orient @ obj.matrix_world

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "mahur_renuka_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Mahur Renuka build complete!")


if __name__ == "__main__":
    build_mahur_renuka()
