"""
Mysore Chamundeshwari Temple (Chamundi Hills, Mysore, Karnataka)
Chamundeshwari Devi - 7-Tier Dravidian Gopuram, Mahishasura Statue & Giant Nandi
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

def build_mysore_chamundeshwari():
    geom.clear_scene()

    # 1. Materials
    mat_granite = mats.create_granite_stone("Hoysala_Granite", color=(0.22, 0.21, 0.20, 1.0))
    mat_black_granite = mats.create_black_stone("Nandi_Black_Basalt", color=(0.06, 0.06, 0.06, 1.0))
    mat_gold = mats.create_gold_metal("Kireeta_Gold")
    mat_brass = mats.create_brass_metal("Bell_Brass")
    mat_flame = mats.create_flame_emission("Deepam_Flame")
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Dhoti")
    mat_silk = mats.create_red_silk("Mysore_Silk", color=(0.82, 0.12, 0.18, 1.0))
    mat_kumkum = mats.create_kumkum_red("Chamundi_Sindoor")
    mat_paving = mats.create_granite_stone("Hilltop_Paving", color=(0.38, 0.35, 0.32, 1.0))
    mat_garland = mats.create_flower_garland("Marigold_Garland")

    # Colorful Gopuram & Mahishasura Stucco Palette
    mat_asura_yellow = mats.create_colorful_gopuram("Asura_Yellow", color=(0.95, 0.75, 0.12, 1.0))
    mat_asura_green = mats.create_colorful_gopuram("Cobra_Green", color=(0.15, 0.55, 0.22, 1.0))
    mat_asura_red = mats.create_colorful_gopuram("Asura_Red", color=(0.85, 0.18, 0.15, 1.0))
    mat_asura_skin = mats.create_colorful_gopuram("Asura_Skin", color=(0.92, 0.68, 0.52, 1.0))

    colorful_palette = [
        mats.create_colorful_gopuram("Gopuram_Gold", color=(0.88, 0.72, 0.18, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Terracotta", color=(0.78, 0.32, 0.18, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Teal", color=(0.18, 0.58, 0.62, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Crimson", color=(0.82, 0.15, 0.22, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Ochre", color=(0.85, 0.55, 0.18, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Green", color=(0.20, 0.60, 0.30, 1.0)),
        mats.create_colorful_gopuram("Gopuram_Cream", color=(0.92, 0.88, 0.78, 1.0)),
    ]

    # 2. Main Ground Plane
    ground = geom.create_ground_plane(name="Ground_Main", size=85, mat=mat_paving)

    # 3. 7-Tier Dravidian Raja Gopuram at Entrance
    gopuram = geom.create_gopuram(
        name="Chamundi_Gopuram",
        location=(0.0, -16.0, 0.0),
        base_width=7.5,
        base_depth=4.0,
        height=13.0,
        tiers=7,
        colorful_mats=colorful_palette
    )

    # 4. Giant Monolithic Nandi Bull (Chamundi Hill Nandi landmark on West courtyard: X = -12, Y = -4)
    nandi = geom.create_nandi(
        name="Giant_Nandi",
        location=(-12.0, -4.0, 0.0),
        scale=2.2,
        mat=mat_black_granite
    )
    # Bell garland around Nandi's neck
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.9, minor_radius=0.1,
        location=(-12.0, -3.2, 1.2)
    )
    nandi_garland = bpy.context.active_object
    nandi_garland.name = "Nandi_Bell_Garland"
    nandi_garland.rotation_euler = (0.5, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    nandi_garland.data.materials.append(mat_brass)

    # 5. Iconic Mahishasura Statue (Chamundi Hill landmark on East courtyard: X = 12, Y = -4)
    asura_objs = []
    asura_loc = (12.0, -4.0, 0.0)

    # Decorative Pedestal
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=1.2, depth=0.5,
        location=(asura_loc[0], asura_loc[1], asura_loc[2] + 0.25)
    )
    a_ped = bpy.context.active_object
    a_ped.data.materials.append(mat_granite)
    asura_objs.append(a_ped)

    # Torso (Muscular demon with royal dhoti)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(asura_loc[0], asura_loc[1], asura_loc[2] + 1.45)
    )
    a_torso = bpy.context.active_object
    a_torso.scale = (0.45, 0.28, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    a_torso.data.materials.append(mat_asura_skin)
    asura_objs.append(a_torso)

    # Dhoti
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.48, depth=0.6,
        location=(asura_loc[0], asura_loc[1], asura_loc[2] + 0.9)
    )
    a_dhoti = bpy.context.active_object
    a_dhoti.data.materials.append(mat_asura_yellow)
    asura_objs.append(a_dhoti)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.22, location=(asura_loc[0], asura_loc[1], asura_loc[2] + 2.15)
    )
    a_head = bpy.context.active_object
    a_head.data.materials.append(mat_asura_skin)
    asura_objs.append(a_head)

    # Prominent Moustache
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.35,
        location=(asura_loc[0], asura_loc[1] - 0.22, asura_loc[2] + 2.1)
    )
    a_moust = bpy.context.active_object
    a_moust.rotation_euler = (0, 0, math.pi / 2)
    bpy.ops.object.transform_apply(rotation=True)
    a_moust.data.materials.append(mat_black_granite)
    asura_objs.append(a_moust)

    # Demon Crown / Kireeta
    bpy.ops.mesh.primitive_cone_add(
        vertices=12, radius1=0.28, radius2=0.05, depth=0.65,
        location=(asura_loc[0], asura_loc[1], asura_loc[2] + 2.65)
    )
    a_crown = bpy.context.active_object
    a_crown.data.materials.append(mat_asura_red)
    asura_objs.append(a_crown)

    # Right Hand holding Upraised Sword (Khadga)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.06, depth=0.7,
        location=(asura_loc[0] + 0.6, asura_loc[1], asura_loc[2] + 1.8)
    )
    a_arm_r = bpy.context.active_object
    a_arm_r.rotation_euler = (0, 0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    a_arm_r.data.materials.append(mat_asura_skin)
    asura_objs.append(a_arm_r)

    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(asura_loc[0] + 0.95, asura_loc[1], asura_loc[2] + 2.4)
    )
    a_sword = bpy.context.active_object
    a_sword.scale = (0.05, 0.1, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    a_sword.data.materials.append(mat_gold)
    asura_objs.append(a_sword)

    # Left Hand holding Coiled Cobra (Naga)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.06, depth=0.7,
        location=(asura_loc[0] - 0.6, asura_loc[1], asura_loc[2] + 1.8)
    )
    a_arm_l = bpy.context.active_object
    a_arm_l.rotation_euler = (0, -0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    a_arm_l.data.materials.append(mat_asura_skin)
    asura_objs.append(a_arm_l)

    # Cobra coiled in hand
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.25, minor_radius=0.06,
        location=(asura_loc[0] - 0.9, asura_loc[1] - 0.1, asura_loc[2] + 2.2)
    )
    cobra = bpy.context.active_object
    cobra.data.materials.append(mat_asura_green)
    asura_objs.append(cobra)

    # Join into single Mahishasura_Statue object
    bpy.ops.object.select_all(action='DESELECT')
    for o in asura_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = asura_objs[0]
    bpy.ops.object.join()
    mahishasura = bpy.context.active_object
    mahishasura.name = "Mahishasura_Statue"

    # 6. Adhisthana (Raised Central Granite Temple Platform)
    adhisthana = geom.create_platform(
        name="Adhisthana_Platform",
        location=(0, 7.5, 0),
        size=(18.0, 22.0, 0.6),
        mat=mat_granite,
        steps=3
    )

    # 7. Garbhagriha (Sanctum of Chamundeshwari Devi)
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

    # Golden Dravidian Vimanam atop Garbhagriha
    vimana_objs = geom.create_shikhara(
        name="Chamundeshwari_Vimanam",
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

    # 8. Deity_Chamundeshwari Murti (8-Armed Mahishasura Mardini)
    # Holding Trishula piercing Mahishasura, Chakra, Shankha, Khadga, Khetaka, Dhanus, Bana, Abhaya
    devi_objs = []
    devi_loc = (0.0, 14.5, 0.62)

    # Lotus Altar with Satiated Lion (Simha Vahana)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.9, depth=0.25,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.125)
    )
    altar = bpy.context.active_object
    altar.data.materials.append(mat_gold)
    devi_objs.append(altar)

    # Slain Buffalo Demon at feet
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(devi_loc[0], devi_loc[1] - 0.2, devi_loc[2] + 0.3)
    )
    mahisha_head = bpy.context.active_object
    mahisha_head.scale = (0.35, 0.25, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    mahisha_head.data.materials.append(mat_black_granite)
    devi_objs.append(mahisha_head)

    # Torso (Radiant Golden Goddess in Mysore Silk Sari)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.0)
    )
    torso = bpy.context.active_object
    torso.scale = (0.32, 0.2, 0.45)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_silk)
    devi_objs.append(torso)

    # Head (Gleaming Golden Devi with third eye)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.17, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.52)
    )
    head = bpy.context.active_object
    head.data.materials.append(mat_gold)
    devi_objs.append(head)

    # Kumkum tilak on forehead
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.035, location=(devi_loc[0], devi_loc[1] - 0.16, devi_loc[2] + 1.58)
    )
    tilak = bpy.context.active_object
    tilak.data.materials.append(mat_kumkum)
    devi_objs.append(tilak)

    # Golden Kireeta (Grand Mysore Royal Crown)
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.24, radius2=0.04, depth=0.65,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.95)
    )
    crown = bpy.context.active_object
    crown.data.materials.append(mat_gold)
    devi_objs.append(crown)

    # Prabhavali Arch (Blazing Golden Arch)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.75, minor_radius=0.07,
        location=(devi_loc[0], devi_loc[1] + 0.08, devi_loc[2] + 1.4)
    )
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    prabha.data.materials.append(mat_gold)
    devi_objs.append(prabha)

    # Central Trishula (Trident held by two front hands, thrusting down at Mahishasura)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.025, depth=1.6,
        location=(devi_loc[0] + 0.1, devi_loc[1] - 0.1, devi_loc[2] + 0.9)
    )
    trishula_shaft = bpy.context.active_object
    trishula_shaft.rotation_euler = (0.2, -0.15, 0)
    bpy.ops.object.transform_apply(rotation=True)
    trishula_shaft.data.materials.append(mat_gold)
    devi_objs.append(trishula_shaft)

    # Trishula 3 prongs at top
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.08, radius2=0.01, depth=0.25,
        location=(devi_loc[0] + 0.22, devi_loc[1] - 0.15, devi_loc[2] + 1.7)
    )
    prong = bpy.context.active_object
    prong.data.materials.append(mat_gold)
    devi_objs.append(prong)

    # Multiple Divine Arms (8 arms radiating majestically)
    arm_angles = [
        (0.45, 0.4, "R_Chakra"),
        (0.5, 0.1, "R_Khadga"),
        (0.4, -0.2, "R_Bana"),
        (-0.45, 0.4, "L_Shankha"),
        (-0.5, 0.1, "L_Khetaka"),
        (-0.4, -0.2, "L_Dhanus"),
    ]
    for ax, az, aname in arm_angles:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.035, depth=0.48,
            location=(devi_loc[0] + ax, devi_loc[1], devi_loc[2] + 1.2 + az)
        )
        arm = bpy.context.active_object
        arm.rotation_euler = (0, 0.8 if ax > 0 else -0.8, 0)
        bpy.ops.object.transform_apply(rotation=True)
        arm.data.materials.append(mat_gold)
        devi_objs.append(arm)

    # Legs (Standing triumphantly with right foot on Mahishasura)
    for sx in [-0.14, 0.14]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.065, depth=0.58,
            location=(devi_loc[0] + sx, devi_loc[1], devi_loc[2] + 0.52)
        )
        leg = bpy.context.active_object
        leg.data.materials.append(mat_silk)
        devi_objs.append(leg)

    # Marigold Garland
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.3, minor_radius=0.05,
        location=(devi_loc[0], devi_loc[1] - 0.05, devi_loc[2] + 1.05)
    )
    garland = bpy.context.active_object
    garland.data.materials.append(mat_garland)
    devi_objs.append(garland)

    # Join into single Deity object named "Deity_Chamundeshwari"
    bpy.ops.object.select_all(action='DESELECT')
    for o in devi_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = devi_objs[0]
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = "Deity_Chamundeshwari"

    # 9. Deepams inside Garbhagriha
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

    # 10. Priest near sanctum door (standing at right of doorway)
    priest = geom.create_human_figure(
        name="Priest",
        location=(1.4, 10.2, 0.6),
        height=1.75,
        mat_skin=mat_skin,
        mat_cloth=mat_cloth
    )

    # 11. Mandapa (Navaranga / Pillared Hall in front of Garbhagriha)
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

    # 12. Ghanta (Hanging Brass Bell at Navaranga entrance)
    ghanta = geom.create_hanging_bell(
        name="Ghanta",
        location=(0.0, 1.4, 3.2),
        mat_brass=mat_brass,
        scale=1.2
    )

    # 13. Spawn Point (facing North inside entrance)
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0.0, -10.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # 14. Bhairava Shrine (Kruradrishti Bhairava on West side)
    b_objs = []
    b_loc = (-11.0, 7.5, 0.0)
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
    # Kruradrishti Bhairava Murti
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

    # 15. Ganesha Shrine (Mahaganapathi on West side near Mandapa)
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
    # Mahaganapathi Murti
    g_murti = geom.create_deity_figure(name="Mahaganapathi_Murti", location=(g_loc[0], g_loc[1], g_loc[2] + 0.6), height=1.1, arms=4, mat_body=mat_granite, mat_ornament=mat_gold)
    g_objs.append(g_murti)
    # Join into Ganesha_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in g_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = g_objs[0]
    bpy.ops.object.join()
    ganesha_shrine = bpy.context.active_object
    ganesha_shrine.name = "Ganesha_Shrine"

    # 16. Prakara Wall with Chamundi Hill battlements
    prakara_objs = geom.create_prakara_wall(
        name="Prakara_Chamundeshwari",
        center=(0, 6.0, 0),
        width=40.0,
        depth=36.0,
        wall_height=3.4,
        wall_thickness=0.6,
        mat=mat_granite,
        gate_width=4.0,
        gate_sides=["S"]
    )

    # 17. Export GLB
    export_path = Path(__file__).resolve().parent.parent / "godot" / "assets" / "models" / "mysore_chamundeshwari_kshetra_full.glb"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    geom.export_glb(str(export_path))
    print(f"Mysore Chamundeshwari export complete: {export_path}")

if __name__ == "__main__":
    build_mysore_chamundeshwari()
