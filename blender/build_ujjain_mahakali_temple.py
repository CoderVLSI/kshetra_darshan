"""
Blender 5.3 Build Script for Ujjain Mahakali / Harasiddhi Temple (Kshetra #14)
Architecture: Maratha-Nagara with twin deepastambhas, Sabha Mandap and a southern well
Deity: Authentic Harasiddhi Devi - vermilion sindoor rock murti seated under silver Chhatra,
       flanked by Mahalakshmi & Mahasaraswati, with Akhanda Jyoti
Output: d:\\Kshetra_Darshan\\godot\\assets\\models\\ujjain_mahakali_kshetra_full.glb
"""
import os
import sys
import math
import bpy
from mathutils import Matrix, Vector

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from common_materials import (
    create_sandstone, create_brass_metal, create_gold_metal,
    create_black_stone, create_flame_emission, create_water,
    create_skin, create_white_dhoti, create_kumkum_red,
    create_flower_garland, create_white_marble
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_hanging_bell, create_deepam, create_human_figure,
    create_ground_plane, create_mandapa, create_prakara_wall, export_glb
)

def build_deepastambha(name, location, height=13.0, tiers=11, mat_stone=None, mat_brass=None, mat_flame=None):
    """Build the signature tall Ujjain Deepastambha lamp pillar joined into a single mesh."""
    objs = []
    x, y, z = location
    
    # Octagonal stepped base
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.6, depth=0.8, location=(x, y, z + 0.4))
    b1 = bpy.context.active_object
    b1.name = f"{name}_Base1"
    if mat_stone: b1.data.materials.append(mat_stone)
    objs.append(b1)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.2, depth=0.6, location=(x, y, z + 1.1))
    b2 = bpy.context.active_object
    b2.name = f"{name}_Base2"
    if mat_stone: b2.data.materials.append(mat_stone)
    objs.append(b2)
    
    # Main octagonal tapering shaft
    shaft_h = height - 3.0
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=.98, radius2=.24, depth=shaft_h,
                                   location=(x, y, z + 1.4 + shaft_h / 2))
    shaft = bpy.context.active_object
    shaft.name = f"{name}_Shaft"
    if mat_stone: shaft.data.materials.append(mat_stone)
    objs.append(shaft)
    
    # Multiple tiers of radiating lamp brackets
    tier_spacing = shaft_h / (tiers + 1)
    for i in range(tiers):
        tz = z + 1.6 + (i + 1) * tier_spacing
        tier_radius = .98 - .74 * ((i + 1) / (tiers + 1))
        
        # Ring shelf
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=tier_radius + 0.15, depth=0.10, location=(x, y, tz))
        ring = bpy.context.active_object
        ring.name = f"{name}_TierRing_{i+1}"
        if mat_stone: ring.data.materials.append(mat_stone)
        objs.append(ring)
        
        # Radiating lamp brackets in 6 directions
        brackets_per_tier = 6
        for b in range(brackets_per_tier):
            angle = (b * (2 * math.pi / brackets_per_tier)) + (i * 0.25)
            bx = x + math.cos(angle) * (tier_radius + 0.32)
            by = y + math.sin(angle) * (tier_radius + 0.32)
            
            # Bracket cup
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=0.04, location=(bx, by, tz + 0.04))
            cup = bpy.context.active_object
            cup.name = f"{name}_Cup_{i}_{b}"
            if mat_brass: cup.data.materials.append(mat_brass)
            objs.append(cup)
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(bx, by, tz + 0.08))
            fl = bpy.context.active_object
            fl.scale = (1, 1, 1.6)
            fl.name = f"{name}_Flame_{i}_{b}"
            bpy.ops.object.transform_apply(scale=True)
            if mat_flame: fl.data.materials.append(mat_flame)
            objs.append(fl)
    
    # Crowning kalasha
    top_z = z + 1.4 + shaft_h
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.45, radius2=0.08, depth=0.8, location=(x, y, top_z + 0.4))
    top_cone = bpy.context.active_object
    if mat_brass: top_cone.data.materials.append(mat_brass)
    objs.append(top_cone)
    
    # Join into single unified deepastambha mesh
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = b1
    bpy.ops.object.join()
    res = bpy.context.active_object
    res.name = name
    return res

