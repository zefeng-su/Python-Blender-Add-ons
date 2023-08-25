import bpy
#pip install numpy if using external IDE, else it's included in blender script editor
import numpy as np 
import json

#clear blender scene
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

collection = bpy.data.collections["Collection"]

# put path in config.json (in same folder as script) in this format
# {"BLENDER_MODEL_PATH": "/path/folder/blenderFileName.blend"}
  
with open('config.json', 'r') as f:
    config = json.load(f)

tree_path = config['TREE_PATH']
house_path = config['HOUSE_PATH']

#-------------------------------------------
# terrain
#-------------------------------------------

# Create a new mesh and object
plane_mesh = bpy.data.meshes.new("terrain_plane")
plane_obj = bpy.data.objects.new("TerrainObject", plane_mesh)

# Link the object to the scene collection
collection = bpy.context.scene.collection
collection.objects.link(plane_obj)

terrain_size = 20
terrain_scale = 70
terrain_max_height = 1  

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

#-------------------------------------------
# trees
#-------------------------------------------

#beta distribution
alpha = 1  # α parameter, note:(should be > 0)
beta = 1 # β parameter, note:(should be > 0)
forest_size = 25 # number of mesh generated
forest_scale = 50 # distribution, smaller value = more dense population
rng = np.random.default_rng()

# suppose size = 50 and scale = 50, the range of values would be [0, 50]. Subtracting 2(size/2) from each value shifts the range to [-25, 25]. This makes the 3D distribution of cubes centered around the world origin (0,0,0) in Blender.
beta_random = rng.beta(alpha,beta, size=(forest_size,2))* forest_scale  
centered_values = beta_random - forest_scale/2

# expected output array of nested array, each with have length 2, index 0 represent x axis, index 1 represent y axis
# print(beta_random) 

with bpy.data.libraries.load(tree_path) as (data_from, data_to):
    data_to.objects.append(data_from.objects[0])

for i in centered_values:
    obj = data_to.objects[0].copy()
    obj.location = (i[0], i[1], 0)
    collection.objects.link(obj)

#-------------------------------------------
# town
#-------------------------------------------
town_size = 10
town_scale = 20

town_position_x = 3
town_position_y = 3

# parametric equation of the circle centered at the origin P (x, y) = P (r cos θ, r sin θ), where 0 ≤ θ ≤ 2π.

town_t = np.linspace(0, 2*np.pi, town_size)
town_formula_x = ((town_scale * np.cos(town_t)) + town_position_x)[:, np.newaxis]
town_formula_y = ((town_scale * np.sin(town_t)) + town_position_y)[:, np.newaxis]

town_coor_set = np.hstack((town_formula_x,town_formula_y))

with bpy.data.libraries.load(house_path) as (data_from, data_to):
    data_to.objects.append(data_from.objects[0])

for i in town_coor_set:
    obj = data_to.objects[0].copy()
    obj.location = (i[0], i[1], 0)
    collection.objects.link(obj)
