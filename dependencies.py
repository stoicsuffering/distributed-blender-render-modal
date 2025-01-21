import modal
from pathlib import Path

app = modal.App("distributed-render")

# cuda_version = "12.4.0"  # should be no greater than host CUDA version
# flavor = "devel"  #  includes full CUDA toolkit
# operating_sys = "ubuntu22.04"
# tag = f"{cuda_version}-{flavor}-{operating_sys}"

# Define your container images
rendering_image = (
    modal.Image.debian_slim(python_version="3.11")
        .apt_install("xorg", "libxkbcommon0")
        .pip_install("bpy==4.2.0")
        .pip_install("pathlib==1.0.1")
    # modal.Image.from_registry(
    #     f"nvidia/cuda:{tag}",
    #     add_python="3.11",
    #     setup_dockerfile_commands=[
    #         "RUN apt update",
    #         "RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt install software-properties-common -y",
    #         "RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt install xorg libxkbcommon0 -y",
    #         "RUN apt install python3.11 python3-pip -y",
    #     ],
    # )
    # .pip_install("bpy==4.2.0")
    # .pip_install("pathlib==1.0.1")
    # # .dockerfile_commands([
    # #     "snap install blender --channel=4.2lts/stable --classic"
    # # ])
)

combination_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("zip")
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

# TODO: modal volume get distributed-render /bafb32b4-2516-4439-9d0c-d52fdb305409/frames.zip /tmp/renders/bafb32b4-2516-4439-9d0c-d52fdb305409/local_frames.zip is correct, not what I'm printing
def volume_zip_path(session_id: str) -> Path:
    return VOLUME_MOUNT_PATH / session_id / "frames.zip"

def volume_zip_local_download_path(session_id: str) -> str:
    return f"/tmp/renders/{session_id}.zip"