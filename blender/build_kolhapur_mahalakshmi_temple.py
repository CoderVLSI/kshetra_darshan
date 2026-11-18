"""
Kolhapur Mahalakshmi (Ambabai) Temple (Kolhapur, Maharashtra)
Authentic Hemadpanti Stellate Architecture & Exact Canonical Ambabai Murti

Iconography:
- Hemadpanti 16-pointed star-shaped stellate plinth of black basalt stone (Karveer)
- Deep ratha offsets with multi-tiered stone cornice bands
- Preceding Garuda Mandapa with tall brass Garuda Stambha & Kurma Mandapa with carved basalt pillars
- Exact 4-armed Ambabai Murti:
  * Black stone (basalt) standing upright on pedestal
  * Lion mount (Vahana) standing behind
  * Crown with Naga (cobra) hood and embedded Shiva Lingam
  * 4 Arms & Ayudhas:
    1. Lower Right: Matulunga (citron fruit)
    2. Upper Right: Kaumodaki Gada (heavy mace touching downward)
    3. Upper Left: Khetaka (warrior shield)
    4. Lower Left: Panapatra (sacred bowl/vessel)
  * Carved Prabhavali arch framing the deity
"""
import os
import sys
import math

blender_dir = os.path.dirname(os.path.abspath(__file__))
if blender_dir not in sys.path:
    sys.path.insert(0, blender_dir)

import bpy
import bmesh
from mathutils import Matrix, Vector
import common_materials as mats
import common_geometry as geom

