"""
Blender 5.3 Build Script for Prayag Madhaveswari Temple (Kshetra #15)
Architecture: Nagara Mandapa with Sacred Jhula (Swing/Cradle) & Triveni Sangam River
Deity: Jhula (Cradle/Swing) as Deity_Madhaveswari (NO murti - Prayagraj Alopi Devi tradition)
Output: d:\\Kshetra_Darshan\\godot\\assets\\models\\prayag_madhaveswari_kshetra_full.glb
"""
import os
import sys
import math
import bpy
from mathutils import Vector

# Ensure blender directory in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from common_materials import (
    create_sandstone, create_brass_metal, create_red_silk,
    create_gold_metal, create_water, create_flame_emission,
    create_skin, create_white_dhoti, create_white_marble,
    create_flower_garland, create_black_stone, create_wood
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_hanging_bell, create_deepam, create_human_figure,
    create_ground_plane, export_glb
)


def build_sacred_jhula(name="Deity_Madhaveswari", location=(0, 11, 0.1), mat_brass=None, mat_silk=None, mat_gold=None, mat_garland=None, mat_marble=None):
    """Build the sacred Divine Jhula (cradle/swing) representing Devi Madhaveswari (NO murti)."""
    objs = []
    x, y, z = location
    
    # 1. Octagonal Marble Platform / Peetha
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.6, depth=0.3, location=(x, y, z + 0.15))
    peetha = bpy.context.active_object
    peetha.name = f"{name}_Peetha"
    if mat_marble: peetha.data.materials.append(mat_marble)
    objs.append(peetha)
    
    # Inner raised brass pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.2, depth=0.15, location=(x, y, z + 0.38))
    ped = bpy.context.active_object
    ped.name = f"{name}_BrassPedestal"
    if mat_brass: ped.data.materials.append(mat_brass)
    objs.append(ped)
    
    # 2. Ornate Jhula Archway Frame (Torana)
    # Left upright carved post
    post_w = 0.95
    post_h = 2.4
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=post_h, location=(x - post_w, y, z + 0.45 + post_h/2))
    post_l = bpy.context.active_object
    post_l.name = f"{name}_Post_L"
    if mat_brass: post_l.data.materials.append(mat_brass)
    objs.append(post_l)
    
    # Right upright carved post
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=post_h, location=(x + post_w, y, z + 0.45 + post_h/2))
    post_r = bpy.context.active_object
    post_r.name = f"{name}_Post_R"
    if mat_brass: post_r.data.materials.append(mat_brass)
    objs.append(post_r)
    
    # Crossbeam joining the posts
    beam_len = post_w * 2 + 0.4
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=beam_len, location=(x, y, z + 0.45 + post_h))
    beam = bpy.context.active_object
    beam.rotation_euler = (0, math.pi/2, 0)
    beam.name = f"{name}_CrossBeam"
    bpy.ops.object.transform_apply(rotation=True)
    if mat_brass: beam.data.materials.append(mat_brass)
    objs.append(beam)
    
    # Golden finials on top of posts and crossbeam
    for fx in [-post_w, 0, post_w]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x + fx, y, z + 0.45 + post_h + 0.2))
        fin = bpy.context.active_object
        fin.name = f"{name}_Finial_{fx}"
        if mat_gold: fin.data.materials.append(mat_gold)
        objs.append(fin)
        
    # Golden Chhatra (sacred umbrella) above the Jhula
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.6, radius2=0.05, depth=0.25, location=(x, y, z + 0.45 + post_h - 0.15))
    chhatra = bpy.context.active_object
    chhatra.name = f"{name}_Chhatra"
    if mat_gold: chhatra.data.materials.append(mat_gold)
    objs.append(chhatra)
    
    # 3. Hanging Brass Chains
    chain_h = 1.3
    for cx in [-0.55, 0.55]:
        for cy in [-0.25, 0.25]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.018, depth=chain_h, location=(x + cx, y + cy, z + 0.45 + post_h - chain_h/2))
            chain = bpy.context.active_object
            chain.name = f"{name}_Chain_{cx}_{cy}"
            if mat_brass: chain.data.materials.append(mat_brass)
            objs.append(chain)
            
    # 4. Sacred Swing Cradle (Jhula Seat)
    seat_z = z + 0.45 + post_h - chain_h
    seat_w = 1.2
    seat_d = 0.65
    
    # Brass cradle frame
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, seat_z))
    seat_frame = bpy.context.active_object
    seat_frame.scale = (seat_w/2, seat_d/2, 0.05)
    seat_frame.name = f"{name}_SeatFrame"
    bpy.ops.object.transform_apply(scale=True)
    if mat_brass: seat_frame.data.materials.append(mat_brass)
    objs.append(seat_frame)
    
    # Cradle backrest and railings
    for rx in [-seat_w/2 + 0.04, seat_w/2 - 0.04]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x + rx, y, seat_z + 0.12))
        rail = bpy.context.active_object
        rail.scale = (0.04, seat_d/2, 0.12)
        rail.name = f"{name}_Railing_{rx}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_brass: rail.data.materials.append(mat_brass)
        objs.append(rail)
        
    # 5. Red Silk Bedding / Cushion (Adorned sacred seat of Devi)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, seat_z + 0.08))
    silk_cushion = bpy.context.active_object
    silk_cushion.scale = (seat_w/2 - 0.06, seat_d/2 - 0.06, 0.06)
    silk_cushion.name = f"{name}_RedSilkCushion"
    bpy.ops.object.transform_apply(scale=True)
    if mat_silk: silk_cushion.data.materials.append(mat_silk)
    objs.append(silk_cushion)
    
    # Red silk bolster / pillows at ends
    for bx in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=seat_d - 0.14, location=(x + bx, y, seat_z + 0.16))
        bolster = bpy.context.active_object
        bolster.rotation_euler = (math.pi/2, 0, 0)
        bolster.name = f"{name}_Bolster_{bx}"
        bpy.ops.object.transform_apply(rotation=True)
        if mat_silk: bolster.data.materials.append(mat_silk)
        objs.append(bolster)
        
    # Sacred Padukas (golden divine footprints) resting on the silk swing
    for px in [-0.08, 0.08]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x + px, y, seat_z + 0.16))
        paduka = bpy.context.active_object
        paduka.scale = (0.04, 0.09, 0.02)
        paduka.name = f"{name}_Paduka_{px}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_gold: paduka.data.materials.append(mat_gold)
        objs.append(paduka)
        
    # Flower garland draped along the cradle
    bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.04, location=(x, y - seat_d/2, seat_z + 0.04))
    garland = bpy.context.active_object
    garland.name = f"{name}_Garland"
    if mat_garland: garland.data.materials.append(mat_garland)
    objs.append(garland)
    
    # Join all elements into single object named Deity_Madhaveswari
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = peetha
    bpy.ops.object.join()
    jhula = bpy.context.active_object
    jhula.name = name
    return jhula


