"""Madurai twin sanctuaries and enclosure traced from archival plans and aerials.

Local X follows the east-facing sanctum axes. Local Y points toward the
northern side of the enclosure. The assembled site is rotated to match aerials.
"""
import math
import random

import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene, create_nandi
from common_materials import create_granite_stone
from deity_detail import Sculpture, crown_band, garland, palette
from present_day_sites import anchor, box, finish, linga, material

WEST, EAST, SOUTH, NORTH = -129.0,129.0,-119.0,119.0
DEVI_Y, SWAMI_Y = -43.0,22.0
TANK = (-20.0,37.0,-91.0,-47.0)


class Blocks:
    """Batch repeated masonry so a full pillared court stays interactive."""

    def __init__(self):
        self.vertices = []
        self.faces = []

    def add(self, center, size):
        x,y,z = center
        a,b,c = (component/2 for component in size)
        index = len(self.vertices)
        self.vertices.extend([
            (x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
            (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c),
        ])
        self.faces.extend(tuple(index+i for i in face) for face in [
            (0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),
        ])

    def finish(self, name, surface):
        return mesh(name,self.vertices,self.faces,surface)


def mesh(name, vertices, faces, surface):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices,[],faces)
    data.update()
    obj = bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(surface)
    return obj


def surface(name, x0, x1, y0, y1, z, mat):
    return mesh(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[(0,1,2,3)],mat)


def rotate_new(before, x, y, angle):
    if not angle:
        return
    pivot = Matrix.Translation((x,y,0))
    turn = pivot @ Matrix.Rotation(angle,4,'Z') @ pivot.inverted()
    bpy.context.view_layer.update()
    for obj in set(bpy.context.scene.objects)-before:
        if obj.parent is None:
            obj.matrix_world = turn @ obj.matrix_world


def floor_without(bounds, cut, height, m):
    x0,x1,y0,y1 = bounds
    a,b,c,d = cut
    for index,rect in enumerate([(x0,a,y0,y1),(b,x1,y0,y1),(a,b,y0,c),(a,b,d,y1)]):
        surface(f'Ground_Temple_Paving_{index}',*rect,height,m['paving'])


def wall(name, x0, x1, y0, y1, opening, width, m, height=4.8, thickness=1.04):
    """Build axis-aligned enclosure courses with independent gate positions."""
    horizontal = abs(y1-y0)<.001
    a,b = (x0,x1) if horizontal else (y0,y1)
    masonry = Blocks()
    trim = Blocks()
    spans = [(a,b)] if opening is None else [(a,opening-width/2),(opening+width/2,b)]
    for start,end in spans:
        if end-start<.04:
            continue
        length = end-start
        t = (start+end)/2
        masonry.add((t,y0,height/2) if horizontal else (x0,t,height/2),
                    (length,thickness,height) if horizontal else (thickness,length,height))
        trim.add((t,y0,.28) if horizontal else (x0,t,.28),
                 (length,thickness+.38,.56) if horizontal else (thickness+.38,length,.56))
        trim.add((t,y0,height+.12) if horizontal else (x0,t,height+.12),
                 (length,thickness+.32,.24) if horizontal else (thickness+.32,length,.24))
    masonry.finish(name,m['granite'])
    trim.finish(name+'_Coped_Moulding',m['edge'])


def shrine_gate(name, x, y, breadth, depth, total, tiers, yaw, m, opening=4.1):
    """Individual talas, miniature aedicules, painted stucco and barrel crest."""
    before = set(bpy.context.scene.objects)
    gate_height = min(total*.34,7.6)
    jamb = (breadth-opening)/2
    for sign in (-1,1):
        cx=x+sign*(opening+jamb)/2
        box(name+'_Granite_Jamb',(cx,y,gate_height/2),(jamb,depth,gate_height),m['granite'],.075)
        box(name+'_Base_Moulding',(cx,y,.52),(jamb+.18,depth+.35,1.04),m['edge'],.06)
        for k in range(1,5):
            px=x+sign*(opening/2+jamb*k/5)
            for py in (y-depth/2-.045,y+depth/2+.045):
                box(name+'_Granite_Facade_Pilaster',(px,py,gate_height*.53),
                    (.37,.28,gate_height*.79),m['edge'],.025)
    box(name+'_Through_Passage_Lintel',(x,y,gate_height+.39),(breadth,depth,.78),m['granite'],.079)
    cornices = Blocks()
    central = Blocks()
    niches = Blocks()
    relief = Sculpture()
    relief.materials.extend(m['stucco'])
    base = gate_height+.77
    crest = min(total*.09,4.5)
    tier_h = (total-base-crest)/tiers
    for row in range(tiers):
        ratio = row/tiers
        w = breadth*(.41+.59*(1-ratio)**1.44)
        d = depth*(.48+.52*(1-ratio)**1.29)
        z = base+row*tier_h
        central.add((x,y,z+tier_h*.47),(w,d,tier_h*.94))
        cornices.add((x,y,z+tier_h*.87),(w+.46,d+.37,tier_h*.20))
        cornices.add((x,y,z+tier_h*.12),(w+.25,d+.24,tier_h*.14))
        count = max(5,round(w/max(tier_h*.58,.74)))
        for i in range(count):
            px=x+(i-(count-1)/2)*w*.934/count
            for sign in (-1,1):
                py=y+sign*(d/2+.09)
                niches.add((px,py,z+tier_h*.47),(w/count*.60,.31,tier_h*.64))
                draw_stucco(relief,px,py+sign*.27,z+tier_h*.23,tier_h*.47,
                            (i+row*2+(sign==1))%len(m['stucco']))
        for sign in (-1,1):
            for k in (-1,0,1):
                draw_stucco(relief,x+sign*(w/2+.17),y+k*d*.30,z+tier_h*.23,
                            tier_h*.42,(row+k+3)%len(m['stucco']))
    central.finish(name+'_Tala_Walls',m['warm_rose'])
    cornices.finish(name+'_Painted_Cornices',m['stucco'][1])
    niches.finish(name+'_Shrine_Aedicules',m['stucco'][4])
    relief.finish(name+'_Stucco_Figure_Studies-renderonly')
    last=base+tiers*tier_h
    span = breadth*.51
    barrel_roof(name+'_Shala_Crown',x,y,last,span,depth*.51,crest*.69,m['stucco'][0])
    for i in range(9 if tiers==9 else 5):
        n=9 if tiers==9 else 5
        kx=x+span*.42*(2*i/(n-1)-1)
        urn(name+'_Kalasha',(kx,y,last+crest*.67),crest*.29,crest*.10,m['gilt'])
    rotate_new(before,x,y,yaw)


