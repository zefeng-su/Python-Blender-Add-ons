bl_info = {
    "name": "Fence Generator",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Generates row of random fences",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *
import random

class FenceGenerator(bpy.types.Panel):
    # Creates panel on sidebar
    bl_label = 'FenceGenerator'
    bl_idname = 'OBJECT_PT_FenceGenerator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Fence Generator'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Create an operator with settings UI
        col = layout.column(align=True)
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator(FenceGeneratorOperator.bl_idname)
        
class FenceGeneratorOperator(bpy.types.Operator):
    '''Generates row of random fences''' # Type tool tip here
    bl_label = 'Generate Fences'
    bl_idname = 'fences.creation_operator'
    bl_options = {"REGISTER", "UNDO"}

    # Create properties
    amt_gap : FloatProperty(
        name = "Gap",
        description = "Gap distance between fences",
        default= 0.1,
        min = 0.1, 
        max = 1.0
    )

    amt_planks : IntProperty(
        name = "Number of planks",
        description = "Number of planks to generate",
        default= 10,
        min = 1, 
        max = 50
    )

    clear_previous_fences: BoolProperty(
        name = "Clear previous fences",
        description = "Clears the scene before generating new fences",
        default = True
    )

    def execute(self, context):
        # Insert script here
        def clean_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)

        def set_origin_bottom(obj):
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
            bpy.ops.transform.translate(value=(0, 0, obj.dimensions.z / 2))

        def create_single_plank(height, thickness, angle):
            bpy.ops.mesh.primitive_cube_add(
                size=1, 
                location=(0, 0, 0),
                rotation=(0, 0, angle)
            )
            plank = bpy.context.object
            plank.scale[0] = thickness  # x-axis
            plank.scale[2] = height  # z-axis
            if bpy.context.selected_objects:  # Check if any object is selected
                set_origin_bottom(bpy.context.selected_objects[0])

        num_plank = self.amt_planks
        gap_plank = self.amt_gap

        if self.clear_previous_fences:
            clean_scene()

        for i in range(num_plank):
            thickness = random.uniform(0.2, 0.25)
            height = random.uniform(9.9, 10.2)
            angle = random.uniform(-0.1, 0.1)
            create_single_plank(height, thickness, angle)
            bpy.context.object.location[1] = (1 + gap_plank) * i  # along y-axis


        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def menu_func(self, context):
    self.layout.operator(FenceGeneratorOperator.bl_idname, text=FenceGeneratorOperator.bl_label)

def register():
    bpy.utils.register_class(FenceGenerator)        
    bpy.utils.register_class(FenceGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(FenceGenerator)        
    bpy.utils.unregister_class(FenceGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__== "__main__":
    register()
