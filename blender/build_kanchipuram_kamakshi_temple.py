"""Kanchi Kamakshi: restored compound, Gayatri Mandapam and shrine studies."""
import math
from mathutils import Matrix, Vector
import bpy

from common_geometry import clear_scene, create_deepam, create_shikhara
from common_materials import create_granite_stone
from deity_detail import Sculpture, crown_band, garland, palette
from kanchi_precinct import boundary, build_tank, cube, framed_portal, hall, orient_scene, pillar, point
from present_day_sites import anchor, cylinder, finish, linga, material, sphere


def setup_murti(s, p, height, seated, face_form='human'):
    dark=p['black']
    torso=height*.55
    face=height*.82
    s.ellipsoid((0,.05,torso),(.181*height,.105*height,.175*height),dark,24,18)
    s.ellipsoid((0,-.016,face),(.104*height,.084*height,.128*height),dark,30,20)
    for side in [-1,1]:
        if seated:
            s.ellipsoid((side*.17*height,-.065,height*.155),(.23*height,.134*height,.095*height),p['red'])
        else:
            s.tube([(side*.078*height,-.015,height*.085),(side*.083*height,.015,height*.23),
                    (side*.088*height,.035,height*.43)],height*.071,dark,14)
            s.ellipsoid((side*.079*height,-.055,height*.064),(.077*height,.105*height,.043*height),dark)
        s.ellipsoid((side*.044*height,-.093*height,face+.021*height),
                    (.028*height,.012*height,.012*height),p['gold'],16,10)
        s.rosette((side*.101*height,-.071*height,face-.039*height),.031*height,p['gold'],p['red'])
    if face_form=='boar':
        s.ellipsoid((.042*height,-.114*height,face-.027*height),(.077*height,.114*height,.063*height),dark)
        for side in [-1,1]:
            s.ellipsoid((side*.076*height,-.030*height,face+.087*height),
                        (.035*height,.032*height,.049*height),dark)
    else:
        s.ellipsoid((0,-.103*height,face),(.021*height,.027*height,.033*height),dark)
        s.ellipsoid((0,-.107*height,face-.049*height),(.033*height,.011*height,.009*height),dark)
    crown_band(s,p,height*.19,face+.09*height,-.071*height,4)
    for row in range(4):
        length=(.091+row*.026)*height
        s.tube([(length*math.cos(math.pi*i/29),-.101*height,
                 torso+height*.10-math.sin(math.pi*i/29)*(.033+row*.038)*height) for i in range(30)],
               .007*height,p['gold'],6)
    s.rosette((0,-.113*height,torso-.07*height),.044*height,p['gold'],p['red'])


def kamakshi(position):
    s=Sculpture(); p=palette(s)
    setup_murti(s,p,1.80,True)
    s.ellipsoid((0,.055,.21),(.64,.36,.17),p['gold'],36,18)
    for petal in range(24):
        a=math.tau*petal/24
        s.ellipsoid((.51*math.cos(a),.29*math.sin(a),.237),(.128,.085,.053),
                    p['gold'] if petal%3 else p['red'],14,8)
    s.ellipsoid((0,-.043,.53),(.49,.18,.34),p['red'],36,24)
    for crease in range(21):
        x=(crease-10)*.043
        s.tube([(x*.28,-.188,.75),(x*.65,-.216,.55),(x,-.186,.28)],.007,p['gold'],7)
    for sign in [-1,1]:
        for level in [0,1]:
            hand=(sign*(.39+level*.13),-.132,1.08+level*.31)
            s.tube([(sign*.237,.047,1.15),(sign*(.43+level*.07),.0,.99+level*.39),hand],
                   .048,p['black'],14)
            s.ellipsoid(hand,(.068,.040,.084),p['black'])
            s.ellipsoid((hand[0],hand[1],hand[2]-.043),(.081,.047,.018),p['gold'])
    # Sugarcane bow on the goddess's left, flowers and parrot on her right.
    s.tube([(.52+.15*math.sin(math.pi*i/44),-.098,.55+i*.029) for i in range(45)],.021,p['green'],10)
    s.tube([(.52,-.097,.55),(.52,-.097,1.83)],.005,p['gold'],6)
    for i in range(5):
        x=-.30-i*.047
        s.tube([(x+.09,-.229,.78),(x,-.23,1.13+i*.035)],.012,p['green'],7)
        s.rosette((x,-.24,1.16+i*.035),.047,p['red'],p['yellow'])
    s.ellipsoid((-.56,-.14,1.21),(.056,.037,.071),p['green'])
    s.ellipsoid((-.58,-.17,1.264),(.034,.026,.034),p['green'])
    s.tube([(-.60,-.187,1.26),(-.634,-.19,1.246)],.015,p['orange'],7)
    s.tube([(-.50+.084*math.cos(math.tau*i/40),-.12,1.53+.116*math.sin(math.tau*i/40))
            for i in range(41)],.012,p['gold'],8)
    s.tube([(.51,-.119,1.39),(.53,-.119,1.75),(.60,-.118,1.79),(.642,-.118,1.72)],
           .013,p['gold'],8)
    s.tube([(.064*math.cos(math.pi+math.pi*i/32),-.186,1.65+.045*math.sin(math.pi+math.pi*i/32))
            for i in range(33)],.010,p['silver'])
    for elevation in [0,.046,.098]:
        s.tube([((.83+elevation)*math.cos(math.pi*i/96),.118,
                 .41+(1.47+elevation)*math.sin(math.pi*i/96)) for i in range(97)],.017,p['gold'],8)
    for i in range(35):
        a=math.pi*i/34
        s.rosette((.89*math.cos(a),.088,.42+1.53*math.sin(a)),.032,p['gold'],p['red'])
    for row in range(3):
        garland(s,p,.44+row*.14,1.37,.61+row*.17,-.25-row*.018,53)
    s.finish('Deity_Kamakshi',position)['has_authored_ornaments']=True