def build_authentic_kolhapur():
    geom.clear_scene()

    # Materials
    mat_basalt_black = mats.create_black_stone("Basalt_Black_Polished", color=(0.08, 0.07, 0.07, 1.0), roughness=0.35)
    mat_basalt_rough = mats.create_black_stone("Basalt_Stone_Molded", color=(0.14, 0.13, 0.12, 1.0), roughness=0.65)
    mat_paving = mats.create_granite_stone("Courtyard_Basalt", color=(0.28, 0.26, 0.24, 1.0))
    mat_gold = mats.create_gold_metal("Deity_Gold_Ornaments", color=(0.92, 0.75, 0.20, 1.0))
    mat_brass = mats.create_brass_metal("Garuda_Stambha_Brass", color=(0.82, 0.62, 0.14, 1.0))
    mat_silver = mats.create_white_marble("Silver_Accents", color=(0.90, 0.90, 0.92, 1.0))
    mat_silk_sari = mats.create_red_silk("Ambabai_Pitambari", color=(0.95, 0.60, 0.05, 1.0)) # Golden-orange pitambari silk
    mat_kumkum = mats.create_kumkum_red("Kumkum_Vermilion", color=(0.88, 0.08, 0.05, 1.0))
    mat_flame = mats.create_flame_emission("Sanctum_Flame", color=(1.0, 0.65, 0.15, 1.0), strength=14.0)
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Dhoti")
    mat_wood = mats.create_wood("Garuda_Mandap_Wood", color=(0.25, 0.15, 0.08, 1.0))
    mat_tree_bark = mats.create_tree_bark("Tree_Bark")
    mat_foliage = mats.create_green_foliage("Tree_Leaves")

    # 1. Main Courtyard Ground (Z = 0)
    geom.create_ground_plane(name="Ground_Main", size=75, mat=mat_paving)

    # 2. Hemadpanti 16-Pointed Star-Shaped Stellate Plinth (Adhisthana)
    # Built by overlapping square platforms rotated at 22.5, 45, 67.5 degrees
    star_center = (0.0, 6.0, 0.0)
    plinth_h = 1.0
    for rot_deg in [0, 22.5, 45, 67.5]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(star_center[0], star_center[1], plinth_h/2))
        star_sq = bpy.context.active_object
        star_sq.scale = (12.0, 12.0, plinth_h)
        star_sq.rotation_euler = (0, 0, math.radians(rot_deg))
        star_sq.name = f"Hemadpanti_Stellate_Plinth_{rot_deg}"
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        star_sq.data.materials.append(mat_basalt_rough)

    # =========================================================================
    # PRECEDING HALL: GARUDA MANDAPA & KURMA MANDAPA
    # The famous open hall where the brass Garuda Pillar stands in front of sanctum
    # =========================================================================
    garuda_center = (0.0, -4.5, plinth_h)
    gm_w, gm_d, gm_h = 10.0, 8.0, 4.0

    # Garuda Mandapa Floor
    bpy.ops.mesh.primitive_cube_add(size=1, location=(garuda_center[0], garuda_center[1], plinth_h + 0.1))
    gmf = bpy.context.active_object
    gmf.scale = (gm_w, gm_d, 0.2)
    gmf.name = "Garuda_Mandapa_Floor"
    bpy.ops.object.transform_apply(scale=True)
    gmf.data.materials.append(mat_basalt_black)

    # A physical approach connects the courtyard to the 1.2m-high hall floor.
    # Six 20cm risers replace the old unwalkable sheer edge. Each tread is
    # filled down to ground, rather than being a suspended thin slab.
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(garuda_center[0], garuda_center[1], plinth_h / 2))
    hall_base = bpy.context.active_object
    hall_base.name = "Garuda_Mandapa_Foundation"
    hall_base.scale = (gm_w, gm_d, plinth_h)
    bpy.ops.object.transform_apply(scale=True)
    hall_base.data.materials.append(mat_basalt_rough)
    approach_count, approach_tread = 6, 0.4
    approach_rise = (plinth_h + 0.2) / approach_count
    hall_front = garuda_center[1] - gm_d / 2
    for index in range(approach_count):
        step_height = (index + 1) * approach_rise
        step_y = hall_front - (approach_count - index - 0.5) * approach_tread
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(0, step_y, step_height / 2))
        step = bpy.context.active_object
        step.name = f"Garuda_Approach_Step_{index + 1}"
        step.scale = (4.2, approach_tread, step_height)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(mat_basalt_rough)

    # Carved Black Basalt Pillars with Yali brackets
    for px in [-4.0, -1.33, 1.33, 4.0]:
        for py in [-7.5, -4.5, -1.5]:
            geom.create_pillar(f"Garuda_Pillar_{px}_{py}", (px, py, plinth_h + 0.2), height=gm_h, radius=0.24, mat=mat_basalt_rough, style="octagonal")

    # Wooden Carved Ceiling Slab of Garuda Mandapa
    bpy.ops.mesh.primitive_cube_add(size=1, location=(garuda_center[0], garuda_center[1], plinth_h + gm_h + 0.2))
    gmr = bpy.context.active_object
    gmr.scale = (gm_w + 0.6, gm_d + 0.6, 0.3)
    gmr.name = "Garuda_Mandapa_Roof"
    bpy.ops.object.transform_apply(scale=True)
    gmr.data.materials.append(mat_wood)

    # Brass Garuda Stambha (The iconic Pillar of Garuda in front of Ambabai)
    stambha_loc = (0.0, -4.5, plinth_h + 0.2)
    # High base
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=0.6, location=(stambha_loc[0], stambha_loc[1], stambha_loc[2] + 0.3))
    stambha_base = bpy.context.active_object
    stambha_base.name = "Garuda_Stambha_Base"
    stambha_base.data.materials.append(mat_brass)

    # Tall brass column
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=3.6, location=(stambha_loc[0], stambha_loc[1], stambha_loc[2] + 0.6 + 1.8))
    stambha_col = bpy.context.active_object
    stambha_col.name = "Garuda_Stambha_Column"
    stambha_col.data.materials.append(mat_brass)

    # Kneeling Garuda statue on top of pillar facing sanctum
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(stambha_loc[0], stambha_loc[1], stambha_loc[2] + 0.6 + 3.6 + 0.25))
    garuda_statue = bpy.context.active_object
    garuda_statue.name = "Preceding_Shrine_Garuda"
    garuda_statue.data.materials.append(mat_brass)

    # Mandapa composite node for Godot inspector
    mandapa_node = bpy.data.objects.new("Mandapa", None)
    bpy.context.scene.collection.objects.link(mandapa_node)
    mandapa_node.location = (garuda_center[0], garuda_center[1], plinth_h)

    # Hanging Brass Ghanta at Mandapa entrance
    geom.create_hanging_bell("Ghanta", (0.0, -8.0, plinth_h + 3.2), mat_brass=mat_brass, scale=1.3)

    # =========================================================================
    # SANCTUM: STAR-SHAPED GARBHAGRIHA & SHIKHARA
    # With deep recessed ratha offsets aligned for Kiranotsav sun rays
    # =========================================================================
    garb_center = (0.0, 7.5, plinth_h)
    garb_w, garb_d, garb_h = 7.0, 7.0, 4.5

    # Hollow Sanctum Chamber with Doorway
    wt = 0.5 # wall thickness
    # Back Wall (North)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, garb_center[1] + garb_d/2 - wt/2, plinth_h + garb_h/2))
    w_back = bpy.context.active_object
    w_back.scale = (garb_w, wt, garb_h)
    w_back.name = "Garbhagriha_Wall_Back"
    bpy.ops.object.transform_apply(scale=True)
    w_back.data.materials.append(mat_basalt_rough)

    # Left Wall (West)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-garb_w/2 + wt/2, garb_center[1], plinth_h + garb_h/2))
    w_left = bpy.context.active_object
    w_left.scale = (wt, garb_d, garb_h)
    w_left.name = "Garbhagriha_Wall_Left"
    bpy.ops.object.transform_apply(scale=True)
    w_left.data.materials.append(mat_basalt_rough)

    # Right Wall (East)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(garb_w/2 - wt/2, garb_center[1], plinth_h + garb_h/2))
    w_right = bpy.context.active_object
    w_right.scale = (wt, garb_d, garb_h)
    w_right.name = "Garbhagriha_Wall_Right"
    bpy.ops.object.transform_apply(scale=True)
    w_right.data.materials.append(mat_basalt_rough)

    # Front Wall (South) flanking 2.2m central doorway
    side_w = (garb_w - 2.2) / 2.0
    for sx, name in [(-garb_w/2 + side_w/2, "Garbhagriha_Front_L"), (garb_w/2 - side_w/2, "Garbhagriha_Front_R")]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, garb_center[1] - garb_d/2 + wt/2, plinth_h + garb_h/2))
        w_front = bpy.context.active_object
        w_front.scale = (side_w, wt, garb_h)
        w_front.name = name
        bpy.ops.object.transform_apply(scale=True)
        w_front.data.materials.append(mat_basalt_rough)

    # Lintel over South doorway
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, garb_center[1] - garb_d/2 + wt/2, plinth_h + garb_h - 0.45))
    door_lintel = bpy.context.active_object
    door_lintel.scale = (2.4, wt + 0.1, 0.9)
    door_lintel.name = "Garbhagriha_Door_Lintel"
    bpy.ops.object.transform_apply(scale=True)
    door_lintel.data.materials.append(mat_basalt_black)

    # Ceiling slab of Garbhagriha
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, garb_center[1], plinth_h + garb_h + 0.1))
    garb_ceil = bpy.context.active_object
    garb_ceil.scale = (garb_w + 0.4, garb_d + 0.4, 0.2)
    garb_ceil.name = "Garbhagriha_Ceiling"
    bpy.ops.object.transform_apply(scale=True)
    garb_ceil.data.materials.append(mat_basalt_rough)

    # Join Garbhagriha walls & ceiling into the main "Garbhagriha" node
    garb_parts = [w_back, w_left, w_right, door_lintel, garb_ceil]
    for obj in bpy.data.objects:
        if obj.name.startswith("Garbhagriha_Front"):
            garb_parts.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for p in garb_parts: p.select_set(True)
    bpy.context.view_layer.objects.active = w_back
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # Stellate corner buttress offsets (Hemadpanti star facets on exterior walls)
    for cx, cy, rot in [(-3.2, 7.5+3.2, 45), (3.2, 7.5+3.2, -45), (-3.2, 7.5-3.2, -45), (3.2, 7.5-3.2, 45)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, plinth_h + garb_h/2))
        cw = bpy.context.active_object
        cw.scale = (0.8, 0.8, garb_h)
        cw.rotation_euler = (0, 0, math.radians(rot))
        cw.name = f"Ratha_Offset_{cx}_{cy}"
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        cw.data.materials.append(mat_basalt_rough)

    # Multi-Tiered Hemadpanti Shikhara Tower
    shikhara_base_z = plinth_h + garb_h
    tiers = 7
    s_h = 9.0
    for i in range(tiers):
        t = i / float(tiers - 1)
        sw = (garb_w / 2) * (1.0 - t * 0.65)
        sz = shikhara_base_z + i * (s_h / tiers) + (s_h / tiers)/2
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, garb_center[1], sz))
        tier = bpy.context.active_object
        tier.scale = (sw, sw, (s_h / tiers)/2)
        tier.name = f"Hemadpanti_Shikhara_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        tier.data.materials.append(mat_basalt_rough)

    # Shikhara Amalaka Disc and Gold Kalasha
    bpy.ops.mesh.primitive_torus_add(major_radius=1.3, minor_radius=0.35, location=(0, garb_center[1], shikhara_base_z + s_h + 0.35))
    amalaka = bpy.context.active_object
    amalaka.name = "Kolhapur_Amalaka"
    amalaka.data.materials.append(mat_basalt_black)

    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.28, radius2=0.04, depth=1.0, location=(0, garb_center[1], shikhara_base_z + s_h + 0.95))
    kalasha = bpy.context.active_object
    kalasha.name = "Kolhapur_Kalasha"
    kalasha.data.materials.append(mat_gold)

    # =========================================================================
    # THE AUTHENTIC DEITY: EXACT CANONICAL MAHALAKSHMI (AMBABAI) MURTI
    # 4-armed standing black stone murti with Lion vahana, Naga hood with Shiva Linga,
    # Matulunga fruit, Kaumodaki Gada, Khetaka shield, and Panapatra bowl
    # =========================================================================
    deity_loc = (0.0, 8.5, plinth_h + 0.2)
    s = 1.0  # scale

    deity_parts = []

    # 1. High Lotus/Stone Pedestal (Pitha)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55*s, depth=0.25*s, location=(deity_loc[0], deity_loc[1], deity_loc[2] + 0.125*s))
    pedestal = bpy.context.active_object
    pedestal.name = "Ambabai_Pedestal"
    pedestal.data.materials.append(mat_basalt_black)
    deity_parts.append(pedestal)

    # 2. Lion Mount (Vahana) standing directly behind the Goddess
    bpy.ops.mesh.primitive_cube_add(size=2, location=(deity_loc[0], deity_loc[1] + 0.25*s, deity_loc[2] + 0.45*s))
    lion_body = bpy.context.active_object
    lion_body.scale = (0.35*s, 0.45*s, 0.30*s)
    lion_body.name = "Ambabai_Lion_Vahana"
    bpy.ops.object.transform_apply(scale=True)
    lion_body.data.materials.append(mat_basalt_black)
    deity_parts.append(lion_body)

    # Lion head with mane
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18*s, location=(deity_loc[0] + 0.28*s, deity_loc[1] + 0.20*s, deity_loc[2] + 0.65*s))
    lion_head = bpy.context.active_object
    lion_head.name = "Lion_Head"
    lion_head.data.materials.append(mat_basalt_black)
    deity_parts.append(lion_head)

    # 3. Devi Lower Body (Standing upright, draped in golden pitambari silk)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.22*s, depth=0.70*s, location=(deity_loc[0], deity_loc[1], deity_loc[2] + 0.60*s))
    lower_body = bpy.context.active_object
    lower_body.name = "Ambabai_Lower_Body"
    lower_body.data.materials.append(mat_silk_sari)
    deity_parts.append(lower_body)

    # 4. Devi Torso & Chest with jeweled necklaces and kavacha
    bpy.ops.mesh.primitive_cube_add(size=2, location=(deity_loc[0], deity_loc[1], deity_loc[2] + 1.15*s))
    torso = bpy.context.active_object
    torso.scale = (0.22*s, 0.14*s, 0.28*s)
    torso.name = "Ambabai_Torso"
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_basalt_black)
    deity_parts.append(torso)

    # Gold Haras / Necklaces
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14*s, minor_radius=0.03*s, location=(deity_loc[0], deity_loc[1] - 0.04*s, deity_loc[2] + 1.25*s))
    necklace = bpy.context.active_object
    necklace.name = "Ambabai_Gold_Necklace"
    necklace.data.materials.append(mat_gold)
    deity_parts.append(necklace)

    # 5. Devi Divine Face with serene expression
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12*s, location=(deity_loc[0], deity_loc[1], deity_loc[2] + 1.48*s))
    face = bpy.context.active_object
    face.name = "Ambabai_Face"
    face.data.materials.append(mat_basalt_black)
    deity_parts.append(face)

    # Kumkum Tilak on Forehead
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015*s, location=(deity_loc[0], deity_loc[1] - 0.12*s, deity_loc[2] + 1.52*s))
    tilak = bpy.context.active_object
    tilak.name = "Ambabai_Kumkum"
    tilak.data.materials.append(mat_kumkum)
    deity_parts.append(tilak)

    # 6. Kiritamukuta (Crown) with Shiva Lingam embedded and Naga (Cobra) hood
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12*s, radius2=0.04*s, depth=0.28*s, location=(deity_loc[0], deity_loc[1], deity_loc[2] + 1.70*s))
    crown = bpy.context.active_object
    crown.name = "Ambabai_Crown"
    crown.data.materials.append(mat_gold)
    deity_parts.append(crown)

    # Embedded Shiva Lingam on top of crown
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.04*s, depth=0.10*s, location=(deity_loc[0], deity_loc[1], deity_loc[2] + 1.88*s))
    crown_lingam = bpy.context.active_object
    crown_lingam.name = "Crown_Shiva_Lingam"
    crown_lingam.data.materials.append(mat_basalt_black)
    deity_parts.append(crown_lingam)

    # Five-headed Naga (Cobra) Hood spreading over the crown
    bpy.ops.mesh.primitive_cube_add(size=2, location=(deity_loc[0], deity_loc[1] + 0.05*s, deity_loc[2] + 1.95*s))
    naga_hood = bpy.context.active_object
    naga_hood.scale = (0.24*s, 0.06*s, 0.15*s)
    naga_hood.name = "Naga_Cobra_Hood"
    bpy.ops.object.transform_apply(scale=True)
    naga_hood.data.materials.append(mat_gold)
    deity_parts.append(naga_hood)

    # 7. THE 4 ARMS & EXACT AYUDHAS:
    # --- Arm 1: Lower Right - Matulunga (Citron Fruit) ---
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035*s, depth=0.32*s, location=(deity_loc[0] + 0.28*s, deity_loc[1] - 0.05*s, deity_loc[2] + 1.05*s))
    arm_lr = bpy.context.active_object
    arm_lr.rotation_euler = (0, math.radians(-35), 0)
    arm_lr.name = "Arm_Lower_Right"
    bpy.ops.object.transform_apply(rotation=True)
    arm_lr.data.materials.append(mat_basalt_black)
    deity_parts.append(arm_lr)

    # Matulunga (Citron Fruit) in Lower Right Hand
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055*s, location=(deity_loc[0] + 0.36*s, deity_loc[1] - 0.10*s, deity_loc[2] + 0.90*s))
    matulunga = bpy.context.active_object
    matulunga.name = "Ayudha_Matulunga_Fruit"
    matulunga.data.materials.append(mat_gold)
    deity_parts.append(matulunga)

    # --- Arm 2: Upper Right - Kaumodaki Gada (Heavy Mace touching downward) ---
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035*s, depth=0.35*s, location=(deity_loc[0] + 0.32*s, deity_loc[1], deity_loc[2] + 1.25*s))
    arm_ur = bpy.context.active_object
    arm_ur.rotation_euler = (0, math.radians(40), 0)
    arm_ur.name = "Arm_Upper_Right"
    bpy.ops.object.transform_apply(rotation=True)
    arm_ur.data.materials.append(mat_basalt_black)
    deity_parts.append(arm_ur)

    # Kaumodaki Gada (Heavy Mace shaft + ribbed head touching pedestal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.025*s, depth=1.0*s, location=(deity_loc[0] + 0.48*s, deity_loc[1], deity_loc[2] + 0.825*s))
    gada_shaft = bpy.context.active_object
    gada_shaft.name = "Ayudha_Gada_Shaft"
    gada_shaft.data.materials.append(mat_gold)
    deity_parts.append(gada_shaft)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075*s, location=(deity_loc[0] + 0.48*s, deity_loc[1], deity_loc[2] + 0.325*s))
    gada_head = bpy.context.active_object
    gada_head.name = "Ayudha_Kaumodaki_Gada"
    gada_head.data.materials.append(mat_gold)
    deity_parts.append(gada_head)

    # --- Arm 3: Upper Left - Khetaka (Warrior Shield) ---
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035*s, depth=0.35*s, location=(deity_loc[0] - 0.32*s, deity_loc[1], deity_loc[2] + 1.25*s))
    arm_ul = bpy.context.active_object
    arm_ul.rotation_euler = (0, math.radians(-40), 0)
    arm_ul.name = "Arm_Upper_Left"
    bpy.ops.object.transform_apply(rotation=True)
    arm_ul.data.materials.append(mat_basalt_black)
    deity_parts.append(arm_ul)

    # Khetaka (Circular warrior shield with central gold boss)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.18*s, depth=0.04*s, location=(deity_loc[0] - 0.46*s, deity_loc[1] - 0.05*s, deity_loc[2] + 1.25*s))
    khetaka = bpy.context.active_object
    khetaka.rotation_euler = (math.radians(90), 0, 0)
    khetaka.name = "Ayudha_Khetaka_Shield"
    bpy.ops.object.transform_apply(rotation=True)
    khetaka.data.materials.append(mat_silver)
    deity_parts.append(khetaka)

    # --- Arm 4: Lower Left - Panapatra (Sacred Bowl / Cup of Nectar) ---
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035*s, depth=0.32*s, location=(deity_loc[0] - 0.28*s, deity_loc[1] - 0.05*s, deity_loc[2] + 1.05*s))
    arm_ll = bpy.context.active_object
    arm_ll.rotation_euler = (0, math.radians(35), 0)
    arm_ll.name = "Arm_Lower_Left"
    bpy.ops.object.transform_apply(rotation=True)
    arm_ll.data.materials.append(mat_basalt_black)
    deity_parts.append(arm_ll)

    # Panapatra / Chashaka Bowl in hand
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.05*s, depth=0.06*s, location=(deity_loc[0] - 0.36*s, deity_loc[1] - 0.10*s, deity_loc[2] + 0.90*s))
    panapatra = bpy.context.active_object
    panapatra.name = "Ayudha_Panapatra_Bowl"
    panapatra.data.materials.append(mat_gold)
    deity_parts.append(panapatra)

    # 8. Ornate Stone Prabhavali (Arch) with Makaras framing the Murti
    bpy.ops.mesh.primitive_torus_add(major_radius=0.75*s, minor_radius=0.08*s, location=(deity_loc[0], deity_loc[1] + 0.10*s, deity_loc[2] + 1.35*s))
    prabhavali = bpy.context.active_object
    prabhavali.scale = (1.0, 0.2, 1.3)
    prabhavali.name = "Prabhavali_Aureole_Arch"
    bpy.ops.object.transform_apply(scale=True)
    prabhavali.data.materials.append(mat_basalt_black)
    deity_parts.append(prabhavali)

    # Join all into single official node "Deity_Mahalakshmi"
    bpy.ops.object.select_all(action='DESELECT')
    for p in deity_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    deity_mahalakshmi = bpy.context.active_object
    deity_mahalakshmi.name = "Deity_Mahalakshmi"

    # Sacred Sanctum Deepams
    geom.create_deepam("Deepam_1", (deity_loc[0] - 1.2, deity_loc[1] - 0.6, plinth_h + 0.2), mat_brass=mat_brass, mat_flame=mat_flame)
    geom.create_deepam("Deepam_2", (deity_loc[0] + 1.2, deity_loc[1] - 0.6, plinth_h + 0.2), mat_brass=mat_brass, mat_flame=mat_flame)

    # Archaka Priest NPC
    geom.create_human_figure("Priest", (1.2, 4.5, plinth_h + 0.2), height=1.75, mat_skin=mat_skin, mat_cloth=mat_cloth)

    # Ganesha is in the approach halls between Garuda and the Sabha Mandapa.
    # The study stands clear of the central path to Ambabai.
    ganesha = bpy.data.objects.new("Ganesha_Mandapa_Anchor", None)
    bpy.context.scene.collection.objects.link(ganesha)
    ganesha.location = (-2.8, -1.05, plinth_h + .2)

    # Courtyard Trees
    for tx, ty in [(-18, -12), (-18, 14), (18, -12), (18, 14)]:
        geom.create_tree(f"Temple_Tree_{tx}_{ty}", (tx, ty, 0.0), height=7.0, mat_trunk=mat_tree_bark, mat_leaves=mat_foliage)

    # Spawn Point at Western Mahadwara entrance
    spawn = bpy.data.objects.new("Spawn_Point", None)
    bpy.context.scene.collection.objects.link(spawn)
    spawn.location = (0.0, -15.0, plinth_h)

    # The archaeological sketch plan shows two smaller sanctuaries opening
    # toward one another through the Sabha Mandapa, west of Ambabai's image.
    geom.create_mandapa(
        "Sabha_Mandapa", (0, 2.0, plinth_h), width=9.4, depth=5.3, height=3.8,
        pillar_count_x=3, pillar_count_y=2, mat_stone=mat_basalt_rough,
        mat_floor=mat_basalt_black, pillar_style="octagonal",
    )
    for name, side in [("Mahakali", -1), ("Mahasaraswati", 1)]:
        center = Vector((side * 7.0, 2.0, plinth_h))
        turn = Matrix.Translation(center) @ Matrix.Rotation(side * -math.pi / 2, 4, 'Z')
        walls = geom.create_garbhagriha(
            name, width=4.5, depth=4.6, wall_height=3.6, mat=mat_basalt_rough,
            door_width=1.9, door_height=2.7,
        )
        bpy.context.view_layer.update()
        for wall in walls:
            wall.matrix_world = turn @ wall.matrix_world
        geom.create_platform(name + "_Foundation", (center.x, center.y, 0),
                             size=(4.6, 4.5, plinth_h), mat=mat_basalt_rough)
        geom.create_platform(name + "_Roof", (center.x, center.y, plinth_h + 3.6),
                             size=(4.8, 4.8, .3), mat=mat_basalt_rough)
        geom.create_shikhara(name + "_Tower", (center.x, center.y, plinth_h + 3.9),
                            base_width=4.3, height=5.0, tiers=5, mat=mat_basalt_rough, style="nagara")
        shrine = bpy.data.objects.new(name + "_Sanctum_Anchor", None)
        bpy.context.scene.collection.objects.link(shrine)
        shrine.matrix_world = turn @ Matrix.Translation((0, 0.65, 0))

    # Convert builder axes to map axes. Mahadwar is west of the sanctuary.
    bpy.context.view_layer.update()
    westward = Matrix.Rotation(-math.pi / 2, 4, 'Z')
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world = westward @ obj.matrix_world

    # Export
    out_dir = os.path.join(os.path.dirname(blender_dir), "godot", "assets", "models")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "kolhapur_mahalakshmi_kshetra_full.glb")

    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
    )
    print(f"Authentic Kolhapur Mahalakshmi exported: {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    build_authentic_kolhapur()
