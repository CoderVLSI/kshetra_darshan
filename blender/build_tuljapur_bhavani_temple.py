"""
Build Script for Tuljapur Bhavani Temple
Shakti Peetha: Tuljapur, Maharashtra (Left cheek of Sati / Kulswamini Bhavani)
Architecture: terraced entrance, cross-shaped Sabha Mandapa, Kallol and Gomukh tirthas
"""
import sys
import os
import math
import bpy
from mathutils import Matrix, Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from common_materials import (
    create_sandstone, create_black_stone, create_gold_metal, create_brass_metal,
    create_flame_emission, create_skin, create_white_dhoti,
    create_water, create_kumkum_red, create_flower_garland
)
from common_geometry import (
    clear_scene, create_pillar, create_platform, create_garbhagriha,
    create_deepam, create_hanging_bell, create_kunda,
    create_human_figure, create_ground_plane, create_mandapa,
    export_glb
)


def export_temple_glb(filepath, apply_modifiers=True):
    """Export scene as GLB compatible with Blender 5.3."""
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


def create_deepamala(name, location, height=6.0, mat_stone=None):
    """Creates a traditional Maratha Deepamala lamp tower with radiating stone lamp brackets."""
    parts = []
    # Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.65, depth=0.7,
                                        location=(location[0], location[1], location[2] + 0.35))
    base = bpy.context.active_object
    if mat_stone: base.data.materials.append(mat_stone)
    parts.append(base)

    # Column shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.32, depth=height - 1.0,
                                        location=(location[0], location[1], location[2] + 0.7 + (height - 1.0)/2))
    shaft = bpy.context.active_object
    if mat_stone: shaft.data.materials.append(mat_stone)
    parts.append(shaft)

    # Radiating brackets around the pillar
    levels = 5
    for lvl in range(levels):
        lz = location[2] + 1.2 + lvl * 0.9
        for angle_i in range(4):
            ang = angle_i * (math.pi / 2) + (lvl * 0.4)
            bx = location[0] + math.cos(ang) * 0.45
            by = location[1] + math.sin(ang) * 0.45
            bpy.ops.mesh.primitive_cube_add(size=2, location=(bx, by, lz))
            b = bpy.context.active_object
            b.scale = (0.12, 0.12, 0.06)
            b.rotation_euler = (0, 0, ang)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            if mat_stone: b.data.materials.append(mat_stone)
            parts.append(b)

    # Top Kalasha
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.4, radius2=0.1, depth=0.5,
                                    location=(location[0], location[1], location[2] + height + 0.1))
    top = bpy.context.active_object
    if mat_stone: top.data.materials.append(mat_stone)
    parts.append(top)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = name
    return base


def create_bhavani_deity(name, location, mat_body, mat_gold, mat_silk):
    """Create 8-armed Mahishasuramardini slaying Mahishasura."""
    parts = []

    # Buffalo Mahishasura underfoot
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.12))
    demon = bpy.context.active_object
    demon.scale = (0.35, 0.22, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: demon.data.materials.append(mat_body)
    parts.append(demon)

    # Lotus Pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=0.1,
                                        location=(location[0], location[1], location[2] + 0.25))
    ped = bpy.context.active_object
    if mat_gold: ped.data.materials.append(mat_gold)
    parts.append(ped)

    # Lower body / silk pleated saree
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.5,
                                        location=(location[0], location[1], location[2] + 0.55))
    lower = bpy.context.active_object
    if mat_silk: lower.data.materials.append(mat_silk)
    parts.append(lower)

    # Torso
    bpy.ops.mesh.primitive_cube_add(size=2, location=(location[0], location[1], location[2] + 0.95))
    torso = bpy.context.active_object
    torso.scale = (0.24, 0.15, 0.26)
    bpy.ops.object.transform_apply(scale=True)
    if mat_body: torso.data.materials.append(mat_body)
    parts.append(torso)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(location[0], location[1], location[2] + 1.25))
    head = bpy.context.active_object
    if mat_body: head.data.materials.append(mat_body)
    parts.append(head)

    # Kiritam (Crown)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=0.03, depth=0.3,
                                    location=(location[0], location[1], location[2] + 1.48))
    crown = bpy.context.active_object
    if mat_gold: crown.data.materials.append(mat_gold)
    parts.append(crown)

    # 8 Arms (4 pairs)
    # Trishula piercing demon (Right primary arm thrusting forward-downward)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=1.2,
                                        location=(location[0] + 0.15, location[1] - 0.2, location[2] + 0.7))
    trishul = bpy.context.active_object
    trishul.rotation_euler = (0.4, -0.2, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: trishul.data.materials.append(mat_gold)
    parts.append(trishul)

    for pair_idx in range(4):
        ang_z = 0.25 * pair_idx
        for side, sx in [("R", 1), ("L", -1)]:
            az = 1.05 - pair_idx * 0.12
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=8, radius=0.032, depth=0.36,
                location=(location[0] + sx * (0.26 + pair_idx * 0.04), location[1], location[2] + az)
            )
            arm = bpy.context.active_object
            arm.rotation_euler = (0, sx * (0.5 + ang_z), 0)
            bpy.ops.object.transform_apply(rotation=True)
            if mat_body: arm.data.materials.append(mat_body)
            parts.append(arm)

    # Golden Prabhavali arch
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.045,
                                     location=(location[0], location[1] + 0.06, location[2] + 1.1))
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    if mat_gold: prabha.data.materials.append(mat_gold)
    parts.append(prabha)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = ped
    bpy.ops.object.join()
    ped.name = name
    return ped


