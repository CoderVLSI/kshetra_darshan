"""
Blender 5.3 Build Script for Gaya Mangalagauri Temple (Kshetra #16)
Architecture: Hilltop Nagara Shikhara (Bhasmakoot Hill) with Falgu River Ghats Below
Deity: Authentic Mangala Gauri Stanapitha - sacred natural rock breast symbols consecrated
       with vermilion sindoor, silver eyes, golden necklaces, silver Chhatra, and Uma-Maheshwara
Output: d:\\Kshetra_Darshan\\godot\\assets\\models\\gaya_mangalagauri_kshetra_full.glb
"""
import os
import sys
import math
import bpy
from mathutils import Vector

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from common_materials import (
    create_sandstone, create_brass_metal, create_gold_metal,
    create_black_stone, create_water, create_flame_emission,
    create_skin, create_white_dhoti, create_granite_stone,
    create_flower_garland, create_kumkum_red, create_white_marble
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_hanging_bell, create_deepam, create_human_figure,
    create_ground_plane, export_glb
)

def build_bhasmakoot_hill_terraces(location=(0, 6, 0), width=24.0, depth=26.0, hill_h=2.2, mat_rock=None, mat_stairs=None):
    """Build the elevated Bhasmakoot hill terrace with grand stone staircase leading up to temple."""
    objs = []
    hx, hy, hz = location
    
    # Lower rocky terraced hill foundation
    bpy.ops.mesh.primitive_cube_add(size=2, location=(hx, hy, hz + hill_h/2))
    hill = bpy.context.active_object
    hill.scale = (width/2, depth/2, hill_h/2)
    hill.name = "Bhasmakoot_Hill_Base"
    bpy.ops.object.transform_apply(scale=True)
    if mat_rock: hill.data.materials.append(mat_rock)
    objs.append(hill)
    
    # Upper paved courtyard terrace
    bpy.ops.mesh.primitive_cube_add(size=2, location=(hx, hy, hz + hill_h + 0.1))
    terrace = bpy.context.active_object
    terrace.scale = (width/2 - 0.4, depth/2 - 0.4, 0.1)
    terrace.name = "Bhasmakoot_Courtyard_Paving"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stairs: terrace.data.materials.append(mat_stairs)
    objs.append(terrace)
    
    # Grand flights of stone stairs ascending from South
    stairs_count = 12
    step_w = 4.2
    step_d = 0.55
    step_h = hill_h / stairs_count
    for i in range(stairs_count):
        sy = hy - depth/2 - (stairs_count - i) * step_d
        sz = i * step_h + step_h/2
        bpy.ops.mesh.primitive_cube_add(size=2, location=(hx, sy, sz))
        step = bpy.context.active_object
        step.scale = (step_w/2, step_d/2, step_h/2)
        step.name = f"Hill_Stair_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stairs: step.data.materials.append(mat_stairs)
        objs.append(step)
        
    # Stone banisters
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(hx + sign * (step_w/2 + 0.2), hy - depth/2 - (stairs_count/2)*step_d, hill_h/2))
        ban = bpy.context.active_object
        ban.scale = (0.2, (stairs_count * step_d)/2, hill_h/2 + 0.4)
        ban.name = f"Stair_Balustrade_{sign}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_rock: ban.data.materials.append(mat_rock)
        objs.append(ban)
        
    return objs

def build_falgu_river_ghat(location=(-22, 5, 0), depth=32.0, mat_stone=None, mat_water=None, mat_sand=None):
    """Build the sacred Falgu river (Niranjana) ghat below the hill."""
    objs = []
    gx, gy, gz = location
    
    # Wide sandy riverbed
    bpy.ops.mesh.primitive_cube_add(size=2, location=(gx - 8, gy, gz - 1.1))
    sand = bpy.context.active_object
    sand.scale = (11, depth/2 + 5, 0.1)
    sand.name = "Falgu_Sandbed"
    bpy.ops.object.transform_apply(scale=True)
    if mat_sand: sand.data.materials.append(mat_sand)
    objs.append(sand)
    
    # Falgu river water stream
    bpy.ops.mesh.primitive_plane_add(size=1, location=(gx - 9, gy, gz - 0.95))
    water = bpy.context.active_object
    water.scale = (7, depth/2 + 4, 1)
    water.name = "Falgu_Water"
    bpy.ops.object.transform_apply(scale=True)
    if mat_water: water.data.materials.append(mat_water)
    objs.append(water)
    
    # Stepped stone ghat descending to riverbed
    for i in range(8):
        sx = gx - (8 - i) * 0.65
        sz = gz - i * 0.15
        bpy.ops.mesh.primitive_cube_add(size=2, location=(sx, gy, sz))
        step = bpy.context.active_object
        step.scale = (0.65/2, depth/2, 0.15/2)
        step.name = f"Falgu_Step_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: step.data.materials.append(mat_stone)
        objs.append(step)
        
    return objs

