from pathlib import Path
from dependencies import app, rendering_image, volume
from paths import VOLUME_MOUNT_PATH
from job import Job

SUPPORTS_CAMERA = False

def print_general_info(ctx):
    print(f"Render engine '{ctx.scene.render.engine}'")
    print(f"Render resolution: {ctx.scene.render.resolution_x} x {ctx.scene.render.resolution_y}")
    print(f"Render resolution %: {ctx.scene.render.resolution_percentage}")

    if ctx.scene.render.engine == "CYCLES":
        cycles = ctx.preferences.addons["cycles"]
        print(f"Cycles samples: {ctx.scene.cycles.samples}")
        # report rendering devices -- a nice snippet for debugging and ensuring the accelerators are being used
        for dev in cycles.preferences.devices:
            print(f"ID:{dev['id']} Name:{dev['name']} Type:{dev['type']} Use:{dev['use']}")

# def print_sys_info(os):
    # os.system("nvidia-smi")
    # os.system("nvcc --version")
    # os.system("cat /proc/cpuinfo")
    # os.system("lscpu")
    # print("printing driver capabilities...")
    # os.system("echo $NVIDIA_DRIVER_CAPABILITIES")
    # os.system("echo $NVIDIA_VISIBLE_DEVICES")
    # # os.system("cat /etc/X11/xorg.conf")
    # os.system("ls /dev | grep nvidia")
    # print("Printed.")

@app.function(
    gpu="L40S",
    cpu=4,
    memory=(8 * 1024),
    concurrency_limit=30,
    image=rendering_image,
    volumes={VOLUME_MOUNT_PATH: volume},
    timeout=10800 # 3 hours.
)
def render_sequence(session_id: str, start_frame: int, end_frame: int, camera_name: str, job: Job) -> str:
    import sys
    import os

    sys.path.append('/opt/blender')
    import bpy
    from paths import blender_proj_remote_path, remote_job_frames_directory_path

    print(f"render sequence job {job}")

    input_path = str(blender_proj_remote_path(session_id, validate=True))

    if SUPPORTS_CAMERA:
        base_output_dir = remote_job_frames_directory_path(session_id) / camera_name # Per-camera subdirectory
    else:
        base_output_dir = remote_job_frames_directory_path(session_id)

    base_output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    output_path = str(base_output_dir / "frame_")  # Base file path for animation frames

    # Load Blender scene
    bpy.ops.wm.open_mainfile(filepath=input_path)
    ctx = bpy.context

    # Set the correct camera
    if SUPPORTS_CAMERA:
        camera_obj = bpy.data.objects.get(camera_name)
        if not camera_obj:
          raise ValueError(f"Camera '{camera_name}' not found in Blender project.")
        ctx.scene.camera = camera_obj  # Assign the camera

    # Set frame range
    ctx.scene.frame_start = start_frame
    ctx.scene.frame_end = end_frame

    bpy.context.scene.render.resolution_x = job.width
    bpy.context.scene.render.resolution_y = job.height

    ctx.scene.render.filepath = output_path  # Blender will auto-append frame numbers

    # print_sys_info(os)

    # Configure rendering and execute animation render
    if job.render_engine == "BLENDER_EEVEE_NEXT":
        configure_rendering_eevee(ctx)
    elif job.render_engine == "CYCLES":
        configure_rendering_cycles(bpy, job)
    else:
        raise ValueError(f"Rendering engine '{job.render_engine}' not supported.")

    print_general_info(bpy.context)

    bpy.ops.render.render(animation=True)  # Render the entire frame range

    return f"Successfully rendered frames {start_frame}-{end_frame} for {camera_name} at {output_path}"

def configure_rendering_eevee(ctx):
    print(f"Configuring rendering for EEVEE")

def configure_rendering_cycles(bpy, job: Job):
    print(f"Configuring rendering for CYCLES")
    bpy.context.scene.render.engine = "CYCLES"

    bpy.context.scene.render.image_settings.color_management = 'OVERRIDE'
    bpy.context.scene.render.image_settings.linear_colorspace_settings.name = 'ACEScg'

    bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    bpy.context.scene.render.image_settings.color_depth = '32'

    cycles = bpy.context.preferences.addons["cycles"]
    cycles.preferences.compute_device_type = "OPTIX"
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.denoising_use_gpu = True
    bpy.context.scene.cycles.use_auto_tile = False
    bpy.context.scene.render.use_persistent_data = True

    bpy.context.scene.cycles.adaptive_min_samples = 48
    bpy.context.scene.cycles.samples = job.render_max_samples
    bpy.context.scene.cycles.use_adaptive_sampling = True

    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.cycles.adaptive_threshold = job.render_adaptive_threshold

    if job.eco_mode_enabled:
        bpy.context.scene.render.resolution_percentage = 25
        bpy.context.scene.cycles.adaptive_threshold = 0.2

    # reload the devices to update the configuration
    cycles.preferences.get_devices()
    for device in cycles.preferences.devices:
        device.use = device.type != "CPU"


    # import subprocess
    # # Build the basic Blender CLI command.
    # blender_bin = "/opt/blender/blender"
    # blender_cmd = [
    #     blender_bin,
    #     "--background", input_path,  # open blend file in background mode
    #     "--render-output", output_path,  # set output filepath pattern
    #     "--render-frame", str(1),  # render a single frame
    #     "--verbose"
    # ]
    #
    # # Log the command for debugging.
    # print("Executing command:")
    # print(" ".join(blender_cmd))
    #
    # # Try to run the command, and catch exceptions to print out the crash log.
    # try:
    #     subprocess.run(blender_cmd, check=True)
    # except subprocess.CalledProcessError as e:
    #     print("Subprocess.run encountered an error:")
    #     print(e)
    #     crash_file = "/tmp/project.crash.txt"
    #     if os.path.exists(crash_file):
    #         print(f"Crash file found at {crash_file}. Contents:")
    #         with open(crash_file, "r") as f:
    #             print(f.read())
    #     else:
    #         print(f"No crash file found at {crash_file}.")
    #     # Optionally, re-raise the exception or handle it appropriately.
    #     raise
    #
    # return "success"