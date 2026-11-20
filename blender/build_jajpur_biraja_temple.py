"""Present-day Biraja precinct, from the aerial footprint and IGNCA survey."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bmesh
import bpy
from mathutils import Matrix, Vector

import common_geometry as geom
import common_materials as mats


round_meshes = {}


def add_mesh(name, vertices, faces, material, smooth=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if smooth:
        for face in mesh.polygons:
            face.use_smooth = True
    return obj


def box(name, center, dim, material, edge=0):
    x, y, z = (v/2 for v in dim)
    obj = add_mesh(name, [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
                          (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],
                   [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)], material)
    obj.location = center
    if edge:
        bevel = obj.modifiers.new("Dressed edges", "BEVEL")
        bevel.width = edge
        bevel.segments = 2
    return obj


def bulb(name, center, radii, material):
    if material.name not in round_meshes:
        rounded = bmesh.new()
        bmesh.ops.create_uvsphere(rounded, u_segments=16, v_segments=10, radius=1)
        mesh = bpy.data.meshes.new(material.name + "_Sphere")
        rounded.to_mesh(mesh)
        rounded.free()
        mesh.materials.append(material)
        for face in mesh.polygons:
            face.use_smooth = True
        round_meshes[material.name] = mesh
    obj = bpy.data.objects.new(name, round_meshes[material.name])
    bpy.context.collection.objects.link(obj)
    obj.location, obj.scale = center, radii
    return obj


def beam(name, a, b, radius, material):
    delta = Vector(b)-Vector(a)
    obj = bulb(name, (Vector(a)+Vector(b))*.5, (radius,radius,delta.length*.5+radius*.3), material)
    obj.rotation_euler = delta.to_track_quat("Z","Y").to_euler()
    return obj


def carving_line(name, points, size, material):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=size
    curve.bevel_resolution=2
    spline=curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point,coords in zip(spline.points,points):
        point.co=(*coords,1)
    obj=bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def anchor(name, coords, turns=0):
    obj=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(obj)
    obj.location=coords
    obj.rotation_euler.z=turns
    return obj


def landmark(key, sight, approach):
    anchor("Biraja_"+key,sight)
    if approach is not None:
        anchor("Landing_"+key,approach)


def floor(name,x0,x1,y0,y1,z,m,depth=.18):
    return box(name,((x1+x0)/2,(y1+y0)/2,z-depth/2),(x1-x0,y1-y0,depth),m)


def steps(name,outer,y,z,height,count,tread,width,m):
    for i in range(count):
        rise=height*(i+1)/count
        box(name+str(i+1),(outer-(i+.5)*tread,y,z+rise*.5),(tread,width,rise),m)


def pass_wall(name,x,y,breadth,depth,z,height,door,m):
    side=(breadth-door)/2
    for sign in (-1,1):
        box(name+"_Jamb",(x,y+sign*(door+side)/2,z+height/2),(depth,side,height),m,.02)
    lintel=min(.68,height*.24)
    box(name+"_Lintel",(x,y,z+height-lintel*.5),(depth,door,lintel),m,.018)


def chamber(name,x,y,width,depth,z,height,door,m,back=True,floor_at=None):
    if floor_at is not None:
        floor(name+"_Floor",x-width/2,x+width/2,y-depth/2,y+depth/2,floor_at,m)
    side_y=depth/2-.19
    for side in (-1,1):
        box(name+"_Lateral",(x,y+side_y*side,z+height/2),(width,.38,height),m)
    if back:
        box(name+"_Rear",(x-width/2+.19,y,z+height/2),(.38,depth,height),m)
    pass_wall(name+"_Entry",x+width/2-.20,y,depth,.4,z,height,door,m)


def pillar(name,x,y,z,height,span,m,trim):
    for i,(h,w) in enumerate(((.17,1.65),(.16,1.24),(height-.64,1),(.16,1.26),(.15,1.64))):
        box(f"{name}_{i}",(x,y,z+h/2),(span*w,span*w,h),trim if i in (0,4) else m,.022)
        z+=h


def pavilion(name,x,y,width,depth,z,height,m,rows=3):
    floor(name+"_Plinth",x-width/2,x+width/2,y-depth/2,y+depth/2,z,m["paving"])
    for i in range(rows):
        xx=x+(i/(rows-1)-.5)*(width-.8)
        for sign in (-1,1):
            pillar(name+"_Post",xx,y+sign*(depth/2-.6),z,height,.39,m["plaster"],m["trim"])
    floor(name+"_Roof",x-width/2-.21,x+width/2+.21,y-depth/2-.22,y+depth/2+.22,z+height+.21,m["plaster"],.24)
    floor(name+"_Painted_Fascia",x-width/2-.33,x+width/2+.33,y-depth/2-.30,y+depth/2+.30,
          z+height+.285,m["blue"],.10)


def band_tower(name,x,y,z,width,height,m,tiers=6,painted=False):
    section=height/(tiers+.7)
    for i in range(tiers):
        w=width*(1-i*.085)
        floor(name+"_Pidha",x-w/2,x+w/2,y-w/2,y+w/2,z+section*(i+1),m["plaster"],section)
        ledge=w+.14
        floor(name+"_Moulded_Eave",x-ledge/2,x+ledge/2,y-ledge/2,y+ledge/2,
              z+section*(i+1)+.065,m["green"] if painted and i%2 else m["trim"],.11)
        if painted:
            for side in (-1,1):
                for j in (-1.0,0,1.0):
                    bulb("OrnamentDetail_Bagalamukhi_Stucco", (x+side*w*.5,y+j*w*.26,z+section*(i+.49)),
                         (.055,.17,.22),m["ochre"] if i%2 else m["red"])
    bulb(name+"_Finial",(x,y,z+height-.22),(.22,.22,.40),m["green"])


def rekha_deula(x,y,z,m):
    # Pancharatha: corner, intermediate and axial offsets on each face.
    quadrant=[(1.02,0),(1.02,.19),(.91,.19),(.91,.44),(.81,.44),(.81,.81),(.44,.81),(.44,.91),(.19,.91),(.19,1.02)]
    outline=[(a*math.cos(i*math.pi/2)-b*math.sin(i*math.pi/2),
              a*math.sin(i*math.pi/2)+b*math.cos(i*math.pi/2)) for i in range(4) for a,b in quadrant]
    n=len(outline)
    vertices=[]
    for row in range(27):
        t=row/26
        span=4.10*(1-.61*t**2.52)
        vertices.extend((x+span*a,y+span*b,z+t*13.65) for a,b in outline)
    faces=[(r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i) for r in range(26) for i in range(n)]
    faces.append(tuple(range(26*n,27*n)))
    add_mesh("Biraja_Curved_Pancharatha_Gandi",vertices,faces,m["plaster"])
    for side in (-1,1):
        for i in range(4):
            scale=4.19*(1-.61*(.21+i*.14)**2.52)
            h=z+2.65+i*1.98
            for a,b in ((side,0),(0,side)):
                bulb("Biraja_Raha_Projecting_Lion",(x+a*scale,y+b*scale,h),(.38,.38,.26),m["trim"])
                bulb("Biraja_Raha_Projecting_Lion_Head",(x+a*(scale+.30),y+b*(scale+.30),h+.1),(.16,.16,.18),m["trim"])
    bulb("Biraja_Beki",(x,y,z+13.72),(1.25,1.25,.54),m["plaster"])
    bulb("Biraja_Amalaka",(x,y,z+14.37),(1.86,1.86,.45),m["green"])
    for i in range(36):
        a=i*math.tau/36
        bulb("Biraja_Amalaka_Fluting",(x+1.70*math.cos(a),y+1.70*math.sin(a),z+14.43),
             (.16,.16,.34),m["trim"] if i%3==0 else m["green"])
    bulb("Biraja_Kalasha",(x,y,z+14.94),(.54,.54,.50),m["ochre"])
    box("Biraja_Dhvaja_Shaft",(x,y,z+15.44),(.09,.09,1.15),m["metal"])
    add_mesh("RenderOnly_Biraja_Flag",[(x,y,z+15.92),(x-.93,y+.14,z+15.70),(x,y,z+15.43)],
             [(0,1,2),(2,1,0)],m["red"])


def linga(name,x,y,z,material,r=.27,h=.48,carvings=False):
    bulb(name+"_Yoni",(x,y,z+.13),(r*2.3,r*1.83,.155),material)
    box(name+"_Spout",(x,y+r*1.75,z+.18),(.48*r,1.72*r,.16),material)
    bulb(name+"_Linga",(x,y,z+.18+h*.47),(r,r,h*.52),material)
    if carvings:
        for layer in range(3):
            for j in range(8):
                a=j*math.tau/8
                bulb("OrnamentDetail_Sahasralinga_Miniatures",(x+r*.96*math.cos(a),y+r*.96*math.sin(a),
                     z+.23+layer*h*.17),(.023,.023,.047),material)


def lion(name,x,y,z,m,scale=1):
    bulb(name+"_Haunch",(x-.20*scale,y,z+.24*scale),(.45*scale,.27*scale,.27*scale),m["ochre"])
    bulb(name+"_Chest",(x+.11*scale,y,z+.38*scale),(.32*scale,.28*scale,.34*scale),m["ochre"])
    bulb(name+"_Mane",(x+.20*scale,y,z+.67*scale),(.28*scale,.29*scale,.29*scale),m["dark"])
    bulb(name+"_Face",(x+.37*scale,y,z+.68*scale),(.20*scale,.20*scale,.23*scale),m["ochre"])
    bulb(name+"_Muzzle",(x+.50*scale,y,z+.625*scale),(.13*scale,.15*scale,.09*scale),m["trim"])
    for side in (-1,1):
        beam(name+"_Foreleg",(x+.23*scale,y+side*.17*scale,z+.48*scale),
             (x+.38*scale,y+side*.18*scale,z+.08*scale),.092*scale,m["ochre"])
        bulb(name+"_Eye",(x+.49*scale,y+side*.08*scale,z+.73*scale),(.027*scale,.026*scale,.025*scale),m["dark"])
        bulb(name+"_Paw",(x+.42*scale,y+side*.18*scale,z+.06*scale),(.15*scale,.09*scale,.07*scale),m["ochre"])


def biraja_murti(x,y,z,m):
    """Study of the Trust's published iconographic model and stated attributes."""
    c=m["idol"]
    def p(depth,lateral,height):
        return x+depth,y+lateral,z+height
    bulb("Deity_Biraja",p(0,0,.15),(.44,.96,.15),c)
    bulb("Mahisha_Buffalo_Body",p(.08,.20,.49),(.26,.69,.31),c)
    bulb("Mahisha_Lowered_Neck",p(.15,-.27,.32),(.24,.39,.16),c)
    bulb("Mahisha_Lowered_Head",p(.21,-.57,.26),(.24,.30,.19),c)
    bulb("Mahisha_Muzzle",p(.31,-.72,.18),(.22,.19,.09),c)
    for s in (-1,1):
        carving_line("Mahisha_Horn",[p(.25+.12*s,-.55,.32),p(.31+.13*s,-.61,.46),p(.39+.14*s,-.66,.48)],.035,c)
        beam("Mahisha_Folded_Leg",p(.02+s*.16,.26,.43),p(.11+s*.13,.39,.19),.089,c)
        bulb("Mahisha_Hoof",p(.13+s*.15,.48,.20),(.08,.13,.07),c)
    # Local south is the deity's anatomical right when facing east.
    # The weapon is in the raised right hand, opposite the tail-lifting left hand.
    arm_r=[p(.02,-.15,1.47),p(.11,-.39,1.57),p(.11,-.38,1.93)]
    arm_l=[p(.02,.15,1.45),p(.11,.33,1.22),p(.17,.61,1.31)]
    legs=[([p(0,.08,1.05),p(.03,.13,.72),p(.07,.04,.27)],.112),
          ([p(0,-.08,1.05),p(.07,-.28,.77),p(.14,-.20,.53)],.12)]
    for points,r in [(arm_r,.069),(arm_l,.070)]+legs:
        for a,b in zip(points,points[1:]):
            beam("Biraja_Figure_Limb",a,b,r,c)
        bulb("Biraja_Hand_Or_Foot",points[-1],(r*.77,r*.76,r*.79),c)
    bulb("Biraja_Hip",p(0,-.015,1.04),(.18,.246,.225),c)
    bulb("Biraja_Torso",p(0,0,1.32),(.15,.228,.26),c)
    bulb("Biraja_Neck",p(.012,0,1.59),(.095,.082,.111),c)
    bulb("Biraja_Oval_Face",p(.017,0,1.75),(.118,.126,.166),c)
    bulb("Biraja_Nose",p(.134,0,1.738),(.044,.023,.053),c)
    for side in (-1,1):
        bulb("Biraja_Lid",p(.121,side*.056,1.77),(.018,.038,.011),c)
        bulb("Biraja_Ear",p(.03,side*.135,1.735),(.04,.03,.06),c)
        bulb("Biraja_Earring",p(.063,side*.136,1.68),(.022,.037,.043),m["brass"])
    carving_line("Biraja_Closed_Lips",[p(.120,-.028,1.685),p(.143,0,1.69),p(.122,.029,1.684)],.008,c)
    bulb("Biraja_Tilak",p(.135,0,1.818),(.012,.021,.027),m["red"])
    for i in range(4):
        bulb("Biraja_Crown",p(-.008,0,1.88+i*.077),(.115-i*.014,.144-i*.024,.063),c)
    # Preserve the small crown motifs as sculpted studies.
    bulb("Biraja_Crown_Ganapati",p(.095,0,1.98),(.027,.041,.049),c)
    beam("Biraja_Crown_Ganapati_Trunk",p(.125,0,1.97),p(.131,.018,1.92),.012,c)
    bulb("Biraja_Crown_Yoni",p(.092,-.079,1.90),(.026,.041,.013),c)
    bulb("Biraja_Crown_Linga",p(.111,-.077,1.921),(.018,.016,.033),c)
    carving_line("Biraja_Crown_Crescent",[p(.096,.052,1.92),p(.109,.082,1.903),p(.103,.109,1.923)],.010,c)
    carving_line("Biraja_Crown_Serpent",[p(.057,-.082,2.04),p(.046,-.051,2.09),p(.047,.012,2.10),p(.062,.083,2.066)],.012,c)
    for row in range(3):
        for j in range(19):
            a=j*math.pi/18
            bulb("Biraja_Carved_Hara",p(.094+.042*math.sin(a),(.10+.026*row)*math.cos(a),1.58-.023*row-(.062+.045*row)*math.sin(a)),
                 (.012,.012,.012),m["brass"] if row==0 else c)
    for i in range(8):
        lateral=(i-3.5)*.04
        carving_line("Biraja_Garment_Ridges",
                     [p(.12,lateral-.10,1.48),p(.162,lateral+.055,1.28),p(.139,lateral+.075,1.09),
                      p(.126,lateral+.015,.92),p(.123,lateral-.029,.73),p(.106,lateral+.047,.46)],.013,c)
    carving_line("Mahisha_Raised_Tail",[p(.12,.66,.55),p(.14,.72,.83),p(.16,.76,1.04),p(.18,.72,1.21),
                                      p(.17,.61,1.31)],.030,c)
    beam("Biraja_Trident_Shaft",p(.19,-.51,2.19),p(.23,-.29,.38),.019,m["brass"])
    for j in (-1,0,1):
        carving_line("Biraja_Trident_Prong",[p(.23,-.29,.42),p(.23,-.36+j*.072,.42),
                                          p(.25,-.40+j*.076,.30)],.011,m["brass"])
    for i in range(31):
        a=math.pi*i/30
        bulb("Biraja_Aureole_Bead",p(-.106,.37*math.cos(a),1.63+.54*math.sin(a)),(.029,.030,.034),c)


