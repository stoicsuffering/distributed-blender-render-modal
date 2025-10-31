####
# Sample command: `modal run src/main.py --frame-count 60 --blend-path my-project.blend`
####

import modal
import uuid
from pathlib import Path
from dependencies import app, volume
from cloud_render import render_sequence
from paths import validate_blender_path, blender_proj_remote_volume_upload_path, remote_job_frames_absolute_volume_directory_path
from job import Job, job_chunks_from_job, selected_job

@app.local_entrypoint()
def main():
    current_job: Job = selected_job(str(uuid.uuid4()))
    print(f"current job: {current_job}")
    current_job.validate()

    # 1. Upload the .blend file into the Volume
    print(f"Uploading to remove server... {current_job.blend_file_path}")
    with volume.batch_upload() as batch:
        local_blend = Path(current_job.blend_file_path)
        validate_blender_path(local_blend)
        batch.put_file(local_blend, blender_proj_remote_volume_upload_path(current_job.session_id))

    total_chunk_target = current_job.render_node_concurrency_target
    if current_job.render_node_concurrency_target > 1:
        # Keep max nodes at original concurrency target, but break down further to better parallelize computationally-intensive localized frame-regions.
        # There's a tricky tradeoff here between startup latency and long stragglers
        total_chunk_target = current_job.render_node_concurrency_target * 2

    job_chunks = job_chunks_from_job(current_job, total_chunk_target=total_chunk_target)
    print(job_chunks)
    args = [[job_chunk] for job_chunk in job_chunks]
    results = list(render_sequence.starmap(args))
    for r in results:
        print(r)
    print("All frames rendered into the Volume.")

    # 4. Show how to download it locally via CLI
    remote_frames_dir_path = remote_job_frames_absolute_volume_directory_path(current_job.session_id)
    local_frames_dir_path = f"~/frames/{current_job.job_name}_{current_job.session_id}"
    command = f"mkdir -p {local_frames_dir_path} && modal volume get distributed-render {remote_frames_dir_path} {local_frames_dir_path}"
    print(f"\nTo download locally, run:\n{command}\n")

    print("Done!")
