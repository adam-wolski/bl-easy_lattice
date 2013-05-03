#TODO Calculate the final position of objects

import bpy
import mathutils
 
 
#Cleanup
def modifiersDelete(obj):
    for mod in obj.modifiers:
        if mod.name=="latticeeasytemp":
            bpy.ops.object.modifier_remove(modifier=mod.name)

#Cleanup
def latticeDelete():
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
         if "LatticeEasytTemp" in ob.name:
             ob.select=True
    bpy.ops.object.delete(use_global=False)        

def createLattice(obj,size,pos):
    # Create lattice and object
    lat = bpy.data.lattices.new('LatticeEasytTemp')
    ob = bpy.data.objects.new('LatticeEasytTemp', lat)
    
    loc=getTransformations(obj)[0]
    rot=getTransformations(obj)[1]
    scl=getTransformations(obj)[2]
    
     
    ob.location=pos
    #ob.location=(pos.x+loc.x,pos.y+loc.y,pos.z+loc.z)
    
    #size=values from selection bbox
    ob.scale=size
    #ob.scale=(size.x*scl.x, size.y*scl.y,size.z*scl.z)
       
    ob.rotation_euler=rot
    
    #Debug
    trans_mat=mathutils.Matrix.Translation(loc)
    trans_mat*=mathutils.Matrix.Scale(scl.x, 4, (1.0, 0.0, 0.0))
    trans_mat*=mathutils.Matrix.Scale(scl.y, 4, (0.0, 1.0, 0.0))
    trans_mat*=mathutils.Matrix.Scale(scl.z, 4, (0.0, 0.0, 1.0))
    

    print("trans mat",trans_mat) 
    
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
    lat.points_u = 3
    lat.points_v = 3
    lat.points_w = 3
 
    # Set lattice points
#    s = 0.0
#    points = [
#        (-s,-s,-s), (s,-s,-s), (-s,s,-s), (s,s,-s),
#        (-s,-s,s), (s,-s,s), (-s,s,s), (s,s,s)
#    ]
#    for n,pt in enumerate(lat.points):
#        for k in range(3):
#            #pt.co[k] = points[n][k]
    return ob


def selectedVerts_Grp(obj):
#     vertices=bpy.context.active_object.data.vertices
    vertices=obj.data.vertices
    
    selverts=[]
    
    if obj.mode=="EDIT":
        bpy.ops.object.editmode_toggle()

    for grp in obj.vertex_groups:
        
        if "templatticegrp" in grp.name:
            bpy.ops.object.vertex_group_set_active(group=grp.name)
            bpy.ops.object.vertex_group_remove()
        
    tempgroup=obj.vertex_groups.new("templatticegrp")
    
    #selverts=[vert for vert in vertices if vert.select==True]
    for vert in vertices:
        if vert.select==True:
            selverts.append(vert)
            tempgroup.add([vert.index], 1.0, "REPLACE")
    
    #print(selverts)
    
#    print(type(selverts[0]))    
    
    return selverts

def getTransformations(obj):
    rot=obj.rotation_euler
    loc=obj.location
    size=obj.scale

    return [loc,rot,size]

def findBBox(obj,selvertsarray):
    
    mat=buildTrnSclMat(obj)
    mat=obj.matrix_world
    
    minx=0
    miny=0
    minz=0
    
    maxx=0
    maxy=0
    maxz=0
    print("")    
    
    #Median Centers
    x_sum=0
    y_sum=0
    z_sum=0
    
    c=0
    for vert in selvertsarray:
        #co=obj.matrix_world*vert.co.to_4d()
        
        co=vert.co
        #co=obj.matrix_world*vert.co
        
        x_sum+=co.x
        y_sum+=co.y
        z_sum+=co.z
        
        if co.x<minx: minx=co.x
        if co.y<miny: miny=co.y
        if co.z<minz: minz=co.z

        if co.x>maxx: maxx=co.x
        if co.y>maxy: maxy=co.y
        if co.z>maxz: maxz=co.z
        
        #print("local cord", vert.co)
        #print("world cord", co)
        c+=1
        
    #DEBUG
#     matrix_decomp=obj.matrix_world.decompose()
    #print ("martix decompose ", matrix_decomp)

    #Based on world coords
    minpoint=mat*mathutils.Vector((minx,miny,minz))
    maxpoint=mat*mathutils.Vector((maxx,maxy,maxz))
    middle=mat*mathutils.Vector((x_sum/float(c), y_sum/float(c), z_sum/float(c)))
    #middle=(maxpoint+minpoint)/2
    
    size=maxpoint-minpoint
    size=mathutils.Vector((abs(size.x),abs(size.y),abs(size.z)))
    
    
    #####################################################
#    minpoint=mathutils.Vector((minx,miny,minz))
#    maxpoint=mathutils.Vector((maxx,maxy,maxz))
#    middle=mathutils.Vector( (x_sum/float(len(selvertsarray)), y_sum/float(len(selvertsarray)), z_sum/float(len(selvertsarray))) )
#    size=maxpoint-minpoint
#    size=mathutils.Vector((abs(size.x),abs(size.y),abs(size.z)))
    

    #####################################################
    #DEBUG
#     bpy.context.scene.cursor_location=middle
    
    print("world matrix", obj.matrix_world)
    print("min - max", minpoint," ",maxpoint)
    print("size",size)
    print("median point ->",middle)

    #return [minx, miny, minz, maxx, maxy, maxz, pos_median  ]
    return [minpoint,maxpoint,size, middle  ]


def buildTrnSclMat(obj):
    #This function builds a matrix that encodes translation and scaleand it leaves out the rotation matrix
    mat_trans = mathutils.Matrix.Translation(obj.location)
    mat_scale = mathutils.Matrix.Scale(obj.scale[0],4,(1,0,0))
    mat_scale *= mathutils.Matrix.Scale(obj.scale[1],4,(0,1,0))
    mat_scale *= mathutils.Matrix.Scale(obj.scale[2],4,(0,2,0))
    
    mat_final=mat_trans*mat_scale
    
    print("mat_final", mat_final)
    return mat_final
    
def run():
    
    #-----
    #Delete all the lattices for testing
    
    obj=bpy.context.active_object
    modifiersDelete(obj)
    selvertsarray=selectedVerts_Grp(obj)
    bbox=findBBox(obj,selvertsarray)
    
    #latsize=[bbox[3]-bbox[0], bbox[4]-bbox[1], bbox[5]-bbox[2]]
    #size=mathutils.Vector( (abs(latsize[0]), abs(latsize[1]), abs(latsize[2])) )
    
    size=bbox[2]
    #pos=mathutils.Vector( ( bbox[3][0], bbox[3][1], bbox[3][2]) )
    pos=bbox[3]
    
    print("lattce size, pos", size, " ", pos)
    latticeDelete()
    lat = createLattice(obj,size, pos )
    
    
    modif=obj.modifiers.new("latticeeasytemp","LATTICE")
    modif.object=lat
    modif.vertex_group="templatticegrp"
    
    bpy.context.scene.update()
    bpy.ops.object.mode_set(mode='EDIT')
    
    return
 



def main(context):
    run()

class EasyLattice(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.easy_lattice"
    bl_label = "Easy Lattice Creator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EasyLattice)


def unregister():
    bpy.utils.unregister_class(EasyLattice)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.easy_lattice()


