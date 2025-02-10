# from modal import Image
#
# def install_and_verify():
#     import sys
#     # import shutil
#     # sys.path.append('/opt/blender')
#     # import bpy
#     # import addon_utils
#     # from time import sleep
#     # import os
#     #
#     # faulthandler.enable()
#     #
#     # for addon in addons:
#     #     print(f'Installing addon: {addon.modulename}')
#     #     bpy.ops.preferences.addon_install(filepath=f'/tmp/blender_addons/{addon.filename}')
#     #     bpy.ops.preferences.addon_enable(module=addon.modulename)
#     # #
#     # bpy.ops.wm.save_userpref()
#     # print('Successfully installed all addons')
#     # os._exit(0)
#
#
#     # for addon in addons:
#     #     installed_module = addon_utils.modules().mapping[addon.modulename]
#     #     if installed_module.bl_info["version"] != addon.version:
#     #         raise ValueError(f"Unexpected {addon.modulename} version: {installed_module.bl_info['version']}")
#     #     print(f"Successfully installed {addon.modulename}, info: {installed_module.bl_info}")
#     # #
#     # bpy.ops.wm.quit_blender()
#
#     # addon_utils.disable_all()
#
#
#     # sleep(1)
#
# def install_blender_addons(self: Image, addons: list[BlenderAddon]) -> Image:
#     return (
#         self.add_local_dir("remote_resources/blender_addons", remote_path="/tmp/blender_addons", copy=True)
#             .run_function(install_and_verify)
#     )
