#----------------------------------------------------------
# File lattice.py
#----------------------------------------------------------

#TODO Calcuate the final position of objects

import bpy
import mathutils
 
def createIcoSphere(origin):
    # Create an icosphere
    bpy.ops.mesh.primitive_ico_sphere_add(location=origin) 
    ob = bpy.context.object
    me = ob.data
 
    # Create vertex groups
    upper = ob.vertex_groups.new('Upper')
    lower = ob.vertex_groups.new('Lower')
    for v in me.vertices:
        if v.co[2] > 0.001:
            upper.add([v.index], 1.0, 'REPLACE')
        elif v.co[2] < -0.001:
            lower.add([v.index], 1.0, 'REPLACE')
        else:
            upper.add([v.index], 0.5, 'REPLACE')
            lower.add([v.index], 0.5, 'REPLACE')
    return ob
 
def createLattice(size,pos):
    # Create lattice and object
    lat = bpy.data.lattices.new('MyLattice')
    ob = bpy.data.objects.new('LatticeObject', lat)
    
    ob.scale=size
    ob.location=pos
    
   
    ob.show_x_ray = True
    # Link object to scene
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    scn.update()
 
    # Set lattice attributes
    lat.interpolation_type_u = 'KEY_LINEAR'
    lat.interpolation_type_v = 'KEY_CARDINAL'
    lat.interpolation_type_w = 'KEY_BSPLINE'
    lat.use_outside = False
    lat.points_u = 2
    lat.points_v = 2
    lat.points_w = 2
 
    # Set lattice points
    s = 1.0
    points = [
        (-s,-s,-s), (s,-s,-s), (-s,s,-s), (s,s,-s),
        (-s,-s,s), (s,-s,s), (-s,s,s), (s,s,s)
    ]
    for n,pt in enumerate(lat.points):
        for k in range(3):
            #pt.co[k] = points[n][k]
            pass
    return ob


def selectedVerts(obj):
#     vertices=bpy.context.active_object.data.vertices
    vertices=obj.data.vertices
    
    selverts=[vert for vert in vertices if vert.select==True]
    
    print(selverts)
    
#    print(type(selverts[0]))    
    return selverts


def findBBox(obj,selvertsarray):
    minx=0
    miny=0
    minz=0
    
    maxx=0
    maxy=0
    maxz=0
    print("  ")    
    
    #Media Centers
    x_sum=0
    y_sum=0
    z_sum=0
    
    for vert in selvertsarray:
        co=vert.co*obj.matrix_world
        x_sum+=co.x
        y_sum+=co.y
        z_sum+=co.z
        
        if co.x<minx: minx=co.x
        if co.y<miny: miny=co.y
        if co.z<minz: minz=co.z

        if co.x>maxx: maxx=co.x
        if co.y>maxy: maxy=co.y
        if co.z>maxz: maxz=co.z
        
        print("local cord", vert.co)
        print("world cord", co)

    pos_median=[x_sum/len(selvertsarray), y_sum/len(selvertsarray), z_sum/len(selvertsarray)]            
    print("min - max", minx," ", miny," ", minz, " ",  maxx," ", maxy," ", maxz)
    print("median point ->",pos_median)

    return [minx, miny, minz, maxx, maxy, maxz, pos_median  ]


def latticeDelete():
#     for ob in bpy.context.scene.objects:
#         if "Lattice" in ob.name:
    if "Lattice" in bpy.context.scene.objects:
        bpy.ops.object.select_pattern(pattern="Lat*")
        bpy.ops.object.delete(use_global=False) 
    
def run(origin):
    #sphere = createIcoSphere(origin)
    
    # Create lattice modifier
    #mod = sphere.modifiers.new('Lat', 'LATTICE')
    #mod.object = lat
    #mod.vertex_group = 'Upper'
    # Lattice in edit mode for easy deform
    
    
    
    #-----
    #Delete all the lattices for testing
    latticeDelete()
    
    obj=bpy.context.active_object
    selvertsarray=selectedVerts(obj)
    bbox=findBBox(obj,selvertsarray)
    
    latsize=[bbox[0]-bbox[3], bbox[1]-bbox[4], bbox[2]-bbox[5]]
    
    
    size=mathutils.Vector( (abs(latsize[0]), abs(latsize[1]), abs(latsize[2])) )
    pos=mathutils.Vector( ( bbox[6][0], bbox[6][1], bbox[6][2]) )
    print("lattce size, pos", size, " ", pos)
    lat = createLattice(size, pos )
    
    
    modif=obj.modifiers.new("latticetemp","LATTICE")
    modif.object=lat
    
    
    
    bpy.context.scene.update()
    bpy.ops.object.mode_set(mode='EDIT')
    
    return
 
if __name__ == "__main__":
    run((0,0,0))