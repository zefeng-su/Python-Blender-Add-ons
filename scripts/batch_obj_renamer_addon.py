# Metadata information about the Blender plugin
bl_info = {
    "name": "Batch Object Renamer",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Rename multiple selected objects",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *

# Define the panel that will appear in the Blender UI
class PanelClass(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'Batch Object Renamer' # Label for the panel
    bl_idname = 'OBJECT_PT_BatchRename' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears 
    bl_category = 'Batch Object Renamer' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        row = layout.row() # Create a new row in the layout
        row.operator(OperatorClass.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action
class OperatorClass(bpy.types.Operator):
    '''Rename multiple selected objects''' # Tooltip that appears when hovering over the button
    bl_label = 'Rename' # Label for the button
    bl_idname = 'batch_rename.creation_operator' # Unique identifier for the operator
    
    # Define properties that appear as settings in the UI for this operator
    prefix: StringProperty(
        name="Prefix_", 
        default="Prefix"
    )
    
    name: StringProperty(
        name="Name", 
        default="Name"
    )
    
    suffix: StringProperty(
        name="_Suffix", 
        default="Suffix"
    )

    # Insert script here to excute in this function
    def execute(self, context):
         
        # Function to rename objects based on the prefix, name, and suffix
        def rename (prefix, name, suffix):
            # Loop through each selected object in Blender
            for obj in bpy.context.selected_objects:
                # Rename the object and its data
                obj.name = (f"{prefix}_{name}_{suffix}")
                obj.data.name = obj.name 

        rename (self.prefix, self.name, self.suffix) # Call the rename function with the current settings

        return {'FINISHED'} # Indicate that the operation was successful
    
    # Invoke function is called to show the settings dialog before executing the operator
    def invoke(self, context, event):
        wm = context.window_manager # Get the window manager
        return wm.invoke_props_dialog(self) # Show the properties dialog for the operator

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(PanelClass)        
    bpy.utils.register_class(OperatorClass)    

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(PanelClass)        
    bpy.utils.unregister_class(OperatorClass)    

# If the script is executed (not imported), register the classes
if __name__== "__main__":
     register()