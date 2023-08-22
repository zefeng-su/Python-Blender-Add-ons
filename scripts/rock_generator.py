import bpy
import random

def clean_scene():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)

    for texture in bpy.data.objects:
        bpy.data.objects.remove(texture)    

def create_cube():
    bpy.ops.mesh.primitive_cube_add()
    return bpy.context.object

def modifier_apply(apply,name):
  if apply:
        bpy.ops.object.modifier_apply(modifier=name)

def subdiv(obj, name, levels, apply=True):
    modifier = obj.modifiers.new(type="SUBSURF", name=name)
    modifier.levels = levels
    modifier_apply(apply, modifier.name)

def create_voronoi(intensity, scale):
    texture = bpy.data.textures.new("voronoi", type="VORONOI")
    texture.distance_metric = "DISTANCE_SQUARED"
    texture.noise_intensity = intensity 
    texture.noise_scale = scale

    return texture
    
def displace(obj, name, apply=True):
    modifier = obj.modifiers.new(type="DISPLACE", name=name)
    texture = create_voronoi(
        intensity = random.uniform(0.1, 0.3),
        scale = random.uniform(0.75, 1)
    )
    modifier.texture = texture
    modifier_apply(apply, modifier.name)

    # print(dir(modifier))

def decimate(obj, name, ratio, apply=True):
    modifier = obj.modifiers.new(type="DECIMATE", name=name)
    modifier.ratio = ratio
    modifier_apply(apply, modifier.name)


def generate_rock():
    cube = create_cube()
    subdiv(cube, "subdivide", levels=5)
    displace(cube, "displace")
    decimate(cube, "decimate", ratio=0.2)
  
     
clean_scene()
generate_rock()  

 