####
# Sample command: `modal run src/main.py --frame-count 60 --blend-path my-project.blend`
####

import modal
import uuid
from pathlib import Path
from dependencies import app, volume, validate_blender_path, blender_proj_remote_volume_upload_path, remote_job_frames_absolute_volume_directory_path
from cloud_render import render_sequence
from chunking import chunk_frame_range
import math

@app.local_entrypoint()
def main(frame_count: int, blend_path: str):
    session_id = str(uuid.uuid4())
    print(f"Rendering {frame_count} frames from blend='{blend_path}', session='{session_id}'")

    # 1. Upload the .blend file into the Volume
    print(f"Uploading to remove server... {blend_path}")
    with volume.batch_upload() as batch:
        local_blend = Path(blend_path)
        validate_blender_path(local_blend)
        batch.put_file(local_blend, blender_proj_remote_volume_upload_path(session_id))

    concurrency_limit = 30
    chunk_size = max(1, math.ceil(frame_count / concurrency_limit))
    chunk_size = min(100, max(3, chunk_size))
    print(f"Splitting {frame_count} frames into chunks of {chunk_size}")
    animations = chunk_frame_range(1, frame_count, chunk_size=chunk_size)

    # 2. Render frames in the Volume
    args = [(session_id, anim[0], anim[1], "TODO CAMERA NAME") for anim in animations]
    print(args)
    results = list(render_sequence.starmap(args))
    for r in results:
        print(r)
    print("All frames rendered into the Volume.")

    # 4. Show how to download it locally via CLI
    remote_frames_dir_path = remote_job_frames_absolute_volume_directory_path(session_id)
    local_frames_dir_path = f"/tmp/renders/{session_id}"
    command = f"mkdir -p {local_frames_dir_path} && modal volume get distributed-render {remote_frames_dir_path} {local_frames_dir_path}"
    print(f"\nTo download locally, run:\n    {command}\n")

    print("Done!")