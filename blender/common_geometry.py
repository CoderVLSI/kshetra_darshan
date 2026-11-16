"""
Shared Geometry Builder Library for Ashta Dasha Maha Shakti Peetha Darshana
Reusable temple geometry primitives: pillars, gopurams, shikharas, deepams, bells, etc.

COORDINATE CONVENTION (Blender):
- Ground plane: Z = 0 (which maps to Y = 0 in Godot)
- Up direction: +Z in Blender (+Y in Godot)
- Blender -> Godot: (godot_x, godot_y, godot_z) = (blender_x, blender_z, -blender_y)
"""
import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    """Remove all objects, meshes, materials from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def set_origin_to_bottom(obj):
    """Set origin to bottom center of the object."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Calculate bottom center
    local_bbox = [Vector(v) for v in obj.bound_box]
    min_z = min(v.z for v in local_bbox)
    center_x = sum(v.x for v in local_bbox) / 8
    center_y = sum(v.y for v in local_bbox) / 8
    offset = Vector((center_x, center_y, min_z))
    # Move mesh data
    for v in obj.data.vertices:
        v.co -= offset
    obj.location += offset
    obj.select_set(False)


def create_pillar(name="Pillar", location=(0, 0, 0), height=3.0, radius=0.2,
                  segments=16, mat=None, style="square"):
    """Create a carved temple pillar.
    style: 'square', 'round', 'octagonal'
    """
    if style == "square":
        # Square pillar with base and capital
        base_h = height * 0.1
        shaft_h = height * 0.75
        capital_h = height * 0.15

        # Base
        bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + base_h/2))
        base = bpy.context.active_object
        base.scale = (radius * 1.5, radius * 1.5, base_h / 2)
        base.name = f"{name}_Base"
        bpy.ops.object.transform_apply(scale=True)
        if mat:
            base.data.materials.append(mat)

        # Shaft
        bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + base_h + shaft_h/2))
        shaft = bpy.context.active_object
        shaft.scale = (radius, radius, shaft_h / 2)
        shaft.name = f"{name}_Shaft"
        bpy.ops.object.transform_apply(scale=True)
        if mat:
            shaft.data.materials.append(mat)

        # Capital
        bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + base_h + shaft_h + capital_h/2))
        capital = bpy.context.active_object
        capital.scale = (radius * 1.8, radius * 1.8, capital_h / 2)
        capital.name = f"{name}_Capital"
        bpy.ops.object.transform_apply(scale=True)
        if mat:
            capital.data.materials.append(mat)

        # Join all parts
        bpy.ops.object.select_all(action='DESELECT')
        base.select_set(True)
        shaft.select_set(True)
        capital.select_set(True)
        bpy.context.view_layer.objects.active = base
        bpy.ops.object.join()
        result = bpy.context.active_object
        result.name = name
        return result

    elif style == "round":
        bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=height,
                                            location=(location[0], location[1], location[2] + height/2))
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return obj

    elif style == "octagonal":
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=height,
                                            location=(location[0], location[1], location[2] + height/2))
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return obj


def create_pillar_row(name_prefix="Pillar", start_pos=(0, 0, 0), count=4, spacing=2.5,
                      direction='x', height=3.0, radius=0.2, mat=None, style="square"):
    """Create a row of equally spaced pillars."""
    pillars = []
    for i in range(count):
        if direction == 'x':
            loc = (start_pos[0] + i * spacing, start_pos[1], start_pos[2])
        else:
            loc = (start_pos[0], start_pos[1] + i * spacing, start_pos[2])
        p = create_pillar(f"{name_prefix}_{i+1}", loc, height, radius, mat=mat, style=style)
        pillars.append(p)
    return pillars


