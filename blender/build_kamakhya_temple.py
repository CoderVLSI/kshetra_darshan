"""
Kamakhya Temple (Nilachal Hill, Guwahati, Assam)
Authentic Nilachala Architecture & Swayambhu Yoni Peetha

Accurate Architectural Chambers:
1. Bhogamandapa - Outer pillared hall
2. Natamandira - Grand dancing hall with curved Assamese calchala barrel-vault roof
3. Chalanta (Antarala) - Preceding shrine housing the movable murtis of Devi Kameshwari & Lord Kameshwara
4. Subterranean Cave Garbhagriha - Steep rock-cut stairs descending below ground into the natural bedrock cave
   housing the natural Yoni-peetha cleft, perennial spring water pool, red silk drape, silver crown, & hibiscus
5. Soaring Nilachala Beehive Dome - Vertical fluted facet ribs, miniature angashikharas, amalaka & 3 gold kalashas
6. Saubhagya Kunda - Sacred stepped tank with central pavilion
"""
import os
import sys
import math

blender_dir = os.path.dirname(os.path.abspath(__file__))
if blender_dir not in sys.path:
    sys.path.insert(0, blender_dir)

import bpy
import bmesh
from mathutils import Vector
import common_materials as mats
import common_geometry as geom

def build_authentic_kamakhya():
    geom.clear_scene()

    # Materials
    mat_laterite_wall = mats.create_red_laterite("Laterite_Wall", color=(0.58, 0.22, 0.14, 1.0))
    mat_laterite_carved = mats.create_red_laterite("Laterite_Carved", color=(0.48, 0.18, 0.11, 1.0))
    mat_bedrock = mats.create_black_stone("Cave_Bedrock", color=(0.10, 0.09, 0.08, 1.0), roughness=0.7)
    mat_paving = mats.create_granite_stone("Nilachal_Paving", color=(0.38, 0.34, 0.30, 1.0))
    mat_gold = mats.create_gold_metal("Kalasha_Gold", color=(0.88, 0.72, 0.22, 1.0))
    mat_silver = mats.create_white_marble("Crown_Silver", color=(0.85, 0.88, 0.90, 1.0), roughness=0.2)
    mat_brass = mats.create_brass_metal("Bell_Lamps_Brass", color=(0.80, 0.60, 0.15, 1.0))
    mat_silk_red = mats.create_red_silk("Kamakhya_Red_Silk", color=(0.85, 0.05, 0.05, 1.0))
    mat_hibiscus = mats.create_kumkum_red("Hibiscus_Red", color=(0.95, 0.08, 0.08, 1.0))
    mat_spring_water = mats.create_water("Spring_Water", color=(0.12, 0.30, 0.35, 0.85))
    mat_kunda_water = mats.create_water("Kunda_Water", color=(0.15, 0.38, 0.42, 0.85))
    mat_flame = mats.create_flame_emission("Deepam_Flame", color=(1.0, 0.65, 0.15, 1.0), strength=12.0)
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Cloth")
    mat_foliage = mats.create_green_foliage("Hill_Foliage")
    mat_bark = mats.create_tree_bark("Tree_Bark")

    # 1. Main Hill Courtyard Ground (Z = 0)
    geom.create_ground_plane(name="Ground_Main", size=75, mat=mat_paving)

    # 2. Nilachal Hill Complex Plinth (elevated temple foundation)
    geom.create_platform(name="Nilachal_Plinth", location=(0, 6.0, 0), size=(26.0, 36.0, 0.8), mat=mat_laterite_wall, steps=4)

    # =========================================================================
    # CHAMBER 1: NATAMANDIRA (Audience & Dance Hall)
    # Features authentic curved barrel-vaulted roof (Dochala/Calchala)
    # =========================================================================
    nata_center = (0.0, -4.0, 0.8)
    nata_w, nata_d, nata_h = 10.0, 8.0, 4.0

    # Natamandira Floor
    bpy.ops.mesh.primitive_cube_add(size=1, location=(nata_center[0], nata_center[1], nata_center[2] + 0.1))
    nf = bpy.context.active_object
    nf.scale = (nata_w, nata_d, 0.1)
    nf.name = "Natamandira_Floor"
    bpy.ops.object.transform_apply(scale=True)
    nf.data.materials.append(mat_paving)

    # Perimeter Carved Pillars
    for px in [-4.2, -1.4, 1.4, 4.2]:
        for py in [-7.2, -4.0, -0.8]:
            geom.create_pillar(f"Nata_Pillar_{px}_{py}", (px, py, nata_center[2] + 0.2), height=nata_h, radius=0.22, mat=mat_laterite_carved, style="square")

    # Enclosing Laterite Side Walls & Front Entrance Facade
    # West Wall
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-nata_w/2 + 0.2, nata_center[1], nata_center[2] + nata_h/2))
    w_wall = bpy.context.active_object
    w_wall.scale = (0.4, nata_d, nata_h)
    w_wall.name = "Nata_Wall_W"
    bpy.ops.object.transform_apply(scale=True)
    w_wall.data.materials.append(mat_laterite_wall)

    # East Wall
    bpy.ops.mesh.primitive_cube_add(size=1, location=(nata_w/2 - 0.2, nata_center[1], nata_center[2] + nata_h/2))
    e_wall = bpy.context.active_object
    e_wall.scale = (0.4, nata_d, nata_h)
    e_wall.name = "Nata_Wall_E"
    bpy.ops.object.transform_apply(scale=True)
    e_wall.data.materials.append(mat_laterite_wall)

    # South Facade flanking entrance portal (leaves 3.2m open gateway at center)
    for sx, name in [(-3.3, "Nata_Facade_SW"), (3.3, "Nata_Facade_SE")]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, nata_center[1] - nata_d/2 + 0.2, nata_center[2] + nata_h/2))
        facade_wall = bpy.context.active_object
        facade_wall.scale = (3.4, 0.4, nata_h)
        facade_wall.name = name
        bpy.ops.object.transform_apply(scale=True)
        facade_wall.data.materials.append(mat_laterite_wall)

    # Lintel Arch Beam over South Entrance Portal
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, nata_center[1] - nata_d/2 + 0.2, nata_center[2] + nata_h - 0.4))
    portal_lintel = bpy.context.active_object
    portal_lintel.scale = (3.4, 0.45, 0.8)
    portal_lintel.name = "Nata_Portal_Lintel"
    bpy.ops.object.transform_apply(scale=True)
    portal_lintel.data.materials.append(mat_laterite_carved)

    # Ceiling Architrave Slab resting flush on pillars and walls
    roof_base_z = nata_center[2] + nata_h
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, nata_center[1], roof_base_z + 0.1))
    ceiling_slab = bpy.context.active_object
    ceiling_slab.scale = (nata_w + 0.4, nata_d + 0.4, 0.2)
    ceiling_slab.name = "Natamandira_Ceiling_Slab"
    bpy.ops.object.transform_apply(scale=True)
    ceiling_slab.data.materials.append(mat_laterite_carved)

    # Authentic Assamese Calchala Curved Barrel-Vaulted Roof resting flush on ceiling slab
    vault_w = nata_w + 0.8  # 10.8m width (0.4m eaves overhang)
    vault_d = nata_d + 0.8  # 8.8m depth
    vault_h = 1.45          # 1.45m arched rise above base
    vault_z = roof_base_z + 0.2

    bm = bmesh.new()
    steps = 16
    front_verts = []
    # Bottom baseline
    front_verts.append(bm.verts.new((-vault_w/2, nata_center[1] - vault_d/2, vault_z)))
    front_verts.append(bm.verts.new((vault_w/2, nata_center[1] - vault_d/2, vault_z)))
    # Curved arch from right to left
    for k in range(steps, -1, -1):
        t = -1.0 + 2.0 * k / float(steps)
        vx = (vault_w / 2.0) * t
        vz = vault_z + vault_h * (1.0 - t * t)
        front_verts.append(bm.verts.new((vx, nata_center[1] - vault_d/2, vz)))

    face = bm.faces.new(front_verts)
    geom_extrude = bmesh.ops.extrude_face_region(bm, geom=[face])
    ext_verts = [v for v in geom_extrude['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, vault_d, 0), verts=ext_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    roof_mesh = bpy.data.meshes.new("Natamandira_Roof_Mesh")
    bm.to_mesh(roof_mesh)
    bm.free()

    nata_roof = bpy.data.objects.new("Natamandira_Roof", roof_mesh)
    bpy.context.scene.collection.objects.link(nata_roof)
    nata_roof.data.materials.append(mat_laterite_wall)

    # Ridge finials on Natamandira roof crest
    for ry in [-7.0, -4.0, -1.0]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, ry, vault_z + vault_h + 0.18))
        finial = bpy.context.active_object
        finial.name = f"Nata_Finial_{ry}"
        finial.data.materials.append(mat_gold)

    # Mandapa composite node for Godot inspector
    mandapa_node = bpy.data.objects.new("Mandapa", None)
    bpy.context.scene.collection.objects.link(mandapa_node)
    mandapa_node.location = (nata_center[0], nata_center[1], nata_center[2])

    # Hanging Brass Bell (Ghanta) at Natamandira entrance arch
    geom.create_hanging_bell("Ghanta", (0.0, -7.5, nata_center[2] + 3.2), mat_brass=mat_brass, scale=1.3)

    # =========================================================================
    # CHAMBER 2: CHALANTA (Antarala / Preceding Shrine)
    # Houses the movable murtis of Devi Kameshwari & Lord Kameshwara before the cave
    # =========================================================================
    chalanta_center = (0.0, 3.5, 0.8)
    chalanta_w, chalanta_d, chalanta_h = 7.0, 5.0, 4.2

    # Walls
    for side, pos, sc in [
        ("W", (-chalanta_w/2 + 0.2, chalanta_center[1], chalanta_center[2] + chalanta_h/2), (0.4, chalanta_d, chalanta_h)),
        ("E", (chalanta_w/2 - 0.2, chalanta_center[1], chalanta_center[2] + chalanta_h/2), (0.4, chalanta_d, chalanta_h)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        w = bpy.context.active_object
        w.scale = (sc[0], sc[1], sc[2])
        w.name = f"Chalanta_Wall_{side}"
        bpy.ops.object.transform_apply(scale=True)
        w.data.materials.append(mat_laterite_wall)

    # Preceding Shrine: Devi Kameshwari & Lord Kameshwara (The Chalanta Murti Altar)
    chalanta_altar_loc = (-2.0, 3.5, 0.8)
    altar_h = 0.5
    bpy.ops.mesh.primitive_cube_add(size=1, location=(chalanta_altar_loc[0], chalanta_altar_loc[1], 0.8 + altar_h/2))
    c_altar = bpy.context.active_object
    c_altar.scale = (1.8, 1.2, altar_h)
    c_altar.name = "Chalanta_Altar"
    bpy.ops.object.transform_apply(scale=True)
    c_altar.data.materials.append(mat_laterite_carved)

    # Movable Devi Kameshwari Murti on the Chalanta Altar (grounded firmly at Z = 1.30)
    geom.create_deity_figure("Preceding_Deity_Kameshwari", (chalanta_altar_loc[0] - 0.3, chalanta_altar_loc[1], 0.8 + altar_h), height=1.1, arms=4, mat_body=mat_gold, mat_ornament=mat_brass)

    # Shiva Lingam for Lord Kameshwara beside Devi
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.14, depth=0.35, location=(chalanta_altar_loc[0] + 0.45, chalanta_altar_loc[1], 0.8 + altar_h + 0.175))
    kamesh_lingam = bpy.context.active_object
    kamesh_lingam.name = "Preceding_Shiva_Kameshwara"
    kamesh_lingam.data.materials.append(mat_bedrock)

    # Lamps beside Chalanta Altar
    geom.create_deepam("Chalanta_Deepam_L", (chalanta_altar_loc[0] - 1.1, chalanta_altar_loc[1], 0.8 + altar_h), mat_brass=mat_brass, mat_flame=mat_flame)
    geom.create_deepam("Chalanta_Deepam_R", (chalanta_altar_loc[0] + 1.1, chalanta_altar_loc[1], 0.8 + altar_h), mat_brass=mat_brass, mat_flame=mat_flame)

    # =========================================================================
    # CHAMBER 3 & 4: SUBTERRANEAN CAVE GARBHAGRIHA & DESCENT STEPS
    # The actual sacred Swayambhu Yoni Peetha in the underground bedrock cave
    # =========================================================================
    cave_floor_z = -2.2  # Subterranean depth below ground
    sanctum_center = (0.0, 11.5, cave_floor_z)

    # Rock-cut descent stairs from Chalanta (Z = 0.8 down to Z = -2.2)
    step_count = 10
    step_dz = (0.8 - cave_floor_z) / step_count
    step_dy = 3.5 / step_count
    for s in range(step_count):
        sz = 0.8 - (s + 1) * step_dz + step_dz/2
        sy = 6.0 + s * step_dy
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, sy, sz))
        step = bpy.context.active_object
        step.scale = (2.2, step_dy, step_dz)
        step.name = f"Cave_Stairs_Step_{s+1}"
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(mat_bedrock)

    # Underground Cave Chamber Walls & Floor
    cave_w, cave_d, cave_h = 7.0, 7.0, 4.0
    # Cave Floor
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sanctum_center[0], sanctum_center[1] + 1.5, cave_floor_z + 0.1))
    c_floor = bpy.context.active_object
    c_floor.scale = (cave_w, cave_d, 0.2)
    c_floor.name = "Cave_Garbhagriha_Floor"
    bpy.ops.object.transform_apply(scale=True)
    c_floor.data.materials.append(mat_bedrock)

    # Cave Rock Walls (rough natural rock texture enclosing subterranean sanctum)
    for side, pos, sc in [
        ("N_Back", (0, sanctum_center[1] + 1.5 + cave_d/2, cave_floor_z + cave_h/2), (cave_w, 0.8, cave_h)),
        ("W_Left", (-cave_w/2, sanctum_center[1] + 1.5, cave_floor_z + cave_h/2), (0.8, cave_d, cave_h)),
        ("E_Right", (cave_w/2, sanctum_center[1] + 1.5, cave_floor_z + cave_h/2), (0.8, cave_d, cave_h)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        cw = bpy.context.active_object
        cw.scale = (sc[0], sc[1], sc[2])
        cw.name = f"Cave_Wall_{side}"
        bpy.ops.object.transform_apply(scale=True)
        cw.data.materials.append(mat_bedrock)

    # Cave Ceiling (Enclosing the cave completely)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sanctum_center[0], sanctum_center[1] + 1.5, cave_floor_z + cave_h + 0.1))
    c_ceil = bpy.context.active_object
    c_ceil.scale = (cave_w, cave_d, 0.4)
    c_ceil.name = "Cave_Garbhagriha_Ceiling"
    bpy.ops.object.transform_apply(scale=True)
    c_ceil.data.materials.append(mat_bedrock)

    # =========================================================================
    # THE AUTHENTIC DEITY: SWAYAMBHU YONI PEETHA
    # Natural bedrock cleft + perennial natural spring + red silk + silver crown + hibiscus
    # =========================================================================
    peetha_loc = (0.0, 13.0, cave_floor_z + 0.2)

    # 1. Natural Bedrock Raised Basin (approx 2.4m x 2.0m natural rock formation)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.2, depth=0.35, location=(peetha_loc[0], peetha_loc[1], peetha_loc[2] + 0.175))
    basin = bpy.context.active_object
    basin.scale = (1.1, 0.85, 1.0)
    basin.name = "Bedrock_Yoni_Basin"
    bpy.ops.object.transform_apply(scale=True)
    basin.data.materials.append(mat_bedrock)

    # 2. Sacred Spring Water Pool (shimmering perennial spring inside the cleft)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.85, depth=0.08, location=(peetha_loc[0], peetha_loc[1], peetha_loc[2] + 0.25))
    spring_water = bpy.context.active_object
    spring_water.scale = (0.9, 1.1, 1.0)
    spring_water.name = "Perennial_Spring_Water"
    bpy.ops.object.transform_apply(scale=True)
    spring_water.data.materials.append(mat_spring_water)

    # 3. Sacred Natural Cleft (Yoni depression in bedrock, wrapped in Red Silk)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.18, location=(peetha_loc[0], peetha_loc[1], peetha_loc[2] + 0.32))
    yoni_cleft = bpy.context.active_object
    yoni_cleft.scale = (0.75, 1.25, 0.65)
    yoni_cleft.name = "Yoni_Peetha_Cleft"
    bpy.ops.object.transform_apply(scale=True)
    yoni_cleft.data.materials.append(mat_silk_red)

    # 4. Consecrated Silver Mukuta / Crown resting over the spring cleft
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.22, radius2=0.06, depth=0.32, location=(peetha_loc[0], peetha_loc[1] + 0.25, peetha_loc[2] + 0.52))
    silver_crown = bpy.context.active_object
    silver_crown.rotation_euler = (math.radians(-25), 0, 0)
    silver_crown.name = "Kamakhya_Silver_Mukuta"
    bpy.ops.object.transform_apply(rotation=True)
    silver_crown.data.materials.append(mat_silver)

    # 5. Red Hibiscus (Jaba) floral garlands heaped around the cleft
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        gx = peetha_loc[0] + math.cos(rad) * 0.75
        gy = peetha_loc[1] + math.sin(rad) * 0.60
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(gx, gy, peetha_loc[2] + 0.35))
        hibiscus = bpy.context.active_object
        hibiscus.name = f"Hibiscus_Garland_{angle}"
        hibiscus.data.materials.append(mat_hibiscus)

    # Join Yoni components into the official primary node "Deity_Kamakhya"
    yoni_parts = [basin, spring_water, yoni_cleft, silver_crown]
    for obj in bpy.data.objects:
        if obj.name.startswith("Hibiscus_Garland"):
            yoni_parts.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for p in yoni_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = basin
    bpy.ops.object.join()
    deity_kamakhya = bpy.context.active_object
    deity_kamakhya.name = "Deity_Kamakhya"

    # Sacred Deepams illuminating the subterranean cave sanctum
    geom.create_deepam("Deepam_1", (peetha_loc[0] - 1.2, peetha_loc[1] - 0.6, cave_floor_z + 0.2), mat_brass=mat_brass, mat_flame=mat_flame)
    geom.create_deepam("Deepam_2", (peetha_loc[0] + 1.2, peetha_loc[1] - 0.6, cave_floor_z + 0.2), mat_brass=mat_brass, mat_flame=mat_flame)
    geom.create_deepam("Deepam_3", (peetha_loc[0] - 1.2, peetha_loc[1] + 1.2, cave_floor_z + 0.2), mat_brass=mat_brass, mat_flame=mat_flame)
    geom.create_deepam("Deepam_4", (peetha_loc[0] + 1.2, peetha_loc[1] + 1.2, cave_floor_z + 0.2), mat_brass=mat_brass, mat_flame=mat_flame)

    # Archaka Priest serving at the sanctum entrance steps
    geom.create_human_figure("Priest", (1.2, 5.5, 0.8), height=1.75, mat_skin=mat_skin, mat_cloth=mat_cloth)

    # =========================================================================
    # EXTERIOR TOWER: AUTHENTIC NILACHALA BEEHIVE SHIKHARA
    # Rises above the ground plinth with vertical fluted facet ribs & angashikharas
    # =========================================================================
    ext_garb_w, ext_garb_d, ext_garb_h = 8.0, 8.0, 5.0
    ext_z = 0.8
    garb_ext_loc = (0.0, 11.5, ext_z)

    # Exterior Sanctum Chamber Walls (octagonal cruciform facade)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(garb_ext_loc[0], garb_ext_loc[1], ext_z + ext_garb_h/2))
    ext_wall = bpy.context.active_object
    ext_wall.scale = (ext_garb_w, ext_garb_d, ext_garb_h)
    ext_wall.name = "Garbhagriha"
    bpy.ops.object.transform_apply(scale=True)
    ext_wall.data.materials.append(mat_laterite_wall)

    # Niches (Devakoshthas) with stone carved devatas on exterior sanctum walls
    for side, pos, rot in [
        ("N", (0, garb_ext_loc[1] + ext_garb_d/2 + 0.1, ext_z + 2.2), (0, 0, 0)),
        ("W", (-ext_garb_w/2 - 0.1, garb_ext_loc[1], ext_z + 2.2), (0, 0, math.pi/2)),
        ("E", (ext_garb_w/2 + 0.1, garb_ext_loc[1], ext_z + 2.2), (0, 0, -math.pi/2)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        niche = bpy.context.active_object
        niche.scale = (0.8, 0.2, 1.2)
        niche.rotation_euler = rot
        niche.name = f"Devakoshtha_{side}"
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        niche.data.materials.append(mat_laterite_carved)

    # Fluted Beehive Dome (The Nilachala Dome)
    dome_base_z = ext_z + ext_garb_h
    dome_h = 10.0
    dome_tiers = 8
    for i in range(dome_tiers):
        t = i / float(dome_tiers - 1)
        # Authentic Nilachala beehive bulge profile
        radius = 3.6 * math.sin((1.0 - t * 0.82) * math.pi * 0.5) + 0.45 * math.sin(t * math.pi)
        tz = dome_base_z + i * (dome_h / dome_tiers) + (dome_h / dome_tiers)/2
        
        # 16-sided cylinder creating vertical fluting facets down the beehive dome
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=dome_h / dome_tiers, location=(0, garb_ext_loc[1], tz))
        tier = bpy.context.active_object
        tier.name = f"Nilachala_Dome_Tier_{i+1}"
        tier.data.materials.append(mat_laterite_wall)

    # Ring of miniature Angashikharas (Urushringas) clustered at base of dome
    for ang in range(8):
        rad = math.radians(ang * 45)
        ax = math.cos(rad) * 3.3
        ay = garb_ext_loc[1] + math.sin(rad) * 3.3
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.6, radius2=0.1, depth=2.4, location=(ax, ay, dome_base_z + 1.2))
        angashikhara = bpy.context.active_object
        angashikhara.name = f"Angashikhara_{ang+1}"
        angashikhara.data.materials.append(mat_laterite_carved)

    # Ribbed Amalaka Disc at apex
    amalaka_z = dome_base_z + dome_h + 0.4
    bpy.ops.mesh.primitive_torus_add(major_radius=1.2, minor_radius=0.4, location=(0, garb_ext_loc[1], amalaka_z))
    amalaka = bpy.context.active_object
    amalaka.scale = (1.0, 1.0, 0.6)
    amalaka.name = "Nilachala_Amalaka"
    bpy.ops.object.transform_apply(scale=True)
    amalaka.data.materials.append(mat_laterite_carved)

    # Three Golden Kalashas (Trident Finial Crest of Kamakhya)
    for kx, ky in [(0.0, 0.0), (-0.45, 0.0), (0.45, 0.0)]:
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.25, radius2=0.04, depth=0.85, location=(kx, garb_ext_loc[1] + ky, amalaka_z + 0.65))
        kalasha = bpy.context.active_object
        kalasha.name = f"Gold_Kalasha_{kx}"
        kalasha.data.materials.append(mat_gold)

    # =========================================================================
    # COURTYARD SUB-SHRINES & SAUBHAGYA KUNDA
    # =========================================================================
    # Saubhagya Kunda (Sacred water tank with stepped ghats & central pavilion)
    kunda_loc = (16.0, -2.0, 0.0)
    geom.create_kunda("Kunda_Saubhagya", kunda_loc, size=(10.0, 10.0, 2.0), mat_stone=mat_paving, mat_water=mat_kunda_water, steps=5)

    # Central Stone Pavilion in Saubhagya Kunda
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.0, depth=1.5, location=(kunda_loc[0], kunda_loc[1], 0.75))
    kunda_pavilion = bpy.context.active_object
    kunda_pavilion.name = "Kunda_Central_Pavilion"
    kunda_pavilion.data.materials.append(mat_laterite_carved)

    # Bhairava Sub-Shrine (Umananda Bhairava)
    bhairava_loc = (-14.0, 10.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bhairava_loc[0], bhairava_loc[1], 1.5))
    b_shrine = bpy.context.active_object
    b_shrine.scale = (1.8, 1.8, 1.5)
    b_shrine.name = "Bhairava_Shrine"
    bpy.ops.object.transform_apply(scale=True)
    b_shrine.data.materials.append(mat_laterite_carved)
    # Lingam & Trident inside Bhairava shrine
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.15, depth=0.45, location=(bhairava_loc[0], bhairava_loc[1], 1.2))
    b_lingam = bpy.context.active_object
    b_lingam.name = "Bhairava_Lingam"
    b_lingam.data.materials.append(mat_bedrock)

    # Ganesha Sub-Shrine
    ganesha_loc = (-14.0, -2.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ganesha_loc[0], ganesha_loc[1], 1.5))
    g_shrine = bpy.context.active_object
    g_shrine.scale = (1.8, 1.8, 1.5)
    g_shrine.name = "Ganesha_Shrine"
    bpy.ops.object.transform_apply(scale=True)
    g_shrine.data.materials.append(mat_laterite_carved)

    # Nilachal Hill Trees & Sacred Peepal Trees
    for tx, ty in [(-18, -14), (-12, -18), (14, 16), (-16, 18), (20, -14)]:
        geom.create_tree(f"Peepal_Tree_{tx}_{ty}", (tx, ty, 0.0), height=7.5, mat_trunk=mat_bark, mat_leaves=mat_foliage)

    # Spawn Point at Nilachal gateway pathway
    spawn = bpy.data.objects.new("Spawn_Point", None)
    bpy.context.scene.collection.objects.link(spawn)
    spawn.location = (0.0, -15.0, 0.8)

    # Open the actual descent through the courtyard plane, raised plinth,
    # and the otherwise solid exterior tower shell. A hidden solid floor over
    # the stairs made the subterranean shrine inaccessible in the old model.
    ground = bpy.data.objects.get("Ground_Main")
    if ground:
        mesh = bpy.data.meshes.new("Courtyard_With_Descent_Opening")
        outer = [(-37.5, -37.5, 0), (37.5, -37.5, 0), (37.5, 37.5, 0), (-37.5, 37.5, 0)]
        inner = [(-1.3, 5.7, 0), (1.3, 5.7, 0), (1.3, 16.6, 0), (-1.3, 16.6, 0)]
        mesh.from_pydata(outer + inner, [], [(0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)])
        mesh.materials.append(mat_paving)
        ground.data = mesh
    for target_name, back_y in [("Nilachal_Plinth", 16.6), ("Garbhagriha", 9.6)]:
        target = bpy.data.objects.get(target_name)
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, (5.7 + back_y) / 2, 0))
        cutter = bpy.context.active_object
        cutter.scale = (1.3, (back_y - 5.7) / 2, 3.2)
        bpy.ops.object.transform_apply(scale=True)
        if target:
            bpy.context.view_layer.objects.active = target
            modifier = target.modifiers.new("Walkable_Cave_Descent", 'BOOLEAN')
            modifier.operation = 'DIFFERENCE'
            modifier.solver = 'EXACT'
            modifier.object = cutter
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    # Export
    out_dir = os.path.join(os.path.dirname(blender_dir), "godot", "assets", "models")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "kamakhya_kshetra_full.glb")

    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
    )
    print(f"Authentic Kamakhya exported: {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    build_authentic_kamakhya()