def build_maratha_nagara_shikhara(name, location, width=6.4, height=14.5, mat_stone=None, mat_gold=None):
    """Build authentic Maratha-Nagara curvilinear shikhara with corner miniature turrets."""
    objs = []
    x, y, z = location
    bada_h = 4.6
    spire_h = height - bada_h - 2.0
    tiers = 8
    tier_h = spire_h / tiers
    
    for i in range(tiers):
        t = i / float(tiers)
        scale_fac = 1.0 - 0.48 * (t ** 1.6)
        tw = (width / 2) * scale_fac
        tz = z + bada_h + i * tier_h + tier_h / 2
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        tier = bpy.context.active_object
        tier.scale = (tw, tw, tier_h / 2)
        tier.name = f"{name}_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: tier.data.materials.append(mat_stone)
        objs.append(tier)
        
        # Corner angashikharas on lower tiers
        if i < 4:
            for cx in [-tw * 0.9, tw * 0.9]:
                for cy in [-tw * 0.9, tw * 0.9]:
                    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=tw * 0.22, radius2=0.05, depth=tier_h * 1.5, location=(x + cx, y + cy, tz + tier_h * 0.2))
                    ang = bpy.context.active_object
                    if mat_stone: ang.data.materials.append(mat_stone)
                    objs.append(ang)
                    
    # Amalaka & Kalasha
    shikh_top = z + bada_h + spire_h
    bpy.ops.mesh.primitive_torus_add(major_radius=width * 0.28, minor_radius=0.25, location=(x, y, shikh_top + 0.3))
    amalaka = bpy.context.active_object
    amalaka.name = f"{name}_Amalaka"
    if mat_stone: amalaka.data.materials.append(mat_stone)
    objs.append(amalaka)
    
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.35, radius2=0.05, depth=1.4, location=(x, y, shikh_top + 1.2))
    kalasha = bpy.context.active_object
    kalasha.name = f"{name}_Kalasha"
    if mat_gold: kalasha.data.materials.append(mat_gold)
    objs.append(kalasha)
    
    return objs

