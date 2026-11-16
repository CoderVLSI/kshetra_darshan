"""
Blender 5.3 Build Script for Lanka Shankari Temple (Kshetra #18)
Architecture: CLIFFSIDE Ocean-view Dravidian Sanctum (Swami Rock, Trincomalee)
Features: Vast Indian Ocean plane, coastal sea rocks, sheer granite cliffs, Dravidian Vimana
Deity: Authentic 4-armed Devi Shankari - Trishula, Damaru, Abhaya, Varada,
       golden crown, royal silk saree, and radiant silver Prabhavali arch
Output: d:\\Kshetra_Darshan\\godot\\assets\\models\\lanka_shankari_kshetra_full.glb
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
    create_granite_stone, create_gold_metal, create_water,
    create_brass_metal, create_black_stone, create_flame_emission,
    create_skin, create_white_dhoti, create_sandstone,
    create_flower_garland, create_white_marble, create_kumkum_red,
    create_red_silk
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_hanging_bell, create_deepam, create_human_figure,
    create_ground_plane, export_glb
)

def build_swami_rock_cliff(location=(0, 6, 0), width=28.0, depth=30.0, cliff_h=3.5, mat_cliff=None, mat_ocean=None):
    """Build dramatic Swami Rock cliff plateau with sheer drops, coastal rocks, and vast ocean."""
    objs = []
    cx, cy, cz = location
    
    # Vast Indian Ocean water plane (Z = -2.5, extending wide)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy + 10, cz - 2.5))
    ocean = bpy.context.active_object
    ocean.scale = (50, 50, 1)
    ocean.name = "Indian_Ocean_Water"
    bpy.ops.object.transform_apply(scale=True)
    if mat_ocean: ocean.data.materials.append(mat_ocean)
    objs.append(ocean)
    
    # Coastal jagged sea rocks jutting from the ocean below the cliffs
    rock_coords = [
        (cx - 18, cy + 18, cz - 2.5, 3.2, 2.5, 2.8),
        (cx - 12, cy + 24, cz - 2.5, 4.0, 3.0, 3.5),
        (cx + 14, cy + 20, cz - 2.5, 3.5, 2.8, 3.0),
        (cx + 20, cy + 12, cz - 2.5, 4.5, 3.5, 3.2),
        (cx - 22, cy + 5, cz - 2.5, 3.8, 4.0, 2.9),
    ]
    for i, (rx, ry, rz, sx, sy, sz) in enumerate(rock_coords):
        bpy.ops.mesh.primitive_cube_add(size=2, location=(rx, ry, rz + sz/2))
        rock = bpy.context.active_object
        rock.scale = (sx/2, sy/2, sz/2)
        rock.rotation_euler = (0.2 * i, -0.3 * i, 0.4 * i)
        rock.name = f"Coastal_Sea_Rock_{i+1}"
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        if mat_cliff: rock.data.materials.append(mat_cliff)
        objs.append(rock)
        
    # Massive granite cliff plateau base
    bpy.ops.mesh.primitive_cube_add(size=2, location=(cx, cy, cz + (cliff_h - 2.5)/2))
    plateau = bpy.context.active_object
    plateau.scale = (width/2, depth/2, (cliff_h + 2.5)/2)
    plateau.name = "Swami_Rock_Plateau"
    bpy.ops.object.transform_apply(scale=True)
    if mat_cliff: plateau.data.materials.append(mat_cliff)
    objs.append(plateau)
    
    # Cliffside stone parapet along North and East ocean edges
    bpy.ops.mesh.primitive_cube_add(size=2, location=(cx, cy + depth/2 - 0.2, cz + cliff_h + 0.6))
    p_n = bpy.context.active_object
    p_n.scale = (width/2, 0.25, 0.6)
    p_n.name = "Ocean_Parapet_North"
    bpy.ops.object.transform_apply(scale=True)
    if mat_cliff: p_n.data.materials.append(mat_cliff)
    objs.append(p_n)
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(cx + width/2 - 0.2, cy, cz + cliff_h + 0.6))
    p_e = bpy.context.active_object
    p_e.scale = (0.25, depth/2, 0.6)
    p_e.name = "Ocean_Parapet_East"
    bpy.ops.object.transform_apply(scale=True)
    if mat_cliff: p_e.data.materials.append(mat_cliff)
    objs.append(p_e)
    
    # Grand stone staircase from ground approach (Z=0) up to cliff level (cliff_h)
    stairs_count = 14
    step_w = 4.2
    step_d = 0.55
    step_h = cliff_h / stairs_count
    for i in range(stairs_count):
        sy = cy - depth/2 - (stairs_count - i - 0.5) * step_d
        sz = i * step_h + step_h/2
        bpy.ops.mesh.primitive_cube_add(size=2, location=(cx, sy, sz))
        step = bpy.context.active_object
        step.scale = (step_w/2, step_d/2, step_h/2)
        step.name = f"Cliff_Stair_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_cliff: step.data.materials.append(mat_cliff)
        objs.append(step)
        
    return objs

def build_dravidian_cliff_vimana(name="Shankari_Vimana", location=(0, 11, 3.5), width=6.0, height=12.5, mat_stone=None, mat_gold=None):
    """Build tiered Dravidian Vimana atop cliff sanctum."""
    objs = []
    x, y, z = location
    bada_h = 4.2
    spire_h = height - bada_h
    tiers = 6
    tier_h = spire_h / tiers
    
    for i in range(tiers):
        t = i / float(tiers)
        scale_fac = 1.0 - 0.52 * t
        tw = (width / 2) * scale_fac
        tz = z + bada_h + i * tier_h + tier_h / 2
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        tier = bpy.context.active_object
        tier.scale = (tw, tw, tier_h / 2)
        tier.name = f"{name}_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: tier.data.materials.append(mat_stone)
        objs.append(tier)
        
    # Sala barrel-vault crown & Golden Kalasha
    shikh_top = z + bada_h + spire_h
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=width * 0.22, depth=0.8, location=(x, y, shikh_top + 0.4))
    sala = bpy.context.active_object
    sala.rotation_euler = (0, math.pi / 2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    sala.name = f"{name}_SalaDome"
    if mat_stone: sala.data.materials.append(mat_stone)
    objs.append(sala)
    
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.28, radius2=0.04, depth=1.1, location=(x, y, shikh_top + 1.2))
    kalasha = bpy.context.active_object
    kalasha.name = f"{name}_Kalasha"
    if mat_gold: kalasha.data.materials.append(mat_gold)
    objs.append(kalasha)
    
    return objs

def create_authentic_shankari_murti(name="Deity_Shankari", location=(0, 11.8, 3.6), mat_granite=None, mat_gold=None, mat_silver=None, mat_silk=None):
    """
    Creates the authentic canonical Shankari Devi Murti of Lanka (Trincomalee):
    - 4-armed standing black granite Goddess
    - Upper Right: holds sacred Trishula (trident)
    - Upper Left: holds Damaru with coiled Naga cobra
    - Lower Right: Abhaya Mudra
    - Lower Left: Varada Mudra / Panapatra
    - Draped in rich silk saree, tall Kireeta Mukuta crown, and radiant silver Prabhavali arch
    """
    parts = []
    x, y, z = location
    
    # 1. High Granite Pedestal (Padma Pitha)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.9, depth=0.25, location=(x, y, z + 0.125))
    ped = bpy.context.active_object
    ped.name = f"{name}_Pedestal"
    if mat_granite: ped.data.materials.append(mat_granite)
    parts.append(ped)
    
    # Lotus Footing
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.75, depth=0.15, location=(x, y, z + 0.32))
    lotus = bpy.context.active_object
    if mat_gold: lotus.data.materials.append(mat_gold)
    parts.append(lotus)
    
    # 2. Devi Lower Body (Standing upright, draped in silk saree)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.24, depth=0.68, location=(x, y, z + 0.72))
    legs = bpy.context.active_object
    legs.name = f"{name}_LowerBody"
    if mat_silk: legs.data.materials.append(mat_silk)
    parts.append(legs)
    
    # 3. Devi Torso & Chest
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 1.25))
    torso = bpy.context.active_object
    torso.scale = (0.24, 0.15, 0.28)
    bpy.ops.object.transform_apply(scale=True)
    torso.name = f"{name}_Torso"
    if mat_granite: torso.data.materials.append(mat_granite)
    parts.append(torso)
    
    # Gold Necklaces & Kasumala
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.03, location=(x, y - 0.05, z + 1.35))
    hara = bpy.context.active_object
    if mat_gold: hara.data.materials.append(mat_gold)
    parts.append(hara)
    
    # 4. Devi Divine Face
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(x, y, z + 1.58))
    face = bpy.context.active_object
    face.name = f"{name}_Face"
    if mat_granite: face.data.materials.append(mat_granite)
    parts.append(face)
    
    # Kumkum Tilak
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(x, y - 0.13, z + 1.62))
    tilak = bpy.context.active_object
    if mat_silk: tilak.data.materials.append(mat_silk)
    parts.append(tilak)
    
    # Golden Kireeta Mukuta Crown
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.14, radius2=0.03, depth=0.45, location=(x, y, z + 1.90))
    crown = bpy.context.active_object
    crown.name = f"{name}_Crown"
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)
    
    # 5. Four Divine Arms & Sacred Ayudhas
    # Upper Right: Trishula (Trident)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.45, location=(x + 0.38, y, z + 1.35))
    arm_ur = bpy.context.active_object
    arm_ur.rotation_euler = (0, 0.5, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_granite: arm_ur.data.materials.append(mat_granite)
    parts.append(arm_ur)
    
    # Golden Trishula
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=1.4, location=(x + 0.55, y - 0.05, z + 1.6))
    trishula_shaft = bpy.context.active_object
    if mat_gold: trishula_shaft.data.materials.append(mat_gold)
    parts.append(trishula_shaft)
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.08, radius2=0.01, depth=0.25, location=(x + 0.55, y - 0.05, z + 2.35))
    prong = bpy.context.active_object
    if mat_gold: prong.data.materials.append(mat_gold)
    parts.append(prong)
    
    # Upper Left: Damaru (Cosmic Drum)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.45, location=(x - 0.38, y, z + 1.35))
    arm_ul = bpy.context.active_object
    arm_ul.rotation_euler = (0, -0.5, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_granite: arm_ul.data.materials.append(mat_granite)
    parts.append(arm_ul)
    
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.06, radius2=0.02, depth=0.12, location=(x - 0.55, y - 0.05, z + 1.62))
    damaru = bpy.context.active_object
    if mat_gold: damaru.data.materials.append(mat_gold)
    parts.append(damaru)
    
    # Lower Right: Abhaya Mudra
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.032, depth=0.36, location=(x + 0.26, y - 0.08, z + 1.05))
    arm_lr = bpy.context.active_object
    arm_lr.rotation_euler = (0.5, 0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_granite: arm_lr.data.materials.append(mat_granite)
    parts.append(arm_lr)
    
    # Lower Left: Varada Mudra / Panapatra
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.032, depth=0.36, location=(x - 0.26, y - 0.08, z + 1.05))
    arm_ll = bpy.context.active_object
    arm_ll.rotation_euler = (0.5, -0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_granite: arm_ll.data.materials.append(mat_granite)
    parts.append(arm_ll)
    
    # 6. Radiant Silver Prabhavali Arch behind Devi
    bpy.ops.mesh.primitive_torus_add(major_radius=0.88, minor_radius=0.07, location=(x, y + 0.1, z + 1.45))
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_silver: prabha.data.materials.append(mat_silver)
    parts.append(prabha)
    
    # Join into single unified Deity object
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = ped
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = name
    return deity

def build_cliff_mandapa(name="Mandapa", location=(0, 4.0, 3.5), width=8.5, depth=7.5, height=3.6, mat_stone=None, mat_marble=None, mat_gold=None):
    """Build Dravidian Cliffside Mandapa (Pillared Hall)."""
    objs = []
    x, y, z = location
    hw = width / 2
    hd = depth / 2
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.1))
    floor = bpy.context.active_object
    floor.scale = (hw, hd, 0.1)
    floor.name = f"{name}_Floor"
    bpy.ops.object.transform_apply(scale=True)
    if mat_marble: floor.data.materials.append(mat_marble)
    objs.append(floor)
    
    for px in [-3.0, -1.0, 1.0, 3.0]:
        for py in [y - 2.8, y, y + 2.8]:
            p = create_pillar(f"{name}_Pillar_{px}_{py}", (px, py, z + 0.2), height=height - 0.2, radius=0.2, mat=mat_stone, style="square")
            objs.append(p)
            
    roof_z = z + height + 0.15
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, roof_z))
    roof = bpy.context.active_object
    roof.scale = (hw + 0.4, hd + 0.4, 0.15)
    roof.name = f"{name}_Roof"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)
    
    return objs

def build_subshrine(name, location, deity_type="bhairava", mat_stone=None, mat_gold=None, mat_black=None):
    """Build subshrine joined into single mesh."""
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
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y + sd/2 - 0.2, z + 0.3 + sh/2))
    wb = bpy.context.active_object
    wb.scale = (sw/2, 0.2, sh/2)
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: wb.data.materials.append(mat_stone)
    objs.append(wb)
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=sw*0.7, radius2=0.15, depth=1.8, location=(x, y, z + 0.3 + sh + 0.9))
    roof = bpy.context.active_object
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(x, y, z + 0.3 + sh + 1.9))
    kal = bpy.context.active_object
    if mat_gold: kal.data.materials.append(mat_gold)
    objs.append(kal)
    
    # Icon
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=0.45, location=(x, y, z + 0.55))
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
    mat_granite = create_granite_stone("Swami_Rock_Granite", color=(0.28, 0.26, 0.24, 1.0))
    mat_gold = create_gold_metal("Shankari_Gold")
    mat_silver = create_white_marble("Shankari_Silver", color=(0.92, 0.94, 0.96, 1.0), roughness=0.15)
    mat_ocean = create_water("Indian_Ocean_Water_Mat", color=(0.08, 0.45, 0.58, 0.88))
    mat_sandstone = create_sandstone("Approach_Sandstone", color=(0.72, 0.65, 0.52, 1.0))
    mat_marble = create_white_marble("Mandapa_Marble")
    mat_brass = create_brass_metal("Bell_Brass")
    mat_flame = create_flame_emission("Deepam_Flame", strength=8.5)
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_silk = create_kumkum_red("Shankari_Silk_Sari", color=(0.88, 0.12, 0.12, 1.0))
    mat_black = create_black_stone("Black_Basalt")
    
    # 1. Main Ground
    ground = create_ground_plane(name="Ground_Main", size=75, mat=mat_sandstone)
    
    # 2. Dramatic Swami Rock Cliff Plateau & Indian Ocean
    build_swami_rock_cliff(location=(0, 6, 0), width=28.0, depth=30.0, cliff_h=3.5, mat_cliff=mat_granite, mat_ocean=mat_ocean)
    
    # 3. Garbhagriha Walls atop Cliff (Z = 3.5)
    garbha_walls = create_garbhagriha(
        name="Garbhagriha_Walls",
        location=(0, 11, 3.5),
        width=5.8,
        depth=5.8,
        wall_height=4.4,
        wall_thickness=0.5,
        mat=mat_granite,
        door_width=2.2,
        door_height=3.0
    )
    bpy.ops.object.select_all(action='DESELECT')
    for obj in garbha_walls: obj.select_set(True)
    bpy.context.view_layer.objects.active = garbha_walls[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"
    
    # 4. Dravidian Vimana Tower atop Cliff Sanctum
    build_dravidian_cliff_vimana(name="Shankari_Vimana", location=(0, 11, 3.5), width=6.0, height=12.5, mat_stone=mat_granite, mat_gold=mat_gold)
    
    # 5. Cliffside Mandapa (Preceding Pillared Hall)
    mandapa_parts = build_cliff_mandapa(name="Mandapa", location=(0, 4.0, 3.5), width=8.5, depth=7.5, height=3.6, mat_stone=mat_granite, mat_marble=mat_marble, mat_gold=mat_gold)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mandapa_parts: obj.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_parts[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"
    
    # 6. Authentic Deity: Devi Shankari (4-armed, Trishula, Damaru, Abhaya, Varada, Silver Prabhavali)
    create_authentic_shankari_murti(name="Deity_Shankari", location=(0, 11.8, 3.6), mat_granite=mat_granite, mat_gold=mat_gold, mat_silver=mat_silver, mat_silk=mat_silk)
    
    # 7. Priest
    create_human_figure(name="Priest", location=(1.5, 10.2, 3.5), height=1.7, mat_skin=mat_skin, mat_cloth=mat_dhoti)
    
    # 8. Ghanta (Hanging Temple Bell in mandapa entrance)
    create_hanging_bell(name="Ghanta", location=(0, 0.4, 6.5), mat_brass=mat_brass, scale=1.3)
    
    # 9. Deepams flanking sanctum doorway atop cliff
    create_deepam(name="Deepam_1", location=(-1.3, 8.1, 3.5), mat_brass=mat_brass, mat_flame=mat_flame)
    create_deepam(name="Deepam_2", location=(1.3, 8.1, 3.5), mat_brass=mat_brass, mat_flame=mat_flame)
    
    # 10. Subshrines on cliff plateau
    build_subshrine("Bhairava_Shrine", location=(-9.0, 6.0, 3.5), deity_type="bhairava", mat_stone=mat_granite, mat_gold=mat_gold, mat_black=mat_black)
    build_subshrine("Ganesha_Shrine", location=(9.0, 6.0, 3.5), deity_type="ganesha", mat_stone=mat_granite, mat_gold=mat_gold, mat_black=mat_black)
    
    # 11. Spawn_Point (at bottom of cliff ascent stairs facing North)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -18.5, 0.1))
    spawn = bpy.context.active_object
    spawn.name = "Spawn_Point"
    
    # 12. Export GLB
    output_path = r"d:\Kshetra_Darshan\godot\assets\models\lanka_shankari_kshetra_full.glb"
    export_glb(output_path)
    print("Successfully built authentic Lanka Shankari Temple GLB!")

if __name__ == "__main__":
    main()
