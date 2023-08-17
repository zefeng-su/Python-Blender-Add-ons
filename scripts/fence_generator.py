import bpy
import random

for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

def set_origin_bottom(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    bpy.ops.transform.translate(value=(0, 0, obj.dimensions.z / 2))

def create_single_plank(height, thickness, angle):
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, 0, 0),
        rotation=(0, 0, angle)
    )
    plank = bpy.context.object
    plank.scale[0] = thickness  # x-axis
    plank.scale[2] = height  # z-axis
    if bpy.context.selected_objects:  # Check if any object is selected
        set_origin_bottom(bpy.context.selected_objects[0])

num_plank = 10
gap_plank = 0.1

for i in range(num_plank):
    thickness = random.uniform(0.2, 0.25)
    height = random.uniform(9.9, 10.2)
    angle = random.uniform(-0.1, 0.1)
    create_single_plank(height, thickness, angle)
    bpy.context.object.location[1] = (1 + gap_plank) * i  # along y-axis
