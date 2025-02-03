from pathlib import Path

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

def remote_job_frames_absolute_volume_directory_path(session_id: str) -> Path:
    return Path("/") / session_id / "frames"

def blender_proj_remote_path(session_id: str, validate: bool) -> Path:
    path = remote_job_path(session_id) / "project.blend"
    if validate:
        validate_blender_path(path)
    return path