def build_nagara_shikhara(name="Nagara_Shikhara", location=(0, 11, 0), width=6.2, height=13.5, mat_stone=None, mat_gold=None):
    """Build Nagara Shikhara with curvilinear towers, amalaka, and kalasha."""
    objs = []
    x, y, z = location
    bada_h = 4.4
    spire_h = height - bada_h
    tiers = 8
    tier_h = spire_h / tiers
    
    for i in range(tiers):
        t = i / float(tiers)
        scale_fac = 1.0 - 0.48 * (t ** 1.5)
        tw = (width / 2) * scale_fac
        tz = z + bada_h + i * tier_h + tier_h/2
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        tier = bpy.context.active_object
        tier.scale = (tw, tw, tier_h/2)
        tier.name = f"{name}_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: tier.data.materials.append(mat_stone)
        objs.append(tier)
        
    # Amalaka disc
    crown_z = z + height
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=width * 0.28, depth=0.45, location=(x, y, crown_z + 0.25))
    am = bpy.context.active_object
    am.name = f"{name}_Amalaka"
    if mat_stone: am.data.materials.append(mat_stone)
    objs.append(am)
    
    # Golden Kalasha
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(x, y, crown_z + 0.75))
    kal = bpy.context.active_object
    kal.scale = (1, 1, 1.4)
    kal.name = f"{name}_Kalasha"
    bpy.ops.object.transform_apply(scale=True)
    if mat_gold: kal.data.materials.append(mat_gold)
    objs.append(kal)
    
    return objs


