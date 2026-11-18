"""Reference-led sculptural detail for the existing main sacred forms.

Original geometry, not photogrammetry and not a claim of AAA/ritual accuracy.
The Renuka face study follows the temple portal's face/head photograph; the
Ambabai adornment study follows the documented four-armed form and the dated
decorated-shrine photograph recorded in research/2026-11-16/deities.json.
No downloaded photograph is embedded as a game texture.
"""
import math
import bpy
import bmesh
from mathutils import Vector
from pathlib import Path


class Sculpture:
    def __init__(self):
        self.vertices, self.faces, self.face_materials, self.materials = [], [], [], []

    def material(self, name, color, metallic=0, roughness=.45):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (*color, 1)
        shader.inputs['Metallic'].default_value = metallic
        shader.inputs['Roughness'].default_value = roughness
        self.materials.append(mat)
        return len(self.materials) - 1

    def ellipsoid(self, center, radii, material, segments=20, rings=12, sculpt=None):
        offset = len(self.vertices)
        for j in range(rings+1):
            phi = math.pi*j/rings
            for i in range(segments):
                theta = math.tau*i/segments
                local = Vector((radii[0]*math.sin(phi)*math.cos(theta), radii[1]*math.sin(phi)*math.sin(theta), radii[2]*math.cos(phi)))
                if sculpt:
                    local = sculpt(local)
                self.vertices.append(tuple(Vector(center)+local))
        for j in range(rings):
            for i in range(segments):
                face = (offset+j*segments+i, offset+j*segments+(i+1)%segments,
                        offset+(j+1)*segments+(i+1)%segments, offset+(j+1)*segments+i)
                self.faces.append(face)
                self.face_materials.append(material)

    def tube(self, points, radius, material, sides=8):
        offset = len(self.vertices)
        for index, value in enumerate(points):
            point = Vector(value)
            direction = (Vector(points[min(index+1,len(points)-1)])-Vector(points[max(0,index-1)])).normalized()
            cross = direction.cross(Vector((0,0,1)))
            if cross.length < .01:
                cross = direction.cross(Vector((0,1,0)))
            cross.normalize()
            up = direction.cross(cross).normalized()
            for side in range(sides):
                angle = math.tau*side/sides
                self.vertices.append(tuple(point + radius*(cross*math.cos(angle)+up*math.sin(angle))))
        for index in range(len(points)-1):
            for side in range(sides):
                self.faces.append((offset+index*sides+side,offset+index*sides+(side+1)%sides,
                                   offset+(index+1)*sides+(side+1)%sides,offset+(index+1)*sides+side))
                self.face_materials.append(material)

    def rosette(self, point, radius, gold, jewel=None, petals=8):
        x,y,z = point
        self.ellipsoid((x,y-.008,z),(radius*.36,.014,radius*.36),gold,12,6)
        for i in range(petals):
            a=math.tau*i/petals
            self.ellipsoid((x+math.cos(a)*radius*.7,y,z+math.sin(a)*radius*.7),
                           (radius*.42,.011,radius*.30),gold,10,5)
        if jewel is not None:
            self.ellipsoid((x,y-.025,z),(radius*.23,.018,radius*.23),jewel,12,6)

    def finish(self, name, location=(0,0,0), scale=1):
        mesh=bpy.data.meshes.new(name+'_SculptedMesh')
        mesh.from_pydata(self.vertices,[],self.faces)
        for mat in self.materials: mesh.materials.append(mat)
        mesh.update()
        bm=bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        for polygon,index in zip(mesh.polygons,self.face_materials):
            polygon.material_index=index
            polygon.use_smooth=True
        obj=bpy.data.objects.new(name,mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location=location
        obj.scale=(scale,)*3
        obj['artwork_status']='Original reference-led sculptural study; not an authenticated 3D scan.'
        return obj


def palette(s):
    return {
        'gold':s.material('Detail_Gold',(.76,.48,.12),.92,.29),
        'silver':s.material('Detail_Silver',(.72,.76,.80),.92,.23),
        'black':s.material('Detail_PolishedBasalt',(.019,.016,.015),0,.35),
        'red':s.material('Detail_RubySilk',(.53,.018,.025),0,.44),
        'orange':s.material('Detail_Vermilion',(.88,.12,.018),0,.35),
        'yellow':s.material('Detail_Turmeric',(.93,.48,.015),0,.52),
        'white':s.material('Detail_Jasmine',(.93,.91,.79),0,.7),
        'green':s.material('Detail_Emerald',(.012,.16,.063),.12,.22),
        'eye':s.material('Detail_EyeWhite',(.92,.92,.87),0,.26),
    }


def garland(s,p,x_radius,z_center,z_radius,y,count=85):
    for index in range(count):
        angle=math.pi+math.pi*index/(count-1)
        x=math.cos(angle)*x_radius
        z=z_center+math.sin(angle)*z_radius
        material=p['white'] if index%16<10 else (p['red'] if index%16<13 else p['yellow'])
        s.rosette((x,y,z),.025,material,p['yellow'] if index%16<10 else None,6)


def crown_band(s,p,width,z,y,tiers=4):
    for row in range(tiers):
        points=[]
        for index in range(81):
            t=-1+2*index/80
            points.append((width*t,y+.10*t*t,z+row*.052+.10*(1-t*t)))
        s.tube(points,.018,p['gold'],10)
        for index in range(23):
            t=-.94+1.88*index/22
            s.rosette((width*t,y-.009+.10*t*t,z+row*.052+.10*(1-t*t)),.026,p['gold'],p['green'] if index%5==0 else None)


def renuka_face(name,location):
    s=Sculpture();p=palette(s)
    def sculpt(v):
        if v.y<0:
            # Continuous nose, cheeks and brow are deformed into the head mesh.
            nose=.065*math.exp(-(v.x/.07)**2-((v.z+.03)/.15)**2)
            cheek=.022*(math.exp(-((v.x-.24)/.13)**2)+math.exp(-((v.x+.24)/.13)**2))*math.exp(-((v.z+.08)/.18)**2)
            v.y-=nose+cheek
        return v
    s.ellipsoid((0,0,.67),(.53,.27,.59),p['orange'],128,96,sculpt)
    # Painted central turmeric field: a shallow surface rather than a new face.
    s.ellipsoid((0,-.255,.85),(.145,.035,.34),p['yellow'],64,48)
    for sign in [-1,1]:
        x=sign*.205
        s.ellipsoid((x,-.257,.82),(.147,.018,.070),p['black'],64,32)
        s.ellipsoid((x,-.279,.82),(.117,.016,.051),p['gold'],64,32)
        s.ellipsoid((x,-.295,.824),(.078,.012,.041),p['eye'],48,24)
        s.ellipsoid((x,-.307,.824),(.020,.009,.026),p['black'],32,20)
        s.ellipsoid((x-sign*.007,-.314,.837),(.006,.003,.007),p['eye'],16,8)
        points=[]
        for index in range(30):
            t=-1+2*index/29
            points.append((x+t*.16,-.236,.952+.047*(1-t*t)))
        s.tube(points,.020,p['black'],10)
        s.rosette((sign*.51,-.10,.66),.072,p['gold'],p['red'],10)
        # Fine hanging ear ornaments.
        for n in range(5):s.ellipsoid((sign*.51,-.13,.59-n*.024),(.012,.010,.014),p['gold'],12,8)
    s.ellipsoid((0,-.299,.49),(.100,.012,.027),p['red'],64,24)
    s.ellipsoid((0,-.312,.484),(.070,.009,.012),p['black'],48,16)
    s.ellipsoid((0,-.299,.94),(.014,.007,.014),p['red'],24,16)
    # Crescent and bindi on the turmeric-painted forehead.
    crescent=[(.045*math.cos(math.pi*i/30),-.292,1.034-.025*math.sin(math.pi*i/30)) for i in range(31)]
    s.tube(crescent,.006,p['red'],8)
    s.ellipsoid((0,-.292,1.055),(.008,.005,.008),p['red'],16,10)
    ring=[(.19+.055*math.cos(math.tau*i/60),-.33,.54+.055*math.sin(math.tau*i/60)) for i in range(61)]
    s.tube(ring,.004,p['silver'],8)
    for n in range(4):s.ellipsoid((.205,-.34,.48-n*.018),(.010,.007,.010),p['silver'],12,8)
    crown_band(s,p,.62,1.13,-.13,5)
    for side in [-1,1]:
        for n in range(5):s.rosette((side*(.16+n*.092),-.16,1.41-n*.022),.043,p['gold'],p['green'] if n%2==0 else None,10)
    s.rosette((0,-.19,1.43),.065,p['gold'],p['red'],12)
    garland(s,p,.61,.99,.85,-.05,115)
    garland(s,p,.66,.99,.90,-.01,125)
    return s.finish(name,location,.94)


def add_reference_ornaments(obj,temple_id):
    """Richer physical ornament without guessing new arms or hidden anatomy."""
    points=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    height=hi.z-lo.z
    if height<.2:return
    s=Sculpture();p=palette(s)
    center=(lo+hi)*.5
    width=max(.25,(hi.x-lo.x)*.48)
    front=-(hi.y-lo.y)*.52-.025
    back=(hi.y-lo.y)*.52+.025
    # Intricate brass prabhavali and individually modelled flower petals.
    for offset in [0,.022,.048]:
        arc=[]
        for index in range(129):
            a=math.pi*index/128
            arc.append((math.cos(a)*(width+.09+offset),back,math.sin(a)*(height*.46+offset)+height*.05))
        s.tube(arc,.009,p['gold'],8)
    for index in range(37):
        a=math.pi*index/36
        s.rosette((math.cos(a)*(width+.13),back-.02,math.sin(a)*(height*.46+.04)+height*.05),.022,p['gold'],p['red'] if index%6==0 else None)
    garland(s,p,width*.89,height*.30,height*.62,front,95)
    # Reference-driven adornment does not change the original sacred form.
    detail=s.finish('MainDeity_OrnamentDetail',tuple(center))
    return detail


def ambabai_refinement(main):
    # The builder used viewer-right for deity-right. Correct the sacred
    # attribute sides before adding reference-led face and jewellery detail.
    for vertex in main.data.vertices:
        vertex.co.x = -vertex.co.x
    bm=bmesh.new();bm.from_mesh(main.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(main.data);bm.free()
    s=Sculpture();p=palette(s)
    y=8.5;z=1.4
    def face_shape(v):
        if v.y<0:
            v.y-=.017*math.exp(-(v.x/.018)**2-((v.z+.005)/.04)**2)
        return v
    s.ellipsoid((0,y-.025,z+1.48),(.125,.107,.143),p['black'],96,64,face_shape)
    for sign in [-1,1]:
        s.ellipsoid((sign*.047,y-.124,z+1.492),(.031,.007,.014),p['gold'],36,20)
        s.ellipsoid((sign*.047,y-.132,z+1.492),(.019,.005,.009),p['eye'],32,16)
        s.ellipsoid((sign*.047,y-.138,z+1.492),(.006,.003,.008),p['black'],24,12)
        s.rosette((sign*.122,y-.052,z+1.45),.023,p['gold'],p['red'],8)
        for i in range(5):s.ellipsoid((sign*.122,y-.066,z+1.43-i*.010),(.005,.004,.006),p['gold'],10,6)
    s.ellipsoid((0,y-.139,z+1.533),(.008,.004,.009),p['red'],20,12)
    s.ellipsoid((0,y-.145,z+1.426),(.023,.004,.005),p['red'],32,16)
    s.rosette((-.015,y-.163,z+1.467),.010,p['gold'],p['white'],7)
    for row in range(5):
        a0=math.pi*.18;a1=math.pi*.82
        chain=[]
        for i in range(75):
            a=a0+(a1-a0)*i/74
            chain.append((math.cos(a)*(.22+row*.012),y-.20-row*.003,z+1.30-math.sin(a)*(.16+row*.11)))
        s.tube(chain,.004,p['gold'] if row%2==0 else p['silver'],6)
        for i in range(0,75,3):s.ellipsoid(chain[i],(.006,.006,.008),p['gold'],10,6)
    crown_band(s,p,.11,z+1.60,y-.10,4)
    for sign in [-1,1]:
        for hand_z,hand_x in [(1.25,.46),(.90,.36)]:
            s.ellipsoid((sign*hand_x,y-.10,z+hand_z),(.046,.037,.055),p['black'],24,16)
            for finger in range(4):
                s.ellipsoid((sign*(hand_x-.025+finger*.016),y-.132,z+hand_z-.025),(.006,.007,.022),p['black'],12,8)
    return s.finish('Ambabai_Face_Jewellery_Detail')


def upgrade_scene(temple_id):
    bpy.context.view_layer.update()
    main=next((obj for obj in bpy.context.scene.objects if obj.type=='MESH' and obj.name.startswith('Deity_')),None)
    if not main:return
    if main.get('has_authored_ornaments'):
        return
    if temple_id=='kolhapur_mahalakshmi':
        ambabai_refinement(main)
    if temple_id=='kamakhya':
        points=[main.matrix_world@Vector(corner) for corner in main.bound_box]
        base=(sum(v.x for v in points)/8,sum(v.y for v in points)/8,min(v.z for v in points))
        name=main.name
        bpy.data.objects.remove(main,do_unlink=True)
        s=Sculpture();p=palette(s)
        rock=s.material('Kamakhya_NaturalBedrock',(.055,.045,.036),0,.63)
        water=s.material('Kamakhya_SpringSurface',(.065,.105,.102),.12,.16)
        # Two irregular banks descending into a narrow spring-fed depression.
        # Broad form follows descriptions; exact contours remain unverified.
        for sign in [-1,1]:
            offset=len(s.vertices)
            for iy in range(65):
                y=-.93+1.86*iy/64
                gap=.055+.013*math.sin(y*9)
                width=.96+.10*math.cos(y*3)+.025*math.sin(y*17)
                for ix in range(33):
                    t=ix/32
                    x=sign*(gap+t*width)
                    z=.08+.23*(1-math.exp(-(t/.38)**2))+.014*math.sin(x*13+y*5)+.008*math.cos(y*19+x*7)
                    s.vertices.append((x,y,z))
            for iy in range(64):
                for ix in range(32):
                    a=offset+iy*33+ix
                    s.faces.append((a,a+1,a+34,a+33))
                    s.face_materials.append(rock)
        # The cleft remains open; water is recessed below the higher banks.
        s.ellipsoid((0,0,.075),(.10,.86,.018),water,80,16)
        # Restrained flowers and cloth are movable offerings, not fixed anatomy.
        for index in range(17):
            a=math.tau*index/17
            x=.80*math.cos(a);y=.75*math.sin(a)
            s.rosette((x,y,.33),.035,p['red'],p['yellow'],7)
        for n in range(19):
            x=-.48+n*.053
            s.tube([(x,.59,.33),(x,.73,.31),(x,.86,.27)],.018,p['red'],6)
        main=s.finish(name,base)
        main['reference_status']='Schematic natural rock cleft and spring; no authenticated sanctum photograph available.'
        return
    if temple_id=='mahur_renuka':
        # Existing builder's altar origin is at z+.08; preserve its exact base.
        name=main.name
        base=tuple(main.location-Vector((0,0,.08)))
        rotation=main.rotation_euler.copy()
        bpy.data.objects.remove(main,do_unlink=True)
        main=renuka_face(name,base)
        main.rotation_euler=rotation
        font_path=Path('C:/Windows/Fonts/Nirmala.ttf')
        if font_path.exists():
            curve=bpy.data.curves.new('Renuka_Forehead_Om','FONT')
            curve.body='\u0950'
            curve.font=bpy.data.fonts.load(str(font_path))
            curve.align_x='CENTER'
            curve.size=.105
            curve.extrude=.0008
            glyph=bpy.data.objects.new('Renuka_Forehead_Om',curve)
            bpy.context.scene.collection.objects.link(glyph)
            glyph.parent=main
            glyph.location=(0,-.303,1.01)
            glyph.rotation_euler=(math.pi/2,0,0)
            red=next(m for m in bpy.data.materials if m.name.startswith('Detail_RubySilk'))
            curve.materials.append(red)
        return
    # Never add an invented human image to a cave cleft, cradle, lost shrine or
    # unresolved sacred symbol. These retain their documented form.
    if temple_id in ['kamakhya','prayag_madhaveswari','gaya_mangalagauri','pradyumna_shrinkhala','lanka_shankari']:
        return
    add_reference_ornaments(main,temple_id)