def create_platform(name="Platform", location=(0, 0, 0), size=(10, 10, 0.5), mat=None, steps=0):
    """Create a raised temple platform (jagati/adhisthana) with optional steps."""
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + size[2]/2))
    obj = bpy.context.active_object
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.name = name
    bpy.ops.object.transform_apply(scale=True)
    if mat:
        obj.data.materials.append(mat)

    if steps > 0:
        step_height = size[2] / steps
        step_depth = 0.4
        for i in range(steps):
            bpy.ops.mesh.primitive_cube_add(size=2,
                location=(location[0], location[1] - size[1]/2 - step_depth * (steps - i - 0.5),
                          location[2] + step_height * i + step_height/2))
            step = bpy.context.active_object
            step.scale = (size[0]/2 * 0.6, step_depth/2, step_height/2)
            step.name = f"{name}_Step_{i+1}"
            bpy.ops.object.transform_apply(scale=True)
            if mat:
                step.data.materials.append(mat)
    return obj


def create_garbhagriha(name="Garbhagriha", location=(0, 0, 0), width=4.0, depth=4.0,
                        wall_height=4.0, wall_thickness=0.4, mat=None, door_width=1.5, door_height=2.5):
    """Create the sanctum (garbhagriha) with walls and doorway."""
    objs = []
    hw = width / 2
    hd = depth / 2
    wt = wall_thickness

    # Back wall
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1] + hd - wt/2, location[2] + wall_height/2))
    wall = bpy.context.active_object
    wall.scale = (hw, wt/2, wall_height/2)
    wall.name = f"{name}_Wall_Back"
    bpy.ops.object.transform_apply(scale=True)
    if mat: wall.data.materials.append(mat)
    objs.append(wall)

    # Left wall
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0] - hw + wt/2, location[1], location[2] + wall_height/2))
    wall = bpy.context.active_object
    wall.scale = (wt/2, hd, wall_height/2)
    wall.name = f"{name}_Wall_Left"
    bpy.ops.object.transform_apply(scale=True)
    if mat: wall.data.materials.append(mat)
    objs.append(wall)

    # Right wall
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0] + hw - wt/2, location[1], location[2] + wall_height/2))
    wall = bpy.context.active_object
    wall.scale = (wt/2, hd, wall_height/2)
    wall.name = f"{name}_Wall_Right"
    bpy.ops.object.transform_apply(scale=True)
    if mat: wall.data.materials.append(mat)
    objs.append(wall)

    # Front wall left side (beside door)
    side_w = (width - door_width) / 2
    if side_w > 0.1:
        bpy.ops.mesh.primitive_cube_add(size=2,
            location=(location[0] - hw + side_w/2, location[1] - hd + wt/2, location[2] + wall_height/2))
        wall = bpy.context.active_object
        wall.scale = (side_w/2, wt/2, wall_height/2)
        wall.name = f"{name}_Wall_Front_L"
        bpy.ops.object.transform_apply(scale=True)
        if mat: wall.data.materials.append(mat)
        objs.append(wall)

    # Front wall right side
    if side_w > 0.1:
        bpy.ops.mesh.primitive_cube_add(size=2,
            location=(location[0] + hw - side_w/2, location[1] - hd + wt/2, location[2] + wall_height/2))
        wall = bpy.context.active_object
        wall.scale = (side_w/2, wt/2, wall_height/2)
        wall.name = f"{name}_Wall_Front_R"
        bpy.ops.object.transform_apply(scale=True)
        if mat: wall.data.materials.append(mat)
        objs.append(wall)

    # Lintel above door
    lintel_h = wall_height - door_height
    if lintel_h > 0.05:
        bpy.ops.mesh.primitive_cube_add(size=2,
            location=(location[0], location[1] - hd + wt/2, location[2] + door_height + lintel_h/2))
        wall = bpy.context.active_object
        wall.scale = (door_width/2, wt/2, lintel_h/2)
        wall.name = f"{name}_Lintel"
        bpy.ops.object.transform_apply(scale=True)
        if mat: wall.data.materials.append(mat)
        objs.append(wall)

    # Floor
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.02))
    floor = bpy.context.active_object
    floor.scale = (hw, hd, 0.02)
    floor.name = f"{name}_Floor"
    bpy.ops.object.transform_apply(scale=True)
    if mat: floor.data.materials.append(mat)
    objs.append(floor)

    return objs