def main_complex(m):
    # IGNCA records the east-facing three-part temple at 22.75 × 10.8 m.
    floor("Biraja_Continuous_Padmapitha",-4.7,18.05,-5.40,5.40,.36,m["stone"],.36)
    steps("Chandi_East_Steps",29.28,0,0,.36,3,.31,5.1,m["stone"])
    chamber("Biraja_Garbhagriha",0,0,8.55,8.20,.36,4.65,2.58,m["plaster"])
    floor("Biraja_Sanctum_Ceiling",-4.37,4.37,-4.25,4.25,5.16,m["plaster"])
    for x,z in ((-3.85,.84),(-4.0,1.10),(-4.14,1.31)):
        for side in (-1,1):
            floor("Biraja_Pabhaga_Outline",x,4.38,side*4.19-.16,side*4.19+.16,z,m["trim"],.11)
    for side in (-1,1):
        for i,xx in enumerate((-3.51,-2.75,-1.16,0,1.17,2.75,3.51)):
            reach=.30 if i==3 else .18
            box("Biraja_Bada_Ratha",(xx,side*(4.16+reach/2),2.58),(.55,reach,3.50),m["plaster"],.04)
        for z in (1.4,1.65,3.92,4.45,4.63,4.88):
            floor("Biraja_Bada_Horizontal_Moulding",-4.45,4.45,side*4.22-.32,side*4.22+.32,
                  z,m["trim"],.095)
    rekha_deula(0,0,5.16,m)
    chamber("Biraja_Antarala",5.63,0,2.72,4.00,.36,3.79,2.45,m["plaster"],back=False)
    floor("Antarala_Roof",4.04,7.24,-2.21,2.21,4.29,m["plaster"])
    chamber("Biraja_Jagamohana",12.58,0,10.86,10.38,.36,4.0,4.0,m["plaster"],back=False)
    for xx in (8.64,12.55,16.46):
        for yy in (-2.85,2.85):
            pillar("Jagamohana_Red_Pillar",xx,yy,.36,4.04,.42,m["brick"],m["trim"])
    floor("Jagamohana_Ceiling",6.99,18.14,-5.32,5.32,4.67,m["plaster"])
    band_tower("Jagamohana",12.55,0,4.62,10.4,4.76,m,tiers=7)
    pavilion("Chandi_Mandapa",23.20,0,10.30,11.15,.36,3.80,m)
    for i in range(3):
        y0=-4.7+i*3.12
        ripple=[]
        for j in range(21):
            a=j*math.pi/20
            ripple.append((28.45,y0+.02+1.4*j/10,3.17+.48*math.sin(a)+.065*math.sin(a*9)))
        carving_line("Chandi_Cusped_Arch",ripple,.076,m["trim"])
    biraja_murti(-1.0,0,.36,m)
    anchor("Sanctum_Lamp_Position",(.6,-.9,2.14))
    for yy in (-1.24,1.24):
        lamp(-.21,yy,.36,m)
    landmark("main",(-.93,0,1.64),(2.35,0,.36))
    landmark("antarala",(5.36,0,1.87),(6.76,0,.36))
    landmark("jagamohana",(12.37,0,2.1),(15.2,0,.36))
    landmark("chandi",(22.5,0,1.96),(26.5,0,.36))


