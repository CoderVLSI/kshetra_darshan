"""
Build Script for Srisailam Bhramaramba Temple
Shakti Peetha: Srisailam, Andhra Pradesh (Neck of Sati / Mallikarjuna Jyotirlinga Kshetra)
Architecture: Dravidian Vimana, Mallikarjuna Shiva Shrine with Nandi, Nallamala hill forest, large prakara
"""
import sys
import os
import math
import bpy
from mathutils import Matrix, Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from common_materials import (
    create_granite_stone, create_black_stone, create_gold_metal, create_brass_metal,
    create_flame_emission, create_skin, create_white_dhoti,
    create_water, create_kumkum_red, create_flower_garland,
    create_green_foliage, create_tree_bark
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_shikhara, create_deepam, create_hanging_bell, create_kunda,
    create_human_figure, create_ground_plane, create_mandapa,
    create_prakara_wall, create_nandi, create_tree, export_glb
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

    # Dravidian stepped vimana tiers
    tiers = 3
    shikhara_objs = []
    for i in range(tiers):
        t = i / tiers
        tw = (hw * 0.8) * (1.0 - t * 0.45)
        th = 0.16
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
        location=(location[0], location[1], location[2] + 0.3 + p_height + 0.16 + tiers * 0.16 + 0.1)
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


def create_mallikarjuna_shiva_shrine(name, location, mat_granite, mat_gold, mat_black_stone):
    """Creates the sacred Mallikarjuna Swamy Shiva shrine with lingam and Dravidian vimana."""
    parts = []
    # Base platform
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.25))
    base = bpy.context.active_object
    base.scale = (1.8, 1.8, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    if mat_granite: base.data.materials.append(mat_granite)
    parts.append(base)

    # Sanctum walls
    for pos, sc in [
        ((location[0], location[1] + 1.2, location[2] + 1.5), (1.5, 0.2, 1.0)),
        ((location[0] - 1.3, location[1], location[2] + 1.5), (0.2, 1.4, 1.0)),
        ((location[0] + 1.3, location[1], location[2] + 1.5), (0.2, 1.4, 1.0)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
        w = bpy.context.active_object
        w.scale = sc
        bpy.ops.object.transform_apply(scale=True)
        if mat_granite: w.data.materials.append(mat_granite)
        parts.append(w)

    # Vimana tower
    for ti in range(4):
        tw = 1.3 * (1.0 - ti * 0.2)
        tz = location[2] + 2.5 + ti * 0.4
        bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], tz + 0.2))
        v = bpy.context.active_object
        v.scale = (tw, tw, 0.2)
        bpy.ops.object.transform_apply(scale=True)
        if mat_granite: v.data.materials.append(mat_granite)
        parts.append(v)

    # Golden Kalasha atop Vimana
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.18, location=(location[0], location[1], location[2] + 4.25)
    )
    kal = bpy.context.active_object
    if mat_gold: kal.data.materials.append(mat_gold)
    parts.append(kal)

    # Shiva Lingam (Yoni base + Linga shaft)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.4, depth=0.18,
        location=(location[0], location[1], location[2] + 0.5 + 0.09)
    )
    yoni = bpy.context.active_object
    if mat_black_stone: yoni.data.materials.append(mat_black_stone)
    parts.append(yoni)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.16, depth=0.45,
        location=(location[0], location[1], location[2] + 0.5 + 0.35)
    )
    linga = bpy.context.active_object
    if mat_black_stone: linga.data.materials.append(mat_black_stone)
    parts.append(linga)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = name
    return base