def draw_stucco(s,x,y,z,h,color):
    s.ellipsoid((x,y,z+h*.48),(h*.20,h*.10,h*.28),color,7,5)
    s.ellipsoid((x,y,z+h*.78),(h*.108,h*.089,h*.113),color,7,5)
    s.ellipsoid((x,y,z+h*.91),(h*.126,h*.09,h*.074),(color+2)%len(s.materials),7,4)
    s.ellipsoid((x,y,z+h*.22),(h*.24,h*.105,h*.088),(color+1)%len(s.materials),7,5)


def barrel_roof(name,x,y,z,width,depth,height,mat):
    vertices=[]
    for px in (x-width/2,x+width/2):
        for i in range(25):
            angle=math.pi*i/24
            vertices.append((px,y+depth*.5*math.cos(angle),z+height*math.sin(angle)))
    faces=[(i,i+25,i+26,i+1) for i in range(24)]
    faces.extend([tuple(range(25)),tuple(range(49,24,-1))])
    mesh(name,vertices,faces,mat)


def urn(name,center,height,radius,mat):
    x,y,z=center
    vertices=[]
    profile=[(0,.58),(.14,.82),(.27,.57),(.48,1),(.67,.71),(.76,.32),(.87,.63),(1,.06)]
    n=16
    for h,r in profile:
        for i in range(n):
            theta=math.tau*i/n
            vertices.append((x+radius*r*math.cos(theta),y+radius*r*math.sin(theta),z+h*height))
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)
           for j in range(len(profile)-1) for i in range(n)]
    obj=mesh(name,vertices,faces,mat)
    for poly in obj.data.polygons:
        poly.use_smooth=True


def mandapa(name,bounds,rows,columns,m,height=5.3,aisle='x',floor=.15,solid_roof=True,cross_y=None):
    x0,x1,y0,y1=bounds
    width,depth=x1-x0,y1-y0
    center_x,center_y=(x0+x1)/2,(y0+y1)/2
    box(name+'_Platform',(center_x,center_y,floor/2),(width,depth,floor),m['granite'],.018)
    shafts,trim=Blocks(),Blocks()
    for i in range(columns):
        x=x0+.90+(width-1.80)*i/max(1,columns-1)
        for j in range(rows):
            y=y0+.86+(depth-1.72)*j/max(1,rows-1)
            if (aisle=='x' and abs(y-center_y)<1.86) or (aisle=='y' and abs(x-center_x)<1.86):
                continue
            if cross_y is not None and abs(y-cross_y)<1.72:
                continue
            shafts.add((x,y,floor+height/2),(.53,.55,height))
            trim.add((x,y,floor+.22),(.86,.86,.44))
            trim.add((x,y,floor+height-.35),(1.27,.89,.35))
            trim.add((x,y,floor+height-.12),(1.43,1.01,.24))
    shafts.finish(name+'_Granite_Piers',m['granite'])
    trim.finish(name+'_Pier_Plinths_And_Brackets',m['edge'])
    if solid_roof:
        box(name+'_Mandapa_Roof',(center_x,center_y,floor+height+.17),
            (width,depth,.34),m['roof'],.033)
        box(name+'_Eaves',(center_x,center_y,floor+height-.015),
            (width+.36,depth+.28,.20),m['edge'],.036)
    return center_x,center_y


def tank(m):
    x0,x1,y0,y1=TANK
    stone=Blocks()
    for tier in range(17):
        offset=tier*.365
        low=(tier+1)*.146
        a,b,c,d=x0+offset,x1-offset,y0+offset,y1-offset
        stone.add(((a+b)/2,c+.183,-low-.18),(b-a,.38,.36))
        stone.add(((a+b)/2,d-.183,-low-.18),(b-a,.38,.36))
        stone.add((a+.183,(c+d)/2,-low-.18),(.38,d-c-.70,.36))
        stone.add((b-.183,(c+d)/2,-low-.18),(.38,d-c-.70,.36))
    stone.finish('Potramarai_Kulam_Stone_Steps',m['edge'])
    surface('Tank_Stone_Basin',x0+6,x1-6,y0+6,y1-6,-2.67,m['granite'])
    surface('Potramarai_Kulam_Water-renderonly',x0+6,x1-6,y0+6,y1-6,-2.36,m['water'])
    for name,bounds,rows,columns,axis in [
        ('Tank_North_Colonnade',(x0-6,x1+6,y1,y1+7),2,14,'x'),
        ('Tank_South_Colonnade',(x0-6,x1+6,y0-6,y0),2,14,'x'),
        ('Tank_East_Colonnade',(x1,x1+6,y0,y1),10,2,'y'),
        ('Tank_West_Colonnade',(x0-6,x0,y0,y1),10,2,'y'),
    ]:
        mandapa(name,bounds,rows,columns,m,3.9,axis)
    petals=Sculpture()
    petals.materials.append(m['gilt'])
    cx,cy=(x0+x1)/2,(y0+y1)/2
    for i in range(16):
        angle=math.tau*i/16
        petals.ellipsoid((cx+.57*math.cos(angle),cy+.57*math.sin(angle),-1.9),
                         (.42,.36,.29),0,10,6)
    petals.ellipsoid((cx,cy,-1.85),(.48,.48,.26),0)
    petals.finish('Golden_Lotus_Water_Study-renderonly')
    landmark('golden_lily',(cx,y1-.25,1.15),(cx,y1+2.45,.18))
    # Preserve a marker for the documented murals without speculative text.
    box('Tank_North_Mural_Frieze_Panel',(12,y1+5.66,2.47),(11.3,.17,1.45),m['redwash'],.022)
    landmark('tank_murals',(12,y1+5.51,2.19),(12,y1+2.43,.18))


def landmark(id, target, landing):
    anchor('Madurai_'+id,target)
    anchor('Landing_'+id,landing)

def east_cell(name,x,y,side,m,floor=.27,height=4.75):
    a,b=x-side/2,x+side/2
    c,d=y-side/2,y+side/2
    box(name+'_Plinth',(x,y,floor/2),(side+.32,side+.32,floor),m['edge'],.045)
    wall(name+'_South',a,b,c,c,None,0,m,height)
    wall(name+'_North',a,b,d,d,None,0,m,height)
    wall(name+'_West',a,a,c,d,None,0,m,height)
    wall(name+'_East_Threshold',b,b,c,d,y,2.48,m,height)
    box(name+'_Lintel',(b,y,3.07),(1.16,3.02,.39),m['edge'],.04)
    box(name+'_Roof',(x,y,height+.22),(side+.60,side+.60,.46),m['roof'],.055)


def vimana(name,x,y,span,m):
    for row in range(4):
        w=span*(1-.18*row)
        z=5.04+row*.85
        box(name+'_Gilt_Storey',(x,y,z+.37),(w,w,.74),m['gilt'],.055)
        box(name+'_Projecting_Course',(x,y,z+.73),(w+.40,w+.40,.22),m['edge_gold'],.045)
    urn(name+'_Golden_Crown',(x,y,8.47),1.95,1.56,m['gilt'])
    urn(name+'_Golden_Kalasha',(x,y,10.37),.87,.26,m['edge_gold'])


