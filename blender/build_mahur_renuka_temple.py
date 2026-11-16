"""
Build Script for Mahur Renuka Temple
Shakti Peetha: Mahur / Mahurgad, Maharashtra (Upper lip of Sati)
Architecture: Hilltop stone sanctum, Parashurama shrine, Matru Tirtha, Renuka Mata face/head sacred form
"""
import sys
import os
import math
import bpy
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from common_materials import (
    create_sandstone, create_black_stone, create_gold_metal, create_brass_metal,
    create_flame_emission, create_skin, create_white_dhoti,
    create_water, create_kumkum_red, create_flower_garland
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_shikhara, create_deepam, create_hanging_bell, create_kunda,
    create_human_figure, create_ground_plane, create_mandapa,
    create_prakara_wall, export_glb
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


def create_sub_shrine(name, location, size=(2.2, 2.2, 2.6), mat_stone=None, mat_deity=None, mat_gold=None, deity_symbol="shrine"):
    """Creates a sub-shrine joined into a single mesh object."""
    hw, hd = size[0] / 2, size[1] / 2
    h = size[2]

    # Plinth
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.15))
    plinth = bpy.context.active_object
    plinth.scale = (hw, hd, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: plinth.data.materials.append(mat_stone)

    # 4 Corner Pillars
    pillars = []
    p_radius = 0.08
    p_height = h - 0.7
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            px = location[0] + sx * (hw - 0.2)
            py = location[1] + sy * (hd - 0.2)
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=8, radius=p_radius, depth=p_height,
                location=(px, py, location[2] + 0.3 + p_height / 2)
            )
            p = bpy.context.active_object
            if mat_stone: p.data.materials.append(mat_stone)
            pillars.append(p)

    # Roof slab
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(location[0], location[1], location[2] + 0.3 + p_height + 0.08)
    )
    roof = bpy.context.active_object
    roof.scale = (hw + 0.1, hd + 0.1, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: roof.data.materials.append(mat_stone)

    # Stepped shikhara
    tiers = 3
    shikhara_objs = []
    for i in range(tiers):
        t = i / tiers
        tw = (hw * 0.8) * (1.0 - t * 0.5)
        th = 0.15
        tz = location[2] + 0.3 + p_height + 0.16 + i * th + th / 2
        bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], tz))
        tier = bpy.context.active_object
        tier.scale = (tw, tw, th / 2)
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: tier.data.materials.append(mat_stone)
        shikhara_objs.append(tier)

    # Kalasha
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.1,
        location=(location[0], location[1], location[2] + 0.3 + p_height + 0.16 + tiers * 0.15 + 0.1)
    )
    kalasha = bpy.context.active_object
    if mat_gold: kalasha.data.materials.append(mat_gold)

    # Deity Murti inside
    murti_objs = []
    if deity_symbol == "parashurama":
        # Parashurama standing with axe (parashu)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=0.18, depth=0.55,
            location=(location[0], location[1], location[2] + 0.3 + 0.28)
        )
        p_body = bpy.context.active_object
        if mat_deity: p_body.data.materials.append(mat_deity)
        murti_objs.append(p_body)

        # Axe shaft & blade
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.02, depth=0.6,
            location=(location[0] + 0.16, location[1], location[2] + 0.3 + 0.32)
        )
        axe_shaft = bpy.context.active_object
        if mat_stone: axe_shaft.data.materials.append(mat_stone)
        murti_objs.append(axe_shaft)

        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=(location[0] + 0.16, location[1], location[2] + 0.3 + 0.55)
        )
        blade = bpy.context.active_object
        blade.scale = (0.12, 0.02, 0.08)
        bpy.ops.object.transform_apply(scale=True)
        if mat_gold: blade.data.materials.append(mat_gold)
        murti_objs.append(blade)
    else:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.2, depth=0.45,
            location=(location[0], location[1], location[2] + 0.3 + 0.25)
        )
        murti = bpy.context.active_object
        if mat_deity: murti.data.materials.append(mat_deity)
        murti_objs.append(murti)

    # Join
    all_parts = [plinth] + pillars + [roof] + shikhara_objs + [kalasha] + murti_objs
    bpy.ops.object.select_all(action='DESELECT')
    for part in all_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = plinth
    bpy.ops.object.join()
    plinth.name = name
    return plinth


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
    mat_water = create_water("Matru_Tirtha_Water")
    mat_sindoor = create_kumkum_red("Renuka_Sindoor", color=(0.92, 0.15, 0.06, 1.0))
    mat_garland = create_flower_garland("Marigold_Garland")

    # 1. Ground Plane (Ground Z=0)
    ground = create_ground_plane("Ground_Main", size=65.0, mat=mat_dark_sandstone)

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
        width=8.0, depth=6.0, height=3.6,
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

    # 9. Sub-shrines
    # Bhairava_Shrine (right side)
    bhairava_shrine = create_sub_shrine(
        name="Bhairava_Shrine",
        location=(9.0, 1.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_dark_sandstone, mat_deity=mat_hill_rock, mat_gold=mat_gold
    )

    # Ganesha_Shrine (left side)
    ganesha_shrine = create_sub_shrine(
        name="Ganesha_Shrine",
        location=(-9.0, 1.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_dark_sandstone, mat_deity=mat_sindoor, mat_gold=mat_gold
    )

    # Parashurama Shrine (prominent sub-shrine in Mahurgad)
    parashurama_shrine = create_sub_shrine(
        name="Parashurama_Shrine",
        location=(9.0, -5.0, 0.0),
        size=(2.6, 2.6, 3.2),
        mat_stone=mat_dark_sandstone, mat_deity=mat_dark_sandstone, mat_gold=mat_gold,
        deity_symbol="parashurama"
    )

    # 10. Matru Tirtha (Sacred Tank at Mahur)
    kunda_objs = create_kunda(
        name="Matru_Tirtha",
        location=(-11.0, -6.5, 0.0),
        size=(6.5, 6.5, 1.4),
        mat_stone=mat_dark_sandstone, mat_water=mat_water, steps=4
    )

    # 11. Prakara Wall with South Gateway
    prakara_objs = create_prakara_wall(
        name="Mahurgad_Prakara",
        center=(0, 0.0, 0.0),
        width=34.0, depth=28.0,
        wall_height=3.4, wall_thickness=0.55,
        mat=mat_dark_sandstone, gate_width=4.0, gate_sides=["S"]
    )

    # 12. Spawn_Point
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0, -11.5, 0.0)
    bpy.context.collection.objects.link(spawn)

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "mahur_renuka_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Mahur Renuka build complete!")


if __name__ == "__main__":
    build_mahur_renuka()
