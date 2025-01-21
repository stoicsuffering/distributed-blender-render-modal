import modal
import uuid
from pathlib import Path
from dependencies import app, volume, validate_blender_path, blender_proj_remote_volume_upload_path, volume_zip_local_download_path
from cloud_render import render
from cloud_combine import zip_frames

@app.local_entrypoint()
def main(frame_count: int, blend_path: str):
    session_id = str(uuid.uuid4())
    print(f"Rendering {frame_count} frames from blend='{blend_path}', session='{session_id}'")

    # 1. Upload the .blend file into the Volume
    with volume.batch_upload() as batch:
        local_blend = Path(blend_path)
        validate_blender_path(local_blend)
        batch.put_file(local_blend, blender_proj_remote_volume_upload_path(session_id))

    # 2. Render frames in the Volume
    args = [(session_id, frame) for frame in range(1, frame_count + 1)]
    results = list(render.starmap(args))
    for r in results:
        print(r)
    print("All frames rendered into the Volume.")

    # 3. Zip the frames in the Volume
    zip_path = zip_frames.remote(session_id)
    print(f"Frames.zip is located at: {zip_path} in the Volume.")

    # 4. Show how to download it locally via CLI
    print("\nTo download locally, run:\n"
          f"  modal volume get distributed-render {volume_zip_local_download_path(session_id)} /tmp/renders/{session_id}/local_frames.zip\n")

    print("Done!")