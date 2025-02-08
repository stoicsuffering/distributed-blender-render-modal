import modal

app = modal.App("distributed-render")

rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("xorg", "libxkbcommon0")  # X11 (Unix GUI) dependencies
    # Blender Install
    .copy_local_file("../remote_resources/blender.tar.gz", remote_path="/opt/blender.tar.gz")
    .run_commands("mkdir /tmp/blender && tar -xvzf /opt/blender.tar.gz -C /tmp/blender && mv /tmp/blender/opt/blender-dst /opt/blender")
    # EGL Install
    .copy_local_file("../remote_resources/EGL-setup.sh", remote_path="/opt/EGL-setup.sh")
    .run_commands("/opt/EGL-setup.sh")
    .env({
        "EGL_DRIVER": "nvidia",
        "__EGL_VENDOR_LIBRARY_DIRS": "/usr/share/glvnd/egl_vendor.d",
    })
)

volume = modal.Volume.from_name("distributed-render", create_if_missing=True)