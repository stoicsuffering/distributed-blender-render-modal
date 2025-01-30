from modal import gpu
from pathlib import Path
from dependencies import app, rendering_image, volume, VOLUME_MOUNT_PATH
USE_CAMERA = False


@app.function(
    # gpu="L40S",
    gpu=[gpu.L40S(count=2), gpu.L40S(count=1)],
    # gpu="H100",
    cpu=8.0,
    memory=10240,
    concurrency_limit=30,
    image=rendering_image,
    volumes={VOLUME_MOUNT_PATH: volume},
    timeout=10800 # 3 hours.
)
def render_sequence(session_id: str, start_frame: int, end_frame: int, camera_name: str) -> str:
    import sys
    sys.path.append('/opt/blender')
    import bpy
    from dependencies import blender_proj_remote_path, remote_job_frames_directory_path

    input_path = str(blender_proj_remote_path(session_id, validate=True))
    if USE_CAMERA:
        base_output_dir = remote_job_frames_directory_path(session_id) / camera_name # Per-camera subdirectory
    else:
        base_output_dir = remote_job_frames_directory_path(session_id)
    base_output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    output_path = str(base_output_dir / "frame_")  # Base file path for animation frames
    # Load Blender scene
    bpy.ops.wm.open_mainfile(filepath=input_path)
    # Set the correct camera
    if USE_CAMERA:
        camera_obj = bpy.data.objects.get(camera_name)
        if not camera_obj:
          raise ValueError(f"Camera '{camera_name}' not found in Blender project.")
        bpy.context.scene.camera = camera_obj  # Assign the camera

    # Set frame range
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    bpy.context.scene.render.filepath = output_path  # Blender will auto-append frame numbers

    # Configure rendering and execute animation render
    configure_rendering(bpy.context)
    bpy.ops.render.render(animation=True)  # Render the entire frame range
    # Commit volume changes (if necessary)
    volume.commit()
    return f"Successfully rendered frames {start_frame}-{end_frame} for {camera_name} at {output_path}"

def configure_rendering(ctx):
    ctx.scene.render.engine = "CYCLES"
    # ctx.scene.render.resolution_x = 3000
    # ctx.scene.render.resolution_y = 3000
    # ctx.scene.render.resolution_percentage = 100
    # ctx.scene.cycles.samples = 1024
    print(f"Cycles samples: {ctx.scene.cycles.samples}")
    print(f"Cycles resolution: {ctx.scene.render.resolution_x} x {ctx.scene.render.resolution_y}")
    print(f"Cycles resolution %: {ctx.scene.render.resolution_percentage}")

    cycles = ctx.preferences.addons["cycles"]
    cycles.preferences.compute_device_type = "OPTIX"
    ctx.scene.cycles.device = "GPU"
    # reload the devices to update the configuration
    cycles.preferences.get_devices()
    for device in cycles.preferences.devices:
        device.use = device.type != "CPU"
    # report rendering devices -- a nice snippet for debugging and ensuring the accelerators are being used
    for dev in cycles.preferences.devices:
        print(f"ID:{dev['id']} Name:{dev['name']} Type:{dev['type']} Use:{dev['use']}")

def print_sys_info(os):
    os.system("nvidia-smi")
    os.system("nvcc --version")
    os.system("cat /proc/cpuinfo")
    os.system("lscpu")