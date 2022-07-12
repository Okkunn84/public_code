import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    BoolProperty,
    StringProperty,
    PointerProperty
)

#-----------------------------------------------------------------------------

bl_info = {
    "name": "Instance_Copy_Replace",
    "author": "Yohhei Suzuki",
    "version": (3, 0),
    "blender": (2, 80, 0),
    "location": "3D ViewPort > Sidebar > [Utility]",
    "description": "Replace Source Object with Selected Objects.",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class Replace_OT_OP(bpy.types.Operator):
    bl_idname = "object.replace_op"
    bl_label = "OP"
    bl_description = "Instance_Copy_Replace"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mode = bpy.context.scene.replace_prop_enum
        source_object = bpy.context.scene.source_object_pointer
        mesh = source_object.data
        target_objects = bpy.context.selected_objects
        
        #decision: instance or copy replace
        if mode == 'INSTANCE':
            linked = True
        else:
            linked = False
        
        def duplicate_object_function(_linked):
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":_linked,
                                            "mode":'TRANSLATION'},
                                            TRANSFORM_OT_translate={"value":(0, 0, 0),
                                            #TRANSFORM_OT_translate={"value":value,
                                            "orient_axis_ortho":'X', "orient_type":'GLOBAL',
                                            "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)),
                                            "orient_matrix_type":'GLOBAL',
                                            "constraint_axis":(False, False, False),
                                            "mirror":False,
                                            "use_proportional_edit":False,
                                            "proportional_edit_falloff":'SMOOTH',
                                            "proportional_size":1,
                                            "use_proportional_connected":False,
                                            "use_proportional_projected":False,
                                            "snap":False,
                                            "snap_target":'CLOSEST',
                                            "snap_point":(0, 0, 0),
                                            "snap_align":False,
                                            "snap_normal":(0, 0, 0),
                                            "gpencil_strokes":False,
                                            "cursor_transform":False,
                                            "texture_space":False,
                                            "remove_on_cancel":False,
                                            "view2d_edge_pan":False,
                                            "release_confirm":False,
                                            "use_accurate":False,
                                            "use_automerge_and_split":False}
                                            )

        #add empty and link to the collection                               
        def add_empty(loc):
            o = bpy.data.objects.new( "empty", None )
            users_collection = source_object.users_collection[0]
            
            if bpy.context.scene.make_new_collection_prop_bool:
                make_new_collection().objects.link(o)
            else:
                users_collection.objects.link(o)
            o.empty_display_size = 2
            o.empty_display_type = 'CUBE'
            o.location = loc
            
            return o
        
        def select_source_object_children():
            #select all the children
            if bpy.context.scene.all_children_prop_bool == True:
                bpy.context.view_layer.objects.active = source_object
                bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
                source_object.select_set(True)
                bpy.context.view_layer.objects.active = source_object
            else:
                bpy.context.view_layer.objects.active = source_object
                source_object.select_set(True)

        def make_new_collection():
            #make new collection or link object to the collection
            collection_name = bpy.context.scene.collection_name_string
            collection_list = [col.name for col in bpy.data.collections]
            if collection_name in collection_list:
                replaced_collection = bpy.data.collections[collection_name]
            else:
                replaced_collection = bpy.data.collections.new(name=collection_name)
                bpy.context.scene.collection.children.link(replaced_collection)
            return replaced_collection
       
       
        def search_parent_of_selected_objects(selected_objects):
            children_list = []
            for o in selected_objects:
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
                children = bpy.context.selected_objects
                print("children",children)
                children_list.append(len(children))
                bpy.ops.object.select_all(action='DESELECT')
                
            max_value = max(children_list)
            max_index = children_list.index(max_value)
            print("children_list",children_list)
            print("max_value",max_value)
            print("max_index",max_index)
            
            return max_index
        
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None
        print("target_objects",target_objects)
        bpy.context.view_layer.objects.active = source_object         
            
        


        #duplicate source objects
        #repeat number of o times
        for o in target_objects:
            if o.animation_data is None:
                select_source_object_children()
                duplicate_object_function(linked)
                objects = bpy.context.selected_objects

                bpy.ops.object.select_all(action='DESELECT')
                index = search_parent_of_selected_objects(objects)
                #objects[index].select_set(True)
                print("objects[index]",objects[index])
                objects[index].location = o.location
                
                bpy.data.objects.remove(o)
            else:
                select_source_object_children()
                duplicate_object_function(linked)
                objects = bpy.context.selected_objects
                
                bpy.ops.object.select_all(action='DESELECT')
                index = search_parent_of_selected_objects(objects)
                print("objects[index]",objects[index]) 
                objects[index].location = o.location

                objects[index].select_set(True)
                parent_empty = add_empty(o.location)
                bpy.context.view_layer.objects.active = parent_empty
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                
                #test
                new_action = o.animation_data.action.copy()
                parent_empty.animation_data_create()
                parent_empty.animation_data.action = new_action    #bpy.data.actions.new(name="MyAction")
                parent_empty.rotation_mode = 'QUATERNION'

                bpy.data.objects.remove(o)


                
            bpy.ops.object.select_all(action='DESELECT')
            
            #make duplicated object into collection
            if bpy.context.scene.make_new_collection_prop_bool:
                for ob in objects:
                    for collection in ob.users_collection:
                        collection.objects.unlink(ob)
                        make_new_collection().objects.link(ob)                      
            
        self.report({'INFO'}, "Replace Completed.")
        print("Operator {} was executed.".format(self.bl_idname))

        return {'FINISHED'}
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class Replace_PT_CustomPanel(bpy.types.Panel):
    
    bl_label = "Instance_Copy_Replace"       
    bl_space_type = 'VIEW_3D'         
    bl_region_type = 'UI'      
    bl_category = "[Utility]"     
    bl_context = "objectmode"       
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SNAP_FACE')
        
    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        
        layout.label(text="Replace Settings :")
        col = layout.column(align=True)
        
        col.prop(scene, "replace_prop_enum", text="Replace Mode")
        
        col = layout.column(align=False)
        col.prop(scene, "source_object_pointer", text="Source Object")
        col = layout.column(align=False)
        
        layout.prop(scene, "make_new_collection_prop_bool", text="Make New Collection")
        if bpy.context.scene.make_new_collection_prop_bool:
            layout.prop(scene, "collection_name_string", text="Collection Name")
        
        layout.prop(scene, "all_children_prop_bool", text="All Children")

        column = layout.column(align=False)
        column.operator(Replace_OT_OP.bl_idname, text="Replace")
        