def create_shikhara(name="Shikhara", location=(0, 0, 0), base_width=4.0, height=8.0,
                    tiers=6, mat=None, style="nagara", mat_gold=None):
    """Create authentic Nagara curvilinear shikhara or Dravidian stepped vimana."""
    objs = []
    x, y, z = location
    if style == "nagara":
        # Curvilinear parabolic Nagara Shikhara with fluted facets & corner turrets
        tier_h = height / tiers
        for i in range(tiers):
            t = i / float(tiers)
            # Curvilinear parabolic taper
            scale_fac = 1.0 - 0.55 * (t ** 1.5)
            tw = (base_width / 2.0) * scale_fac
            tz = z + i * tier_h + tier_h / 2.0
            
            # 16-faceted polygonal cylinder for vertical fluted ribs
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=tw, depth=tier_h, location=(x, y, tz))
            tier = bpy.context.active_object
            tier.name = f"{name}_Tier_{i+1}"
            if mat: tier.data.materials.append(mat)
            objs.append(tier)
            
            # Miniature corner angashikharas on lower tiers (ratha projections)
            if i < 3:
                for ang in [45, 135, 225, 315]:
                    rad = math.radians(ang)
                    ax = x + math.cos(rad) * (tw * 0.95)
                    ay = y + math.sin(rad) * (tw * 0.95)
                    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=tw * 0.22, radius2=0.04, depth=tier_h * 1.4, location=(ax, ay, tz))
                    ang_cone = bpy.context.active_object
                    if mat: ang_cone.data.materials.append(mat)
                    objs.append(ang_cone)

        # Ribbed Amalaka Disc at top
        amalaka_z = z + height + 0.25
        bpy.ops.mesh.primitive_torus_add(major_radius=base_width * 0.28, minor_radius=0.18, location=(x, y, amalaka_z))
        amalaka = bpy.context.active_object
        amalaka.scale = (1.0, 1.0, 0.55)
        amalaka.name = f"{name}_Amalaka"
        bpy.ops.object.transform_apply(scale=True)
        if mat: amalaka.data.materials.append(mat)
        objs.append(amalaka)

        # Pointed Golden Kalasha Finial
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=base_width * 0.10, radius2=0.02, depth=0.85, location=(x, y, amalaka_z + 0.55))
        kalasha = bpy.context.active_object
        kalasha.name = f"{name}_Kalasha"
        if mat_gold: kalasha.data.materials.append(mat_gold)
        elif mat: kalasha.data.materials.append(mat)
        objs.append(kalasha)

    elif style == "dravidian":
        # Dravidian stepped Vimana with cornice moldings & corner kutas
        tier_h = height / tiers
        for i in range(tiers):
            t = i / float(tiers)
            s = (base_width / 2.0) * (1.0 - t * 0.58)
            tz = z + i * tier_h + tier_h / 2.0
            
            # Main tier body
            bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
            tier = bpy.context.active_object
            tier.scale = (s, s, tier_h * 0.5)
            tier.name = f"{name}_Tier_{i+1}"
            bpy.ops.object.transform_apply(scale=True)
            if mat: tier.data.materials.append(mat)
            objs.append(tier)
            
            # Overhanging Kapota cornice
            bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz + tier_h * 0.25))
            cornice = bpy.context.active_object
            cornice.scale = (s + 0.15, s + 0.15, 0.08)
            bpy.ops.object.transform_apply(scale=True)
            if mat: cornice.data.materials.append(mat)
            objs.append(cornice)

        # Domed Stupi cupola & Golden Kalasha
        stupi_z = z + height + 0.35
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=base_width * 0.22, location=(x, y, stupi_z))
        stupi = bpy.context.active_object
        stupi.scale = (1.0, 1.0, 0.75)
        bpy.ops.object.transform_apply(scale=True)
        if mat: stupi.data.materials.append(mat)
        objs.append(stupi)

        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=base_width * 0.08, radius2=0.02, depth=0.75, location=(x, y, stupi_z + 0.55))
        kalasha = bpy.context.active_object
        kalasha.name = f"{name}_Kalasha"
        if mat_gold: kalasha.data.materials.append(mat_gold)
        elif mat: kalasha.data.materials.append(mat)
        objs.append(kalasha)

    return objs