def create_authentic_harasiddhi_murti(name="Deity_Mahakali", location=(0, 11.8, 0.1), mat_sindoor=None, mat_gold=None, mat_silver=None, mat_black=None, mat_silk=None):
    """
    Creates the authentic Harasiddhi / Mahakali Murti of Ujjain:
    - Vermilion-Sindoor covered sacred rock-cut idol
    - Seated on elevated marble/gold Pitha
    - Golden Mukuta crown with third eye
    - Ornate Silver Chhatra (umbrella) suspended above
    - Flanked by Goddess Mahalakshmi & Goddess Mahasaraswati icons
    - Akhanda Jyoti brass lamp before the idol
    """
    parts = []
    x, y, z = location
    
    # 1. High Gold/Marble Pedestal (Pitha)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.1, depth=0.28, location=(x, y, z + 0.14))
    ped = bpy.context.active_object
    ped.name = f"{name}_Pedestal"
    if mat_gold: ped.data.materials.append(mat_gold)
    parts.append(ped)
    
    # 2. Main Central Idol: Harasiddhi Devi (Vermilion Sindoor Swayambhu Rock)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.48, location=(x, y, z + 0.65))
    devi_body = bpy.context.active_object
    devi_body.scale = (0.9, 0.75, 1.15)
    bpy.ops.object.transform_apply(scale=True)
    devi_body.name = f"{name}_Sindoor_Body"
    if mat_sindoor: devi_body.data.materials.append(mat_sindoor)
    parts.append(devi_body)
    
    # Divine Face with large silver/black eyes
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(x, y - 0.15, z + 1.15))
    face = bpy.context.active_object
    face.name = f"{name}_Face"
    if mat_sindoor: face.data.materials.append(mat_sindoor)
    parts.append(face)
    
    # Silver Eyes (Netra)
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(x + sign * 0.08, y - 0.30, z + 1.18))
        eye = bpy.context.active_object
        eye.scale = (1.2, 0.4, 0.7)
        bpy.ops.object.transform_apply(scale=True)
        if mat_silver: eye.data.materials.append(mat_silver)
        parts.append(eye)
        
    # Third eye on forehead
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(x, y - 0.31, z + 1.25))
    third_eye = bpy.context.active_object
    if mat_gold: third_eye.data.materials.append(mat_gold)
    parts.append(third_eye)
    
    # Golden Crown (Mukuta)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.22, radius2=0.06, depth=0.42, location=(x, y - 0.05, z + 1.50))
    crown = bpy.context.active_object
    crown.name = f"{name}_Crown"
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)
    
    # Red Silk Zari Dupatta/Sari drapery
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=0.35, location=(x, y, z + 0.45))
    sari = bpy.context.active_object
    if mat_silk: sari.data.materials.append(mat_silk)
    parts.append(sari)
    
    # Silver Chhatra (Umbrella) suspended above Devi
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.75, radius2=0.08, depth=0.28, location=(x, y, z + 2.1))
    chhatra = bpy.context.active_object
    chhatra.name = f"{name}_Silver_Chhatra"
    if mat_silver: chhatra.data.materials.append(mat_silver)
    parts.append(chhatra)
    
    # 3. Flanking Deity: Goddess Mahalakshmi on Left
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(x - 0.65, y, z + 0.55))
    laxmi = bpy.context.active_object
    laxmi.scale = (0.8, 0.7, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    laxmi.name = f"{name}_Mahalakshmi"
    if mat_gold: laxmi.data.materials.append(mat_gold)
    parts.append(laxmi)
    
    # 4. Flanking Deity: Goddess Mahasaraswati on Right
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(x + 0.65, y, z + 0.55))
    saraswati = bpy.context.active_object
    saraswati.scale = (0.8, 0.7, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    saraswati.name = f"{name}_Mahasaraswati"
    if mat_silver: saraswati.data.materials.append(mat_silver)
    parts.append(saraswati)
    
    # 5. Golden Prabhavali arch framing all three
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.08, location=(x, y + 0.1, z + 1.1))
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: prabha.data.materials.append(mat_gold)
    parts.append(prabha)
    
    # Join into single unified Deity object
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = ped
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = name
    return deity

def build_maratha_mandapa(name="Mandapa", location=(0, 3.2, 0), width=8.5, depth=7.5, height=3.6, mat_stone=None, mat_gold=None):
    """Build Sabha Mandap with carved octagonal pillars and corner chhatris."""
    objs = []
    x, y, z = location
    hw = width / 2
    hd = depth / 2
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.1))
    floor = bpy.context.active_object
    floor.scale = (hw, hd, 0.1)
    floor.name = f"{name}_Floor"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: floor.data.materials.append(mat_stone)
    objs.append(floor)
    
    # Carved octagonal pillars
    for px in [-3.2, -1.1, 1.1, 3.2]:
        for py in [y - 3.0, y, y + 3.0]:
            p = create_pillar(f"{name}_Pillar_{px}_{py}", (px, py, z + 0.2), height=height - 0.2, radius=0.2, mat=mat_stone, style="octagonal")
            objs.append(p)
            
    # Roof slab
    roof_z = z + height + 0.15
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, roof_z))
    roof = bpy.context.active_object
    roof.scale = (hw + 0.4, hd + 0.4, 0.15)
    roof.name = f"{name}_RoofSlab"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)
    
    # Corner chhatris on mandapa roof
    for cx in [-hw * 0.85, hw * 0.85]:
        for cy in [y - hd * 0.85, y + hd * 0.85]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.55, depth=0.8, location=(cx, cy, roof_z + 0.55))
            ch = bpy.context.active_object
            if mat_stone: ch.data.materials.append(mat_stone)
            objs.append(ch)
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(cx, cy, roof_z + 1.1))
            ch_dome = bpy.context.active_object
            if mat_stone: ch_dome.data.materials.append(mat_stone)
            objs.append(ch_dome)
            
    return objs

