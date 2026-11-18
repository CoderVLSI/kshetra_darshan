"""
Blender 5.3 Build Script for Jajpur Biraja Temple (Kshetra #13)
Kalinga Architecture: Rekha Deula (sanctum) + Pidha Jagamohana (hall)
Deity: 2-armed Biraja (Dvi-bhuja Mahishasuramardini)
Features: East-facing Simhadwara, Chandi Mandapa, Nabhigaya and the northeast shrine group
Output: d:\\Kshetra_Darshan\\godot\\assets\\models\\jajpur_biraja_kshetra_full.glb
"""
import os
import sys
import math
import bpy
from mathutils import Matrix, Vector

# Ensure blender directory in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from common_materials import (
    create_sandstone, create_gold_metal, create_brass_metal,
    create_red_silk, create_water, create_flame_emission,
    create_skin, create_white_dhoti, create_flower_garland,
    create_black_stone
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_hanging_bell, create_deepam, create_human_figure,
    create_ground_plane, create_mandapa, create_prakara_wall, create_shikhara
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
    
    # The garbhagriha walls form the lower mass and leave the sanctuary open.
    bada_h = 4.8

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


def build_linga(name, position, material, radius=.16, height=.36):
    x, y, z = position
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20, radius=radius * 1.7, depth=.12, location=(x, y, z + .06)
    )
    base = bpy.context.active_object
    base.name = name + "_Base"
    base.data.materials.append(material)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=1, location=(x, y, z + .1 + height / 2)
    )
    form = bpy.context.active_object
    form.name = name
    form.scale = (radius, radius, height / 2)
    form.data.materials.append(material)