def meenakshi(x,y,z):
    s=Sculpture()
    p=palette(s)
    red=s.material('Meenakshi_Pleated_Silk',(.355,.025,.07),0,.63)
    cobalt=s.material('Meenakshi_Lotus',(.15,.27,.58),0,.53)
    s.ellipsoid((0,0,.08),(.61,.39,.10),p['gold'])
    for j in range(28):
        ang=math.tau*j/28
        s.ellipsoid((.54*math.cos(ang),.34*math.sin(ang),.15),(.13,.09,.045),p['gold'],12,6)
    for sign in (-1,1):
        s.ellipsoid((sign*.119,-.052,.237),(.105,.102,.07),p['green'])
    s.ellipsoid((.023,0,.61),(.259,.157,.386),red)
    s.ellipsoid((-.012,.012,.98),(.233,.148,.283),p['green'])
    s.ellipsoid((-.012,-.053,1.01),(.214,.106,.208),red)
    for index in range(8):
        d=(index-3.5)*.037
        s.tube([(-.191+d*.43,-.104,1.187),(-.11+d,-.166,1.055),
                (-.018+d*.89,-.163,.956),(.103+d*.61,-.140,.857)],.015,
               p['gold'] if index in (0,7) else red,8)
    for j in range(12):
        dx=(j-5.5)*.032
        s.tube([(dx,-.135,.30),(dx*.82,-.17,.62),(dx*.62,-.166,.86)],.013,
               p['gold'] if j in (1,10) else red,8)
    s.tube([(-.24,-.102,.834),(-.12,-.168,.81),(.10,-.165,.811),(.26,-.09,.854)],.032,p['gold'],12)
    s.ellipsoid((0,0,1.245),(.092,.070,.117),p['green'])
    s.ellipsoid((0,0,1.384),(.150,.124,.178),p['green'],34,21,
                lambda v: v if v.y>-.09 else Vector((v.x,v.y-.024*math.exp(-(v.x/.044)**2),v.z)))
    s.ellipsoid((0,.047,1.48),(.161,.117,.11),p['black'],24,14)
    for sign in (-1,1):
        s.ellipsoid((sign*.062,-.120,1.407),(.037,.010,.014),p['eye'],14,8)
        s.ellipsoid((sign*.061,-.130,1.407),(.010,.006,.011),p['black'],12,8)
        s.tube([(sign*.030,-.122,1.443),(sign*.071,-.120,1.449),(sign*.103,-.109,1.436)],.009,p['black'])
        s.rosette((sign*.156,-.052,1.35),.046,p['gold'],p['red'],8)
    s.tube([(-.042,-.12,1.337),(0,-.142,1.342),(.043,-.12,1.337)],.011,p['red'])
    s.rosette((0,-.127,1.476),.025,p['red'],p['gold'])
    for j in range(6):
        s.ellipsoid((0,.028,1.515+j*.059),(.176-j*.020,.114-j*.013,.064),p['gold'],25,12)
    crown_band(s,p,.139,1.518,-.108,tiers=3)
    # Meenakshi's right hand presents the lotus and its companion parrot.
    s.tube([(-.197,0,1.176),(-.329,-.017,.987),(-.367,-.106,1.188),
            (-.386,-.148,1.276)],.059,p['green'],14)
    s.tube([(.193,.015,1.158),(.268,-.004,.924),(.242,-.046,.705),
            (.244,-.086,.641)],.056,p['green'],14)
    s.tube([(-.387,-.148,1.247),(-.433,-.164,1.51)],.011,p['green'],9)
    s.rosette((-.434,-.163,1.517),.085,cobalt,p['yellow'],9)
    s.ellipsoid((-.443,-.117,1.59),(.051,.053,.081),p['green'],20,11)
    s.ellipsoid((-.471,-.125,1.646),(.041,.037,.042),p['green'])
    s.ellipsoid((-.506,-.146,1.632),(.025,.022,.018),p['red'],13,7)
    s.tube([(-.416,-.091,1.567),(-.362,-.058,1.46)],.025,p['green'],8)
    garland(s,p,.268,1.166,.41,-.183,46)
    for row in range(3):
        width=.12+row*.034
        necklace=[(width*math.cos(math.pi+i*math.pi/32),-.185,
                   1.225-.023*row+(.048+.023*row)*math.sin(math.pi+i*math.pi/32))
                  for i in range(33)]
        s.tube(necklace,.010,p['gold'],9)
        s.rosette((0,-.204,1.177-row*.047),.030,p['gold'],p['red'],7)
    halo=[(.66*math.cos(math.pi*i/80),.233,.34+1.47*math.sin(math.pi*i/80)) for i in range(81)]
    s.tube(halo,.047,p['gold'],13)
    for i in range(29):
        a=math.pi*i/28
        s.rosette((.71*math.cos(a),.22,.34+1.53*math.sin(a)),.040,p['gold'],p['red'],7)
    model=s.finish('Deity_Meenakshi',(x,y,z),1.34)
    model.rotation_euler.z=math.pi/2
    model['has_authored_ornaments']=True


def vinayagar(x,y,z):
    s=Sculpture()
    p=palette(s)
    k=p['black']
    s.ellipsoid((0,0,.105),(.87,.59,.13),k)
    s.ellipsoid((0,0,.67),(.52,.35,.49),k)
    for side in (-1,1):
        s.ellipsoid((side*.39,-.026,.33),(.38,.27,.19),k)
        s.ellipsoid((side*.36,.02,1.082),(.23,.11,.31),k)
        s.tube([(side*.29,0,.97),(side*.53,-.09,.75),(side*.47,-.272,.53)],.101,k,15)
        s.tube([(side*.24,.07,1.03),(side*.47,.028,1.19),(side*.52,-.04,1.31)],.076,k,12)
    s.ellipsoid((0,-.054,1.15),(.32,.24,.34),k)
    s.ellipsoid((0,.041,1.415),(.214,.182,.15),p['gold'])
    s.tube([(0,-.208,1.18),(.04,-.33,1.00),(.05,-.374,.80),(.22,-.379,.62),
            (.39,-.337,.70)],.122,k,14)
    s.tube([(-.125,-.27,1.07),(-.253,-.34,.98)],.038,p['white'],12)
    s.rosette((0,-.298,1.315),.047,p['red'],p['yellow'])
    garland(s,p,.40,1.084,.36,-.29,40)
    model=s.finish('Mukkuruni_Vinayagar_Sculpture',(x,y,z),1.72)
    model.rotation_euler.z=math.pi/2