def add_marker(name, position):
    marker = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(marker)
    marker.location = position
    return marker


def build_shrine_chamber(name, position, width, stone):
    create_garbhagriha(name, position, width=width, depth=width,
                       wall_height=2.8, door_width=1.35, door_height=2.15,
                       mat=stone)
    x, y, z = position
    create_platform(name + "_Roof", (x, y, z + 2.8),
                    size=(width + .25, width + .25, .24), mat=stone)


def build_east_descent(stone, paving):
    # Thirty shallow risers span two flights and a landing.
    for index in range(30):
        x = 33 + index * .83 + (2.5 if index >= 15 else 0)
        y = 3.3 + (x - 33) * .21
        height = (index + 1) * .18
        create_platform("Descent_Riser", (x, y, 0),
                        size=(.99, 4.8, height), mat=stone)
        for sign in [-1, 1]:
            create_platform("Descent_Parapet", (x, y + sign * 2.45, height),
                            size=(1.0, .18, .55), mat=stone)
    create_platform("Descent_Intermediate_Landing", (46.3, 6.1, 0),
                    size=(2.48, 4.8, 2.7), mat=paving)
    create_platform("Descent_Upper_Landing", (65.05, 10.7, 0),
                    size=(10.9, 9.8, 5.4), mat=stone)
    create_platform("Markandeya_Upper_Terrace", (65, 16.1, 0),
                    size=(5.8, 5.2, 5.4), mat=stone)


