"""Kamakhya's west-facing measured hall sequence and subterranean Peethas."""
import math
import random

import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene
from deity_detail import Sculpture
from present_day_sites import anchor, finish, material
from surface_detail import add_stone_detail, prepare_scene


def mesh(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.materials.append(mat)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return obj


def block(name, center, dims, mat, bevel=0):
    x, y, z = [value/2 for value in dims]
    out = mesh(name, [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
                      (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],
               [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)], mat)
    out.location = center
    if bevel:
        wear = out.modifiers.new('Worn edges', 'BEVEL')
        wear.width = bevel
        wear.segments = 2
    return out


def lathe(name, center, rings, mat, sides=16, closed=True, rotation=0):
    x,y,z = center
    verts = [(x+rx*math.cos(a),y+ry*math.sin(a),z+h) for h,rx,ry in rings
             for a in [rotation+math.tau*i/sides for i in range(sides)]]
    faces = [tuple(range(sides-1,-1,-1))] if closed else []
    for k in range(len(rings)-1):
        for i in range(sides):
            j = (i+1)%sides
            start = k*sides
            faces.append((start+i,start+j,start+sides+j,start+sides+i))
    if closed:
        faces.append(tuple(range(len(verts)-sides,len(verts))))
    return mesh(name, verts, faces, mat)


def rail(name,start,end,radius,mat):
    delta=Vector(end)-Vector(start)
    part=block(name,(Vector(start)+Vector(end))/2,(radius*2,radius*2,delta.length),mat,.012)
    part.rotation_euler=delta.to_track_quat('Z','Y').to_euler()


def point(id, target, landing):
    anchor(id+'_Anchor',target)
    anchor(id+'_Landing',landing)


def dome(name,x,y,z,radius,height,tint,m,ribs=17):
    # Sixteen facets and banded masonry are distinctive to the Nilachala crown.
    def contour(t):
        return radius*(.96+.19*t)*math.cos(t*1.48)**.77

    rings=[]
    for i in range(ribs):
        t=i/ribs
        r=contour(t)
        rings.extend([(height*t,r,r), (height*(t+.29/ribs),r+.033*radius,r+.033*radius),
                      (height*(t+.44/ribs),r+.029*radius,r+.029*radius)])
    r=contour(1)
    rings.append((height,r,r))
    lathe(name+'_Polygonal_Shikhara',(x,y,z),rings,tint,16,rotation=math.pi/16)
    lathe(name+'_Brass_Kalasha',(x,y,z+height),
          [(0,r*.99,r*.99),(.12*r,.93*r,.93*r),(.29*r,.63*r,.63*r),
           (.36*r,.79*r,.79*r),(.66*r,.87*r,.87*r),(.98*r,.44*r,.44*r),
           (1.09*r,.52*r,.52*r),(1.39*r,.29*r,.29*r),
           (1.48*r,.19*r,.19*r),(1.81*r,.055*r,.055*r)],m['gold'],16)
    if radius>3:
        rail(name+'_Flagpole',(x,y,z+height+r*1.60),(x,y,z+height+r*3.0),.024,m['gold'])
        mesh(name+'_Pennant-renderonly',[(x,y,z+height+r*2.98),(x+.74,y+.25,z+height+r*2.74),
                  (x+.045,y,z+height+r*2.33)],[(0,1,2),(0,2,1)],m['red'])


def wall(name, a, b, floor, height, thickness, mat):
    x1,y1=a
    x2,y2=b
    part=block(name,((x1+x2)/2,(y1+y2)/2,floor+height/2),
               (math.hypot(x2-x1,y2-y1)+.035,thickness,height),mat,.02)
    part.rotation_euler.z=math.atan2(y2-y1,x2-x1)
    return part


def opening_wall(name,a,b,floor,height,thickness,gap,m,surface=None,band=True,head=2.38):
    surface=surface or m['plaster']
    a,b=Vector(a),Vector(b)
    d=(b-a).normalized()
    center=(a+b)/2
    if gap:
        for p,q in [(a,center-d*gap/2),(center+d*gap/2,b)]:
            wall(name,p,q,floor,height,thickness,surface)
        wall(name+'_Head',center-d*gap/2,center+d*gap/2,floor+head,height-head,thickness,surface)
    else:
        wall(name,a,b,floor,height,thickness,surface)
    if band:
        wall(name+'_Painted_Cornice',a,b,floor+height-.13,.16,thickness+.17,m['red'])
        for p,q in ([(a,center-d*gap/2),(center+d*gap/2,b)] if gap else [(a,b)]):
            wall(name+'_Stone_Skirting',p,q,floor,.26,thickness+.10,m['stone'])


def pillar(name,x,y,floor,height,m):
    lathe(name,(x,y,floor),[(0,.45,.45),(.13,.45,.45),(.16,.38,.38),(.29,.38,.38),
         (.34,.27,.27),(height-.44,.27,.27),(height-.37,.34,.34),(height-.19,.34,.34),
         (height-.12,.46,.46),(height,.46,.46)],m['stone'],8,rotation=math.pi/8)


def paving(name,x1,x2,y1,y2,top,m,mat='paving'):
    block(name,((x1+x2)/2,(y1+y2)/2,top-.14),(x2-x1,y2-y1,.28),m[mat],.009)


def steps_x(name,start,end,y,width,low,high,m,count=14):
    """Visible individual treads over a continuous walk surface."""
    for i in range(count):
        a,b=start+(end-start)*i/count,start+(end-start)*(i+1)/count
        top=low+(high-low)*(i+(1 if high>low else 0))/count
        block(name+'_Tread-renderonly',((a+b)/2,y,top-.085),
              (abs(b-a)+.012,width,.17),m['stone'],.018)
    verts=[(start,y-width/2,low),(end,y-width/2,high),(end,y+width/2,high),
           (start,y+width/2,low),(start,y-width/2,low-.31),(end,y-width/2,high-.31),
           (end,y+width/2,high-.31),(start,y+width/2,low-.31)]
    mesh(name+'_Ascent-colonly', verts, [(0,1,2,3),(4,7,6,5),(4,5,1,0),(5,6,2,1),
                                      (6,7,3,2),(7,4,0,3)],m['stone'])


def natmandir(floor,m):
    # IITG figure 36. The apse opens toward the west. Lateral passages sit
    # between the curved west end and the narrower entrance to the next hall.
    cx=-33.3
    x0,x1=-36.75,-28.10
    half=4.02
    h=3.58
    paving('Natmandir_Stone_Floor',-40.60,x1,-half,half,floor,m)
    for sy in [-1,1]:
        opening_wall('Natmandir_Side',(x0,sy*half),(x1,sy*half),floor,h,.37,1.86,m)
        x=-37.65
        opening_wall('Natmandir_Lateral_Return',(x0,sy*half),(x,sy*2.59),floor,h,.37,1.42,m)
        for i in range(7):
            a,b=(.16+.128*i)*math.pi/2,(.16+.128*(i+1))*math.pi/2
            end=lambda t:(x-2.84*math.cos(t),sy*2.60*math.sin(t))
            opening_wall('Natmandir_Apsidal_Wall',end(a),end(b),floor,h,.38,0,m)
        pillar('Natmandir_Apsidal_Pillar',-35.39,sy*2.26,floor,h-.10,m)
    opening_wall('Natmandir_East_Door',(x1,-half),(x1,half),floor,h,.39,1.94,m)
    # Long elephant-back roof, rounded over its apse rather than a pyramid.
    rings=[]
    for i in range(23):
        x=-40.70+i*(12.94/22)
        plan_frac=math.sqrt(max(.04,1-((x+37.38)/3.34)**2)) if x<-37.38 else 1
        rings.append([(x,(4.22*plan_frac)*math.cos(a),floor+h+.04+2.94*plan_frac*math.sin(a)**.83)
                       for a in [math.pi*j/20 for j in range(21)]])
    vertices=[v for ring in rings for v in ring]
    faces=[(i*21+j,i*21+j+1,(i+1)*21+j+1,(i+1)*21+j)
           for i in range(len(rings)-1) for j in range(20)]
    mesh('Natmandir_Gajapristha_Roof',vertices,faces,m['terra'])
    mesh('Natmandir_Gajapristha_Vault',[(x,y,z-.17) for x,y,z in vertices],
         [tuple(reversed(face)) for face in faces],m['plaster'])
    mesh('Natmandir_Vault_East_Gable',rings[-1],[tuple(range(21))],m['plaster'])
    rail('Natmandir_Capped_Ridge',(cx-3.3,0,floor+h+3.0),(x1+.21,0,floor+h+3.0),.09,m['red'])
    s=Sculpture()
    s.materials.append(m['gold'])
    s.ellipsoid((-36.45,0,floor+h+3.14),(.16,.11,.19),0,16,11)
    for sy in [-1,1]:
        s.tube([(-36.46,0,floor+h+3.19),(-36.57,sy*.29,floor+h+3.32),
                (-36.62,sy*.39,floor+h+3.43)],.055,0,9)
    s.finish('Natmandir_Garuda_Roof_Finial-renderonly')


def bhogamandapa(floor,m):
    lo,hi,half=-27.90,-15.18,5.04
    h=3.48
    paving('Bhogamandapa_Floor',lo,hi,-half,half,floor,m)
    for side in [-1,1]:
        opening_wall('Pancharatna_Side',(lo,side*half),(hi,side*half),floor,h,.48,0,m)
    for x in [lo,hi]:
        opening_wall('Pancharatna_Axial_Door',(x,-half),(x,half),floor,h,.48,1.92,m)
    block('Pancharatna_Continuous_Roof',((lo+hi)/2,0,floor+h),(hi-lo+.48,2*half+.42,.30),m['stone'],.03)
    for dx in [-3.02,3.02]:
        for y in [-2.84,2.84]:
            pillar('Bhogamandapa_L_Pier',-21.45+dx,y,floor,h-.12,m)
            wall('Bhogamandapa_Return_Pier',(-21.45+dx,y),(-21.45+dx-math.copysign(.48,dx),y),
                 floor,h-.14,.32,m['stone'])
    dome('Pancharatna_Main_Dome',-21.55,0,floor+h+.19,2.57,3.18,m['terra'],m,11)
    for dx in [-4.18,4.18]:
        for side in [-1,1]:
            dome('Pancharatna_Corner_Dome',-21.55+dx,side*3.16,floor+h+.16,1.09,1.54,
                 m['terra_high'],m,7)


def chalanta(floor,m):
    lo,hi,half=-15.0,-5.75,4.85
    h=3.51
    # The western floor stops at the head of the long descent. The side strips
    # continue around the opening and leave both cardinal doors available.
    paving('Chalanta_West_Floor',lo,-9.25,-half,half,floor,m)
    paving('Chalanta_North_Floor',-9.25,hi,1.22,half,floor,m)
    paving('Chalanta_South_Floor',-9.25,hi,-half,-1.22,floor,m)
    for x in [lo,hi]:
        opening_wall('Chalanta_Axial_Door',(x,-half),(x,half),floor,h,.47,2.21,m)
    for side in [-1,1]:
        # The north bay is the darshan entrance. The other side opens to the court.
        opening_wall('Chalanta_Cardinal_Door',(lo,side*half),(hi,side*half),floor,h,.43,2.44,m)
    for x in [-14.10,-11.63,-8.96,-6.86]:
        for side in [-1,1]:
            pillar('Chalanta_Perimeter_Pillar',x,side*3.61,floor,h-.12,m)
    for x in [-13.56,-8.40]:
        for side in [-1,1]:
            pillar('Chalanta_Inner_Pillar',x,side*2.17,floor,h-.12,m)
    paving('Chalanta_North_Antechamber',-12.35,-8.55,4.85,7.55,floor,m)
    for x in [-12.35,-8.55]:
        opening_wall('Chalanta_North_Antechamber_Wall',(x,4.85),(x,7.55),floor,3.05,.36,0,m)
    block('Chalanta_North_Porch_Roof',(-10.44,6.18,floor+3.13),(4.05,3.00,.23),m['terra'],.025)
    block('Chalanta_Shell_Support',((lo+hi)/2,0,floor+h),(hi-lo+.34,2*half+.35,.30),m['stone'],.023)
    for level in [0,1]:
        span=(9.32,9.49) if level==0 else (8.6,8.75)
        z=floor+h+.15+level*.69
        rings=[(0,.53,.53),(.12,.56,.56),(.42,.48,.49),(.88,.26,.30),(1.32,.035,.10)]
        lathe('Chalanta_Two_Cottage_Roofs',(-10.38,0,z),
              [(ht,span[0]*wx,span[1]*wy) for ht,wx,wy in rings],
              m['terra_high'],4,rotation=math.pi/4)
    for side in [-1,1]:
        rail('Stair_Stone_Border',(-9.20,side*1.27,floor+.095),(-3.3,side*1.27,floor-2.35),
             .10,m['stone'])

def vimana(floor,m):
    cave=floor-2.5
    # The outer plan is pancharatha. It surrounds a separate, octagonal room below grade.
    radius=5.85
    angles=[math.pi/8+i*math.tau/8 for i in range(8)]
    corners=[(radius*math.cos(a),radius*math.sin(a)) for a in angles]
    for i,(a,b) in enumerate(zip(corners,corners[1:]+corners[:1])):
        if i==3:
            opening_wall('Cave_West_Stone_Wall',a,b,cave,3.45,.43,2.35,m,m['rock'],False,head=3.03)
            opening_wall('Vimana_Stone_West_Opening',a,b,floor,3.83,.64,2.49,m,m['stone'],False)
        else:
            wall('Cave_Octagonal_Wall',a,b,cave,3.45,.60,m['rock'])
            wall('Vimana_Jangha_Stone_Body',a,b,floor,3.83,.64,m['stone'])
        delta=Vector(b)-Vector(a)
        normal=Vector((delta.y,-delta.x)).normalized()
        mid=(Vector(a)+Vector(b))/2
        for ratha in ([-.40,.40] if i==3 else [-.33,0,.33]):
            draw=mid+normal*.62+delta*ratha
            p=block('Vimana_Pancharatha_Projection',(draw.x,draw.y,floor+1.94),
                    (1.02,1.60,3.88),m['stone'],.027)
            p.rotation_euler.z=math.atan2(normal.y,normal.x)
            for z,t in [(.42,.79),(.78,.69),(3.25,.77),(3.71,.87)]:
                part=block('Vimana_Ratha_Moulding',(draw.x,draw.y,floor+z),
                           (t+.47,1.70,.17),m['trim'],.024)
                part.rotation_euler.z=p.rotation_euler.z
        for z,mult in [(.14,.73),(.47,.56),(.92,.46),(3.18,.47),(3.48,.67),(3.72,.77)]:
            if i==3 and z<3:
                continue
            d=normal*.47
            wall('Vimana_Continuous_Stone_Course',Vector(a)+d,Vector(b)+d,floor+z,.18,
                 mult,m['trim'])
    lathe('Vimana_Central_Vault_Ceiling',(0,0,floor+1.21),
          [(-.11,5.95,5.95),(.10,5.95,5.95)],m['rock'],8,rotation=math.pi/8)
    lathe('Vimana_Stone_Platform',(0,0,floor+3.69),
          [(0,6.48,6.48),(.21,6.48,6.48),(.46,5.58,5.58)],m['trim'],16)
    dome('Kamakhya_Main_Beehive',0,0,floor+4.1,5.52,7.62,m['darkbrick'],m,23)
    for i in range(8):
        a=math.tau*i/8
        dome('Vimana_Angasikhara',5.45*math.cos(a),5.45*math.sin(a),floor+3.80,
             .72,2.10,m['darkbrick'],m,8)

    paving('Manobhava_Guha_Floor',-7.68,6.05,-5.33,5.33,cave,m,'rock')
    steps_x('Manobhava_Guha_Stone_Descent',-9.25,-3.32,0,2.42,floor,cave,m)
    for side in [-1,1]:
        wall('Descent_Channel_Rough_Stone_Wall',(-9.25,side*1.25),(-3.36,side*1.25),cave,2.51,.18,m['rock'])
    return cave


def spring_peetha(x,y,floor,m,seed,principal=False):
    rng=random.Random(seed)
    # Low natural stone, a concave spring basin and red offerings. Exact
    # contours remain unverified, so there is no figurative sacred image.
    s=Sculpture()
    s.materials.extend([m['rock'],m['water'],m['red'],m['gold']])
    scale=1 if principal else .51
    sides,rows=48,14
    vertices=[]
    for row in range(rows):
        t=row/(rows-1)
        for i in range(sides):
            a=math.tau*i/sides
            r=(.09+t*.96)*(1+.10*math.sin(a*5+.4)+.05*math.cos(a*9))
            trough=.29+.17*math.sin(t*math.pi/2)
            z=.15+trough*(1-math.exp(-t*t*9))-.34*t**8
            z+= .037*math.sin(a*3+t*6) + .012*rng.uniform(-1,1)
            vertices.append((r*math.cos(a)*1.22*scale,r*math.sin(a)*.83*scale,z*scale))
    faces=[]
    for j in range(rows-1):
        faces.extend((j*sides+i,(j+1)*sides+i,(j+1)*sides+(i+1)%sides,j*sides+(i+1)%sides)
                     for i in range(sides))
    faces.append(tuple(range(sides)))
    s.vertices.extend(vertices)
    s.faces.extend(faces)
    s.face_materials.extend([0]*len(faces))
    s.ellipsoid((0,0,.164*scale),(.40*scale,.221*scale,.041*scale),1,36,18)
    for i in range(33 if principal else 13):
        a=math.tau*i/(33 if principal else 13)
        c=2 if i%4 else 3
        s.ellipsoid((.69*scale*math.cos(a),.49*scale*math.sin(a),.471*scale),
                    (.023,.030,.018),c,8,6)
    name='Kamakhya' if principal else ('Matangi' if seed==2 else 'Kamala')
    s.finish(name+'_Sacred_Stone-renderonly',(x,y,floor))
    lathe(name+'_Stone_Approach_Block-colonly',(x,y,floor),
          [(0,.83*scale,.57*scale),(.35*scale,.83*scale,.57*scale)],m['rock'],16)
    for sy in [-1,1]:
        px,py=x-.55*scale,y+sy*.75*scale
        lathe(name+'_Brass_Offering_Lamp-renderonly',(px,py,floor),
              [(0,.11,.11),(.08,.115,.115),(.16,.06,.06),(.45,.043,.043),
               (.48,.11,.11),(.54,.14,.14)],m['gold'],16)
        lamp=Sculpture()
        lamp.materials.append(m['lamp'])
        lamp.ellipsoid((0,0,.553),(.028,.023,.083),0,13,10)
        lamp.finish(name+'_Oil_Flame-renderonly',(px,py,floor))


def carved_figure(name,position,form,m,scale=1,facing=-math.pi/2):
    # Original iconographic studies where photos do not resolve the form.
    s=Sculpture()
    s.materials.extend([m['rock'],m['trim'],m['gold'],m['red'],m['pale']])
    stone=0 if form not in ['kameshwara','kameshwari'] else 2
    s.ellipsoid((0,.025,.62),(.21,.096,.32),stone,25,14)
    s.ellipsoid((0,-.022,1.02),(.123,.103,.139),stone,25,16)
    s.ellipsoid((0,.005,1.176),(.096,.083,.122),stone,19,13)
    small_arms=form in ['ganesha','chamunda','durga','kameshwari']
    seated=form in ['ganesha','chamunda','manasa','kameshwari','kameshwara','batuk','royal']
    for side in [-1,1]:
        s.ellipsoid((side*.046,-.111,1.046),(.024,.014,.011),1,13,8)
        s.tube([(side*.158,.017,.761),(side*.265,-.033,.591),(side*.177,-.14,.54)],.049,stone,12)
        if seated:
            s.tube([(side*.08,.01,.415),(side*.24,-.041,.225),(side*.031,-.154,.146)],.082,stone,12)
        else:
            s.tube([(side*.078,.01,.43),(side*.078,.012,.176),(side*.070,-.047,.068)],.062,stone,12)
        if small_arms:
            s.tube([(side*.153,.035,.79),(side*.293,.009,.796),(side*.30,-.076,.973)],.041,stone,10)
            s.ellipsoid((side*.30,-.081,.976),(.048,.045,.055),stone,12,9)
        if form=='ganesha':
            s.ellipsoid((side*.142,-.038,1.033),(.075,.046,.093),stone,15,10)
    if form=='ganesha':
        s.tube([(0,-.117,1.022),(0,-.165,.927),(-.067,-.181,.861),(-.114,-.154,.912)],.043,stone,10)
    if form in ['shiva','durga','batuk']:
        s.tube([(.35,-.036,.12),(.35,-.036,1.24)],.016,1,8)
        for side in [-1,0,1]:
            s.tube([(.35,-.036,1.18),(.35+side*.054,-.036,1.264),(.35+side*.060,-.036,1.323)],.011,1,8)
    if form=='manasa':
        for i in range(5):
            f=(i-2)/2
            s.ellipsoid((f*.21,.12,1.23+.13*(1-f*f)),(.084,.048,.119),stone,14,9)
    if form=='chamunda':
        for i in range(6):
            z=.70+i*.039
            s.tube([(-.097,.012,z),(-.062,-.091,z+.025),(0,-.10,z),
                    (.064,-.091,z+.025),(.097,.012,z)],.012,1,8)
        s.ellipsoid((0,-.11,1.092),(.018,.010,.017),1,12,8)
    if form in ['kameshwari','kameshwara']:
        for i in range(24):
            a=math.pi+math.pi*i/23
            s.ellipsoid((.17*math.cos(a),-.112,.83+.30*math.sin(a)),
                        (.019,.017,.022),3 if i%6<3 else 4,9,6)
    ob=s.finish(name+'-renderonly',position,scale)
    ob.rotation_euler.z=facing


def front_relieves(floor,m):
    x=-28.38
    for y,id,form in [(-2.28,'Nat_Durga','durga'),(2.28,'Nat_Shiva','shiva')]:
        block(id+'_Stone_Backplate',(x+.06,y,floor+1.19),(.25,1.22,2.12),m['stone'],.032)
        block(id+'_Sculpture_Pedestal',(x-.10,y,floor+.26),(.49,1.03,.35),m['trim'],.026)
        carved_figure(id+'_Standing_Relief',(x-.17,y,floor+.42),form,m,1.15)
        point(id,(x-.24,y,floor+1.48),(x-2.15,y,floor+.055))

    for y,side in [(-5.67,'South'),(5.67,'North')]:
        x=1.61
        for i in range(4):
            px=x+i*.62-1.1
            for dx in [-.25,.25]:
                block('Vimana_Standing_Figure_Niche_Post',(px+dx,y,floor+1.93),
                      (.10,.28,1.41),m['trim'],.019)
            block('Vimana_Standing_Figure_Niche_Head',(px,y,floor+2.67),
                  (.56,.28,.15),m['trim'],.024)
            carved_figure('Vimana_Standing_Figure_Study',(px,y+math.copysign(.20,y),floor+1.27),
                          'shiva' if i==1 else 'royal',m,.84,0 if y<0 else math.pi)
        point('Vimana_'+side+'_Sculptures',(x,y+math.copysign(.24,y),floor+2.02),
              (x,y+math.copysign(2.9,y),floor+.08))


def kund(name,x,y,w,d,m,shubhagya=False):
    # The studied tanks are adjacent, stone lined and lower than the court.
    for side in [-1,1]:
        for i in range(7 if shubhagya else 4):
            level=-.115-.215*i
            width=.42 if shubhagya else .24
            px=x+side*(w/2-width*(i+.5))
            block(name+'_Steps',(px,y,level-.18),(width+.015,d-.39*i,.36),m['stone'],.018)
            py=y+side*(d/2-width*(i+.5))
            block(name+'_End_Steps',(x,py,level-.18),(w-width*(i+1)*2+.05,width+.015,.36),m['stone'],.018)
        block(name+'_Coping',(x+side*w/2,y,.16),(.25,d,.31),m['red'],.022)
        block(name+'_Coping',(x,y+side*d/2,.16),(w,.25,.31),m['red'],.022)
        for i in range(10):
            px=x+(i/9-.5)*(w-.65)
            rail(name+'_Iron_Upright',(px,y+side*d/2,.24),(px,y+side*d/2,1.0),.024,m['iron'])
        rail(name+'_Iron_Handrail',(x-w/2,y+side*d/2,.91),(x+w/2,y+side*d/2,.91),.036,m['iron'])

    bottom=-1.66 if shubhagya else -1.07
    paving(name+'_Water-renderonly',x-w/2+.13,x+w/2-.13,y-d/2+.13,y+d/2-.13,bottom,m,'water')
    paving(name+'_Low_Floor',x-w/2+.08,x+w/2-.08,y-d/2+.08,y+d/2-.08,bottom-.14,m,'stone')
    if shubhagya:
        for px in [x-1.3,x+1.3]:
            for py in [y+d/2-2.55,y+d/2-.62]:
                pillar(name+'_Small_Pavilion_Pier',px,py,-.68,2.32,m)
        block(name+'_Small_Pavilion_Eaves',(x,y+d/2-1.56,1.72),(3.0,2.34,.23),m['pale'],.028)
        dome(name+'_Pavilion_Dome',x,y+d/2-1.56,1.83,.89,1.04,m['terra'],m,7)
    point(name,(x,y-.24,bottom+.14),(x,y-d/2-2.8,.116))

def altar(id,x,y,floor,m,form,scale=.76,look='west'):
    block(id+'_Pedestal',(x,y,floor+.223),(.80,1.12,.447),m['stone'],.026)
    carved_figure(id+'_Devotional_Study',(x,y,floor+.447),form,m,scale,
                  facing=(-math.pi/2 if look=='west' else math.pi))
    point(id,(x,y,floor+1.04),(x-1.58,y,floor+.061) if look=='west' else (x,y+1.51,floor+.061))


def courtyard_bhairavi(m):
    # Figure 81 shows a pair of worn, vermilion-covered forms carved on a
    # granite face. The catalogue identifies Tripura Bhairavi in the group.
    x,y=7.60,-8.20
    block('Tripura_Bhairavi_Granite_Outcrop',(x,y,.73),(3.4,.47,1.45),m['rock'],.095)
    block('Tripura_Bhairavi_Stone_Ledge',(x,y-.23,.30),(3.59,.74,.36),m['trim'],.034)
    s=Sculpture()
    s.materials.extend([m['red'],m['gold'],m['rock']])
    for n,offset in enumerate([-.74,.66]):
        s.ellipsoid((x+offset,y-.247,.77),(.37,.095,.37),0,22,14)
        s.ellipsoid((x+offset,y-.29,1.045),(.16,.11,.22),0,21,15)
        for i in range(19):
            a=math.tau*i/19
            s.ellipsoid((x+offset+.157*math.cos(a),y-.412,
                         1.064+.214*math.sin(a)),(.034,.025,.035),1,9,7)
        for dx in [-.11,.10]:
            s.ellipsoid((x+offset+dx*.48,y-.389,1.078),(.014,.011,.011),2,10,7)
        for i in range(3):
            px=x+offset+(i-1)*.42
            z=1.47+.12*(i+n)
            s.tube([(px,y-.44,z+.24),(px+.015,y-.44,z+.076)],.014,1,8)
            s.ellipsoid((px+.016,y-.44,z),(.092,.076,.094),1,12,10)
    s.finish('Tripura_Bhairavi_Worn_Red_Relief-renderonly')
    point('Tripura_Bhairavi_Court',(x,y-.33,1.01),(x,y-1.80,.116))


def court(m):
    # Cut the elevated walking surface around the stair descent and the two
    # tanks. A foundation below the rock floor gives all routes a safe base.
    block('Ground_Nilachal_Foundation',(-10,4,-3.50),(192,173,.88),m['rock'])
    bounds=(-64,20,-22,42)
    holes=[(-9.27,6.92,-6.18,6.18),(-39.02,-24.93,23.76,34.22),
           (-48.06,-41.94,25.52,32.68)]
    xs=sorted({bounds[0],bounds[1],*(x for a,b,c,d in holes for x in [a,b])})
    ys=sorted({bounds[2],bounds[3],*(y for a,b,c,d in holes for y in [c,d])})
    for x1,x2 in zip(xs,xs[1:]):
        for y1,y2 in zip(ys,ys[1:]):
            if any(a<(x1+x2)/2<b and c<(y1+y2)/2<d for a,b,c,d in holes):
                continue
            paving('Court_Terrace_Stone_Paving',x1,x2,y1,y2,.046,m)
    for a,b in [((-64,-22),(20,-22)),((20,-22),(20,42)),
                ((20,42),(-64,42)),((-64,42),(-64,-22))]:
        wall('Nilachal_Terrace_Stone_Retaining_Base',a,b,-3.14,3.15,.46,m['stone'])
    paving('Vimana_East_Outer_Court',5.58,6.92,-6.18,6.18,.046,m)
    paving('Vimana_North_Outer_Court',-9.27,5.58,5.57,6.18,.046,m)
    paving('Vimana_South_Outer_Court',-9.27,5.58,-6.18,-5.57,.046,m)

    for a,b in [((-61,-16),(-46,-20)),((-46,-20),(-16,-22)),((-16,-22),(15,-13)),
                ((15,-13),(18,5)),((18,5),(14,17)),((14,17),(-4,25)),
                ((-4,25),(-10,32)),((-10,32),(-25,41)),((-25,41),(-49,38)),
                ((-49,38),(-61,24)),((-61,24),(-62,5)),((-62,-4),(-61,-16))]:
        wall('Hilltop_White_Retaining_Boundary',a,b,.0,1.36,.37,m['plaster'])
        wall('Hilltop_Red_Boundary_Cap',a,b,1.34,.14,.47,m['red'])

    # A covered range follows the Balighar approach. The northern axis doglegs
    # past the tanks and the visible red-roofed entry structures.
    for name,x,y,w,d,h in [
        ('West_Balighar_Range',-46.6,-3.83,9.9,7.0,3.35),
        ('South_Covered_Range',-43.3,-13.15,15.5,5.5,3.15),
        ('North_Queue_Range',-11.5,11.7,6.15,9.7,3.40),
        ('North_Compound_Range',-25.7,37.1,15.7,5.6,3.23),
        ('Upper_Approach_Pavilion',-14.15,30.4,8.1,7.1,4.7),
        ('East_Precinct_Service_Range',10.2,11.8,6.7,7.1,3.20)]:
        block(name+'_Stone_Base',(x,y,.16),(w-.22,d-.22,.32),m['stone'],.03)
        for px in [x-w*.42,x+w*.42]:
            for py in [y-d*.40,y+d*.40]:
                block(name+'_Column',(px,py,h*.51),(.26,.26,h),m['plaster'],.02)
        if name in ['Upper_Approach_Pavilion','East_Precinct_Service_Range']:
            block(name+'_Brick_Enclosure',(x,y,h*.49),(w-.31,d-.39,h*.98),m['plaster'],.034)
        rings=[(0,w*.52,d*.52),(.16,w*.54,d*.54),(.68,w*.44,d*.25),(1.06,w*.36,.07)]
        lathe(name+'_Sloped_Roof',(x,y,h),rings,m['terra'],4,rotation=math.pi/4)

    kund('Saubhagya_Kund',-31.98,28.99,14.12,10.50,m,True)
    kund('Rinmoksha_Kund',-45.00,29.1,6.12,7.16,m)
    # Passage along the raised eastern side supports pradakshina around the dome.
    p=[(8.2,-9.9),(12.8,-7.65),(14.1,-2.1),(14.5,3.8),(12.4,8.9),(8.2,11.45)]
    for a,b in zip(p,p[1:]):
        wall('Vimana_Outer_White_Circumambulatory_Parapet',a,b,.045,1.07,.36,m['plaster'])
        wall('Vimana_Outer_Red_Coping',a,b,1.09,.13,.47,m['red'])


def foliage(m):
    rng=random.Random(711)
    s=Sculpture()
    s.materials.extend([m['bark'],*m['foliage']])
    for x,y,r in [(-49,9,5.5),(-41,15,5.9),(-21,-11,5.9),(-9,-10,5.7),
                  (8,9,5.8),(4,-11,4.4),(-36,18,4.6),(-34,35,4.2),(-9,20,4.8),
                  (-59,-10,3.8),(-48,36,4.2),(-52,-19,3.8),(-2,30,4.7),(18,3,4.6)]:
        h=r*.85+4.38
        s.tube([(x,y,-.04),(x+.13,y+.19,h*.44),(x-.30,y+.23,h*.79)],.23,0,10)
        for i in range(24):
            a=rng.random()*math.tau
            d=rng.uniform(.06,r*.75)
            z=rng.uniform(h*.65,h*1.04)-d*.16
            s.ellipsoid((x+math.cos(a)*d,y+math.sin(a)*d,z),
                        (rng.uniform(1.35,2.41),rng.uniform(1.31,2.39),rng.uniform(1.05,1.68)),i%3+1,11,8)
    s.finish('Terrain_Nilachal_Courtyard_Banyan_Canopies-renderonly')

    # Low rolling context behind the terrace. The climb and village lanes are
    # outside the modeled main compound.
    rows,cols=28,26
    verts=[]
    faces=[]
    for j in range(rows):
        for i in range(cols):
            x=-110+i*6.8
            y=-73+j*6.4
            outside=max(0,-65-x,x-21,-23-y,y-43)
            z=-3.30-min(12,outside*.47)+max(0,outside/25)*math.sin(x*.082+y*.070)
            verts.append((x,y,z))
    for j in range(rows-1):
        for i in range(cols-1):
            k=j*cols+i
            faces.append((k,k+1,k+cols+1,k+cols))
    mesh('Terrain_Nilachal_Hill_Slope-renderonly',verts,faces,m['foliage'][0])


def build():
    clear_scene()
    m={
        'stone':material('Kamakhya Worn Granite',(.278,.250,.219)),
        'trim':material('Kamakhya Patinated Granite Moulding',(.369,.322,.273)),
        'paving':material('Kamakhya Worn Flag Paving',(.319,.298,.257)),
        'rock':material('Kamakhya Dark Natural Stone',(.096,.092,.078),.75),
        'darkbrick':material('Kamakhya Patinated Brick Shikhara',(.174,.156,.129),.82),
        'plaster':material('Kamakhya Limewashed Walls',(.61,.56,.46)),
        'pale':material('Kamakhya Warm White Pavilion',(.70,.64,.54)),
        'terra':material('Kamakhya Aged Terracotta Roof',(.31,.080,.058),.69),
        'terra_high':material('Kamakhya Pancharatna Ochre Terracotta',(.43,.119,.072)),
        'red':material('Kamakhya Vermilion Offering and Trim',(.39,.044,.049),.73),
        'iron':material('Kamakhya Worn Iron Rail',(.073,.092,.098),.65,.32),
        'gold':material('Kamakhya Tarnished Brass',(.77,.49,.16),.32,.55),
        'water':material('Kamakhya Still Spring Water',(.023,.055,.031),.28,.23),
        'lamp':material('Kamakhya Lamp Flame',(1.0,.51,.163),.35,0,2.4),
        'bark':material('Kamakhya Nilachal Tree Bark',(.115,.081,.052)),
        'foliage':[material('Kamakhya Nilachal Leaf '+str(i),c) for i,c in enumerate(
            [(.073,.16,.073),(.098,.205,.098),(.133,.255,.109)])]
    }
    for key in ['stone','trim','paving','rock','darkbrick']:
        mat=m[key]
        shader=mat.node_tree.nodes.get('Principled BSDF')
        add_stone_detail(mat,shader,tuple(shader.inputs['Base Color'].default_value))
    floor=.248
    court(m)
    natmandir(floor,m)
    bhogamandapa(floor,m)
    chalanta(floor,m)
    cave=vimana(floor,m)

    # Preserve separate roof and walls over the connecting antarala. It
    # straddles the deeper approach, with the cavity open beneath it.
    for side in [-1,1]:
        wall('Antarala_Red_Stone_Return',(-6.08,side*1.43),(-4.75,side*1.43),floor,2.71,.21,m['stone'])
    block('Antarala_Lintel',(-5.69,0,2.89),(1.53,3.41,.29),m['stone'],.025)
    lathe('Antarala_Joined_Low_Roof',(-5.79,0,3.03),
          [(0,1.10,2.08),(.18,1.12,2.15),(.52,.79,1.52),(.68,.34,.57)],m['terra'],4,rotation=math.pi/4)
    paving('Western_Entrance_Threshold',-41.03,-39.93,-1.07,1.07,.149,m)

    # All three Peethas share the octagonal Manobhava Guha. The two
    # subsidiary stones sit toward its east side, with a shared circulation lane.
    for x,y,seed,principal in [(1.02,-.12,5,True),(3.55,1.73,2,False),(3.55,-1.81,3,False)]:
        spring_peetha(x,y,cave,m,seed,principal)
    anchor('Deity_Kamakhya',(1.02,-.12,cave+.38))
    anchor('Kamakhya_Darshan_Landing',(-.89,-.12,cave+.065))
    anchor('Sanctum_Lamp_Position',(.28,.22,cave+2.12))
    point('Matangi_Peetha',(3.55,1.73,cave+.23),(2.78,3.38,cave+.065))
    point('Kamala_Peetha',(3.55,-1.81,cave+.23),(2.78,-3.44,cave+.065))

    altar('Entrance_Ganesh',-43.36,3.29,.046,m,'ganesha',.88)
    block('Chalanta_Simhasana',(-12.95,-2.71,floor+.28),(1.17,2.24,.56),m['stone'],.036)
    for name,y,form in [('Kameshwari',-2.10,'kameshwari'),('Kameshwara',-3.22,'kameshwara')]:
        carved_figure(name+'_Processional_Study',(-13.05,y,floor+.57),form,m,.79,math.pi)
        point(name,(-13.04,y,floor+1.21),(-11.68,y+.21,floor+.058))
    altar('Batuk_Bhairava',-12.33,2.45,floor,m,'batuk')
    altar('Pancharatna_Manasa',-21.68,-2.45,floor,m,'manasa',.72)
    altar('Pancharatna_Chamunda',-21.68,2.30,floor,m,'chamunda',.81)
    front_relieves(floor,m)
    courtyard_bhairavi(m)
    for sy in [-1,1]:
        x=-2.90
        y=sy*7.24
        block('Chamunda_Exterior_Granite_Slab',(x,y,.87),(1.39,.29,1.63),m['stone'],.035)
        carved_figure('Chamunda_Courtyard_Relief',(x,y+sy*.18,.20),'chamunda',m,.93,
                      math.pi if sy>0 else 0)
        point('Chamunda_Courtyard_North' if sy==1 else 'Chamunda_Courtyard_South',
              (x,y+sy*.22,1.02),(x,y+sy*1.86,.121))
    # The locations and summaries identify the recorded inscriptions.
    # Cut and worn surfaces are modeled without fabricated letter forms.
    block('Koch_Reconstruction_Tablet',(-10.92,-4.53,1.77),(1.24,.15,.76),m['rock'],.024)
    point('Koch_Reconstruction',(-10.92,-4.44,1.77),(-10.92,-2.98,floor+.06))
    block('Natmandir_Ahom_Dedication_Tablet',(-30.0,3.79,1.51),(1.18,.14,.73),m['rock'],.021)
    point('Ahom_Dedication',(-30.0,3.72,1.51),(-30.0,2.16,floor+.06))

    foliage(m)
    anchor('Spawn_Point',(-53.1,.01,.126))
    anchor('Arrival_Facing',(-39.1,.01,.126))
    rot=Matrix.Rotation(math.radians(-6.3),4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world=rot@obj.matrix_world


if __name__=='__main__':
    build()
    if not globals().get('DEFER_GLB_EXPORT',False):
        prepare_scene()
        finish('kamakhya')
