"""Pandua monument study from ASI photographs and plan, not a lost temple."""
import math
import bpy
from present_day_sites import box, cylinder, sphere, material, anchor
from common_geometry import clear_scene

def build():
    clear_scene()
    brick = material('Pandua brick', (.34,.16,.11))
    plaster = material('Weathered surki', (.43,.41,.34))
    stone = material('Grey stone', (.24,.25,.23))
    grass = material('Pandua ground', (.22,.29,.15))
    box('Ground_Pandua',(9,0,-.18),(115,105,.36),grass)
    # ASI's 127-foot tower, four diminishing stages. Profiles approximate.
    cx,cy=34,8
    box('Minar_Platform',(cx,cy,.13),(17,17,.26),plaster,.06)
    bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=8,radius2=6.8,depth=2.4,location=(cx,cy,1.45))
    bpy.context.object.name='Minar_Sloping_Base'
    bpy.context.object.data.materials.append(brick)
    height=2.65
    for stage,(radius,depth) in enumerate([(5.8,6.0),(4.8,13.2),(3.65,7.7),(2.65,6.3)]):
        cylinder(f'Minar_Stage_{stage+1}',(cx,cy,height+depth/2),radius,depth,plaster)
        for offset in [0,.23]:
            cylinder(f'Minar_Cornice_{stage}_{offset}',(cx,cy,height+depth-.1+offset),radius+.28,.18,plaster)
        if stage < 3:
            for rib in range(64):
                angle=math.tau*rib/64
                cylinder(f'OrnamentDetail_Minar_Flute_{stage}_{rib}',(cx+math.cos(angle)*radius,cy+math.sin(angle)*radius,height+depth*.50),.045,depth*.88,plaster)
        height+=depth
    cylinder('Minar_Top_Ring',(cx,cy,height+.15),2.25,.30,plaster)
    sphere('Minar_Finial',(cx,cy,height+.85),(.58,.58,.65),plaster)
    anchor('Pandua_Minar',(cx,cy,1.0))
    # Roofless east-facing Bari Masjid lies west of minaret in ASI plan.
    mx=-20
    box('BariMasjid_Floor',(mx,0,.05),(13,70,.10),stone)
    box('BariMasjid_West_Ruin',(mx-6.5,0,2.1),(.8,70,4.2),brick,.04)
    for side in [-1,1]:
        box('BariMasjid_End_Ruin',(mx,side*35,1.5),(13,.8,3),brick,.04)
    for index in range(21):
        y=-33.3+index*3.33
        for side in [-1,1]:
            box(f'Mihrab_Jamb_{index}_{side}',(mx-5.98,y+side*.65,1.28),(.24,.22,2.3),brick)
        box(f'Mihrab_Header_{index}',(mx-5.98,y,2.48),(.25,1.52,.24),brick)
        if index in [5,6,10,11,12,13]:
            continue
        x=mx+6.5
        for side in [-1,1]:
            box(f'East_Arcade_Pier_{index}_{side}',(x,y+side*1.48,1.0),(.75,.37,2),brick,.035)
        for wedge in range(14):
            angle=math.pi*(wedge+.5)/14
            o=box(f'Arcade_Arch_{index}_{wedge}',(x,y+math.cos(angle)*1.30,1.85+math.sin(angle)*1.30),(.78,.31,.30),brick,.01)
            o.rotation_euler.x=angle-math.pi/2
    for row in range(2):
        for index in range(1,20):
            y=-33.3+index*3.33
            h=1.7 if (row+index)%4==0 else .54
            cylinder(f'Column_Remnant_{row}_{index}',(mx-2+row*4,y,h/2+.1),.24,h,stone)
    anchor('BariMasjid_Ruins',(mx,0,.1))
    anchor('Pandua_Interpretation_Point',(12,-13,.1))
    anchor('Spawn_Point',(12,-25,.1))
