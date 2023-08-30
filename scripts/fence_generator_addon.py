# Metadata information about the Blender plugin
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

# Define the panel that will appear in the Blender UI
class FenceGenerator(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'FenceGenerator' # Label for the panel
    bl_idname = 'OBJECT_PT_FenceGenerator' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears 
    bl_category = 'Fence Generator' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        
        # Create an operator with settings UI
        col = layout.column(align=True) # Create a new column in the layout
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator(FenceGeneratorOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action        
class FenceGeneratorOperator(bpy.types.Operator):
    '''Generates row of random fences''' # Tooltip that appears when hovering over the button
    bl_label = 'Generate Fences' # Label for the button
    bl_idname = 'fences.creation_operator' # Unique identifier for the operator
    bl_options = {"REGISTER", "UNDO"} # Enable undo for the operator

     # Define properties that appear as settings in the UI for this operator
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

    # Insert script here to excute in this function
    def execute(self, context):

        # Remove all existing objects from the Blender scene
        def clean_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)

         # Set the origin point to the bottom of the object
        def set_origin_bottom(obj):
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
            bpy.ops.transform.translate(value=(0, 0, obj.dimensions.z / 2))
        
        # Create a single fence plank
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

        # Fetch user-defined properties
        num_plank = self.amt_planks
        gap_plank = self.amt_gap

        # Clear the scene if the corresponding checkbox is checked
        if self.clear_previous_fences:
            clean_scene()

        # Generate the fence planks
        for i in range(num_plank):
            thickness = random.uniform(0.2, 0.25)
            height = random.uniform(9.9, 10.2)
            angle = random.uniform(-0.1, 0.1)
            create_single_plank(height, thickness, angle)
            bpy.context.object.location[1] = (1 + gap_plank) * i  # along y-axis

        return {'FINISHED'} # Indicate that the operation was successful
    
    # Invoke function is called to show the settings dialog before executing the operator
    def invoke(self, context, event):
        wm = context.window_manager # Get the window manager
        return wm.invoke_props_dialog(self) # Show the properties dialog for the operator

# Function to add the Operator to the Blender UI menu
def menu_func(self, context):
    self.layout.operator(FenceGeneratorOperator.bl_idname, text=FenceGeneratorOperator.bl_label)

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(FenceGenerator)        
    bpy.utils.register_class(FenceGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(FenceGenerator)        
    bpy.utils.unregister_class(FenceGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

# If the script is executed (not imported), register the classes
if __name__== "__main__":
    register()