import bpy

from bpy.props import (EnumProperty, StringProperty)

from .cbtools_import_export import CBTools_PT_Import_Export_Panel

def update_panel_category(self, context):
    is_panel = hasattr(bpy.types, 'VIEW3D_PT_Import_Export_Tools_Panel')

    if is_panel:
        try:
            bpy.utils.unregister_class(CBTools_PT_Import_Export_Panel)
        except:
            pass

    CBTools_PT_Import_Export_Panel.bl_category = self.cbtools_category

    bpy.utils.register_class(CBTools_PT_Import_Export_Panel)

class VIEW3D_OT_CBTools_Preferences(bpy.types.AddonPreferences):
    """Contains the Blender addon preferences"""
    # This must match the addon name, use '__package__'
    # when defining this in a subnodule of a python package.
    bl_idname = __package__

    prefs_tabs: EnumProperty(items=(('ui', "UI", "UI"), ('about', "About", "About")), default='ui')

    cbtools_category: StringProperty(name="Category",
                                      description="Defines in which category of the tools panel the CBTools panel is listed.",
                                      default='CBTools', update=update_panel_category)  # update = update_panel_position,

    def draw(self, context):
        """Preference UI to define settings."""
        layout = self.layout
        wm = context.window_manager

        row = layout.row(align=True)
        row.prop(self, "prefs_tabs", expand=True)

        if self.prefs_tabs == 'ui':
            row = layout.row()
            row.prop(self, "cbtools_category", expand=True)

        if self.prefs_tabs == 'about':
            element = self.layout
            box = element.box()

            box.label(text="A rework of Cyberpunk 2077 glTF Importer by Zendrex")


classes = (
    VIEW3D_OT_CBTools_Preferences,
)

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)