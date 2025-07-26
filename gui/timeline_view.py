#!/usr/bin/env python3
"""
TimelineView widget for displaying black frame segments visually.
Supports interaction with Marker, Split, and Selection tools.
"""

from typing import List, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, pyqtSignal


class TimelineView(QWidget):
    segmentClicked = pyqtSignal(int)  # emits clicked frame index

    def __init__(self):
        super().__init__()
        self.segments: List[Tuple[int, int]] = []
        self.video_length = 1  # total number of frames
        self.setMinimumHeight(50)

    def set_segments(self, segments: List[Tuple[int, int]], total_frames: int):
        """Set segments and total video length for display."""
        self.segments = segments
        self.video_length = max(total_frames, 1)
        self.update()

    def paintEvent(self, event):
        """Draw timeline and black segments."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(220, 220, 220))  # light gray background

        width = self.width()
        height = self.height()

        pen = QPen(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(QColor(50, 50, 50))  # black segments

        for start, end in self.segments:
            x1 = int((start / self.video_length) * width)
            x2 = int((end / self.video_length) * width)
            painter.drawRect(x1, 0, x2 - x1, height)

    def mousePressEvent(self, event):
        """Emit clicked frame based on position."""
        if event.button() == Qt.MouseButton.LeftButton:
            click_x = event.position().x()
            frame = int((click_x / self.width()) * self.video_length)
            self.segmentClicked.emit(frame)
