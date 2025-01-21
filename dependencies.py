import modal
from pathlib import Path

app = modal.App("distributed-render")

# Define your container images
rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("xorg", "libxkbcommon0")
    .pip_install("bpy==4.2.0")
    .pip_install("pathlib==1.0.1")
)

combination_image = (
    modal.Image.debian_slim(python_version="3.11")
)

volume = modal.Volume.from_name("distributed-render", create_if_missing=True)
VOLUME_MOUNT_PATH = Path("/jobs")

def validate_blender_path(path: Path):
    assert path.exists()
    assert path.is_file()
    assert path.suffix == ".blend"

def blender_proj_remote_volume_upload_path(session_id: str) -> Path:
    return Path(f"{session_id}/project.blend")

def remote_job_path(session_id: str) -> Path:
    return VOLUME_MOUNT_PATH / session_id

def remote_job_frames_directory_path(session_id: str) -> Path:
    return VOLUME_MOUNT_PATH / session_id / "frames"

def remote_job_frame_path(session_id: str, frame: int) -> Path:
    return remote_job_frames_directory_path(session_id) / f"frame_{frame:05}.exr"

def blender_proj_remote_path(session_id: str, validate: bool) -> Path:
    path = remote_job_path(session_id) / "project.blend"
    if validate:
        validate_blender_path(path)
    return path

def volume_zip_path(session_id: str) -> Path:
    return VOLUME_MOUNT_PATH / session_id / "frames.zip"

def volume_zip_local_download_path(session_id: str) -> Path:
    return Path("/session_id") / "frames.zip"