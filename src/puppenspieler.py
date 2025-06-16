bl_info = {
    "name": " Puppenspieler",
    "author": "Fabio Nascimento",
    "version": (0, 7, 4),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Puppenspieler",
    "description": "Manage object hierarchy and order under categorized Empties",
    "category": "Object",
}

import bpy

addon_keymaps = []
key_defs = [
    ('F1', 'Armrest'),
    ('F2', 'Backrest'),
    ('F3', 'Cushion'),
    ('F4', 'Structure'),
    ('F5', 'Seat Legs')
]

def get_or_create_empty(name):
    empty = bpy.data.objects.get(name)
    if empty is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = bpy.context.active_object
        empty.name = name
    return empty

def get_children(group_name):
    group = bpy.data.objects.get(group_name)
    if group:
        return sorted([child for child in group.children if child.name.startswith(group_name + "_")], key=lambda x: x.name)
    return []

def add_to_group(obj, group_name):
    group_empty = get_or_create_empty(group_name)
    obj.parent = group_empty
    count = len(get_children(group_name))
    print(f"Children's count: {count}")
    obj.name = f"{group_name}_{count + 1}"

def swap_names(obj1, obj2, base):
    obj2_name = obj2.name
    obj1.name, obj2.name = "TEMP_NAME", obj1.name
    obj1.name = obj2_name


class OBJECT_OT_AddToGroup(bpy.types.Operator):
    bl_idname = "object.add_to_group"
    bl_label = "Add to Group"

    group: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.active_object
        print(f"Self.group: {self.group}")
        if obj:
            add_to_group(obj, self.group)
            return {'FINISHED'}
        return {'CANCELLED'}

class OBJECT_OT_MoveActiveUp(bpy.types.Operator):
    bl_idname = "object.move_active_up"
    bl_label = "Move Active Up"

    def execute(self, context):
        selected = context.active_object
        if selected and selected.parent:
            group = selected.parent.name
            children = get_children(group)
            index = children.index(selected) if selected in children else -1
            if index > 0:
                swap_names(children[index - 1], selected, group[:-1])
                return {'FINISHED'}
        return {'CANCELLED'}

class OBJECT_OT_MoveActiveDown(bpy.types.Operator):
    bl_idname = "object.move_active_down"
    bl_label = "Move Active Down"

    def execute(self, context):
        selected = context.active_object
        if selected and selected.parent:
            group = selected.parent.name
            children = get_children(group)
            index = children.index(selected) if selected in children else -1
            if 0 <= index < len(children) - 1:
                swap_names(selected, children[index + 1], group[:-1])
                return {'FINISHED'}
        return {'CANCELLED'}


class OBJECT_PT_PuppenspielerPanel(bpy.types.Panel):
    bl_label = "Puppenspieler (v" + '.'.join([str(x) for x in bl_info.get("version")]) + ")"
    bl_category = 'PACE'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        # layout = self.layout
        pass

class OBJECT_PT_PuppenspielerPanel_groups(bpy.types.Panel):
    bl_label = "Groups Operations"
    bl_idname = "OBJECT_PT_Puppenspieler_groups"
    bl_parent_id = "OBJECT_PT_PuppenspielerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        for key, group in key_defs:
            box.operator("object.add_to_group", icon='ADD', text=' [' + key + '] - ' + group).group = group

        box.separator()
        box.label(text="Reorder Selected")
        row = box.row()
        row.operator("object.move_active_up", text="Up", icon='TRIA_UP')
        row.operator("object.move_active_down", text="Down", icon='TRIA_DOWN')


#============== Set Pivot ==============
# c = bpy.context.scene.cursor
# o = bpy.context.active_object
# o.mode = 'OBJECT' || 'EDIT'
# bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
# bpy.ops.view3d.snap_cursor_to_selected()
# l = bpy.context.scene.cursor.location.copy()
# bpy.context.selected_objects

##TODO:"
# - Move selection to under cursor without changing positions
#   - If an Empty is selected, all other objects should be moved to under it
# - Move Parent Empty without changing the children position, based on 3D cursor or Selection(?)"

def set_pivot_object_mode(obj):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    pass

def set_pivot_edit_mode(obj):
    previous_cursor_location = bpy.context.scene.cursor.location.copy()
    previous_cursor_rotation = bpy.context.scene.cursor.rotation_euler.copy()
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.editmode_toggle()
    bpy.context.scene.cursor.location = previous_cursor_location
    bpy.context.scene.cursor.rotation_euler = previous_cursor_rotation
    pass

class OBJECT_OT_Set_Pivot(bpy.types.Operator):
    bl_idname = "object.set_pivot"
    bl_label = "Set Pivot"

    # group: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.active_object
        # objs = bpy.context.selected_objects
        # print(f"Self.group: {self.group}")
        if obj:
            if obj.type == 'MESH':
                if obj.mode == 'OBJECT':
                    set_pivot_object_mode(obj)
                elif obj.mode == 'EDIT':
                    set_pivot_edit_mode(obj)
            elif obj.type == 'EMPTY':
                # if it is an Empty
                pass
            return {'FINISHED'}
        return {'CANCELLED'}


class OBJECT_PT_PuppenspielerPanel_pivots(bpy.types.Panel):
    bl_label = "Pivot Operations"
    bl_idname = "OBJECT_PT_PuppenspielerPanel_pivots"
    bl_parent_id = "OBJECT_PT_PuppenspielerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        hot_key = 'F9'
        label = 'Set Pivot'
        layout = self.layout        
        box = layout.box()
        box.separator()
        if context.mode == 'OBJECT':
            label = '3D Cursor'
        else:
            label = 'Selection'


        box.operator("object.set_pivot", icon='OUTLINER_DATA_EMPTY', text=f'[{hot_key}] - Set Pivot ({label})')
        # box.label(text="Set pivot")
        # for key, group in key_defs:
        #     box.operator("object.add_to_group", icon='ADD', text=' [' + key + '] - ' + group).group = group

        # box.separator()
        # box.label(text="Reorder Selected")
        # row = box.row()
        # row.operator("object.move_active_up", text="Up", icon='TRIA_UP')
        # row.operator("object.move_active_down", text="Down", icon='TRIA_DOWN')


#=======================================================

classes = (
    OBJECT_OT_AddToGroup,
    OBJECT_OT_MoveActiveUp,
    OBJECT_OT_MoveActiveDown,
    OBJECT_PT_PuppenspielerPanel,
    OBJECT_PT_PuppenspielerPanel_groups,
    OBJECT_OT_Set_Pivot,
    OBJECT_PT_PuppenspielerPanel_pivots
)

def register_keymaps():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        # For 'OBJECT MODE' keymaps
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        for key, group in key_defs:
            kmi = km.keymap_items.new(OBJECT_OT_AddToGroup.bl_idname, type=key, value='PRESS')
            kmi.properties.group = group
            addon_keymaps.append((km, kmi))
        km_pivot = km.keymap_items.new(OBJECT_OT_Set_Pivot.bl_idname, type='F9', value='PRESS')
        kmi.properties.group = 'PIVOT'
        addon_keymaps.append((km, km_pivot))
        # For 'EDIT MODE' keymaps
        kmm = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
        kmm_pivot = kmm.keymap_items.new(OBJECT_OT_Set_Pivot.bl_idname, type='F9', value='PRESS')
        addon_keymaps.append((kmm, kmm_pivot))



def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()

def unregister():
    unregister_keymaps()
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
