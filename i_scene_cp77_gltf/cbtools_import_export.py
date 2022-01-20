import bpy
import json
import os

from bpy.props import StringProperty, EnumProperty, BoolProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper
from io_scene_gltf2.io.imp.gltf2_io_gltf import glTFImporter
from io_scene_gltf2.blender.imp.gltf2_blender_gltf import BlenderGlTF
from io_scene_gltf2.blender.imp.gltf2_blender_mesh import BlenderMesh

from .cbtools_material_builder import MaterialBuilder

class CBToolsProperties(bpy.types.PropertyGroup):
    image_format: EnumProperty(
        name="",
        items=(
            ("png", "Use PNG textures", ""),
            ("dds", "Use DDS textures", ""),
            ("jpg", "Use JPG textures", ""),
            ("tga", "Use TGA textures", ""),
            ("bmp", "Use BMP textures", ""),
            ("jpeg", "Use JPEG textures", ""),
        ),
        description="Texture Format",
        default="png",
    )

    exclude_unused_mats: BoolProperty(
        name="Exclude Unused Materials",
        default=True,
        description="Skip all materials that aren't being used by any mesh",
    )

    exclude_duplicate_mats: BoolProperty(
        name="Exclude Duplicate Materials",
        default=False,
        description="Skip all repeated materials on a mesh",
    )

    use_existing_mats: BoolProperty(
        name="Use Existing Materials",
        default=False,
        description="Utilize existing materials within this project which share the same name",
    )

    parent_child_meshes: BoolProperty(
        name="Parent Child Meshes",
        default=False,
        description="Don't use this when creating mesh edits instended to go back into the game!",
    )

    name_all_the_things: BoolProperty(
        name="Fuck It, Name Everything",
        default=False,
        description="This will ruin any chance of re-importing meshes back into the game.",
    )

