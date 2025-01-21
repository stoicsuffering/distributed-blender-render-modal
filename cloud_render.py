from pathlib import Path
from dependencies import app, rendering_image, volume, VOLUME_MOUNT_PATH, remote_job_frames_directory_path

WITH_GPU = True  # try changing this to "False" to run rendering massively in parallel on CPUs!

# We decorate the function with `@app.function` to define it as a Modal function.
# Note that in addition to defining the hardware requirements of the function,
# we also specify the container image that the function runs in (the one we defined above).

# The details of the scene aren't too important for this example, but we'll load
# a .blend file that we created earlier. This scene contains a rotating
# Modal logo made of a transmissive ice-like material, with a generated displacement map. The
# animation keyframes were defined in Blender.

@app.function(
    gpu="L40S" if WITH_GPU else None,
    # default limits on Modal free tier
    concurrency_limit=10 if WITH_GPU else 100,
    image=rendering_image,
    volumes={VOLUME_MOUNT_PATH: volume}
)
def test_render_image(session_id: str, frame_number: int) -> str:
    import bpy
    from dependencies import blender_proj_remote_path, remote_job_frames_directory_path

    input_path = blender_proj_remote_path(session_id, validate=True)
    output_path = remote_job_frames_directory_path(session_id)

    remote_job_frames_directory_path(session_id).mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.open_mainfile(filepath=input_path)
    bpy.context.scene.frame_set(frame_number)
    bpy.context.scene.render.filepath = output_path
    configure_rendering(bpy.context, with_gpu=WITH_GPU)
    bpy.ops.render.render(write_still=True)

    volume.commit()

    return f"successfully rendered {output_path.as_posix()}"

# ### Rendering with acceleration

# We can configure the rendering process to use GPU acceleration with NVIDIA CUDA.
# We select the [Cycles rendering engine](https://www.cycles-renderer.org/), which is compatible with CUDA,
# and then activate the GPU.


def configure_rendering(ctx, with_gpu: bool):
    # configure the rendering process
    ctx.scene.render.engine = "CYCLES"
    ctx.scene.render.resolution_x = 3000
    ctx.scene.render.resolution_y = 2000
    ctx.scene.render.resolution_percentage = 50
    ctx.scene.cycles.samples = 128

    cycles = ctx.preferences.addons["cycles"]

    # Use GPU acceleration if available.
    if with_gpu:
        cycles.preferences.compute_device_type = "CUDA"
        ctx.scene.cycles.device = "GPU"

        # reload the devices to update the configuration
        cycles.preferences.get_devices()
        for device in cycles.preferences.devices:
            device.use = True

    else:
        ctx.scene.cycles.device = "CPU"

    # report rendering devices -- a nice snippet for debugging and ensuring the accelerators are being used
    for dev in cycles.preferences.devices:
        print(
            f"ID:{dev['id']} Name:{dev['name']} Type:{dev['type']} Use:{dev['use']}"
        )
