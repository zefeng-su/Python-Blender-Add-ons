import bpy
from bpy.props import *
from math import radians

class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    bl_options = {"REGISTER", "UNDO"}

    #create properties
    noise_scale : FloatProperty(
        name = "Noise Scale",
        description = "The scale of the noise",
        default= 1.0,
        min = 0.0, 
        max = 2.0,
    )

    # add-on code in here
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()

        cube_obj = bpy.context.active_object

        # 0:x 1:y z:2
        cube_obj.location[0] = 5
        cube_obj.location[1] = 0
        cube_obj.location[2] = 5

        cube_obj.rotation_euler[0] += radians(45)
        cube_obj.rotation_euler[1] = 0
        cube_obj.rotation_euler[2] = 0
        
        cube_obj.scale[0] = 2   
        cube_obj.scale[1] = 2
        cube_obj.scale[2] = 2 

        mod_subsurf = cube_obj.modifiers.new ("Subdivisions", 'SUBSURF') 
        mod_subsurf.levels = 3

        bpy.ops.object.shade_smooth()

        # mesh = cube_obj.data
        # for face in mesh.polygons:
        #     face.use_smooth = True

        mod_displace = cube_obj.modifiers.new ("Displacment", 'DISPLACE') 

        new_tex = bpy.data.textures.new("Texture","DISTORTED_NOISE")
        new_tex.noise_scale = self.noise_scale

        mod_displace.texture = new_tex

        new_mat = bpy.data.materials.new(name = "Material")
        cube_obj.data.materials.append(new_mat)

        new_mat.use_nodes = True
        nodes = new_mat.node_tree.nodes

        material_output = nodes.get("Material Output")
        node_emission = nodes.new(type="ShaderNodeEmission")

        #color node RGBA
        node_emission.inputs[0].default_value = (0.0,0.3,1.0,1) 

        #emission strength
        node_emission.inputs[1].default_value = 500.0

        links = new_mat.node_tree.links
        new_link = links.new(node_emission.outputs[0], material_output.inputs[0])
      
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)

# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.simple_operator()