def lamp(x,y,z,m):
    bulb("Lamp_Base",(x,y,z+.033),(.101,.101,.033),m["brass"])
    beam("Lamp_Stem",(x,y,z+.04),(x,y,z+.19),.023,m["brass"])
    bulb("Lamp_Bowl",(x,y,z+.187),(.11,.11,.035),m["brass"])
    bulb("Lamp_Flame",(x,y,z+.235),(.035,.035,.063),m["flame"])


def roofed_linga_hall(key,x,y,w,d,count,dense,facing,m,votives=0):
    # The survey records GI sheet roofs, open fronts and varied stone forms.
    floor(key+"_Floor",x-w/2,x+w/2,y-d/2,y+d/2,.15,m["paving"])
    for yside in (-1,1):
        box(key+"_Side",(x,y+yside*(d/2-.10),1.27),(w,.2,2.54),m["plaster"])
    box(key+"_Back",(x-facing*(w/2-.12),y,1.29),(.24,d,2.58),m["plaster"])
    for dy in (-d/2+.20,0,d/2-.20):
        pillar(key+"_Iron_Column",x+facing*(w/2-.13),y+dy,.15,2.74,.18,m["metal"],m["stone"])
    for i in range(21):
        yrow=y+(i/20-.5)*(d+.35)
        z=3.43-abs(yrow-y)*.096
        rib=box(key+"_Corrugated_GI",(x,yrow,z),(w+.44,d/20+.08,.12),m["metal"],.013)
        rib.rotation_euler.x=-math.copysign(.096,yrow-y)
    positions=[]
    for i in range(count):
        rx=(i%8-3.5)*(w-1.24)/8
        ry=(i//8-(math.ceil(count/8)-1)/2)*(d-1.24)/math.ceil(count/8)
        r=.105+((i*13)%7)*.011
        h=.26+((i*17)%8)*.018
        positions.append((x+rx,y+ry,r,h))
    for i,(px,py,r,h) in enumerate(positions):
        linga(key+"_Linga_%02d"%i,px,py,.15,m["dark"],r,h,carvings=i<dense)
    for i in range(votives):
        offset=(i-(votives-1)/2)*.76
        floor(key+"_Votive_Base",x-.27,x+.27,y+offset-.26,y+offset+.26,.53,m["stone"],.30)
        band_tower(key+"_Votive_Pidha",x,y+offset,.55,.53,.62,m,tiers=3)
    landmark(key,(x+facing*(w/2-.5),y,1.52),(x+facing*(w/2+2.02),y,0))


def pidha_shrine(key,x,y,width,z,m,form=True,total=6.9):
    if z > 0:
        floor(key+"_Platform",x-width/2-.24,x+width/2+.24,y-width/2-.25,y+width/2+.25,z,m["stone"],z)
        steps(key+"_Approach",x+width/2+.24+.92,y,0,z,4,.23,min(width-.3,3.15),m["stone"])
    chamber(key,x,y,width,width,z,3.0,min(1.72,width*.50),m["plaster"])
    band_tower(key,x,y,z+3.0,width+.18,total-z-3.0,m)
    if form:
        linga(key,x-.31,y,z,m["dark"])
    landmark(key,(x-.30,y,z+.64),(x+width/2+1.67,y,0))


def isanesvara(x,y,m):
    # The archaeological inventory records a 7.5 × 5.75 m block, an open
    # east-facing mandapa, and the linga one metre below the courtyard.
    chamber("Isanesvara",x,y,4.15,4.20,-.94,4.22,1.65,m["plaster"])
    band_tower("Isanesvara",x,y,3.16,4.39,4.84,m)
    floor("Isanesvara_Open_Mandapa",x+2.07,x+5.46,y-2.87,y+2.87,.12,m["paving"])
    for xx in (x+2.65,x+5.10):
        for yy in (y-2.42,y+2.42):
            pillar("Isanesvara_Mandapa_Post",xx,yy,.12,2.98,.32,m["plaster"],m["trim"])
    floor("Isanesvara_Mandapa_Flat_Roof",x+2.03,x+5.61,y-2.88,y+2.88,3.23,m["plaster"])
    floor("Isanesvara_Lower_Stone_Floor",x-2.07,x+2.07,y-2.10,y+2.10,-.94,m["stone"])
    linga("Isanesvara_Circular_Base",x,y,-.94,m["dark"],.23,.49)
    for i in range(6):
        z=-.94+(i+1)*.94/6
        floor("Isanesvara_Descent_Tread",x+.36+i*.315,x+.675+i*.315,y-.72,y+.72,z,m["stone"],.18)
    landmark("isanesvara",(x,y,-.44),(x+3.5,y,.12))


def bagalamukhi(x,y,m):
    top=.69
    floor("Bagalamukhi_Stair_Platform",x-2.68,x+3.52,y-2.70,y+2.70,top,m["dark"],top)
    steps("Bagalamukhi_Treads",x+4.89,y,0,top,5,.274,3.45,m["stone"])
    chamber("Bagalamukhi",x-.18,y,4.46,4.48,top,3.06,1.50,m["plaster"])
    for yy in (y-2.24,y+2.24):
        pillar("Bagalamukhi_Porch_Post",x+3.10,yy,top,2.55,.38,m["plaster"],m["stone"])
        floor("Bagalamukhi_Lion_Platform",x+3.24,x+4.25,yy-.43,yy+.43,.99,m["dark"])
        lion("Bagalamukhi_Entry_Lion",x+3.64,yy,.98,m,.67)
    floor("Bagalamukhi_Flat_Porch_Roof",x-.62,x+3.86,y-2.82,y+2.82,3.51,m["plaster"],.39)
    for side in (-1,1):
        for i in range(4):
            yy=y+side*(2.54-i*.39)
            box("Bagalamukhi_Painted_Porch_Trim",(x+3.88,yy,3.22+i*.075),(.07,.41,.065),m["green"])
    band_tower("Bagalamukhi_Painted_Tower",x-.47,y,3.76,3.74,4.14,m,tiers=5,painted=True)
    # The documented ten panels are represented, with the route itself open.
    for side in (-1,1):
        for panel in range(5):
            yy=y+side*.89
            z=top+.31+panel*.40
            box("Mahavidya_Carved_Door_Panel",(x+2.23,yy,z),(.12,.31,.33),m["wood"],.016)
            bulb("Mahavidya_Panel_Figure",(x+2.30,yy,z+.02),(.035,.074,.123),m["ochre"])
            bulb("Mahavidya_Panel_Head",(x+2.33,yy,z+.094),(.035,.038,.042),m["ochre"])
    landmark("bagalamukhi",(x+2.72,y,2.46),(x+8.45,y,0))
    landmark("mahavidya_door",(x+2.30,y+.91,2.08),(x+3.15,y,.69))
    # The installed mūrti is concealed in the visit photographs. Leave that
    # identity distinct from the adjacent documented relief studies.
    for offset,key in ((-2.02,"mahamaya"),(-.73,"mahakali"),(1.31,"kapalabhairava")):
        relief("Bagalamukhi_Wall_"+key,x-2.52,y+offset,.94,m["dark"],m,shape="seated",face=-1)
        landmark(key,(x-2.68,y+offset,1.46),(x-3.86,y+offset,0))


def relief(name,x,y,z,stone,m,shape="standing",face=1):
    # The stone form is a stylised relief study, never a fabricated facsimile.
    box(name+"_Stone",(x,y,z+.36),(.18,.76,.95),stone,.057)
    surface=x+face*.108
    bulb(name+"_Head",(surface,y,z+.65),(.062,.091,.105),stone)
    bulb(name+"_Torso",(surface,y,z+.425),(.078,.151,.184),stone)
    for side in (-1,1):
        beam(name+"_Arm",(surface,y+side*.10,z+.52),(surface,y+side*.216,z+.32),.042,stone)
    feet=(-.2,.2) if shape=="seated" else ((0,) if shape=="one_leg" else (-.081,.081))
    for yy in feet:
        beam(name+"_Leg",(surface,y+.035,z+.37),(surface,y+yy,z+.085),.062,stone)
    if shape in ("one_leg","seated"):
        bulb(name+"_Sindoor",(surface+face*.062,y,z+.66),(.028,.056,.067),m["red"])


def nabhi_gaya(x,y,m):
    # Tiled well chamber and the circular wrought ritual enclosure.
    width,depth=6.3,6.7
    chamber("Nabhi_Gaya_Wellhouse",x,y,width,depth,0,3.31,2.12,m["plaster"])
    floor("Nabhi_Gaya_Floor",x-width/2,x+width/2,y-depth/2,y+depth/2,.075,m["paving"])
    floor("Nabhi_Gaya_Roof",x-width/2-.18,x+width/2+.18,y-depth/2-.15,y+depth/2+.15,3.53,m["metal"])
    palette=("tile_blue","tile_green","tile_yellow","trim")
    for i in range(16):
        for j in range(9):
            yy=y-depth/2+.27+i*.41
            box("Nabhi_Gaya_Glazed_Wall_Tile",(x-width/2+.394,yy,.235+j*.34),
                (.028,.405,.335),m[palette[(i*7+j*5+i*j)%4]])
    bulb("Nabhi_Gaya_Rim",(x-.37,y,.405),(1.08,1.08,.385),m["stone"])
    bulb("Nabhi_Gaya_Offerings_Leaf_Bed",(x-.37,y,.696),(.88,.88,.050),m["green"])
    for i in range(32):
        a=i*2.399963
        r=.86*math.sqrt(i/32)
        px=x-.37+r*math.cos(a)
        py=y+r*math.sin(a)
        leaf=bulb("OrnamentDetail_Nabhi_Offering_Leaf",(px,py,.731+.036*math.sin(i*7)),
                  (.127,.059,.016),m["leafshade"] if i%3 else m["green"])
        leaf.rotation_euler.z=a
        if i%3==0:
            bulb("OrnamentDetail_Nabhi_Offering_Flower",(px,py,.759),(.044,.043,.032),
                 m["ochre"] if i%2 else m["red"])
    for z in (.37,.88,1.27,1.61):
        pts=[(x-.37+1.09*math.cos(i*math.tau/64),y+1.09*math.sin(i*math.tau/64),z) for i in range(65)]
        carving_line("Nabhi_Gaya_Silver_Grille_Hoop",pts,.021,m["metal"])
    for i in range(30):
        a=i*math.tau/30
        px=x-.37+1.09*math.cos(a)
        py=y+1.09*math.sin(a)
        box("Nabhi_Gaya_Grille_Bar",(px,py,.937),(.029,.029,1.36),m["metal"])
    landmark("nabhigaya",(x-.37,y,1.10),(x+1.82,y,.075))


def boundary(m):
    # North and south limits are off the main axis and all four paths begin at
    # different offsets. Footprint fits the present satellite image.
    west,east,south,north=-31.4,56.8,-34.0,44.8
    for key,x,y,span,axis in (
        ("west_gate",west,-1.9,3.70,"x"),("simhadwara",east,0,5.1,"x"),
        ("north_gate",21.8,north,3.40,"y"),("south_gate",15.9,south,3.55,"y"),
    ):
        if axis=="x":
            for lo,hi in ((south,y-span/2),(y+span/2,north)):
                floor("Prakara_"+key,x-.38,x+.38,lo,hi,2.96,m["plaster"],2.96)
                floor("Prakara_Coping",x-.55,x+.55,lo,hi,3.16,m["trim"],.20)
        else:
            for lo,hi in ((west,x-span/2),(x+span/2,east)):
                floor("Prakara_"+key,lo,hi,y-.38,y+.38,2.96,m["plaster"],2.96)
                floor("Prakara_Coping",lo,hi,y-.55,y+.55,3.16,m["trim"],.20)
        if key=="simhadwara":
            simhadwara(x,y,m)
        else:
            for sign in (-1,1):
                xx=x if axis=="x" else x+sign*(span/2+.31)
                yy=y+sign*(span/2+.31) if axis=="x" else y
                box(key+"_Stone_Post",(xx,yy,1.55),(.69,.69,3.10),m["stone"],.06)
            roof=(1.2,span+1.8,.26) if axis=="x" else (span+1.8,1.2,.26)
            box(key+"_Gate_Lintel",(x,y,3.17),roof,m["trim"],.025)
            dx,dy=(2.6,0) if key=="west_gate" else (0,-2.5 if key=="north_gate" else 2.5)
            landmark(key,(x,y,2.06),(x+dx,y+dy,0))
    # Model the ground around the sunken Isanesvara chamber as four slabs.
    hole=(3.82,7.40,29.70,33.66)
    floor("Ground_Main_South",-42,68,-43,hole[2],0,m["paving"],1.20)
    floor("Ground_Main_North",-42,68,hole[3],54,0,m["paving"],1.20)
    floor("Ground_Main_West",-42,hole[0],hole[2],hole[3],0,m["paving"],1.20)
    floor("Ground_Main_East",hole[1],68,hole[2],hole[3],0,m["paving"],1.20)
    anchor("Spawn_Point",(48,0,.0))
    anchor("Arrival_Facing",(25,0,.0))


def simhadwara(x,y,m):
    height=4.4
    for s in (-1,1):
        yy=y+s*3.30
        floor("Simhadwara_Weighty_Base",x-2.64,x+2.64,yy-.70,yy+.70,.42,m["stone"],.42)
        box("Simhadwara_Pier",(x,yy,2.40),(3.55,1.13,4.0),m["plaster"],.06)
        for j,z in enumerate((.49,.67,3.36,3.67,3.89)):
            floor("Simhadwara_Moulding"+str(j),x-1.91,x+1.91,yy-.68,yy+.68,z,m["trim"],.13)
        lion("Simhadwara_Lion",x+2.13,yy,.51,m,.92)
    floor("Simhadwara_Gate_Roof",x-2.27,x+2.27,y-4.09,y+4.09,height,m["plaster"],.66)
    band_tower("Simhadwara_Gate_Pidha",x,y,height,5.18,2.78,m,tiers=5)
    # Preserve the lintel's slab proportions and weathered stone as a study.
    box("Bhikari_Das_Inscription_Stone",(x+2.34,y,4.13),(.16,2.44,.57),m["dark"],.018)
    landmark("simhadwara",(x,y,3.00),(x-4.4,y,0))
    landmark("bhikari_das_lintel",(x+2.42,y,4.13),(x+5.25,y,0))
    plaque("East_Gate_Wall_Fragment",x-.45,y-7.14,1.21,m["stone"])
    landmark("gate_wall_fragment",(x-.55,y-7.14,1.38),(x-2.97,y-7.14,0))


def plaque(name,x,y,z,m,turn=0,width=.85,height=.55):
    obj=box(name,(x,y,z),(.115,width,height),m,.031)
    obj.rotation_euler.z=turn


def dola_mandapa(x,y,m):
    floor("Dola_Raised_Pitha",x-2.49,x+2.49,y-2.16,y+2.16,.59,m["trim"],.59)
    steps("Dola_Mandapa_Steps",x+3.51,y,0,.59,4,.255,3.46,m["stone"])
    for yy in (y-1.15,y+1.15):
        pillar("Dola_Arch_Post",x-.52,yy,.59,1.98,.34,m["plaster"],m["trim"])
        lion("Dola_Parapet_Lion",x+1.92,yy,.59,m,.51)
    pts=[]
    for j in range(30):
        a=j*math.pi/29
        r=1.20+.07*math.cos(a*12)
        pts.append((x-.52,y+r*math.cos(a),2.54+r*.75*math.sin(a)))
    carving_line("Dola_White_Cusped_Arch",pts,.14,m["plaster"])
    landmark("dola",(x-.40,y,2.38),(x+1.05,y,.59))


def paired_reliefs(x,y,m):
    floor("Bhairavi_Kali_Platform",x-.72,x+.71,y-1.15,y+1.15,.38,m["stone"])
    box("Bhairavi_Kali_Alcove_Back",(x-.20,y,1.42),(.34,2.42,2.43),m["plaster"])
    relief("Ekapaada_Bhairavi",x+.028,y-.47,.34,m["dark"],m,"one_leg")
    relief("Dvipada_Kali",x+.02,y+.48,.34,m["dark"],m,"seated")
    landmark("ekapada_bhairavi",(x+.13,y-.47,1.0),(x+2.4,y-.54,0))
    landmark("dvipad_kali",(x+.13,y+.48,1.0),(x+2.4,y+.59,0))


def courtyard_paving(m):
    # Narrow joints and weathered blocks visible in the paved approach photos.
    paving=m["paving"]
    warm=mats.create_sandstone("Biraja_Paving_Warm_Blocks",(.36,.275,.201,1),roughness=.97)
    worn=mats.create_sandstone("Biraja_Paving_Worn_Blocks",(.29,.245,.202,1),roughness=.98)
    materials=(paving,paving,paving,warm,worn)
    for row in range(9):
        y=(row-4)*1.37
        for column in range(30):
            x=16.6+column*1.32 + .62*(row%2)
            # Lower continuous collision surface; the thin slabs are visual.
            z=.012
            floor("RenderOnly_Approach_Paving_Block",x-.644,x+.644,y-.66,y+.66,z,
                  materials[(column*7+row*13+column*row)%len(materials)],.017)


def perimeter_features(m):
    # Present-day roof footprints visible in the aerial. Anonymous buildings
    # are retained as architecture without assigning them shrine identities.
    for name,x,y,w,d,h in (
        ("Northwest_Sheet_Roof", -25,28.1,10.75,11.2,3.6),
        ("North_Perimeter_Rooms", 20.3,40.0,16.5,5.7,3.38),
        ("East_Row_Enclosure", 50.3,19,5.1,10.3,3.23),
        ("Southwest_Roof", -10.4,-24.6,11.5,10,3.12),
        ("South_Row_Late_Roof", 28.2,-27.2,23.4,10.2,3.26),
        ("South_East_Service_Room", 48.0,-27.6,7.1,6.5,3.10),
    ):
        floor(name+"_Foundation",x-w/2,x+w/2,y-d/2,y+d/2,.12,m["stone"])
        box(name+"_Walls",(x,y,h/2),(w,d,h),m["plaster"])
        floor(name+"_Ribbed_Roof",x-w/2-.20,x+w/2+.20,y-d/2-.2,y+d/2+.2,h+.24,m["metal"],.32)
    for x,y,r in ((-8.7,15.0,3.3),(25.3,31.1,4.4),(38.0,-24.8,3.4),(-9.0,36.2,3.4)):
        # Branched rounded crown, with split-trunk stone-platform tree toward Dola.
        beam("Courtyard_Tree_Trunk",(x,y,.0),(x,y,4.53),r*.13,m["wood"])
        for i in range(9):
            a=i*math.tau/9
            dx=r*.62*math.cos(a)
            dy=r*.64*math.sin(a)
            hz=4.42+.55*math.sin(i*3.4)
            beam("Courtyard_Tree_Branch",(x,y,2.50),(x+dx,y+dy,hz),r*.034,m["wood"])
            for j in range(5):
                t=j*2.399963+a
                radius=r*(.29+j*.012)
                bulb("Tree_Canopy_Cluster",(x+dx+radius*.83*math.cos(t),
                     y+dy+radius*.76*math.sin(t),hz+.35+.43*math.cos(i+j*1.37)),
                     (radius,radius*.85,radius*.68),m["leafshade"] if (i+j)%3 else m["green"])
    x,y=25.3,31.1
    bulb("Sacred_Tree_Stone_Pitha",(x,y,.24),(1.75,1.77,.25),m["stone"])
    for j in range(20):
        a=j*math.tau/20
        tx=x+1.5*math.cos(a)
        ty=y+1.23*math.sin(a)
        beam("OrnamentDetail_Sacred_Tree_Vow_Cloth",(tx,ty,2.56),(tx+.12,ty,2.04),.033,
             m["red"] if j%3 else m["ochre"])
    landmark("sacred_tree",(x,y,1.62),(x,y-2.8,0))


def epigraphy(m):
    # Trust locations for all five surviving records. The fragmented text on
    # three pieces is undeciphered. Do not carve invented letters into them.
    plaque("Chodaganga_Lamp_Grant_Stone",8.30,-5.29,1.57,m["stone"],math.pi/2)
    landmark("chodaganga_record",(8.30,-5.42,1.57),(8.30,-7.42,0))
    relief("Jagamohana_Hero_Stone",18.4,-4.06,.35,m["dark"],m)
    plaque("Hero_Stone_Inscribed_Pedestal",18.53,-4.06,.31,m["stone"],width=.81,height=.27)
    landmark("hero_stone",(18.60,-4.06,.93),(20.15,-3.40,.36))
    plaque("Southwest_Wall_Inscribed_Fragment",-23.73,-33.57,1.37,m["stone"],math.pi/2,width=.96,height=.48)
    landmark("southwest_fragment",(-23.73,-33.50,1.39),(-23.73,-30.87,0))
    # The IGNCA records early fragments in the temple walls. Their positions
    # in the current photo mosaic are uncertain, so use one attributed study
    # grouping rather than attaching a new identity to an unconfirmed niche.
    for i,key in enumerate(("Ardhanarisvara","Lakulisa","Uma_Mahesvara","Matrikas")):
        x=8.6+i*2.32
        y=5.45
        relief("OrnamentDetail_Study_"+key,x,y,.46,m["stone"],m,
                    shape="seated" if i>1 else "standing",face=1)
    landmark("carved_fragments",(12.1,5.56,1.61),(12.15,7.57,0))


def build():
    geom.clear_scene()
    round_meshes.clear()
    m={
        "plaster":mats.create_sandstone("Biraja_Weathered_Limewash",(.43,.39,.46,1),roughness=.93),
        "trim":mats.create_sandstone("Biraja_Offwhite_Moulding",(.59,.55,.54,1),roughness=.90),
        "paving":mats.create_sandstone("Biraja_Worn_Courtyard",(.32,.245,.176,1),roughness=.97),
        "stone":mats.create_sandstone("Biraja_Khondalite_Dressed",(.22,.188,.15,1),roughness=.92),
        "dark":mats.create_black_stone("Biraja_Dark_Relief",(.071,.059,.049,1),roughness=.88),
        "idol":mats.create_sandstone("Biraja_Iconographic_Study_Stone",(.32,.22,.115,1),roughness=.76),
        "metal":mats.create_black_stone("Biraja_Corrugated_GI",(.15,.16,.17,1),roughness=.81),
        "wood":mats.create_wood("Biraja_Door_Grain",(.16,.077,.039,1)),
        "brick":mats.create_terracotta("Biraja_Red_Pillar",(.31,.071,.046,1)),
        "red":mats.create_red_silk("Biraja_Red_Seva_Cloth",(.39,.042,.023,1)),
        "ochre":mats.create_red_silk("Biraja_Ochre_Paint",(.53,.238,.046,1)),
        "green":mats.create_black_stone("Biraja_Olive_Green",(.126,.228,.085,1),roughness=.91),
        "leafshade":mats.create_black_stone("Biraja_Tree_Shade",(.065,.122,.036,1),roughness=.97),
        "blue":mats.create_black_stone("Biraja_Fascia_Blue",(.072,.135,.255,1),roughness=.92),
        "tile_blue":mats.create_white_marble("Nabhi_Tile_Blue",(.20,.40,.51,1)),
        "tile_green":mats.create_white_marble("Nabhi_Tile_Green",(.28,.41,.26,1)),
        "tile_yellow":mats.create_white_marble("Nabhi_Tile_Ochre",(.49,.43,.22,1)),
        "brass":mats.create_brass_metal("Biraja_Votive_Brass",(.65,.40,.12,1)),
        "flame":mats.create_flame_emission("Biraja_Deepa_Flame",strength=3.0),
    }
    boundary(m)
    courtyard_paving(m)
    main_complex(m)
    # The medical deity temple and both Deva Sabha halls occupy the north/east courts.
    pidha_shrine("baidyanatha",39.9,10.4,4.10,.18,m,total=7.0)
    roofed_linga_hall("sahasralinga_i",50.2,36.1,6,10.5,53,24,-1,m,votives=1)
    roofed_linga_hall("sahasralinga_ii",38.4,38.8,5.80,10.20,37,0,1,m,votives=5)
    isanesvara(5.2,31.2,m)
    pidha_shrine("bhushandesvara",-23.7,-27.0,3.50,.18,m,total=5.5)
    bagalamukhi(-16.2,-8.45,m)
    paired_reliefs(-17.2,6.60,m)
    nabhi_gaya(5.30,8.20,m)
    dola_mandapa(-1.20,-17.65,m)
    perimeter_features(m)
    epigraphy(m)
    pillar("Simha_Stambha_Main",34.1,0,0,3.12,.41,m["stone"],m["trim"])
    lion("Simha_Stambha_Lion",34.1,0,3.12,m,.83)
    landmark("simha_stambha",(34.1,0,3.19),(37.3,2.1,0))
    bpy.context.view_layer.update()
    true_north=Matrix.Rotation(math.radians(-19),4,"Z")
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world=true_north @ obj.matrix_world
    path=os.path.join(os.path.dirname(os.path.dirname(__file__)),"godot","assets","models",
                      "jajpur_biraja_kshetra_full.glb")
    bpy.ops.export_scene.gltf(filepath=path,export_format="GLB",export_apply=True,
                              export_yup=True,export_materials="EXPORT",
                              export_cameras=False,export_lights=False)
    print("Exported Biraja precinct:",path,flush=True)


if __name__=="__main__":
    build()
