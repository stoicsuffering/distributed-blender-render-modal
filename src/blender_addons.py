from modal import Image

class BlenderAddon:
    def __init__(self, modulename: str, version: (int, int, int), filename: str):
        self.modulename = modulename
        self.version = version
        self.filename = filename

def verify_addons(addons: list[BlenderAddon]):
    import addon_utils

    for addon in addons:
        installed_module = addon_utils.modules().mapping[addon.modulename]
        if installed_module.bl_info["version"] != addon.version:
            raise ValueError(f"Unexpected {addon.modulename} version: {installed_module.bl_info['version']}")
        print(f"Successfully verified {addon.modulename}, info: {installed_module.bl_info}")

def install_and_verify(addons: list[BlenderAddon]):
    import bpy

    for addon in addons:
        print(f'Installing addon: {addon.modulename}')
        bpy.ops.preferences.addon_install(filepath=f'/tmp/blender_addons/{addon.filename}')
        bpy.ops.preferences.addon_enable(module=addon.modulename)
    #
    bpy.ops.wm.save_userpref()
    print('Successfully installed all addons')

    verify_addons(addons)

