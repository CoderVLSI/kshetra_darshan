"""
Build Script for Pithapuram Puruhutika Temple
Shakti Peetha: Pithapuram / Peethikapuram, Andhra Pradesh (Left hand of Sati / Pada Gaya Kshetra)
Architecture: Coastal Andhra Raja Gopuram, Pada Gaya Sarovar (tank), Kukkuteswara complex, 4-armed Puruhutika
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
    create_granite_stone, create_colorful_gopuram, create_gold_metal, create_brass_metal,
    create_flame_emission, create_skin, create_white_dhoti,
    create_water, create_white_marble, create_kumkum_red, create_flower_garland,
    create_sandstone
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_shikhara, create_gopuram, create_deepam, create_hanging_bell, create_kunda,
    create_human_figure, create_ground_plane, create_mandapa,
    create_prakara_wall, create_nandi, export_glb
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


def create_pada_gaya_tank(name, location, size=(8.0, 8.0, 1.6), mat_granite=None, mat_water=None, mat_gold=None):
    """Creates the sacred Pada Gaya Sarovar (tank) with stepped ghats and central mandapa."""
    kunda_objs = create_kunda(
        name=name,
        location=location,
        size=size,
        mat_stone=mat_granite,
        mat_water=mat_water,
        steps=4
    )
    # Small central Neerazhi Mandapa in the tank center
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.3))
    cm = bpy.context.active_object
    cm.scale = (0.7, 0.7, 0.3)
    cm.name = f"{name}_Central_Mandapa"
    bpy.ops.object.transform_apply(scale=True)
    if mat_granite: cm.data.materials.append(mat_granite)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.5, radius2=0.1, depth=0.6,
                                    location=(location[0], location[1], location[2] + 0.9))
    top = bpy.context.active_object
    top.name = f"{name}_Mandapa_Top"
    if mat_gold: top.data.materials.append(mat_gold)

    return kunda_objs + [cm, top]


def create_puruhutika_deity(name, location, mat_body, mat_gold, mat_silk):
    """Create 4-armed Puruhutika Devi murti (holding amrita kalasha, lotus, abhaya and varada mudras)."""
    parts = []

    # Pedestal (Lotus seat)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.42, depth=0.15,
                                        location=(location[0], location[1], location[2] + 0.075))
    ped = bpy.context.active_object
    if mat_gold: ped.data.materials.append(mat_gold)
    parts.append(ped)

    # Lower body / silk garment
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

    # High Andhra Kiritam (Crown)
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

    # Upper Left: Amrita Kalasha (Nectar Vessel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35,
                                        location=(location[0] - 0.28, location[1], location[2] + 0.95))
    al1 = bpy.context.active_object
    al1.rotation_euler = (0, -0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_body: al1.data.materials.append(mat_body)
    parts.append(al1)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(location[0] - 0.38, location[1] - 0.05, location[2] + 1.05))
    amrita = bpy.context.active_object
    if mat_gold: amrita.data.materials.append(mat_gold)
    parts.append(amrita)

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


def build_pithapuram_puruhutika():
    clear_scene()

    # Materials
    mat_granite = create_granite_stone("Andhra_Granite", color=(0.26, 0.24, 0.22, 1.0), roughness=0.85)
    mat_gold = create_gold_metal("Temple_Gold")
    mat_brass = create_brass_metal("Temple_Brass")
    mat_flame = create_flame_emission("Deepam_Flame")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_water = create_water("Pada_Gaya_Water")
    mat_silk = create_kumkum_red("Puruhutika_Silk")

    # Colorful Gopuram Tier Materials
    gopuram_mats = [
        create_colorful_gopuram("Gopuram_Red", color=(0.82, 0.22, 0.14, 1.0)),
        create_colorful_gopuram("Gopuram_Yellow", color=(0.88, 0.72, 0.15, 1.0)),
        create_colorful_gopuram("Gopuram_Blue", color=(0.18, 0.45, 0.78, 1.0)),
        create_colorful_gopuram("Gopuram_Green", color=(0.15, 0.60, 0.25, 1.0)),
        create_colorful_gopuram("Gopuram_Orange", color=(0.90, 0.45, 0.10, 1.0)),
        create_colorful_gopuram("Gopuram_White", color=(0.92, 0.90, 0.88, 1.0)),
        create_colorful_gopuram("Gopuram_Gold", color=(0.85, 0.70, 0.20, 1.0))
    ]

    # 1. Ground Plane (Ground Z=0)
    mat_paving = create_granite_stone(
        "Pithapuram_Courtyard_Paving", color=(.46, .44, .40, 1.0)
    )
    ground = create_ground_plane("Ground_Main", size=68.0, mat=mat_paving)

    # 2. Raised Dravidian Jagati Plinth
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 4.0, 0.3))
    plinth = bpy.context.active_object
    plinth.scale = (4.2, 4.2, 0.3)
    plinth.name = "Pithapuram_Jagati"
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

    # Dravidian Vimana atop Garbhagriha
    shikhara_objs = create_shikhara(
        name="Pithapuram_Vimana",
        location=(0, 4.0, 4.6),
        base_width=4.4, height=7.8,
        tiers=5, mat=mat_granite, style="dravidian"
    )
    for so in shikhara_objs:
        if "Kalasha" in so.name:
            so.data.materials.clear()
            so.data.materials.append(mat_gold)

    # 4. Deity: Deity_Puruhutika (4-armed Goddess)
    deity = create_puruhutika_deity(
        name="Deity_Puruhutika",
        location=(0, 4.8, 0.62),
        mat_body=mat_granite,
        mat_gold=mat_gold,
        mat_silk=mat_silk
    )

    # 5. Mandapa: Pillared Hall with carved granite columns
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

    # Puruhutika occupies the northeast of the shrine group and opens south.
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj != ground and obj.parent is None:
            obj.location += Vector((-6, 7, 0))

    # Kukkuteswara occupies its own sanctuary west of the tank. The approach
    # runs eastward from the shrine to the Nandi mandapa.
    shiva = Vector((-21, -6, 0))
    parts = create_garbhagriha(
        "Kukkuteswara_Garbhagriha", width=6.2, depth=6,
        wall_height=4, mat=mat_granite, door_width=2, door_height=2.7,
    )
    turn = Matrix.Translation(shiva) @ Matrix.Rotation(math.pi / 2, 4, 'Z')
    bpy.context.view_layer.update()
    for part in parts:
        part.matrix_world = turn @ part.matrix_world
    create_platform("Kukkuteswara_Roof", (-21, -6, 4),
                    size=(6.4, 6.5, .25), mat=mat_granite)
    create_shikhara("Kukkuteswara_Vimana", (-21, -6, 4.25),
                    base_width=5.8, height=6.2, tiers=5,
                    mat=mat_granite, mat_gold=mat_gold, style="dravidian")
    create_mandapa("Kukkuteswara_Mandapa", (-14.5, -6, 0), width=7, depth=6,
                   height=3.8, mat_stone=mat_granite, mat_floor=mat_granite)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=.8, depth=.32, location=(-21, -6, .16))
    pedestal = bpy.context.active_object
    pedestal.name = "Kukkuteswara_Pedestal"
    pedestal.data.materials.append(mat_granite)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(-21, -6, .68))
    lingam = bpy.context.active_object
    lingam.name = "Kukkuteswara_Lingam_Study"
    lingam.scale = (.32, .32, .51)
    lingam.data.materials.append(mat_granite)
    nandi = create_nandi("Kukkuteswara_Nandi", (-11.8, -6, .1), scale=1.3, mat=mat_granite)
    nandi.rotation_euler.z = math.pi / 2

    # 10. Sacred Pada Gaya Sarovar (Tank with central mandapa)
    tank_objs = create_pada_gaya_tank(
        name="Pada_Gaya_Tank",
        location=(10.0, -3.5, 0.0),
        size=(19.5, 23.0, 1.6),
        mat_granite=mat_granite,
        mat_water=mat_water,
        mat_gold=mat_gold
    )

    # 11. Coastal Andhra Colorful Raja Gopuram Gateway Tower at North Entrance
    gopuram_objs = create_gopuram(
        name="Pithapuram_Raja_Gopuram",
        location=(-6, 19.5, 0.0),
        base_width=7.0, base_depth=4.0,
        height=11.0, tiers=7,
        mat=mat_granite, colorful_mats=gopuram_mats
    )

    # 12. Prakara Wall with Gateway Opening
    prakara_objs = create_prakara_wall(
        name="Pithapuram_Prakara",
        center=(-6, 0, 0),
        width=56.0, depth=39.0,
        wall_height=3.4, wall_thickness=0.55,
        mat=mat_granite, gate_width=4.2, gate_sides=["N"]
    )

    # 13. Spawn_Point on the interior festival approach
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (-6, -3.5, 0.0)
    bpy.context.collection.objects.link(spawn)

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "pithapuram_puruhutika_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Pithapuram Puruhutika build complete!")


if __name__ == "__main__":
    build_pithapuram_puruhutika()
