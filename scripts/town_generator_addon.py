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
 
class TownGenerator(bpy.types.Panel):
    # Creates panel on sidebar
    bl_label = 'TownGenerator'
    bl_idname = 'OBJECT_PT_TownGenerator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Town Generator'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Create an operator with settings UI
        col = layout.column(align=True)
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator(TownGeneratorOperator.bl_idname)
        
class TownGeneratorOperator(bpy.types.Operator):
    '''Generates town with randomly placed trees and buildings''' # Type tool tip here
    bl_label = 'Generate Town'
    bl_idname = 'town.creation_operator'
    bl_options = {"REGISTER", "UNDO"}

    # Create properties
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
        name = "Houses Density",
        description = "Density distribution of Houses",
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

    def execute(self, context):
        # Insert script here
        def clean_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)

            for texture in bpy.data.objects:
                bpy.data.objects.remove(texture)    
     
        if self.clear_previous_town:
            clean_scene()

        collection = bpy.data.collections["Collection"]

        # The path belows assumes the config.json is in the path /Blender_Python/scripts/, change it to your own path 
        # Get example_JSON.json from git repository to see example of how to write config.json
        
        # path for config.json that stores path of where the models are  
        with open('/Blender_Python/scripts/config.json', 'r') as f:
            config = json.load(f)

        tree_path1 = config['TREE_PATH1']
        tree_path2 = config['TREE_PATH2']
        tree_path3 = config['TREE_PATH3']
        house_path1 = config['HOUSE_PATH1']
        house_path2 = config['HOUSE_PATH2']
        house_path3 = config['HOUSE_PATH3']
        
        # constraint models on terrain level
        def add_shrinkwrap(data, target):
            constraint = data.constraints.new('SHRINKWRAP')
            constraint.target = target
            constraint.shrinkwrap_type = "PROJECT"
            constraint.project_axis = "NEG_Z"
        

        def look_at(obj,target):
            position = mathutils.Vector((obj.location[0], obj.location[1], obj.location[2]))
            target_position = mathutils.Vector((target[0], target[1], target[2]))
            default_direction = mathutils.Vector((0, -1, 0))
            
            direction = (target_position - position).normalized()
            angle = math.acos( default_direction.dot(direction))
            
            rotation = default_direction.cross(direction).normalized()
            obj.delta_rotation_euler = [0,0,rotation[2]*angle]

        def random_direction(obj):
            obj.delta_rotation_euler = [0,0,random.uniform(0, math.pi * 2)]

        def random_size(obj):
            value = random.uniform(0.25, 0.5)
            obj.delta_scale = [obj.delta_scale[0] + value, obj.delta_scale[1] + value, obj.delta_scale[2] + value]

        def isNearObjects(obj,arr,min_distance):
            position = mathutils.Vector((obj[0], obj[1], obj[2]))
            result = False
            for i in arr:
                if not result:
                    target_position = mathutils.Vector((i[0], i[1], i[2]))
                    direction = (target_position - position)
                    distance = math.sqrt(math.pow(direction.x,2) + math.pow(direction.y,2))
                    if min_distance >= distance:
                        result=True
            return result

        used_positions=[]
        #-------------------------------------------
        # terrain
        #-------------------------------------------

        # Create a new mesh and object
        plane_mesh = bpy.data.meshes.new("terrain_plane")
        plane_obj = bpy.data.objects.new("TerrainObject", plane_mesh)

        # Link the object to the scene collection
        collection = bpy.context.scene.collection
        collection.objects.link(plane_obj)

        terrain_size = self.terrain_size_level
        terrain_scale =  self.terrain_scale_level
        terrain_max_height = self.terrain_max_height_level  
 

        # Generate vertices, edges, and faces
        verts = []
        edges = []
        faces = []

        x_coords = np.linspace(-terrain_scale / 2, terrain_scale / 2, terrain_size)
        y_coords = np.linspace(-terrain_scale / 2, terrain_scale / 2, terrain_size)

        x_grid, y_grid = np.meshgrid(x_coords, y_coords)

        # Generate random height variations
        z_coords = np.random.uniform(0, terrain_max_height, size=(terrain_size, terrain_size))

        verts = np.column_stack((x_grid.flatten(), y_grid.flatten(), z_coords.flatten()))

        for i in range(terrain_size - 1):
            for j in range(terrain_size - 1):
                v1 = i * terrain_size + j
                v2 = v1 + 1
                v3 = (i + 1) * terrain_size + j + 1
                v4 = (i + 1) * terrain_size + j
                faces.append((v1, v2, v3, v4))

        plane_mesh.from_pydata(verts, edges, faces)
        plane_mesh.update()

        for polygon in plane_mesh.polygons:
            polygon.use_smooth = True

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

        # suppose size = 50 and scale = 50, the range of values would be [0, 50]. Subtracting 2(size/2) from each value shifts the range to [-25, 25]. This makes the 3D distribution of cubes centered around the world origin (0,0,0) in Blender.
        beta_random = rng.beta(alpha,beta, size=(forest_size,2))* forest_scale  
        centered_values = beta_random - forest_scale/2

        # expected output array of nested array, each with have length 2, index 0 represent x axis, index 1 represent y axis
        # print(beta_random) 

        tree_arr= []
        
        with bpy.data.libraries.load(tree_path1) as (data_from, data_to):
            data_to.objects.append(data_from.objects[0])
        tree_arr.append(data_to.objects[0])

        with bpy.data.libraries.load(tree_path2) as (data_from, data_to):
            data_to.objects.append(data_from.objects[0])
        tree_arr.append(data_to.objects[0])
            
        for i in np.unique(centered_values,axis=0):
            if not isNearObjects([i[0], i[1], 3],used_positions,3):
                obj = tree_arr[random.randint(0,len(tree_arr)-1)].copy()
                obj.location = (i[0], i[1], 3)
                collection.objects.link(obj)
                add_shrinkwrap(obj,plane_obj)
                random_direction(obj)
                random_size(obj)
                used_positions.append([i[0], i[1], 3])

        #-------------------------------------------
        # town
        #-------------------------------------------
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
      

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def menu_func(self, context):
    self.layout.operator(TownGeneratorOperator.bl_idname, text=TownGeneratorOperator.bl_label)

def register():
    bpy.utils.register_class(TownGenerator)        
    bpy.utils.register_class(TownGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(TownGenerator)        
    bpy.utils.unregister_class(TownGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__== "__main__":
    register()