def build_tuljapur_tower(stone, gold):
    # Existing tower photograph in the conservation report, page 42.
    sage = create_sandstone("Tuljapur_Tower_Sage", color=(.33, .43, .39, 1))
    rose = create_sandstone("Tuljapur_Tower_Rose", color=(.47, .33, .36, 1))
    pale = create_sandstone("Tuljapur_Tower_Pale", color=(.52, .52, .46, 1))
    bottom = 4.5
    tiers = [(2.55, 1.68), (2.11, 1.55), (1.67, 1.35), (1.25, 1.16), (.9, .84)]
    for tier, (radius, height) in enumerate(tiers):
        for name, z, r, depth, mat in [
            ("Cornice_Base", bottom + .14, radius, .28, sage),
            ("Niche_Drum", bottom + height * .49, radius * .86, height * .72, stone),
            ("Cornice_Crown", bottom + height - .07, radius * .95, .14, rose),
        ]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=depth, location=(0, 4, z))
            drum = bpy.context.active_object
            drum.name = f"Tuljapur_Tower_{name}_{tier}"
            drum.data.materials.append(mat)
        count = 10 if tier < 2 else 8
        for index in range(count):
            turn = math.tau * index / count
            normal = Vector((math.cos(turn), math.sin(turn), 0))
            tangent = Vector((-normal.y, normal.x, 0))
            center = Vector((0, 4, bottom + height * .51)) + normal * radius * .88
            vertices, faces = [], []
            # Rounded archivolts around the recessed sculptural bays.
            for step in range(13):
                angle = math.pi * step / 12
                offset = tangent * (math.cos(angle) * radius * .215)
                offset.z = math.sin(angle) * height * .32
                for lip in [-1, 1]:
                    for side in [-1, 1]:
                        edge = tangent * (math.cos(angle) * .044 * side)
                        edge.z = math.sin(angle) * .044 * side
                        vertices.append(center + offset + edge + normal * (.046 * lip))
                if step:
                    previous = (step - 1) * 4
                    for a, b in [(0, 1), (1, 3), (3, 2), (2, 0)]:
                        faces.append((previous + a, previous + b, previous + b + 4, previous + a + 4))
            mesh = bpy.data.meshes.new("Tuljapur_Archivolt")
            mesh.from_pydata(vertices, [], faces)
            arch = bpy.data.objects.new("Tuljapur_Tower_Archivolt", mesh)
            bpy.context.collection.objects.link(arch)
            mesh.materials.append(rose if tier % 2 == 0 else sage)
            # Small stone figures preserve the niche rhythm. Individual
            # figures require elevation photographs from each side.
            for z, size in [(height * .06, (.12, .10, .13)), (-height * .13, (.17, .10, .26))]:
                offset = center + normal * .035 + Vector((0, 0, z))
                bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5, location=offset)
                figure = bpy.context.active_object
                figure.name = "Tuljapur_Tower_Niche_Relief"
                figure.scale = tuple(dimension * min(height, 1.3) for dimension in size)
                figure.rotation_euler.z = turn + math.pi / 2
                figure.data.materials.append(pale)
        bottom += height
    for rise, radius, depth, material in [(.08, .68, .20, sage), (.43, .46, .39, rose),
                                           (.95, .19, .24, gold)]:
        z = bottom + rise
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=(0, 4, z))
        finial = bpy.context.active_object
        finial.name = "Tuljapur_Tower_Kalasha"
        finial.scale = (radius, radius, depth)
        finial.data.materials.append(material)


