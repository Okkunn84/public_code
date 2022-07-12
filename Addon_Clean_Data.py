import bpy
import os
#-----------------------------------------------------------------------------

bl_info = {
    "name": "Clean Data",
    "author": "Yohhei Suzuki",
    "version": (3, 0),
    "blender": (2, 80, 0),
    "location": "3D ViewPort > Sidebar > [Data]",
    "description": "delete unused data.",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}

#-----------------------------------------------------------------------------

    
#delete unused data
class Delete_Unused_Data_OT_OP(bpy.types.Operator):
    bl_idname = "object.deleteunuseddata_op"
    bl_label = "OP"
    bl_description = "DeleteUnusedData"
    bl_options = {'REGISTER', 'UNDO'}
    
    # メニューを実行したときに呼ばれるメソッド
    def execute(self, context):
        
        def delete_un_used_data():
            original_type = bpy.context.area.type
            bpy.context.area.type = "OUTLINER"
            bpy.context.space_data.display_mode = 'ORPHAN_DATA'
            bpy.ops.outliner.orphans_purge()
            bpy.context.area.type = original_type
            
        delete_un_used_data()
        bpy.ops.wm.save_as_mainfile()
        
        self.report({'INFO'}, "Delete Unused Data.")
        print("Operator {} was executed.".format(self.bl_idname))

        return {'FINISHED'}
    
#-----------------------------------------------------------------------------

class Data_Manage_PT_CustomPanel(bpy.types.Panel):
    
    bl_label = "Clean Data"      
    bl_space_type = 'VIEW_3D'     
    bl_region_type = 'UI'      
    bl_category = "[Data]"    
    bl_context = "objectmode"         
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SNAP_FACE')    
        
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        scene = context.scene
        
        row = layout.row()
        row.alignment = 'EXPAND'
        row.label(text="file size:")
        filepath = bpy.data.filepath
        mb = str(round(os.path.getsize(filepath)/1000000,2)) + " MB"
        row.label(text=mb)
        
        layout.operator(Delete_Unused_Data_OT_OP.bl_idname, text="Delete Unused Data")
        
#-----------------------------------------------------------------------------

classes = [
    Delete_Unused_Data_OT_OP,
    Data_Manage_PT_CustomPanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    print("Enable Addon")


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    print("Disable Addon")


if __name__ == "__main__":
    register()
    
#-----------------------------------------------------------------------------