def build_nagara_mandapa(name="Mandapa", location=(0, 3.5, 0), width=8.5, depth=7.5, height=3.6, mat_stone=None, mat_gold=None):
    """Build pillared Nagara mandapa hall and join into single object named Mandapa."""
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
    
    # Square carved Nagara pillars
    for px in [-3.0, -1.2, 1.2, 3.0]:
        for py in [y - 2.8, y, y + 2.8]:
            p = create_pillar(f"{name}_Pillar_{px}_{py}", (px, py, z + 0.2), height=height - 0.2, radius=0.2, mat=mat_stone, style="square")
            objs.append(p)
            
    # Mandapa pyramid stepped roof (Phamsana style)
    roof_z = z + height
    for i in range(5):
        t = i / 4.0
        rw = (hw + 0.3) * (1.0 - t * 0.55)
        rd = (hd + 0.3) * (1.0 - t * 0.55)
        tz = roof_z + i * 0.35 + 0.17
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        rt = bpy.context.active_object
        rt.scale = (rw, rd, 0.17)
        rt.name = f"{name}_RoofTier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: rt.data.materials.append(mat_stone)
        objs.append(rt)
        
    # Kalasha on mandapa
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x, y, roof_z + 1.95))
    m_kal = bpy.context.active_object
    m_kal.name = f"{name}_MandapaKalasha"
    if mat_gold: m_kal.data.materials.append(mat_gold)
    objs.append(m_kal)
    
    # Join into single object named Mandapa
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = floor
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = name
    return mandapa


def build_triveni_sangam_ghat(location=(22, 5, 0), depth=32.0, mat_stone=None, mat_water_ganga=None, mat_water_yamuna=None, mat_wood=None):
    """Build Triveni Sangam confluence with two distinct water channels, ghat steps, and pilgrimage boats."""
    objs = []
    gx, gy, gz = location
    
    # Ganga Water Plane (pale sacred translucent green)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(gx + 8, gy + 8, gz - 1.2))
    w_ganga = bpy.context.active_object
    w_ganga.scale = (9, depth/4 + 4, 1)
    w_ganga.name = "Ganga_Water"
    bpy.ops.object.transform_apply(scale=True)
    if mat_water_ganga: w_ganga.data.materials.append(mat_water_ganga)
    objs.append(w_ganga)
    
    # Yamuna Water Plane (deep blue-green sacred water)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(gx + 8, gy - 8, gz - 1.2))
    w_yamuna = bpy.context.active_object
    w_yamuna.scale = (9, depth/4 + 4, 1)
    w_yamuna.name = "Yamuna_Water"
    bpy.ops.object.transform_apply(scale=True)
    if mat_water_yamuna: w_yamuna.data.materials.append(mat_water_yamuna)
    objs.append(w_yamuna)
    
    # Stepped Sangam Ghat terraces
    for i in range(8):
        sx = gx + (8 - i) * 0.7
        sz = gz - i * 0.16
        bpy.ops.mesh.primitive_cube_add(size=2, location=(sx, gy, sz))
        step = bpy.context.active_object
        step.scale = (0.7/2, depth/2, 0.16/2)
        step.name = f"Sangam_Step_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: step.data.materials.append(mat_stone)
        objs.append(step)
        
    # Pilgrimage wooden boat (Nauka) moored at ghat
    bpy.ops.mesh.primitive_cube_add(size=2, location=(gx + 5.5, gy - 3.0, gz - 1.0))
    boat = bpy.context.active_object
    boat.scale = (0.6, 1.8, 0.25)
    boat.name = "Sangam_PilgrimBoat"
    bpy.ops.object.transform_apply(scale=True)
    if mat_wood: boat.data.materials.append(mat_wood)
    objs.append(boat)
    
    return objs


