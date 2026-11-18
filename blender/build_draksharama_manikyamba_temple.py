"""Draksharamam precinct modeled from satellite imagery and Rama Rao's survey."""

import math

import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene, create_gopuram, create_mandapa, create_nandi, create_pillar, create_tree
from common_materials import create_gold_metal, create_granite_stone, create_green_foliage, create_tree_bark, create_white_marble
from deity_detail import Sculpture, palette
from present_day_sites import anchor, box, cylinder, finish, linga, material


def rotate_new_objects(previous, transform):
    bpy.context.view_layer.update()
    for obj in set(bpy.context.scene.objects) - previous:
        if obj.parent is None:
            obj.matrix_world = transform @ obj.matrix_world


def build_gates(stone, white, gold, lawn):
    box("Ground_Outer_Prakara", (0, 0, -.23), (168, 157, .36), lawn)
    for side, x, y, rotation, span in [
        ("West", -69, 0, math.pi / 2, 130), ("East", 69, 0, math.pi / 2, 130),
        ("North", 0, 65, 0, 138), ("South", 0, -65, 0, 138),
    ]:
        previous = set(bpy.context.scene.objects)
        gap = 5.6
        for sign in [-1, 1]:
            section = (span - gap) / 2
            box("Outer_Prakara_" + side, (sign * (gap / 2 + section / 2), 0, 1.8),
                (section, .95, 3.6), stone, .04)
        height = {"West": 13, "East": 8.8, "North": 7, "South": 6.4}[side]
        create_gopuram("Outer_Gopuram_" + side, base_width=8.4, base_depth=5.1,
                       height=height, tiers=5 if side == "West" else 3, mat=white, mat_gold=gold)
        rotate_new_objects(previous, Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rotation, 4, 'Z'))

    for x in [-57, 57]:
        for y in [-4.7, 4.7]:
            create_mandapa("Outer_Gate_Verandah", (x, y, 0), width=9.2, depth=5.2,
                           height=3.4, pillar_count_x=3, pillar_count_y=3,
                           mat_stone=stone, mat_floor=stone)
    create_mandapa("Northwest_Pillared_Mandapa", (-38, 30, 0), width=13, depth=26,
                   height=3.5, pillar_count_x=6, pillar_count_y=13, mat_stone=stone, mat_floor=stone)


def build_inner_enclosure(stone, paving):
    box("Inner_Court_Paving", (0, 0, -.085), (56.2, 39.2, .17), paving)
    for name, x, y, length, rotate, has_gate in [
        ("North", 0, 19.5, 56, 0, False), ("South", 0, -19.5, 56, 0, True),
        ("East", 28, 0, 39, math.pi / 2, True), ("West", -28, 0, 39, math.pi / 2, False),
    ]:
        previous = set(bpy.context.scene.objects)
        inward = 1 if name in ("South", "East") else -1
        for floor in [0, 3.35]:
            gate = 4.8 if has_gate and floor == 0 else 0
            segments = [(0, length)] if not gate else [
                (sign * (length + gate) / 4, (length - gate) / 2) for sign in [-1, 1]
            ]
            for middle, width in segments:
                box(name + "_Prakara_Wall", (middle, 0, floor + 1.66), (width, .7, 3.32), stone)
            box(name + "_Gallery_Cornice", (0, inward * 2.25, floor + 3.23),
                (length, 5.2, .27), stone, .025)
            for index in range(math.floor(length / 3.4) + 1):
                along = -length / 2 + 1.35 + index * 3.35
                if abs(along) > length / 2 - .35 or gate and abs(along) < gate / 2 + .33:
                    continue
                create_pillar(name + "_Gallery_Column", (along, inward * 4.15, floor), height=3.12,
                              radius=.25, mat=stone, style="octagonal")
        rotate_new_objects(previous, Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rotate, 4, 'Z'))


