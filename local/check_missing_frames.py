#!/usr/bin/env python3

import sys
import os
import re


def check_contiguous_frames(directory):
    """
    Checks for contiguous frames in the specified directory, assuming
    filenames in the format: frame_XXXX.exr
    e.g., frame_0001.exr, frame_0002.exr, etc.
    """
    # Regex to match the frame number from filenames like frame_0001.exr
    pattern = re.compile(r'^frame_(\d{4})\.exr$')

    # Collect frame numbers
    frame_numbers = []

    # Walk through directory and find all matching files
    for fname in os.listdir(directory):
        match = pattern.match(fname)
        if match:
            # Convert the extracted string to integer
            frame_num = int(match.group(1))
            frame_numbers.append(frame_num)

    if not frame_numbers:
        print("No frames matching the pattern 'frame_XXXX.exr' were found.")
        return

    # Sort frame numbers
    frame_numbers.sort()

    # Determine min and max
    min_frame = frame_numbers[0]
    max_frame = frame_numbers[-1]

    # Identify missing frames
    missing_frames = []
    for frame_id in range(min_frame, max_frame + 1):
        if frame_id not in frame_numbers:
            missing_frames.append(frame_id)

    # Print results
    if missing_frames:
        print("Missing frames:")
        for mf in missing_frames:
            # Format the frame number back to 4 digits, if desired
            print(f"frame_{mf:04d}.exr")
    else:
        print("All frames are contiguous (no missing frames).")


def main():
    # Simple arg check
    if len(sys.argv) < 2:
        print("Usage: python check_frames.py <directory_path>")
        sys.exit(1)

    directory = sys.argv[1]

    # Validate directory
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    check_contiguous_frames(directory)


if __name__ == "__main__":
    main()