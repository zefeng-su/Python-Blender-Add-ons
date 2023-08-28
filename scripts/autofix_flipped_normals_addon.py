import bpy
 

class FixNormal(bpy.types.Panel):
    #creates panel on sidebar
    bl_label = 'Fix flipped Normals'
    bl_idname = 'OBJECT_PT_FixNormal'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Fix Flipped Normals'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.operator(FixNormalOperator.bl_idname)

class FixNormalOperator(bpy.types.Operator):
    '''Fix flipped Normals''' #type tool tip here
    bl_label = 'Run'
    bl_idname = 'fix_normal.creation_operator'

    def execute(self, context):
        def flip_normals(obj):
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')

        def main():
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                if obj.type == 'MESH':
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.select_all(action='INVERT')
                    flipped_normals = any([v.normal.z < 0 for v in bpy.context.active_object.data.vertices])
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    if flipped_normals:
                        print(f"Flipping normals for object: {obj.name}")
                        flip_normals(obj)
                    else:
                        print(f"No flipped normals found for object: {obj.name}")

        main()
           
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FixNormal)        
    bpy.utils.register_class(FixNormalOperator)    

def unregister():
    bpy.utils.unregister_class(FixNormal)        
    bpy.utils.unregister_class(FixNormalOperator)    

if __name__== "__main__":
     register()