def silver_sabha(x,y,z):
    s=Sculpture()
    p=palette(s)
    body=p['silver']
    s.ellipsoid((0,0,.11),(.67,.37,.13),p['black'])
    s.ellipsoid((0,0,1.16),(.211,.138,.281),body)
    s.ellipsoid((.01,.013,1.52),(.134,.112,.15),body)
    s.ellipsoid((0,.055,1.685),(.208,.122,.15),body)
    s.tube([(.055,.010,1.02),(.18,-.038,.55),(.17,-.077,.27)],.078,body,13)
    # The Madurai dance image raises the right leg.
    s.tube([(-.05,-.016,1.025),(-.35,-.090,1.03),(-.49,-.16,1.27),(-.55,-.16,1.48)],
           .072,body,13)
    for arm in [
        [(-.17,.015,1.36),(-.40,.07,1.43),(-.54,-.01,1.54)],
        [(.17,.009,1.36),(.43,.07,1.44),(.55,-.03,1.56)],
        [(-.17,-.04,1.26),(-.32,-.14,1.18),(-.37,-.17,1.36)],
        [(.16,-.035,1.27),(.10,-.18,1.17),(-.21,-.20,1.07)],
    ]:
        s.tube(arm,.056,body,10)
        s.ellipsoid(arm[-1],(.062,.042,.075),body,13,8)
    loop=[(.88*math.cos(i*math.tau/100),.12,1.04+.93*math.sin(i*math.tau/100))
          for i in range(101)]
    s.tube(loop,.043,body,12)
    for i in range(26):
        a=math.tau*i/26
        s.rosette((.94*math.cos(a),.11,1.04+.985*math.sin(a)),.048,p['gold'],p['red'])
    model=s.finish('Velli_Ambalam_Right_Leg_Nataraja',(x,y,z),1.19)
    model.rotation_euler.z=math.pi/2


def small_linga(id,x,y,m,size=.82):
    east_cell('Shrine_'+id,x,y,4.6,m,height=3.18)
    obj=linga('Linga_'+id,(x-.42,y,.30),size,m['basalt'])
    obj.rotation_euler.z=math.pi/2
    landmark(id,(x-.42,y,.83),(x+3.96,y,.17))


def sculpture_study(id,x,y,surface_mat,m,count=1,landing=None):
    s=Sculpture()
    s.materials.append(surface_mat)
    for k in range(count):
        dy=(k-(count-1)/2)*.66
        s.ellipsoid((x,y+dy,.27),(.32,.31,.16),0,10,7)
        s.ellipsoid((x,y+dy,.73),(.128,.216,.38),0,14,10)
        s.ellipsoid((x,y+dy,1.20),(.105,.117,.135),0,14,10)
        s.ellipsoid((x,y+dy,1.35),(.095,.13,.102),0,14,9)
        for sign in (-1,1):
            s.tube([(x,y+dy+sign*.13,1.0),(x+.07,y+dy+sign*.24,.84),
                    (x+.20,y+dy+sign*.17,.67)],.055,0,9)
    s.finish(id+'_Iconographic_Study-renderonly')
    landmark(id,(x+.16,y,.96),landing or (x+2.52,y,.15))