def build_subshrine(name, location, deity_type="bhairava", mat_stone=None, mat_gold=None, mat_black=None):
    """Build sub-shrine joined into single mesh."""
    objs = []
    x, y, z = location
    sw, sd, sh = 2.4, 2.4, 2.6
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.15))
    plat = bpy.context.active_object
    plat.scale = (sw/2, sd/2, 0.15)
    plat.name = f"{name}_Plat"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: plat.data.materials.append(mat_stone)
    objs.append(plat)
    
    # Back wall
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y + sd/2 - 0.2, z + 0.3 + sh/2))
    wb = bpy.context.active_object
    wb.scale = (sw/2, 0.2, sh/2)
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: wb.data.materials.append(mat_stone)
    objs.append(wb)
    
    # Shikhara roof
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=sw*0.7, radius2=0.15, depth=2.0, location=(x, y, z + 0.3 + sh + 1.0))
    shikh = bpy.context.active_object
    if mat_stone: shikh.data.materials.append(mat_stone)
    objs.append(shikh)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(x, y, z + 0.3 + sh + 2.1))
    kal = bpy.context.active_object
    if mat_gold: kal.data.materials.append(mat_gold)
    objs.append(kal)
    
    # Lingam or deity inside
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.2, depth=0.45, location=(x, y, z + 0.55))
    icon = bpy.context.active_object
    if mat_black: icon.data.materials.append(mat_black)
    objs.append(icon)
    
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = plat
    bpy.ops.object.join()
    res = bpy.context.active_object
    res.name = name
    return res

