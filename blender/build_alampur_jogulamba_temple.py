"""
Build Script for Alampur Jogulamba Temple
Shakti Peetha: Alampur, Telangana (Upper teeth of Sati)
Architecture: Chalukyan Rekhanagara, Tungabhadra River ghat, Navabrahma Courtyard (9 mini shrines)
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


def create_chalukya_mini_shrine(name, location, size=(1.8, 1.8, 2.4), mat_sandstone=None, mat_gold=None):
    """Creates a miniature Chalukyan Rekhanagara shrine for the Navabrahma group."""
    parts = []
    hw, hd = size[0] / 2, size[1] / 2
    h = size[2]

    # Plinth
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.12))
    plinth = bpy.context.active_object
    plinth.scale = (hw, hd, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    if mat_sandstone: plinth.data.materials.append(mat_sandstone)
    parts.append(plinth)

    # Sanctum cube
    cube_h = 1.0
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(location[0], location[1], location[2] + 0.24 + cube_h / 2)
    )
    cube = bpy.context.active_object
    cube.scale = (hw * 0.9, hd * 0.9, cube_h / 2)
    bpy.ops.object.transform_apply(scale=True)
    if mat_sandstone: cube.data.materials.append(mat_sandstone)
    parts.append(cube)

    # Rekhanagara ribbed curvilinear tower
    tiers = 4
    for i in range(tiers):
        t = i / tiers
        tw = (hw * 0.85) * (1.0 - t * 0.45)
        th = 0.22
        tz = location[2] + 0.24 + cube_h + i * th + th / 2
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=tw, depth=th,
            location=(location[0], location[1], tz)
        )
        tier = bpy.context.active_object
        if mat_sandstone: tier.data.materials.append(mat_sandstone)
        parts.append(tier)

    # Amalaka & Kalasha
    shikhara_top = location[2] + 0.24 + cube_h + tiers * 0.22
    bpy.ops.mesh.primitive_torus_add(
        major_radius=hw * 0.35, minor_radius=0.06,
        location=(location[0], location[1], shikhara_top + 0.06)
    )
    amalaka = bpy.context.active_object
    if mat_sandstone: amalaka.data.materials.append(mat_sandstone)
    parts.append(amalaka)

    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.08, location=(location[0], location[1], shikhara_top + 0.18)
    )
    kalasha = bpy.context.active_object
    if mat_gold: kalasha.data.materials.append(mat_gold)
    parts.append(kalasha)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = plinth
    bpy.ops.object.join()
    plinth.name = name
    return plinth


def create_sub_shrine(name, location, size=(2.2, 2.2, 2.6), mat_stone=None, mat_deity=None, mat_gold=None):
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

    # Rekhanagara Shikhara
    tiers = 3
    shikhara_objs = []
    for i in range(tiers):
        t = i / tiers
        tw = (hw * 0.8) * (1.0 - t * 0.45)
        th = 0.18
        tz = location[2] + 0.3 + p_height + 0.16 + i * th + th / 2
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=tw, depth=th, location=(location[0], location[1], tz))
        tier = bpy.context.active_object
        if mat_stone: tier.data.materials.append(mat_stone)
        shikhara_objs.append(tier)

    # Kalasha
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.1,
        location=(location[0], location[1], location[2] + 0.3 + p_height + 0.16 + tiers * 0.18 + 0.1)
    )
    kalasha = bpy.context.active_object
    if mat_gold: kalasha.data.materials.append(mat_gold)

    # Deity Murti inside
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.2, depth=0.45,
        location=(location[0], location[1], location[2] + 0.3 + 0.25)
    )
    murti = bpy.context.active_object
    if mat_deity: murti.data.materials.append(mat_deity)

    # Join
    all_parts = [plinth] + pillars + [roof] + shikhara_objs + [kalasha, murti]
    bpy.ops.object.select_all(action='DESELECT')
    for part in all_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = plinth
    bpy.ops.object.join()
    plinth.name = name
    return plinth


def create_jogulamba_deity(name, location, mat_body, mat_gold, mat_silk):
    """Create 4-armed Jogulamba Devi murti (seated with Trishula, sword, kapala, damaru)."""
    parts = []

    # Pedestal (Linga/Corpse seat)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.1))
    seat = bpy.context.active_object
    seat.scale = (0.42, 0.28, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: seat.data.materials.append(mat_body)
    parts.append(seat)

    # Lower body / silk garment
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.24, depth=0.45,
                                        location=(location[0], location[1], location[2] + 0.38))
    lower = bpy.context.active_object
    if mat_silk: lower.data.materials.append(mat_silk)
    parts.append(lower)

    # Torso
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.8))
    torso = bpy.context.active_object
    torso.scale = (0.22, 0.14, 0.26)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: torso.data.materials.append(mat_body)
    parts.append(torso)

    # Head (Ugra / Fierce Yogini Swaroop with third eye)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(location[0], location[1], location[2] + 1.1))
    head = bpy.context.active_object
    if mat_body: head.data.materials.append(mat_body)
    parts.append(head)

    # Jata-mukuta (high ascetic matted hair crown)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=0.04, depth=0.32,
                                    location=(location[0], location[1], location[2] + 1.34))
    crown = bpy.context.active_object
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)

    # 4 Arms:
    # Upper Right: Trishula (Trident)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35,
                                        location=(location[0] + 0.28, location[1], location[2] + 0.9))
    ar1 = bpy.context.active_object
    ar1.rotation_euler = (0, 0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: ar1.data.materials.append(mat_body)
    parts.append(ar1)

    # Upper Left: Damaru
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35,
                                        location=(location[0] - 0.28, location[1], location[2] + 0.9))
    al1 = bpy.context.active_object
    al1.rotation_euler = (0, -0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: al1.data.materials.append(mat_body)
    parts.append(al1)

    # Lower Right: Khadga (Sword)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.32,
                                        location=(location[0] + 0.22, location[1] - 0.08, location[2] + 0.68))
    ar2 = bpy.context.active_object
    ar2.rotation_euler = (0.4, 0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: ar2.data.materials.append(mat_body)
    parts.append(ar2)

    # Lower Left: Kapala (Skull cup)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.32,
                                        location=(location[0] - 0.22, location[1] - 0.08, location[2] + 0.68))
    al2 = bpy.context.active_object
    al2.rotation_euler = (0.4, -0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: al2.data.materials.append(mat_body)
    parts.append(al2)

    # Golden Prabhavali arch
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.04,
                                     location=(location[0], location[1] + 0.06, location[2] + 0.98))
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: prabha.data.materials.append(mat_gold)
    parts.append(prabha)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = seat
    bpy.ops.object.join()
    seat.name = name
    return seat


def build_alampur_jogulamba():
    clear_scene()

    # Materials
    mat_sandstone = create_sandstone("Chalukyan_Red_Sandstone", color=(0.74, 0.52, 0.35, 1.0), roughness=0.88)
    mat_dark_stone = create_black_stone("Chalukya_Dark_Basalt", color=(0.14, 0.12, 0.10, 1.0), roughness=0.6)
    mat_gold = create_gold_metal("Temple_Gold")
    mat_brass = create_brass_metal("Temple_Brass")
    mat_flame = create_flame_emission("Deepam_Flame")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_water = create_water("Tungabhadra_River_Water")
    mat_silk = create_kumkum_red("Jogulamba_Red_Silk")

    # 1. Ground Plane (Ground Z=0)
    ground = create_ground_plane("Ground_Main", size=68.0, mat=mat_sandstone)

    # 2. Raised Chalukyan Jagati Platform for Main Temple
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 4.0, 0.3))
    plinth = bpy.context.active_object
    plinth.scale = (4.0, 4.0, 0.3)
    plinth.name = "Chalukyan_Jagati"
    bpy.ops.object.transform_apply(scale=True)
    if mat_sandstone: plinth.data.materials.append(mat_sandstone)

    # 3. Garbhagriha
    gb_parts = create_garbhagriha(
        name="Garbhagriha_Structure",
        location=(0, 4.0, 0.6),
        width=4.6, depth=4.6,
        wall_height=4.0, wall_thickness=0.45,
        mat=mat_sandstone,
        door_width=1.6, door_height=2.6
    )
    bpy.ops.object.select_all(action='DESELECT')
    for p in gb_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = gb_parts[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # Chalukyan Rekhanagara Shikhara atop Garbhagriha
    shikhara_objs = create_shikhara(
        name="Chalukyan_Rekhanagara_Shikhara",
        location=(0, 4.0, 4.6),
        base_width=4.4, height=8.2,
        tiers=6, mat=mat_sandstone, style="nagara"
    )
    for so in shikhara_objs:
        if "Kalasha" in so.name:
            so.data.materials.clear()
            so.data.materials.append(mat_gold)

    # 4. Deity: Deity_Jogulamba (4-armed fierce Devi)
    deity = create_jogulamba_deity(
        name="Deity_Jogulamba",
        location=(0, 4.8, 0.62),
        mat_body=mat_dark_stone,
        mat_gold=mat_gold,
        mat_silk=mat_silk
    )

    # 5. Mandapa: Chalukyan Mukhamandapa with carved pillars
    mandapa_parts = create_mandapa(
        name="Mandapa_Part",
        location=(0, -1.0, 0.0),
        width=8.0, depth=6.0, height=3.6,
        pillar_count_x=4, pillar_count_y=3,
        mat_stone=mat_sandstone, mat_floor=mat_sandstone,
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
        location=(-1.1, 1.8, 0.6),
        mat_brass=mat_brass, mat_flame=mat_flame
    )
    deepam_2 = create_deepam(
        name="Deepam_2",
        location=(1.1, 1.8, 0.6),
        mat_brass=mat_brass, mat_flame=mat_flame
    )

    # 8. Priest
    priest = create_human_figure(
        name="Priest",
        location=(1.3, 2.5, 0.6),
        height=1.7,
        mat_skin=mat_skin, mat_cloth=mat_dhoti
    )

    # 9. Sub-shrines: Bhairava_Shrine and Ganesha_Shrine
    bhairava_shrine = create_sub_shrine(
        name="Bhairava_Shrine",
        location=(9.0, 1.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_sandstone, mat_deity=mat_dark_stone, mat_gold=mat_gold
    )

    ganesha_shrine = create_sub_shrine(
        name="Ganesha_Shrine",
        location=(-9.0, 1.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_sandstone, mat_deity=mat_sandstone, mat_gold=mat_gold
    )

    # 10. Navabrahma Courtyard: 9 Miniature Chalukyan Shrines
    # Arranged neatly around the perimeter courtyard (outside walking corridors)
    navabrahma_names = [
        "Taraka_Brahma", "Swarga_Brahma", "Padma_Brahma",
        "Bala_Brahma", "Garuda_Brahma", "Kumara_Brahma",
        "Arka_Brahma", "Vira_Brahma", "Vishwa_Brahma"
    ]
    navabrahma_locs = [
        (-12.0, 7.0, 0.0), (-12.0, 2.0, 0.0), (-12.0, -3.0, 0.0),
        (12.0, 7.0, 0.0), (12.0, 2.0, 0.0), (12.0, -3.0, 0.0),
        (-6.0, 9.5, 0.0), (0.0, 9.5, 0.0), (6.0, 9.5, 0.0)
    ]
    for idx, (b_name, b_loc) in enumerate(zip(navabrahma_names, navabrahma_locs)):
        create_chalukya_mini_shrine(
            name=f"Navabrahma_{b_name}",
            location=b_loc,
            size=(1.8, 1.8, 2.5),
            mat_sandstone=mat_sandstone,
            mat_gold=mat_gold
        )

    # 11. Tungabhadra River & Ghat Steps along the Western edge
    # River plane
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-18.0, 0.0, -0.2))
    river = bpy.context.active_object
    river.scale = (4.0, 22.0, 1.0)
    river.name = "Tungabhadra_River"
    bpy.ops.object.transform_apply(scale=True)
    if mat_water: river.data.materials.append(mat_water)

    # Ghat steps descending to river
    for step_i in range(4):
        bpy.ops.mesh.primitive_cube_add(
            size=2, location=(-14.5 - step_i * 0.4, 0.0, 0.15 - step_i * 0.1)
        )
        ghat_step = bpy.context.active_object
        ghat_step.scale = (0.2, 16.0, 0.06)
        ghat_step.name = f"Tungabhadra_Ghat_Step_{step_i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_sandstone: ghat_step.data.materials.append(mat_sandstone)

    # 12. Prakara Enclosure Wall with South Gateway
    prakara_objs = create_prakara_wall(
        name="Alampur_Prakara",
        center=(0, 0.0, 0.0),
        width=36.0, depth=30.0,
        wall_height=3.2, wall_thickness=0.55,
        mat=mat_sandstone, gate_width=4.0, gate_sides=["S"]
    )

    # 13. Spawn_Point
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0, -12.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "alampur_jogulamba_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Alampur Jogulamba build complete!")


if __name__ == "__main__":
    build_alampur_jogulamba()