def inner_courts(m):
    # Meenakshi's south enclosure and Sundareshwarar's larger north
    # enclosure have separate east-facing ritual axes.
    for x in [-102,-91]:
        wall('Amman_West_Prakaras',x,x,-90,-14,DEVI_Y,4.1,m)
    wall('Amman_Outer_South',-102,-31,-90,-90,None,0,m)
    wall('Amman_Outer_East',-31,-31,-90,-14,DEVI_Y,5.0,m)
    wall('Shared_Amman_Swami_Wall',-102,38,-14,-14,-24,5.4,m)
    for y in [-61,-26]:
        wall('Amman_Inner_Prakaras',-91,-46,y,y,None,0,m)
    wall('Amman_Inner_East_Wall',-46,-46,-61,-26,DEVI_Y,4.0,m)
    mandapa('Amman_East_Inner_Mandapa',(-69,-47,-53,-33),4,5,m,4.5)
    mandapa('Amman_North_Prakaras',(-88,-48,-26,-17),2,10,m,4.2)
    mandapa('Amman_South_Prakaras',(-91,-50,-81,-68),3,10,m,4.1)
    east_cell('Meenakshi_Garbhagriha',-70,DEVI_Y,9.9,m)
    vimana('Meenakshi_Golden_Vimana',-70,DEVI_Y,7.05,m)
    meenakshi(-71.0,DEVI_Y,.30)
    landmark('main',(-70.77,DEVI_Y,1.67),(-66.70,DEVI_Y,.29))
    anchor('Sanctum_Lamp_Position',(-68.31,DEVI_Y-.71,2.2))
    worship_portal('Meenakshi_Sanctum_Portal',-65.05,DEVI_Y,m)
    mandapa('Amman_West_Roofed_Corridor',(-90.1,-82.6,-58.8,-29.5),8,2,m,4.2,'y',cross_y=DEVI_Y)
    small_linga('sevvanthiswarar',-82.5,-34.4,m)
    small_linga('kasi_viswanathar',-82.5,-55.4,m)
    for x,y,j in [(-97,DEVI_Y,5),(-46,DEVI_Y,3)]:
        name='Kadaka_Gopuram' if j==5 else 'Amman_Sannidhi_Gopuram'
        shrine_gate(name,x,y,9.3,5.0,15.0 if j==5 else 9.1,j,math.pi/2,m,
                    4.1 if j==5 else 4.0)

    wall('Swami_North_Outer',-95,37,83,83,-24,5.0,m)
    wall('Swami_West_Outer',-95,-95,-14,83,SWAMI_Y,4.6,m)
    wall('Swami_East_Outer',37,37,-14,83,SWAMI_Y,5.4,m)
    wall('Swami_Inner_West',-74,-74,-3,51,None,0,m)
    wall('Swami_Inner_North',-74,2,51,51,None,0,m)
    wall('Swami_Inner_South',-74,2,-3,-3,None,0,m)
    wall('Swami_Inner_East',2,2,-3,51,SWAMI_Y,4.65,m)
    mandapa('Swami_Inner_North_Gallery',(-73,-1,43,50),2,16,m,4.3)
    mandapa('Swami_Inner_South_Gallery',(-73,-1,-2,6),2,16,m,4.3)
    mandapa('Swami_Ardha_And_Maha_Mandapa',(-49,1,8,37),6,12,m,5.5)
    east_cell('Sundareswarar_Garbhagriha',-57,SWAMI_Y,12.5,m)
    vimana('Sundareswarar_Golden_Vimana',-57,SWAMI_Y,8.62,m)
    ling=linga('Sundareswarar_Linga',(-57.65,SWAMI_Y,.29),1.78,m['basalt'])
    ling.rotation_euler.z=math.pi/2
    landmark('sundareswarar',(-57.31,SWAMI_Y,1.43),(-52.53,SWAMI_Y,.29))
    worship_portal('Swami_Sanctum_Portal',-50.75,SWAMI_Y,m)
    mandapa('Swami_Inner_West_Colonnade',(-73.4,-68.0,5.6,42.1),10,2,m,4.3,'y')
    for name,x,y,s,w,d,h,t,yaw in [
        ('Gopura_Nayaka',37,SWAMI_Y,5.4,13,7,20,5,math.pi/2),
        ('Palakai_Gopuram',-95,SWAMI_Y,4.6,11,6,16,5,math.pi/2),
        ('Chinnamottai_Gopuram',-24,83,5,11,6,13.5,5,0),
        ('Nadukattu_Gopuram',-24,-14,5.4,12,6.4,17,5,0),
        ('Swami_Sannidhi_Gopuram',2,SWAMI_Y,4.65,10,5.0,11,3,math.pi/2),
    ]:
        shrine_gate(name,x,y,w,d,h,t,yaw,m,s)
    landmark('nadukattu',(-24,-14,1.66),(-24,-20.1,.16))
    mandapa('Kambathadi_Mandapam',(4.8,32,-0.1,44),9,5,m,5.45)
    landmark('kambathadi',(14,29.62,1.36),(20.9,29.8,.17))
    nandi=create_nandi('Kambathadi_Nandi',(16.75,SWAMI_Y,.31),2.54,mat=m['basalt'])
    nandi.rotation_euler.z=math.pi/2
    box('Kambathadi_Nandi_Platform',(16.75,SWAMI_Y,.23),(3.05,2.19,.46),m['edge'],.048)
    landmark('nandi',(16.75,SWAMI_Y,1.45),(21.0,SWAMI_Y,.17))
    urn('Kambathadi_Gold_Dhvajastambha',(26,SWAMI_Y,.28),7.7,.49,m['gilt'])
    landmark('flagstaff',(26,SWAMI_Y,2.45),(28.85,SWAMI_Y,.17))
    # Right-leg Nataraja occupies the silver hall beside the Swami axis.
    east_cell('Velli_Ambalam',-18.8,11.2,6.4,m,height=4.25)
    silver_sabha(-19.84,11.2,.30)
    landmark('nataraja',(-19.51,11.2,1.51),(-13.6,11.2,.16))
    east_cell('Mukkuruni_Vinayagar_Shra',-32,-8.5,5.5,m,height=4.33)
    vinayagar(-32.7,-8.5,.30)
    landmark('mukkuruni_vinayagar',(-32.34,-8.5,1.44),(-27.35,-8.5,.16))
    east_cell('Murugan_Second_Prakaras',-63.5,65.5,5.8,m,height=3.57)
    sculpture_study('murugan',-64.17,65.5,m['basalt'],m)
    spear=Sculpture()
    spear.materials.append(m['gilt'])
    spear.tube([(-63.69,65.1,.28),(-63.69,65.1,1.69)],.026,0,10)
    spear.ellipsoid((-63.69,65.1,1.78),(.05,.052,.17),0,12,8)
    spear.finish('Murugan_Vel-renderonly')
    east_cell('Kalyanasundarar_Second_Prakaras',11.5,65.5,6.0,m,height=3.63)
    sculpture_study('kalyanasundarar',10.75,65.5,m['basalt'],m,count=2)
    east_cell('Ekadasa_Linga_Gallery',-43.9,73,8.9,m,height=3.75)
    for k in range(11):
        ling=linga('Ekadasa_Linga_'+str(k+1),(-45.21,69.70+k*.641,.265),.56,m['basalt'])
        ling.rotation_euler.z=math.pi/2
    landmark('ekadasa_linga',(-45.1,73,.74),(-40.7,73,.28))
    east_cell('Sangathar_Sannadhi',-81.1,68,5.4,m,height=3.51)
    # Record the named scholars' shrine without asserting a figurative roster.
    box('Sangathar_Stone_Threshold',(-80.64,68,.21),(1.22,2.56,.42),m['edge'],.035)
    landmark('sangathar',(-81.35,68,.96),(-77.05,68,.16))
    east_cell('Navagraha_Second_Prakaras',15.7,7.45,5.64,m,height=3.46)
    for k in range(3):
        sculpture_study('Navagraha_Study_Row_'+str(k+1),14.80+k*.64,7.45,m['basalt'],m,count=3)
    landmark('navagraha',(15.63,7.45,1.12),(20.32,7.45,.17))
    subsidiary_circuit(m)


def worship_portal(name,x,y,m):
    frames=Blocks()
    for i in range(3):
        for sign in (-1,1):
            frames.add((x+.15+i*.045,y+sign*(1.30+i*.087),1.73),
                       (.34,.10,2.83+i*.18))
        frames.add((x+.15+i*.045,y,3.105+i*.103),(.34,2.76+i*.175,.11))
    frames.finish(name+'_Carved_Door_Surround',m['edge'])
    ornaments=Sculpture()
    ornaments.materials.extend([m['edge_gold'],m['gilt'],m['warm_rose']])
    for sign in (-1,1):
        py=y+sign*1.17
        urn(name+'_Tall_Deepam',(x-1.21,y+sign*1.95,.29),1.11,.15,m['edge_gold'])
        ornaments.ellipsoid((x-1.21,y+sign*1.95,1.40),(.19,.18,.084),0,14,10)
        for i in range(8):
            ornaments.ellipsoid((x+.38,py,.63+i*.285),(.040,.066,.085),i%3,10,6)
    ornaments.finish(name+'_Metal_And_Stone_Detail-renderonly')


def subsidiary_circuit(m):
    small_linga('jayantishwarar',-78.0,-72.6,m)
    for id,x,y,count in [
        ('karimanikka_perumal',-54.0,57.4,1),
        ('dakshinamurti',-60.6,3.1,1),
        ('durga',-65.6,39.70,1),
        ('swami_mahalakshmi',-57.6,37.4,1),
        ('bhairavar',-8.35,38.1,1),
        ('surya',-23.8,38.8,3),
    ]:
        sculpture_study(id,x,y,m['basalt'],m,count=count)
    # The saint images form one named grouping along the southern corridor.
    arts=Sculpture()
    arts.materials.append(m['basalt'])
    for index in range(63):
        x=-69.4+index*.346
        arts.ellipsoid((x,.51,.50),(.108,.11,.24),0,10,7)
        arts.ellipsoid((x,.517,.823),(.074,.070,.094),0,11,8)
        arts.tube([(x-.083,.61,.57),(x,.665,.67),(x+.082,.61,.57)],.022,0,7)
    arts.finish('Arupathu_Moovar_Saint_Row-renderonly')
    box('Arupathu_Moovar_Stone_Plinth',(-58.65,.52,.135),(22.0,.87,.27),m['edge'],.018)
    landmark('nayanmars',(-58.65,.58,.72),(-58.65,2.58,.17))
    # Worshipped figures remain artwork studies wherever the installed
    # image or the precise doorway of the present bay is unverified.
    sculpture_study('sabhapati',20.4,76.3,m['basalt'],m,landing=(20.10,74.45,.17))

