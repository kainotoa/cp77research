bl_info = {
    "name": "Cyberpunk 2077 Tools",
    "author": "HitmanHimself, Turk, Jato, Zendrex",
    "version": (1, 0, 6),
    "blender": (2, 93, 0),
    "location": "View3D > Tools ",
    "description": "Tools to import, modify & export (meshes/materials) to and from Wolvenkit for Cyberpunk 2077.",
    "category": "Object",
}

if "bpy" in locals():
	import importlib

	importlib.reload(cbtools_import_export)
	importlib.reload(cbtools_preferences)

else:
	from . import cbtools_import_export
	from . import cbtools_preferences

# Import standard modules.
import bpy

def register():
	# Call the register function of the sub modules.
	cbtools_import_export.register()

	# Keymap & Preferences should be last.
	cbtools_preferences.register()

def unregister():
	# Keymap & Preferences should be first.
	cbtools_preferences.unregister()

	# Call the unregister function of the sub modules.
	cbtools_import_export.unregister()

if __name__ == "__main__":
	register()