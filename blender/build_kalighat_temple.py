"""
Kalighat Kali Temple (Kalighat, Kolkata, West Bengal)
Dakshina Kali - Bengali Aatchala Architecture & Adi Ganga Ghat
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

# Monkeypatch export_glb in case coordinator's fix or local override needed
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

def create_curved_chala_roof(base_loc, base_size, height, mat_roof, mat_trim):
    """Create a Bengal style curved-eave (chala) roof segment."""
    bw, bd = base_size
    bx, by, bz = base_loc
    objs = []
    
    # 4 curved triangular/trapezoid roof slopes using stacked tiers with curved profile
    tiers = 8
    for i in range(tiers):
        t0 = i / tiers
        t1 = (i + 1) / tiers
        # Parabolic droop for Bengali curved eaves
        curve_factor0 = (1.0 - t0**1.4)
        curve_factor1 = (1.0 - t1**1.4)
        
        w0 = bw * 0.5 * (curve_factor0 * 0.85 + 0.15)
        d0 = bd * 0.5 * (curve_factor0 * 0.85 + 0.15)
        
        z = bz + i * (height / tiers) + (height / tiers) * 0.5
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(bx, by, z))
        tier = bpy.context.active_object
        tier.scale = (w0, d0, (height / tiers) * 0.5)
        bpy.ops.object.transform_apply(scale=True)
        tier.data.materials.append(mat_roof if i % 2 == 0 else mat_trim)
        objs.append(tier)
    
    return objs

def build_kalighat():
    geom.clear_scene()

    # 1. Materials
    mat_marble = mats.create_white_marble("Marble_White")
    mat_terracotta = mats.create_terracotta("Bengal_Terracotta")
    mat_gold = mats.create_gold_metal("Ornament_Gold")
    mat_black_stone = mats.create_black_stone("Kali_Basalt")
    mat_red = mats.create_kumkum_red("Sindoor_Red")
    mat_silk = mats.create_red_silk("Kali_Red_Silk")
    mat_brass = mats.create_brass_metal("Bell_Brass")
    mat_flame = mats.create_flame_emission("Deepam_Flame")
    mat_water = mats.create_water("Adi_Ganga_Water")
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Dhoti")
    mat_paving = mats.create_granite_stone("Courtyard_Paving", color=(0.75, 0.72, 0.68, 1.0))
    mat_ghat_stone = mats.create_sandstone("Ghat_Sandstone", color=(0.6, 0.55, 0.48, 1.0))
    mat_garland = mats.create_flower_garland("Hibiscus_Garland", color=(0.9, 0.1, 0.1, 1.0))

    # 2. Main Ground Plane
    ground = geom.create_ground_plane(name="Ground_Main", size=75, mat=mat_paving)

    # 3. Adi Ganga River & Ghat (on East side: X = 15 to 35)
    ghat_objs = []
    # Water plane for Adi Ganga
    bpy.ops.mesh.primitive_plane_add(size=1, location=(25.0, 5.0, 0.05))
    river = bpy.context.active_object
    river.name = "Adi_Ganga_River"
    river.scale = (12.0, 36.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    river.data.materials.append(mat_water)
    ghat_objs.append(river)

    # Stepped Ghat leading down to river
    steps_count = 6
    step_width = 2.0
    for i in range(steps_count):
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=(14.0 + i * 1.5, 5.0, 0.5 - i * 0.08)
        )
        step = bpy.context.active_object
        step.scale = (0.75, 25.0, 0.1)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(mat_ghat_stone)
        ghat_objs.append(step)

    # 4. Temple Plinth / Raised Adhisthana
    plinth = geom.create_platform(
        name="Temple_Plinth",
        location=(0, 8.0, 0),
        size=(18.0, 22.0, 0.6),
        mat=mat_marble,
        steps=3
    )

    # 5. Garbhagriha (Sanctum)
    garb_center = (0.0, 14.0, 0.6)
    garb_objs = geom.create_garbhagriha(
        name="Garbhagriha_Wall",
        location=garb_center,
        width=5.5,
        depth=5.5,
        wall_height=4.2,
        wall_thickness=0.5,
        mat=mat_marble,
        door_width=1.6,
        door_height=2.7
    )

    # Add terracotta relief borders to Garbhagriha facade
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(garb_center[0], garb_center[1] - 2.8, garb_center[2] + 2.1)
    )
    t_border = bpy.context.active_object
    t_border.scale = (2.7, 0.08, 2.1)
    bpy.ops.object.transform_apply(scale=True)
    t_border.data.materials.append(mat_terracotta)
    garb_objs.append(t_border)

    # Join Garbhagriha walls, lintel, floor & terracotta panels into "Garbhagriha"
    bpy.ops.object.select_all(action='DESELECT')
    for o in garb_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = garb_objs[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # 6. Bengali Aatchala Roof (Double curved-eave chala roof)
    # Lower chala roof
    lower_chala = create_curved_chala_roof(
        base_loc=(garb_center[0], garb_center[1], garb_center[2] + 4.2),
        base_size=(7.0, 7.0),
        height=2.8,
        mat_roof=mat_terracotta,
        mat_trim=mat_marble
    )
    # Upper chala roof (smaller tier on top)
    upper_chala = create_curved_chala_roof(
        base_loc=(garb_center[0], garb_center[1], garb_center[2] + 7.0),
        base_size=(4.2, 4.2),
        height=2.4,
        mat_roof=mat_terracotta,
        mat_trim=mat_gold
    )
    # Crown Kalasha (Kalash finials on roof peak)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.35,
        location=(garb_center[0], garb_center[1], garb_center[2] + 9.6)
    )
    k_sphere = bpy.context.active_object
    k_sphere.data.materials.append(mat_gold)

    bpy.ops.mesh.primitive_cone_add(
        vertices=12, radius1=0.2, radius2=0.02, depth=0.7,
        location=(garb_center[0], garb_center[1], garb_center[2] + 10.05)
    )
    k_finial = bpy.context.active_object
    k_finial.data.materials.append(mat_gold)

    # 7. Deity_Kalika (Dakshina Kali Murti)
    # 4-armed dark basalt murti, golden crown, tongue, khadga, abhaya/varada, garland
    kali_objs = []
    kali_loc = (0.0, 15.0, 0.62)

    # Shiva lying in dhyana beneath Kali's feet
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(kali_loc[0], kali_loc[1] - 0.15, kali_loc[2] + 0.12)
    )
    shiva_pedestal = bpy.context.active_object
    shiva_pedestal.scale = (0.9, 0.5, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    shiva_pedestal.data.materials.append(mat_marble)
    kali_objs.append(shiva_pedestal)

    # Lotus Altar Base
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.9, depth=0.15,
        location=(kali_loc[0], kali_loc[1], kali_loc[2] + 0.28)
    )
    lotus_altar = bpy.context.active_object
    lotus_altar.data.materials.append(mat_gold)
    kali_objs.append(lotus_altar)

    # Torso (Dark Basalt Stone)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(kali_loc[0], kali_loc[1], kali_loc[2] + 1.1)
    )
    torso = bpy.context.active_object
    torso.scale = (0.32, 0.2, 0.45)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_black_stone)
    kali_objs.append(torso)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.18, location=(kali_loc[0], kali_loc[1], kali_loc[2] + 1.62)
    )
    head = bpy.context.active_object
    head.data.materials.append(mat_black_stone)
    kali_objs.append(head)

    # Golden Tongue protruding (classic Kalighat iconography)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(kali_loc[0], kali_loc[1] - 0.2, kali_loc[2] + 1.55)
    )
    tongue = bpy.context.active_object
    tongue.scale = (0.06, 0.12, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    tongue.data.materials.append(mat_gold)
    kali_objs.append(tongue)

    # Third eye on forehead
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.035, location=(kali_loc[0], kali_loc[1] - 0.17, kali_loc[2] + 1.68)
    )
    third_eye = bpy.context.active_object
    third_eye.data.materials.append(mat_red)
    kali_objs.append(third_eye)

    # Golden Mukuta (Tall Radiant Bengal Crown)
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.25, radius2=0.05, depth=0.55,
        location=(kali_loc[0], kali_loc[1], kali_loc[2] + 2.0)
    )
    crown = bpy.context.active_object
    crown.data.materials.append(mat_gold)
    kali_objs.append(crown)

    # Radiant Golden Prabhavali (Halo / Aura behind head)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.6, depth=0.04,
        location=(kali_loc[0], kali_loc[1] + 0.1, kali_loc[2] + 1.65)
    )
    halo = bpy.context.active_object
    halo.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    halo.data.materials.append(mat_gold)
    kali_objs.append(halo)

    # 4 Arms
    # Upper Left: Khadga / Scimitar
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.6,
        location=(kali_loc[0] - 0.5, kali_loc[1], kali_loc[2] + 1.45)
    )
    arm_ul = bpy.context.active_object
    arm_ul.rotation_euler = (0, -0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ul.data.materials.append(mat_black_stone)
    kali_objs.append(arm_ul)
    # Scimitar blade
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(kali_loc[0] - 0.75, kali_loc[1], kali_loc[2] + 1.8)
    )
    blade = bpy.context.active_object
    blade.scale = (0.04, 0.08, 0.35)
    bpy.ops.object.transform_apply(scale=True)
    blade.data.materials.append(mat_gold)
    kali_objs.append(blade)

    # Lower Left: Severed head / Asura munda
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.5,
        location=(kali_loc[0] - 0.45, kali_loc[1], kali_loc[2] + 0.95)
    )
    arm_ll = bpy.context.active_object
    arm_ll.rotation_euler = (0, -0.3, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ll.data.materials.append(mat_black_stone)
    kali_objs.append(arm_ll)

    # Upper Right: Abhaya mudra (protection)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.55,
        location=(kali_loc[0] + 0.5, kali_loc[1], kali_loc[2] + 1.45)
    )
    arm_ur = bpy.context.active_object
    arm_ur.rotation_euler = (0, 0.6, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ur.data.materials.append(mat_black_stone)
    kali_objs.append(arm_ur)

    # Lower Right: Varada mudra (boon-giving)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.5,
        location=(kali_loc[0] + 0.45, kali_loc[1], kali_loc[2] + 0.95)
    )
    arm_lr = bpy.context.active_object
    arm_lr.rotation_euler = (0, 0.3, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_lr.data.materials.append(mat_black_stone)
    kali_objs.append(arm_lr)

    # Legs (Standing on Shiva)
    for sx in [-0.14, 0.14]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.07, depth=0.65,
            location=(kali_loc[0] + sx, kali_loc[1], kali_loc[2] + 0.6)
        )
        leg = bpy.context.active_object
        leg.data.materials.append(mat_black_stone)
        kali_objs.append(leg)

    # Garland of Hibiscus (Mundamala / Jaba Phool)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.35, minor_radius=0.06,
        location=(kali_loc[0], kali_loc[1] - 0.08, kali_loc[2] + 1.05)
    )
    mala = bpy.context.active_object
    mala.data.materials.append(mat_garland)
    kali_objs.append(mala)

    # Red silk sash
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.34, depth=0.3,
        location=(kali_loc[0], kali_loc[1], kali_loc[2] + 0.8)
    )
    sash = bpy.context.active_object
    sash.data.materials.append(mat_silk)
    kali_objs.append(sash)

    # Join into single Deity object named "Deity_Kalika"
    bpy.ops.object.select_all(action='DESELECT')
    for o in kali_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = kali_objs[0]
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = "Deity_Kalika"

    # 8. Deepams inside Garbhagriha
    deepam1 = geom.create_deepam(
        name="Deepam_1",
        location=(-1.4, 13.5, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    deepam2 = geom.create_deepam(
        name="Deepam_2",
        location=(1.4, 13.5, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_3",
        location=(-1.4, 15.2, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_4",
        location=(1.4, 15.2, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )

    # 9. Priest near sanctum door (standing reverently to the right of doorway)
    priest = geom.create_human_figure(
        name="Priest",
        location=(1.5, 10.5, 0.6),
        height=1.75,
        mat_skin=mat_skin,
        mat_cloth=mat_cloth
    )

    # 10. Mandapa (Natmandir spacious pillared hall in front of Garbhagriha)
    # Center at (0, 5.5, 0.6), size 8.5 x 7.5, height 3.8
    mandapa_objs = geom.create_mandapa(
        name="Mandapa_Hall",
        location=(0.0, 5.5, 0.6),
        width=8.5,
        depth=7.5,
        height=3.8,
        pillar_count_x=4,
        pillar_count_y=3,
        mat_stone=mat_marble,
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

    # 11. Ghanta (Hanging Brass Bell at Natmandir entrance)
    ghanta = geom.create_hanging_bell(
        name="Ghanta",
        location=(0.0, 1.8, 3.2),
        mat_brass=mat_brass,
        scale=1.2
    )

    # 12. Spawn Point (facing North towards temple entrance)
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0.0, -8.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # 13. Bhairava Shrine (Nakuleshwar Mahadev on West side)
    nak_objs = []
    nak_loc = (-10.5, 7.0, 0.0)
    # Base
    bpy.ops.mesh.primitive_cube_add(size=2, location=(nak_loc[0], nak_loc[1], nak_loc[2] + 0.3))
    n_base = bpy.context.active_object
    n_base.scale = (1.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    n_base.data.materials.append(mat_terracotta)
    nak_objs.append(n_base)
    # 4 Corner Pillars
    for dx, dy in [(-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)]:
        p = geom.create_pillar(f"N_Pillar_{dx}_{dy}", (nak_loc[0] + dx, nak_loc[1] + dy, nak_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_terracotta)
        nak_objs.append(p)
    # Chala style roof for shrine
    bpy.ops.mesh.primitive_cube_add(size=2, location=(nak_loc[0], nak_loc[1], nak_loc[2] + 2.9))
    n_roof = bpy.context.active_object
    n_roof.scale = (1.6, 1.6, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    n_roof.data.materials.append(mat_terracotta)
    nak_objs.append(n_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.2, radius2=0.2, depth=1.4, location=(nak_loc[0], nak_loc[1], nak_loc[2] + 3.8))
    n_cone = bpy.context.active_object
    n_cone.data.materials.append(mat_terracotta)
    nak_objs.append(n_cone)
    # Shiva Linga / Nakuleshwar Mahadev idol
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.2, depth=0.5, location=(nak_loc[0], nak_loc[1], nak_loc[2] + 0.85))
    linga = bpy.context.active_object
    linga.data.materials.append(mat_black_stone)
    nak_objs.append(linga)
    # Join into Bhairava_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in nak_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = nak_objs[0]
    bpy.ops.object.join()
    bhairava_shrine = bpy.context.active_object
    bhairava_shrine.name = "Bhairava_Shrine"

    # 14. Ganesha Shrine (on West side near entrance)
    gan_objs = []
    gan_loc = (-10.5, 12.5, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(gan_loc[0], gan_loc[1], gan_loc[2] + 0.3))
    g_base = bpy.context.active_object
    g_base.scale = (1.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    g_base.data.materials.append(mat_terracotta)
    gan_objs.append(g_base)
    for dx, dy in [(-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)]:
        p = geom.create_pillar(f"G_Pillar_{dx}_{dy}", (gan_loc[0] + dx, gan_loc[1] + dy, gan_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_terracotta)
        gan_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(gan_loc[0], gan_loc[1], gan_loc[2] + 2.9))
    g_roof = bpy.context.active_object
    g_roof.scale = (1.6, 1.6, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    g_roof.data.materials.append(mat_terracotta)
    gan_objs.append(g_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.2, radius2=0.2, depth=1.4, location=(gan_loc[0], gan_loc[1], gan_loc[2] + 3.8))
    g_cone = bpy.context.active_object
    g_cone.data.materials.append(mat_terracotta)
    gan_objs.append(g_cone)
    # Ganesha Murti
    g_murti = geom.create_deity_figure(name="Ganesha_Murti", location=(gan_loc[0], gan_loc[1], gan_loc[2] + 0.6), height=1.1, arms=4, mat_body=mat_terracotta, mat_ornament=mat_gold)
    gan_objs.append(g_murti)
    # Join into Ganesha_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in gan_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = gan_objs[0]
    bpy.ops.object.join()
    ganesha_shrine = bpy.context.active_object
    ganesha_shrine.name = "Ganesha_Shrine"

    # 15. Prakara Wall with Bengal terracotta cornices
    prakara_objs = geom.create_prakara_wall(
        name="Prakara_Kalighat",
        center=(0, 7.0, 0),
        width=36.0,
        depth=32.0,
        wall_height=3.2,
        wall_thickness=0.55,
        mat=mat_terracotta,
        gate_width=4.0,
        gate_sides=["S"]
    )

    # 16. Sacred Banyan Tree (Harkath Tala)
    mat_bark = mats.create_tree_bark("Banyan_Bark")
    mat_leaves = mats.create_green_foliage("Banyan_Leaves")
    geom.create_tree("Sacred_Banyan_Harkath", (-12.0, -2.0, 0.0), height=6.0, mat_trunk=mat_bark, mat_leaves=mat_leaves)

    # 17. Export GLB
    export_path = Path(__file__).resolve().parent.parent / "godot" / "assets" / "models" / "kalighat_kshetra_full.glb"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    geom.export_glb(str(export_path))
    print(f"Kalighat export complete: {export_path}")

if __name__ == "__main__":
    build_kalighat()
