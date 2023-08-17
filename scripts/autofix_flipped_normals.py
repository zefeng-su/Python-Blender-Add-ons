import bpy

def flip_normals(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

def main():
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.select_all(action='INVERT')
            flipped_normals = any([v.normal.z < 0 for v in bpy.context.active_object.data.vertices])
            bpy.ops.object.mode_set(mode='OBJECT')
            
            if flipped_normals:
                print(f"Flipping normals for object: {obj.name}")
                flip_normals(obj)
            else:
                print(f"No flipped normals found for object: {obj.name}")

main()