def build_tuljapur_bhavani():
    clear_scene()

    # Materials
    mat_sandstone = create_sandstone("Tuljapur_Sandstone", color=(0.38, 0.35, 0.32, 1.0), roughness=0.85)
    mat_dark_stone = create_black_stone("Fort_Stone_Basalt", color=(0.12, 0.11, 0.10, 1.0), roughness=0.6)
    mat_gold = create_gold_metal("Temple_Gold")
    mat_brass = create_brass_metal("Temple_Brass")
    mat_flame = create_flame_emission("Deepam_Flame")
    mat_skin = create_skin("Priest_Skin")
    mat_dhoti = create_white_dhoti("Priest_Dhoti")
    mat_water = create_water("Kallol_Tirtha_Water")
    mat_silk = create_kumkum_red("Bhavani_Saree_Silk")
    mat_paving = create_sandstone("Tuljapur_Courtyard_Paving", color=(.36, .32, .28, 1.0))

    # 1. Ground Plane (Ground Z=0)
    ground = create_ground_plane("Ground_Main", size=180.0, mat=mat_paving)

    # 2. Raised Sanctum Plinth
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 4.0, 0.25))
    plinth = bpy.context.active_object
    plinth.scale = (3.5, 3.5, 0.25)
    plinth.name = "Tuljapur_Adhisthana"
    bpy.ops.object.transform_apply(scale=True)
    if mat_sandstone: plinth.data.materials.append(mat_sandstone)

    # 3. Garbhagriha
    gb_parts = create_garbhagriha(
        name="Garbhagriha_Structure",
        location=(0, 4.0, 0.5),
        width=4.6, depth=4.6,
        wall_height=4.0, wall_thickness=0.45,
        mat=mat_sandstone,
        door_width=1.6, door_height=2.6
    )
    bpy.ops.object.select_all(action='DESELECT')
    for p in gb_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = gb_parts[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # Rounded tower with the existing tiered palette and arched niches.
    build_tuljapur_tower(mat_sandstone, mat_gold)

    # 4. Deity: Deity_Bhavani (8-armed Mahishasuramardini)
    deity = create_bhavani_deity(
        name="Deity_Bhavani",
        location=(0, 4.8, 0.52),
        mat_body=mat_dark_stone,
        mat_gold=mat_gold,
        mat_silk=mat_silk
    )

    # 5. Mandapa: Pillared Sabha Mandapa with warm sandstone pillars
    mandapa_parts = create_mandapa(
        name="Mandapa_Part",
        location=(0, -4.25, 0.0),
        width=8.0, depth=8.6, height=3.6,
        pillar_count_x=4, pillar_count_y=4,
        mat_stone=mat_dark_stone, mat_floor=mat_paving,
        pillar_style="square"
    )
    bpy.ops.object.select_all(action='DESELECT')
    for p in mandapa_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_parts[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"

    # 6. Ghanta (Hanging Brass Bell in Mandapa corridor)
    ghanta = create_hanging_bell(
        name="Ghanta",
        location=(0, -1.0, 2.7),
        mat_brass=mat_brass, scale=1.1
    )

    # 7. Deepam_1 and Deepam_2
    deepam_1 = create_deepam(
        name="Deepam_1",
        location=(-1.1, 1.8, 0.5),
        mat_brass=mat_brass, mat_flame=mat_flame
    )
    deepam_2 = create_deepam(
        name="Deepam_2",
        location=(1.1, 1.8, 0.5),
        mat_brass=mat_brass, mat_flame=mat_flame
    )

    # 8. Priest
    priest = create_human_figure(
        name="Priest",
        location=(1.3, 2.5, 0.5),
        height=1.7,
        mat_skin=mat_skin, mat_cloth=mat_dhoti
    )

    # The Trust's existing plan shows a cross-shaped Sabha Mandapa and a
    # separate chamber between the hall and garbhagriha.
    create_mandapa("Outer_Mandapa_Arms", (0, -4.25, 0), width=11.9, depth=3.7,
                   height=3.6, pillar_count_x=2, pillar_count_y=2,
                   mat_stone=mat_dark_stone, mat_floor=mat_paving)
    vestibule = create_garbhagriha(
        "Darshan_Chamber", (0, .7, 0), width=5.3, depth=3.4, wall_height=3.2,
        door_width=2, door_height=2.6, mat=mat_dark_stone,
    )
    bpy.data.objects.remove(vestibule[0], do_unlink=True)
    create_platform("Darshan_Chamber_Roof", (0, .7, 3.2),
                    size=(5.6, 3.45, .3), mat=mat_dark_stone)
    # The existing plan places Bhavani Shankar at the east end of the hall.
    prior = set(bpy.context.scene.objects)
    build_shrine_chamber("Bhavani_Shankar", (0, 0, 0), 2.25, mat_dark_stone)
    bpy.context.view_layer.update()
    toward_bhavani = Matrix.Translation((0, -9.6, 0)) @ Matrix.Rotation(math.pi, 4, 'Z')
    for obj in set(bpy.context.scene.objects) - prior:
        if obj.parent is None:
            obj.matrix_world = toward_bhavani @ obj.matrix_world
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.48, depth=.18,
                                       location=(0, -9.6, .09))
    yoni = bpy.context.active_object
    yoni.name = "Bhavani_Shankar_Yonipitha"
    yoni.data.materials.append(mat_dark_stone)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=1,
                                        location=(0, -9.6, .41))
    linga = bpy.context.active_object
    linga.name = "Bhavani_Shankar_Linga"
    linga.scale = (.23, .23, .29)
    linga.data.materials.append(mat_dark_stone)

    # The 1881 record belongs to the southern doorway. Model the stone and
    # use the in-game reference to identify the inscription.
    create_platform("Southern_Door_Inscription_Stone", (-5.97, -4.25, 2.76),
                    size=(.16, 1.45, .38), mat=mat_dark_stone)
    add_marker("Southern_Door_Inscription_Anchor", (-6.15, -4.25, 1.2))

    # The survey shows the Devi's rest room and Nahani beside the sanctuary.
    build_shrine_chamber("Devicha_Palang_Room", (4.15, 3.3, 0), 3.5, mat_dark_stone)
    build_shrine_chamber("Nahani_Room", (4.15, 6.4, 0), 2.35, mat_dark_stone)
    create_platform("Sanctum_Approach_Tread_Lower", (0, -.15, 0),
                    size=(1.6, .55, .17), mat=mat_dark_stone)
    create_platform("Sanctum_Approach_Tread_Upper", (0, .28, 0),
                    size=(1.6, .5, .34), mat=mat_dark_stone)

    bpy.context.view_layer.update()
    eastward = Matrix.Rotation(math.pi / 2, 4, 'Z')
    for obj in bpy.context.scene.objects:
        if obj != ground and obj.parent is None:
            obj.matrix_world = eastward @ obj.matrix_world

    # The courtyard outline and approach are traced approximately from the
    # Trust's precinct plan. The visitor route climbs toward the east street.
    outline = [(-44, -7), (-38, -15), (-10, -22), (5, -27), (11, -20),
               (23, -22), (33, -13), (47, -7), (55, -13), (67, -11),
               (70, 9), (68, 26), (46, 21), (31, 15), (23, 17),
               (18, 12), (9, 14), (3, 19), (-14, 26), (-31, 31), (-45, 31)]
    for index, (left, right) in enumerate(zip(outline, outline[1:] + outline[:1])):
        if index in (9, 20):
            continue  # East street entry and historic west gate.
        dx, dy = right[0] - left[0], right[1] - left[1]
        segment = create_platform(
            "Tuljapur_Prakar", (0, 0, 0),
            size=(math.hypot(dx, dy) + .4, .62, 3.25), mat=mat_dark_stone,
        )
        segment.rotation_euler.z = math.atan2(dy, dx)
        segment.location = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2, 0)

    build_east_descent(mat_dark_stone, mat_paving)
    create_mandapa("Sardar_Nimbalkar_Gateway", (67, 12.2, 5.4),
                   width=3.9, depth=6.2, height=4.1, pillar_count_x=2,
                   pillar_count_y=2, mat_stone=mat_dark_stone, mat_floor=mat_paving)
    create_mandapa("Historic_West_Gateway", (-44, 0, 0), width=4.2, depth=5,
                   height=3.8, pillar_count_x=2, pillar_count_y=2,
                   mat_stone=mat_dark_stone, mat_floor=mat_paving)

    # Elongated Kallol basin on the left, Gomukh's smaller spout and basin to
    # the right. Their geometry follows photos on page 54 of the Trust report.
    bpy.context.view_layer.update()
    tank_parts = create_kunda("Kallol_Tirtha", size=(15.5, 6.5, 1.55),
                              mat_stone=mat_dark_stone, mat_water=mat_water, steps=8)
    bpy.context.view_layer.update()
    tank_pose = Matrix.Translation((55, -4.5, 0)) @ Matrix.Rotation(math.radians(26), 4, 'Z')
    for part in tank_parts:
        part.matrix_world = tank_pose @ part.matrix_world
    add_marker("Kallol_Tirtha_Anchor", (54, -1, .85))

    create_kunda("Gomukh_Tirtha", (50, 13, 0), size=(4.7, 3.6, 1.7),
                 mat_stone=mat_dark_stone, mat_water=mat_water, steps=5)
    create_platform("Gomukh_Spout_Block", (50, 14.3, 1.45),
                    size=(.6, .7, .37), mat=mat_dark_stone)
    create_platform("Gomukh_Water_Spill", (50, 13.96, .52),
                            size=(.08, .04, 1.07), mat=mat_water)
    add_marker("Gomukh_Tirtha_Anchor", (50, 12.8, 1.0))

    # Named shrines on the descent and in the courtyard. Small shrine
    # footprints and the installed murtis still need an interior survey.
    for name, position, width in [
        ("Markandeya", (65, 17, 5.4), 3.0),
        ("Siddhivinayaka", (45, 11.1, 0), 3.5),
        ("Vitthal_Rakhumai", (48, 17.1, 0), 3.1),
        ("Annapurna", (-10, -10, 0), 3.5),
        ("Adimaya_Adishakti", (15, 11, 0), 3.1),
    ]:
        build_shrine_chamber(name, position, width, mat_dark_stone)
        x, y, z = position
        add_marker(name + "_Anchor", (x, y + width * .2, z + .1))

    for index, y in enumerate([-3.55, 3.55], 1):
        create_deepamala("Tuljapur_Deepamala_" + str(index), (12.6, y, 0),
                         height=5.8, mat_stone=mat_dark_stone)

    add_marker("Spawn_Point", (64, 10.1, 5.4))

    # Export GLB
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "godot", "assets", "models", "tuljapur_bhavani_kshetra_full.glb")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    export_temple_glb(output_path)
    print("Tuljapur Bhavani build complete!")


if __name__ == "__main__":
    build_tuljapur_bhavani()
