import bpy
import numpy as np

#clear blender scene
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

#beta distribution
alpha = 1  # α parameter, note:(should be > 0)
beta = 1 # β parameter, note:(should be > 0)
size = 50 # number of mesh generated
scale = 30 # distribution, smaller value = more dense population
rng = np.random.default_rng()

# suppose size = 50 and scale = 50, the range of values would be [0, 50]. Subtracting 2(size/2) from each value shifts the range to [-25, 25]. This makes the 3D distribution of cubes centered around the world origin (0,0,0) in Blender.
beta_random = rng.beta(alpha,beta, size=(size,2))* scale  
centered_values = beta_random - scale/2

# expected output array of nested array, each with have length 2, index 0 represent x axis, index 1 represent y axis
# print(beta_random) 

for i in centered_values:
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        enter_editmode=False, 
        align='WORLD', 
        location=(
            i[0], # x-axis
            i[1], # y-axis
            0 # z-axis
        ), 
        scale=(
            0.25, # x-axis
            0.25, # y-axis
            1 # z-axis
        )
    )

