bl_info = {
    "name": "Batch Object Renamer",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Rename multiple selected objects",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *

class PanelClass(bpy.types.Panel):
    #creates panel on sidebar
    bl_label = 'Batch Object Renamer'
    bl_idname = 'OBJECT_PT_StudioLighting'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Batch Object Renamer'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.operator(OperatorClass.bl_idname)

class OperatorClass(bpy.types.Operator):
    '''Rename multiple selected objects''' #type tool tip here
    bl_label = 'Rename'
    bl_idname = 'batch_rename.creation_operator'
    
     # Add properties for prefix, name, and suffix
    prefix: StringProperty(name="Prefix", default="Prefix")
    name: StringProperty(name="Name", default="Name")
    suffix: StringProperty(name="Suffix", default="Suffix")

    def execute(self, context):
        #insert script here
        def rename (prefix, name, suffix):

            for obj in bpy.context.selected_objects:
                obj.name = (f"{prefix}_{name}_{suffix}")
                obj.data.name = obj.name 

        rename (self.prefix, self.name, self.suffix)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(PanelClass)        
    bpy.utils.register_class(OperatorClass)    

def unregister():
    bpy.utils.unregister_class(PanelClass)        
    bpy.utils.unregister_class(OperatorClass)    

if __name__== "__main__":
     register()