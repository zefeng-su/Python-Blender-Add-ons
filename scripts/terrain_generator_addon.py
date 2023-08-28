import bpy
from bpy.props import *
#pip install numpy if using external IDE, else it's included in blender script editor
import numpy as np 

class TerrainGenerator(bpy.types.Panel):
    #creates panel on sidebar
    bl_label = 'TerrainGenerator'
    bl_idname = 'OBJECT_PT_TerrainGenerator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Terrain Generator'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.operator(TerrainGeneratorOperator.bl_idname)

class TerrainGeneratorOperator(bpy.types.Operator):
    '''Generates random Terrain''' #type tool tip here
    bl_label = 'Generate Terrain'
    bl_idname = 'rock.creation_operator'
    bl_options = {"REGISTER", "UNDO"}

    #create properties

    size_level : IntProperty(
        name = "Subdivide level",
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

    def execute(self, context):
        #insert script here
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)

        # Create a new mesh and object
        plane_mesh = bpy.data.meshes.new("terrain_plane")
        plane_obj = bpy.data.objects.new("TerrainObject", plane_mesh)

        # Link the object to the scene collection
        collection = bpy.context.scene.collection
        collection.objects.link(plane_obj)

        size = self.size_level
        scale = self.scale_level
        max_height = self.max_height_level  

        # Generate vertices, edges, and faces
        verts = []
        edges = []
        faces = []

        x_coords = np.linspace(-scale / 2, scale / 2, size)
        y_coords = np.linspace(-scale / 2, scale / 2, size)

        x_grid, y_grid = np.meshgrid(x_coords, y_coords)

        # Generate random height variations
        z_coords = np.random.uniform(0, max_height, size=(size, size))

        verts = np.column_stack((x_grid.flatten(), y_grid.flatten(), z_coords.flatten()))

        for i in range(size - 1):
            for j in range(size - 1):
                v1 = i * size + j
                v2 = v1 + 1
                v3 = (i + 1) * size + j + 1
                v4 = (i + 1) * size + j
                faces.append((v1, v2, v3, v4))

        plane_mesh.from_pydata(verts, edges, faces)
        plane_mesh.update()

        for polygon in plane_mesh.polygons:
            polygon.use_smooth = True

        return {'FINISHED'}
    
def menu_func(self, context):
    self.layout.operator(TerrainGeneratorOperator.bl_idname, text=TerrainGeneratorOperator.bl_label)

def register():
    bpy.utils.register_class(TerrainGenerator)        
    bpy.utils.register_class(TerrainGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(TerrainGenerator)        
    bpy.utils.unregister_class(TerrainGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__== "__main__":
     register()