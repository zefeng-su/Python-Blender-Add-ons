# Metadata information about the Blender plugin
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

# Define the panel that will appear in the Blender UI
class StudioLighting(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'Studio Lighting' # Label for the panel
    bl_idname = 'OBJECT_PT_StudioLighting' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears
    bl_category = 'Studio Lighting' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        row = layout.row() # Create a new row in the layout
        row.operator(StudioOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action
class StudioOperator(bpy.types.Operator):
    '''Create 2 pt lighting template''' # Tooltip that appears when hovering over the button
    bl_label = 'Create Studio lighting' # Label for the button
    bl_idname = 'studio.creation_operator' # Unique identifier for the operator

    # Insert script here to excute in this function
    def execute(self, context):
        # Remove all existing objects from the Blender scene
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
            
        # Initialize an array to hold vertex indices for later use
        vertex_list = [2,3,13,14,15]

        #-------------------------------------------------------
        # Adds the BG curved plane
        #-------------------------------------------------------

        z_up_value = 8 # Define the amount by which to raise certain vertices

        # Add a plane to the scene and enter edit mode
        bpy.ops.mesh.primitive_plane_add(size=15, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        # Rename the newly created plane to 'bg_geo'
        for obj in bpy.context.selected_objects:
                obj.name = 'bg_geo'
                obj.data.name = obj.name 

        bpy.ops.mesh.subdivide(number_cuts=3) # Subdivide the plane into smaller parts

        # Exit edit mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Raise the vertices specified in vertex_list
        for num in vertex_list:     
            bpy.data.objects['bg_geo'].data.vertices[num].co.z += z_up_value
        
        bpy.ops.object.subdivision_set(level=2)  # Add a subdivision surface modifier and set its level to 2
        bpy.ops.object.shade_smooth()   # Smooth the surface of the plane

        #-------------------------------------------------------
        # Adds camera
        #-------------------------------------------------------
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, -7.5, 1), rotation=(math.radians(90), 0, 0), scale=(1, 1, 1))

        #-------------------------------------------------------
        # Adds monkey prop to scene
        #-------------------------------------------------------
        bpy.ops.mesh.primitive_monkey_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))

        bpy.ops.object.subdivision_set(level=2)  # Add a subdivision surface modifier and set its level to 2
        bpy.ops.object.shade_smooth() # Smooth the surface of the plane

        #-------------------------------------------------------
        # Adds lights to scene
        #-------------------------------------------------------

        # Key light
        bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(-2.7, -2.5, 3.3), rotation=(1.05, 0.18, -0.88), scale=(1, 1, 1))
        bpy.context.object.data.energy = 100 # Set the energy value for the key light

        # Rename the newly created key light
        for obj in bpy.context.selected_objects:
                obj.name = 'key_light'
                obj.data.name = obj.name 

        # Fill light
        bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(-2.7, -2.5, 3.3), rotation=(1.31, -0.26, 0.88), scale=(1, 1, 1))
        bpy.context.object.data.energy = 30 # Set the energy value for the fill light

        # Rename the newly created fill light
        for obj in bpy.context.selected_objects:
                obj.name = 'fill_light'
                obj.data.name = obj.name     

                return {'FINISHED'}  # Indicate that the operation was successful

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(StudioLighting)        
    bpy.utils.register_class(StudioOperator)    

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(StudioLighting)        
    bpy.utils.unregister_class(StudioOperator)    

# If the script is executed (not imported), register the classes
if __name__== "__main__":
     register()