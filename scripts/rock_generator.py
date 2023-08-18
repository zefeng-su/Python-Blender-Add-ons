import bpy
import math

def clean_scene():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)

def create_cube():
    bpy.ops.mesh.primitive_cube_add(size=1)
    return bpy.context.object

def modifier_apply(apply,name):
  if apply:
        bpy.ops.object.modifier_apply(modifier=name)

def subdivide(obj, name, levels, apply=True):
    subdiv_mod = obj.modifiers.new(type='SUBSURF', name=name)
    subdiv_mod.levels = levels
    modifier_apply(apply, subdiv_mod.name)

def spherify(obj, name, apply=True):
    cast_mod = obj.modifiers.new(type='CAST', name=name)
    modifier_apply(apply, cast_mod.name)

def decimate(obj, name, angle, apply=True):
    decimate_mod = obj.modifiers.new(type='DECIMATE', name=name)
    decimate_mod.decimate_type="DISSOLVE"
    decimate_mod.angle_limit = math.radians(angle)
    decimate_mod.use_dissolve_boundaries = True
    modifier_apply(apply, decimate_mod.name)

def generate_rock():
    # create a cube
    cube = create_cube()
    
    # Subdivide  
    subdivide(cube,"subdiv_cube", 5, True)
   
    # Spherify
    spherify(cube, "cast_cube", True) 

    # Decimate
    decimate(cube, "decimate_cube", 25, True)
    
clean_scene()
generate_rock()   

 