def build_subshrine(name, location, deity_type="bhairava", mat_stone=None, mat_gold=None, mat_black=None):
    """Build subshrine and join into single named object."""
    objs = []
    x, y, z = location
    sw, sd, sh = 3.2, 3.2, 2.8
    
    # Base
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.15))
    plat = bpy.context.active_object
    plat.scale = (sw/2 + 0.2, sd/2 + 0.2, 0.15)
    plat.name = f"{name}_Plat"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: plat.data.materials.append(mat_stone)
    objs.append(plat)
    
    # 3 Walls
    # Back
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y + sd/2 - 0.2, z + 0.3 + sh/2))
    wb = bpy.context.active_object
    wb.scale = (sw/2, 0.2, sh/2)
    wb.name = f"{name}_WallB"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: wb.data.materials.append(mat_stone)
    objs.append(wb)
    
    # Left
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x - sw/2 + 0.2, y, z + 0.3 + sh/2))
    wl = bpy.context.active_object
    wl.scale = (0.2, sd/2, sh/2)
    wl.name = f"{name}_WallL"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: wl.data.materials.append(mat_stone)
    objs.append(wl)
    
    # Right
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x + sw/2 - 0.2, y, z + 0.3 + sh/2))
    wr = bpy.context.active_object
    wr.scale = (0.2, sd/2, sh/2)
    wr.name = f"{name}_WallR"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: wr.data.materials.append(mat_stone)
    objs.append(wr)
    
    # Pillars
    p1 = create_pillar(f"{name}_P1", (x - sw/2 + 0.3, y - sd/2 + 0.2, z + 0.3), height=sh, radius=0.15, mat=mat_stone)
    objs.append(p1)
    p2 = create_pillar(f"{name}_P2", (x + sw/2 - 0.3, y - sd/2 + 0.2, z + 0.3), height=sh, radius=0.15, mat=mat_stone)
    objs.append(p2)
    
    # Pyramid roof
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=sw*0.7, radius2=0.15, depth=2.0, location=(x, y, z + 0.3 + sh + 1.0))
    roof = bpy.context.active_object
    roof.name = f"{name}_Roof"
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(x, y, z + 0.3 + sh + 2.1))
    kal = bpy.context.active_object
    kal.name = f"{name}_Kalasha"
    if mat_gold: kal.data.materials.append(mat_gold)
    objs.append(kal)
    
    # Murti / Linga inside
    if deity_type == "bhairava":
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.25, depth=0.15, location=(x, y, z + 0.38))
        yoni = bpy.context.active_object
        if mat_black: yoni.data.materials.append(mat_black)
        objs.append(yoni)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.12, depth=0.35, location=(x, y, z + 0.58))
        linga = bpy.context.active_object
        if mat_black: linga.data.materials.append(mat_black)
        objs.append(linga)
    else:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.6))
        g = bpy.context.active_object
        g.scale = (0.2, 0.15, 0.25)
        g.name = f"{name}_GaneshaIcon"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: g.data.materials.append(mat_stone)
        objs.append(g)
        
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = plat
    bpy.ops.object.join()
    res = bpy.context.active_object
    res.name = name
    return res


