import uuid

from dependencies import app, rendering_image, volume
from paths import VOLUME_MOUNT_PATH
from job import JobChunk, Job
from utils import print_general_info


@app.function(
    gpu="L40S",
    cpu=4,
    memory=(8 * 1024),
    concurrency_limit=30,
    image=rendering_image,
    volumes={VOLUME_MOUNT_PATH: volume},
    timeout=(8*60*60) # 8 hours.
)
def render_sequence(job_chunk: JobChunk) -> str:
    import subprocess
    import pickle
    import os

    job_UUID = str(uuid.uuid4())

    output_file_path = f"/tmp/output-{job_UUID}.txt"
    pickle_path = f"/tmp/perform_render-result-{job_UUID}.pickle"

    # Write the object to a pickle file.
    with open(pickle_path, "wb") as f:
        pickle.dump(job_chunk, f)

    try:
        output = subprocess.run(
            ['python3.11', '-u', '/tmp/blender_addons/perform_render.py', pickle_path, output_file_path],
            check=True
        )
        print(f"Finished running install_addons.py, output: {output.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(f"Combined output (stdout and stderr): {e.output}")

    # After the child process exits, check for the output file.
    if os.path.exists(output_file_path):
        with open(output_file_path) as f:
            print("Child process output:")
            result = f.read()
            print(result)
            if result == "success":
                print("Verified job completed successfully")
            else:
                raise ValueError("Output file was not expected value")
    else:
        print("No output file found—task may have failed.")
        raise ValueError("No output file found!")

    return


def configure_rendering(bpy, job_chunk: JobChunk):
    bpy.ops.wm.open_mainfile(filepath=job_chunk.remote_blender_proj_path())

    frame_path = job_chunk.make_remote_frame_path()
    bpy.context.scene.render.filepath = frame_path

    # Set Camera
    camera_obj = bpy.data.objects.get(job_chunk.job.camera_name)
    if not camera_obj:
        raise ValueError(f"Camera '{job_chunk.job.camera_name}' not found in Blender project.")
    bpy.context.scene.camera = camera_obj

    bpy.context.scene.frame_start = job_chunk.chunk_start_frame
    bpy.context.scene.frame_end = job_chunk.chunk_end_frame

    bpy.context.scene.render.resolution_x = job_chunk.job.width
    bpy.context.scene.render.resolution_y = job_chunk.job.height

    bpy.context.scene.render.image_settings.color_management = 'OVERRIDE'
    bpy.context.scene.render.image_settings.linear_colorspace_settings.name = 'ACEScg'

    bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    bpy.context.scene.render.image_settings.color_depth = '32'

    if job_chunk.job.render_engine == "CYCLES":
        configure_rendering_cycles(bpy, job_chunk.job)
    else:
        raise ValueError(f"Rendering engine '{job_chunk.job.render_engine}' not supported.")


def configure_rendering_cycles(bpy, job: Job):
    print(f"Configuring rendering for CYCLES")
    bpy.context.scene.render.engine = "CYCLES"

    cycles = bpy.context.preferences.addons["cycles"]
    cycles.preferences.compute_device_type = "OPTIX"
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.denoising_use_gpu = True
    bpy.context.scene.cycles.use_auto_tile = False
    bpy.context.scene.render.use_persistent_data = True

    bpy.context.scene.cycles.adaptive_min_samples = 42
    bpy.context.scene.cycles.samples = job.render_max_samples
    bpy.context.scene.cycles.use_adaptive_sampling = True

    if job.eco_mode_enabled:
        bpy.context.scene.render.resolution_percentage = 25
        bpy.context.scene.cycles.adaptive_threshold = 0.2
    else:
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.cycles.adaptive_threshold = job.render_adaptive_threshold

    # reload the devices to update the configuration
    cycles.preferences.get_devices()
    for device in cycles.preferences.devices:
        device.use = device.type != "CPU"