def create_bhramaramba_deity(name, location, mat_body, mat_gold, mat_silk):
    """Create 4-armed Bhramaramba Devi murti (holding lotus blossoms, abhaya & varada mudras)."""
    parts = []

    # Ornate Lotus Pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.42, depth=0.15,
                                        location=(location[0], location[1], location[2] + 0.075))
    ped = bpy.context.active_object
    if mat_gold: ped.data.materials.append(mat_gold)
    parts.append(ped)

    # Saree lower body
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.5,
                                        location=(location[0], location[1], location[2] + 0.4))
    lower = bpy.context.active_object
    if mat_silk: lower.data.materials.append(mat_silk)
    parts.append(lower)

    # Torso
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.85))
    torso = bpy.context.active_object
    torso.scale = (0.22, 0.14, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: torso.data.materials.append(mat_body)
    parts.append(torso)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(location[0], location[1], location[2] + 1.15))
    head = bpy.context.active_object
    if mat_body: head.data.materials.append(mat_body)
    parts.append(head)

    # Golden Kiritam (Crown)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=0.03, depth=0.3,
                                    location=(location[0], location[1], location[2] + 1.38))
    crown = bpy.context.active_object
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)

    # 4 Arms:
    # Upper Right: Lotus
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35,
                                        location=(location[0] + 0.28, location[1], location[2] + 0.95))
    ar1 = bpy.context.active_object
    ar1.rotation_euler = (0, 0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: ar1.data.materials.append(mat_body)
    parts.append(ar1)

    # Upper Left: Lotus
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35,
                                        location=(location[0] - 0.28, location[1], location[2] + 0.95))
    al1 = bpy.context.active_object
    al1.rotation_euler = (0, -0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: al1.data.materials.append(mat_body)
    parts.append(al1)

    # Lower Right: Abhaya Mudra
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.32,
                                        location=(location[0] + 0.22, location[1] - 0.08, location[2] + 0.72))
    ar2 = bpy.context.active_object
    ar2.rotation_euler = (0.4, 0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: ar2.data.materials.append(mat_body)
    parts.append(ar2)

    # Lower Left: Varada Mudra
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.32,
                                        location=(location[0] - 0.22, location[1] - 0.08, location[2] + 0.72))
    al2 = bpy.context.active_object
    al2.rotation_euler = (0.4, -0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: al2.data.materials.append(mat_body)
    parts.append(al2)

    # Golden Prabhavali arch
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.04,
                                     location=(location[0], location[1] + 0.06, location[2] + 1.0))
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: prabha.data.materials.append(mat_gold)
    parts.append(prabha)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = ped
    bpy.ops.object.join()
    ped.name = name
    return ped


