import os
import configparser
import sys
from typing import Literal

# Allowed render engine values.
RenderEngine = Literal["BLENDER_EEVEE_NEXT", "CYCLES"]

class SubJob:
    """
    A SubJob holds the task-specific information extracted from a Job.
    For example, the blend file path, frame range, and camera to be used.
    """

    def __init__(self, blend_file_path: str, start_frame: int, end_frame: int, camera_name: str):
        self.blend_file_path = blend_file_path
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.camera_name = camera_name

    def __repr__(self):
        return (f"SubJob(blend_file_path={self.blend_file_path}, "
                f"start_frame={self.start_frame}, end_frame={self.end_frame}, "
                f"camera_name={self.camera_name})")


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
            render_node_concurrency_target: int,
            render_engine: RenderEngine,
            blend_file_path: str,
            start_frame: int,
            end_frame: int,
            width: int,
            height: int,
            render_max_samples: int,
            render_adaptive_threshold: float,
            eco_mode_enabled: bool,
            min_chunk_size: int,
            max_chunk_size: int,
    ):
        self.render_node_concurrency_target = render_node_concurrency_target
        self.render_engine = render_engine
        self.blend_file_path = blend_file_path
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.width = width
        self.height = height
        self.render_max_samples = render_max_samples
        self.render_adaptive_threshold = render_adaptive_threshold
        self.eco_mode_enabled = eco_mode_enabled
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def __repr__(self):
        return (f"Job(render_node_concurrency_target={self.render_node_concurrency_target}, "
                f"render_engine={self.render_engine}, "
                f"blend_file_path={self.blend_file_path}, "
                f"width={self.width}, height={self.height}, "
                f"render_max_samples={self.render_max_samples}, render_adaptive_threshold={self.render_adaptive_threshold}, eco_mode_enabled={self.eco_mode_enabled}, "
                f"start_frame={self.start_frame}, end_frame={self.end_frame}, "
                f"min_chunk_size={self.min_chunk_size}, "
                f"max_chunk_size={self.max_chunk_size})")

    @staticmethod
    def current_job():
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
        ]
        # ...but these keys must be defined explicitly in the job section.
        job_specific_keys = [
            "blend_file_path",
            "start_frame",
            "end_frame",
            "width",
            "height",
            "render_max_samples",
            "render_adaptive_threshold",
            "eco_mode_enabled"
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
            render_node_concurrency_target=render_node_concurrency_target,
            render_engine=render_engine,
            blend_file_path=config.get(current_job_name, "blend_file_path"),
            start_frame=config.getint(current_job_name, "start_frame"),
            end_frame=config.getint(current_job_name, "end_frame"),
            width=config.getint(current_job_name, "width"),
            height=config.getint(current_job_name, "height"),
            render_max_samples=config.getint(current_job_name, "render_max_samples"),
            render_adaptive_threshold=config.getfloat(current_job_name, "render_adaptive_threshold"),
            eco_mode_enabled=config.getboolean(current_job_name, "eco_mode_enabled"),
            min_chunk_size=config.getint(current_job_name, "min_chunk_size"),
            max_chunk_size=config.getint(current_job_name, "max_chunk_size"),
        )

    def create_sub_job(self) -> SubJob:
        """
        Create a SubJob instance using values from this Job.
        """
        return SubJob(
            blend_file_path=self.blend_file_path,
            start_frame=self.start_frame,
            end_frame=self.end_frame,
        )