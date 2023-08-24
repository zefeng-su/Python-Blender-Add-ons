import bpy
import random

def clean_scene():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)

    for mat in bpy.data.objects:
        bpy.data.materials.remove(mat)

def create_cube(x_size, y_size, z_size):
    bpy.ops.mesh.primitive_cube_add(size=1)
    
    resize(x_size, y_size, z_size)
    align(x_size, y_size, z_size)

    return bpy.context.active_object 

# context_override boiler plate
def get_context_override():
    window = bpy.context.window
    screen = window.screen
    area = next (area for area in screen.areas if area.type=='VIEW_3D')
    region = next (region for region in area.regions if region.type=='WINDOW')

    return{
        'window': window,
        'screen': screen,
        'area': area,
        'region': region,
        'scene': bpy.context.scene
    }

def resize(x, y, z):
    bpy.ops.transform.resize(value=(x, y, z))

def align(x, y, z):
    bpy.ops.transform.translate(value=(x*0.5,y*0.5,z*0.5))


def loopcut(number_cuts, edge_index, offset):
    context_override = get_context_override()
    bpy.ops.mesh.loopcut_slide(context_override,
        MESH_OT_loopcut={
            "number_cuts":number_cuts,
            "smoothness":0,
            "falloff":'INVERSE_SQUARE',
            "object_index":0,
            "edge_index": edge_index,
            "mesh_select_mode_init":(False,True,False)
        },

        TRANSFORM_OT_edge_slide={
            "value":offset, 
            "single_side":False, 
            "use_even":False, 
            "flipped":False, 
            "use_clamp":True, 
            "mirror":True, 
            "snap":False, 
            "snap_elements":{'INCREMENT'}, 
            "use_snap_project":False, 
            "snap_target":'CLOSEST', 
            "use_snap_self":True, 
            "use_snap_edit":True, 
            "use_snap_nonedit":True, 
            "use_snap_selectable":False, 
            "snap_point":(0, 0, 0), 
            "correct_uv":True, 
            "release_confirm":False, 
            "use_accurate":False
        }     
    )

def book_edge_loops():
    bpy.ops.object.mode_set(mode="EDIT")
    loopcut(1,8,-0.8)

    loopcut(1,15,0)
    resize(0.85,1,1)
    
    loopcut(2,11,0)
    resize(2,1,1)

def update_mesh(obj):
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.update(calc_edges=False)

def get_faces(book):
    top_face = None
    bottom_face = None
    front_face = None

    update_mesh(book)
    for face in book.data.polygons:
        face_normal = face.normal
         
        if face_normal[2] == 1: 
            top_face = face

        if face_normal[2] == -1: 
            bottom_face = face
          
        if face_normal[1] == -1: 
            front_face = face        
        
    return top_face, bottom_face, front_face

def select_faces(obj, face_indexes):
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")

    for face_index in face_indexes:
        obj.data.polygons[face_index].select = True

def extrude(amount):
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.extrude_region_shrink_fatten(
        MESH_OT_extrude_region={
            "use_normal_flip":False, 
            "mirror":False
        },

        TRANSFORM_OT_shrink_fatten={
            "value":amount, 
            "use_even_offset": False,
            "mirror": False,
            "use_proportional_edit": False,
            "proportional_edit_falloff": 'SMOOTH',
            "proportional_size": 1,
            "snap":False, 
            "use_accurate":False,
        }
    )

def create_material(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color

    return material

def create_single_book(x_size, y_size, z_size):
    book = create_cube(x_size, y_size, z_size)
        
    book_edge_loops()

    top_face, bottom_face, front_face = get_faces(book)

    select_faces(
        book,
        [top_face.index, bottom_face.index,front_face.index]
    )

    extrude(random.uniform(-0.025, -0.05))
    
    cover_material = create_material("cover_material", (
        random.uniform(0,1), #R
        random.uniform(0,1), #G
        random.uniform(0,1), #B
        1 #B
    ))
    book.data.materials.append(cover_material)

    paper_material = create_material("paper_material", (0.9,0.9,0.9,1))
    book.data.materials.append(paper_material)
    bpy.context.object.active_material_index = 1
    bpy.ops.object.material_slot_assign()
                           
    bpy.ops.object.mode_set(mode="OBJECT")

def create_books(amt_books):
    x_pos = 0
    for i in range (amt_books):
        x_size = random.uniform(0.15, 0.3)
        y_size = random.uniform(0.7, 0.9)
        z_size = random.uniform(1.0, 1.2)
    
        create_single_book(x_size, y_size, z_size)

        bpy.ops.transform.translate(value=(x_pos,0,0))
        x_pos += x_size
 
clean_scene()
create_books(15)
