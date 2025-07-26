#!/usr/bin/env python3
"""
Video Processor for Automatic Meme Filler App.
Stage 8: Adds zoom intensity and fade-out effect for inserted memes.
"""

import cv2
import numpy as np
from typing import List, Tuple


def detect_black_frames(video_path: str) -> List[Tuple[int, int]]:
    """
    Detect black frames (segments where brightness is very low).

    Returns:
        List of (start_frame, end_frame) tuples.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    segments = []
    threshold = 10  # brightness threshold
    start = None
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            if start is not None:
                segments.append((start, frame_idx - 1))
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean()

        if brightness < threshold:
            if start is None:
                start = frame_idx
        else:
            if start is not None:
                segments.append((start, frame_idx - 1))
                start = None

        frame_idx += 1

    cap.release()
    return segments


def insert_memes(
    video_path: str,
    output_path: str,
    black_segments: List[Tuple[int, int]],
    memes: List[str],
    zoom_factor: int = 2,
    fade_ms: int = 500
) -> None:
    """
    Replace black segments with memes, applying zoom and fade effects.

    Args:
        video_path: Path to input video.
        output_path: Path to save final edited video.
        black_segments: List of (start, end) black frame ranges.
        memes: List of meme file paths to insert.
        zoom_factor: Zoom multiplier for memes (e.g., 2 means 2x zoom).
        fade_ms: Fade-out duration in milliseconds.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Could not open input video.")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fade_frames = int((fade_ms / 1000.0) * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    segment_idx = 0
    meme_idx = 0
    black_start, black_end = (black_segments[segment_idx]
                              if black_segments else (None, None))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if black_start is not None and black_start <= frame_idx <= black_end:
            meme_path = memes[meme_idx % len(memes)]
            meme_img = cv2.imread(meme_path)
            if meme_img is not None:
                # Apply zoom
                zoomed = cv2.resize(meme_img, (int(width * zoom_factor), int(height * zoom_factor)))
                # Crop center to fit video size
                start_x = (zoomed.shape[1] - width) // 2
                start_y = (zoomed.shape[0] - height) // 2
                meme_resized = zoomed[start_y:start_y + height, start_x:start_x + width]

                # Apply fade-out at the end of the segment
                segment_length = black_end - black_start + 1
                fade_start = black_end - fade_frames
                alpha = 1.0
                if frame_idx >= fade_start:
                    alpha = max(0.0, (black_end - frame_idx) / max(1, fade_frames))
                frame = cv2.addWeighted(meme_resized, alpha, frame, 1 - alpha, 0)

        out.write(frame)

        if black_start is not None and frame_idx > black_end:
            segment_idx += 1
            meme_idx += 1
            if segment_idx < len(black_segments):
                black_start, black_end = black_segments[segment_idx]
            else:
                black_start, black_end = None, None

        frame_idx += 1

    cap.release()
    out.release()