def build_linga_shrine(stone, white, gold):
    # The main entrance faces east. Build the two stairs along its north and
    # south sides to leave the ground and upper darshan spaces connected.
    for width, depth, z in [(21, 14.5, .15), (20.2, 13.8, .43)]:
        box("Bhimeswara_Adhisthana", (-5, 0, z), (width, depth, .25), stone, .03)
    for y in [-6.75, 6.75]:
        box("Bhimeswara_Side_Wall", (-5.2, y, 3.55), (19.5, .65, 6.8), stone, .045)
    box("Bhimeswara_West_Wall", (-14.85, 0, 3.55), (.68, 14, 6.8), stone, .045)
    for y in [-4.4, 4.4]:
        box("Bhimeswara_East_Front_Wall", (4.7, y, 3.55), (.62, 4.75, 6.8), stone, .045)
    for z in [3.42, 6.84]:
        box("Bhimeswara_Door_Lintel", (4.72, 0, z), (.73, 4.3, .45), stone)
    for y in [-3.85, 3.85]:
        box("Bhimeswara_Upper_Floor_Side", (-5, y, 3.36), (19.3, 5.8, .24), stone)
    for x in [-12, 1]:
        box("Bhimeswara_Upper_Floor_Axial", (x, 0, 3.36), (6.6, 2.7, .24), stone)
    box("Bhimeswara_Upper_East_Porch", (8.1, 0, 3.35), (7.1, 14, .25), stone, .04)
    for y in [-5.2, -2.65, 2.65, 5.2]:
        for x in [6.7, 10.4]:
            create_pillar("Bhimeswara_Upper_Porch_Column", (x, y, 3.48),
                          height=3.22, radius=.28, mat=stone, style="octagonal")
    for y in [-6.9, 6.9]:
        for k in range(21):
            rise = (k + 1) * 3.48 / 21
            box("Bhimeswara_Upper_Stair_Tread", (18.0 - (k + .5) * .34, y, rise / 2),
                (.35, 2.85, rise), stone, .01)
        box("Bhimeswara_Stair_Landing", (10.55, y, 3.355), (1.05, 2.85, .25), stone)
    for i in range(3):
        rise = .16 * (i + 1)
        box("Bhimeswara_Lower_Door_Step", (5.55 - i * .35, 0, rise / 2),
            (.37, 3.6, rise), stone)
    for y in [-1.07,1.07]:
        box("Linga_Upper_Opening_Balustrade", (-5.5,y,3.84), (6.15,.15,.72), stone)
    box("Bhimeswara_Roof", (-2, 0, 6.94), (27, 15, .38), stone, .055)
    for y in [-6.6, 6.6]:
        for x in range(-14, 6, 2):
            box("Bhimeswara_Upper_Stone_Pilaster", (x, y, 5.3), (.38, .9, 3.05), stone, .035)
    for width, z, height in [(8.8, 7.52, .65), (7.2, 8.27, 1.1), (6.28, 9.11, .5),
                             (5.45, 9.67, .69), (4.2, 10.24, .45)]:
        box("Bhimeswara_Whitewashed_Vimana", (-7.1, 0, z), (width, width, height), white, .08)
    cylinder("Bhimeswara_Kalasha", (-7.1, 0, 10.78), .25, .66, gold)
    # A single tall pale shaft passes through the upper-floor opening.
    linga("Bhimeswara_Linga", (-5.65, 0, .52), 3.75, white)
    anchor("Bhimeswara_Upper_Darshan", (-4.5, 0, 4.25))


def shrine_bay(name, xyz, yaw, stone, wide=2.65):
    """Build a shrine on the inner gallery wall, open toward the courtyard."""
    previous = set(bpy.context.scene.objects)
    for x in [-wide / 2, wide / 2]:
        box(name + "_Door_Jamb", (x, -.8, 1.22), (.22, .53, 2.44), stone, .03)
    box(name + "_Lintel", (0, -.8, 2.51), (wide + .22, .55, .36), stone, .025)
    box(name + "_Pedestal", (0, .4, .24), (wide * .72, .83, .48), stone, .05)
    anchor(name + "_Anchor", (0, .18, .42))
    transform = Matrix.Translation(xyz) @ Matrix.Rotation(yaw, 4, 'Z')
    rotate_new_objects(previous, transform)


