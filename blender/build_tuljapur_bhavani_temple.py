"""
Build Script for Tuljapur Bhavani Temple
Shakti Peetha: Tuljapur, Maharashtra (Left cheek of Sati / Kulswamini Bhavani)
Architecture: Hill-fort prakara, Kallol Tirtha, 8-armed Mahishasuramardini, Hanuman Shrine
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


def create_sub_shrine(name, location, size=(2.2, 2.2, 2.6), mat_stone=None, mat_deity=None, mat_gold=None, deity_type="shrine"):
    """Creates a complete sub-shrine joined into a single mesh object."""
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

    # Murti inside (Hanuman gets orange/sindoor tinted form with mace)
    murti_objs = []
    if deity_type == "hanuman":
        # Hanuman body + tail
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=0.18, depth=0.5,
            location=(location[0], location[1], location[2] + 0.3 + 0.25)
        )
        h_body = bpy.context.active_object
        if mat_deity: h_body.data.materials.append(mat_deity)
        murti_objs.append(h_body)

        # Gada (mace)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.03, depth=0.4,
            location=(location[0] + 0.18, location[1], location[2] + 0.3 + 0.28)
        )
        gada = bpy.context.active_object
        if mat_gold: gada.data.materials.append(mat_gold)
        murti_objs.append(gada)
    else:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.2, depth=0.45,
            location=(location[0], location[1], location[2] + 0.3 + 0.25)
        )
        murti = bpy.context.active_object
        if mat_deity: murti.data.materials.append(mat_deity)
        murti_objs.append(murti)

    # Join all
    all_parts = [plinth] + pillars + [roof] + shikhara_objs + [kalasha] + murti_objs
    bpy.ops.object.select_all(action='DESELECT')
    for part in all_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = plinth
    bpy.ops.object.join()
    plinth.name = name
    return plinth


def create_deepamala(name, location, height=6.0, mat_stone=None):
    """Creates a traditional Maratha Deepamala lamp tower with radiating stone lamp brackets."""
    parts = []
    # Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.65, depth=0.7,
                                        location=(location[0], location[1], location[2] + 0.35))
    base = bpy.context.active_object
    if mat_stone: base.data.materials.append(mat_stone)
    parts.append(base)

    # Column shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.32, depth=height - 1.0,
                                        location=(location[0], location[1], location[2] + 0.7 + (height - 1.0)/2))
    shaft = bpy.context.active_object
    if mat_stone: shaft.data.materials.append(mat_stone)
    parts.append(shaft)

    # Radiating brackets around the pillar
    levels = 5
    for lvl in range(levels):
        lz = location[2] + 1.2 + lvl * 0.9
        for angle_i in range(4):
            ang = angle_i * (math.pi / 2) + (lvl * 0.4)
            bx = location[0] + math.cos(ang) * 0.45
            by = location[1] + math.sin(ang) * 0.45
            bpy.ops.mesh.primitive_cube_add(size=2, location=(bx, by, lz))
            b = bpy.context.active_object
            b.scale = (0.12, 0.12, 0.06)
            b.rotation_euler = (0, 0, ang)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            if mat_stone: b.data.materials.append(mat_stone)
            parts.append(b)

    # Top Kalasha
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.4, radius2=0.1, depth=0.5,
                                    location=(location[0], location[1], location[2] + height + 0.1))
    top = bpy.context.active_object
    if mat_stone: top.data.materials.append(mat_stone)
    parts.append(top)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = name
    return base


def create_bhavani_deity(name, location, mat_body, mat_gold, mat_silk):
    """Create 8-armed Mahishasuramardini slaying Mahishasura."""
    parts = []

    # Buffalo Mahishasura underfoot
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.12))
    demon = bpy.context.active_object
    demon.scale = (0.35, 0.22, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: demon.data.materials.append(mat_body)
    parts.append(demon)

    # Lotus Pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=0.1,
                                        location=(location[0], location[1], location[2] + 0.25))
    ped = bpy.context.active_object
    if mat_gold: ped.data.materials.append(mat_gold)
    parts.append(ped)

    # Lower body / silk pleated saree
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.5,
                                        location=(location[0], location[1], location[2] + 0.55))
    lower = bpy.context.active_object
    if mat_silk: lower.data.materials.append(mat_silk)
    parts.append(lower)

    # Torso
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.95))
    torso = bpy.context.active_object
    torso.scale = (0.24, 0.15, 0.26)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: torso.data.materials.append(mat_body)
    parts.append(torso)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(location[0], location[1], location[2] + 1.25))
    head = bpy.context.active_object
    if mat_body: head.data.materials.append(mat_body)
    parts.append(head)

    # Kiritam (Crown)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=0.03, depth=0.3,
                                    location=(location[0], location[1], location[2] + 1.48))
    crown = bpy.context.active_object
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)

    # 8 Arms (4 pairs)
    # Trishula piercing demon (Right primary arm thrusting forward-downward)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=1.2,
                                        location=(location[0] + 0.15, location[1] - 0.2, location[2] + 0.7))
    trishul = bpy.context.active_object
    trishul.rotation_euler = (0.4, -0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: trishul.data.materials.append(mat_gold)
    parts.append(trishul)

    for pair_idx in range(4):
        ang_z = 0.25 * pair_idx
        for side, sx in [("R", 1), ("L", -1)]:
            az = 1.05 - pair_idx * 0.12
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=8, radius=0.032, depth=0.36,
                location=(location[0] + sx * (0.26 + pair_idx * 0.04), location[1], location[2] + az)
            )
            arm = bpy.context.active_object
            arm.rotation_euler = (0, sx * (0.5 + ang_z), 0)
            bpy.ops.object.transform_apply(rotation=True)
            if mat_body: arm.data.materials.append(mat_body)
            parts.append(arm)

    # Golden Prabhavali arch
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.045,
                                     location=(location[0], location[1] + 0.06, location[2] + 1.1))
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


def build_tuljapur_bhavani():
    clear_scene()

    # Materials
    mat_sandstone = create_sandstone("Tuljapur_Sandstone", color=(0.75, 0.60, 0.40, 1.0), roughness=0.85)
    mat_dark_stone = create_black_stone("Fort_Stone_Basalt", color=(0.12, 0.11, 0.10, 1.0), roughness=0.6)
    mat_gold = create_gold_metal("Temple_Gold")
    mat_brass = create_brass_metal("Temple_Brass")
    mat_flame = create_flame_emission("Deepam_Flame")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_water = create_water("Kallol_Tirtha_Water")
    mat_silk = create_kumkum_red("Bhavani_Saree_Silk")
    mat_sindoor = create_kumkum_red("Hanuman_Sindoor", color=(0.90, 0.25, 0.05, 1.0))

    # 1. Ground Plane (Ground Z=0)
    ground = create_ground_plane("Ground_Main", size=65.0, mat=mat_sandstone)

    # 2. Raised Sanctum Plinth
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 4.0, 0.25))
    plinth = bpy.context.active_object
    plinth.scale = (3.5, 3.5, 0.25)
    plinth.name = "Tuljapur_Adhisthana"
    bpy.ops.object.transform_apply(scale=True)
    if mat_sandstone: plinth.data.materials.append(mat_sandstone)

    # 3. Garbhagriha
    gb_parts = create_garbhagriha(
        name="Garbhagriha_Structure",
        location=(0, 4.0, 0.5),
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

    # Shikhara atop Garbhagriha
    shikhara_objs = create_shikhara(
        name="Tuljapur_Shikhara",
        location=(0, 4.0, 4.5),
        base_width=4.4, height=8.0,
        tiers=6, mat=mat_sandstone, style="nagara"
    )
    for so in shikhara_objs:
        if "Kalasha" in so.name:
            so.data.materials.clear()
            so.data.materials.append(mat_gold)

    # 4. Deity: Deity_Bhavani (8-armed Mahishasuramardini)
    deity = create_bhavani_deity(
        name="Deity_Bhavani",
        location=(0, 4.8, 0.52),
        mat_body=mat_dark_stone,
        mat_gold=mat_gold,
        mat_silk=mat_silk
    )

    # 5. Mandapa: Pillared Sabha Mandapa with warm sandstone pillars
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
        mat_stone=mat_sandstone, mat_deity=mat_dark_stone, mat_gold=mat_gold
    )

    # Hanuman_Shrine (CRUCIAL: instead of Ganesha!)
    hanuman_shrine = create_sub_shrine(
        name="Hanuman_Shrine",
        location=(-9.0, 1.0, 0.0),
        size=(2.4, 2.4, 3.0),
        mat_stone=mat_sandstone, mat_deity=mat_sindoor, mat_gold=mat_gold,
        deity_type="hanuman"
    )

    # 10. Kallol Tirtha (Sacred Step-well Tank)
    kunda_objs = create_kunda(
        name="Kallol_Tirtha",
        location=(-11.0, -6.5, 0.0),
        size=(7.0, 7.0, 1.5),
        mat_stone=mat_sandstone, mat_water=mat_water, steps=5
    )

    # 11. Gomukh Tirtha spout near Kallol Tirtha
    bpy.ops.mesh.primitive_cube_add(size=2, location=(-11.0, -2.6, 0.5))
    gomukh = bpy.context.active_object
    gomukh.scale = (0.4, 0.4, 0.5)
    gomukh.name = "Gomukh_Tirtha_Spout"
    bpy.ops.object.transform_apply(scale=True)
    if mat_sandstone: gomukh.data.materials.append(mat_sandstone)

    # 12. Traditional Deepamala Pillar (Left Courtyard)
    deepamala = create_deepamala(
        name="Tuljapur_Deepamala",
        location=(4.5, -6.5, 0.0),
        height=6.5,
        mat_stone=mat_sandstone
    )

    # 13. Fortified Hill-Fort Prakara Walls with Corner Bastions
    prakara_objs = create_prakara_wall(
        name="Tuljapur_Fort_Prakara",
        center=(0, 0.0, 0.0),
        width=36.0, depth=30.0,
        wall_height=3.6, wall_thickness=0.65,
        mat=mat_dark_stone, gate_width=4.0, gate_sides=["S"]
    )
    # Add 4 circular corner bastions for hill-fort look
    for bx, by in [(-18.0, 15.0), (18.0, 15.0), (-18.0, -15.0), (18.0, -15.0)]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=1.6, depth=4.2,
            location=(bx, by, 2.1)
        )
        bastion = bpy.context.active_object
        bastion.name = f"Fort_Bastion_{int(bx)}_{int(by)}"
        if mat_dark_stone: bastion.data.materials.append(mat_dark_stone)

    # 14. Spawn_Point (Empty object at entrance facing north)
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0, -12.5, 0.0)
    bpy.context.collection.objects.link(spawn)

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "tuljapur_bhavani_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Tuljapur Bhavani build complete!")


if __name__ == "__main__":
    build_tuljapur_bhavani()
