import bpy
#pip install numpy if using external IDE, else it's included in blender 
import numpy as np 

for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

# Create a new mesh and object
plane_mesh = bpy.data.meshes.new("terrain_plane")
plane_obj = bpy.data.objects.new("TerrainObject", plane_mesh)

# Link the object to the scene collection
collection = bpy.context.scene.collection
collection.objects.link(plane_obj)

size = 21
scale = 100
max_height = 3   

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