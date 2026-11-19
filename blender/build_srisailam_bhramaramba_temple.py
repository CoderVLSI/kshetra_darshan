"""Srisailam double sanctuary, historic enclosure and in-complex shrines."""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

from common_geometry import clear_scene, create_deepam
from deity_detail import Sculpture, crown_band, garland, palette
from present_day_sites import anchor, finish, material
from surface_detail import add_stone_detail, prepare_scene


def register(id, target, landing):
    anchor(id+'_Anchor',target)
    anchor(id+'_Landing',landing)


def box(name, position, size, surface, bevel=0):
    """Link a dimensioned box without a global Blender operator per masonry piece."""
    x,y,z = (d/2 for d in size)
    vertices=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
              (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    data=bpy.data.meshes.new(name)
    data.from_pydata(vertices,[],faces)
    data.materials.append(surface)
    data.update()
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=position
    if bevel:
        modifier=obj.modifiers.new('Worn Edges','BEVEL')
        modifier.width=bevel
        modifier.segments=2
    return obj


def sphere(name, position, scale, surface, segments=24):
    data=bpy.data.meshes.new(name)
    geometry=bmesh.new()
    bmesh.ops.create_uvsphere(geometry,u_segments=segments,v_segments=14,radius=1)
    bmesh.ops.scale(geometry,verts=list(geometry.verts),vec=Vector(scale))
    for face in geometry.faces:
        face.smooth=True
    geometry.to_mesh(data)
    geometry.free()
    data.materials.append(surface)
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=position
    return obj


def cylinder(name, position, radius, height, surface):
    verts=[(radius*math.cos(i*math.tau/24),radius*math.sin(i*math.tau/24),z)
           for z in [-height/2,height/2] for i in range(24)]
    faces=[tuple(range(23,-1,-1)),tuple(range(24,48))]
    faces.extend((i,(i+1)%24,(i+1)%24+24,i+24) for i in range(24))
    data=bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.materials.append(surface)
    data.update()
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=position
    return obj


def profile(name, position, dimensions, rows, surface):
    """Join successive horizontal rectangular cornice sections."""
    x,y,z = position
    w,d = dimensions
    verts=[(x+sx*w*rw/2,y+sy*d*rd/2,z+h) for h,rw,rd in rows
           for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    faces=[(3,2,1,0)]
    for i in range(len(rows)-1):
        j=4*i
        faces.extend((j+k,j+(k+1)%4,j+(k+1)%4+4,j+k+4) for k in range(4))
    faces.append(tuple(range(len(verts)-4,len(verts))))
    data=bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.materials.append(surface)
    data.update()
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    return obj


def beam(name,start,end,section,surface):
    axis=Vector(end)-Vector(start)
    obj=box(name,(Vector(start)+Vector(end))/2,(section,section,axis.length),surface,.012)
    obj.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
    return obj


def rotate_objects(before, center, radians):
    x,y,z=center
    transform=Matrix.Translation(Vector((x,y,z))) @ Matrix.Rotation(radians,4,'Z') @ Matrix.Translation(Vector((-x,-y,-z)))
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.name not in before and obj.parent is None:
            obj.matrix_world=transform @ obj.matrix_world


def pillar(name,x,y,z,h,m,rich=False):
    rows=[(0,1.42,1.42),(.15,1.42,1.42),(.22,1.17,1.17),(.43,1.17,1.17),
          (.51,.85,.85),(h*.23,.85,.85),(h*.30,1.11,1.11),(h*.63,1.11,1.11),
          (h*.71,.82,.82),(h*.83,.82,.82),(h*.89,1.06,1.06),(h*.96,1.49,1.49),(h,1.60,1.60)]
    profile(name,(x,y,z),(.50,.54),rows,m['granite'])
    if rich:
        for dx in [-.29,.29]:
            for dy in [-.30,.30]:
                cylinder(name+'_Inset_Rod',(x+dx,y+dy,z+h*.47),.046,h*.32,m['trim'])
        for offset in [.25,.335,h*.32,h*.58,h*.885]:
            box(name+'_Carved_Band',(x,y,z+offset),(.63,.67,.055),m['trim'],.013)


def mandapa(name,cx,cy,width,depth,floor,height,nx,ny,m,closed=False):
    box(name+'_Plinth',(cx,cy,floor-.105),(width,depth,.21),m['granite'],.028)
    box(name+'_Roof_Fascia',(cx,cy,floor+height),(width+.43,depth+.43,.24),m['trim'],.042)
    box(name+'_Granite_Roof',(cx,cy,floor+height+.22),(width+.6,depth+.60,.23),m['granite'],.042)
    for i in range(nx):
        x=cx+(i/(nx-1)-.5)*(width-1.30)
        for j in range(ny):
            y=cy+(j/(ny-1)-.5)*(depth-1.37)
            if abs(y-cy) < 1.3:
                continue
            pillar(name+'_Pillar',x,y,floor,height-.12,m,rich=i in [0,nx-1] or j in [0,ny-1])
    if closed:
        for side in [-1,1]:
            y=cy+side*(depth/2-.21)
            segment=(width-3.8)/2
            for sx in [-1,1]:
                x=cx+sx*(1.9+segment/2)
                box(name+'_Side_Wall',(x,y,floor+height/2),(segment,.42,height-.10),m['granite'],.022)
            box(name+'_Side_Porch_Lintel',(cx,y,floor+height-.43),(3.82,.46,.69),m['trim'],.021)


def stone_steps(name,x_end,cy,width,low,high,count,tread,m):
    run=count*tread
    for i in range(count):
        z=low+(high-low)*(i+1)/count
        x=x_end+run-(i+.5)*tread
        box(name+'_Stone_Tread-renderonly',(x,cy,(low+z)/2),
            (tread+.011,width,z-low),m['granite'],.018)
    half=width/2
    coords=[(x_end+run,cy-half,low),(x_end+run,cy+half,low),
            (x_end,cy+half,high),(x_end,cy-half,high),
            (x_end,cy+half,low),(x_end,cy-half,low)]
    data=bpy.data.meshes.new(name+'_Ascent')
    data.from_pydata(coords,[],[(0,1,2,3),(0,3,5),(1,4,2),(3,2,4,5),(5,4,1,0)])
    data.materials.append(m['granite'])
    data.update()
    obj=bpy.data.objects.new(name+'_Ascent-colonly',data)
    bpy.context.collection.objects.link(obj)


def doorway(name,cx,cy,w,d,z,h,m,surface):
    section=(w-2.25)/2
    for x in [cx-w/2+.20,cx+w/2-.20]:
        box(name+'_Cell_Side',(x,cy,z+h/2),(.40,d,h),surface,.028)
    box(name+'_Cell_Back',(cx,cy+d/2-.19,z+h/2),(w,.38,h),surface,.026)
    for side in [-1,1]:
        x=cx+side*(1.125+section/2)
        box(name+'_Cell_Front',(x,cy-d/2+.18,z+h/2),(section,.37,h),surface,.024)
        box(name+'_Torana_Jamb',(cx+side*1.19,cy-d/2-.055,z+1.13),(.16,.13,2.22),m['trim'],.026)
    box(name+'_Cell_Lintel',(cx,cy-d/2+.18,z+(h+2.25)/2),(2.26,.43,h-2.25),surface,.025)
    box(name+'_Cell_Flat_Lid',(cx,cy,z+h),(w+.39,d+.39,.24),surface,.03)
    box(name+'_Torana_Header',(cx,cy-d/2-.055,z+2.30),(2.53,.14,.17),m['trim'],.027)


def roof_tower(name,x,y,z,w,d,height,levels,m,metal=False):
    body=m['gold'] if metal else m['trim']
    trim=m['gold_hi'] if metal else m['granite']
    for i in range(levels):
        t=i/levels
        hh=height/levels
        size=1-.71*t
        sw,sd=w*size,d*size
        base=z+i*hh
        profile(name+'_Tala',(x,y,base),(sw,sd),
                [(0,1,1),(.11*hh,1.02,1.02),(.21*hh,.97,.97),(.35*hh,.91,.91),
                 (.80*hh,.87,.87),(hh,.82,.82)],body)
        box(name+'_Tala_Cornice',(x,y,base+.26*hh),(sw*1.055,sd*1.05,.095*height/levels),trim,.026)
        for sign in [-1,1]:
            for frac in [-.34,0,.34]:
                px=x+frac*sw
                py=y+sign*.451*sd
                profile(name+'_Kuta',(px,py,base+.31*hh),(sw*.170,.106*sd),
                        [(0,1,1),(.16*hh,1,1),(.29*hh,.73,.76),(.48*hh,.17,.26)],trim)
    top_z=z+height
    sphere(name+'_Rounded_Sikhara',(x,y,top_z+.06*height),
           (.187*w,.185*d,.102*height),body,32)
    sphere(name+'_Kalasha',(x,y,top_z+.177*height),(.126*w,.126*w,.063*height),
           m['gold_hi'] if metal else m['trim'],22)
    cylinder(name+'_Finial',(x,y,top_z+.242*height),.043*w,.084*height,trim)


def gate(name,x,y,z,w,d,height,levels,m,finish_key,angle):
    origin=(x,y,z)
    before={o.name for o in bpy.context.scene.objects}
    passage=4.48
    jamb=(w-passage)/2
    for side in [-1,1]:
        px=x+side*(passage/2+jamb/2)
        box(name+'_Granite_Jamb',(px,y,z+2.61),(jamb,d,5.22),m['granite'],.040)
        for dz in [.15,.44,.81,4.43,4.77,5.17]:
            box(name+'_Granite_Jamb_Band',(px,y,z+dz),(jamb+.17,d+.21,.14),m['trim'],.023)
        for dir_y in [-1,1]:
            for i in [-1,0,1]:
                pillar(name+'_Door_Engaged_Pilaster',px+i*jamb*.24,y+dir_y*(d/2+.03),
                       z+.67,3.86,m,rich=True)
    box(name+'_Door_Ceiling',(x,y,z+5.47),(w+.30,d+.39,.50),m['granite'],.035)
    bind=height/levels
    body=m[finish_key]
    dem=m['gopura_shadow'] if finish_key=='ochre' else m['cream_shadow']
    for row in range(levels):
        taper=1-.56*(row/levels)
        ww,dd=w*taper,d*taper
        base=z+5.69+row*bind
        profile(name+'_Tower_Tala',(x,y,base),(ww,dd),
                [(0,1,1),(.13*bind,1.025,1.03),(.24*bind,.965,.96),
                 (.30*bind,.936,.93),(.77*bind,.906,.90),(bind,.86,.88)],body)
        count=max(3,9-2*(row//2))
        frieze=Sculpture()
        frieze.materials.extend([body,dem,m['gold_hi']])
        for side in [-1,1]:
            outer_y=y+side*dd*.477
            for n in range(count):
                px=x+(n-(count-1)/2)*ww*.82/count
                dim=ww*.13 if n==count//2 else ww*.098
                profile(name+'_Tower_Panel',(px,outer_y,base+.29*bind),(dim,dd*.102),
                        [(0,1,1),(.28*bind,.93,.98),(.42*bind,.49,.7),(.52*bind,.14,.4)],body)
                frieze.ellipsoid((px,outer_y+side*.054*dd,base+.54*bind),
                                (dim*.25,.10,.18*bind),1,10,8)
                frieze.ellipsoid((px,outer_y+side*.061*dd,base+.70*bind),
                                (dim*.12,.12,.082*bind),0,10,8)
            box(name+'_Horizontal_Tower_Moulding',(x,outer_y,base+.239*bind),
                (ww,dd*.095,.12),dem,.018)
        frieze.finish(name+'_Stucco_Details-renderonly')
    cap=z+5.69+height
    profile(name+'_Shala_Ridge_Base',(x,y,cap),(w*.45,d*.48),
            [(0,1,1),(.23,1.10,1.10),(.47,.98,.98),(.90,.87,.79),(1.38,.79,.47)],body)
    for i in range(7):
        px=x+(i-3)*.058*w
        sphere(name+'_Ridge_Kalasha',(px,y,cap+1.63),(.14,.14,.27),m['gold_hi'],16)
    rotate_objects(before,origin,angle)


def east_opening(name,cx,cy,w,d,z,h,m):
    before={o.name for o in bpy.context.scene.objects}
    doorway(name,cx,cy,d,w,z,h,m,m['granite'])
    rotate_objects(before,(cx,cy,z),math.pi/2)

def nandi(name,x,y,z,m,scale=1):
    s=Sculpture()
    p=palette(s)
    s.materials.append(m['dark'])
    stone=len(s.materials)-1
    s.ellipsoid((0,.16,.29),(.35,.64,.29),stone,30,18)
    s.ellipsoid((0,-.24,.48),(.28,.27,.26),stone,24,16)
    s.ellipsoid((0,-.43,.60),(.206,.20,.20),stone,24,16)
    s.ellipsoid((0,-.586,.54),(.17,.136,.092),stone,24,16)
    for sx in [-1,1]:
        s.tube([(sx*.22,.024,.17),(sx*.28,-.21,.11),(sx*.19,-.41,.09)],.095,stone,12)
        s.tube([(sx*.155,-.392,.70),(sx*.20,-.40,.82),(sx*.14,-.38,.91)],.036,stone,12)
        s.ellipsoid((sx*.216,-.415,.648),(.122,.063,.049),stone)
        s.ellipsoid((sx*.132,-.568,.652),(.026,.022,.023),p['eye'],14,10)
    for row in range(3):
        s.tube([(.245*math.cos(a),-.42+row*.081,.46+.267*math.sin(a))
                for a in [math.tau*i/50 for i in range(51)]],.013,p['gold'],9)
    for i in range(13):
        a=math.pi+i*math.pi/12
        s.ellipsoid((.22*math.cos(a),-.48,.47+.25*math.sin(a)),(.033,.023,.036),p['gold'],10,8)
    s.tube([(.21,.59,.20),(.35,.64,.16),(.42,.40,.12),(.38,.18,.12)],.035,stone,9)
    obj=s.finish(name+'-renderonly',(x,y,z),scale)
    obj.rotation_euler.z=-math.pi/2


def sacred_linga(name,x,y,z,m,scale=1,kind='standard'):
    s=Sculpture()
    p=palette(s)
    s.materials.append(m['dark'])
    black=len(s.materials)-1
    s.ellipsoid((0,0,.15),(.58,.49,.106),black,34,18)
    s.ellipsoid((0,0,.243),(.54,.43,.076),black,34,16)
    s.ellipsoid((-.42,0,.209),(.32,.125,.08),black,24,14)
    height=.40 if kind=='mallikarjuna' else .56
    s.ellipsoid((0,0,.263+height*.32),(.23,.226,height*.47),black,36,20)
    if kind=='sahasra':
        # The Census records forty small lingas in each of twenty-five facets.
        for facet in range(25):
            a=math.tau*facet/25
            for i in range(40):
                zz=.309+i*.0091
                r=.185+.023*math.sin(i*math.pi/40)
                s.ellipsoid((r*math.cos(a),r*math.sin(a),zz),(.016,.016,.012),black,6,5)
        for a in [-.95,0,.95]:
            pz=.83+.047*(1-abs(a))
            s.tube([(-.29,.05,.27),(-.34,.09,.43),(-.12,.17,.73),
                    (.17*math.sin(a),.16,pz)],.025,p['gold'],9)
            s.ellipsoid((.17*math.sin(a),.155,pz),(.075,.032,.093),p['gold'],14,9)
    if kind=='mallikarjuna':
        for hood in range(5):
            f=(hood-2)/2
            s.ellipsoid((f*.35,.22,.82+.12*(1-f*f)),(.102,.059,.178),p['gold'],22,14)
            s.ellipsoid((f*.35,.156,.88+.12*(1-f*f)),(.031,.021,.042),p['black'],14,10)
            s.tube([(0,.23,.29),(f*.22,.23,.61),(f*.35,.22,.79)],.036,p['gold'],12)
        s.ellipsoid((0,0,1.26),(.177,.174,.153),p['gold'],24,18)
        s.tube([(0,0,1.12),(0,0,1.07)],.028,p['gold'],10)
        for sx in [-1,1]:
            s.tube([(sx*.142,0,1.34),(sx*.062,0,1.58),(0,0,1.70)],.012,p['gold'],9)
        for i in range(45):
            a=math.tau*i/45
            s.ellipsoid((.42*math.cos(a),.34*math.sin(a),.322+(.013 if i%2 else 0)),
                        (.032,.033,.026),p['orange'] if i%3 else p['red'],10,7)
    s.finish(name+'-renderonly',(x,y,z),scale).rotation_euler.z=math.pi/2


def queen_study(position):
    # The published alankara shows visible gold kavacha, not the limbs beneath it.
    s=Sculpture()
    p=palette(s)
    gold=s.material('Bhramaramba Kavacha Gold',(.70,.49,.19),.45,.36)
    cloth=s.material('Bhramaramba Deep Red Textile',(.31,.027,.048),0,.73)
    s.ellipsoid((0,.03,.84),(.29,.133,.58),cloth,36,24)
    def face_shape(v):
        if v.y < 0:
            v.y -= .030*math.exp(-(v.x/.062)**2-((v.z-.007)/.052)**2)
        return v
    s.ellipsoid((0,-.045,1.31),(.136,.103,.162),gold,48,34,face_shape)
    s.ellipsoid((0,-.148,1.246),(.051,.018,.021),p['red'],22,12)
    s.ellipsoid((0,-.152,1.243),(.030,.017,.008),p['black'],16,8)
    for side in [-1,1]:
        s.ellipsoid((side*.052,-.135,1.332),(.040,.022,.019),p['eye'],20,12)
        s.ellipsoid((side*.052,-.153,1.332),(.013,.008,.015),p['black'],16,9)
        s.tube([(side*.017,-.146,1.370),(side*.049,-.145,1.384),(side*.090,-.117,1.367)],
               .009,p['black'],8)
        s.rosette((side*.155,-.091,1.286),.051,gold,p['red'],9)
    s.rosette((0,-.151,1.397),.021,p['red'],p['silver'],7)
    for i in range(5):
        zz=1.475+i*.067
        radial=.145-i*.017
        s.ellipsoid((0,.002,zz),(radial,.097-i*.009,.052),gold,22,12)
        s.rosette((0,-.099+i*.004,zz),.031 if i<3 else .022,gold,p['silver'],8)
    crown_band(s,p,.145,1.48,-.078,4)
    for n in range(5):
        for i in range(45):
            a=math.pi+i*math.pi/44
            clr=p['white'] if i%15<8 else (p['red'] if i%15<12 else p['green'])
            s.rosette(((.29+n*.042)*math.cos(a),-.111-n*.007,
                       1.41-n*.024+(.53+n*.087)*math.sin(a)),
                      .032 if n>1 else .023,clr,None,6)
    for j in range(7):
        for i in range(38):
            a=math.pi+i*math.pi/37
            z=1.24+(.27+j*.079)*math.sin(a)
            s.ellipsoid(((.185+j*.011)*math.cos(a),-.162-j*.005,z),(.013,.012,.013),
                        gold if i%9 else p['silver'],9,7)
        s.rosette((0,-.218,.969-j*.072),.041 if j%2 else .056,
                  p['silver'] if j%2 else gold,p['green'] if j%3==0 else p['red'],10)
    for i in range(13):
        t=(i-6)/6
        s.tube([(t*.245,-.072,.65),(t*.31,-.131,.29),(t*.44,-.279,.071)],.038,cloth,12)
        s.tube([(t*.38,-.252,.144),(t*.44,-.304,.073)],.008,gold,9)
    for i in range(8):
        t=(i-3.5)*.125
        s.rosette((t,-.25,.12),.034,p['red'] if i%3 else p['white'],p['gold'],8)
    st=-.66
    s.tube([(st,-.21,.09),(st,-.21,1.38)],.023,p['silver'],12)
    for side in [-1,0,1]:
        s.tube([(st,-.21,1.23),(st+side*.093,-.21,1.34),
                (st+side*.114,-.21,1.48)],.019,gold,10)
    s.finish('Bhramaramba_Photographed_Alankara-renderonly',position).rotation_euler.z=math.pi/2


def arch_details(name,x,y,z,span,height,m):
    s=Sculpture()
    p=palette(s)
    for i in range(4):
        pts=[((span/2+i*.053)*math.cos(a),-.035-i*.014,height*(.53+.45*math.sin(a)))
             for a in [math.pi*j/61 for j in range(62)]]
        s.tube(pts,.025,p['gold'],12)
    for i in range(25):
        a=math.pi*i/24
        s.rosette(((span/2+.14)*math.cos(a),-.10,height*(.55+.45*math.sin(a))),.046,p['gold'],p['red'],7)
    for side in [-1,1]:
        s.tube([(side*(span/2+.15),-.08,.09),(side*(span/2+.15),-.08,height*.56)],.046,p['gold'],12)
    s.finish(name+'-renderonly',(x,y,z)).rotation_euler.z=math.pi/2


def sri_chakra(x,y,floor,m):
    cylinder('Sri_Chakra_Stone_Pitha',(x,y,floor+.065),.69,.13,m['dark'])
    s=Sculpture()
    s.materials.extend([m['trim'],m['gold_hi']])
    for i in range(9):
        r=.25+i*.037
        a=math.pi/2 if i<4 else -math.pi/2
        points=[(x+r*math.cos(a+j*math.tau/3),y+r*math.sin(a+j*math.tau/3),floor+.138)
                for j in range(4)]
        s.tube(points,.009,0,8)
    for ring,r in enumerate([.59,.632]):
        s.tube([(x+r*math.cos(a),y+r*math.sin(a),floor+.139)
                for a in [math.tau*i/60 for i in range(61)]],.010,ring,8)
    s.ellipsoid((x,y,floor+.143),(.021,.021,.012),1,12,8)
    s.finish('Srichakra_Sculpted_Geometry-renderonly')
    register('Sri_Chakra',(x,y,floor+.14),(x+1.58,y,floor+.090))


def study_figure(name,position,form,m,angle=math.pi/2):
    s=Sculpture()
    p=palette(s)
    dark=p['black'] if form!='ganesha' else p['red']
    seated=form in ['ganesha','uma','ardha','kumara','rajarajeshwari','akkamahadevi','mallamma']
    dress=p['red'] if form in ['rajarajeshwari','annapurna','bhadrakali','mallamma'] else dark
    s.ellipsoid((0,.025,.63),(.245,.115,.29),dress,28,17)
    s.ellipsoid((0,-.017,1.00),(.133,.103,.159),dark,28,18)
    s.ellipsoid((0,.01,1.161),(.107,.075,.129),p['gold'],24,14)
    for side in [-1,1]:
        s.ellipsoid((side*.046,-.111,1.029),(.024,.016,.014),p['eye'],14,9)
        if seated:
            s.tube([(side*.09,.009,.439),(side*.251,-.019,.245),(side*.099,-.202,.176)],.101,dress,12)
        else:
            s.tube([(side*.099,.01,.461),(side*.084,.005,.174),(side*.101,-.036,.068)],.071,dress,12)
        s.tube([(side*.185,.01,.794),(side*.275,-.007,.661),(side*.200,-.145,.575)],
               .058,dark,12)
    fans={'veera':4,'sudarshana':7,'bhadrakali':1,'kumara':5,'ardha':1,'ganesha':1,'rajarajeshwari':1}
    for arm in range(fans.get(form,0)):
        for side in [-1,1]:
            px=side*(.35+arm*.032)
            pz=.55+arm*.123
            s.tube([(side*.166,.057,.77-arm*.016),(px*.87,.018,pz-.084),(px,-.076,pz)],.036,dark,10)
            s.ellipsoid((px,-.087,pz),(.044,.035,.062),dark,14,9)
    if form=='ganesha':
        for side in [-1,1]:
            s.ellipsoid((side*.138,-.011,1.004),(.090,.046,.101),dark,20,12)
        s.tube([(0,-.109,1.029),(0,-.174,.927),(.073,-.19,.863),(.109,-.135,.895)],.048,dark,12)
    if form in ['veera','sudarshana','bhadrakali','ardha','kumara']:
        stick=.32
        s.tube([(stick,-.143,.18),(stick,-.143,1.202)],.019,p['silver'],9)
        for side in [-1,0,1]:
            s.tube([(stick,-.143,1.15),(stick+side*.078,-.143,1.213),
                    (stick+side*.08,-.143,1.284)],.012,p['silver'],8)
    if form=='kumara':
        for a in range(5):
            f=(a-2)*.092
            s.ellipsoid((f,.058,1.012-.52*abs(f)),(.071,.058,.10),dark,14,9)
    if form=='uma':
        s.ellipsoid((.24,-.073,.54),(.120,.088,.237),p['red'],24,16)
        s.ellipsoid((.246,-.091,.80),(.076,.061,.094),dark,22,14)
        s.ellipsoid((.246,-.064,.89),(.069,.051,.070),p['gold'],17,12)
    if form=='annapurna':
        s.ellipsoid((-.226,-.166,.62),(.076,.069,.043),p['gold'],20,12)
        s.tube([(.192,-.134,.59),(.278,-.169,.828)],.012,p['gold'],9)
    garland(s,p,.209,.831,.396,-.17,38)
    s.finish(name+'-renderonly',position).rotation_euler.z=angle


def small_shrine(id,x,y,level,w,d,form,m,angle=math.pi/2,tower='stone'):
    before={o.name for o in bpy.context.scene.objects}
    box(id+'_Carved_Adhisthana',(x,y,level+.115),(w+.50,d+.53,.23),m['trim'],.028)
    doorway(id,x,y,w,d,level+.23,2.84,m,m['granite'])
    roof_tower(id+'_Roof',x,y,level+3.23,w+.17,d+.15,1.64,3,m,metal=tower=='gilt')
    box(id+'_Altar',(x,y+.45,level+.38),(1.48,1.25,.31),m['trim'],.021)
    register(id,(x,y+.44,level+1.13),(x,y-d/2-1.36,level+.06))
    rotate_objects(before,(x,y,level),angle)
    gx,gy=x-.45*math.sin(angle),y+.45*math.cos(angle)
    if form in ['linga','sahasra','vriddha']:
        sacred_linga(id+'_Form',gx,gy,level+.55,m,.82,form)
    else:
        study_figure(id+'_Form',(gx,gy,level+.54),form,m,angle)


def shrine_row(prefix,x,start_y,count,pitch,m,style):
    depth=5.0
    w=(count-1)*pitch+4.21
    cy=start_y+(count-1)*pitch/2
    level=.13
    box(prefix+'_Continuous_Adhisthana',(x+.82,cy,level-.07),(8.6,w,.27),m['trim'],.036)
    box(prefix+'_Back_Wall',(x-2.52,cy,1.67),(.43,w,3.10),m['redstone'] if style=='pancha' else m['granite'],.027)
    box(prefix+'_Continuous_Roof',(x+.67,cy,3.37),(8.88,w+.43,.34),m['redstone'] if style=='pancha' else m['granite'],.034)
    for k in range(count+1):
        y=start_y+(k-.5)*pitch
        pillar(prefix+'_Veranda_Pillar',x+4.77,y,.17,3.04,m,rich=True)
        box(prefix+'_Cell_Partition',(x-.19,y,1.56),(4.25,.28,2.83),m['redstone'] if style=='pancha' else m['granite'],.023)
    for k in range(count):
        y=start_y+k*pitch
        name=prefix+'_%02d'%(k+1)
        box(name+'_Darshan_Pitha',(x-1.03,y,.33),(1.62,1.18,.37),m['trim'],.024)
        sacred_linga(name,x-1.04,y,.53,m,.74)
        if style=='pancha':
            roof_tower(name+'_Sikhara',x-.54,y,3.59,depth*.72,pitch*.83,1.93,4,m,False)
        else:
            box(name+'_Nandi_Low_Plinth',(x+2.68,y,.29),(.98,.91,.26),m['trim'],.031)
            nandi(name+'_Nandi',x+2.68,y,.42,m,.86)
        register(name,(x-1.04,y,1.02),(x+1.1,y,.205))

def wall_block(name,center,length,axis,m):
    x,y=center
    if length<.4:
        return
    def dim(span,depth,height):
        return (span,depth,height) if axis=='x' else (depth,span,height)
    box(name+'_Masonry',(x,y,2.51),dim(length,1.47,5.02),m['wall'],.023)
    for z,w,h in [(.23,1.94,.23),(.78,1.68,.17),(3.72,1.53,.11),(4.63,1.67,.16),
                  (5.06,1.79,.24)]:
        box(name+'_Horizontal_Ledge',(x,y,z),dim(length,w,h),m['trim'],.021)
    n=int(length/3.20)
    step=length/max(1,n)
    for i in range(n):
        loc=(i+.5)*step-length/2
        px,py=(x+loc,y) if axis=='x' else (x,y+loc)
        box(name+'_Crowning_Merlon-renderonly',(px,py,5.31),dim(step*.62,.89,.36),m['wall'],.021)


def prakara(m):
    west,east,south,north=-84.5,74.2,-96.5,100
    for side,axis,offset,lo,hi,gate_at,opening in [
        ('North','x',north,west,east,1.0,7.50),('South','x',south,west,east,-18.6,7.40),
        ('West','y',west,south,north,-17.0,8.60),('East','y',east,south,north,-13.9,10.1)]:
        for start,end in [(lo,gate_at-opening),(gate_at+opening,hi)]:
            mid=(start+end)/2
            wall_block(side+'_Prakara',(mid,offset) if axis=='x' else (offset,mid),end-start,axis,m)
    for name,x,y,w,d,h,n,style,a in [
        ('East_Rajagopura',east,-13.9,20.2,9.3,20.5,7,'ochre',math.pi/2),
        ('West_Brahmaraya_Gopura',west,-17.0,17.2,8.8,15.2,5,'cream',-math.pi/2),
        ('North_Shivaji_Gopura',1.0,north,15.0,8.5,22.3,7,'cream',math.pi),
        ('South_Harihara_Gopura',-18.6,south,14.8,8.3,16.7,5,'cream',0)]:
        gate(name,x,y,.0,w,d,h,n,m,style,a)
        normal=Vector((math.sin(a),-math.cos(a),0))
        register(name,(x,y,2.38),(x+normal.x*(d/2+3.5),y+normal.y*(d/2+3.5),.08))


def southern_panel(m):
    # The south prakara has an independently documented two-giraffe,
    # two-camel procession. The exact block position is kept approximate.
    x,y=12.0,-97.248
    box('Procession_Relief_Stone',(x,y,1.31),(7.52,.24,1.79),m['granite'],.018)
    s=Sculpture()
    s.materials.extend([m['granite'],m['trim'],m['wall']])
    for i,form in enumerate(['giraffe','giraffe','camel','camel']):
        cx=x-2.58+i*1.71
        body_z=1.20 if form=='giraffe' else 1.14
        s.ellipsoid((cx,y-.16,body_z),(.40,.082,.176),1,20,14)
        for j in range(4):
            dx=(j-1.5)*.19
            s.tube([(cx+dx,y-.148,body_z-.08),(cx+dx+.022,y-.155,1.00),
                    (cx+dx-.025,y-.158,.71)],.025,1,9)
        neck_top=1.92 if form=='giraffe' else 1.51
        s.tube([(cx-.26,y-.16,body_z),(cx-.38,y-.16,body_z+.19),(cx-.49,y-.16,neck_top)],.066,1,11)
        s.ellipsoid((cx-.54,y-.163,neck_top),(.123,.068,.065),1,15,9)
        if form=='giraffe':
            for sx in [-1,1]:
                s.tube([(cx-.53+sx*.033,y-.156,neck_top),(cx-.54+sx*.04,y-.155,neck_top+.12)],.018,1,8)
            for d in [-.19,0,.19]:
                s.ellipsoid((cx+d,y-.234,1.23),(.033,.018,.029),2,10,8)
        else:
            s.ellipsoid((cx+.02,y-.157,1.25),(.195,.079,.174),1,16,10)
        s.tube([(cx+.33,y-.165,body_z+.04),(cx+.47,y-.15,body_z-.057),(cx+.53,y-.16,body_z-.153)],.024,1,8)
        hx=cx-.69
        s.ellipsoid((hx,y-.158,1.18),(.055,.036,.065),1,13,8)
        s.tube([(hx,y-.15,1.12),(hx+.014,y-.16,.92),(hx-.016,y-.162,.72)],.034,1,9)
        s.tube([(hx,y-.158,1.04),(hx+.12,y-.159,1.11),(cx-.56,y-.158,neck_top-.05)],.014,1,9)
    for h in [.55,2.12]:
        s.tube([(x-3.66,y-.140,h),(x+3.66,y-.14,h)],.041,1,10)
    s.finish('South_Prakara_Animal_Procession-renderonly')
    register('South_Prakara_Relief',(x,y-.17,1.41),(x,y-3.20,.07))


def awning(name,x,y,z,w,d,m):
    for px in [x-w/2+.26,x+w/2-.26]:
        for py in [y-d/2+.22,y+d/2-.22]:
            box(name+'_Support',(px,py,z+1.42),(.18,.18,2.83),m['steel'],.012)
    profile(name+'_Roof',(x,y,z+2.72),(w,d),
            [(0,1,1),(.16,1.025,1.06),(.49,.98,.47)],m['canopy'])


def covered_gundam(name,x,y,z,m,depth=5.3):
    box(name+'_Stone_Coping',(x,y,z+.24),(6.5,depth,.48),m['trim'],.026)
    box(name+'_Dark_Centre-renderonly',(x,y,z+.482),(5.54,depth-.78,.018),m['water'],.013)
    for sign in [-1,1]:
        for py in [y-depth/2-.17,y+depth/2+.17]:
            pillar(name+'_Roof_Pillar',x+sign*3.5,py,z,2.90,m,True)
        box(name+'_Visitor_Rail',(x+sign*3.12,y,z+.77),(.09,depth,.09),m['steel'],.011)
    box(name+'_Roof',(x,y,z+3.10),(7.68,depth+1.25,.31),m['granite'],.026)
    register(name,(x,y,z+.53),(x+5.6,y,z+.07))


def nallamala(m):
    rng=random.Random(897)
    for cx,cy,r in [(-50,50,14),(-39,-62,16),(35,-57,8),(34,15,10),(54,47,9),
                    (-28,84,8),(31,74,6),(-70,14,6),(-84,69,6),(-78,-72,6)]:
        for i in range(3):
            x=cx+rng.uniform(-r*.46,r*.46)
            y=cy+rng.uniform(-r*.46,r*.46)
            tall=rng.uniform(5.7,9.8)
            cylinder('Nallamala_Tree_Trunk',(x,y,tall*.31),.30,tall*.63,m['bark'])
            for j in range(16):
                a=rng.random()*math.tau
                spread=rng.uniform(.0,4.0)
                zz=tall+rng.uniform(-2.0,1.15)-spread*.29
                sphere('Nallamala_Tree_Crown-renderonly',(x+spread*math.cos(a),y+spread*math.sin(a),zz),
                       (rng.uniform(1.36,2.69),rng.uniform(1.4,2.72),rng.uniform(1.1,2.05)),
                       m['leaves'][j%3],14)
    cols,rows=50,18
    verts=[]
    for j in range(rows):
        y=113+j*7.0
        for i in range(cols):
            x=(i-(cols-1)/2)*8.2
            profile_z=8.0+7.6*math.sin(x*.025+y*.017)+3.7*math.sin(x*.059-y*.021)
            fade=math.sin(math.pi*j/(rows-1))
            z=-.64+max(0,fade*(profile_z+7.5))+rng.uniform(-.7,.7)*fade
            verts.append((x,y,z))
    faces=[(i+j*cols,i+1+j*cols,i+1+(j+1)*cols,i+(j+1)*cols)
           for j in range(rows-1) for i in range(cols-1)]
    data=bpy.data.meshes.new('Nallamala Hill Profile')
    data.from_pydata(verts,[],faces)
    for surface in m['leaves']:
        data.materials.append(surface)
    for face in data.polygons:
        face.material_index=rng.choices([0,1,2],[4,9,3])[0]
    obj=bpy.data.objects.new('Terrain_Nallamala_Far_Ridges-renderonly',data)
    bpy.context.collection.objects.link(obj)


def build():
    clear_scene()
    m={
        'granite':material('Srisailam Grey Granite',(.247,.206,.166)),
        'trim':material('Srisailam Weathered Stone',(.322,.270,.216)),
        'redstone':material('Srisailam Reddish Shrine Stone',(.31,.174,.124)),
        'wall':material('Srisailam Prakara Stone',(.331,.269,.208)),
        'paving':material('Srisailam Flag Paving',(.250,.224,.182)),
        'dark':material('Srisailam Polished Dark Stone',(.045,.038,.033),.39),
        'cream':material('Srisailam Lime Plaster',(.65,.602,.431)),
        'cream_shadow':material('Srisailam Lime Relief Shade',(.513,.451,.264)),
        'ochre':material('Srisailam East Ochre Stucco',(.69,.491,.231)),
        'gopura_shadow':material('Srisailam Ochre Relief Shade',(.48,.320,.122)),
        'gold':material('Srisailam Vimana Gilding',(.598,.352,.074),.35,.30),
        'gold_hi':material('Srisailam Sunlit Brass',(.733,.477,.149),.32,.28),
        'steel':material('Srisailam Queue Rail',(.087,.155,.162),.55,.32),
        'canopy':material('Srisailam Rust Red Cover',(.34,.094,.057),.7),
        'canopy_pale':material('Srisailam Pavilion Roof',(.34,.333,.247)),
        'water':material('Srisailam Covered Spring',(.048,.098,.071),.48),
        'lawn':material('Srisailam Garden Surface',(.125,.183,.093)),
        'earth':material('Srisailam Ground Earth',(.242,.219,.166)),
        'bark':material('Nallamala Bark',(.12,.079,.043)),
        'leaves':[material('Nallamala Foliage '+str(i),c) for i,c in enumerate(
            [(.091,.142,.065),(.135,.202,.080),(.188,.254,.097)])],
    }
    for key in ['paving','granite','trim','redstone','wall']:
        mat=m[key]
        shader=mat.node_tree.nodes.get('Principled BSDF')
        add_stone_detail(mat,shader,tuple(shader.inputs['Base Color'].default_value))
    box('Ground_Nallamala_Plateau',(0,0,-.66),(430,420,1.20),m['earth'])
    box('Ground_Main_Enclosure',(-4.9,1.4,-.168),(159.5,198,.33),m['paving'],.012)
    box('Ground_Outer_Perimeter_Promenade',(-5,.2,-.126),(195,231,.18),m['paving'],.012)
    north_y,south_y=37.8,-36.6
    for name,cx,cy,w,d in [('North_Lawn',-34,68,49,40),('South_Lawn',-10,-66,51,39),
                           ('Southwest_Lawn',-66,-74,27,35),('Southeast_Lawn',54,-68,28,41)]:
        box(name,(cx,cy,.023),(w,d,.050),m['lawn'],.022)
    prakara(m)
    southern_panel(m)

    for name,x,y,w,d in [('North_Sala_Mandapa',15,north_y,53,5.45),
                        ('South_Sala_Mandapa',8,south_y,64,5.60),
                        ('Western_Terrace_Cover',-48,23,30,18),
                        ('South_Service_Mandapa',49,-71,19,27)]:
        mandapa(name,x,y,w,d,.17,3.25,7 if w>40 else 5,4 if d>11 else 2,m)
    awning('South_Queue_Roof',-.6,-30.8,.0,78,3.4,m)
    awning('East_Queuing_Approach',88.4,-13.9,.0,18.2,6.8,m)

    y=-13.9
    # Clear through-route beside the monumental bull. It faces the lingam to the west.
    mandapa('Nandi_Mandapa',50.6,y,15.8,13.0,.205,4.04,7,6,m)
    mandapa('Veerasiro_Mandapa',35.34,y,13.6,12.14,.205,3.59,4,4,m)
    mandapa('Mallikarjuna_Mukha_Mandapa',21.54,y,12.62,12.61,.205,3.66,4,4,m,True)
    box('Nandi_Stone_Dais',(50.6,y,.49),(5.57,4.08,.54),m['trim'],.062)
    nandi('Nandimandapa_Monolithic_Bull',50.6,y,.76,m,4.28)
    register('Nandimandapa',(50.6,y,2.56),(55.4,y-2.64,.27))
    register('Veerasiromandapa',(35.3,y,.46),(39.2,y-1.45,.27))
    for px in [30.1,39.1]:
        for side in [-1,1]:
            nandi('Veerasiro_Roof_Nandi',px,y+side*4.85,3.99,m,.74)

    box('Mallikarjuna_Sanctum_Plinth',(9.37,y,.119),(10.38,10.1,.238),m['granite'],.037)
    east_opening('Mallikarjuna_Garbhagriha',9.37,y,10.1,9.08,.207,3.72,m)
    roof_tower('Mallikarjuna_Gold_Vimana',9.37,y,4.23,9.65,8.56,8.2,8,m,True)
    mandapa('Mallikarjuna_Antarala',15.86,y,3.76,5.58,.205,3.38,2,2,m)
    for side in [-1,1]:
        pillar('Mukha_Sanctum_Engaged_Torana',14.31,y+side*1.33,.207,2.74,m,True)
    arch_details('Mallikarjuna_Silverwork_Border',13.02,y,.335,1.89,2.12,m)
    box('Mallikarjuna_Octagonal_Darshan_Base',(8.60,y,.407),(1.86,1.86,.40),m['trim'],.041)
    sacred_linga('Mallikarjuna_Photographed_Ritual_Study',8.48,y,.62,m,1.04,'mallikarjuna')
    box('Mukha_Mandapa_Interior_Nandi_Plinth',(19.76,y,.31),(1.63,1.04,.23),m['trim'],.024)
    nandi('Mukha_Mandapa_Interior_Nandi',19.76,y,.43,m,1.27)
    register('Mallikarjuna',(8.48,y,1.31),(11.66,y,.28))

    for id,x,sy,form in [('Ratnagarbha_Ganapati',17.12,-17.96,'ganesha'),
                        ('Sudarshana_Veerabhadra',16.92,-10.14,'sudarshana'),
                        ('Bhadrakali',19.21,-9.68,'bhadrakali')]:
        box(id+'_Mandapa_Plinth',(x,sy,.376),(1.50,1.29,.342),m['redstone'],.028)
        study_figure(id+'_Sculpture',(x,sy,.55),form,m)
        register(id,(x,sy,1.53),(x+1.79,sy,.28))

    # The raised Devi court occupies the west end of the south-central axis.
    terrace=2.05
    box('Bhramaramba_West_Terrace',(-64.5,-17.0,terrace/2),(37.8,25.5,terrace),m['granite'],.034)
    stone_steps('Bhramaramba_Front_Ascent',-45.45,-17.0,5.78,.004,terrace,12,.47,m)
    before={o.name for o in bpy.context.scene.objects}
    stone_steps('Bhramaramba_West_Ascent',-83.40,-17.0,3.51,.004,terrace,12,.47,m)
    rotate_objects(before,(-83.40,-17.0,0),math.pi)
    for sy in [-1,1]:
        box('Bhramaramba_Stair_Balustrade',(-43.01,-17.0+sy*3.14,.67),(5.36,.38,1.33),m['trim'],.025)
        mandapa('Bhramaramba_Enclosure_Veranda',-62.5,-17.0+sy*10.77,35.0,3.20,
                terrace+.015,2.81,8,2,m)
    gate('Bhramaramba_Mandapa_Dwaram',-47.88,-17.0,terrace,8.1,4.7,4.35,3,m,'cream',math.pi/2)
    mandapa('Bhramaramba_Eastern_Porch',-60.65,-17.0,16.1,13.1,terrace+.015,3.63,4,4,m)
    sri_chakra(-62.14,-17.0,terrace+.025,m)
    east_opening('Bhramaramba_Garbhagriha',-72.24,-17,10.67,10.45,terrace+.02,3.75,m)
    roof_tower('Bhramaramba_Dvitala_Vimana',-72.24,-17,terrace+3.96,10.05,9.73,4.85,2,m)
    for sx,sy,niche,a in [(-67.2,-17.0,'Durga',math.pi/2),(-77.32,-17,'Vaishnavi',-math.pi/2),
                          (-72.24,-12.22,'Brahmi',math.pi)]:
        study_figure('Bhramaramba_Vimana_'+niche,(sx,sy,terrace+5.01),'rajarajeshwari',m,a)
    box('Bhramaramba_Darshan_Dais',(-73.63,-17,terrace+.41),(1.71,1.95,.81),m['trim'],.035)
    arch_details('Bhramaramba_Gilded_Prabhavali',-73.75,-17,terrace+.83,1.64,2.15,m)
    queen_study((-73.48,-17,terrace+.83))
    anchor('Deity_Bhramaramba',(-73.44,-17,terrace+2.14))
    anchor('Bhramaramba_Darshan_Landing',(-70.23,-17,terrace+.095))
    anchor('Sanctum_Lamp_Position',(-71.51,-16.60,terrace+2.61))
    lamp=material('Srisailam Sacred Lamp',(.66,.31,.063),.48,.0,1.8)
    for x,sy,z in [(-72.3,-18.45,terrace+.02),(-72.3,-15.55,terrace+.02),(9.1,-15.65,.23)]:
        create_deepam('Srisailam_Deepam',(x,sy,z),m['gold_hi'],lamp)

    # Documented groups share continuous porticoes. Individual cells use model order.
    shrine_row('Pancha_Sivalaya',-3.65,10.0,5,4.27,m,'pancha')
    shrine_row('Nava_Brahma',-24.2,-12.7,9,3.67,m,'nava')
    for id,x,sy,w,d,form,ang in [
        ('Vriddha_Mallikarjuna',19.5,10.9,6.0,6.45,'vriddha',math.pi),
        ('Sahasra_Lingeswara',19.5,18.8,5.4,5.3,'sahasra',0),
        ('Ardhanariswara',10.7,21.8,5.0,5.2,'ardha',math.pi/2),
        ('Jwala_Veerabhadra',-3.72,33.0,5.2,5.5,'veera',math.pi/2),
        ('Kumaraswamy',-24.2,20.0,5.4,5.2,'kumara',math.pi/2),
        ('Uma_Maheswara',19.6,40.3,5.25,5.3,'uma',0),
        ('Rajarajeswara',29.1,41.5,5.25,5.3,'linga',-math.pi/2),
        ('Rajarajeswari',35.6,41.5,5.25,5.3,'rajarajeshwari',-math.pi/2),
        ('Annapurna',-9.9,-43.0,5.3,5.5,'annapurna',math.pi/2),
        ('Akkamahadevi',-33.0,-8.2,4.7,4.5,'akkamahadevi',-math.pi/2),
        ('Hema_Reddy_Mallamma',-33.0,-14.55,4.7,4.5,'mallamma',-math.pi/2),
    ]:
        small_shrine(id,x,sy,0,w,d,form,m,ang)
    covered_gundam('Mallika_Gundam',35,26.6,.0,m)
    covered_gundam('Manohara_Gundam',21.6,-29.2,.0,m)
    covered_gundam('Rudhira_Gundam',-75.0,-8.49,terrace,m)
    box('Bhringi_Stone_Pedestal',(68.0,-20.65,.32),(1.68,1.48,.61),m['trim'],.031)
    study_figure('Bhringi_Iconographic_Study',(68.0,-20.65,.63),'bhringi',m)
    register('Bhringi',(68.0,-20.65,1.40),(70.01,-20.65,.07))
    bx,by=23.1,-5.15
    profile('Mallikarjuna_Balipitha_Pedestal',(bx,by,.02),(2.65,2.23),
            [(0,1,1),(.22,1,1),(.31,.94,.94),(.66,.74,.74),(.75,.93,.93)],m['trim'])
    roof_tower('Mallikarjuna_Balipitha_Miniature_Shrine',bx,by,.76,1.81,1.51,.89,2,m)
    register('Mallikarjuna_Balipitha',(bx,by,1.25),(bx+2.70,by,.07))
    mandapa('Sayana_Mirror_Hall',54.0,75.8,9.2,9.1,.18,3.53,4,4,m,True)
    box('Sayana_Mandapa_Back',(50.1,75.8,1.97),(.37,8.8,3.58),m['granite'],.028)
    register('Sayana_Mandapa',(54.0,75.8,1.54),(61.0,75.8,.08))
    register('Bhramaramba_Vimana_Reliefs',(-67.34,-17,terrace+5.51),(-55.83,-17,terrace+.07))

    # Secondary access surface, surrounding vegetation and outer parade ground.
    for sx in [-1,1]:
        for py in [-66,-50,-41,53,66,86]:
            box('Prakara_Edge_Path',(-5+sx*69,py,.013),(4.9,7.3,.032),m['paving'],.012)
    nallamala(m)
    anchor('Spawn_Point',(88,-13.9,.075))
    anchor('Arrival_Facing',(65,-13.9,.075))
    # Rotate local axes back to the approximate true north in satellite imagery.
    rotate_objects(set(),(0,0,0),math.radians(-5.7))


if __name__=='__main__':
    build()
    if not globals().get('DEFER_GLB_EXPORT',False):
        prepare_scene()
        finish('srisailam_bhramaramba')
