import bpy
from bpy.props import *
import random

class RockGenerator(bpy.types.Panel):
    #creates panel on sidebar
    bl_label = 'RockGenerator'
    bl_idname = 'OBJECT_PT_RockGenerator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rock Generator'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.operator(RockGeneratorOperator.bl_idname)

class RockGeneratorOperator(bpy.types.Operator):
    '''Generates random rock''' #type tool tip here
    bl_label = 'Generate Rock'
    bl_idname = 'rock.creation_operator'
    bl_options = {"REGISTER", "UNDO"}

     #create properties
    noise_scale : FloatProperty(
        name = "Noise",
        description = "The scale of the noise",
        default= 0.75,
        min = 0.75, 
        max = 1.0
    )

    intensity_scale : FloatProperty(
        name = "Intensity",
        description = "The intensity of the noise",
        default= 0.1,
        min = 0.1, 
        max = 0.3
    )

    subdivide_level : IntProperty(
        name = "Subdivide level",
        description = "Level of subdivision",
        default= 3,
        min = 2, 
        max = 5
    )

    decimate_ratio : FloatProperty(
        name = "Decimate",
        description = "Adjust to control polygon count",
        default= 0.2,
        min = 0.1, 
        max = 1.0
    )

    def execute(self, context):
        #insert script here
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

        def subdiv(obj, name, apply=True):
            modifier = obj.modifiers.new(type="SUBSURF", name=name)
            modifier.levels = self.subdivide_level
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
                intensity = self.intensity_scale,
                scale = self.noise_scale
            )
            modifier.texture = texture
            modifier_apply(apply, modifier.name)

            # print(dir(modifier))

        def decimate(obj, name, apply=True):
            modifier = obj.modifiers.new(type="DECIMATE", name=name)
            modifier.ratio = self.decimate_ratio
            modifier_apply(apply, modifier.name)


        def generate_rock():
            cube = create_cube()
            subdiv(cube, "subdivide")
            displace(cube, "displace")
            decimate(cube, "decimate")
             
        clean_scene()
        generate_rock()    

        return {'FINISHED'}
    
def menu_func(self, context):
    self.layout.operator(RockGeneratorOperator.bl_idname, text=RockGeneratorOperator.bl_label)

def register():
    bpy.utils.register_class(RockGenerator)        
    bpy.utils.register_class(RockGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(RockGenerator)        
    bpy.utils.unregister_class(RockGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__== "__main__":
     register()