def companion(name, position, angle, height, seated=False, form='human'):
    s=Sculpture(); p=palette(s)
    setup_murti(s,p,height,seated,form)
    for side in [-1,1]:
        for i in range(2 if form=='boar' else 1):
            hand=(side*height*(.16+i*.075),-.09*height,height*(.43+i*.29))
            s.tube([(side*.141*height,.01,height*.64),(side*.23*height,-.03,height*(.44+i*.19)),hand],
                   height*.033,p['black'],13)
            s.ellipsoid(hand,(.041*height,.037*height,.059*height),p['black'])
    if name.startswith('Kalvar'):
        for side in [-1,1]:
            x=side*height*.21
            s.rosette((x,-.08,height*.74),.052*height,p['gold'],p['red'])
    if name.startswith('Ardhanari'):
        for i in range(4):
            s.rosette((-.091,-.098,.41+i*.11),.044,p['gold'],p['red'])
    garland(s,p,height*.19,height*.63,height*.37,-.119*height,31)
    obj=s.finish(name,position)
    obj.rotation_euler.z=angle


def shrine(name, x, y, angle, stone, floor=.15, approach=2.15):
    local=Matrix.Translation((x,y,0))@Matrix.Rotation(angle,4,'Z')
    before=set(bpy.context.scene.objects)
    cube(name+'_Niche_Back',(0,.54,floor+1.38),(2.20,.28,2.76),stone,.042)
    for side in [-1,1]:
        cube(name+'_Niche_Jamb',(side*.99,0,floor+1.38),(.24,1.14,2.76),stone,.038)
    cube(name+'_Niche_Canopy',(0,0,floor+2.85),(2.32,1.30,.19),stone,.043)
    cube(name+'_Pedestal',(0,.08,floor+.19),(1.37,.83,.38),stone,.034)
    anchor(name+'_Anchor',(0,.02,floor+.11))
    anchor(name+'_Landing',(0,-approach,floor+.02))
    bpy.context.view_layer.update()
    for obj in set(bpy.context.scene.objects)-before:
        obj.matrix_world=local@obj.matrix_world
    return local


