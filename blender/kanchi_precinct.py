"""Footprints from the HUDCO restoration drawing and post-restoration aerial views."""
import math
from mathutils import Matrix
import bpy

from common_geometry import create_gopuram, create_shikhara
from deity_detail import Sculpture
from present_day_sites import anchor


PLAN_SCALE = .113
NORTH_ROTATION = math.radians(42.1)


def point(px, py):
    return ((px-834)*PLAN_SCALE,(1115-py)*PLAN_SCALE)


def shape(name, vertices, faces, mat, position=(0,0,0)):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(mat)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    obj.location=position
    bpy.context.collection.objects.link(obj)
    return obj


def cube(name, p, dimensions, mat, bevel=0):
    x,y,z=(d/2 for d in dimensions)
    corners=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
             (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    obj=shape(name,corners,faces,mat,p)
    if bevel:
        b=obj.modifiers.new('Dressed stone edges','BEVEL')
        b.width=bevel
        b.segments=2
    return obj


def range_wall(name, start, end, z, thickness, height, mat):
    a,b=start,end
    dx,dy=b[0]-a[0],b[1]-a[1]
    obj=cube(name,((a[0]+b[0])/2,(a[1]+b[1])/2,z+height/2),
             (math.hypot(dx,dy),thickness,height),mat,.018)
    obj.rotation_euler.z=math.atan2(dy,dx)
    return obj


def framed_portal(name, x, y, width, opening, floor, height, stone, trim):
    h=height-floor
    j=(width-opening)/2
    for side in [-1,1]:
        cube(name+'_Jamb',(x+side*(opening+j)/2,y,floor+h/2),(j,.59,h),stone,.045)
        for layer in range(3):
            cube(name+'_Stone_Reveal',(x+side*(opening/2+.12+layer*.14),y-.31,floor+h*.42),
                 (.074,.17,h*.84),trim,.012)
    cube(name+'_Lintel',(x,y,height-h*.105),(opening,.63,h*.21),stone,.032)


def pillar(name, x, y, z, height, stone, width=.48):
    for part,off,w,h in [('Base',.046,1.51,.092),('Lower_Moulding',.12,1.21,.067),
                         ('Shaft',.475,1,.653),('Upper_Moulding',.82,1.35,.065),
                         ('Capital',.913,1.63,.174)]:
        cube(name+'_'+part,(x,y,z+height*off),(width*w,width*w,h*height),stone,.024)


def hall(name, bounds, stone, paving, ceiling, z=0, height=4.2, bays=(5,4)):
    x,y,x2,y2=bounds
    width,depth=x2-x,y2-y
    center=((x+x2)/2,(y+y2)/2)
    cube(name+'_Plinth',(*center,z+.081),(width,depth,.162),paving,.034)
    for i in range(bays[0]):
        for j in range(bays[1]):
            if i not in (0,bays[0]-1) and j not in (0,bays[1]-1):
                continue
            pillar(name+'_Pillar',x+1+i*(width-2)/(bays[0]-1),
                   y+1+j*(depth-2)/(bays[1]-1),z+.16,height-.20,stone)
    for overhang,dz,thickness in [(0,0,.31),(.21,.27,.22),(.44,.48,.21)]:
        cube(name+'_Roof',(*center,z+height+dz),(width+overhang,depth+overhang,thickness),ceiling,.033)


def build_tank(tank_stone, pavement, water):
    cx,cy=point(851,632)
    w,d=47.5,51.0
    angle=math.radians(-8)
    transform=Matrix.Translation((cx,cy,0))@Matrix.Rotation(angle,4,'Z')
    before=set(bpy.context.scene.objects)
    # Solid slabs meet the tank opening. The long arrival lane remains on
    # one slab, so the capsule never crosses a diagonal floor mesh join.
    x0,x1,y0,y1=-104,104,-147,87
    for lx,hx,ly,hy in [(x0,x1,y0,-d/2),(x0,x1,d/2,y1),
                        (x0,-w/2,-d/2,d/2),(w/2,x1,-d/2,d/2)]:
        cube('Ground_Paved_Processional_Court',((lx+hx)/2,(ly+hy)/2,-.19),
             (hx-lx,hy-ly,.38),pavement)
    for i in range(11):
        step=.38*i
        z=-.23-.23*i
        perimeter_x=w-2*step
        perimeter_y=d-2*step
        for side in [-1,1]:
            cube('Pushkarini_Long_Granite_Step',(side*(perimeter_x/2-.20),0,z),
                 (.40,perimeter_y,.46),tank_stone,.014)
            cube('Pushkarini_Short_Granite_Step',(0,side*(perimeter_y/2-.20),z),
                 (perimeter_x-.80,.40,.46),tank_stone,.014)
    cube('Pushkarini_Water',(0,0,-2.39),(w-7.4,d-7.4,.04),water)
    cube('Pushkarini_Bed',(0,0,-3.27),(w-6.4,d-6.4,.70),tank_stone)
    hall('Teppam_Island_Pavilion',(-2.55,-2.55,2.55,2.55),tank_stone,tank_stone,tank_stone,-2.32,3.5,(2,2))
    create_shikhara('Teppam_Pavilion_Vimana',(0,0,1.42),4.20,3.6,3,tank_stone,'dravidian')
    anchor('Kamakshi_Tank_Island_Reference',(0,0,1.35))
    anchor('Kamakshi_Tank_Landing',(0,-d/2-2.30,.06))
    bpy.context.view_layer.update()
    for obj in set(bpy.context.scene.objects)-before:
        if obj.parent is None:
            obj.matrix_world=transform@obj.matrix_world


def tower_stucco(name, width, depth, height, tiers):
    # Readable aedicules and pillars at the photographed tier spacing.
    # Small forms here study the architectural rhythm of the gopurams.
    s=Sculpture()
    plaster=s.material('Kanchi_Weathered_Stucco',(.66,.59,.44),0,.82)
    recess=s.material('Kanchi_Stucco_Recess',(.43,.38,.31),0,.90)
    tier_h=height/tiers
    for tier in range(tiers):
        factor=1-.52*tier/(tiers-1)
        for side in [-1,1]:
            for front in [True,False]:
                breadth=(width if front else depth)*factor
                edge=(depth if front else width)*factor/2
                count=max(3,int(breadth/1.75))
                for i in range(count):
                    along=(i-(count-1)/2)*breadth/(count+.7)
                    if front and abs(along)<.3:
                        continue
                    z=3+tier*tier_h+tier_h*.35
                    at=lambda a,b,h:(along+a,side*(edge+b),z+h) if front else (side*(edge+b),along+a,z+h)
                    s.ellipsoid(at(0,.025,.19),(.39,.064,.59) if front else (.064,.39,.59),recess,10,7)
                    s.ellipsoid(at(0,.105,.04),(.15,.16,.43),plaster,10,7)
                    s.ellipsoid(at(0,.119,.48),(.16,.15,.16),plaster,10,7)
                    for sign in [-1,1]:
                        s.tube([at(sign*.36,.12,-.39),at(sign*.36,.12,.34),
                                at(sign*.22,.16,.63),at(0,.19,.80)],.051,plaster,7)
    s.finish(name+'_Stucco_OrnamentDetail')


def boundary(base_wall, light, gold):
    # Positions come from the named gates in the restoration plan.
    corner_pixels=[(350,256),(1521,438),(1339,1452),(390,1516)]
    gate_pixels=[(1151,384),(1451,885),(954,1454),(379,706)]
    names=['West','North','East','South']
    for index,name in enumerate(names):
        a=point(*corner_pixels[index])
        b=point(*corner_pixels[(index+1)%4])
        g=point(*gate_pixels[index])
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        axis=(dx/length,dy/length)
        width,depth,height,tiers=(18.5,10.1,21.5,7) if name=='East' else (12.8,7.45,15.4,5)
        gate_x=a[0]+sum((g[i]-a[i])*axis[i] for i in range(2))*axis[0]
        gate_y=a[1]+sum((g[i]-a[i])*axis[i] for i in range(2))*axis[1]
        edge_a=(gate_x-axis[0]*width*.47,gate_y-axis[1]*width*.47)
        edge_b=(gate_x+axis[0]*width*.47,gate_y+axis[1]*width*.47)
        for u,v in [(a,edge_a),(edge_b,b)]:
            range_wall(name+'_Prakara_Base',u,v,0,.88,3.71,base_wall)
            range_wall(name+'_Prakara_Coping',u,v,3.71,.99,.47,light)
        before=set(bpy.context.scene.objects)
        create_gopuram(name+'_Gopuram',(0,0,0),width,depth,height,tiers,light,None,gold)
        tower_stucco(name+'_Gopuram',width,depth,height,tiers)
        rotation=Matrix.Rotation(math.atan2(dy,dx),4,'Z')
        move=Matrix.Translation((gate_x,gate_y,0))@rotation
        bpy.context.view_layer.update()
        for obj in set(bpy.context.scene.objects)-before:
            if obj.parent is None:
                if 'Jamb' in obj.name:
                    obj.data.materials[0]=base_wall
                obj.matrix_world=move@obj.matrix_world


def orient_scene():
    transform=Matrix.Rotation(NORTH_ROTATION,4,'Z')
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.parent is None:
            obj.matrix_world=transform@obj.matrix_world