def manikyamba_study(position):
    # A seated devotional study. The drapery and ornaments are original
    # modeling and the hidden anatomy of the installed image is unverified.
    study = Sculpture()
    colors = palette(study)
    dark, gold, silk = colors["black"], colors["gold"], colors["red"]
    study.ellipsoid((0, 0, .08), (.47, .35, .08), gold)
    for side in [-1, 1]:
        study.ellipsoid((side * .19, -.045, .23), (.29, .185, .13), silk)
        study.tube([(side*.18, 0, .6), (side*.33, -.052, .39), (side*.22, -.20, .35)], .061, dark, 12)
    study.ellipsoid((0, 0, .48), (.21, .135, .25), silk)
    study.ellipsoid((0, -.012, .78), (.13, .112, .16), dark)
    for side in [-1, 1]:
        study.ellipsoid((side*.124, -.026, .77), (.038, .042, .067), gold)
        study.ellipsoid((side*.053, -.106, .801), (.036, .017, .014), colors["eye"])
        study.ellipsoid((side*.053, -.119, .801), (.012, .009, .012), dark)
    for z, radius in [(.922, .143), (.982, .122), (1.035, .085)]:
        study.ellipsoid((0, .012, z), (radius, radius*.72, .053), gold)
    study.rosette((0, -.104, .974), .051, gold, colors["red"])
    for width, middle in [(.15, .55), (.21, .44)]:
        study.tube([(-width, -.068, .68), (0, -.155, middle), (width, -.068, .68)], .018, gold, 10)
    return study.finish("Manikyamba_Seated_Sculpture_Study", position, 1.32)


