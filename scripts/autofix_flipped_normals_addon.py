# Metadata information about the Blender plugin
bl_info = {
    "name": "Fix flipped Normals",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Fix flipped Normals",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
 
# Define the panel that will appear in the Blender UI
class FixNormal(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'Fix flipped Normals' # Label for the panel
    bl_idname = 'OBJECT_PT_FixNormal' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears
    bl_category = 'Fix Flipped Normals' # Tab under which the panel appears

     # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        row = layout.row() # Create a new row in the layout
        row.operator(FixNormalOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action
class FixNormalOperator(bpy.types.Operator):
    '''Fix flipped Normals'''  # Tooltip that appears when hovering over the button
    bl_label = 'Run'  # Label for the button
    bl_idname = 'fix_normal.creation_operator' # Unique identifier for the operator

    # Insert script here to excute in this function
    def execute(self, context):
        # Function to flip normals for a given object
        def flip_normals(obj):
            bpy.context.view_layer.objects.active = obj # Set the active object
            bpy.ops.object.mode_set(mode='EDIT')  # Switch to Edit Mode
            bpy.ops.mesh.select_all(action='SELECT') # Select all vertices
            bpy.ops.mesh.normals_make_consistent(inside=False) # Make normals consistent
            bpy.ops.object.mode_set(mode='OBJECT') # Switch back to Object Mode

        # Main function that loops through selected objects and fixes their normals
        def main():
            selected_objects = bpy.context.selected_objects # Get all selected objects
            for obj in selected_objects: # Loop through each selected object
                if obj.type == 'MESH': # Check if the object is a mesh
                    bpy.context.view_layer.objects.active = obj  # Set the active object
                    bpy.ops.object.mode_set(mode='EDIT') # Switch to Edit Mode
                    bpy.ops.mesh.select_all(action='DESELECT') # Deselect all vertices
                    bpy.ops.mesh.select_all(action='SELECT') # Select all vertices
                    bpy.ops.mesh.select_all(action='INVERT') # Invert the current selection (selected becomes deselected, deselected becomes selected)

                    # Check if any vertex has a flipped normal (normal.z < 0)
                    flipped_normals = any([v.normal.z < 0 for v in bpy.context.active_object.data.vertices])
                    bpy.ops.object.mode_set(mode='OBJECT')  # Switch back to Object Mode
                    
                     # If flipped normals are found, call flip_normals function
                    if flipped_normals:
                        flip_normals(obj)
                    
        main() 
           
        return {'FINISHED'} # Indicate that the operation was successful

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(FixNormal)        
    bpy.utils.register_class(FixNormalOperator)    

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(FixNormal)        
    bpy.utils.unregister_class(FixNormalOperator)    

# If the script is executed (not imported), register the classes
if __name__== "__main__":
     register()