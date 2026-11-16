"""
Kashi Vishalakshi Temple (Mir Ghat, Varanasi, Uttar Pradesh)
Vishalakshi Devi - Nagara Shikhara, Annapurna Shrine & Ganga Ghat
"""
import sys
from pathlib import Path

blender_dir = Path(__file__).resolve().parent
if str(blender_dir) not in sys.path:
    sys.path.insert(0, str(blender_dir))

import bpy
import bmesh
import math
from mathutils import Vector

import common_materials as mats
import common_geometry as geom

# Ensure Blender 5.3 compatibility
def export_glb_53(filepath, apply_modifiers=True):
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

geom.export_glb = export_glb_53

def build_kashi_vishalakshi():
    geom.clear_scene()

    # 1. Materials
    mat_sandstone = mats.create_sandstone("Kashi_Sandstone", color=(0.78, 0.62, 0.42, 1.0))
    mat_red_sandstone = mats.create_sandstone("Red_Sandstone", color=(0.65, 0.35, 0.22, 1.0))
    mat_gold = mats.create_gold_metal("Kalasha_Gold")
    mat_brass = mats.create_brass_metal("Bell_Brass")
    mat_water = mats.create_water("Ganga_Water", color=(0.18, 0.42, 0.48, 0.88))
    mat_flame = mats.create_flame_emission("Deepam_Flame")
    mat_skin = mats.create_skin("Priest_Skin")
    mat_cloth = mats.create_white_dhoti("Priest_Dhoti")
    mat_silk = mats.create_red_silk("Devi_Silk")
    mat_black_stone = mats.create_black_stone("Bhairava_Basalt")
    mat_paving = mats.create_granite_stone("Ghat_Paving", color=(0.68, 0.64, 0.58, 1.0))
    mat_garland = mats.create_flower_garland("Marigold_Garland")

    # 2. Main Ground Plane
    ground = geom.create_ground_plane(name="Ground_Main", size=75, mat=mat_paving)

    # 3. Holy Ganga Ghat & River (East side: X = 16 to 36)
    # Ganga Water Plane
    bpy.ops.mesh.primitive_plane_add(size=1, location=(26.0, 5.0, 0.05))
    ganga = bpy.context.active_object
    ganga.name = "Ganga_River"
    ganga.scale = (12.0, 36.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    ganga.data.materials.append(mat_water)

    # Mir Ghat stone steps descending to Ganga
    for i in range(8):
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=(13.0 + i * 1.5, 5.0, 0.6 - i * 0.08)
        )
        step = bpy.context.active_object
        step.scale = (0.75, 26.0, 0.1)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(mat_sandstone)

    # 4. Jagati (Raised Sandstone Temple Platform)
    jagati = geom.create_platform(
        name="Jagati_Platform",
        location=(0, 7.5, 0),
        size=(18.0, 22.0, 0.6),
        mat=mat_sandstone,
        steps=3
    )

    # 5. Garbhagriha (Sanctum)
    garb_center = (0.0, 13.5, 0.6)
    garb_objs = geom.create_garbhagriha(
        name="Garbhagriha_Wall",
        location=garb_center,
        width=5.0,
        depth=5.0,
        wall_height=4.2,
        wall_thickness=0.5,
        mat=mat_sandstone,
        door_width=1.6,
        door_height=2.7
    )

    # Join Garbhagriha walls & floor into "Garbhagriha"
    bpy.ops.object.select_all(action='DESELECT')
    for o in garb_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = garb_objs[0]
    bpy.ops.object.join()
    garbhagriha = bpy.context.active_object
    garbhagriha.name = "Garbhagriha"

    # 6. Nagara Shikhara (Curvilinear tower with Urushringas, Amalaka & Golden Kalasha)
    shikhara_objs = geom.create_shikhara(
        name="Nagara_Shikhara",
        location=(garb_center[0], garb_center[1], garb_center[2] + 4.2),
        base_width=4.8,
        height=8.5,
        tiers=6,
        mat=mat_sandstone,
        style="nagara"
    )
    # The kalasha created by create_shikhara is the last object, apply gold material to it
    for obj in shikhara_objs:
        if "Kalasha" in obj.name or "Amalaka" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_gold)

    # 7. Deity_Vishalakshi Murti
    # 4-armed goddess with large divine eyes, golden mukuta, abhaya & varada, lotus, vessel
    devi_objs = []
    devi_loc = (0.0, 14.5, 0.62)

    # Lotus Altar Base
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.85, depth=0.25,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.125)
    )
    altar = bpy.context.active_object
    altar.data.materials.append(mat_gold)
    devi_objs.append(altar)

    # Torso (Draped in radiant red silk)
    bpy.ops.mesh.primitive_cube_add(
        size=2, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.85)
    )
    torso = bpy.context.active_object
    torso.scale = (0.3, 0.18, 0.4)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_silk)
    devi_objs.append(torso)

    # Head (Polished golden brass murti)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.16, location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.35)
    )
    head = bpy.context.active_object
    head.data.materials.append(mat_gold)
    devi_objs.append(head)

    # Large Divine Eyes (Vishala-Akshi - iconic wide almond eyes)
    for eye_x in [-0.065, 0.065]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.038,
            location=(devi_loc[0] + eye_x, devi_loc[1] - 0.14, devi_loc[2] + 1.38)
        )
        eye = bpy.context.active_object
        eye.scale = (1.6, 0.6, 0.8)
        bpy.ops.object.transform_apply(scale=True)
        eye.data.materials.append(mat_black_stone)
        devi_objs.append(eye)

    # Golden Mukuta (Nagara tiered crown)
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.2, radius2=0.04, depth=0.5,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 1.7)
    )
    crown = bpy.context.active_object
    crown.data.materials.append(mat_gold)
    devi_objs.append(crown)

    # Prabhavali (Golden ornate arch behind Vishalakshi)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.6, minor_radius=0.06,
        location=(devi_loc[0], devi_loc[1] + 0.08, devi_loc[2] + 1.25)
    )
    prabha = bpy.context.active_object
    prabha.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    prabha.data.materials.append(mat_gold)
    devi_objs.append(prabha)

    # 4 Arms
    # Upper Right: Lotus flower
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.45,
        location=(devi_loc[0] + 0.4, devi_loc[1], devi_loc[2] + 1.05)
    )
    arm_ur = bpy.context.active_object
    arm_ur.rotation_euler = (0, 0.5, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ur.data.materials.append(mat_gold)
    devi_objs.append(arm_ur)

    # Upper Left: Amrita Kalasha (sacred pot)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.45,
        location=(devi_loc[0] - 0.4, devi_loc[1], devi_loc[2] + 1.05)
    )
    arm_ul = bpy.context.active_object
    arm_ul.rotation_euler = (0, -0.5, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ul.data.materials.append(mat_gold)
    devi_objs.append(arm_ul)

    # Lower Right: Abhaya Mudra
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.42,
        location=(devi_loc[0] + 0.35, devi_loc[1], devi_loc[2] + 0.75)
    )
    arm_lr = bpy.context.active_object
    arm_lr.rotation_euler = (0, 0.25, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_lr.data.materials.append(mat_gold)
    devi_objs.append(arm_lr)

    # Lower Left: Varada Mudra
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.42,
        location=(devi_loc[0] - 0.35, devi_loc[1], devi_loc[2] + 0.75)
    )
    arm_ll = bpy.context.active_object
    arm_ll.rotation_euler = (0, -0.25, 0)
    bpy.ops.object.transform_apply(rotation=True)
    arm_ll.data.materials.append(mat_gold)
    devi_objs.append(arm_ll)

    # Padmasana Seated Cross-legged Base
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.4, depth=0.25,
        location=(devi_loc[0], devi_loc[1], devi_loc[2] + 0.38)
    )
    legs = bpy.context.active_object
    legs.data.materials.append(mat_silk)
    devi_objs.append(legs)

    # Flower Garland
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.28, minor_radius=0.045,
        location=(devi_loc[0], devi_loc[1] - 0.05, devi_loc[2] + 0.9)
    )
    garland = bpy.context.active_object
    garland.data.materials.append(mat_garland)
    devi_objs.append(garland)

    # Join into single Deity object named "Deity_Vishalakshi"
    bpy.ops.object.select_all(action='DESELECT')
    for o in devi_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = devi_objs[0]
    bpy.ops.object.join()
    deity = bpy.context.active_object
    deity.name = "Deity_Vishalakshi"

    # 8. Deepams inside Garbhagriha
    deepam1 = geom.create_deepam(
        name="Deepam_1",
        location=(-1.3, 13.0, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    deepam2 = geom.create_deepam(
        name="Deepam_2",
        location=(1.3, 13.0, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_3",
        location=(-1.3, 14.8, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )
    geom.create_deepam(
        name="Deepam_4",
        location=(1.3, 14.8, 0.62),
        mat_brass=mat_brass,
        mat_flame=mat_flame
    )

    # 9. Priest near sanctum door (standing at right of doorway)
    priest = geom.create_human_figure(
        name="Priest",
        location=(1.4, 10.2, 0.6),
        height=1.75,
        mat_skin=mat_skin,
        mat_cloth=mat_cloth
    )

    # 10. Mandapa (Gudhamandapa / Pillared Hall in front of Garbhagriha)
    mandapa_objs = geom.create_mandapa(
        name="Mandapa_Hall",
        location=(0.0, 5.0, 0.6),
        width=8.0,
        depth=7.0,
        height=3.8,
        pillar_count_x=4,
        pillar_count_y=3,
        mat_stone=mat_sandstone,
        mat_floor=mat_paving,
        pillar_style="square"
    )
    bpy.ops.object.select_all(action='DESELECT')
    for o in mandapa_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = mandapa_objs[0]
    bpy.ops.object.join()
    mandapa = bpy.context.active_object
    mandapa.name = "Mandapa"

    # 11. Ghanta (Hanging Brass Bell at mandapa entrance)
    ghanta = geom.create_hanging_bell(
        name="Ghanta",
        location=(0.0, 1.4, 3.2),
        mat_brass=mat_brass,
        scale=1.2
    )

    # 12. Spawn Point (facing North)
    spawn = bpy.data.objects.new("Spawn_Point", None)
    spawn.location = (0.0, -8.0, 0.0)
    bpy.context.collection.objects.link(spawn)

    # 13. Annapurna Sub-Shrine (Varanasi's beloved Annapurna Devi shrine in courtyard)
    anna_objs = []
    anna_loc = (-10.5, 2.5, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(anna_loc[0], anna_loc[1], anna_loc[2] + 0.3))
    an_base = bpy.context.active_object
    an_base.scale = (1.6, 1.6, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    an_base.data.materials.append(mat_sandstone)
    anna_objs.append(an_base)
    for dx, dy in [(-1.3, -1.3), (1.3, -1.3), (-1.3, 1.3), (1.3, 1.3)]:
        p = geom.create_pillar(f"AN_Pillar_{dx}_{dy}", (anna_loc[0] + dx, anna_loc[1] + dy, anna_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_sandstone)
        anna_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(anna_loc[0], anna_loc[1], anna_loc[2] + 2.9))
    an_roof = bpy.context.active_object
    an_roof.scale = (1.8, 1.8, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    an_roof.data.materials.append(mat_sandstone)
    anna_objs.append(an_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.4, radius2=0.2, depth=1.6, location=(anna_loc[0], anna_loc[1], anna_loc[2] + 3.9))
    an_shikhara = bpy.context.active_object
    an_shikhara.data.materials.append(mat_sandstone)
    anna_objs.append(an_shikhara)
    # Annapurna murti holding ladle and food bowl
    an_murti = geom.create_deity_figure(name="Annapurna_Murti", location=(anna_loc[0], anna_loc[1], anna_loc[2] + 0.6), height=1.2, arms=4, mat_body=mat_gold, mat_ornament=mat_red_sandstone)
    anna_objs.append(an_murti)
    # Join into Annapurna shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in anna_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = anna_objs[0]
    bpy.ops.object.join()
    annapurna_shrine = bpy.context.active_object
    annapurna_shrine.name = "Annapurna_Shrine"

    # 14. Bhairava Shrine (Kala Bhairava - Kotwal of Varanasi on West side)
    bhairava_objs = []
    bhairava_loc = (-10.5, 8.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(bhairava_loc[0], bhairava_loc[1], bhairava_loc[2] + 0.3))
    b_base = bpy.context.active_object
    b_base.scale = (1.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    b_base.data.materials.append(mat_sandstone)
    bhairava_objs.append(b_base)
    for dx, dy in [(-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)]:
        p = geom.create_pillar(f"KB_Pillar_{dx}_{dy}", (bhairava_loc[0] + dx, bhairava_loc[1] + dy, bhairava_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_sandstone)
        bhairava_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(bhairava_loc[0], bhairava_loc[1], bhairava_loc[2] + 2.9))
    b_roof = bpy.context.active_object
    b_roof.scale = (1.6, 1.6, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    b_roof.data.materials.append(mat_sandstone)
    bhairava_objs.append(b_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.2, radius2=0.2, depth=1.5, location=(bhairava_loc[0], bhairava_loc[1], bhairava_loc[2] + 3.8))
    b_cone = bpy.context.active_object
    b_cone.data.materials.append(mat_sandstone)
    bhairava_objs.append(b_cone)
    # Kala Bhairava idol (dark basalt stone with trishula & dog vahana)
    kb_murti = geom.create_deity_figure(name="Kala_Bhairava_Murti", location=(bhairava_loc[0], bhairava_loc[1], bhairava_loc[2] + 0.6), height=1.2, arms=4, mat_body=mat_black_stone, mat_ornament=mat_gold)
    bhairava_objs.append(kb_murti)
    # Join into Bhairava_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in bhairava_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = bhairava_objs[0]
    bpy.ops.object.join()
    bhairava_shrine = bpy.context.active_object
    bhairava_shrine.name = "Bhairava_Shrine"

    # 15. Ganesha Shrine (Dhundhiraja Ganesha on West side)
    ganesha_objs = []
    ganesha_loc = (-10.5, 13.5, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(ganesha_loc[0], ganesha_loc[1], ganesha_loc[2] + 0.3))
    g_base = bpy.context.active_object
    g_base.scale = (1.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    g_base.data.materials.append(mat_sandstone)
    ganesha_objs.append(g_base)
    for dx, dy in [(-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)]:
        p = geom.create_pillar(f"DG_Pillar_{dx}_{dy}", (ganesha_loc[0] + dx, ganesha_loc[1] + dy, ganesha_loc[2] + 0.6), height=2.2, radius=0.12, mat=mat_sandstone)
        ganesha_objs.append(p)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(ganesha_loc[0], ganesha_loc[1], ganesha_loc[2] + 2.9))
    g_roof = bpy.context.active_object
    g_roof.scale = (1.6, 1.6, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    g_roof.data.materials.append(mat_sandstone)
    ganesha_objs.append(g_roof)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.2, radius2=0.2, depth=1.5, location=(ganesha_loc[0], ganesha_loc[1], ganesha_loc[2] + 3.8))
    g_cone = bpy.context.active_object
    g_cone.data.materials.append(mat_sandstone)
    ganesha_objs.append(g_cone)
    # Dhundhiraja Ganesha idol
    g_murti = geom.create_deity_figure(name="Dhundhiraja_Ganesha_Murti", location=(ganesha_loc[0], ganesha_loc[1], ganesha_loc[2] + 0.6), height=1.1, arms=4, mat_body=mat_red_sandstone, mat_ornament=mat_gold)
    ganesha_objs.append(g_murti)
    # Join into Ganesha_Shrine
    bpy.ops.object.select_all(action='DESELECT')
    for o in ganesha_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = ganesha_objs[0]
    bpy.ops.object.join()
    ganesha_shrine = bpy.context.active_object
    ganesha_shrine.name = "Ganesha_Shrine"

    # 16. Prakara Wall with Sandstone Jali screens
    prakara_objs = geom.create_prakara_wall(
        name="Prakara_Vishalakshi",
        center=(0, 6.5, 0),
        width=36.0,
        depth=32.0,
        wall_height=3.4,
        wall_thickness=0.55,
        mat=mat_sandstone,
        gate_width=4.0,
        gate_sides=["S"]
    )

    # 17. Export GLB
    export_path = Path(__file__).resolve().parent.parent / "godot" / "assets" / "models" / "kashi_vishalakshi_kshetra_full.glb"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    geom.export_glb(str(export_path))
    print(f"Kashi Vishalakshi export complete: {export_path}")

if __name__ == "__main__":
    build_kashi_vishalakshi()
