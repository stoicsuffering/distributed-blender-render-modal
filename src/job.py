import os
import configparser
from typing import Literal
from paths import blender_proj_remote_path, remote_job_frames_directory_path
from chunking import chunk_frame_range
import math

# Allowed render engine values.
RenderEngine = Literal["BLENDER_EEVEE_NEXT", "CYCLES"]

class Job:
    """
    A Job holds both rendering/hardware parameters and project-specific settings.

    The following keys must be defined in the job's section (and cannot come from defaults):
      - blend_file_path
      - start_frame
      - end_frame
    """

    def __init__(
            self,
            job_name: str,
            session_id: str,
            render_node_concurrency_target: int,
            render_engine: RenderEngine,
            blend_file_path: str,
            camera_name: str,
            overall_start_frame: int,
            overall_end_frame: int,
            width: int,
            height: int,
            render_max_samples: int,
            render_adaptive_threshold: float,
            eco_mode_enabled: bool,
            min_chunk_size: int,
            max_chunk_size: int
    ):
        self.job_name = job_name
        self.session_id = session_id
        self.render_node_concurrency_target = render_node_concurrency_target
        self.render_engine = render_engine
        self.blend_file_path = blend_file_path
        self.camera_name = camera_name
        self.overall_start_frame = overall_start_frame
        self.overall_end_frame = overall_end_frame
        self.width = width
        self.height = height
        self.render_max_samples = render_max_samples
        self.render_adaptive_threshold = render_adaptive_threshold
        self.eco_mode_enabled = eco_mode_enabled
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def __repr__(self):
        return (f"Job(name={self.job_name}, session_id={self.session_id}, render_node_concurrency_target={self.render_node_concurrency_target}, "
                f"render_engine={self.render_engine}, "
                f"blend_file_path={self.blend_file_path}, camera_name={self.camera_name}, "
                f"width={self.width}, height={self.height}, "
                f"render_max_samples={self.render_max_samples}, render_adaptive_threshold={self.render_adaptive_threshold}, eco_mode_enabled={self.eco_mode_enabled}, "
                f"start_frame={self.overall_start_frame}, end_frame={self.overall_end_frame}, "
                f"min_chunk_size={self.min_chunk_size}, "
                f"max_chunk_size={self.max_chunk_size})")

    def chunk_size(self) -> int:
        chunk_size = math.ceil(self.frame_count() / self.render_node_concurrency_target)
        return min(self.max_chunk_size, max(self.min_chunk_size, chunk_size))

    def frame_count(self) -> int:
        frame_count = self.overall_end_frame - self.overall_start_frame
        if self.overall_end_frame == self.overall_start_frame:
            frame_count = 1
        return frame_count

    def validate(self):
        if self.frame_count() < 1 or self.overall_start_frame < 1:
            raise Exception("Invalid frame range")

class JobChunk:
    def __init__(
            self,
            job: Job,
            chunk_start_frame: int,
            chunk_end_frame: int
    ):
        self.job = job
        self.chunk_start_frame = chunk_start_frame
        self.chunk_end_frame = chunk_end_frame

    def __repr__(self):
        return f"JobChunk(chunk_start_frame={self.chunk_start_frame}, chunk_end_frame={self.chunk_end_frame}, job={self.job})"

    def remote_blender_proj_path(self) -> str:
        return str(blender_proj_remote_path(self.job.session_id, validate=True))

    def make_remote_frame_path(self) -> str:
        base_output_dir = remote_job_frames_directory_path(self.job.session_id)
        base_output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        return str(base_output_dir / f"{self.job.job_name}_")  # Base file path for animation frames

# Helpers

