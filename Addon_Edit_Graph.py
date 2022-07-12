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
    "name": "Edit Graph",
    "author": "Yohhei Suzuki",
    "version": (3, 0),
    "blender": (2, 80, 0),
    "location": "3D ViewPort > Sidebar > [Animation]",
    "description": "Edit Graph",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Animation"
}

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class Graph_Clean_OT_OP(bpy.types.Operator):
    bl_idname = "object.graph_clean_op"
    bl_label = "OP"
    bl_description = "make graph clean"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        #clean
        def clean_graph(obj):
            current_area = bpy.context.area.type
            layer = bpy.context.view_layer
            bpy.context.area.type = "GRAPH_EDITOR"
            layer.update()
            bpy.ops.graph.clean()
            interpolation_type = bpy.context.scene.interpolation_prop_enum
            bpy.ops.graph.interpolation_type(type=interpolation_type)
            
            # switch back to original area
            bpy.context.area.type = current_area
        
        objects = bpy.context.selected_objects
        for obj in objects:
            clean_graph(obj)

        self.report({'INFO'}, "clean graph data.")
        print("Operator {} was executed.".format(self.bl_idname))

        return {'FINISHED'}
#-----------------------------------------------------------------------------

class Graph_Smooth_OT_OP(bpy.types.Operator):
    bl_idname = "object.graph_smooth_op"
    bl_label = "OP"
    bl_description = "make graph smooth"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        #smooth
        def Smooth_graph(obj):
            current_area = bpy.context.area.type
            layer = bpy.context.view_layer
            bpy.context.area.type = "GRAPH_EDITOR"
            layer.update()
            bpy.ops.graph.smooth()
            interpolation_type = bpy.context.scene.interpolation_prop_enum
            bpy.ops.graph.interpolation_type(type=interpolation_type)
            
            # switch back to original area
            bpy.context.area.type = current_area
        
        objects = bpy.context.selected_objects
        for obj in objects:
            Smooth_graph(obj)
        self.report({'INFO'}, "smooth graph data.")
        print("Operator {} was executed.".format(self.bl_idname))

        return {'FINISHED'}
#-----------------------------------------------------------------------------

class Reduction_Keyframes_OT_OP(bpy.types.Operator):
    bl_idname = "object.edit_graph_op"
    bl_label = "OP"
    bl_description = "edit graph"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        def keyframeEdit(obj,start,end):
            loc_step = bpy.context.scene.location_step_prop_int
            rot_step = bpy.context.scene.rotation_step_prop_int
            scl_step = bpy.context.scene.scale_step_prop_int
            hre_step = bpy.context.scene.hide_render_step_prop_int
            
            fc = obj.animation_data.action.fcurves
            for c in fc:
                if "hide_render" in c.data_path:
                    hr = True
                    break
                else:
                    hr = False
            
            for c in fc:
                if "rotation_euler" in c.data_path:
                    r_euler = True
                    break
                else:
                    r_euler = False
            
            if hr:
                if r_euler:
                    list = {'location':loc_step , 'rotation_euler':rot_step , 'scale':scl_step , 'hide_render':hre_step}
                else: #rotation_mode = "Quartanion"
                    list = {'location':loc_step , 'rotation_quaternion':rot_step , 'scale':scl_step , 'hide_render':hre_step}
            else:
                if r_euler:
                    list = {'location':loc_step , 'rotation_euler':rot_step , 'scale':scl_step}
                else: #rotation_mode = "Quartanion"
                    list = {'location':loc_step , 'rotation_quaternion':rot_step , 'scale':scl_step}                

            for num in range(start,end):
                if num == 0:
                    continue
                for key,value in list.items():
                    if not num % value == 0:
                        #bpy.context.scene.frame_set(num)
                        obj.keyframe_delete(key,frame = num)
                        #print("key:",key,"frame:",num)
                     
        objects = bpy.context.selected_objects
        start = bpy.context.scene.frame_start_prop_int
        end = bpy.context.scene.frame_end_prop_int
        for obj in objects:
            keyframeEdit(obj,start,end)
        return {'FINISHED'}
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------


class Edit_Graph_PT_CustomPanel(bpy.types.Panel):
    
    bl_label = "Edit Graph"       
    bl_space_type = 'VIEW_3D'       
    bl_region_type = 'UI'          
    bl_category = "[Animation]"   
    bl_context = "objectmode"  

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SNAP_FACE')
        
    def draw(self, context):
        
        icon1 = 'SNAP_FACE'
        
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        
        layout.separator()
        layout.label(text="Clean & Smooth Graph:")
        
        
        layout.prop(scene, "interpolation_prop_enum", text="Interpolation")
        layout.separator()
        column = layout.column(align=False)
        column.operator(Graph_Clean_OT_OP.bl_idname, text="Clean Graph")
        column.operator(Graph_Smooth_OT_OP.bl_idname, text="Smooth Graph")
        
        layout.separator()
        layout.label(text="Reduction Keyframes:")
        
        col = layout.column(align=True)
        col.prop(scene, "frame_start_prop_int", text="Frame Range Start")
        col.prop(scene, "frame_end_prop_int", text="End")
        
        col = layout.column(align=True)
        col.prop(scene, "location_step_prop_int", text="location_step")
        col.prop(scene, "rotation_step_prop_int", text="rotation_step")
        col.prop(scene, "scale_step_prop_int", text="scale_step")
        col.prop(scene, "hide_render_step_prop_int", text="hide_render_step")
        
        layout.separator()
        column = layout.column(align=False)
        column.operator(Reduction_Keyframes_OT_OP.bl_idname, text="Reduction Keyframes")
#-----------------------------------------------------------------------------

def init_props():
    scene = bpy.types.Scene
    
    scene.frame_start_prop_int = IntProperty(
        name="property1",
        description="frame_start_property(int)",
        default=0,
        min=0,
        max=255
    )
    scene.frame_end_prop_int = IntProperty(
        name="property1_1",
        description="frame_end_property(int)",
        default=100,
        min=1,
        max=500
    )
    scene.interpolation_prop_enum = EnumProperty(
        name="property4",
        description="property(enum)",
        items=[
            ('BEZIER', "BEZIER", "BEZIER"),
            ('LINEAR', "LINEAR", "LINEAR"),
            ('CONSTANT', "CONSTANT", "CONSTANT")
        ],
        default='BEZIER'
    )
    scene.location_step_prop_int = IntProperty(
        name="property1_2",
        description="location_step_property(int)",
        default=1,
        min=1,
        max=10
    )
    scene.rotation_step_prop_int = IntProperty(
        name="property1_3",
        description="rotation_step_property(int)",
        default=1,
        min=1,
        max=10
    )
    scene.scale_step_prop_int = IntProperty(
        name="property1_4",
        description="scale_step_property(int)",
        default=1,
        min=1,
        max=10
    )
    scene.hide_render_step_prop_int = IntProperty(
        name="property1_5",
        description="hide_render_step_property(int)",
        default=1,
        min=1,
        max=10
    )
    
    
#delete property
def clear_props():
    scene = bpy.types.Scene
    del mode_prop_enum
    del scene.frame_start_prop_int
    del scene.frame_end_prop_int
    del scene.interpolation_prop_enum
    
classes = [
    Graph_Clean_OT_OP,
    Graph_Smooth_OT_OP,
    Reduction_Keyframes_OT_OP,
    Edit_Graph_PT_CustomPanel
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
        
#-----------------------------------------------------------------------------