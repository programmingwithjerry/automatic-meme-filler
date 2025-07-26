#!/usr/bin/env python3
"""
MainWindow for Automatic Meme Filler App with in-app video preview.
Stage 10: Plays video inside the app using OpenCV + QLabel.
"""

import sys, os, tempfile, cv2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QScrollArea,
    QCheckBox, QFrame, QMessageBox, QStatusBar,
    QSlider, QComboBox, QSizePolicy
)
#from PyQt6.QtCore import Qt, QTimer, QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

from core.video_processor import detect_black_frames, insert_memes
from utils.meme_loader import get_random_memes, load_meme_library
from gui.timeline_editor import TimelineEditor
from gui.timeline_view import TimelineView


class MemeFillerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automatic Meme Filler - Stage 10")
        self.setMinimumSize(900, 700)

        self.video_path = None
        self.timeline = TimelineEditor()
        self.meme_library = load_meme_library("memes")
        self.selected_categories = set()

        # Video preview variables
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.playing = False

        # --- Central widget ---
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Video preview area ---
        self.video_label = QLabel("Video preview will appear here")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setMinimumHeight(300)
        layout.addWidget(self.video_label)

        # --- Playback controls ---
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        playback_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_video)
        playback_layout.addWidget(self.stop_btn)
        layout.addLayout(playback_layout)

        # --- Top buttons ---
        top_btns = QHBoxLayout()
        for btn_text, handler in [
            ("Load Video", self.load_video),
            ("Detect Black Frames", self.detect_black_frames),
            ("Undo", self.undo_edit),
            ("Redo", self.redo_edit)
        ]:
            btn = QPushButton(btn_text)
            btn.clicked.connect(handler)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if btn_text in ("Undo", "Redo"):
                btn.setEnabled(False)
                if btn_text == "Undo":
                    self.undo_btn = btn
                else:
                    self.redo_btn = btn
            top_btns.addWidget(btn)
        layout.addLayout(top_btns)

        # --- Tool picker ---
        self.tool_picker = QComboBox()
        self.tool_picker.addItems(["Marker Tool", "Split Tool", "Selection Tool"])
        self.tool_picker.currentIndexChanged.connect(self.change_tool)
        layout.addWidget(self.tool_picker)

        # --- Sliders ---
        sliders_layout = QHBoxLayout()

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(5)
        self.zoom_slider.setValue(2)
        sliders_layout.addWidget(QLabel("Zoom Intensity"))
        sliders_layout.addWidget(self.zoom_slider)

        self.fade_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_slider.setMinimum(0)
        self.fade_slider.setMaximum(2000)
        self.fade_slider.setValue(500)
        sliders_layout.addWidget(QLabel("Fade-out Duration (ms)"))
        sliders_layout.addWidget(self.fade_slider)

        layout.addLayout(sliders_layout)

        # --- Timeline View ---
        self.timeline_view = TimelineView()
        self.timeline_view.segmentClicked.connect(self.on_timeline_click)
        layout.addWidget(self.timeline_view)

        # --- Scrollable meme categories ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        category_widget = QWidget()
        self.category_layout = QVBoxLayout(category_widget)
        for category in self.meme_library:
            cb = QCheckBox(category)
            cb.stateChanged.connect(self.update_selected_categories)
            self.category_layout.addWidget(cb)
        scroll.setWidget(category_widget)
        layout.addWidget(scroll, stretch=1)

        # --- Preview & Export ---
        action_btns = QHBoxLayout()
        self.preview_btn = QPushButton("Preview Memes")
        self.preview_btn.clicked.connect(self.preview_memes)
        action_btns.addWidget(self.preview_btn)

        self.export_btn = QPushButton("Export Video with Memes")
        self.export_btn.clicked.connect(self.export_video)
        action_btns.addWidget(self.export_btn)

        layout.addLayout(action_btns)

        # --- Status bar ---
        self.status_label = QLabel("Load a video to get started.")
        self.status_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        layout.addWidget(self.status_label)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    # ----------------- Video Player Functions -----------------
    def toggle_play(self):
        if not self.cap:
            return
        if self.playing:
            self.timer.stop()
            self.play_btn.setText("Play")
            self.playing = False
        else:
            self.timer.start(int(1000 / max(self.cap.get(cv2.CAP_PROP_FPS), 24)))
            self.play_btn.setText("Pause")
            self.playing = True

    def stop_video(self):
        if self.cap:
            self.timer.stop()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.play_btn.setText("Play")
            self.playing = False
            self.next_frame()

    def next_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.play_btn.setText("Play")
            self.playing = False
            return
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    # ----------------- Existing Logic -----------------
    def refresh_timeline(self):
        if not self.video_path:
            return
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) if self.cap else 1000
        self.timeline_view.set_segments(self.timeline.get_segments(), total_frames)

    def on_timeline_click(self, frame: int):
        tool = self.timeline.active_tool
        if tool == "Marker Tool":
            self.timeline.add_marker(frame)
        elif tool == "Split Tool":
            self.timeline.split_segment(frame)
        elif tool == "Selection Tool":
            self.timeline.add_marker(frame)
        self.refresh_timeline()
        self.update_undo_redo_buttons()

    def update_status(self, text: str):
        self.status_label.setText(text)
        self.status_bar.showMessage(text, 5000)

    def change_tool(self):
        tool = self.tool_picker.currentText()
        self.timeline.set_tool(tool)
        self.update_status(f"Tool changed to: {tool}")

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov)")
        if path:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Error", "Could not open video.")
                return
            self.video_path = path
            self.update_status(f"Loaded video: {os.path.basename(path)}")
            self.stop_video()

    def detect_black_frames(self):
        if not self.video_path:
            QMessageBox.warning(self, "No Video", "Please load a video first.")
            return
        self.update_status("Detecting black frames...")
        segments = detect_black_frames(self.video_path)
        self.timeline.set_segments(segments)
        self.refresh_timeline()
        self.update_status(f"Detected {len(segments)} black segments.")
        self.update_undo_redo_buttons()

    def undo_edit(self):
        updated = self.timeline.undo()
        if updated is None:
            QMessageBox.information(self, "Undo", "No more actions to undo.")
        else:
            self.refresh_timeline()
            self.update_status(f"Undo performed. Segments: {len(updated)}")
        self.update_undo_redo_buttons()

    def redo_edit(self):
        updated = self.timeline.redo()
        if updated is None:
            QMessageBox.information(self, "Redo", "No more actions to redo.")
        else:
            self.refresh_timeline()
            self.update_status(f"Redo performed. Segments: {len(updated)}")
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        self.undo_btn.setEnabled(bool(self.timeline.undo_stack))
        self.redo_btn.setEnabled(bool(self.timeline.redo_stack))

    def update_selected_categories(self):
        self.selected_categories.clear()
        for i in range(self.category_layout.count()):
            cb = self.category_layout.itemAt(i).widget()
            if cb.isChecked():
                self.selected_categories.add(cb.text())

    def preview_memes(self):
        if not self.video_path:
            QMessageBox.warning(self, "No Video", "Please load a video first.")
            return
        if not self.timeline.get_segments():
            QMessageBox.warning(self, "No Black Frames", "No black frames detected.")
            return
        memes = get_random_memes(self.meme_library, self.selected_categories, len(self.timeline.get_segments()))
        if not memes:
            QMessageBox.warning(self, "No Memes", "No memes available for the selected categories.")
            return
        zoom_factor = self.zoom_slider.value()
        fade_ms = self.fade_slider.value()
        temp_path = os.path.join(tempfile.gettempdir(), "preview_with_memes.mp4")
        insert_memes(self.video_path, temp_path, self.timeline.get_segments(), memes,
                     zoom_factor=zoom_factor, fade_ms=fade_ms)
        self.cap.release()
        self.cap = cv2.VideoCapture(temp_path)
        self.stop_video()

    def export_video(self):
        if not self.video_path:
            QMessageBox.warning(self, "No Video", "Please load a video first.")
            return
        if not self.timeline.get_segments():
            QMessageBox.warning(self, "No Black Frames", "No black frames detected.")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Edited Video", "", "MP4 Files (*.mp4)")
        if not output_path:
            return
        if not output_path.lower().endswith(".mp4"):
            output_path += ".mp4"
        memes = get_random_memes(self.meme_library, self.selected_categories, len(self.timeline.get_segments()))
        if not memes:
            QMessageBox.warning(self, "No Memes", "No memes available for the selected categories.")
            return
        zoom_factor = self.zoom_slider.value()
        fade_ms = self.fade_slider.value()
        try:
            insert_memes(self.video_path, output_path, self.timeline.get_segments(), memes,
                         zoom_factor=zoom_factor, fade_ms=fade_ms)
            self.update_status(f"Video exported successfully: {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("bootstrap.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("bootstrap.qss not found, running with default theme.")
    window = MemeFillerApp()
    window.show()
    sys.exit(app.exec())
