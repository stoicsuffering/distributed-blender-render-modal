import modal
from enum import Enum

app = modal.App("distributed-render")

rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("xorg", "libxkbcommon0")  # X11 (Unix GUI) dependencies
    .add_local_dir("/Users/johnrivera/workspace/distributed-render-modal/remote_opt", remote_path="/opt", copy=True)
    .run_commands("/opt/EGL-setup.sh")
    .run_commands("mkdir /tmp/blender && tar -xvzf /opt/blender.tar.gz -C /tmp/blender && mv /tmp/blender/opt/blender-dst /opt/blender")
    .env({
        "EGL_DRIVER": "nvidia",
        "__EGL_VENDOR_LIBRARY_DIRS": "/usr/share/glvnd/egl_vendor.d",
        # "BLENDER_DEBUG": "1",
        # "BLENDER_DEBUG_GPU": "1"
    })
    # .pip_install("bpy==4.2.0")
    # .run_commands([
    #     "cp /opt/dummy-xorg.conf /etc/X11/xorg.conf",
    #     "Xorg -noreset -nolisten tcp :0 &"
    # ])
    # .env({
    #     # "DISPLAY": ":0",
    #     # "__GLX_VENDOR_LIBRARY_NAME": "nvidia",
    #     # "LIBGL_DEBUG": "verbose",
    #     # "EGL_PLATFORM": "surfaceless",
    #     # "LD_DEBUG": "libs"
    # })
    # .apt_install("libwayland-dev", "libegl-dev")
)

volume = modal.Volume.from_name("distributed-render", create_if_missing=True)