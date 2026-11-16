"""
Blender 5.3 Build Script for Jajpur Biraja Temple (Kshetra #13)
Kalinga Architecture: Rekha Deula (sanctum) + Pidha Jagamohana (hall)
Deity: 2-armed Biraja (Dvi-bhuja Mahishasuramardini)
Features: Baitarani River Ghat, Vaitaraneeshwar Bhairava Shrine, Ganesha Shrine
Output: d:\\Kshetra_Darshan\\godot\\assets\\models\\jajpur_biraja_kshetra_full.glb
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
    create_sandstone, create_gold_metal, create_brass_metal,
    create_red_silk, create_water, create_flame_emission,
    create_skin, create_white_dhoti, create_flower_garland,
    create_black_stone, create_white_marble
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_hanging_bell, create_deepam, create_human_figure,
    create_ground_plane
)


def export_glb(filepath, apply_modifiers=True):
    """Export the scene as .glb for Godot import (Blender 5.3 compatible)."""
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


def build_kalinga_rekha_deula(name="Rekha_Deula", location=(0, 12, 0), width=7.0, height=16.0, mat_stone=None, mat_gold=None):
    """Build authentic Kalinga Rekha Deula tower with bada, gandi (curvilinear pagas), amalaka, kalasha, and dhwaja."""
    objs = []
    x, y, z = location
    
    # Bada (lower wall structure)
    bada_h = 4.5
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + bada_h/2))
    bada = bpy.context.active_object
    bada.scale = (width/2, width/2, bada_h/2)
    bada.name = f"{name}_Bada"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: bada.data.materials.append(mat_stone)
    objs.append(bada)
    
    # Gandi (spire with vertical pagas and curved taper)
    tiers = 10
    gandi_h = height - bada_h - 2.5
    tier_h = gandi_h / tiers
    for i in range(tiers):
        t = i / float(tiers)
        # Curvilinear parabola profile characteristic of Kalinga Rekha
        scale_fac = 1.0 - 0.45 * (t ** 1.8)
        tw = (width / 2) * scale_fac
        tz = z + bada_h + i * tier_h + tier_h/2
        
        # Central tier body
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        tier = bpy.context.active_object
        tier.scale = (tw, tw, tier_h/2)
        tier.name = f"{name}_Gandi_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: tier.data.materials.append(mat_stone)
        objs.append(tier)
        
        # Raha-paga (central projected vertical pilasters on 4 faces)
        paga_proj = tw * 1.06
        paga_w = tw * 0.45
        for px, py in [(x, y + tw), (x, y - tw), (x + tw, y), (x - tw, y)]:
            is_y = (abs(px - x) < 0.01)
            bpy.ops.mesh.primitive_cube_add(size=2, location=(px, py, tz))
            paga = bpy.context.active_object
            if is_y:
                paga.scale = (paga_w/2, 0.15, tier_h/2 * 0.95)
            else:
                paga.scale = (0.15, paga_w/2, tier_h/2 * 0.95)
            paga.name = f"{name}_RahaPaga_{i+1}"
            bpy.ops.object.transform_apply(scale=True)
            if mat_stone: paga.data.materials.append(mat_stone)
            objs.append(paga)
            
    # Mastaka (crowning section)
    # Beki (neck cylinder)
    mastaka_z = z + bada_h + gandi_h
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=width * 0.22, depth=0.5,
                                        location=(x, y, mastaka_z + 0.25))
    beki = bpy.context.active_object
    beki.name = f"{name}_Beki"
    if mat_stone: beki.data.materials.append(mat_stone)
    objs.append(beki)
    
    # Amalaka (fluted ribbed disc)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=width * 0.35, depth=0.6,
                                        location=(x, y, mastaka_z + 0.7))
    amalaka = bpy.context.active_object
    amalaka.name = f"{name}_Amalaka"
    if mat_stone: amalaka.data.materials.append(mat_stone)
    objs.append(amalaka)
    
    # Khapuri (skull cap convex disc)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=width * 0.25, depth=0.3,
                                        location=(x, y, mastaka_z + 1.1))
    khapuri = bpy.context.active_object
    khapuri.name = f"{name}_Khapuri"
    if mat_stone: khapuri.data.materials.append(mat_stone)
    objs.append(khapuri)
    
    # Golden Kalasha (water urn finial)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(x, y, mastaka_z + 1.5))
    kalasha = bpy.context.active_object
    kalasha.scale = (1, 1, 1.4)
    kalasha.name = f"{name}_Kalasha"
    bpy.ops.object.transform_apply(scale=True)
    if mat_gold: kalasha.data.materials.append(mat_gold)
    objs.append(kalasha)
    
    # Dhwaja / Trishula finial
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.2,
                                        location=(x, y, mastaka_z + 2.4))
    dhwaja = bpy.context.active_object
    dhwaja.name = f"{name}_Dhwaja"
    if mat_gold: dhwaja.data.materials.append(mat_gold)
    objs.append(dhwaja)
    
    return objs


def build_kalinga_pidha_jagamohana(name="Mandapa", location=(0, 3, 0), width=9.0, depth=8.0, height=4.0, mat_stone=None, mat_gold=None):
    """Build authentic Kalinga Pidha Jagamohana (pyramidal tiered assembly hall)."""
    objs = []
    x, y, z = location
    
    # Hall floor
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.1))
    floor = bpy.context.active_object
    floor.scale = (width/2, depth/2, 0.1)
    floor.name = f"{name}_Floor"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: floor.data.materials.append(mat_stone)
    objs.append(floor)
    
    # Hall perimeter walls with large front and back arched entrance openings
    hw = width / 2
    hd = depth / 2
    wt = 0.5
    
    # Left wall
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x - hw + wt/2, y, z + height/2))
    w_l = bpy.context.active_object
    w_l.scale = (wt/2, hd, height/2)
    w_l.name = f"{name}_Wall_L"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: w_l.data.materials.append(mat_stone)
    objs.append(w_l)
    
    # Right wall
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x + hw - wt/2, y, z + height/2))
    w_r = bpy.context.active_object
    w_r.scale = (wt/2, hd, height/2)
    w_r.name = f"{name}_Wall_R"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: w_r.data.materials.append(mat_stone)
    objs.append(w_r)
    
    # Front wall with entrance doorway (door width = 2.4m)
    door_w = 2.6
    side_w = (width - door_w) / 2
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x + sign * (door_w/2 + side_w/2), y - hd + wt/2, z + height/2))
        fw = bpy.context.active_object
        fw.scale = (side_w/2, wt/2, height/2)
        fw.name = f"{name}_FrontWall_{sign}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: fw.data.materials.append(mat_stone)
        objs.append(fw)
        
    # Front lintel above doorway
    lintel_h = height - 2.8
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y - hd + wt/2, z + 2.8 + lintel_h/2))
    lint = bpy.context.active_object
    lint.scale = (door_w/2, wt/2, lintel_h/2)
    lint.name = f"{name}_FrontLintel"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: lint.data.materials.append(mat_stone)
    objs.append(lint)
    
    # Interior carved pillars
    for px in [-2.5, 2.5]:
        for py in [y - 2.0, y + 2.0]:
            p = create_pillar(f"{name}_Pillar_{px}_{py}", (px, py, z), height=height, radius=0.22, mat=mat_stone, style="square")
            objs.append(p)
            
    # Pidha roof tiers (pyramidal stepped potalas)
    pidha_tiers = 6
    pidha_h = 3.5
    tier_h = pidha_h / pidha_tiers
    for i in range(pidha_tiers):
        t = i / float(pidha_tiers)
        pw = (width / 2 + 0.3) * (1.0 - t * 0.65)
        pd = (depth / 2 + 0.3) * (1.0 - t * 0.65)
        tz = z + height + i * tier_h + tier_h/2
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        pt = bpy.context.active_object
        pt.scale = (pw, pd, tier_h/2)
        pt.name = f"{name}_PidhaTier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: pt.data.materials.append(mat_stone)
        objs.append(pt)
        
    # Crowning bell (Ghanta) and Kalasha on Jagamohana
    crown_z = z + height + pidha_h
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=width * 0.16, depth=0.4,
                                        location=(x, y, crown_z + 0.2))
    ghanta_crown = bpy.context.active_object
    ghanta_crown.name = f"{name}_GhantaCrown"
    if mat_stone: ghanta_crown.data.materials.append(mat_stone)
    objs.append(ghanta_crown)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(x, y, crown_z + 0.65))
    k_crown = bpy.context.active_object
    k_crown.scale = (1, 1, 1.3)
    k_crown.name = f"{name}_KalashaCrown"
    bpy.ops.object.transform_apply(scale=True)
    if mat_gold: k_crown.data.materials.append(mat_gold)
    objs.append(k_crown)
    
    return objs


def create_two_armed_biraja(name="Deity_Biraja", location=(0, 12, 0.4), mat_stone=None, mat_ornament=None):
    """Create authentic 2-armed Biraja Devi (Dvi-bhuja Mahishasuramardini).
    Right hand thrusts spear (trishula) into Mahishasura demon.
    Left hand pulls the demon's hair / tail.
    Standing atop the buffalo demon at her feet.
    """
    objs = []
    x, y, z = location
    
    # Buffalo demon (Mahisha) body at base
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.15))
    buf = bpy.context.active_object
    buf.scale = (0.45, 0.25, 0.15)
    buf.name = f"{name}_Mahisha_Body"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: buf.data.materials.append(mat_stone)
    objs.append(buf)
    
    # Demon head with buffalo horns
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x - 0.35, y, z + 0.18))
    mhead = bpy.context.active_object
    mhead.scale = (0.15, 0.15, 0.12)
    mhead.name = f"{name}_Mahisha_Head"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: mhead.data.materials.append(mat_stone)
    objs.append(mhead)
    
    # Lotus Pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.6, depth=0.15, location=(x, y, z + 0.075))
    ped = bpy.context.active_object
    ped.name = f"{name}_Pedestal"
    if mat_ornament: ped.data.materials.append(mat_ornament)
    objs.append(ped)
    
    # Devi Torso
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.8))
    torso = bpy.context.active_object
    torso.scale = (0.22, 0.14, 0.32)
    torso.name = f"{name}_Torso"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: torso.data.materials.append(mat_stone)
    objs.append(torso)
    
    # Devi Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(x, y, z + 1.25))
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    if mat_stone: head.data.materials.append(mat_stone)
    objs.append(head)
    
    # Kiritamukuta (tall ornate crown)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.11, radius2=0.03, depth=0.3,
                                    location=(x, y, z + 1.48))
    crown = bpy.context.active_object
    crown.name = f"{name}_Crown"
    if mat_ornament: crown.data.materials.append(mat_ornament)
    objs.append(crown)
    
    # Right Arm (holding Trishula spearing downwards)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.045, depth=0.45,
                                        location=(x + 0.28, y - 0.05, z + 0.85))
    r_arm = bpy.context.active_object
    r_arm.rotation_euler = (0.3, 0.4, -0.2)
    r_arm.name = f"{name}_RightArm"
    bpy.ops.object.transform_apply(rotation=True)
    if mat_stone: r_arm.data.materials.append(mat_stone)
    objs.append(r_arm)
    
    # Trishula / Spear shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=1.6,
                                        location=(x + 0.15, y - 0.1, z + 0.8))
    spear = bpy.context.active_object
    spear.rotation_euler = (0.2, 0.6, -0.1)
    spear.name = f"{name}_Trishula_Shaft"
    bpy.ops.object.transform_apply(rotation=True)
    if mat_ornament: spear.data.materials.append(mat_ornament)
    objs.append(spear)
    
    # Left Arm (grasping the demon)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.045, depth=0.45,
                                        location=(x - 0.25, y - 0.05, z + 0.8))
    l_arm = bpy.context.active_object
    l_arm.rotation_euler = (-0.2, -0.5, 0.3)
    l_arm.name = f"{name}_LeftArm"
    bpy.ops.object.transform_apply(rotation=True)
    if mat_stone: l_arm.data.materials.append(mat_stone)
    objs.append(l_arm)
    
    # Legs (pratyalidha warrior posture)
    for sx, lx in [(-0.12, x - 0.1), (0.12, x + 0.12)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.065, depth=0.45,
                                            location=(lx, y, z + 0.42))
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg"
        if mat_stone: leg.data.materials.append(mat_stone)
        objs.append(leg)
        
    # Prabhavali (ornate halo aura ring behind Devi)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.04,
                                     location=(x, y + 0.1, z + 1.05))
    halo = bpy.context.active_object
    halo.rotation_euler = (math.pi/2, 0, 0)
    halo.name = f"{name}_Prabhavali"
    bpy.ops.object.transform_apply(rotation=True)
    if mat_ornament: halo.data.materials.append(mat_ornament)
    objs.append(halo)
    
    # Join into single object named Deity_Biraja
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = name
    return deity


def build_baitarani_ghat(location=(-22, 5, 0), width=14.0, depth=30.0, mat_stone=None, mat_water=None):
    """Build the sacred Baitarani (Vaitarani) river ghat with wide stone steps and water plane."""
    objs = []
    gx, gy, gz = location
    
    # River water plane (Z = -1.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(gx - 10, gy, gz - 1.0))
    water = bpy.context.active_object
    water.scale = (12, depth/2 + 5, 1)
    water.name = "Baitarani_Water"
    bpy.ops.object.transform_apply(scale=True)
    if mat_water: water.data.materials.append(mat_water)
    objs.append(water)
    
    # Ghat stepped terraces descending into water
    steps_count = 8
    step_w = 4.0
    step_h = 0.18
    for i in range(steps_count):
        sx = gx - (steps_count - i) * 0.6
        sz = gz - i * step_h
        bpy.ops.mesh.primitive_cube_add(size=2, location=(sx, gy, sz))
        step = bpy.context.active_object
        step.scale = (0.6/2, depth/2, step_h/2)
        step.name = f"Baitarani_Ghat_Step_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: step.data.materials.append(mat_stone)
        objs.append(step)
        
    # Ghat promenade upper platform
    bpy.ops.mesh.primitive_cube_add(size=2, location=(gx + 1.5, gy, gz - 0.05))
    prom = bpy.context.active_object
    prom.scale = (2.0, depth/2, 0.05)
    prom.name = "Baitarani_Promenade"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: prom.data.materials.append(mat_stone)
    objs.append(prom)
    
    # Riverside Chhatri / Bathing pavilion
    for cy in [gy - 8, gy + 8]:
        p = create_pillar(f"Ghat_Pillar_{cy}_1", (gx + 0.5, cy - 1.5, gz), height=2.8, radius=0.15, mat=mat_stone)
        objs.append(p)
        p2 = create_pillar(f"Ghat_Pillar_{cy}_2", (gx + 0.5, cy + 1.5, gz), height=2.8, radius=0.15, mat=mat_stone)
        objs.append(p2)
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.8, radius2=0.2, depth=1.0,
                                        location=(gx + 0.5, cy, gz + 3.3))
        roof = bpy.context.active_object
        roof.name = f"Ghat_Chhatri_Roof_{cy}"
        if mat_stone: roof.data.materials.append(mat_stone)
        objs.append(roof)
        
    return objs


def build_subshrine(name, location, style="kalinga", mat_stone=None, mat_gold=None):
    """Build a complete sub-shrine (Bhairava or Ganesha) and join into a single named object."""
    objs = []
    x, y, z = location
    sw, sd, sh = 3.2, 3.2, 2.8
    
    # Platform
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.15))
    plat = bpy.context.active_object
    plat.scale = (sw/2 + 0.2, sd/2 + 0.2, 0.15)
    plat.name = f"{name}_Plat"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: plat.data.materials.append(mat_stone)
    objs.append(plat)
    
    # Walls (3 solid walls, front open with doorway)
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
    
    # Front doorway pillars
    for px in [-sw/2 + 0.3, sw/2 - 0.3]:
        p = create_pillar(f"{name}_Pillar_{px}", (x + px, y - sd/2 + 0.2, z + 0.3), height=sh, radius=0.15, mat=mat_stone)
        objs.append(p)
        
    # Front lintel
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y - sd/2 + 0.2, z + 0.3 + sh - 0.2))
    lint = bpy.context.active_object
    lint.scale = (sw/2, 0.25, 0.2)
    lint.name = f"{name}_Lintel"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: lint.data.materials.append(mat_stone)
    objs.append(lint)
    
    # Stepped Pidha roof for subshrine
    for i in range(4):
        t = i / 3.0
        rw = (sw/2 + 0.2) * (1.0 - t * 0.6)
        rd = (sd/2 + 0.2) * (1.0 - t * 0.6)
        rz = z + 0.3 + sh + i * 0.4 + 0.2
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, rz))
        rt = bpy.context.active_object
        rt.scale = (rw, rd, 0.2)
        rt.name = f"{name}_RoofTier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: rt.data.materials.append(mat_stone)
        objs.append(rt)
        
    # Kalasha finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(x, y, z + 0.3 + sh + 1.8))
    fin = bpy.context.active_object
    fin.name = f"{name}_Finial"
    if mat_gold: fin.data.materials.append(mat_gold)
    objs.append(fin)
    
    # Murti / Linga inside shrine
    if "Bhairava" in name:
        # Vaitaraneeshwar Shiva Lingam
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.25, depth=0.15, location=(x, y, z + 0.38))
        yoni = bpy.context.active_object
        if mat_stone: yoni.data.materials.append(mat_stone)
        objs.append(yoni)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.12, depth=0.35, location=(x, y, z + 0.58))
        linga = bpy.context.active_object
        if mat_stone: linga.data.materials.append(mat_stone)
        objs.append(linga)
    else:
        # Ganesha icon
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z + 0.6))
        g_body = bpy.context.active_object
        g_body.scale = (0.2, 0.15, 0.25)
        g_body.name = f"{name}_GaneshaBody"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: g_body.data.materials.append(mat_stone)
        objs.append(g_body)
        
    # Join into single object
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = plat
    bpy.ops.object.join()
    shrine = bpy.context.active_object
    shrine.name = name
    return shrine


def main():
    clear_scene()
    
    # 1. Materials
    mat_sandstone = create_sandstone("Jajpur_Sandstone", color=(0.76, 0.62, 0.44, 1.0))
    mat_gold = create_gold_metal("Jajpur_Gold")
    mat_brass = create_brass_metal("Jajpur_Brass")
    mat_silk = create_red_silk("Jajpur_Silk")
    mat_water = create_water("Baitarani_Water_Mat", color=(0.12, 0.38, 0.48, 0.85))
    mat_flame = create_flame_emission("Flame_Glow")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_stone_dark = create_black_stone("Black_Basalt_Biraja")
    mat_marble = create_white_marble("Courtyard_Paving")
    
    # 2. Main Courtyard Ground
    ground = create_ground_plane(name="Ground_Main", size=70, mat=mat_sandstone)
    
    # 3. Sanctum (Garbhagriha) Walls
    # Sanctum interior size: 5.4 x 5.4, height 4.8, centered at (0, 12, 0)
    garbha_walls = create_garbhagriha(
        name="Garbhagriha_Walls",
        location=(0, 12, 0),
        width=6.0,
        depth=6.0,
        wall_height=4.8,
        wall_thickness=0.5,
        mat=mat_sandstone,
        door_width=2.2,
        door_height=3.2
    )
    # Join sanctum walls into single object named "Garbhagriha"
    bpy.ops.object.select_all(action='DESELECT')
    for obj in garbha_walls:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = garbha_walls[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"
    
    # 4. Kalinga Rekha Deula Tower over Garbhagriha
    build_kalinga_rekha_deula(name="Biraja_RekhaDeula", location=(0, 12, 0), width=6.8, height=15.5, mat_stone=mat_sandstone, mat_gold=mat_gold)
    
    # 5. Kalinga Pidha Jagamohana (Mandapa)
    mandapa_parts = build_kalinga_pidha_jagamohana(name="Mandapa_Struct", location=(0, 3.5, 0), width=8.5, depth=7.5, height=3.8, mat_stone=mat_sandstone, mat_gold=mat_gold)
    # Join into single object named "Mandapa"
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mandapa_parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_parts[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"
    
    # 6. Deity_Biraja (2-armed Mahishasuramardini)
    create_two_armed_biraja(name="Deity_Biraja", location=(0, 12.8, 0.1), mat_stone=mat_stone_dark, mat_ornament=mat_gold)
    
    # 7. Priest
    create_human_figure(name="Priest", location=(1.6, 11.2, 0), height=1.7, mat_skin=mat_skin, mat_cloth=mat_dhoti)
    
    # 8. Ghanta (Hanging Temple Bell in Jagamohana entrance)
    create_hanging_bell(name="Ghanta", location=(0, 0.0, 3.1), mat_brass=mat_brass, scale=1.3)
    
    # 9. Deepams flanking Garbhagriha door
    create_deepam(name="Deepam_1", location=(-1.3, 8.8, 0), mat_brass=mat_brass, mat_flame=mat_flame)
    create_deepam(name="Deepam_2", location=(1.3, 8.8, 0), mat_brass=mat_brass, mat_flame=mat_flame)
    
    # 10. Subshrines
    # Bhairava: Vaitaraneeshwar Shrine (North-West courtyard)
    build_subshrine("Bhairava_Shrine", location=(-10, 6, 0), style="kalinga", mat_stone=mat_sandstone, mat_gold=mat_gold)
    
    # Ganesha Shrine (North-East courtyard)
    build_subshrine("Ganesha_Shrine", location=(10, 6, 0), style="kalinga", mat_stone=mat_sandstone, mat_gold=mat_gold)
    
    # 11. Baitarani River Ghat on West side
    build_baitarani_ghat(location=(-20, 6, 0), width=12.0, depth=32.0, mat_stone=mat_sandstone, mat_water=mat_water)
    
    # 12. Spawn_Point (South entrance, walk path facing +Y towards Mandapa and Sanctum)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -14, 0.1))
    spawn = bpy.context.active_object
    spawn.name = "Spawn_Point"
    
    # 13. Export GLB
    output_path = r"d:\Kshetra_Darshan\godot\assets\models\jajpur_biraja_kshetra_full.glb"
    export_glb(output_path)
    print("Successfully built and exported Jajpur Biraja Temple GLB!")


if __name__ == "__main__":
    main()