def build_deva_sabha(name, center, width, depth, count, faces_east, stone, roof):
    x, y = center
    create_platform(name + "_Floor", (x, y, 0), size=(width, depth, .12), mat=stone)
    front = 1 if faces_east else -1
    for side in [-1, 1]:
        create_platform(name + "_End_Wall", (x, y + side * (depth / 2 - .12), .12),
                        size=(width, .24, 3.1), mat=stone)
    create_platform(name + "_Rear_Wall", (x - front * (width / 2 - .12), y, .12),
                    size=(.24, depth, 3.1), mat=stone)
    for dy in [-depth / 2 + .25, 0, depth / 2 - .25]:
        create_pillar(name + "_Post", (x + front * (width / 2 - .18), y + dy, .12),
                      height=3.1, radius=.12, mat=stone)
    for side in [-1, 1]:
        sheet = create_platform(name + "_Sheet_Roof", (x + side * width / 4, y, 3.58),
                                size=(width / 2 + .2, depth + .35, .11), mat=roof)
        sheet.rotation_euler.y = side * .14
    # Preserve the documented counts. The arrangement and individual shapes
    # are representative until a measured interior survey is available.
    for index in range(count):
        row, column = divmod(index, 12)
        build_linga(name + "_Linga_" + str(index + 1),
                    (x - front * (width / 2 - .55 - row * .8),
                     y + (column - 5.5) * (depth - 1) / 12, .12),
                    stone, radius=.10, height=.26 + .05 * (index % 4))
    marker = bpy.data.objects.new(name + "_Anchor", None)
    bpy.context.scene.collection.objects.link(marker)
    marker.location = (x + front * width / 3, y, .65)


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
    mat_paving = create_sandstone("Biraja_Courtyard_Paving", color=(.39, .36, .31, 1.0))
    
    # 2. Main Courtyard Ground
    create_ground_plane(name="Ground_Main", size=75, mat=mat_sandstone)
    create_platform("Biraja_Courtyard_Paving", (0, 0, 0), size=(50, 50, .04), mat=mat_paving)
    
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
    build_kalinga_rekha_deula(name="Biraja_RekhaDeula", location=(0, 12, 0), width=7.2, height=21.15, mat_stone=mat_sandstone, mat_gold=mat_gold)
    
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
    
    # Add the antarala and the documented Chandi Mandapa in front of the hall.
    connector = create_garbhagriha("Biraja_Antarala", (0, 8.1, 0), width=4.6,
                                  depth=2.1, wall_height=3.35, door_width=2.2,
                                  door_height=2.6, mat=mat_sandstone)
    bpy.data.objects.remove(connector[0], do_unlink=True)
    create_platform("Biraja_Antarala_Roof", (0, 8.1, 3.35),
                    size=(4.9, 2.4, .25), mat=mat_sandstone)
    create_mandapa("Chandi_Mandapa", (0, -4.2, 0), width=10.8, depth=7.9,
                   height=3.5, pillar_count_x=4, pillar_count_y=2,
                   mat_stone=mat_sandstone, mat_floor=mat_paving)

    # Rotate the sanctuary, halls and figures together toward the Simhadwara.
    bpy.context.view_layer.update()
    eastward = Matrix.Rotation(math.pi / 2, 4, 'Z')
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world = eastward @ obj.matrix_world

    # IGNCA records a 50 m square courtyard with gates on all four sides.
    create_prakara_wall("Biraja_Prakar", width=50, depth=50, wall_height=2.8,
                        wall_thickness=.55, mat=mat_sandstone, gate_width=4.8,
                        gate_sides=["E", "W", "N", "S"])
    create_mandapa("Simhadwara", (24.8, 0, 0), width=3.2, depth=5.2,
                   height=3.8, pillar_count_x=2, pillar_count_y=2,
                   mat_stone=mat_sandstone, mat_floor=mat_paving)

    # The separate northeast shrines follow IGNCA's footprint and orientation data.
    baidyanatha = (7, 18, 0)
    walls = create_garbhagriha("Baidyanatha", width=4.1, depth=4.1, wall_height=3.4,
                              door_width=1.4, door_height=2.4, mat=mat_sandstone)
    shrine_transform = Matrix.Translation(baidyanatha) @ eastward
    bpy.context.view_layer.update()
    for wall in walls:
        wall.matrix_world = shrine_transform @ wall.matrix_world
    for index, width in enumerate([4.1, 3.55, 3.0, 2.45, 1.9, 1.35]):
        create_platform("Baidyanatha_Pidha", (7, 18, 3.4 + index * .6),
                        size=(width, width, .6), mat=mat_sandstone)
    build_linga("Baidyanatha_Linga", baidyanatha, mat_stone_dark, radius=.22, height=.65)
    metal = create_black_stone("Deva_Sabha_Grey_Roof", color=(.31, .34, .35, 1.0))
    build_deva_sabha("Sahasralinga_I", (18, 18), 6, 10.5, 54, False, mat_stone_dark, metal)
    build_deva_sabha("Sahasralinga_II", (18, 6.8), 5.8, 10.2, 37, True, mat_stone_dark, metal)
    for index in range(5):
        votive_x, votive_y = 18.1, 4.8 + index * .8
        create_platform("Deva_Sabha_Votive_Plinth", (votive_x, votive_y, .12),
                        size=(.48, .48, .28), mat=mat_sandstone)
        create_shikhara("Deva_Sabha_Votive_Spire", (votive_x, votive_y, .4),
                        base_width=.46, height=.56, tiers=4, mat=mat_sandstone)

    # The Trust identifies this shrine in front of the southwest wall fragment.
    create_garbhagriha("Bhushandeshwara", (-18, -19, 0),
                       width=3.4, depth=3.4, wall_height=2.9, door_width=1.5,
                       door_height=2.2, mat=mat_sandstone)
    create_platform("Bhushandeshwara_Roof", (-18, -19, 2.9),
                    size=(3.6, 3.6, .2), mat=mat_sandstone)
    create_shikhara("Bhushandeshwara_Tower", (-18, -19, 3.1),
                    base_width=3, height=2.7, tiers=4, mat=mat_sandstone)
    build_linga("Bhushandeshwara_Linga", (-18, -19, 0), mat_stone_dark)

    # The Trust documents the Bhikari Das inscription at this upper lintel.
    create_platform("Simhadwara_Inscription_Stone", (26.15, 0, 3.13),
                    size=(.20, 2.45, .45), mat=mat_stone_dark)

    # The satellite view places the Nabhi Gaya well southeast of the main shrine.
    create_mandapa("Nabhigaya_Pavilion", (7.7, -7.5, 0), width=5.2, depth=5,
                   height=3.1, pillar_count_x=2, pillar_count_y=2,
                   mat_stone=mat_sandstone, mat_floor=mat_paving)
    bpy.ops.mesh.primitive_torus_add(
        major_segments=40, minor_segments=12, location=(7.7, -7.5, .42),
        major_radius=.83, minor_radius=.16
    )
    rim = bpy.context.active_object
    rim.name = "Nabhigaya_Well_Rim"
    rim.data.materials.append(mat_stone_dark)
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=.75, depth=.03, location=(7.7, -7.5, .16))
    bpy.context.active_object.name = "Nabhigaya_Well_Water"
    bpy.context.active_object.data.materials.append(mat_water)

    # The Trust photo shows the well enclosed by a circular metal grille.
    for level in [.47, .96, 1.60]:
        bpy.ops.mesh.primitive_torus_add(major_segments=40, minor_segments=8,
                                        location=(7.7, -7.5, level),
                                        major_radius=.87, minor_radius=.022)
        hoop = bpy.context.active_object
        hoop.name = "Nabhigaya_Grille_Hoop"
        hoop.data.materials.append(metal)
    for index in range(32):
        angle = math.tau * index / 32
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=.014, depth=1.16,
            location=(7.7 + .87 * math.cos(angle), -7.5 + .87 * math.sin(angle), 1.04),
        )
        bar = bpy.context.active_object
        bar.name = "Nabhigaya_Grille_Bar"
        bar.data.materials.append(metal)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(20, 0, .1))
    bpy.context.active_object.name = "Spawn_Point"

    output_path = os.path.join(os.path.dirname(script_dir), "godot", "assets", "models",
                               "jajpur_biraja_kshetra_full.glb")
    export_glb(output_path)
    print("Successfully built and exported Jajpur Biraja Temple GLB!")


if __name__ == "__main__":
    main()
