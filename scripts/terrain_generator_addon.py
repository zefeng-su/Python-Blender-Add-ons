# Metadata information about the Blender plugin
bl_info = {
    "name": "Terrain Generator",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Generates random Terrain",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *
#pip install numpy if using external IDE, else it's included in blender script editor
import numpy as np 

# Define the panel that will appear in the Blender UI 
class TerrainGenerator(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'TerrainGenerator' # Label for the panel
    bl_idname = 'OBJECT_PT_TerrainGenerator' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears 
    bl_category = 'Terrain Generator' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        row = layout.row() # Create a new row in the layout
        row.operator(TerrainGeneratorOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action  
class TerrainGeneratorOperator(bpy.types.Operator):
    '''Generates random Terrain''' # Tooltip that appears when hovering over the button
    bl_label = 'Generate Terrain' # Label for the button
    bl_idname = 'terrain.creation_operator' # Unique identifier for the operator
    bl_options = {"REGISTER", "UNDO"} # Enable undo for the operator

    # Define properties that appear as settings in the UI for this operator
    size_level : IntProperty(
        name = "Terrain Subdivision",
        description = "Subdivision level of Terrain",
        default= 20,
        min = 10, 
        max = 100
    )

    scale_level : IntProperty(
        name = "Terrain Scale",
        description = "Overall scale of Terrain",
        default= 100,
        min = 1, 
        max = 500
    )

    max_height_level : FloatProperty(
        name = "Max Height",
        description = "Max Height of Terrain",
        default= 2,
        min = 0.1, 
        max = 5.0
    )

    # Insert script here to excute in this function 
    def execute(self, context):

        # Remove all existing objects from the Blender scene 
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)

        # Create a new mesh and object for the terrain
        plane_mesh = bpy.data.meshes.new("terrain_plane")
        plane_obj = bpy.data.objects.new("TerrainObject", plane_mesh)

        # Link the object to the scene collection
        collection = bpy.context.scene.collection
        collection.objects.link(plane_obj)

        # Retrieve properties from the operator's UI
        size = self.size_level
        scale = self.scale_level
        max_height = self.max_height_level  

        # Initialize empty lists for vertices, edges, and faces
        verts = []
        edges = []
        faces = []

        # Generate grid coordinates for the terrain ----------------------------------------------------------------------------------
        # Using NumPy's linspace function to create an array of evenly spaced values.
        # Each array goes from -scale/2 to scale/2 and has 'size' number of points.
        # The idea is to create a square grid where the length of each side is 'scale',  and the grid is centered at the origin (0,0).
        # ----------------------------------------------------------------------------------------------------------------------------
        x_coords = np.linspace(-scale / 2, scale / 2, size) # x_coords contains the x-coordinates of each vertex in the grid
        y_coords = np.linspace(-scale / 2, scale / 2, size) # y_coords contains the y-coordinates of each vertex in the grid
        x_grid, y_grid = np.meshgrid(x_coords, y_coords) # Create a 2D grid using NumPy's meshgrid function.

        # Generate random height values for the Z-axis 
        z_coords = np.random.uniform(0, max_height, size=(size, size))

        # Combine X, Y, and Z coordinates into vertex data ---------------------------------------------------------------
        # Using NumPy's column_stack function to combine the 1D arrays of x, y, and z coordinates into a single 2D array.
        # Each row in this 2D array will represent a vertex in the format (x, y, z).
        # Before stacking, we flatten the 2D arrays x_grid, y_grid, and z_coords into 1D arrays.
        # This is necessary because column_stack expects 1D input arrays.
        # Flattening converts the 2D grid structure into a 1D list, but preserves the order of the vertices.
        # ----------------------------------------------------------------------------------------------------------------
        verts = np.column_stack((x_grid.flatten(), y_grid.flatten(), z_coords.flatten()))

        # Generate face indices based on grid structure
        # Loop through each 'cell' in the grid except the last row and column
        # (because faces are formed by connecting vertices in adjacent rows and columns)
        for i in range(size - 1):
            for j in range(size - 1):
                v1 = i * size + j # v1 is the vertex at the top-left corner of the cell
                v2 = v1 + 1 # v2 is the vertex at the top-right corner of the cell
                v3 = (i + 1) * size + j + 1 # v3 is the vertex at the bottom-right corner of the cell
                v4 = (i + 1) * size + j # v4 is the vertex at the bottom-left corner of the cell
                # Append the face defined by the four corner vertices (v1, v2, v3, v4)
                # The order matters: vertices are specified in counter-clockwise order to ensure the face normal is oriented correctly
                faces.append((v1, v2, v3, v4))

        # Populate the mesh data from generated vertices, edges, and faces
        plane_mesh.from_pydata(verts, edges, faces) # create a mesh object from, a list of vertices, a list of edges, and a list of faces.
        plane_mesh.update() # Refreshes to ensure the mesh updates and recalculates its normals and other derived data

        # Enable smoothing for all polygons
        for polygon in plane_mesh.polygons:
            polygon.use_smooth = True

        return {'FINISHED'} # Indicate that the operation was successful

# Function to add the Operator to the Blender UI menu    
def menu_func(self, context):
    self.layout.operator(TerrainGeneratorOperator.bl_idname, text=TerrainGeneratorOperator.bl_label)

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(TerrainGenerator)        
    bpy.utils.register_class(TerrainGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(TerrainGenerator)        
    bpy.utils.unregister_class(TerrainGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

# If the script is executed (not imported), register the classes
if __name__== "__main__":
     register()