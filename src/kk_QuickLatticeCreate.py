#----------------------------------------------------------
# File lattice.py


#----------------------------------------------------------
import bpy
 
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
 
def createLattice(origin,size):
    # Create lattice and object
    lat = bpy.data.lattices.new('MyLattice')
    ob = bpy.data.objects.new('LatticeObject', lat)
    
   
    ob.location = origin
    ob.show_x_ray = True
    # Link object to scene
    scn = bpy.context.scene
    ob.scale=size
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
 
def run(origin):
    #sphere = createIcoSphere(origin)
    
    # Create lattice modifier
    #mod = sphere.modifiers.new('Lat', 'LATTICE')
    #mod.object = lat
    #mod.vertex_group = 'Upper'
    # Lattice in edit mode for easy deform
    
    
    
    #-----
    obj=bpy.context.active_object
    lat = createLattice(origin,(2,2,2))
    
    modif=obj.modifiers.new("latticetemp","LATTICE")
    modif.object=lat
    
    
    
    bpy.context.scene.update()
    bpy.ops.object.mode_set(mode='EDIT')
    
    return
 
if __name__ == "__main__":
    run((0,0,0))
