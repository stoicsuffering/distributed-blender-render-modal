import modal
from blender_addons import BlenderAddon, install_and_verify

app = modal.App("distributed-render")

addons: list[BlenderAddon] = [
    BlenderAddon(modulename="physical-starlight-atmosphere", version=(1, 6, 3), filename="physical-starlight-atmosphere-1.6.3.zip"),
    BlenderAddon(modulename="colorist_pro", version=(1, 2, 0), filename="colorist_pro_1.2.0.zip"),
]

bpy_package_name = "bpy-4.2.6-cp311-cp311-manylinux_2_35_x86_64.whl"

rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("xorg", "libxkbcommon0")  # X11 (Unix GUI) dependencies
    # EGL
    .add_local_file("remote_resources/EGL-setup.sh", remote_path="/opt/EGL-setup.sh", copy=True)
    .run_commands("/opt/EGL-setup.sh")
    .env({
        "EGL_DRIVER": "nvidia",
        "__EGL_VENDOR_LIBRARY_DIRS": "/usr/share/glvnd/egl_vendor.d",
    })
    # Blender
    .add_local_file(f"remote_resources/{bpy_package_name}", remote_path=f"/opt/{bpy_package_name}", copy=True)
    .run_commands(f"python3.11 -m pip install /opt/{bpy_package_name}")
    # Blender Addons
    .add_local_dir("remote_resources/blender_addons", remote_path="/tmp/blender_addons", copy=True)
)

volume = modal.Volume.from_name("distributed-render", create_if_missing=True)