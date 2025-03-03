import math
from typing import List, Tuple


def chunk_frames(frame_count: int, chunk_size: int) -> List[Tuple[int, int]]:
    """
    Splits a frame range into evenly sized chunks, assuming a zero-based start.

    Args:
        frame_count (int): Total number of frames in the range.
        chunk_size (int): Maximum frames per chunk.

    Returns:
        list: List of (start_offset, end_offset) tuples, zero-based.
    """
    num_chunks = math.ceil(frame_count / chunk_size)

    return [
        (i * chunk_size, min((i + 1) * chunk_size - 1, frame_count - 1))
        for i in range(num_chunks)
    ]


def chunk_frame_range(start: int, end: int, chunk_size: int) -> List[Tuple[int, int]]:
    """
    Applies chunk_frames() while preserving the original start frame offset.

    Args:
        start (int): Start frame number.
        end (int): End frame number.
        chunk_size (int): Maximum frames per chunk.

    Returns:
        list: List of (start_frame, end_frame) tuples adjusted for the offset.
    """
    frame_count = end - start + 1  # Total frames in range
    zero_based_chunks = chunk_frames(frame_count, chunk_size)

    # Apply offset to map zero-based chunks to actual frame numbers
    return [(start + chunk_start, start + chunk_end) for chunk_start, chunk_end in zero_based_chunks]


def chunk_frame_ranges(camera_ranges: List[Tuple[str, int, int]], concurrency_limit: int) -> List[
    Tuple[str, int, int, str]]:
    """
    Determines an optimal chunk size and applies chunk_frame_range() to multiple camera frame ranges.

    Args:
        camera_ranges (list): List of tuples (camera_name, start_frame, end_frame).
        concurrency_limit (int): Maximum number of concurrent render jobs.

    Returns:
        list: List of (camera_name, start_frame, end_frame, sequence_id) tuples.
    """
    # Calculate total frame count across all camera ranges
    total_frames = sum((end - start + 1) for _, start, end in camera_ranges)

    # Determine optimal chunk size
    chunk_size = max(1, math.ceil(total_frames / concurrency_limit))

    print(f"Total frames: {total_frames}, Concurrency limit: {concurrency_limit}, Computed chunk size: {chunk_size}")

    chunked_frames = []

    for camera_name, start, end in camera_ranges:
        chunks = chunk_frame_range(start, end, chunk_size)
        for chunk_start, chunk_end in chunks:
            sequence_id = f"{camera_name}-{chunk_start}-{chunk_end}"
            chunked_frames.append((camera_name, chunk_start, chunk_end, sequence_id))

    return chunked_frames


def test():
    # Example: Flattened Camera Ranges
    # camera_ranges = [
    #     ("Camera A", 1, 240),
    #     ("Camera A", 700, 1000),
    #     ("Camera B", 200, 500),
    #     ("Camera C", 900, 1500)
    # ]
    #
    # # Define concurrency limit (e.g., 30 concurrent render jobs)
    # concurrency_limit = 30
    #
    # # Process frame chunking
    # result = chunk_frame_ranges(camera_ranges, concurrency_limit)

    animations = chunk_frame_range(1, 24, chunk_size=10)
    print(animations)
    #
    # # Print results
    # print("Chunked Frame Ranges:")
    # for camera_name, start, end, sequence_id in result:
    #     print(f"{camera_name}: [{start} - {end}] -> {sequence_id}")

# test()