def build_gaya_nagara_shikhara(name="Mangalagauri_Shikhara", location=(0, 11, 2.4), width=6.0, height=13.0, mat_stone=None, mat_gold=None):
    """Build ancient dark sandstone Nagara Shikhara."""
    objs = []
    x, y, z = location
    bada_h = 4.2
    spire_h = height - bada_h
    tiers = 8
    tier_h = spire_h / tiers
    
    for i in range(tiers):
        t = i / float(tiers)
        scale_fac = 1.0 - 0.45 * (t ** 1.6)
        tw = (width / 2) * scale_fac
        tz = z + bada_h + i * tier_h + tier_h / 2
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        tier = bpy.context.active_object
        tier.scale = (tw, tw, tier_h / 2)
        tier.name = f"{name}_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: tier.data.materials.append(mat_stone)
        objs.append(tier)
        
    shikh_top = z + bada_h + spire_h
    bpy.ops.mesh.primitive_torus_add(major_radius=width * 0.25, minor_radius=0.22, location=(x, y, shikh_top + 0.25))
    amalaka = bpy.context.active_object
    amalaka.name = f"{name}_Amalaka"
    if mat_stone: amalaka.data.materials.append(mat_stone)
    objs.append(amalaka)
    
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.3, radius2=0.04, depth=1.2, location=(x, y, shikh_top + 1.0))
    kalasha = bpy.context.active_object
    kalasha.name = f"{name}_Kalasha"
    if mat_gold: kalasha.data.materials.append(mat_gold)
    objs.append(kalasha)
    
    return objs

def create_authentic_mangalagauri_stanapitha(name="Deity_Mangalagauri", location=(0, 11.8, 2.5), mat_sindoor=None, mat_gold=None, mat_silver=None, mat_stone=None, mat_garland=None):
    """
    Creates the authentic Mangala Gauri Stanapitha of Gaya:
    - Natural rock-carved breast symbols (Stana) of Sati
    - Consecrated with glowing vermilion sindoor
    - Silver eyes and golden third eye
    - Ornate golden Haras / necklaces
    - Silver Chhatra (umbrella) suspended above
    - Adjacent ancient stone Uma-Maheshwara murti
    - Prabhavali ornamental arch
    """
    parts = []
    x, y, z = location
    
    # 1. High Stone Pedestal (Pitha)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.0, depth=0.25, location=(x, y, z + 0.125))
    ped = bpy.context.active_object
    ped.name = f"{name}_Pedestal"
    if mat_stone: ped.data.materials.append(mat_stone)
    parts.append(ped)
    
    # 2. Sacred Natural Stanapitha Bedrock Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.8, depth=0.2, location=(x, y, z + 0.35))
    bedrock = bpy.context.active_object
    bedrock.scale = (1.1, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    bedrock.name = f"{name}_Bedrock"
    if mat_stone: bedrock.data.materials.append(mat_stone)
    parts.append(bedrock)
    
    # 3. Two Sacred Stana (Breast) Rock Mound Symbols of Sati covered in Sindoor
    for sign, sx in [("L", -0.22), ("R", 0.22)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.26, location=(x + sx, y - 0.05, z + 0.65))
        stana = bpy.context.active_object
        stana.scale = (0.95, 0.9, 1.1)
        bpy.ops.object.transform_apply(scale=True)
        stana.name = f"{name}_Stana_{sign}"
        if mat_sindoor: stana.data.materials.append(mat_sindoor)
        parts.append(stana)
        
        # Golden Mukuta/Chakri top crest on each mound
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.06, location=(x + sx, y - 0.05, z + 0.95))
        crest = bpy.context.active_object
        if mat_gold: crest.data.materials.append(mat_gold)
        parts.append(crest)
        
        # Silver Eyes on the sacred symbols
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(x + sx, y - 0.25, z + 0.72))
        eye = bpy.context.active_object
        eye.scale = (1.2, 0.4, 0.7)
        bpy.ops.object.transform_apply(scale=True)
        if mat_silver: eye.data.materials.append(mat_silver)
        parts.append(eye)
        
    # 4. Gold Haras / Necklaces draped around the Stanapitha
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.04, location=(x, y - 0.05, z + 0.52))
    hara = bpy.context.active_object
    hara.rotation_euler = (0.3, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: hara.data.materials.append(mat_gold)
    parts.append(hara)
    
    # 5. Silver Chhatra (Umbrella) suspended overhead
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.7, radius2=0.06, depth=0.26, location=(x, y, z + 1.8))
    chhatra = bpy.context.active_object
    chhatra.name = f"{name}_Chhatra"
    if mat_silver: chhatra.data.materials.append(mat_silver)
    parts.append(chhatra)
    
    # 6. Ancient Uma-Maheshwara Stone Murti flanking on the right
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x + 0.65, y + 0.15, z + 0.6))
    uma_mah = bpy.context.active_object
    uma_mah.scale = (0.22, 0.15, 0.35)
    uma_mah.name = f"{name}_Uma_Maheshwara"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: uma_mah.data.materials.append(mat_stone)
    parts.append(uma_mah)
    
    # 7. Golden Prabhavali Arch framing the sanctum altar
    bpy.ops.mesh.primitive_torus_add(major_radius=0.9, minor_radius=0.07, location=(x, y + 0.15, z + 1.0))
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

