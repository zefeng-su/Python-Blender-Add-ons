import bpy

# copy paste this function to new script and run to create multiple cubes for quick testing  
 
# def create_cubes(size, numCube, distance):
#     for i in range(numCube):
#         bpy.ops.mesh.primitive_cube_add(size=size)
#         cube_obj = bpy.context.active_object
#         cube_obj.location.z = i * distance

# # Call the function with desired properties
# create_cubes(size=4, numCube=15, distance=5)

#select the items want to rename then run script

def rename (prefix, name, suffix ):

    for obj in bpy.context.selected_objects:
        obj.name = (f"{prefix}_{name}_{suffix}")
        obj.data.name = obj.name 

rename ('new', 'cube', 'name')