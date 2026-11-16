"""
Madurai Meenakshi Amman Temple (Madurai, Tamil Nadu)
Meenakshi Devi - 4 Towering Colorful Raja Gopurams, Potramarai Kulam & Sundareshwarar Shrine
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

def build_madurai_meenakshi():
    geom.clear_scene()

    # 1. Materials
    mat_granite = mats.create_granite_stone("Madurai_Granite", color=(0.20, 0.19, 0.18, 1.0))
    mat_gold = mats.create_gold_metal("Lotus_Gold")
    mat_brass = mats.create_brass_metal("Bell_Brass")
    mat_water = mats.create_water("Potramarai_Water", color=(0.12, 0.38, 0.42, 0.85))
    mat_flame = mats.create_flame_emission("Deepam_Flame")
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Dhoti")
    mat_silk = mats.create_red_silk("Madurai_Silk", color=(0.85, 0.1, 0.25, 1.0))
    mat_paving = mats.create_granite_stone("Prakara_Paving", color=(0.32, 0.30, 0.28, 1.0))
    mat_garland = mats.create_flower_garland("Madurai_Malli", color=(0.96, 0.96, 0.90, 1.0))
    mat_meenakshi_green = mats.create_granite_stone("Emerald_Green_Stone", color=(0.08, 0.28, 0.16, 1.0), roughness=0.35)

    # Colorful Gopuram Tier Materials (Vibrant traditional stucco colors)
    colorful_palette = [
        mats.create_colorful_gopuram("Gopuram_Vermilion", color=(0.85, 0.22, 0.12, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Turquoise", color=(0.15, 0.65, 0.72, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Gold", color=(0.88, 0.72, 0.15, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Emerald", color=(0.12, 0.62, 0.28, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Coral", color=(0.92, 0.42, 0.22, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Indigo", color=(0.22, 0.25, 0.68, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Cream", color=(0.94, 0.90, 0.80, 1.0)),
    ]

    # 2. Main Ground Plane
    ground = geom.create_ground_plane(name="Ground_Main", size=85, mat=mat_paving)

    # 3. 4 TOWERING RAJA GOPURAMS in the 4 Cardinal Directions
    # South Raja Gopuram (Tallest - 9 tiers, landmark gateway)
    gopuram_south = geom.create_gopuram(
        name="South_Raja_Gopuram",
        location=(0.0, -18.0, 0.0),
        base_width=8.0,
        base_depth=4.5,
        height=15.0,
        tiers=9,
        colorful_mats=colorful_palette
    )
    # North Raja Gopuram (7 tiers)
    gopuram_north = geom.create_gopuram(
        name="North_Raja_Gopuram",
        location=(0.0, 26.0, 0.0),
        base_width=7.0,
        base_depth=4.0,
        height=13.0,
        tiers=7,
        colorful_mats=colorful_palette
    )
    # East Raja Gopuram (7 tiers)
    gopuram_east = geom.create_gopuram(
        name="East_Raja_Gopuram",
        location=(24.0, 4.0, 0.0),
        base_width=4.0,
        base_depth=7.0,
        height=13.0,
        tiers=7,
        colorful_mats=colorful_palette
    )
    # West Raja Gopuram (7 tiers)
    gopuram_west = geom.create_gopuram(
        name="West_Raja_Gopuram",
        location=(-24.0, 4.0, 0.0),
        base_width=4.0,
        base_depth=7.0,
        height=13.0,
        tiers=7,
        colorful_mats=colorful_palette
    )

    # 4. Potramarai Kulam (Golden Lotus Tank on Southeast side: X = 11 to 21, Y = -11 to -1)
    kulam_objs = geom.create_kunda(
        name="Potramarai_Kulam",
        location=(15.0, -6.0, 0.0),
        size=(9.0, 9.0, 1.8),
        mat_stone=mat_granite,
        mat_water=mat_water,
        steps=5
    )
    # Golden Lotus floating in center of Potramarai Kulam
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.7, depth=0.15,
        location=(15.0, -6.0, 0.55)
    )
    golden_lotus_base = bpy.context.active_object
    golden_lotus_base.name = "Golden_Lotus_Base"
    golden_lotus_base.data.materials.append(mat_gold)

    bpy.ops.mesh.primitive_cone_add(
        vertices=12, radius1=0.55, radius2=0.1, depth=0.45,
        location=(15.0, -6.0, 0.8)
    )
    golden_lotus_petals = bpy.context.active_object
    golden_lotus_petals.name = "Golden_Lotus_Petals"
    golden_lotus_petals.data.materials.append(mat_gold)

    # 5. Adhisthana (Raised Central Granite Temple Platform)
    adhisthana = geom.create_platform(
        name="Adhisthana_Platform",
        location=(0, 7.5, 0),
        size=(18.0, 22.0, 0.6),
        mat=mat_granite,
        steps=3
    )

    # 6. Garbhagriha (Sanctum of Meenakshi Amman)
    garb_center = (0.0, 13.5, 0.6)
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

    # Golden Vimanam atop Garbhagriha
    vimana_objs = geom.create_shikhara(
        name="Meenakshi_Vimanam",
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

    # 7. Deity_Meenakshi Murti (Green-tinted emerald stone with divine parrot)
    devi_objs = []
    devi_loc = (0.0, 14.5, 0.62)

    # Carved Lotus Pedestal
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.85, depth=0.25,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.125)
    )
    pedestal = bpy.context.active_object
    pedestal.data.materials.append(mat_gold)
    devi_objs.append(pedestal)

    # Torso (Emerald green deity stone draped in rich silk)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.95)
    )
    torso = bpy.context.active_object
    torso.scale = (0.3, 0.18, 0.42)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_silk)
    devi_objs.append(torso)

    # Head (Sculpted in gleaming emerald-green Maragatham stone)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.17, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.48)
    )
    head = bpy.context.active_object
    head.data.materials.append(mat_meenakshi_green)
    devi_objs.append(head)

    # Golden Kireeta (Tall Madurai Crown with gem crest)
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.22, radius2=0.04, depth=0.6,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.88)
    )
    crown = bpy.context.active_object
    crown.data.materials.append(mat_gold)
    devi_objs.append(crown)

    # Prabhavali Arch (Golden halo)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.7, minor_radius=0.065,
        location=(devi_loc[0], devi_loc[1] + 0.08, devi_loc[2] + 1.35)
    )
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    prabha.data.materials.append(mat_gold)
    devi_objs.append(prabha)

    # Arms (Right arm holding blue lotus, left arm resting gracefully in Lolahasta)
    # Right arm: raised holding Nilotpala (blue lotus)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.48,
        location=(devi_loc[0] + 0.4, devi_loc[1], devi_loc[2] + 1.15)
    )
    arm_r = bpy.context.active_object
    arm_r.rotation_euler = (0, 0.45, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_r.data.materials.append(mat_meenakshi_green)
    devi_objs.append(arm_r)

    # Blue Lotus in right hand
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.1, depth=0.08,
        location=(devi_loc[0] + 0.52, devi_loc[1] - 0.08, devi_loc[2] + 1.4)
    )
    lotus_flower = bpy.context.active_object
    lotus_flower.data.materials.append(colorful_palette[1])  # Turquoise/Blue
    devi_objs.append(lotus_flower)

    # Left arm: draped downward gracefully (Lola Hasta)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.55,
        location=(devi_loc[0] - 0.38, devi_loc[1], devi_loc[2] + 0.95)
    )
    arm_l = bpy.context.active_object
    arm_l.rotation_euler = (0, -0.15, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_l.data.materials.append(mat_meenakshi_green)
    devi_objs.append(arm_l)

    # Green Parrot (Kili) perched near right shoulder (Iconic Meenakshi attribute!)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.15,
        location=(devi_loc[0] + 0.28, devi_loc[1] - 0.12, devi_loc[2] + 1.48)
    )
    parrot_body = bpy.context.active_object
    parrot_body.rotation_euler = (0.3, 0.4, 0)
    bpy.ops.object.transform_apply(rotation=True)
    parrot_body.data.materials.append(colorful_palette[3])  # Emerald Green
    devi_objs.append(parrot_body)

    # Legs (Standing gracefully in Tribhanga / Samabhanga posture)
    for sx in [-0.12, 0.12]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.065, depth=0.55,
            location=(devi_loc[0] + sx, devi_loc[1], devi_loc[2] + 0.5)
        )
        leg = bpy.context.active_object
        leg.data.materials.append(mat_silk)
        devi_objs.append(leg)

    # Fragrant Madurai Jasmine Garland
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.28, minor_radius=0.045,
        location=(devi_loc[0], devi_loc[1] - 0.05, devi_loc[2] + 1.0)
    )
    garland = bpy.context.active_object
    garland.data.materials.append(mat_garland)
    devi_objs.append(garland)

    # Join into single Deity object named "Deity_Meenakshi"
    bpy.ops.object.select_all(action='DESELECT')
    for o in devi_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = devi_objs[0]
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = "Deity_Meenakshi"

    # 8. Deepams inside Garbhagriha
    deepam1 = geom.create_deepam(
        name="Deepam_1",
        location=(-1.4, 13.0, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    deepam2 = geom.create_deepam(
        name="Deepam_2",
        location=(1.4, 13.0, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_3",
        location=(-1.4, 14.8, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_4",
        location=(1.4, 14.8, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )

    # 9. Priest near sanctum door (standing at right of doorway)
    priest = geom.create_human_figure(
        name="Priest",
        location=(1.4, 10.2, 0.6),
        height=1.75,
        mat_skin=mat_skin,
        mat_cloth=mat_cloth
    )

    # 10. Mandapa (Ashta Shakti Mandapam / Pillared Hall in front of Garbhagriha)
    mandapa_objs = geom.create_mandapa(
        name="Mandapa_Hall",
        location=(0.0, 5.0, 0.6),
        width=8.5,
        depth=7.5,
        height=3.8,
        pillar_count_x=4,
        pillar_count_y=3,
        mat_stone=mat_granite,
        mat_floor=mat_paving,
        pillar_style="square"
    )
    bpy.ops.object.select_all(action='DESELECT')
    for o in mandapa_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_objs[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"

    # 11. Ghanta (Hanging Brass Bell at mandapa entrance)
    ghanta = geom.create_hanging_bell(
        name="Ghanta",
        location=(0.0, 1.4, 3.2),
        mat_brass=mat_brass,
        scale=1.2
    )

    # 12. Spawn Point (facing North, inside South Raja Gopuram)
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0.0, -10.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # 13. Sundareshwarar Shrine (Lord Shiva shrine on Northwest side: X = -12, Y = 13.5)
    sun_objs = []
    sun_loc = (-12.0, 13.5, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(sun_loc[0], sun_loc[1], sun_loc[2] + 0.3))
    s_base = bpy.context.active_object
    s_base.scale = (2.2, 2.2, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    s_base.data.materials.append(mat_granite)
    sun_objs.append(s_base)
    for dx, dy in [(-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8)]:
        p = geom.create_pillar(f"Sun_Pillar_{dx}_{dy}", (sun_loc[0] + dx, sun_loc[1] + dy, sun_loc[2] + 0.6), height=2.8, radius=0.16, mat=mat_granite)
        sun_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(sun_loc[0], sun_loc[1], sun_loc[2] + 3.5))
    s_roof = bpy.context.active_object
    s_roof.scale = (2.4, 2.4, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    s_roof.data.materials.append(mat_granite)
    sun_objs.append(s_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.8, radius2=0.3, depth=2.2, location=(sun_loc[0], sun_loc[1], sun_loc[2] + 4.8))
    s_vimana = bpy.context.active_object
    s_vimana.data.materials.append(mat_gold)
    sun_objs.append(s_vimana)
    # Sundareshwarar Shiva Lingam inside
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.25, depth=0.6, location=(sun_loc[0], sun_loc[1], sun_loc[2] + 0.9))
    lingam = bpy.context.active_object
    lingam.data.materials.append(mat_granite)
    sun_objs.append(lingam)
    # Small Nandi facing the Lingam
    nandi = geom.create_nandi("Sundareshwarar_Nandi", (sun_loc[0], sun_loc[1] - 1.2, sun_loc[2] + 0.6), scale=0.6, mat=mat_granite)
    sun_objs.append(nandi)
    # Join into Sundareshwarar_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in sun_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = sun_objs[0]
    bpy.ops.object.join()
    sundareshwarar = bpy.context.active_object
    sundareshwarar.name = "Sundareshwarar_Shrine"

    # 14. Bhairava Shrine on West side
    b_objs = []
    b_loc = (-12.0, 7.0, 0.0)
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

    # 15. Ganesha Shrine (Mukkuruni Vinayagar on West side near Mandapa)
    g_objs = []
    g_loc = (-12.0, 1.5, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(g_loc[0], g_loc[1], g_loc[2] + 0.3))
    g_base = bpy.context.active_object
    g_base.scale = (1.6, 1.6, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    g_base.data.materials.append(mat_granite)
    g_objs.append(g_base)
    for dx, dy in [(-1.3, -1.3), (1.3, -1.3), (-1.3, 1.3), (1.3, 1.3)]:
        p = geom.create_pillar(f"MV_Pillar_{dx}_{dy}", (g_loc[0] + dx, g_loc[1] + dy, g_loc[2] + 0.6), height=2.4, radius=0.14, mat=mat_granite)
        g_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(g_loc[0], g_loc[1], g_loc[2] + 3.1))
    g_roof = bpy.context.active_object
    g_roof.scale = (1.7, 1.7, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    g_roof.data.materials.append(mat_granite)
    g_objs.append(g_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.3, radius2=0.2, depth=1.6, location=(g_loc[0], g_loc[1], g_loc[2] + 4.1))
    g_cone = bpy.context.active_object
    g_cone.data.materials.append(mat_granite)
    g_objs.append(g_cone)
    # Mukkuruni Vinayagar Idol (Large monolithic Ganesha)
    g_murti = geom.create_deity_figure(name="Mukkuruni_Vinayagar_Murti", location=(g_loc[0], g_loc[1], g_loc[2] + 0.6), height=1.35, arms=4, mat_body=mat_granite, mat_ornament=mat_gold)
    g_objs.append(g_murti)
    # Join into Ganesha_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in g_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = g_objs[0]
    bpy.ops.object.join()
    ganesha_shrine = bpy.context.active_object
    ganesha_shrine.name = "Ganesha_Shrine"

    # 16. Prakara Wall connecting the 4 Gopurams
    prakara_objs = geom.create_prakara_wall(
        name="Prakara_Meenakshi",
        center=(0, 4.0, 0),
        width=46.0,
        depth=42.0,
        wall_height=3.6,
        wall_thickness=0.65,
        mat=mat_granite,
        gate_width=4.5,
        gate_sides=["N", "S", "E", "W"]
    )

    # 17. Export GLB
    export_path = Path(__file__).resolve().parent.parent / "godot" / "assets" / "models" / "madurai_meenakshi_kshetra_full.glb"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    geom.export_glb(str(export_path))
    print(f"Madurai Meenakshi export complete: {export_path}")

if __name__ == "__main__":
    build_madurai_meenakshi()
