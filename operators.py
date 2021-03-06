# ##### BEGIN GPL LICENSE BLOCK #####
#
#  <Blender Project Starter is made for automatic Project Folder Generation.>
#    Copyright (C) <2021>  <Steven Scott>
#    Mofified <2021> <Blender Defender>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    EnumProperty
)
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

import os
from os import path as p

from .functions.main_functions import (
    build_file_folders,
    generate_file_version_number,
    get_file_subfolder,
    open_directory,
    is_file_in_project_folder,
    save_file,
    add_open_project,
    close_project,
    redefine_project_path
)

from .functions.json_functions import (
    decode_json,
    encode_json
)

from .functions.register_functions import (
    register_automatic_folders,
    unregister_automatic_folders
)

C = bpy.context


class BLENDER_PROJECT_MANAGER_OT_Build_Project(Operator):
    bl_idname = "blender_project_manager.build_project"
    bl_label = "Build Project"
    bl_description = "Build Project Operator "
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        D = bpy.data
        scene = context.scene
        prefs = C.preferences.addons[__package__].preferences
        path = p.join(context.scene.project_location,
                      context.scene.project_name)
        filename = context.scene.save_file_name

        if not p.isdir(path):
            os.makedirs(path)

        if prefs.prefix_with_project_name:
            pre = context.scene.project_name + "_"
        else:
            pre = ""

        if context.scene.add_new_project:
            add_open_project(path)

        if context.scene.project_setup == "Automatic_Setup":
            for index, folder in enumerate(prefs.automatic_folders):
                try:
                    build_file_folders(context,
                                       pre + \
                                       folder[context.scene.project_setup])
                except:
                    pass
            subfolder = pre + \
                        get_file_subfolder(context.scene.project_setup,
                                           prefs.automatic_folders,
                                           prefs.save_folder)
        else:
            for index, folder in enumerate(prefs.custom_folders):
                try:
                    build_file_folders(context,
                                       pre + \
                                       folder[context.scene.project_setup])
                except:
                    pass
            subfolder = pre + \
                        get_file_subfolder(context.scene.project_setup,
                                           prefs.custom_folders,
                                           prefs.save_folder)

        if context.scene.save_blender_file:
            if D.filepath == "":
                save_file(context, filename, subfolder)

            elif not is_file_in_project_folder(context, D.filepath):
                old_file_path = D.filepath

                if context.scene.save_file_with_new_name:
                    save_file(context, filename, subfolder)
                else:
                    save_file(context,
                              p.basename(D.filepath).split(".blend")[0],
                              subfolder)

                if context.scene.cut_or_copy:
                    os.remove(old_file_path)

            elif context.scene.save_blender_file_versioned:
                path = D.filepath
                filepath = p.dirname(path)
                filename = p.basename(path).split(".blen")[0].split("_v0")[0]
                version = generate_file_version_number(p.join(filepath,
                                                              filename))

                filename += version

                save_file(context, filename, subfolder)
            else:
                bpy.ops.wm.save_as_mainfile(filepath=D.filepath,
                                            compress=scene.compress_save,
                                            relative_remap=scene.remap_relative
                                            )

        if context.scene.open_directory:

                OpenLocation = p.join(context.scene.project_location,
                                      context.scene.project_name)
                OpenLocation = p.realpath(OpenLocation)

                open_directory(OpenLocation)

        return {"FINISHED"}


class BLENDER_PROJECT_MANAGER_OT_add_folder(Operator):
    bl_idname = "blender_project_manager.add_folder"
    bl_label = "Add Folder"
    bl_description = "Add a Folder with the subfolder \
Layout Folder>>Subfolder>>Subsubfolder."

    coming_from: StringProperty()

    def execute(self, context):
        pref = context.preferences.addons[__package__].preferences

        if self.coming_from == "prefs":
            folder = pref.automatic_folders.add()

        else:
            folder = pref.custom_folders.add()

        return {"FINISHED"}


class BLENDER_PROJECT_MANAGER_OT_remove_folder(Operator):
    bl_idname = "blender_project_manager.remove_folder"
    bl_label = "Remove Folder"
    bl_description = "Remove the selected Folder."

    index: IntProperty()
    coming_from: StringProperty()

    def execute(self, context):
        pref = context.preferences.addons[__package__].preferences

        if self.coming_from == "prefs":
            folder = pref.automatic_folders.remove(self.index)

        else:
            folder = pref.custom_folders.remove(self.index)

        return {"FINISHED"}


class BLENDER_PROJECT_MANAGER_OT_add_project(Operator, ImportHelper):
    bl_idname = "blender_project_manager.add_project"
    bl_label = "Add Project"
    bl_description = "Add a Project"

    filter_glob: StringProperty(default='*.filterall', options={'HIDDEN'})

    def execute(self, context):
        path = p.dirname(self.filepath)
        add_open_project(path)

        message = "Successfully added project " + p.basename(path)
        self.report({'INFO'}, message)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Please select a project Directory")



class BLENDER_PROJECT_MANAGER_OT_close_project(bpy.types.Operator):
    bl_idname = "blender_project_manager.close_project"
    bl_label = "Close Project"
    bl_description = "Close the selected Project."
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty()

    def execute(self, context):
        close_project(self.index)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        # layout.prop(self, "disable")

        layout.label(text="Are you sure?")
        layout.label(text="This will remove your project from the open projects list.")

        layout.separator(factor=1)

        layout.label(text="Don't worry, no file gets deleted, ")
        layout.label(text="but you might forget about this project and never finish it.")


class BLENDER_PROJECT_MANAGER_OT_redefine_project_path(Operator, ImportHelper):
    bl_idname = "blender_project_manager.redefine_project_path"
    bl_label = "Update Project path"
    bl_description = "Your project has changed location - \
please update the project path"

    name: StringProperty()
    filter_glob: StringProperty(default='*.filterall', options={'HIDDEN'})
    index: IntProperty()

    def execute(self, context):
        path = p.dirname(self.filepath)
        redefine_project_path(self.index, path)

        message = "Successfully changed project path: " + p.basename(path)
        self.report({'INFO'}, message)
        return {"FINISHED"}

    def draw(self, context):
        name = self.name

        layout = self.layout
        layout.label(text="Please select your project Directory for:")
        layout.label(text=name)


class BLENDER_PROJECT_MANAGER_OT_open_project_path(Operator):
    bl_idname = "blender_project_manager.open_project_path"
    bl_label = "Open Project path"
    bl_description = "Open your project folder."

    path: StringProperty()

    def execute(self, context):
        path = self.path
        open_directory(path)
        self.report({'INFO'}, "Opened project path")
        return {"FINISHED"}


classes = (
    BLENDER_PROJECT_MANAGER_OT_add_folder,
    BLENDER_PROJECT_MANAGER_OT_remove_folder,
    BLENDER_PROJECT_MANAGER_OT_Build_Project,
    BLENDER_PROJECT_MANAGER_OT_add_project,
    BLENDER_PROJECT_MANAGER_OT_close_project,
    BLENDER_PROJECT_MANAGER_OT_redefine_project_path,
    BLENDER_PROJECT_MANAGER_OT_open_project_path
)


def register():
    folders = C.preferences.addons[__package__].preferences.automatic_folders
    register_automatic_folders(folders)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    folders = C.preferences.addons[__package__].preferences.automatic_folders
    unregister_automatic_folders(folders)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