def create_gopuram(name="Gopuram", location=(0, 0, 0), base_width=6.0, base_depth=3.0,
                   height=12.0, tiers=7, mat=None, colorful_mats=None, mat_gold=None):
    """Create authentic Dravidian Gopuram gateway tower with tiered cornices, corner kutas, and shala-shikhara crown."""
    objs = []
    x, y, z = location
    # The tower stands over a usable gateway, not a solid block across the entry.
    passage_height = 3.0
    passage_width = min(2.8, base_width * 0.48)
    jamb_width = (base_width - passage_width) / 2.0
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(
            x + sign * (passage_width / 2 + jamb_width / 2), y,
            z + passage_height / 2))
        jamb = bpy.context.active_object
        jamb.name = f"{name}_Gateway_Jamb_{suffix}"
        jamb.scale = (jamb_width / 2, base_depth / 2, passage_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        if mat:
            jamb.data.materials.append(mat)
        objs.append(jamb)
    z += passage_height
    tier_h = height / tiers
    
    for i in range(tiers):
        t = i / max(tiers - 1, 1)
        w = (base_width / 2.0) * (1.0 - t * 0.52)
        d = (base_depth / 2.0) * (1.0 - t * 0.52)
        tz = z + i * tier_h + tier_h / 2.0
        
        # Main tier body
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz))
        tier = bpy.context.active_object
        tier.scale = (w, d, tier_h * 0.5)
        tier.name = f"{name}_Tier_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        
        tier_mat = colorful_mats[i % len(colorful_mats)] if (colorful_mats and i < len(colorful_mats)) else mat
        if tier_mat: tier.data.materials.append(tier_mat)
        objs.append(tier)
        
        # Overhanging Kapota cornice on each tier
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, tz + tier_h * 0.22))
        cornice = bpy.context.active_object
        cornice.scale = (w + 0.18, d + 0.18, 0.08)
        cornice.name = f"{name}_Cornice_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if tier_mat: cornice.data.materials.append(tier_mat)
        objs.append(cornice)

        # Corner mini-turrets (kutas) on lower tiers
        if i < 4:
            for cx in [-w * 0.9, w * 0.9]:
                for cy in [-d * 0.9, d * 0.9]:
                    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=tier_h * 0.65, location=(x + cx, y + cy, tz + 0.05))
                    kuta = bpy.context.active_object
                    if tier_mat: kuta.data.materials.append(tier_mat)
                    objs.append(kuta)

    # Shala-Shikhara barrel vault crown (characteristic curved Dravidian crest)
    crown_z = z + height + base_width * 0.08
    crown_w = (base_width / 2.0) * (1.0 - 0.52) * 1.15
    crown_d = (base_depth / 2.0) * (1.0 - 0.52) * 0.85
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=crown_d, depth=crown_w * 2.0, location=(x, y, crown_z))
    crown = bpy.context.active_object
    crown.rotation_euler = (0, math.pi / 2, 0)
    crown.scale = (1.0, 0.75, 1.0)
    crown.name = f"{name}_Crown"
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    if mat: crown.data.materials.append(mat)
    objs.append(crown)

    # Row of Golden Kalashas along the ridge of the Shala-Shikhara crown
    kalasha_count = 5
    for k in range(kalasha_count):
        kt = -1.0 + 2.0 * k / float(kalasha_count - 1)
        kx = x + kt * (crown_w * 0.75)
        kz = crown_z + crown_d * 0.75 + 0.25
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.12, radius2=0.03, depth=0.45, location=(kx, y, kz))
        kal = bpy.context.active_object
        kal.name = f"{name}_Kalasha_{k+1}"
        if mat_gold: kal.data.materials.append(mat_gold)
        elif mat: kal.data.materials.append(mat)
        objs.append(kal)

    return objs