#-------------------------------------------------------
# Batch Import Mesh Files
class CBTools_OT_Import_Mesh(bpy.types.Operator, ImportHelper):
    """Batch Import Mesh Files"""
    bl_idname ="object.import_mesh"
    bl_label = "Import Mesh"

    filter_glob: StringProperty(
        default='*.gltf;*.glb',
        options={'HIDDEN'}
    )

    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement
    )

    directory: StringProperty(
        subtype="DIR_PATH"
    )
    #############

    def execute(self, context):
        directory = self.directory
        scene = context.scene
        props = scene.cbtools

        for f in self.files:
            filepath = os.path.join(directory, f.name)

            gltf_importer = glTFImporter(
                filepath,
                {
                    "files": None,
                    "loglevel": 0,
                    "import_pack_images": True,
                    "merge_vertices": False,
                    "import_shading": "NORMALS",
                    "bone_heuristic": "TEMPERANCE",
                    "guess_original_bind_pose": False,
                }
            )

            gltf_importer.read()
            gltf_importer.checks()

            existingMeshes = bpy.data.meshes.keys()
            existingObjects = bpy.data.objects.keys()
            existingMaterials = bpy.data.materials.keys()

            BlenderGlTF.create(gltf_importer)

            for name in bpy.data.materials.keys():
                if name not in existingMaterials:
                    bpy.data.materials.remove(bpy.data.materials[name], do_unlink = True, do_id_user = True, do_ui_user = True)

            basePath = os.path.splitext(filepath)[0]
            materialFile = open(basePath + ".Material.json", mode="r")
            meshData = json.loads(materialFile.read())
            basePath = str(meshData["MaterialRepo"]) + "\\"

            Builder = MaterialBuilder(meshData, basePath, str(props.image_format))

            usedMaterials = {}
            counter = 0

            usedMaterials = {}
            counter = 0
            for name in bpy.data.meshes.keys():
                if name not in existingMeshes:
                    bpy.data.meshes[name].materials.clear()
                    for matname in gltf_importer.data.meshes[counter].extras["materialNames"]:
                        if matname not in usedMaterials.keys():
                            index = 0
                            for rawmat in meshData["Materials"]:
                                if rawmat["Name"] == matname:
                                    if props.use_existing_mats:
                                        if matname in existingMaterials:
                                            exmat = bpy.data.materials.get(matname)
                                            bpy.data.meshes[name].materials.append(exmat)
                                            usedMaterials.update({matname: exmat})
                                        else:
                                            bpymat = Builder.create(index)
                                            bpy.data.meshes[name].materials.append(bpymat)
                                            usedMaterials.update({matname: bpymat})
                                    else:
                                        bpymat = Builder.create(index)
                                        bpy.data.meshes[name].materials.append(bpymat)
                                        usedMaterials.update({matname: bpymat})

                                index = index + 1

                        else:
                            if not props.exclude_duplicate_mats:
                                bpy.data.meshes[name].materials.append(usedMaterials[matname])

                    counter = counter + 1

            if not props.exclude_unused_mats:
                index = 0
                for rawmat in meshData["Materials"]:
                    if rawmat["Name"] not in usedMaterials:
                        Builder.create(index)
                    index = index + 1

            collection = bpy.data.collections.new(os.path.splitext(f.name)[0])
            bpy.context.scene.collection.children.link(collection)

            for name in bpy.data.objects.keys():
                if name not in existingObjects:
                    for parent in bpy.data.objects[name].users_collection:
                        parent.objects.unlink(bpy.data.objects[name])
                    collection.objects.link(bpy.data.objects[name])

            parent = None

            if props.parent_child_meshes:
                for name in bpy.data.objects.keys():
                    if name not in existingObjects:
                        if "submesh_00_" in name:
                            parent = bpy.data.objects[name]
                        else:
                            bpy.data.objects[name].parent = parent

            if props.name_all_the_things:
                for name in bpy.data.objects.keys():
                    if name not in existingObjects:
                        if "submesh_00_" in name:
                            bpy.data.meshes[name].name = os.path.splitext(f.name)[0]
                            bpy.data.objects[name].name = os.path.splitext(f.name)[0]
                        else:
                            meshType = ''

                            firstMat = ''
                            if bpy.data.meshes[name].materials:
                                firstMat = bpy.data.meshes[name].materials[0].name
                                if "decal" in firstMat:
                                    meshType = 'decals'
                                else:
                                    meshType = 'unknown'
                            else:
                                meshType = 'unknown'

                            bpy.data.meshes[name].name = os.path.splitext(f.name)[0] + '_' + meshType
                            bpy.data.objects[name].name = os.path.splitext(f.name)[0] + '_' + meshType


        return {'FINISHED'}

class CBTools_PT_Import_Export_Panel(bpy.types.Panel):
    """Creates an Import/Export Panel"""
    bl_label = "Cyberpunk 2077 Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CBTools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.cbtools

        wm = context.window_manager

        ## Import Button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.import_mesh", text="Import Mesh(s)", icon="FILE_FOLDER")

        # Settings
        col = layout.column(align=True)
        col.prop(props, 'image_format')

        col.separator()

        ###############################################

        # --- Import Settings ---
        box = col.box()
        box.label(text = "Import Settings", icon = "SETTINGS")

        box.prop(props, 'use_existing_mats')
        box.prop(props, 'exclude_unused_mats')
        box.prop(props, 'exclude_duplicate_mats')
        
        ###############################################

        col.separator()

        # --- Expiremental Settings ---
        box = col.box()
        box.label(text = "Expiremental Settings", icon = "MODIFIER")

        box.prop(props, 'parent_child_meshes')
        box.prop(props, 'name_all_the_things')
        
        ###############################################

classes = [ CBToolsProperties, CBTools_PT_Import_Export_Panel, CBTools_OT_Import_Mesh ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

        bpy.types.Scene.cbtools = bpy.props.PointerProperty(type=CBToolsProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)