# Metadata information about the Blender plugin
bl_info = {
    "name": "Rock Generator",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Generates random rock",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *

# Define the panel that will appear in the Blender UI 
class RockGenerator(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'RockGenerator' # Label for the panel
    bl_idname = 'OBJECT_PT_RockGenerator' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears 
    bl_category = 'Rock Generator' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        
        # Create an operator with settings UI
        col = layout.column(align=True)  # Create a new column in the layout
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator(RockGeneratorOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action           
class RockGeneratorOperator(bpy.types.Operator):
    '''Generates random rock''' # Tooltip that appears when hovering over the button
    bl_label = 'Generate Rock' # Label for the button
    bl_idname = 'rock.creation_operator' # Unique identifier for the operator
    bl_options = {"REGISTER", "UNDO"} # Enable undo for the operator

    # Define properties that appear as settings in the UI for this operator
    noise_scale : FloatProperty(
        name = "Noise",
        description = "The scale of the noise",
        default= 0.75,
        min = 0.75, 
        max = 1.0
    )

    intensity_scale : FloatProperty(
        name = "Intensity",
        description = "The intensity of the noise",
        default= 0.1,
        min = 0.1, 
        max = 0.3
    )

    subdivide_level : IntProperty(
        name = "Subdivide level",
        description = "Level of subdivision",
        default= 3,
        min = 2, 
        max = 5
    )

    decimate_ratio : FloatProperty(
        name = "Decimate",
        description = "Adjust to control polygon count",
        default= 0.2,
        min = 0.1, 
        max = 1.0
    )
    
    clear_previous_rock : BoolProperty(
        name = "Clear previous rocks?",
        description = "Clears the scene before generating new rock",
        default = True
    )

    # Insert script here to excute in this function
    def execute(self, context):

        # Remove all existing objects from the Blender scene 
        def clean_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)

            for texture in bpy.data.objects:
                bpy.data.objects.remove(texture)    

         # Function to create a cube 
        def create_cube():
            bpy.ops.mesh.primitive_cube_add()
            return bpy.context.object
        
        # Function to apply a modifier to an object
        def modifier_apply(apply, name):
            if apply:
                bpy.ops.object.modifier_apply(modifier=name)

        # Function to apply subdivision to an object
        def subdiv(obj, name, apply=True):
            modifier = obj.modifiers.new(type="SUBSURF", name=name)
            modifier.levels = self.subdivide_level
            modifier_apply(apply, modifier.name)

        # Function to create a Voronoi texture
        def create_voronoi(intensity, scale):
            texture = bpy.data.textures.new("voronoi", type="VORONOI")
            texture.distance_metric = "DISTANCE_SQUARED"
            texture.noise_intensity = intensity 
            texture.noise_scale = scale

            return texture
        
        # Function to displace vertices of an object based on a texture    
        def displace(obj, name, apply=True):
            modifier = obj.modifiers.new(type="DISPLACE", name=name)
            texture = create_voronoi(
                intensity = self.intensity_scale,
                scale = self.noise_scale
            )
            modifier.texture = texture
            modifier_apply(apply, modifier.name)

        # Function to decimate (reduce polygons of) an object
        def decimate(obj, name, apply=True):
            modifier = obj.modifiers.new(type="DECIMATE", name=name)
            modifier.ratio = self.decimate_ratio
            modifier_apply(apply, modifier.name)

        # Function to generate the rock by combining all the above functions
        def generate_rock():
            cube = create_cube()
            subdiv(cube, "subdivide")
            displace(cube, "displace")
            decimate(cube, "decimate")

        # Clear the scene if the corresponding checkbox is checked     
        if self.clear_previous_rock:
            clean_scene()
            
        generate_rock()    

        return {'FINISHED'} # Indicate that the operation was successful
    
    # Invoke function is called to show the settings dialog before executing the operator
    def invoke(self, context, event):
        wm = context.window_manager  # Get the window manager
        return wm.invoke_props_dialog(self) # Show the properties dialog for the operator
    
# Function to add the Operator to the Blender UI menu
def menu_func(self, context):
    self.layout.operator(RockGeneratorOperator.bl_idname, text=RockGeneratorOperator.bl_label)

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(RockGenerator)        
    bpy.utils.register_class(RockGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(RockGenerator)        
    bpy.utils.unregister_class(RockGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

# If the script is executed (not imported), register the classes
if __name__== "__main__":
    register()