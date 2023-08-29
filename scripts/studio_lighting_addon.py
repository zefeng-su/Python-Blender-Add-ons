bl_info = {
    "name": "Studio Lighting",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Create 2 pt lighting template",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
import math

class StudioLighting(bpy.types.Panel):
    #creates panel on sidebar
    bl_label = 'Studio Lighting'
    bl_idname = 'OBJECT_PT_StudioLighting'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Studio Lighting'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.operator(StudioOperator.bl_idname)

class StudioOperator(bpy.types.Operator):
    '''Create 2 pt lighting template''' #type tool tip here
    bl_label = 'Create Studio lighting'
    bl_idname = 'studio.creation_operator'

    def execute(self, context):
        #clear blender scene
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
            
        #array to store vertex values
        vertex_list = [2,3,13,14,15]

        #-------------------------------------------------------
        # Adds the BG curved plane
        #-------------------------------------------------------

        z_up_value = 8

        bpy.ops.mesh.primitive_plane_add(size=15, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        for obj in bpy.context.selected_objects:
                obj.name = 'bg_geo'
                obj.data.name = obj.name 

        bpy.ops.mesh.subdivide(number_cuts=3)

        #Sets interactive mode on obj
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for num in vertex_list:     
            bpy.data.objects['bg_geo'].data.vertices[num].co.z += z_up_value
        
        bpy.ops.object.subdivision_set(level=2)
        bpy.ops.object.shade_smooth()

        #-------------------------------------------------------
        # Adds camera
        #-------------------------------------------------------
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, -7.5, 1), rotation=(math.radians(90), 0, 0), scale=(1, 1, 1))

        #-------------------------------------------------------
        # Adds monkey prop to scene
        #-------------------------------------------------------
        bpy.ops.mesh.primitive_monkey_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))

        bpy.ops.object.subdivision_set(level=2)
        bpy.ops.object.shade_smooth()

        #-------------------------------------------------------
        # Adds lights to scene
        #-------------------------------------------------------

        # Key light
        bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(-2.7, -2.5, 3.3), rotation=(1.05, 0.18, -0.88), scale=(1, 1, 1))

        bpy.context.object.data.energy = 100

        for obj in bpy.context.selected_objects:
                obj.name = 'key_light'
                obj.data.name = obj.name 

        # Fill light
        bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(-2.7, -2.5, 3.3), rotation=(1.31, -0.26, 0.88), scale=(1, 1, 1))

        bpy.context.object.data.energy = 30

        for obj in bpy.context.selected_objects:
                obj.name = 'fill_light'
                obj.data.name = obj.name     

                return {'FINISHED'}

def register():
    bpy.utils.register_class(StudioLighting)        
    bpy.utils.register_class(StudioOperator)    

def unregister():
    bpy.utils.unregister_class(StudioLighting)        
    bpy.utils.unregister_class(StudioOperator)    

if __name__== "__main__":
     register()