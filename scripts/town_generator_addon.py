# Metadata information about the Blender plugin
bl_info = {
    "name": "Town Generator",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Generates a terrain, trees and buildings",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *
#pip install numpy if using external IDE, else it's included in blender script editor
import numpy as np 
import json
import mathutils
import math
import random

# Define the panel that will appear in the Blender UI  
class TownGenerator(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'TownGenerator' # Label for the panel
    bl_idname = 'OBJECT_PT_TownGenerator' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears 
    bl_category = 'Town Generator' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        
        # Create an operator with settings UI
        col = layout.column(align=True) # Create a new column in the layout
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator(TownGeneratorOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action          
class TownGeneratorOperator(bpy.types.Operator):
    '''Generates town with randomly placed trees and buildings''' # Tooltip that appears when hovering over the button
    bl_label = 'Generate Town' # Label for the button
    bl_idname = 'town.creation_operator' # Unique identifier for the operator
    bl_options = {"REGISTER", "UNDO"} # Enable undo for the operator

    # Define properties that appear as settings in the UI for this operator
    terrain_size_level : IntProperty(
        name = "Terrain Subdivision",
        description = "Subdivision level of Terrain",
        default= 20,
        min = 10, 
        max = 100
    )

    terrain_scale_level : IntProperty(
        name = "Terrain Scale",
        description = "Overall scale of Terrain",
        default= 100,
        min = 1, 
        max = 500
    )

    terrain_max_height_level : FloatProperty(
        name = "Terrain Max Height",
        description = "Max Height of Terrain",
        default= 2,
        min = 0.1, 
        max = 5.0
    ) 
    
    tree_alpha : IntProperty(
        name = "Trees Alpha",
        description = "Alpha distribution of Trees",
        default= 1,
        min = 1, 
        max = 10
    )

    tree_beta : IntProperty(
        name = "Trees Beta",
        description = "Beta distribution of Trees",
        default= 1,
        min = 1, 
        max = 10
    )

    tree_num : IntProperty(
        name = "Trees Num",
        description = "Number of Trees",
        default= 20,
        min = 1, 
        max = 250
    )

    tree_distro : IntProperty(
        name = "Trees Density",
        description = "Density distribution of Trees",
        default= 60,
        min = 1, 
        max = 500
    )

    house_alpha : IntProperty(
        name = "Houses Alpha",
        description = "Alpha distribution of Houses",
        default= 1,
        min = 1, 
        max = 10
    )

    house_beta : IntProperty(
        name = "Houses Beta",
        description = "Beta distribution of Houses",
        default= 1,
        min = 1, 
        max = 10
    )

    house_num : IntProperty(
        name = "Houses Num",
        description = "Number of Houses",
        default= 20,
        min = 1, 
        max = 250
    )

    house_distro : IntProperty(
        name = "Houses Density",
        description = "Density distribution of Houses",
        default= 60,
        min = 1, 
        max = 500
    )

    clear_previous_town : BoolProperty(
        name = "Clear previous town?",
        description = "Clears the scene before generating new town",
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
        
        # Check if the scene should be cleared before generating a new town
        if self.clear_previous_town:
            clean_scene()

        # Initialize collection and load configurations for tree and house paths
        collection = bpy.data.collections["Collection"]

        # The path belows assumes the config.json is in the path /Blender_Python/scripts/, change it to your own path 
        # Get example_JSON.json from git repository to see example of how to write the config.json
        
        # path for config.json that stores path of where the models are  
        with open('/Blender_Python/scripts/config.json', 'r') as f:
            config = json.load(f)

        tree_path1 = config['TREE_PATH1']
        tree_path2 = config['TREE_PATH2']
        tree_path3 = config['TREE_PATH3']
        house_path1 = config['HOUSE_PATH1']
        house_path2 = config['HOUSE_PATH2']
        house_path3 = config['HOUSE_PATH3']
        
        # Helper function to add a Shrinkwrap constraint to an object, in this case the terrain
        def add_shrinkwrap(data, target):
            constraint = data.constraints.new('SHRINKWRAP')
            constraint.target = target
            constraint.shrinkwrap_type = "PROJECT"
            constraint.project_axis = "NEG_Z"

        # Helper function to rotate an object in a random direction
        def random_direction(obj):
            obj.delta_rotation_euler = [0,0,random.uniform(0, math.pi * 2)]

        # Helper function to randomly scale the size of an object
        def random_size(obj):
            value = random.uniform(0.25, 0.5)
            obj.delta_scale = [obj.delta_scale[0] + value, obj.delta_scale[1] + value, obj.delta_scale[2] + value]

        # Helper function to check if an object is near other objects in a list
        def isNearObjects(obj,arr,min_distance):
            position = mathutils.Vector((obj[0], obj[1], obj[2])) # Convert the object's (x, y, z) coordinates to a Vector for easier calculations
            result = False # Initialize result to False. This will be set to True if obj is near any object in arr
            
            # Loop through each object in the array 
            for i in arr:
                # Check if the result is already True; if it is, no need to continue checking
                if not result:  
                    target_position = mathutils.Vector((i[0], i[1], i[2])) # Convert the coordinates of the object in 'arr' to a Vector
                    direction = (target_position - position) # Calculate the vector difference between obj and the current object in 'arr'
                    distance = math.sqrt(math.pow(direction.x,2) + math.pow(direction.y,2)) # Calculate the Euclidean distance between obj and the current object in 'arr'
                    
                    # Check if the distance is less than or equal to the specified minimum distance
                    if min_distance >= distance:
                        result=True # If so, set result to True and exit the loop

            return result # Return the result: True if obj is near any object in 'arr', False otherwise
        
        # Initialize list to keep track of object positions
        used_positions=[]

        #-------------------------------------------
        # terrain
        #-------------------------------------------

        # Create a new mesh and object for the terrain
        plane_mesh = bpy.data.meshes.new("terrain_plane")
        plane_obj = bpy.data.objects.new("TerrainObject", plane_mesh)

        # Link the object to the scene collection
        collection = bpy.context.scene.collection
        collection.objects.link(plane_obj)

        # Retrieve properties from the operator's UI
        terrain_size = self.terrain_size_level
        terrain_scale =  self.terrain_scale_level
        terrain_max_height = self.terrain_max_height_level  

        # Initialize empty lists for vertices, edges, and faces
        verts = []
        edges = []
        faces = []

        # Generate grid coordinates for the terrain ----------------------------------------------------------------------------------
        # Using NumPy's linspace function to create an array of evenly spaced values.
        # Each array goes from -scale/2 to scale/2 and has 'size' number of points.
        # The idea is to create a square grid where the length of each side is 'scale',  and the grid is centered at the origin (0,0).
        # ----------------------------------------------------------------------------------------------------------------------------
        x_coords = np.linspace(-terrain_scale / 2, terrain_scale / 2, terrain_size) # x_coords contains the x-coordinates of each vertex in the grid
        y_coords = np.linspace(-terrain_scale / 2, terrain_scale / 2, terrain_size) # y_coords contains the y-coordinates of each vertex in the grid
        x_grid, y_grid = np.meshgrid(x_coords, y_coords) # Create a 2D grid using NumPy's meshgrid function.

        # Generate random height values for the Z-axis 
        z_coords = np.random.uniform(0, terrain_max_height, size=(terrain_size, terrain_size))

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
        for i in range(terrain_size - 1):
            for j in range(terrain_size - 1):
                v1 = i * terrain_size + j # v1 is the vertex at the top-left corner of the cell
                v2 = v1 + 1 # v2 is the vertex at the top-right corner of the cell
                v3 = (i + 1) * terrain_size + j + 1 # v3 is the vertex at the bottom-right corner of the cel
                v4 = (i + 1) * terrain_size + j # v4 is the vertex at the bottom-left corner of the cell
                # Append the face defined by the four corner vertices (v1, v2, v3, v4)
                # The order matters: vertices are specified in counter-clockwise order to ensure the face normal is oriented correctly
                faces.append((v1, v2, v3, v4))

        # Populate the mesh data from generated vertices, edges, and faces
        plane_mesh.from_pydata(verts, edges, faces) # create a mesh object from, a list of vertices, a list of edges, and a list of faces.
        plane_mesh.update() # Refreshes to ensure the mesh updates and recalculates its normals and other derived data

        # Enable smoothing for all polygons
        for polygon in plane_mesh.polygons:
            polygon.use_smooth = True

        # Create terrain material and apply it to the terrain object
        def add_material(obj):
            material = bpy.data.materials.new(name="Terrain_Mat")
            material.diffuse_color = 0.5,0.481,0.108,1
            material.specular_intensity = 0
            material.roughness = 1
            obj.data.materials.append(material)

        add_material(plane_obj)    

        #-------------------------------------------
        # trees
        #-------------------------------------------

        #beta distribution
        alpha = self.tree_alpha  # α parameter, note:(should be > 0)
        beta = self.tree_beta # β parameter, note:(should be > 0)
        forest_size = self.tree_num # number of mesh generated
        forest_scale = self.tree_distro # distribution, smaller value = more dense population
        rng = np.random.default_rng()

        # Suppose size = 50 and scale = 50, the range of values would be [0, 50]. Subtracting 2(size/2) from each value shifts the range to [-25, 25]. This makes the 3D distribution of cubes centered around the world origin (0,0,0) in Blender.
        beta_random = rng.beta(alpha,beta, size=(forest_size,2))* forest_scale  
        centered_values = beta_random - forest_scale/2

        # Expected output array of nested array, each with have length 2, index 0 represent x axis, index 1 represent y axis
        # print(beta_random) 

        tree_arr= []
        
        # Append imported models
        with bpy.data.libraries.load(tree_path1) as (data_from, data_to):
            data_to.objects.append(data_from.objects[0])
        tree_arr.append(data_to.objects[0])

        with bpy.data.libraries.load(tree_path2) as (data_from, data_to):
            data_to.objects.append(data_from.objects[0])
        tree_arr.append(data_to.objects[0])

        # Loop through each unique coordinate in 'centered_values'
        # 'np.unique' is used to remove duplicate coordinates    
        for i in np.unique(centered_values,axis=0):

            # Check if the current position [i[0], i[1], 3] is near any previously used position
            # 'isNearObjects' returns True if the point is near any in 'used_positions' within a distance of 3 units
            if not isNearObjects([i[0], i[1], 3],used_positions,3):
                obj = tree_arr[random.randint(0,len(tree_arr)-1)].copy() # Randomly choose a tree model from 'tree_arr' and create a copy of it
                obj.location = (i[0], i[1], 3)  # Set the location of the copied tree object to the current coordinates
                collection.objects.link(obj) # Link the new tree object to the scene's collection
                add_shrinkwrap(obj,plane_obj) # Apply a Shrinkwrap constraint to the tree object to make it stick to the terrain
                random_direction(obj)  # Randomly rotate the tree object to give it a more natural look
                random_size(obj) # Randomly scale the size of the tree object for variety
                used_positions.append([i[0], i[1], 3]) # Append the current coordinates to 'used_positions' so that future trees won't be placed too close to this one

        #----------------------------------------------------
        # town
        # same logic as trees, see above comments for details
        #----------------------------------------------------
        #beta distribution
        town_alpha = self.house_alpha # α parameter, note:(should be > 0)
        town_beta = self.house_beta # β parameter, note:(should be > 0)
        town_size = self.house_num # number of mesh generated
        town_scale = self.house_distro # distribution, smaller value = more dense population
        rng = np.random.default_rng()

        town_beta_random = rng.beta(town_alpha,town_beta, size=(town_size,2))* town_scale  
        town_centered_values = town_beta_random - town_scale/2

        houses_arr = []
        with bpy.data.libraries.load(house_path1) as (data_from, data_to):
            data_to.objects.append(data_from.objects[0])
        houses_arr.append(data_to.objects[0])

        with bpy.data.libraries.load(house_path3) as (data_from, data_to):
            data_to.objects.append(data_from.objects[0])
        houses_arr.append(data_to.objects[0])

        for i in np.unique(town_centered_values,axis=0):
            if not isNearObjects([i[0], i[1], 3],used_positions,3):
                obj = houses_arr[random.randint(0,len(houses_arr)-1)].copy()
                obj.location = (i[0], i[1], 3)
                collection.objects.link(obj)
                add_shrinkwrap(obj,plane_obj)
                random_direction(obj)
                random_size(obj)
                used_positions.append([i[0], i[1], 3])    

        return {'FINISHED'} # Indicate that the operation was successful
     
    # Invoke function is called to show the settings dialog before executing the operator
    def invoke(self, context, event):
        wm = context.window_manager # Get the window manager
        return wm.invoke_props_dialog(self) # Show the properties dialog for the operator

# Function to add the Operator to the Blender UI menu    
def menu_func(self, context):
    self.layout.operator(TownGeneratorOperator.bl_idname, text=TownGeneratorOperator.bl_label)

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(TownGenerator)        
    bpy.utils.register_class(TownGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(TownGenerator)        
    bpy.utils.unregister_class(TownGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

# If the script is executed (not imported), register the classes
if __name__== "__main__":
    register()