def main():
    clear_scene()
    
    # Materials
    mat_sandstone = create_sandstone("Ujjain_Sandstone", color=(0.74, 0.60, 0.42, 1.0))
    mat_brass = create_brass_metal("Ujjain_Brass")
    mat_gold = create_gold_metal("Ujjain_Gold")
    mat_silver = create_white_marble("Ujjain_Silver", color=(0.90, 0.92, 0.95, 1.0), roughness=0.18)
    mat_black = create_black_stone("Mahakali_Black_Basalt")
    mat_sindoor = create_kumkum_red("Harasiddhi_Sindoor", color=(0.92, 0.18, 0.08, 1.0))
    mat_silk = create_kumkum_red("Red_Silk_Sari", color=(0.85, 0.08, 0.08, 1.0))
    mat_flame = create_flame_emission("Flame_Glow", strength=9.0)
    mat_water = create_water("Harsiddhi_Well_Water", color=(0.14, 0.36, 0.45, 0.85))
    mat_paving = create_sandstone("Harsiddhi_Courtyard_Paving", color=(.45, .41, .37, 1.0))
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    
    # 1. Main Ground
    ground = create_ground_plane(name="Ground_Main", size=70, mat=mat_paving)
    
    # 2. Garbhagriha Walls
    garbha_walls = create_garbhagriha(
        name="Garbhagriha_Walls",
        location=(0, 11, 0),
        width=5.8,
        depth=5.8,
        wall_height=4.6,
        wall_thickness=0.5,
        mat=mat_sandstone,
        door_width=2.2,
        door_height=3.0
    )
    bpy.ops.object.select_all(action='DESELECT')
    for obj in garbha_walls: obj.select_set(True)
    bpy.context.view_layer.objects.active = garbha_walls[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"
    
    # 3. Maratha-Nagara Shikhara
    build_maratha_nagara_shikhara(name="Mahakali_Shikhara", location=(0, 11, 0), width=6.4, height=14.5, mat_stone=mat_sandstone, mat_gold=mat_gold)
    
    # 4. Sabha Mandap (Preceding Hall)
    mandapa_parts = build_maratha_mandapa(name="Mandapa", location=(0, 3.2, 0), width=8.5, depth=7.5, height=3.6, mat_stone=mat_sandstone, mat_gold=mat_gold)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mandapa_parts: obj.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_parts[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"
    
    # 5. SIGNATURE TWIN DEEPASTAMBHAS
    build_deepastambha(name="Deepastambha_Left", location=(-4.8, -4.5, 0), height=13.0, tiers=11, mat_stone=mat_sandstone, mat_brass=mat_brass, mat_flame=mat_flame)
    build_deepastambha(name="Deepastambha_Right", location=(4.8, -4.5, 0), height=13.0, tiers=11, mat_stone=mat_sandstone, mat_brass=mat_brass, mat_flame=mat_flame)
    
    # 6. Authentic Deity: Harasiddhi Devi (seated under silver Chhatra with Lakshmi and Saraswati)
    create_authentic_harasiddhi_murti(name="Deity_Mahakali", location=(0, 11.8, 0.1), mat_sindoor=mat_sindoor, mat_gold=mat_gold, mat_silver=mat_silver, mat_black=mat_black, mat_silk=mat_silk)
    
    # 7. Priest
    create_human_figure(name="Priest", location=(1.5, 10.2, 0), height=1.7, mat_skin=mat_skin, mat_cloth=mat_dhoti)
    
    # 8. Ghanta (Hanging Temple Bell in mandapa entrance)
    create_hanging_bell(name="Ghanta", location=(0, -0.4, 3.0), mat_brass=mat_brass, scale=1.3)
    
    # 9. Deepams flanking doorway
    create_deepam(name="Deepam_1", location=(-1.3, 8.0, 0), mat_brass=mat_brass, mat_flame=mat_flame)
    create_deepam(name="Deepam_2", location=(1.3, 8.0, 0), mat_brass=mat_brass, mat_flame=mat_flame)
    
    # The district inventory puts all three deities in the shared sanctum.
    for name, position in [
        ("Mahalakshmi_Sanctum_Anchor", (-.65, 11.8, .82)),
        ("Mahasaraswati_Sanctum_Anchor", (.65, 11.8, .82)),
    ]:
        marker = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(marker)
        marker.location = position

    bpy.context.view_layer.update()
    eastward = Matrix.Rotation(math.pi / 2, 4, 'Z')
    for obj in bpy.context.scene.objects:
        if obj != ground and obj.parent is None:
            obj.matrix_world = eastward @ obj.matrix_world

    # The temple and district describe four entrances, with the eastern main
    # gate leading between the two lamp towers.
    create_prakara_wall("Harsiddhi_Enclosure", width=48, depth=35, wall_height=2.75,
                        mat=mat_sandstone, gate_width=4.5, gate_sides=["E", "W", "N", "S"])
    create_mandapa("Harsiddhi_East_Gateway", (24, 0, 0), width=3.5, depth=5,
                   height=3.9, pillar_count_x=2, pillar_count_y=2,
                   mat_stone=mat_sandstone, mat_floor=mat_paving)

    # The district inventory places the well on the south side.
    bpy.ops.mesh.primitive_torus_add(major_segments=48, location=(-4, -12, .56),
                                    major_radius=1.5, minor_radius=.23)
    well = bpy.context.active_object
    well.name = "Harsiddhi_South_Well"
    well.data.materials.append(mat_black)
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=1.3, depth=.05,
                                       location=(-4, -12, .14))
    water = bpy.context.active_object
    water.name = "Harsiddhi_Well_Water"
    water.data.materials.append(mat_water)
    create_pillar("Harsiddhi_Well_Dated_Pillar", (-5.5, -12, 0), height=2.65,
                  radius=.27, mat=mat_sandstone, style="octagonal")

    # Karkoteshwar occupies the north side of the main temple.
    karkot = build_subshrine("Karkoteshwar_Shiva", location=(0, 0, 0),
                             deity_type="bhairava", mat_stone=mat_sandstone,
                             mat_gold=mat_gold, mat_black=mat_black)
    karkot.rotation_euler.z = math.pi / 2
    karkot.location = (-6, 11, 0)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(19, 0, .1))
    bpy.context.active_object.name = "Spawn_Point"

    output_path = os.path.join(os.path.dirname(script_dir), "godot", "assets", "models",
                               "ujjain_mahakali_kshetra_full.glb")
    export_glb(output_path)
    print("Successfully built authentic Ujjain Mahakali / Harasiddhi Temple GLB!")

if __name__ == "__main__":
    main()