def main():
    clear_scene()
    
    # 1. Materials
    mat_sandstone = create_sandstone("Prayag_Sandstone", color=(0.78, 0.64, 0.46, 1.0))
    mat_brass = create_brass_metal("Prayag_Brass")
    mat_silk = create_red_silk("Prayag_Red_Silk")
    mat_gold = create_gold_metal("Prayag_Gold")
    mat_marble = create_white_marble("Prayag_Marble")
    mat_garland = create_flower_garland("Jhula_Garland")
    mat_black = create_black_stone("Black_Stone")
    mat_wood = create_wood("Pilgrim_Boat_Wood")
    mat_water_ganga = create_water("Ganga_Water_Mat", color=(0.18, 0.42, 0.40, 0.82))
    mat_water_yamuna = create_water("Yamuna_Water_Mat", color=(0.10, 0.28, 0.48, 0.88))
    mat_flame = create_flame_emission("Flame_Glow")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    
    # 2. Main Ground Plane
    ground = create_ground_plane(name="Ground_Main", size=70, mat=mat_sandstone)
    
    # 3. Sanctum (Garbhagriha) Walls
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
    for obj in garbha_walls:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = garbha_walls[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"
    
    # 4. Nagara Shikhara Tower
    build_nagara_shikhara(name="Prayag_Shikhara", location=(0, 11, 0), width=6.4, height=14.0, mat_stone=mat_sandstone, mat_gold=mat_gold)
    
    # 5. Nagara Mandapa
    build_nagara_mandapa(name="Mandapa", location=(0, 3.5, 0), width=8.5, depth=7.5, height=3.6, mat_stone=mat_sandstone, mat_gold=mat_gold)
    
    # 6. SACRED JHULA (Swing/Cradle) as Deity_Madhaveswari (NO murti)
    build_sacred_jhula(
        name="Deity_Madhaveswari",
        location=(0, 11.5, 0.1),
        mat_brass=mat_brass,
        mat_silk=mat_silk,
        mat_gold=mat_gold,
        mat_garland=mat_garland,
        mat_marble=mat_marble
    )
    
    # 7. Priest
    create_human_figure(name="Priest", location=(1.5, 10.2, 0), height=1.7, mat_skin=mat_skin, mat_cloth=mat_dhoti)
    
    # 8. Ghanta (Hanging Temple Bell in mandapa entrance)
    create_hanging_bell(name="Ghanta", location=(0, -0.2, 3.0), mat_brass=mat_brass, scale=1.3)
    
    # 9. Deepams flanking sanctum doorway
    create_deepam(name="Deepam_1", location=(-1.3, 8.0, 0), mat_brass=mat_brass, mat_flame=mat_flame)
    create_deepam(name="Deepam_2", location=(1.3, 8.0, 0), mat_brass=mat_brass, mat_flame=mat_flame)
    
    # 10. Subshrines
    # Bhairava Shrine (West courtyard)
    build_subshrine("Bhairava_Shrine", location=(-10, 5, 0), deity_type="bhairava", mat_stone=mat_sandstone, mat_gold=mat_gold, mat_black=mat_black)
    
    # Ganesha Shrine (East courtyard)
    build_subshrine("Ganesha_Shrine", location=(10, 5, 0), deity_type="ganesha", mat_stone=mat_sandstone, mat_gold=mat_gold, mat_black=mat_black)
    
    # 11. Triveni Sangam River Ghat on East side
    build_triveni_sangam_ghat(location=(20, 5, 0), depth=32.0, mat_stone=mat_sandstone, mat_water_ganga=mat_water_ganga, mat_water_yamuna=mat_water_yamuna, mat_wood=mat_wood)
    
    # 12. Spawn_Point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -14, 0.1))
    spawn = bpy.context.active_object
    spawn.name = "Spawn_Point"
    
    # 13. Export GLB
    output_path = r"d:\Kshetra_Darshan\godot\assets\models\prayag_madhaveswari_kshetra_full.glb"
    export_glb(output_path)
    print("Successfully built and exported Prayag Madhaveswari Temple GLB!")


if __name__ == "__main__":
    main()