def build_draksharama():
    clear_scene()
    stone = create_granite_stone("Draksharamam_Cut_Stone", (.25,.225,.19,1))
    paving = create_granite_stone("Draksharamam_Court_Paving", (.42,.37,.29,1))
    white = create_white_marble("Draksharamam_Whitewashed_Towers", (.84,.80,.70,1), .75)
    gold = create_gold_metal("Draksharamam_Brass")
    lawn = material("Draksharamam_Outer_Court_Grass", (.26,.29,.175))
    water = material("Sapta_Godavari_Water", (.11,.23,.20), .58)
    bark = create_tree_bark("Draksharamam_Peepal_Bark")
    foliage = create_green_foliage("Draksharamam_Peepal")
    build_gates(stone, white, gold, lawn)
    build_inner_enclosure(stone, paving)
    build_linga_shrine(stone, white, gold)

    # Current aerial footprint shows a long south approach between enclosures.
    box("South_Covered_Approach_Paving", (0, -42, -.01), (6.2, 42, .16), paving)
    canopy = material("South_Passage_Blue_Sheet", (.23,.37,.51), .75)
    for y in range(-60, -21, 4):
        for x in [-2.5, 2.5]:
            create_pillar("South_Passage_Post", (x,y,0), height=3.35, radius=.13, mat=stone)
    box("South_Passage_Sheet_Roof", (0,-42,3.45), (6,38,.16), canopy)

    # Named groups in the four inner galleries, in their documented sections.
    shrine_bay("Manikyamba", (1.3, 18.1, 0), 0, stone, 4.0)
    manikyamba_study((1.3, 18.37, .49))
    for name, x in [("Ganapati",-19),("Nakuleswara",-13.5),("Brahma",-8),
                    ("Lakshmi_Narayana",8),("Virupaksha",13.5),("Nataraja",19)]:
        shrine_bay(name, (x,-18.1,0), math.pi, stone)
    linga("Nakuleswara_Study", (-13.5,-18.25,.49), .66, stone)
    linga("Virupaksha_Study", (13.5,-18.25,.49), .66, stone)
    for name, y in [("Virabhadra",10),("Vatuka_Bhairava",5.3),
                    ("Dikpalakas",-6.3),("Navagrahas",-12.2)]:
        shrine_bay(name, (26.5,y,0), -math.pi / 2, stone, 3.6 if name in ("Dikpalakas","Navagrahas") else 2.65)
    for name, y in [("Saptamatrikas",9),("Kumara_Group",1.8),("Mahishasuramardini",-7)]:
        shrine_bay(name, (-26.5,y,0), math.pi / 2, stone, 3.9)
    navagraha = Sculpture()
    basalt = navagraha.material("Navagraha_Stone", (.16,.13,.105))
    # The surveyed eastern hall houses a group. Nine small human figures
    # represent the group while individual attributes require photographs.
    for index in range(9):
        y = (index - 4) * .32
        navagraha.ellipsoid((0,y,.24),(.115,.12,.135),basalt)
        navagraha.ellipsoid((-.015,y,.42),(.065,.061,.073),basalt)
        for offset in [-.07,.07]:
            navagraha.ellipsoid((-.035,y + offset,.105),(.11,.065,.055),basalt)
    navagraha.finish("Navagraha_Group_Study", (26.65,-12.2,.49))

    # The southern inner doorway carries a Gajalakshmi lintel, recorded on
    # p. 20. Model the central seated figure, lotuses and flanking elephants.
    lintel = Sculpture()
    relief = lintel.material("South_Door_Lintel_Stone", (.31,.25,.18))
    lintel.ellipsoid((0,0,.31),(.19,.075,.18),relief)
    lintel.ellipsoid((0,-.05,.54),(.075,.048,.08),relief)
    for side in [-1,1]:
        lintel.ellipsoid((side*.63,0,.25),(.25,.085,.17),relief)
        lintel.ellipsoid((side*.40,-.018,.40),(.14,.071,.13),relief)
        lintel.tube([(side*.36,-.035,.42),(side*.28,-.06,.53),
                      (side*.20,-.064,.62)], .034, relief, 10)
        lintel.rosette((side*.29,-.057,.29), .074, relief, petals=6)
    lintel.finish("Gajalakshmi_South_Gateway_Relief_Study", (0,-19.88,2.76))
    anchor("Gajalakshmi_South_Lintel_Anchor", (0,-20.05,1.5))

    # Three shrines in one west-facing hall outside the south inner entrance.
    create_mandapa("Vijayeswara_Triple_Shrine_Hall", (9.4,-25.8,0), width=10, depth=9.5,
                   height=3.5, pillar_count_x=3, pillar_count_y=3, mat_stone=stone, mat_floor=paving)
    for name, pos, yaw in [
        ("Vijayeswara",(13.3,-25.8,0),-math.pi/2),
        ("Annapurna",(9.4,-29.3,0),math.pi),
        ("Dakshinamurti",(9.4,-22.3,0),0),
    ]:
        shrine_bay(name,pos,yaw,stone,2.2)
    linga("Vijayeswara_Linga", (13.5,-25.8,.48), .72, stone)
    shrine_bay("Kala_Bhairava", (51,45,0), 0, stone, 3.9)
    box("Kala_Bhairava_Roof", (51,45,3.12), (5.5,5.6,.28), stone, .04)
    create_mandapa("East_Nandi_Mandapa", (41,0,0), width=8.7, depth=8,
                   height=3.8, pillar_count_x=3, pillar_count_y=2, mat_stone=stone, mat_floor=paving)
    nandi = create_nandi("Bhimeswara_Nandi", (0,0,0), scale=1.9, mat=stone)
    nandi.rotation_euler.z = math.pi / 2
    nandi.location = (41,0,.11)
    cylinder("Peepal_Platform", (53,1,.27), 3,.55, stone)
    create_tree("East_Courtyard_Peepal", (53,1,.55), height=8, mat_trunk=bark, mat_leaves=foliage)
    box("Sapta_Godavari_Tank", (88,4,-.39), (27,145,.19), water)
    box("East_Tank_Causeway", (87,0,-.10), (38,4,.24), paving)
    box("Bhimeswara_South_Wall_Inscription_Stone", (-11,-7.11,1.3),
        (1.76,.1,.85), stone, .025)
    anchor("Bhimeswara_South_Wall_Inscription", (-11,-7.22,1.25))
    anchor("Spawn_Point", (0,-55,.15))

    # The satellite view places the east axis about 21 degrees north of east.
    rotate_new_objects(set(), Matrix.Rotation(math.radians(21),4,'Z'))
    finish("draksharama_manikyamba")


build_draksharama()
