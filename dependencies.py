import modal
from pathlib import Path

app = modal.App("distributed-render")

rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("xorg", "libxkbcommon0")  # X11 (Unix GUI) dependencies
    .add_local_dir("/Users/johnrivera/workspace/distributed-render-modal/remote_opt", remote_path="/opt", copy=True)
    .run_commands("mkdir /tmp/blender && tar -xvzf /opt/blender.tar.gz -C /tmp/blender && mv /tmp/blender/opt/blender-dst /opt/blender")
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

def blender_proj_remote_path(session_id: str, validate: bool) -> Path:
    path = remote_job_path(session_id) / "project.blend"
    if validate:
        validate_blender_path(path)
    return path
