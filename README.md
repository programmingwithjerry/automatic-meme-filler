# Automatic Meme Filler

A desktop video editing tool that **automatically detects black frames or black screen gaps** in videos and fills them with meme images or videos.  
Designed for **fast meme-style editing** — making empty moments fun and engaging.

---

## ✨ Features

- **Black Frame Detection**: Automatically scans videos for black screen segments.
- **Meme Auto-Insertion**: Fills detected gaps with randomly selected memes.
- **Meme Categorization & Filtering**: Choose from tagged meme categories (funny, reaction, gaming, etc.).
- **Interactive Timeline**: Edit and preview insertion points on a timeline view.
- **Real-time Video Preview**: Play and pause your video directly in the app.
- **Dynamic Zoom & Fade Effects**: Add smooth animations to inserted memes.
- **Undo/Redo Support**: Easily correct mistakes while editing.
- **Export Video**: Save your edited video with memes added.
- **Cross-platform**: Works on Windows, Linux, and macOS.

---

## 🛠 Tech Stack

- **Python 3.10+**
- **PyQt6** for GUI
- **OpenCV** for video preview and frame processing
- **FFmpeg** for final video export
- **QSS (Bootstrap-inspired)** for a clean UI design

---

## 📂 Project Structure
automatic-meme-filler/
├── gui/
│ ├── main_window.py # Main application window
│ ├── timeline_editor.py # Timeline editor logic
│ ├── timeline_view.py # Timeline visualization
├── core/
│ └── video_processor.py # Video processing & meme insertion
├── utils/
│ └── meme_loader.py # Loads meme packs & categories
├── memes/ # Meme pack folder (images & videos)
├── bootstrap.qss # UI theme
└── README.md # Project documentation


## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/automatic-meme-filler.git
   cd automatic-meme-filler

2. Set up a virtual environment (optional but recommended):
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

3. Install dependencies:
pip install PyQt6 opencv-python ffmpeg-python

4. Ensure FFmpeg is installed:
https://ffmpeg.org/download.html

USAGE:
Run the app
python3 gui/main_window.py

Load a video.

Detect black frames.

Select meme categories.

Preview memes (real-time video preview inside the app).

Export the final edited video.

🤝 Contributing
Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to change.

📄 License
This project is licensed under the MIT License.