def ayiram_kaal(m):
    x0,x1,y0,y1=48.0,126.3,41.0,114.6
    cx,cy=(x0+x1)/2,(y0+y1)/2
    box('Ayiram_Kaal_Raised_Platform',(cx,cy,.14),(x1-x0,y1-y0,.28),m['edge'],.055)
    for i in range(2):
        top=(i+1)*.14
        box('Thousand_Pillar_Entry_Stair',(88.0,y0-.90+i*.44,top/2),(6.7,.48,top),m['edge'],.022)
    shafts,brackets=Blocks(),Blocks()
    for i in range(32):
        for j in range(31):
            # Seven planned openings in the repeated bay field leave 985
            # modeled supports. The exact historic pillar roster is unresolved.
            if (i,j) in {(14,0),(14,1),(14,2),(15,0),(15,1),(15,2),(15,30)}:
                continue
            x=x0+1.25+(x1-x0-2.5)*i/31
            y=y0+1.32+(y1-y0-2.64)*j/30
            if i>=16: x+=.76*(1-(i-16)/15)
            else: x-=.76*i/15
            shafts.add((x,y,2.51),(.47,.51,4.46))
            brackets.add((x,y,.46),(.75,.72,.37))
            brackets.add((x,y,4.46),(1.13,.78,.43))
    shafts.finish('Ayiram_Kaal_Granite_Pillar_Field',m['granite'])
    brackets.finish('Ayiram_Kaal_Carved_Bracket_And_Base_Field',m['edge'])
    box('Ayiram_Kaal_Main_Stone_Roof',(cx,cy,5.11),(x1-x0+.40,y1-y0+.41,.72),m['roof'],.045)
    for i in range(5):
        x=x0+(i+.5)*(x1-x0)/5
        box('Ayiram_Kaal_Roof_Ridge',(x,cy,5.59),(.25,y1-y0+.46,.23),m['roof_edge'],.025)
    wall('Ayiram_Kaal_North_Back',x0,x1,y1,y1,None,0,m,4.85)
    wall('Ayiram_Kaal_East_Back',x1,x1,y0,y1,None,0,m,4.85)
    landmark('thousand_pillars',(88.0,y0+3.6,1.55),(88.0,y0-2.8,.14))
    for id,x,y in [
        ('horse_rider',82.0,44.5),('kuratti',84.27,48.95),('kuravan',92.48,48.95),
        ('tripurantaka',84.27,52.05),('pandya_king',92.48,52.05),
        ('bhikshatana',84.27,55.83),('arjuna',92.48,55.83),('daksha',92.48,59.68),
    ]:
        museum_relief(id,x,y,m)
    musical=Sculpture()
    musical.materials.append(m['granite'])
    for side in (-1,1):
        x=88.3+side*2.7
        for reed in range(5):
            px=x+reed*.135
            musical.tube([(px,62,.28),(px,62,2.39+reed*.09)],.061,0,12)
    musical.finish('Ayiram_Kaal_Musical_Pillar_Study')
    landmark('musical_pillars',(85.92,62,1.40),(88.0,62,.30))


def museum_relief(id,x,y,m):
    s=Sculpture()
    s.materials.append(m['edge'])
    mounted = id == 'horse_rider'
    bow = id in ('arjuna','tripurantaka')
    base = 1.06 if mounted else .16
    if mounted:
        s.ellipsoid((-.18,.17,.78),(.26,.63,.33),0,18,12)
        s.tube([(-.19,-.18,.81),(-.16,-.42,1.08),(-.15,-.61,1.29)],.154,0,13)
        s.ellipsoid((-.14,-.68,1.37),(.154,.30,.17),0,18,11)
        for px in (-.36,.06):
            for py in (-.12,.51):
                s.tube([(px,py,.75),(px+.08,py-.11,.47),(px,py,.17)],.081,0,10)
        s.tube([(-.20,.69,.84),(-.25,.80,.64),(-.22,.84,.42)],.052,0,9)
    s.ellipsoid((0,0,base+.62),(.168,.231,.354),0,18,12)
    s.ellipsoid((.019,0,base+1.13),(.112,.134,.148),0,20,13)
    s.ellipsoid((0,0,base+1.28),(.096,.117,.105 if id!='pandya_king' else .175),0,16,10)
    for side in (-1,1):
        s.tube([(0,side*.12,base+.47),(.062,side*.13,base+.28),(.146,side*.113,base+.08)],
               .071,0,11)
        end=(.25,side*(.40 if bow else .22),base+(.84 if bow else .68))
        s.tube([(.024,side*.169,base+.85),(.16,side*.245,base+.71),end],.061,0,10)
    if bow:
        s.tube([(.26,-.40,.44),(.46,-.43,.66),(.49,-.43,1.10),(.26,-.40,1.41)],.032,0,10)
        s.tube([(.26,-.40,.44),(.26,-.40,1.41)],.011,0,8)
        s.tube([(.36,-.46,base+.84),(.36,.51,base+.89)],.017,0,8)
    if id=='kuratti':
        s.ellipsoid((-.19,.27,base+.69),(.18,.22,.28),0,16,10)
        s.ellipsoid((-.22,.25,base+1.07),(.14,.22,.20),0,16,10)
    if id=='kuravan':
        s.tube([(.26,-.22,.25),(.26,-.22,1.60)],.027,0)
    if id=='bhikshatana':
        s.ellipsoid((.23,-.29,base+.67),(.118,.117,.072),0,14,8)
        s.ellipsoid((.07,.36,.42),(.21,.32,.18),0,14,8)
        s.tube([(.09,.43,.42),(.10,.55,.63),(.10,.57,.76)],.063,0,9)
    s.finish(id+'_Carved_Pillar_Study-renderonly',(x,y,.28))
    landing={
        'kuravan':(92.861,47.071,.30),
        'pandya_king':(92.12,50.206,.30),
        'arjuna':(92.861,53.951,.30),
    }.get(id,(x+1.82,y,.30))
    landmark(id,(x+.10,y,base+.88),landing)


