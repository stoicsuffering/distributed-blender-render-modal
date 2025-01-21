import modal
import uuid
from pathlib import Path
from dependencies import app, volume, validate_blender_path, blender_proj_remote_volume_upload_path
from cloud_render import render, test_render_image
from cloud_combine import combine

@app.local_entrypoint()
def main(frame_count: int, blend_path: str):
    session_id = str(uuid.uuid4())
    print(f"main frame_count={frame_count}, blend_path='{blend_path}, sessionID='{session_id}'")

    output_directory = Path("/tmp") / "render"
    output_directory.mkdir(parents=True, exist_ok=True)

    with volume.batch_upload() as batch:
        local_project_path = Path(blend_path)
        validate_blender_path(local_project_path)
        batch.put_file(local_project_path, blender_proj_remote_volume_upload_path(session_id))

    args = [
        (session_id, frameIdx) for frameIdx in range(1, frame_count + 1, 1)
    ]
    # print(f"args={len(args[0])}")

    results = list(test_render_image.starmap(args))
    print(results)

    # images = list(render.starmap(args))
    # for i, image in enumerate(images):
    #     frame_path = output_directory / f"frame_{i + 1}.png"
    #     frame_path.write_bytes(image)
    #     print(f"Frame saved to {frame_path}")
    #
    # video_path = output_directory / "output.mp4"
    # video_bytes = combine.remote(images)
    # video_path.write_bytes(video_bytes)
    # print(f"Video saved to {video_path}")