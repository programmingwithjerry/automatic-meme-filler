#!/usr/bin/env python3
"""
TimelineEditor - Manages black frame segments, markers, split operations, and undo/redo history.
Stage 9 version: Works with TimelineView for visual editing.
"""

from typing import List, Tuple


class TimelineEditor:
    def __init__(self):
        # List of black frame segments (start_frame, end_frame)
        self.segments: List[Tuple[int, int]] = []
        # Undo/redo stacks for editing history
        self.undo_stack: List[List[Tuple[int, int]]] = []
        self.redo_stack: List[List[Tuple[int, int]]] = []
        # Currently active editing tool ("Marker Tool", "Split Tool", etc.)
        self.active_tool: str = "Marker Tool"

    def set_segments(self, segments: List[Tuple[int, int]]):
        """Set detected black frame segments (push previous state to undo)."""
        self.undo_stack.append(self.segments.copy())
        self.segments = segments.copy()
        self.redo_stack.clear()

    def get_segments(self) -> List[Tuple[int, int]]:
        """Return current black frame segments."""
        return self.segments

    def add_marker(self, frame: int):
        """
        Add a new marker segment at a specific frame.
        Here we just add a small segment [frame, frame+5] for demonstration.
        """
        self.undo_stack.append(self.segments.copy())
        self.segments.append((frame, frame + 5))
        self.redo_stack.clear()

    def split_segment(self, frame: int):
        """
        Split an existing segment at a given frame, if the frame lies inside it.
        """
        self.undo_stack.append(self.segments.copy())
        for seg in self.segments:
            start, end = seg
            if start < frame < end:
                self.segments.remove(seg)
                self.segments.append((start, frame))
                self.segments.append((frame, end))
                break
        self.redo_stack.clear()

    def undo(self):
        """Undo the last action."""
        if not self.undo_stack:
            return None
        self.redo_stack.append(self.segments.copy())
        self.segments = self.undo_stack.pop()
        return self.segments

    def redo(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            return None
        self.undo_stack.append(self.segments.copy())
        self.segments = self.redo_stack.pop()
        return self.segments

    def set_tool(self, tool: str):
        """Set the currently active editing tool."""
        self.active_tool = tool