def ashta_shakti_pillar(id,x,y,toward,m):
    s=Sculpture()
    s.materials.append(m['edge'])
    for i in range(7):
        width=.41-.039*i
        s.ellipsoid((0,-.025,1.82+.072*i),(width*.50,.087,.079),0,16,8)
    s.ellipsoid((0,-.09,1.67),(.175,.111,.218),0,22,13)
    s.ellipsoid((0,-.055,1.12),(.294,.168,.370),0,20,13)
    s.ellipsoid((.013,-.037,.63),(.270,.158,.333),0,22,12)
    for sign in (-1,1):
        s.tube([(sign*.143,-.048,.64),(sign*.134,-.087,.38),(sign*.16,-.122,.24)],.092,0,12)
        s.tube([(sign*.235,-.090,1.32),(sign*.404,-.11,1.13),
                (sign*.31,-.21,.91)],.067,0,11)
        s.tube([(sign*.237,-.03,1.41),(sign*.43,-.036,1.53),
                (sign*.51,-.14,1.68)],.064,0,11)
        s.rosette((sign*.18,-.159,1.64),.054,0,None,7)
    if id in ('raudri','maheshwari','kaumari'):
        s.tube([(.51,-.155,1.31),(.515,-.157,2.14)],.021,0,10)
        if id == 'kaumari':
            s.ellipsoid((.515,-.158,2.15),(.07,.038,.15),0,13,8)
        else:
            for offset in (-.073,0,.073):
                s.tube([(.515,-.157,2.07),(.515+offset,-.157,2.21)],.016,0,8)
    elif id=='vaishnavi':
        points=[(-.51+.12*math.cos(k*math.tau/36),-.157,1.77+.12*math.sin(k*math.tau/36))
                for k in range(37)]
        s.tube(points,.024,0,8)
        s.ellipsoid((.51,-.16,1.77),(.072,.052,.132),0,18,10)
    elif id=='shyamala':
        s.tube([(-.35,-.22,1.13),(.48,-.22,1.52)],.027,0,9)
        s.ellipsoid((-.36,-.225,1.13),(.113,.070,.097),0,15,9)
    else:
        s.rosette((-.51,-.151,1.75),.105,0,None,9)
        s.rosette((.51,-.151,1.75),.105,0,None,9)
    obj=s.finish(id+'_Mantapa_Pillar_Relief-renderonly',(x,y,.17))
    obj.rotation_euler.z=0 if toward<0 else math.pi
    landing_y=DEVI_Y if y<DEVI_Y else y+toward*2.18
    landmark(id,(x,y+toward*.17,1.48),(x,landing_y,.17))


def approach_halls(m):
    halls=[
        ('Ashta_Shakti_Mandapa',(110,129,-58,-26),6,4,5.2,'x'),
        ('Veda_Mandapa',(103,110,-54,-31),4,2,4.6,'x'),
        ('Meenakshi_Nayaka_Mandapa',(78,103,-58,-26),6,6,5.28,'x'),
        ('Mudali_Pillai_Mandapa',(44,63,-58,-28),5,5,4.9,'x'),
        ('Kilikoottu_Mandapa',(-30,-22,-89,-32),12,2,4.6,'y'),
        ('Oonjal_Mandapa',(-34,-21,-90,-71),4,4,4.65,'x'),
        ('Thirukalyana_Mandapa',(65,95,-9,7),4,7,5.05,'x'),
        ('Mangayarkarasi_Mandapa',(95,119,-16,4),5,5,4.9,'x'),
        ('Veera_Vasantharayar_Mandapa',(44,121,10,35),6,12,5.28,'x'),
        ('Hundred_Pillar_Mandapa',(-12,28,57,80),10,10,4.55,'x'),
        ('West_Amman_Mandapa',(-100,-91,-80,-21),10,2,4.55,'y'),
        ('Tiruvilayadal_Gallery',(-90,-76,34,77),8,4,4.55,'y'),
        ('South_Outer_Service_Mandapa',(16,49,-112,-101),2,8,4.5,'x'),
    ]
    for name,bounds,rows,cols,height,axis in halls:
        crossing = DEVI_Y if name in ('Kilikoottu_Mandapa','West_Amman_Mandapa') else None
        mandapa(name,bounds,rows,cols,m,height,axis,cross_y=crossing)
    shrine_gate('Chitra_Gopuram',68,DEVI_Y,17.0,7.4,24,7,math.pi/2,m,5.8)
    landmark('chitra',(68,DEVI_Y,2.0),(74.4,DEVI_Y,.17))
    landmark('ashta_shakti',(120,DEVI_Y,1.43),(124.0,DEVI_Y,.18))
    landmark('meenakshi_nayaka',(92,DEVI_Y,1.50),(97.8,DEVI_Y,.18))
    landmark('kilikoottu',(-26,-56,1.22),(-27.0,-51.6,.16))
    landmark('oonjal',(-26,-78,1.27),(-26.46,-79.84,.17))
    anchor('Spawn_Point',(121.6,DEVI_Y,.18))
    anchor('Arrival_Facing',(86,DEVI_Y,.18))
    landmark('veera_vasantharayar',(75,SWAMI_Y,1.56),(81,SWAMI_Y,.18))
    landmark('kalyana_hall',(80,-1.0,1.35),(87,-1.04,.16))
    landmark('mangayarkarasi',(104,-8.0,1.55),(111,-8.3,.18))
    landmark('mudali_pillai',(53,DEVI_Y,1.40),(57.1,DEVI_Y,.18))
    landmark('hundred_pillars',(8,67.5,1.65),(12.6,68.5,.17))
    # Eight carved pillar positions along the Ashta Shakti entrance.
    for direction,names in [
        (1,('yajnarupini','shyamala','maheshwari','manonmani')),
        (-1,('kaumari','raudri','vaishnavi','mahalakshmi')),
    ]:
        for index,name in enumerate(names):
            ashta_shakti_pillar(name,126-index*4.38,DEVI_Y+direction*3.62,-direction,m)
    # A relief group study identifies the documented wedding group
    # in Kambathadi. It is kept distinct from the Kalyanasundarar shrine.
    sculpture_study('wedding_relief',12.65,34.8,m['edge'],m,count=3)
    Sculpture # Keep the authored figure studies independent of colliders.
    ayiram_kaal(m)