def build_gaya_mandapa(name="Mandapa", location=(0, 4.0, 2.4), width=8.0, depth=7.0, height=3.5, mat_stone=None, mat_gold=None):
    """Build Sabha Mandap on the hilltop terrace."""
    objs = []
    x, y, z = location
    hw = width / 2
    hd = depth / 2
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.1))
    floor = bpy.context.active_object
    floor.scale = (hw, hd, 0.1)
    floor.name = f"{name}_Floor"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: floor.data.materials.append(mat_stone)
    objs.append(floor)
    
    # Carved pillars
    for px in [-2.8, -0.95, 0.95, 2.8]:
        for py in [y - 2.6, y, y + 2.6]:
            p = create_pillar(f"{name}_Pillar_{px}_{py}", (px, py, z + 0.2), height=height - 0.2, radius=0.18, mat=mat_stone, style="octagonal")
            objs.append(p)
            
    # Roof
    roof_z = z + height + 0.12
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, roof_z))
    roof = bpy.context.active_object
    roof.scale = (hw + 0.35, hd + 0.35, 0.12)
    roof.name = f"{name}_Roof"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)
    
    return objs

def build_subshrine(name, location, deity_type="bhairava", mat_stone=None, mat_gold=None, mat_black=None):
    """Build subshrine joined into single mesh."""
    objs = []
    x, y, z = location
    sw, sd, sh = 2.2, 2.2, 2.4
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.15))
    plat = bpy.context.active_object
    plat.scale = (sw/2, sd/2, 0.15)
    plat.name = f"{name}_Plat"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: plat.data.materials.append(mat_stone)
    objs.append(plat)
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y + sd/2 - 0.2, z + 0.3 + sh/2))
    wb = bpy.context.active_object
    wb.scale = (sw/2, 0.2, sh/2)
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: wb.data.materials.append(mat_stone)
    objs.append(wb)
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=sw*0.65, radius2=0.12, depth=1.8, location=(x, y, z + 0.3 + sh + 0.9))
    roof = bpy.context.active_object
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(x, y, z + 0.3 + sh + 1.9))
    kal = bpy.context.active_object
    if mat_gold: kal.data.materials.append(mat_gold)
    objs.append(kal)
    
    # Lingam or icon
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=0.4, location=(x, y, z + 0.55))
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
    mat_dark_sandstone = create_sandstone("Gaya_Dark_Sandstone", color=(0.45, 0.38, 0.32, 1.0), roughness=0.92)
    mat_rock = create_granite_stone("Bhasmakoot_Hill_Rock", color=(0.32, 0.28, 0.24, 1.0))
    mat_sand = create_sandstone("Falgu_Sand", color=(0.75, 0.68, 0.50, 1.0))
    mat_gold = create_gold_metal("Gaya_Gold")
    mat_silver = create_white_marble("Gaya_Silver", color=(0.90, 0.92, 0.95, 1.0), roughness=0.18)
    mat_brass = create_brass_metal("Gaya_Brass")
    mat_black = create_black_stone("Gaya_Basalt")
    mat_sindoor = create_kumkum_red("Mangalagauri_Sindoor", color=(0.94, 0.16, 0.06, 1.0))
    mat_water = create_water("Falgu_Water_Mat", color=(0.16, 0.38, 0.46, 0.82))
    mat_flame = create_flame_emission("Flame_Glow", strength=8.0)
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    
    # 1. Main Ground
    ground = create_ground_plane(name="Ground_Main", size=70, mat=mat_sand)
    
    # 2. Elevated Bhasmakoot Hill Terraces & Ascending Grand Staircase
    build_bhasmakoot_hill_terraces(location=(0, 6, 0), width=24.0, depth=26.0, hill_h=2.2, mat_rock=mat_rock, mat_stairs=mat_dark_sandstone)
    
    # 3. Garbhagriha Walls atop Hill
    garbha_walls = create_garbhagriha(
        name="Garbhagriha_Walls",
        location=(0, 11, 2.4),
        width=5.6,
        depth=5.6,
        wall_height=4.4,
        wall_thickness=0.5,
        mat=mat_dark_sandstone,
        door_width=2.2,
        door_height=3.0
    )
    bpy.ops.object.select_all(action='DESELECT')
    for obj in garbha_walls: obj.select_set(True)
    bpy.context.view_layer.objects.active = garbha_walls[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"
    
    # 4. Hilltop Nagara Shikhara
    build_gaya_nagara_shikhara(name="Mangalagauri_Shikhara", location=(0, 11, 2.4), width=6.0, height=13.0, mat_stone=mat_dark_sandstone, mat_gold=mat_gold)
    
    # 5. Sabha Mandap (Preceding Hall on hilltop)
    mandapa_parts = build_gaya_mandapa(name="Mandapa", location=(0, 4.0, 2.4), width=8.0, depth=7.0, height=3.5, mat_stone=mat_dark_sandstone, mat_gold=mat_gold)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mandapa_parts: obj.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_parts[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"
    
    # 6. Authentic Deity: Mangalagauri Stanapitha
    create_authentic_mangalagauri_stanapitha(name="Deity_Mangalagauri", location=(0, 11.8, 2.5), mat_sindoor=mat_sindoor, mat_gold=mat_gold, mat_silver=mat_silver, mat_stone=mat_dark_sandstone)
    
    # 7. Priest
    create_human_figure(name="Priest", location=(1.5, 10.2, 2.4), height=1.7, mat_skin=mat_skin, mat_cloth=mat_dhoti)
    
    # 8. Ghanta (Hanging Temple Bell in mandapa entrance)
    create_hanging_bell(name="Ghanta", location=(0, 0.4, 5.4), mat_brass=mat_brass, scale=1.3)
    
    # 9. Deepams flanking sanctum doorway
    create_deepam(name="Deepam_1", location=(-1.3, 8.1, 2.4), mat_brass=mat_brass, mat_flame=mat_flame)
    create_deepam(name="Deepam_2", location=(1.3, 8.1, 2.4), mat_brass=mat_brass, mat_flame=mat_flame)
    
    # 10. Subshrines on hilltop courtyard
    build_subshrine("Bhairava_Shrine", location=(-7.5, 6.0, 2.4), deity_type="bhairava", mat_stone=mat_dark_sandstone, mat_gold=mat_gold, mat_black=mat_black)
    build_subshrine("Ganesha_Shrine", location=(7.5, 6.0, 2.4), deity_type="ganesha", mat_stone=mat_dark_sandstone, mat_gold=mat_gold, mat_black=mat_black)
    
    # 11. Sacred Falgu River Ghats Below
    build_falgu_river_ghat(location=(-20, 6, 0), depth=32.0, mat_stone=mat_dark_sandstone, mat_water=mat_water, mat_sand=mat_sand)
    
    # 12. Spawn_Point (at base of hill staircase facing up)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -14, 0.1))
    spawn = bpy.context.active_object
    spawn.name = "Spawn_Point"
    
    # 13. Export GLB
    output_path = r"d:\Kshetra_Darshan\godot\assets\models\gaya_mangalagauri_kshetra_full.glb"
    export_glb(output_path)
    print("Successfully built authentic Gaya Mangalagauri Temple GLB!")

if __name__ == "__main__":
    main()