def job_chunks_from_job(job: Job) -> list[JobChunk]:
    frame_count = job.frame_count()
    chunk_size = math.ceil(frame_count / job.render_node_concurrency_target)
    chunk_size = min(job.max_chunk_size, max(job.min_chunk_size, chunk_size))
    chunks = chunk_frame_range(job.overall_start_frame, job.overall_end_frame, chunk_size=chunk_size)
    print(f"Splitting {frame_count} frames into chunks of {chunk_size}, chunks={chunks}")
    return [JobChunk(job=job, chunk_start_frame=chunk[0], chunk_end_frame=chunk[1]) for chunk in chunks]

def selected_job(session_id: str) -> Job:
    # Compute the absolute path to your INI file (one level up from the src directory).
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    config_file_path = os.path.join(project_root, "jobs.ini")
    print(f"current_dir: {current_dir}. project_root: {project_root}, config_file_path: {config_file_path}")

    config = configparser.ConfigParser()
    read_files = config.read(config_file_path)
    if not read_files:
        raise FileNotFoundError(f"Configuration file '{config_file_path}' not found.")

    # Load the current job name from the [RUN] section.
    try:
        current_job_name = config.get("RUN", "CURRENT_JOB")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        raise ValueError(
            "The 'RUN' section with 'CURRENT_JOB' property is missing in the configuration file.") from e

    print("Current job:", current_job_name)

    # Ensure the specified job section exists.
    if current_job_name not in config.sections():
        raise ValueError(f"Job '{current_job_name}' not found in the configuration file.")

    # Define keys required in the job configuration.
    # Some keys can be inherited from [DEFAULT]...
    required_keys = [
        "render_node_concurrency_target",
        "render_engine",
        "min_chunk_size",
        "max_chunk_size",
        "width",
        "height",
        "eco_mode_enabled",
        "render_max_samples",
        "render_adaptive_threshold"
    ]
    # ...but these keys must be defined explicitly in the job section.
    job_specific_keys = [
        "blend_file_path",
        "camera_name",
        "start_frame",
        "end_frame"
    ]

    # First, check that job-specific keys are defined in the job section.
    # (Using the internal _sections dict to bypass fallback to DEFAULT.)
    job_section = config._sections.get(current_job_name, {})
    for key in job_specific_keys:
        if key not in job_section:
            raise ValueError(
                f"Missing required job-specific key '{key}' in job '{current_job_name}'. "
                "It must be defined in the job section (not in the [DEFAULT] section)."
            )

    # Now check that all required keys are available (either in the job section or as defaults).
    for key in required_keys + job_specific_keys:
        if config.get(current_job_name, key, fallback=None) is None:
            raise ValueError(
                f"Missing required key '{key}' in job '{current_job_name}'. "
                "Define it in the job section or in the [DEFAULT] section (if allowed)."
            )

    # Read and convert the values.
    render_node_concurrency_target = config.getint(current_job_name, "render_node_concurrency_target")
    render_engine_str = config.get(current_job_name, "render_engine").strip().upper()

    if render_engine_str in ("BLENDER_EEVEE_NEXT", "CYCLES"):
        render_engine: RenderEngine = render_engine_str  # type: ignore
    else:
        raise ValueError(f"Unknown render engine '{render_engine_str}'.")

    return Job(
        job_name=current_job_name,
        session_id=session_id,
        render_node_concurrency_target=render_node_concurrency_target,
        render_engine=render_engine,
        blend_file_path=config.get(current_job_name, "blend_file_path"),
        camera_name=config.get(current_job_name, "camera_name"),
        overall_start_frame=config.getint(current_job_name, "start_frame"),
        overall_end_frame=config.getint(current_job_name, "end_frame"),
        width=config.getint(current_job_name, "width"),
        height=config.getint(current_job_name, "height"),
        render_max_samples=config.getint(current_job_name, "render_max_samples"),
        render_adaptive_threshold=config.getfloat(current_job_name, "render_adaptive_threshold"),
        eco_mode_enabled=config.getboolean(current_job_name, "eco_mode_enabled"),
        min_chunk_size=config.getint(current_job_name, "min_chunk_size"),
        max_chunk_size=config.getint(current_job_name, "max_chunk_size"),
    )