def outer_prakara(m):
    floor_without((WEST-3,EAST+4,SOUTH-3,NORTH+3),TANK,0.0,m)
    for label,coord,axis,height,breadth,gap in [
        ('South',(-25,SOUTH),'y',51.9,32.0,7.2),
        ('North',(-25,NORTH),'y',45.8,26.5,6.0),
        ('West',(WEST,SWAMI_Y),'x',47.0,27.3,6.8),
        ('East',(EAST,SWAMI_Y),'x',45.7,27.9,7.0),
    ]:
        x,y=coord
        yaw=0 if axis=='y' else math.pi/2
        name=label+'_Raja_Gopuram'
        shrine_gate(name,x,y,breadth,11.15,height,9,yaw,m,gap)
        if label=='South':
            landing=(x,y+8.0,.05)
        elif label=='North':
            landing=(x,y-8.0,.05)
        elif label=='West':
            landing=(x+8.0,y,.05)
        else:
            landing=(x-10.0,y,.17)
        landmark(label.lower()+'_raja',(x,y,2.34),landing)
    wall('South_Street_Outer_Prakaras',WEST,EAST,SOUTH,SOUTH,-25,7.2,m,7.0,1.48)
    wall('North_Street_Outer_Prakaras',WEST,EAST,NORTH,NORTH,-25,6.0,m,7.0,1.48)
    wall('West_Street_Outer_Prakaras',WEST,WEST,SOUTH,NORTH,SWAMI_Y,6.8,m,7.0,1.48)
    wall('East_Street_Outer_Prakaras_North',EAST,EAST,-28,NORTH,SWAMI_Y,7.0,m,7.0,1.48)
    wall('East_Street_Outer_Prakaras_South',EAST,EAST,SOUTH,-58,None,0,m,7.0,1.48)
    # Roofed ranges and tree clusters line the inner Aadi streets.
    ranges=[
        ('West_Aadi_Upper',(WEST+4,WEST+10,31,110),17,2,'y'),
        ('West_Aadi_Lower',(WEST+4,WEST+10,-111,11),23,2,'y'),
        ('South_Aadi_West',(WEST+8,-38,SOUTH+5,SOUTH+10),2,16,'x'),
        ('South_Aadi_East',(-13,EAST-8,SOUTH+5,SOUTH+10),2,22,'x'),
        ('North_Aadi_West',(WEST+8,-39,NORTH-10,NORTH-5),2,17,'x'),
        ('North_Aadi_East',(-11,44,NORTH-10,NORTH-5),2,12,'x'),
    ]
    for name,bounds,rows,cols,aisle in ranges:
        mandapa(name,bounds,rows,cols,m,4.0,aisle)
    city_context(m)


def city_context(m):
    # Visual context follows the streets around the precinct. Buildings
    # outside the enclosure carry no shrines or shrine-map markers.
    box('Ground_City_Context',(0,0,-2.98),(385,352,.37),m['city_ground'])
    for index,rect in enumerate([
        (-192.5,WEST-3,-176,176),(EAST+4,192.5,-176,176),
        (WEST-3,EAST+4,-176,SOUTH-3),(WEST-3,EAST+4,NORTH+3,176),
    ]):
        surface(f'Ground_Chithirai_Street_{index}',*rect,-.041,m['city_ground'])
    rng=random.Random(637)
    blocks=[Blocks() for color in m['city']]
    roofs=Blocks()
    for direction in (-1,1):
        for i in range(24):
            x=-152+i*13.1+rng.uniform(-2.4,2.4)
            y=direction*(141+rng.uniform(-1.8,6.1))
            h=rng.uniform(3.4,10.1)
            w=rng.uniform(8.4,14.5)
            d=rng.uniform(10.0,22.0)
            blocks[i%len(blocks)].add((x,y,h/2),(w,d,h))
            roofs.add((x,y,h+.11),(w+.23,d+.23,.22))
        for i in range(19):
            x=direction*(151+rng.uniform(-1.75,5.6))
            y=-108+i*12.8+rng.uniform(-1.6,1.7)
            if direction==1 and 6<y<38:
                continue
            h=rng.uniform(3.3,9.6)
            w=rng.uniform(10.9,17.6)
            d=rng.uniform(7.9,13.9)
            blocks[(i+1)%len(blocks)].add((x,y,h/2),(w,d,h))
            roofs.add((x,y,h+.12),(w+.24,d+.24,.24))
    for i,network in enumerate(blocks):
        network.finish(f'Terrain_City_Block_Study_{i}-renderonly',m['city'][i])
    roofs.finish('Terrain_City_Roof_Waterproofing-renderonly',m['roof'])
    foliage=Sculpture()
    foliage.materials.extend(m['leaf'])
    bark=Blocks()
    for i,(x,y) in enumerate([(-118,-80),(-116,-28),(-118,68),(-104,106),(-75,103),(-64,-105),
                               (-21,-106),(46,-105),(90,-106),(113,-100),(110,-69),
                               (113,-20),(118,39),(29,102),(-87,93),(43,-72)]):
        h=rng.uniform(3.9,6.8)
        bark.add((x,y,h*.33),(.57,.51,h*.66))
        for j in range(10):
            angle=math.tau*j/10
            offset=rng.uniform(1.1,3.21)
            foliage.ellipsoid((x+offset*math.cos(angle),y+offset*math.sin(angle),h+rng.uniform(-.99,1.21)),
                              (rng.uniform(1.6,2.9),rng.uniform(1.5,2.8),rng.uniform(1.4,2.9)),
                              (i+j)%len(m['leaf']),12,8)
    foliage.finish('Aadi_Courtyard_Trees-renderonly')
    bark.finish('Aadi_Tree_Trunks',m['bark'])


def build():
    clear_scene()
    m={
        'granite':create_granite_stone('Madurai_Granite',(.21,.183,.151,1)),
        'edge':create_granite_stone('Madurai_Dressed_Granite',(.30,.249,.205,1)),
        'paving':create_granite_stone('Madurai_Court_Paving',(.415,.367,.304,1)),
        'basalt':material('Madurai_Sacred_Basalt',(.025,.021,.019),.47),
        'roof':material('Madurai_Terracotta_Weathered_Roofs',(.205,.093,.049),.88),
        'roof_edge':material('Madurai_Masonry_Waterproof_Ridge',(.19,.082,.041),.88),
        'warm_rose':material('Madurai_Painted_Pink_Lime_Plaster',(.387,.216,.170)),
        'gilt':material('Madurai_Gilt_Vimana',(.60,.34,.075),.35,.61),
        'edge_gold':material('Madurai_Darker_Gilt',(.42,.185,.027),.37,.66),
        'water':material('Potramarai_Deep_Green_Water',(.039,.091,.062),.46),
        'redwash':material('Nayak_Mural_Undercoat',(.27,.143,.094)),
        'city_ground':material('Madurai_Chithirai_Street',(.151,.136,.119),.89),
        'bark':material('Madurai_Tree_Bark',(.125,.083,.047)),
        'city':[material('Madurai_City_Lime_'+str(i),color) for i,color in enumerate([
            (.35,.207,.129),(.49,.391,.315),(.295,.358,.309),(.342,.282,.228),(.48,.303,.249)])],
        'leaf':[material('Madurai_Leaf_Canopy_'+str(i),color) for i,color in enumerate([
            (.100,.173,.065),(.133,.210,.075),(.10,.151,.050),(.166,.234,.079)])],
        'stucco':[material('Madurai_Tower_Stucco_'+str(i),color) for i,color in enumerate([
            (.149,.305,.262),(.37,.202,.10),(.151,.24,.365),(.443,.298,.14),
            (.31,.145,.174),(.275,.35,.194),(.43,.347,.199)])],
    }
    outer_prakara(m)
    tank(m)
    inner_courts(m)
    approach_halls(m)
    rotate_new(set(),0,0,math.radians(14.0))


build()
if not globals().get('DEFER_GLB_EXPORT',False):
    finish('madurai_meenakshi')
