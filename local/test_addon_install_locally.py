import sys
# import shutil

# sys.path.append('/opt/blender')

import bpy

class BlenderAddon:
    def __init__(self, modulename: str, version: (int, int, int), filename: str):
        self.modulename = modulename
        self.version = version
        self.filename = filename

addons = [
    BlenderAddon(modulename="physical-starlight-atmosphere", version=(1, 8, 2), filename="physical-starlight-atmosphere-1.8.2.zip"),
    # BlenderAddon(modulename="colorist_pro", version=(1, 2, 0), filename="colorist_pro_1.2.0.zip"),
]

for addon in addons:
    print(f'Installing addon: {addon.modulename}')
    bpy.ops.preferences.addon_install(filepath=f'/tmp/blender_addons/{addon.filename}')
    bpy.ops.preferences.addon_enable(module=addon.modulename)

bpy.ops.wm.save_userpref()

print('Successfully installed all addons')
os._exit(0)

