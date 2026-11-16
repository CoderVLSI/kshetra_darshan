"""
Kanchipuram Kamakshi Amman Temple (Kanchipuram, Tamil Nadu)
Kamakshi Devi - Golden Dravidian Vimanam, 24-Pillar Gayatri Mandapam & Panchaganga Tank
"""
import sys
from pathlib import Path

blender_dir = Path(__file__).resolve().parent
if str(blender_dir) not in sys.path:
    sys.path.insert(0, str(blender_dir))

import bpy
import bmesh
import math
from mathutils import Vector

import common_materials as mats
import common_geometry as geom

def export_glb_53(filepath, apply_modifiers=True):
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

geom.export_glb = export_glb_53

def build_kanchipuram_kamakshi():
    geom.clear_scene()

    # 1. Materials
    mat_granite = mats.create_granite_stone("Dravidian_Granite", color=(0.22, 0.20, 0.19, 1.0))
    mat_gold = mats.create_gold_metal("Vimanam_Gold")
    mat_marble = mats.create_white_marble("Mandapam_Floor")
    mat_brass = mats.create_brass_metal("Bell_Brass")
    mat_water = mats.create_water("Panchaganga_Water")
    mat_flame = mats.create_flame_emission("Deepam_Flame")
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Dhoti")
    mat_silk = mats.create_red_silk("Kamakshi_Kanchipuram_Silk")
    mat_kumkum = mats.create_kumkum_red("Kumkum_Vermilion")
    mat_garland = mats.create_flower_garland("Jasmine_Garland", color=(0.95, 0.95, 0.85, 1.0))
    mat_paving = mats.create_granite_stone("Prakara_Paving", color=(0.35, 0.32, 0.30, 1.0))

    # 2. Main Ground Plane
    ground = geom.create_ground_plane(name="Ground_Main", size=75, mat=mat_paving)

    # 3. Panchaganga Theertham (Sacred Temple Tank on East side: X = 14 to 28)
    kunda_objs = geom.create_kunda(
        name="Panchaganga_Tank",
        location=(19.0, 5.0, 0.0),
        size=(10.0, 12.0, 1.8),
        mat_stone=mat_granite,
        mat_water=mat_water,
        steps=5
    )

    # 4. Adhisthana (Raised Dravidian Temple Platform)
    adhisthana = geom.create_platform(
        name="Adhisthana_Platform",
        location=(0, 8.0, 0),
        size=(18.0, 24.0, 0.6),
        mat=mat_granite,
        steps=3
    )

    # 5. Garbhagriha (Sanctum)
    garb_center = (0.0, 14.5, 0.6)
    garb_objs = geom.create_garbhagriha(
        name="Garbhagriha_Wall",
        location=garb_center,
        width=5.5,
        depth=5.5,
        wall_height=4.2,
        wall_thickness=0.5,
        mat=mat_granite,
        door_width=1.6,
        door_height=2.7
    )

    # Join Garbhagriha walls & floor into "Garbhagriha"
    bpy.ops.object.select_all(action='DESELECT')
    for o in garb_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = garb_objs[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # 6. Golden Dravidian Vimanam (Stepped Pyramid covered in gold)
    vimana_objs = geom.create_shikhara(
        name="Golden_Vimanam",
        location=(garb_center[0], garb_center[1], garb_center[2] + 4.2),
        base_width=5.2,
        height=7.5,
        tiers=5,
        mat=mat_gold,
        style="dravidian"
    )
    for obj in vimana_objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat_gold)

    # 7. Deity_Kamakshi Murti (Kamakshi Amman seated in Padmasana)
    # 4 arms: Sugarcane bow (Ikshu kodanda), 5 flower arrows (Pancha bana), Pasha (noose), Ankusha (goad)
    devi_objs = []
    devi_loc = (0.0, 15.5, 0.62)

    # Sri Chakra Yantra Peetha (Sanctum front altar)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.9, depth=0.25,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.125)
    )
    yantra_peetha = bpy.context.active_object
    yantra_peetha.data.materials.append(mat_gold)
    devi_objs.append(yantra_peetha)

    # Padmasana Lotus Throne
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.75, depth=0.2,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.32)
    )
    lotus = bpy.context.active_object
    lotus.data.materials.append(mat_gold)
    devi_objs.append(lotus)

    # Torso (Dark Granite clad in Kanchipuram silk sari)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.95)
    )
    torso = bpy.context.active_object
    torso.scale = (0.32, 0.2, 0.42)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_silk)
    devi_objs.append(torso)

    # Head (Polished black granite with kumkum tilak)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.17, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.48)
    )
    head = bpy.context.active_object
    head.data.materials.append(mat_granite)
    devi_objs.append(head)

    # Kumkum tilak on forehead
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.035, location=(devi_loc[0], devi_loc[1] - 0.16, devi_loc[2] + 1.54)
    )
    tilak = bpy.context.active_object
    tilak.data.materials.append(mat_kumkum)
    devi_objs.append(tilak)

    # Golden Kireeta (Grand Dravidian Crown)
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.22, radius2=0.04, depth=0.6,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.88)
    )
    crown = bpy.context.active_object
    crown.data.materials.append(mat_gold)
    devi_objs.append(crown)

    # Crescent Moon (Chandra Kala) on crown
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.15, minor_radius=0.02,
        location=(devi_loc[0] + 0.1, devi_loc[1] - 0.1, devi_loc[2] + 1.95)
    )
    moon = bpy.context.active_object
    moon.data.materials.append(mat_gold)
    devi_objs.append(moon)

    # Golden Prabhavali Arch
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.7, minor_radius=0.07,
        location=(devi_loc[0], devi_loc[1] + 0.08, devi_loc[2] + 1.35)
    )
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    prabha.data.materials.append(mat_gold)
    devi_objs.append(prabha)

    # Padmasana folded legs
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.48, depth=0.25,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.48)
    )
    legs = bpy.context.active_object
    legs.data.materials.append(mat_silk)
    devi_objs.append(legs)

    # 4 Arms:
    # Upper Right: Pasha (sacred noose)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.45,
        location=(devi_loc[0] + 0.42, devi_loc[1], devi_loc[2] + 1.2)
    )
    arm_ur = bpy.context.active_object
    arm_ur.rotation_euler = (0, 0.5, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ur.data.materials.append(mat_granite)
    devi_objs.append(arm_ur)

    # Upper Left: Ankusha (elephant goad)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.45,
        location=(devi_loc[0] - 0.42, devi_loc[1], devi_loc[2] + 1.2)
    )
    arm_ul = bpy.context.active_object
    arm_ul.rotation_euler = (0, -0.5, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ul.data.materials.append(mat_granite)
    devi_objs.append(arm_ul)

    # Lower Left: Ikshu Kodanda (Sugarcane bow held vertically)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.02, depth=1.4,
        location=(devi_loc[0] - 0.38, devi_loc[1] - 0.1, devi_loc[2] + 1.1)
    )
    bow = bpy.context.active_object
    bow.data.materials.append(mat_gold)
    devi_objs.append(bow)

    # Lower Right: Pushpa Bana (5 flower arrows)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.015, depth=0.6,
        location=(devi_loc[0] + 0.35, devi_loc[1] - 0.1, devi_loc[2] + 0.85)
    )
    arrows = bpy.context.active_object
    arrows.rotation_euler = (0.2, 0.3, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arrows.data.materials.append(mat_gold)
    devi_objs.append(arrows)

    # Jasmine garland (Malli poo)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.3, minor_radius=0.045,
        location=(devi_loc[0], devi_loc[1] - 0.05, devi_loc[2] + 1.0)
    )
    garland = bpy.context.active_object
    garland.data.materials.append(mat_garland)
    devi_objs.append(garland)

    # Join into single Deity object named "Deity_Kamakshi"
    bpy.ops.object.select_all(action='DESELECT')
    for o in devi_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = devi_objs[0]
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = "Deity_Kamakshi"

    # 8. Deepams inside Garbhagriha
    deepam1 = geom.create_deepam(
        name="Deepam_1",
        location=(-1.4, 14.0, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    deepam2 = geom.create_deepam(
        name="Deepam_2",
        location=(1.4, 14.0, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_3",
        location=(-1.4, 15.8, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_4",
        location=(1.4, 15.8, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )

    # 9. Priest near sanctum door (standing at right of doorway)
    priest = geom.create_human_figure(
        name="Priest",
        location=(1.4, 11.0, 0.6),
        height=1.75,
        mat_skin=mat_skin,
        mat_cloth=mat_cloth
    )

    # 10. Gayatri Mandapam (24 pillars representing 24 syllables of Gayatri Mantra!)
    # 6 rows along Y (at Y = 2.0, 3.5, 5.0, 6.5, 8.0, 9.5), 4 pillars per row (X = -3.6, -1.8, 1.8, 3.6)
    # The central corridor (-1.8 to +1.8) is completely open!
    mandapa_objs = []
    # Floor slab
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(0.0, 5.8, 0.6 + 0.05)
    )
    m_floor = bpy.context.active_object
    m_floor.scale = (4.6, 4.6, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    m_floor.data.materials.append(mat_marble)
    mandapa_objs.append(m_floor)

    # 24 Gayatri Pillars
    pillar_idx = 1
    y_coords = [2.0, 3.5, 5.0, 6.5, 8.0, 9.5]
    x_coords = [-3.6, -1.8, 1.8, 3.6]
    for py in y_coords:
        for px in x_coords:
            p = geom.create_pillar(
                name=f"Gayatri_Pillar_{pillar_idx}",
                location=(px, py, 0.7),
                height=3.6,
                radius=0.18,
                mat=mat_granite,
                style="square"
            )
            mandapa_objs.append(p)
            pillar_idx += 1

    # Roof slab
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(0.0, 5.8, 0.7 + 3.6 + 0.1)
    )
    m_roof = bpy.context.active_object
    m_roof.scale = (4.8, 4.8, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    m_roof.data.materials.append(mat_granite)
    mandapa_objs.append(m_roof)

    # Join into single object named "Mandapa"
    bpy.ops.object.select_all(action='DESELECT')
    for o in mandapa_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_objs[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"

    # 11. Ghanta (Hanging Brass Bell at Gayatri Mandapam entrance)
    ghanta = geom.create_hanging_bell(
        name="Ghanta",
        location=(0.0, 1.4, 3.2),
        mat_brass=mat_brass,
        scale=1.2
    )

    # 12. Spawn Point (facing North)
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0.0, -8.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # 13. Bhairava Shrine on West side
    b_objs = []
    b_loc = (-11.0, 7.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(b_loc[0], b_loc[1], b_loc[2] + 0.3))
    b_base = bpy.context.active_object
    b_base.scale = (1.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    b_base.data.materials.append(mat_granite)
    b_objs.append(b_base)
    for dx, dy in [(-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)]:
        p = geom.create_pillar(f"B_Pillar_{dx}_{dy}", (b_loc[0] + dx, b_loc[1] + dy, b_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_granite)
        b_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(b_loc[0], b_loc[1], b_loc[2] + 2.9))
    b_roof = bpy.context.active_object
    b_roof.scale = (1.6, 1.6, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    b_roof.data.materials.append(mat_granite)
    b_objs.append(b_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.2, radius2=0.2, depth=1.5, location=(b_loc[0], b_loc[1], b_loc[2] + 3.8))
    b_cone = bpy.context.active_object
    b_cone.data.materials.append(mat_granite)
    b_objs.append(b_cone)
    # Bhairava Murti
    b_murti = geom.create_deity_figure(name="Bhairava_Murti", location=(b_loc[0], b_loc[1], b_loc[2] + 0.6), height=1.2, arms=4, mat_body=mat_granite, mat_ornament=mat_gold)
    b_objs.append(b_murti)
    # Join into Bhairava_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in b_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = b_objs[0]
    bpy.ops.object.join()
    bhairava_shrine = bpy.context.active_object
    bhairava_shrine.name = "Bhairava_Shrine"

    # 14. Ganesha Shrine (Santhana Ganapathi on West side)
    g_objs = []
    g_loc = (-11.0, 13.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(g_loc[0], g_loc[1], g_loc[2] + 0.3))
    g_base = bpy.context.active_object
    g_base.scale = (1.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    g_base.data.materials.append(mat_granite)
    g_objs.append(g_base)
    for dx, dy in [(-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)]:
        p = geom.create_pillar(f"G_Pillar_{dx}_{dy}", (g_loc[0] + dx, g_loc[1] + dy, g_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_granite)
        g_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(g_loc[0], g_loc[1], g_loc[2] + 2.9))
    g_roof = bpy.context.active_object
    g_roof.scale = (1.6, 1.6, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    g_roof.data.materials.append(mat_granite)
    g_objs.append(g_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.2, radius2=0.2, depth=1.5, location=(g_loc[0], g_loc[1], g_loc[2] + 3.8))
    g_cone = bpy.context.active_object
    g_cone.data.materials.append(mat_granite)
    g_objs.append(g_cone)
    # Santhana Ganapathi Murti
    g_murti = geom.create_deity_figure(name="Santhana_Ganapathi_Murti", location=(g_loc[0], g_loc[1], g_loc[2] + 0.6), height=1.1, arms=4, mat_body=mat_granite, mat_ornament=mat_gold)
    g_objs.append(g_murti)
    # Join into Ganesha_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in g_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = g_objs[0]
    bpy.ops.object.join()
    ganesha_shrine = bpy.context.active_object
    ganesha_shrine.name = "Ganesha_Shrine"

    # 15. Prakara Wall with Dravidian Yali pillars & South Gateway
    prakara_objs = geom.create_prakara_wall(
        name="Prakara_Kamakshi",
        center=(0, 7.0, 0),
        width=38.0,
        depth=34.0,
        wall_height=3.4,
        wall_thickness=0.6,
        mat=mat_granite,
        gate_width=4.0,
        gate_sides=["S"]
    )

    # 16. Export GLB
    export_path = Path(__file__).resolve().parent.parent / "godot" / "assets" / "models" / "kanchipuram_kamakshi_kshetra_full.glb"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    geom.export_glb(str(export_path))
    print(f"Kanchipuram Kamakshi export complete: {export_path}")

if __name__ == "__main__":
    build_kanchipuram_kamakshi()