def create_deepam(name="Deepam", location=(0, 0, 0), mat_brass=None, mat_flame=None):
    """Create an oil lamp (deepam) with flame."""
    # Lamp bowl
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.04,
                                        location=(location[0], location[1], location[2] + 0.02))
    bowl = bpy.context.active_object
    bowl.name = f"{name}_Bowl"
    if mat_brass: bowl.data.materials.append(mat_brass)

    # Stem
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.15,
                                        location=(location[0], location[1], location[2] + 0.04 + 0.075))
    stem = bpy.context.active_object
    stem.name = f"{name}_Stem"
    if mat_brass: stem.data.materials.append(mat_brass)

    # Flame
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025,
        location=(location[0], location[1], location[2] + 0.04 + 0.16))
    flame = bpy.context.active_object
    flame.name = f"{name}_Flame"
    flame.scale = (1, 1, 2)
    bpy.ops.object.transform_apply(scale=True)
    if mat_flame: flame.data.materials.append(mat_flame)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    bowl.select_set(True)
    stem.select_set(True)
    flame.select_set(True)
    bpy.context.view_layer.objects.active = bowl
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    return result


def create_hanging_bell(name="Ghanta", location=(0, 0, 0), mat_brass=None, scale=1.0):
    """Create a hanging brass temple bell (ghanta)."""
    s = scale
    # Bell body (cone-ish)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.2*s, radius2=0.05*s, depth=0.3*s,
        location=(location[0], location[1], location[2]))
    bell = bpy.context.active_object
    bell.name = f"{name}_Body"
    if mat_brass: bell.data.materials.append(mat_brass)

    # Clapper
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04*s,
        location=(location[0], location[1], location[2] - 0.1*s))
    clapper = bpy.context.active_object
    clapper.name = f"{name}_Clapper"
    if mat_brass: clapper.data.materials.append(mat_brass)

    # Chain link
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.015*s, depth=0.3*s,
        location=(location[0], location[1], location[2] + 0.25*s))
    chain = bpy.context.active_object
    chain.name = f"{name}_Chain"
    if mat_brass: chain.data.materials.append(mat_brass)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    bell.select_set(True)
    clapper.select_set(True)
    chain.select_set(True)
    bpy.context.view_layer.objects.active = bell
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    return result


def create_kunda(name="Kunda", location=(0, 0, 0), size=(6, 6, 1.5),
                 mat_stone=None, mat_water=None, steps=4):
    """Create a sacred water tank (pushkarini/kunda) with stepped sides."""
    objs = []
    w, d, h = size

    # Outer walls
    for side_name, pos, scale in [
        ("N", (location[0], location[1] + d/2, location[2] + h/2), (w/2 + 0.2, 0.2, h/2)),
        ("S", (location[0], location[1] - d/2, location[2] + h/2), (w/2 + 0.2, 0.2, h/2)),
        ("E", (location[0] + w/2, location[1], location[2] + h/2), (0.2, d/2, h/2)),
        ("W", (location[0] - w/2, location[1], location[2] + h/2), (0.2, d/2, h/2)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
        wall = bpy.context.active_object
        wall.scale = scale
        wall.name = f"{name}_Wall_{side_name}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: wall.data.materials.append(mat_stone)
        objs.append(wall)

    # Steps along one side
    step_h = h / steps
    step_d = 0.4
    for i in range(steps):
        z = location[2] + h - (i + 1) * step_h + step_h / 2
        y = location[1] - d / 2 + 0.2 + step_d * i + step_d / 2
        bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], y, z))
        step = bpy.context.active_object
        step.scale = (w / 2 - 0.3, step_d / 2, step_h / 2)
        step.name = f"{name}_Step_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_stone: step.data.materials.append(mat_stone)
        objs.append(step)

    # Water surface
    bpy.ops.mesh.primitive_plane_add(size=2,
        location=(location[0], location[1], location[2] + h * 0.3))
    water = bpy.context.active_object
    water.scale = (w / 2 - 0.3, d / 2 - 0.3, 1)
    water.name = f"{name}_Water"
    bpy.ops.object.transform_apply(scale=True)
    if mat_water: water.data.materials.append(mat_water)
    objs.append(water)

    return objs