def front_mandapa():
    clear_scene()
    pavement=create_granite_stone('Kanchi_Courtyard_Paving',(.55,.50,.42,1))
    charcoal=create_granite_stone('Kanchi_Gray_Granite',(.355,.326,.28,1))
    stone=create_granite_stone('Kanchi_Interior_Granite',(.39,.345,.29,1))
    cream=material('Kanchi_Ivory_Limework',(.75,.69,.53))
    coping=material('Kanchi_Worn_Terrace',(.58,.54,.47))
    gold=material('Kanchi_Gilt',(.83,.49,.105),.63,.35)
    water=material('Kanchi_Pushkarini',(.031,.092,.075),.17,.13)
    grass=material('Kanchi_Garden',(.19,.27,.09))
    leaves=material('Kanchi_Garden_Trees',(.10,.19,.068))
    bark=material('Kanchi_Garden_Bark',(.21,.135,.072))
    red=material('Kanchi_Kumkum',(.48,.036,.019))
    wick=material('Kanchi_OilLampFlame',(.98,.54,.16),emission=2.4)
    build_tank(charcoal,pavement,water)
    boundary(charcoal,cream,gold)
    for name,bounds,z,columns in [
        ('Vasantha_Mandapam',(1075,960,1327,1177),.24,(7,6)),
        ('Shukrawara_Mandapam',(950,963,1064,1272),.14,(4,7)),
        ('Vahana_Mandapam',(1247,416,1492,565),.0,(7,4)),
        ('Navaratri_Mandapam',(401,299,550,593),.0,(4,7)),
        ('Madapalli_Range',(399,1324,570,1482),.0,(4,4)),
        ('East_Interior_Arrival_Mandapam',(663,1284,760,1380),.0,(3,3)),
        ('North_Prakaras_Range',(1370,612,1462,742),.0,(3,4)),
        ('East_Utility_Range',(1210,1290,1380,1448),.0,(4,5))]:
        x1,y1=point(bounds[0],bounds[3])
        x2,y2=point(bounds[2],bounds[1])
        hall(name,(x1,y1,x2,y2),charcoal,pavement,coping,z,4.25,columns)
    for px,py,w,d in [(444,969,12.1,32.6),(1087,788,7,22),(1384,781,8,8)]:
        x,y=point(px,py)
        cube('Kanchi_Nandavanam_Lawn',(x,y,.12),(w,d,.24),grass,.04)
        for inset,side in [(0,-1),(1,1)]:
            cube('Kanchi_Nandavanam_Granite_Seating',(x+side*(w/2-.12),y,.37),(.51,d,.74),charcoal,.05)
        for i in range(3):
            cylinder('Kanchi_Garden_Trunk',(x,y+(i-1)*d*.29,1.84),.24,3.62,bark)
            sphere('Kanchi_Garden_Canopy',(x,y+(i-1)*d*.29,4.3),(2.9,3.3,2.8),leaves,20)

    # Restoration plan's enclosed temple block, with a smaller Gayatri core.
    x1,y1=point(633,1296)
    x2,y2=point(952,919)
    cube('Kamakshi_Main_Temple_Floor',((x1+x2)/2,(y1+y2)/2,.065),(x2-x1,y2-y1,.13),pavement,.02)
    for x in [x1,x2]:
        cube('Kamakshi_Main_Temple_Long_Wall',(x,(y1+y2)/2,2.6),(.51,y2-y1,5.2),stone,.041)
    cube('Kamakshi_Main_Temple_Sanctum_Back',((x1+x2)/2,y2,2.6),(x2-x1,.51,5.2),stone,.041)
    framed_portal('Kamakshi_East_Temple_Entrance',(x1+x2)/2,y1,x2-x1,4.65,.13,5.20,stone,cream)
    cube('Kamakshi_Main_Temple_Roof',((x1+x2)/2,(y1+y2)/2,5.32),(x2-x1+.65,y2-y1+.65,.56),coping,.075)
    cube('Gayatri_Mandapam_Paving',(0,-.24,.145),(16.35,16.2,.29),pavement,.034)
    for x in [-6.6,-3.03,3.03,6.6]:
        for y in [-7.15,-4.25,-1.38,1.52,4.37,7.26]:
            pillar('Gayatri_Mandapam_Carved_Pillar',x,y,.28,4.75,charcoal,.42)
    for x in [-2.83,2.83]:
        cube('Kamakshi_Sanctum_Side',(x,4.12,2.61),(.56,6.05,4.72),stone,.039)
    cube('Kamakshi_Sanctum_Back',(0,7.15,2.61),(6.2,.51,4.72),stone,.039)
    framed_portal('Kamakshi_Sanctum_Door',0,1.24,6.2,2.66,.25,4.85,stone,gold)
    for px,py,w,h,mat in [(833,1105,6.8,7.4,gold),(710,968,6.1,6.7,cream),
                           (918,960,5.4,5.8,cream),(913,1241,4.95,5.2,cream)]:
        x,y=point(px,py)
        create_shikhara('Golden_Kamakshi_Vimana' if mat==gold else 'Kamakshi_Subsidiary_Vimana',
                        (x,y,5.61),w,h,4,mat,'dravidian')
    anchor('Spawn_Point',(12.35,-45.0,.065))
    anchor('Arrival_Facing',(13.65,-27.0,.065))
    anchor('Kamakshi_Darshan_Landing',(0,1.67,.30))
    anchor('Sanctum_Lamp_Position',(0,2.8,2.76))
    # Ritual apparatus has a dedicated footprint before the installed image.
    cylinder('Sri_Chakra_Peetha',(0,3.17,.43),.72,.35,stone)
    cylinder('Sri_Chakra_Peetha_Copper_Rim',(0,3.17,.61),.64,.035,gold)
    for side in [-1,1]:
        create_deepam('Gayatri_OilLamp',(side*1.62,3.66,.30),gold,wick)
        create_deepam('Gayatri_OilLamp',(side*1.92,4.95,.30),gold,wick)
    cube('Kamakshi_Murti_Adhisthana',(0,5.43,.58),(2.34,1.52,.63),charcoal,.067)
    kamakshi((0,5.34,.90))

    # Individual interior bays are arranged from left/right relationships in the
    # authority and CEC accounts. The restoration drawing labels the hall.
    bay_specs=[
        ('Varahi',-6.05,3.43,math.pi/2,.29),
        ('Arupa_Lakshmi',-6.05,.88,math.pi/2,.29),
        ('Sowbhagya_Ganapati',-2.02,-3.13,-math.pi/2,.29),
        ('Kalvar_Perumal',7.63,5.65,0,.29),
        ('Soundarya_Lakshmi',5.46,-.33,0,.29),
        ('Ardhanari',7.48,-5.03,-math.pi/2,.29),
        ('Ayyappan',-17.16,3.9,math.pi/2,.15),
        ('Saraswati',-17.16,9.5,math.pi/2,.15),
        ('Annapoorani',-17.16,15.2,math.pi/2,.15),
        ('Adi_Shankara',-10.70,17.67,0,.15),
        ('Kala_Bhairavar',-32.18,-4.23,math.pi/2,.01),
        ('Mahishasuramardini',-32.18,2.32,math.pi/2,.01),
        ('Kashi_Viswanathar',14.13,14.28,math.pi,.01)]
    for name,x,y,angle,z in bay_specs:
        approach=1.76 if name in ['Varahi','Arupa_Lakshmi'] else 2.15
        transform=shrine(name,x,y,angle,charcoal,z,approach)
        if name in ['Sowbhagya_Ganapati','Saraswati','Annapoorani','Varahi']:
            continue
        if name=='Kashi_Viswanathar':
            model=linga('Kanchi_Kashi_Viswanathar_Linga',tuple(transform@Vector((0,.08,z+.38))),.85,charcoal)
            model.rotation_euler.z=angle
        elif name=='Arupa_Lakshmi':
            # Anjana Lakshmi receives kumkum. Preserve a low sacred surface and
            # offerings while leaving the unknown anatomy unrepresented.
            for i in range(5):
                sphere('Arupa_Lakshmi_Vermilion_Offering',tuple(transform@Vector(((i-2)*.12,-.19,z+.40))),
                       (.072,.081,.023),red,16)
            sphere('Arupa_Lakshmi_Sacred_Relief_Study',tuple(transform@Vector((0,.14,z+.84))),
                   (.19,.25,.50),red,24)
        else:
            companion(name+'_Iconographic_Study',tuple(transform@Vector((0,.10,z+.38))),
                      angle,1.19 if name in ['Ayyappan','Adi_Shankara'] else 1.51,
                      name in ['Ayyappan','Adi_Shankara'],'boar' if name=='Kalvar_Perumal' else 'human')
    # A whole architectural destination for the pillared comparison views.
    for name,px,py,z,offset in [('Vasantha_Mandapam',1210,1074,1.1,4.1),
                                ('Shukrawara_Mandapam',1018,1158,1.1,4.1),
                                ('Navaratri_Mandapam',460,450,1.1,4.1)]:
        x,y=point(px,py)
        anchor(name+'_Reference',(x,y,z))
        anchor(name+'_Landing',(x,y-offset,.18))
    anchor('Sri_Chakra_Anchor',(0,3.17,.65))
    anchor('Sri_Chakra_Landing',(-.82,1.91,.30))
    orient_scene()


if __name__=='__main__':
    front_mandapa()
    if not globals().get('DEFER_GLB_EXPORT', False):
        finish('kanchipuram_kamakshi')
