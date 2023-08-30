# Metadata information about the Blender plugin
bl_info = {
    "name": "Books Generator",
    "author": "Su Zefeng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Generates row of random books",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *
import random

# Define the panel that will appear in the Blender UI
class BookGenerator(bpy.types.Panel):
    # Create a panel on the sidebar in 3D view
    bl_label = 'BookGenerator' # Label for the panel
    bl_idname = 'OBJECT_PT_BookGenerator' # Unique identifier for the panel
    bl_space_type = 'VIEW_3D' # Space where the panel appears
    bl_region_type = 'UI' # Region of the space where the panel appears 
    bl_category = 'Book Generator' # Tab under which the panel appears

    # Draw the UI elements on the panel
    def draw(self, context):
        layout = self.layout # Get the layout of the panel
        obj = context.object # Get the currently selected object
        
        # Create an operator with settings UI
        col = layout.column(align=True) # Create a new column in the layout
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator(BookGeneratorOperator.bl_idname) # Add a button that triggers the Operator

# Define the operator that will perform the action           
class BookGeneratorOperator(bpy.types.Operator):
    '''Generates row of random books''' # Tooltip that appears when hovering over the button
    bl_label = 'Generate Books' # Label for the button
    bl_idname = 'books.creation_operator' # Unique identifier for the operator
    bl_options = {"REGISTER", "UNDO"} # Enable undo for the operator

    # Define properties that appear as settings in the UI for this operator
    amt_books : IntProperty(
        name = "Number of books",
        description = "Number of books to generate",
        default= 3,
        min = 1, 
        max = 50
    )

    clear_previous_book : BoolProperty(
        name = "Clear previous books?",
        description = "Clears the scene before generating new books",
        default = True
    )

    # Insert script here to excute in this function
    def execute(self, context):
         
        # Remove all existing objects from the Blender scene 
        def clean_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)

            for mat in bpy.data.objects:
                bpy.data.materials.remove(mat)

        # Create a cube object with specified dimensions
        def create_cube(x_size, y_size, z_size):
            bpy.ops.mesh.primitive_cube_add(size=1)
            
            resize(x_size, y_size, z_size)
            align(x_size, y_size, z_size)

            return bpy.context.active_object 

        # Context_override boiler plate
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
        
        # Function to resize an object
        def resize(x, y, z):
            bpy.ops.transform.resize(value=(x, y, z))

        # Function to align an object to the world origin
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

        # Function to add loop cuts to a cube to make it look like a book
        def book_edge_loops():
            bpy.ops.object.mode_set(mode="EDIT")
            loopcut(1,8,-0.8)

            loopcut(1,15,0)
            resize(0.85,1,1)
            
            loopcut(2,11,0)
            resize(2,1,1)

        # Update mesh geometry after operations
        def update_mesh(obj):
            bpy.ops.object.mode_set(mode="OBJECT")
            obj.data.update(calc_edges=False)

        # Identify faces of the cube that represent top, bottom, and front of a book
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
        
        # Function to select specific faces of a mesh
        def select_faces(obj, face_indexes):
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")

            for face_index in face_indexes:
                obj.data.polygons[face_index].select = True

         # Function to extrude selected faces
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

        # Function to create a new material with a given color
        def create_material(name, color):
            material = bpy.data.materials.new(name)
            material.diffuse_color = color

            return material

        # Function to create a single book
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

        # Function to create multiple books
        def create_books(amt_books):
            x_pos = 0
            for i in range (amt_books):
                x_size = random.uniform(0.15, 0.3)
                y_size = random.uniform(0.7, 0.9)
                z_size = random.uniform(1.0, 1.2)
            
                create_single_book(x_size, y_size, z_size)

                bpy.ops.transform.translate(value=(x_pos,0,0))
                x_pos += x_size

        # Clear the scene if the corresponding checkbox is checked
        if self.clear_previous_book:
            clean_scene()

        create_books(self.amt_books)

        return {'FINISHED'} # Indicate that the operation was successful
    
    # Invoke function is called to show the settings dialog before executing the operator
    def invoke(self, context, event):
        wm = context.window_manager # Get the window manager
        return wm.invoke_props_dialog(self) # Show the properties dialog for the operator

# Function to add the Operator to the Blender UI menu
def menu_func(self, context): 
    self.layout.operator(BookGeneratorOperator.bl_idname, text=BookGeneratorOperator.bl_label)

# Register the classes so that they appear in Blender
def register():
    bpy.utils.register_class(BookGenerator)        
    bpy.utils.register_class(BookGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.append(menu_func)

# Unregister the classes when the plugin is deactivated
def unregister():
    bpy.utils.unregister_class(BookGenerator)        
    bpy.utils.unregister_class(BookGeneratorOperator)    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

# If the script is executed (not imported), register the classes
if __name__== "__main__":
    register()