def create_tree(name="Tree", location=(0, 0, 0), height=5.0, mat_trunk=None, mat_leaves=None):
    """Create a simple stylized tree."""
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15, depth=height * 0.5,
        location=(location[0], location[1], location[2] + height * 0.25))
    trunk = bpy.context.active_object
    trunk.name = f"{name}_Trunk"
    if mat_trunk: trunk.data.materials.append(mat_trunk)

    # Canopy (icosphere)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=height * 0.35,
        location=(location[0], location[1], location[2] + height * 0.65))
    canopy = bpy.context.active_object
    canopy.name = f"{name}_Canopy"
    if mat_leaves: canopy.data.materials.append(mat_leaves)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    trunk.select_set(True)
    canopy.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    return result


def create_nandi(name="Nandi", location=(0, 0, 0), scale=1.0, mat=None):
    """Create a simplified sacred Nandi bull."""
    s = scale
    # Body
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.4*s))
    body = bpy.context.active_object
    body.scale = (0.3*s, 0.6*s, 0.3*s)
    body.name = f"{name}_Body"
    bpy.ops.object.transform_apply(scale=True)
    if mat: body.data.materials.append(mat)

    # Head
    bpy.ops.mesh.primitive_cube_add(size=2,
        location=(location[0], location[1] + 0.55*s, location[2] + 0.55*s))
    head = bpy.context.active_object
    head.scale = (0.2*s, 0.25*s, 0.2*s)
    head.name = f"{name}_Head"
    bpy.ops.object.transform_apply(scale=True)
    if mat: head.data.materials.append(mat)

    # Legs
    for lx, ly in [(-0.2, -0.35), (0.2, -0.35), (-0.2, 0.25), (0.2, 0.25)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06*s, depth=0.35*s,
            location=(location[0] + lx*s, location[1] + ly*s, location[2] + 0.175*s))
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg"
        if mat: leg.data.materials.append(mat)

    # Join all
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    return result


def create_deity_figure(name="Deity", location=(0, 0, 0), height=1.5, arms=4,
                         mat_body=None, mat_ornament=None, holding_items=None):
    """Create a simplified deity murti with multiple arms.
    holding_items: list of strings like ['lotus', 'trident', 'gada', 'chakra']
    """
    s = height / 1.5  # normalize
    # Body torso
    bpy.ops.mesh.primitive_cube_add(size=2,
        location=(location[0], location[1], location[2] + 0.7*s))
    torso = bpy.context.active_object
    torso.scale = (0.25*s, 0.15*s, 0.35*s)
    torso.name = f"{name}_Torso"
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: torso.data.materials.append(mat_body)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12*s,
        location=(location[0], location[1], location[2] + 1.1*s))
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    if mat_body: head.data.materials.append(mat_body)

    # Crown
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.1*s, radius2=0.02*s, depth=0.2*s,
        location=(location[0], location[1], location[2] + 1.3*s))
    crown = bpy.context.active_object
    crown.name = f"{name}_Crown"
    if mat_ornament: crown.data.materials.append(mat_ornament)

    # Arms
    arm_pairs = arms // 2
    for pair in range(arm_pairs):
        angle_offset = pair * 0.3
        for side, sx in [("L", -1), ("R", 1)]:
            arm_z = 0.85*s - pair * 0.15*s
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04*s, depth=0.4*s,
                location=(location[0] + sx * 0.35*s, location[1], location[2] + arm_z))
            arm = bpy.context.active_object
            arm.rotation_euler = (0, math.pi/2 * sx * 0.7 + angle_offset * sx, 0)
            arm.name = f"{name}_Arm_{side}_{pair+1}"
            bpy.ops.object.transform_apply(rotation=True)
            if mat_body: arm.data.materials.append(mat_body)

    # Legs
    for sx in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06*s, depth=0.4*s,
            location=(location[0] + sx * 0.1*s, location[1], location[2] + 0.2*s))
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg"
        if mat_body: leg.data.materials.append(mat_body)

    # Pedestal / Lotus seat
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.25*s, depth=0.08*s,
        location=(location[0], location[1], location[2] + 0.04*s))
    pedestal = bpy.context.active_object
    pedestal.name = f"{name}_Pedestal"
    if mat_ornament: pedestal.data.materials.append(mat_ornament)

    # Join all
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    return result


