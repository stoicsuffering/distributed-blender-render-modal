from pathlib import Path
from dependencies import (
    app,
    combination_image,
    volume,
    VOLUME_MOUNT_PATH,
    remote_job_path,
    remote_job_frames_directory_path,
    volume_zip_path
)

@app.function(
    image=combination_image,
    volumes={VOLUME_MOUNT_PATH: volume},  # Attach the same volume
)
def zip_frames(session_id: str) -> str:
    """
    Zips all frames for the given session_id in the Volume
    and returns the *Volume path* to the resulting frames.zip file.
    """
    import subprocess

    # We'll store frames in /jobs/<session_id>/frames,
    # and we want to produce /jobs/<session_id>/frames.zip
    frames_dir = remote_job_frames_directory_path(session_id)
    out_zip = volume_zip_path(session_id)

    # Shell out to create a zip at maximum compression (-9).
    # We'll run this in job_dir so we can reference frames/ simply.
    subprocess.run(
        ["zip", "-9", "-r", out_zip.as_posix(), frames_dir.as_posix()],  # 'frames/'
        check=True
    )

    # Commit the changes to ensure the new frames.zip is visible
    volume.commit()

    # Return the path to the .zip *within* the Volume
    return out_zip.as_posix()