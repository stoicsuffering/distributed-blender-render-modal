from dependencies import app, rendering_image, volume, addons
from paths import VOLUME_MOUNT_PATH
from job import JobChunk, Job
from utils import print_general_info
from blender_addons import verify_addons

@app.function(
     gpu="L40S",
     cpu=4,
     memory=(8 * 1024),
    concurrency_limit=20,
    image=rendering_image,
    volumes={VOLUME_MOUNT_PATH: volume},
    timeout=(8 * 60 * 60),  # 8 hours.
    retries=0  # No need to burn money if there's an issue...
)
def render_sequence(job_chunk: JobChunk) -> str:
    import bpy
    print(f"render sequence job chunk: {job_chunk}")
    verify_addons(addons)
    configure_rendering(bpy, job_chunk)
    print_general_info(bpy.context)
    bpy.ops.render.render(animation=True)  # Render the entire frame range
    return f"Successfully rendered frames {job_chunk.chunk_start_frame}-{job_chunk.chunk_end_frame} for {job_chunk.job.camera_name} at {bpy.context.scene.render.filepath}"


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