def create_human_figure(name="Priest", location=(0, 0, 0), height=1.75, mat_skin=None, mat_cloth=None):
    """Create an authentic human figure (priest/devotee) with feet on floor and traditional dhoti."""
    s = height / 1.75
    x, y, z = location
    objs = []

    # Bare feet flat on floor at z
    for sx in [-0.10 * s, 0.10 * s]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.045 * s, depth=0.18 * s, location=(x + sx, y - 0.04 * s, z + 0.03 * s))
        foot = bpy.context.active_object
        foot.rotation_euler = (math.pi/2, 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        foot.name = f"{name}_Foot"
        if mat_skin: foot.data.materials.append(mat_skin)
        objs.append(foot)

        # Lower legs / shins
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.045 * s, depth=0.38 * s, location=(x + sx, y, z + 0.22 * s))
        shin = bpy.context.active_object
        shin.name = f"{name}_Shin"
        if mat_skin: shin.data.materials.append(mat_skin)
        objs.append(shin)

    # Traditional Dhoti wrapping legs from knee to waist (z + 0.40*s to z + 0.98*s)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18 * s, depth=0.58 * s, location=(x, y, z + 0.69 * s))
    dhoti = bpy.context.active_object
    dhoti.scale = (1.1, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    dhoti.name = f"{name}_Dhoti"
    if mat_cloth: dhoti.data.materials.append(mat_cloth)
    objs.append(dhoti)

    # Torso (z + 0.98*s to z + 1.40*s)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.16 * s, depth=0.42 * s, location=(x, y, z + 1.19 * s))
    torso = bpy.context.active_object
    torso.scale = (1.15, 0.80, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    torso.name = f"{name}_Torso"
    if mat_skin: torso.data.materials.append(mat_skin)
    objs.append(torso)

    # Arms folded reverently
    for sx, sign in [(-0.19 * s, 1), (0.19 * s, -1)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.038 * s, depth=0.32 * s, location=(x + sx, y - 0.05 * s, z + 1.20 * s))
        arm = bpy.context.active_object
        arm.rotation_euler = (math.radians(28), math.radians(sign * 20), 0)
        bpy.ops.object.transform_apply(rotation=True)
        arm.name = f"{name}_Arm"
        if mat_skin: arm.data.materials.append(mat_skin)
        objs.append(arm)

    # Neck & Head
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.05 * s, depth=0.10 * s, location=(x, y, z + 1.44 * s))
    neck = bpy.context.active_object
    neck.name = f"{name}_Neck"
    if mat_skin: neck.data.materials.append(mat_skin)
    objs.append(neck)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.10 * s, location=(x, y, z + 1.55 * s))
    head = bpy.context.active_object
    head.scale = (0.92, 1.05, 1.15)
    bpy.ops.object.transform_apply(scale=True)
    head.name = f"{name}_Head"
    if mat_skin: head.data.materials.append(mat_skin)
    objs.append(head)

    # Join and smooth
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    res = bpy.context.active_object
    res.name = name
    bpy.ops.object.shade_smooth()
    return res


