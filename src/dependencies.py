import modal
# from blender_addons import install_blender_addons, BlenderAddon

app = modal.App("distributed-render")

volume = modal.Volume.from_name("distributed-render", create_if_missing=True)

def install_and_verify():
    import subprocess
    import os

    try:
        output = subprocess.run(
            ['python3.11', '/tmp/blender_addons/install_addons.py'],
            check=True
        )
        print(f"Finished running install_addons.py, output: {output.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(f"Combined output (stdout and stderr): {e.output}")

    output_file_path = '/tmp/addon-install-result'
    if os.path.exists(output_file_path):
        with open(output_file_path) as f:
            if f.read() == "success":
                print("Verified successful installation")
            else:
                raise ValueError("Output file was not expected value")
    else:
        print("No output file found—task may have failed.")
        raise ValueError("No output file found!")

rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
        .apt_install("xorg", "libxkbcommon0")
        # Blender Install
        # .add_local_file("remote_resources/blender.tar.gz", remote_path="/opt/blender.tar.gz", copy=True)
        # .run_commands("mkdir /tmp/blender && tar -xvzf /opt/blender.tar.gz -C /tmp/blender && mv /tmp/blender/opt/blender-dst /opt/blender")
        # EGL Install
        .add_local_file("remote_resources/EGL-setup.sh", remote_path="/opt/EGL-setup.sh", copy=True)
        .run_commands("/opt/EGL-setup.sh")
        .env({
            "EGL_DRIVER": "nvidia",
            "__EGL_VENDOR_LIBRARY_DIRS": "/usr/share/glvnd/egl_vendor.d",
        })
        # Blender Install
        .add_local_file("remote_resources/bpy-4.2.6-cp311-cp311-manylinux_2_35_x86_64.whl", remote_path="/opt/bpy-4.2.6-cp311-cp311-manylinux_2_35_x86_64.whl", copy=True)
        .run_commands("python3.11 -m pip install /opt/bpy-4.2.6-cp311-cp311-manylinux_2_35_x86_64.whl")
        # Addons
        .add_local_dir("remote_resources/blender_addons", remote_path="/tmp/blender_addons", copy=True)
        # .run_function(install_and_verify)
)