#-----------------------------------------------------------------------------

def init_props():
    scene = bpy.types.Scene
    
    scene.replace_prop_enum = EnumProperty(
        name="replace_prop_enum",
        description="property(enum)",
        items=[
            ('INSTANCE', "INSTANCE", "INSTANCE"),
            ('COPY', "COPY", "COPY"),
        ],
        default='INSTANCE'
    )
    scene.all_children_prop_bool = BoolProperty(
        name="all_children_prop_bool",
        description="property(bool)",
        default=True
    )
    scene.make_new_collection_prop_bool = BoolProperty(
        name="make_new_collection_prop_bool",
        description="property(bool)",
        default=True
    ) 
    scene.source_object_pointer = PointerProperty(
        name="source_object_pointer",
        type=bpy.types.Object,
        description="property(Pointer)"
    )
    scene.collection_name_string = StringProperty(
        name="collection_name_string",
        description="property(string)",
        default="Replaced_Collection",
        maxlen=1024
    )
#-----------------------------------------------------------------------------

#delete property
def clear_props():
    scene = bpy.types.Scene
    del scene.replace_prop_enum
    del scene.all_children_prop_bool
    del scene.source_object_pointer

classes = [
    Replace_OT_OP,
    Replace_PT_CustomPanel
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()
    print("Enable Addon")


def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    print("Disable Addon")


if __name__ == "__main__":
    register()