def create_ground_plane(name="Ground", size=50, mat=None):
    """Create ground plane at Z=0."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj


def create_mandapa(name="Mandapa", location=(0, 0, 0), width=8, depth=6, height=3.5,
                    pillar_count_x=4, pillar_count_y=3, mat_stone=None, mat_floor=None,
                    pillar_style="square"):
    """Create a pillared hall (mandapa)."""
    objs = []
    # Floor
    bpy.ops.mesh.primitive_cube_add(size=2,
        location=(location[0], location[1], location[2] + 0.05))
    floor = bpy.context.active_object
    floor.scale = (width/2, depth/2, 0.05)
    floor.name = f"{name}_Floor"
    bpy.ops.object.transform_apply(scale=True)
    if mat_floor: floor.data.materials.append(mat_floor)
    objs.append(floor)

    # Pillars
    x_spacing = width / (pillar_count_x - 1) if pillar_count_x > 1 else 0
    y_spacing = depth / (pillar_count_y - 1) if pillar_count_y > 1 else 0
    start_x = location[0] - width / 2
    start_y = location[1] - depth / 2
    for ix in range(pillar_count_x):
        for iy in range(pillar_count_y):
            # Only perimeter pillars
            if 0 < ix < pillar_count_x - 1 and 0 < iy < pillar_count_y - 1:
                continue
            px = start_x + ix * x_spacing
            py = start_y + iy * y_spacing
            p = create_pillar(f"{name}_Pillar_{ix}_{iy}", (px, py, location[2] + 0.1),
                              height=height - 0.1, radius=0.18, mat=mat_stone, style=pillar_style)
            objs.append(p)

    # Roof slab
    bpy.ops.mesh.primitive_cube_add(size=2,
        location=(location[0], location[1], location[2] + height + 0.1))
    roof = bpy.context.active_object
    roof.scale = (width/2 + 0.3, depth/2 + 0.3, 0.15)
    roof.name = f"{name}_Roof"
    bpy.ops.object.transform_apply(scale=True)
    if mat_stone: roof.data.materials.append(mat_stone)
    objs.append(roof)

    return objs


def create_prakara_wall(name="Prakara", center=(0, 0, 0), width=30, depth=25,
                         wall_height=3.0, wall_thickness=0.5, mat=None,
                         gate_width=3.0, gate_sides=["S"]):
    """Create a rectangular enclosure wall (prakara) with gates."""
    objs = []
    hw, hd = width / 2, depth / 2

    sides = {
        "N": ((center[0], center[1] + hd, center[2] + wall_height/2), (hw, wall_thickness/2, wall_height/2)),
        "S": ((center[0], center[1] - hd, center[2] + wall_height/2), (hw, wall_thickness/2, wall_height/2)),
        "E": ((center[0] + hw, center[1], center[2] + wall_height/2), (wall_thickness/2, hd, wall_height/2)),
        "W": ((center[0] - hw, center[1], center[2] + wall_height/2), (wall_thickness/2, hd, wall_height/2)),
    }
    for side, (pos, sc) in sides.items():
        if side in gate_sides:
            # Split wall with gate opening
            if side in ["N", "S"]:
                half_w = (hw - gate_width / 2) / 2
                offset = hw - half_w
                for sign, suffix in [(-1, "L"), (1, "R")]:
                    bpy.ops.mesh.primitive_cube_add(size=2,
                        location=(pos[0] + sign * offset, pos[1], pos[2]))
                    w = bpy.context.active_object
                    w.scale = (half_w, sc[1], sc[2])
                    w.name = f"{name}_{side}_{suffix}"
                    bpy.ops.object.transform_apply(scale=True)
                    if mat: w.data.materials.append(mat)
                    objs.append(w)
            else:
                half_d = (hd - gate_width / 2) / 2
                offset = hd - half_d
                for sign, suffix in [(-1, "L"), (1, "R")]:
                    bpy.ops.mesh.primitive_cube_add(size=2,
                        location=(pos[0], pos[1] + sign * offset, pos[2]))
                    w = bpy.context.active_object
                    w.scale = (sc[0], half_d, sc[2])
                    w.name = f"{name}_{side}_{suffix}"
                    bpy.ops.object.transform_apply(scale=True)
                    if mat: w.data.materials.append(mat)
                    objs.append(w)
        else:
            bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
            w = bpy.context.active_object
            w.scale = sc
            w.name = f"{name}_{side}"
            bpy.ops.object.transform_apply(scale=True)
            if mat: w.data.materials.append(mat)
            objs.append(w)
    return objs


def export_glb(filepath, apply_modifiers=True):
    """Export the scene as .glb for Godot import."""
    kwargs = {
        'filepath': filepath,
        'export_format': 'GLB',
        'export_apply': apply_modifiers,
        'export_yup': True,  # Godot expects Y-up
        'export_materials': 'EXPORT',
        'export_cameras': False,
        'export_lights': False,
    }
    bpy.ops.export_scene.gltf(**kwargs)
    print(f"Exported: {filepath}")