def build_srisailam_bhramaramba():
    clear_scene()

    # Materials
    mat_granite = create_granite_stone("Dravidian_Granite", color=(0.28, 0.26, 0.24, 1.0), roughness=0.85)
    mat_black_stone = create_black_stone("Srisailam_Linga_Basalt", color=(0.08, 0.08, 0.07, 1.0), roughness=0.4)
    mat_gold = create_gold_metal("Temple_Gold")
    mat_brass = create_brass_metal("Temple_Brass")
    mat_flame = create_flame_emission("Deepam_Flame")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_silk = create_kumkum_red("Bhramaramba_Silk")
    mat_leaves = create_green_foliage("Nallamala_Foliage")
    mat_bark = create_tree_bark("Nallamala_Bark")

    # 1. Ground Plane (Ground Z=0)
    ground = create_ground_plane("Ground_Main", size=68.0, mat=mat_granite)

    # 2. Raised Dravidian Jagati Plinth for Bhramaramba Sanctum
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 4.0, 0.3))
    plinth = bpy.context.active_object
    plinth.scale = (4.2, 4.2, 0.3)
    plinth.name = "Bhramaramba_Jagati"
    bpy.ops.object.transform_apply(scale=True)
    if mat_granite: plinth.data.materials.append(mat_granite)

    # 3. Garbhagriha
    gb_parts = create_garbhagriha(
        name="Garbhagriha_Structure",
        location=(0, 4.0, 0.6),
        width=4.6, depth=4.6,
        wall_height=4.0, wall_thickness=0.45,
        mat=mat_granite,
        door_width=1.6, door_height=2.6
    )
    bpy.ops.object.select_all(action='DESELECT')
    for p in gb_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = gb_parts[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # Dravidian Vimana Tower atop Garbhagriha
    shikhara_objs = create_shikhara(
        name="Srisailam_Vimana",
        location=(0, 4.0, 4.6),
        base_width=4.4, height=8.0,
        tiers=5, mat=mat_granite, style="dravidian"
    )
    for so in shikhara_objs:
        if "Kalasha" in so.name:
            so.data.materials.clear()
            so.data.materials.append(mat_gold)

    # 4. Deity: Deity_Bhramaramba (4-armed Goddess)
    deity = create_bhramaramba_deity(
        name="Deity_Bhramaramba",
        location=(0, 4.8, 0.62),
        mat_body=mat_black_stone,
        mat_gold=mat_gold,
        mat_silk=mat_silk
    )

    # 5. Mandapa: Dravidian Mukhamandapa with carved granite pillars
    mandapa_parts = create_mandapa(
        name="Mandapa_Part",
        location=(0, -1.0, 0.0),
        width=8.0, depth=6.0, height=3.6,
        pillar_count_x=4, pillar_count_y=3,
        mat_stone=mat_granite, mat_floor=mat_granite,
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

    # The Kurnool district census describes Bhramaramba west of Mallikarjuna.
    # Turn the entire sanctuary and approach together, facing the eastern gate.
    bpy.context.view_layer.update()
    sanctuary_transform = (
        Matrix.Translation((-9, 0, 0))
        @ Matrix.Rotation(math.pi / 2, 4, 'Z')
        @ Matrix.Translation((0, -4, 0))
    )
    for obj in list(bpy.context.scene.objects):
        if obj != ground and obj.parent is None:
            obj.matrix_world = sanctuary_transform @ obj.matrix_world

    # 9. Sub-shrines in Courtyard: Bhairava_Shrine and Ganesha_Shrine
    bhairava_shrine = create_sub_shrine(
        name="Bhairava_Shrine",
        location=(9.0, 8.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_granite, mat_deity=mat_black_stone, mat_gold=mat_gold
    )

    ganesha_shrine = create_sub_shrine(
        name="Ganesha_Shrine",
        location=(-9.0, 8.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_granite, mat_deity=mat_black_stone, mat_gold=mat_gold
    )

    # 10. Mallikarjuna Shiva Shrine (Secondary Sanctum in Srisailam Complex)
    mallikarjuna_shrine = create_mallikarjuna_shiva_shrine(
        name="Mallikarjuna_Shiva_Shrine",
        location=(0, 0, 0),
        mat_granite=mat_granite,
        mat_gold=mat_gold,
        mat_black_stone=mat_black_stone
    )

    mallikarjuna_shrine.rotation_euler.z = math.pi / 2
    mallikarjuna_shrine.location = (3, 0, 0)

    # Nandi facing Mallikarjuna Shiva Shrine
    nandi = create_nandi(
        name="Srisailam_Nandi",
        location=(0, 0, 0),
        scale=1.1,
        mat=mat_black_stone
    )
    nandi.rotation_euler.z = math.pi / 2
    nandi.location = (13, 0, 0)

    # 11. Large Srisailam Prakara Enclosure Wall
    prakara_objs = create_prakara_wall(
        name="Srisailam_Prakara",
        center=(0, 0.0, 0.0),
        width=36.0, depth=30.0,
        wall_height=3.6, wall_thickness=0.6,
        mat=mat_granite, gate_width=4.0, gate_sides=["E", "W", "N", "S"]
    )

    # 12. Nallamala Forest Sacred Trees along the outer perimeter
    tree_locs = [
        (-16.0, 12.0, 0.0), (-16.0, -12.0, 0.0),
        (16.0, 12.0, 0.0), (16.0, -12.0, 0.0),
        (-6.0, 13.0, 0.0), (6.0, 13.0, 0.0)
    ]
    for tidx, tloc in enumerate(tree_locs):
        create_tree(
            name=f"Nallamala_Tree_{tidx+1}",
            location=tloc,
            height=4.8,
            mat_trunk=mat_bark,
            mat_leaves=mat_leaves
        )

    # 13. Spawn_Point
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0, -12.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "srisailam_bhramaramba_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Srisailam Bhramaramba build complete!")


if __name__ == "__main__":
    build_srisailam_bhramaramba()
