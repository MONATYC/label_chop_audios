from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QSlider,
    QProgressBar,
    QApplication,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QImage, QIcon, QShortcut, QKeySequence
import os
import numpy as np
import sounddevice as sd
import soundfile as sf
from config import CONFIG
from audio_processor.cutter import cut_audio_segment
from audio_processor.spectrogram_generator import (
    generate_spectrogram_pixmap,
    draw_playback_line,
    draw_annotations,
)
from utils.file_manager import get_audio_files_in_folder, create_directory_if_not_exists
from utils.logger import load_labeled_audios_log, log_labeled_audio
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Labeling Tool")
        self.setGeometry(100, 100, 900, 600)

        self.audio_files = []
        self.current_audio_index = -1
        self.current_audio_data = None
        self.current_samplerate = None
        self.playback_stream = None
        self.playback_stream_id = 0
        self.playback_position = 0
        self.is_playing = False
        self.annotations = []  # Stores (start_time, end_time, category)
        self.base_spectrogram = None
        self.spectrogram_bounds = None
        self.temp_start_time = None
        self.icons_path = os.path.join(os.path.dirname(__file__), "icons")
        self.shortcuts = CONFIG.get("SHORTCUTS", {})

        self.init_ui()
        self.labeled_audios = load_labeled_audios_log()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)


        # Folder selection
        self.folder_select_button = QPushButton("Select Audio Folder")
        self.folder_select_button.clicked.connect(self.select_audio_folder)
        self.main_layout.addWidget(self.folder_select_button)

        # Top status bar showing current file
        self.status_layout = QHBoxLayout()
        self.status_icon = QLabel()
        audio_pix = QPixmap(os.path.join(self.icons_path, "audio.svg"))
        self.status_icon.setPixmap(audio_pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation))
        self.status_label = QLabel("No audio loaded.")
        self.status_layout.addWidget(self.status_icon)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addStretch()
        self.main_layout.addLayout(self.status_layout)

        self.metadata_label = QLabel("")
        self.main_layout.addWidget(self.metadata_label)

        self.load_progress = QProgressBar()
        self.load_progress.setRange(0, 100)
        self.load_progress.hide()
        self.main_layout.addWidget(self.load_progress)

        # Spectrogram display
        self.spectrogram_label = QLabel("Spectrogram will appear here.")
        self.spectrogram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spectrogram_label.setMouseTracking(
            True
        )  # Enable mouse tracking for selection
        self.spectrogram_label.mousePressEvent = self.spectrogram_mouse_press
        self.spectrogram_label.mouseReleaseEvent = self.spectrogram_mouse_release
        self.main_layout.addWidget(self.spectrogram_label)

        # Playback controls
        self.playback_layout = QHBoxLayout()
        self.play_pause_button = QPushButton(
            f"Play ({self.shortcuts.get('play_pause', '')})"
        )
        self.play_pause_button.setIcon(QIcon(os.path.join(self.icons_path, "play.svg")))
        self.play_pause_button.setIconSize(QSize(24, 24))
        self.play_pause_button.clicked.connect(self.toggle_playback)
        self.play_pause_button.setFixedHeight(40)
        self.playback_layout.addWidget(self.play_pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setIcon(QIcon(os.path.join(self.icons_path, "stop.svg")))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.clicked.connect(
            lambda: self.stop_playback(reset_position=True)
        )
        self.stop_button.setFixedHeight(40)
        self.playback_layout.addWidget(self.stop_button)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_playback_position)
        self.playback_layout.addWidget(self.position_slider)
        self.main_layout.addLayout(self.playback_layout)

        # Labeling controls
        self.labeling_layout = QHBoxLayout()

        self.category_selector = QComboBox()
        self.category_selector.addItems(CONFIG["CATEGORIES"])
        self.labeling_layout.addWidget(self.category_selector)

        self.mark_start_button = QPushButton(
            f"Mark Start ({self.shortcuts.get('mark_start', '')})"
        )
        self.mark_start_button.clicked.connect(self.mark_start)
        self.labeling_layout.addWidget(self.mark_start_button)

        self.mark_end_button = QPushButton(
            f"Mark End ({self.shortcuts.get('mark_end', '')})"
        )
        self.mark_end_button.clicked.connect(self.mark_end)
        self.labeling_layout.addWidget(self.mark_end_button)

        self.save_labels_button = QPushButton("Save Labels & Cut")
        self.save_labels_button.clicked.connect(self.save_labels_and_cut)
        self.labeling_layout.addWidget(self.save_labels_button)
        self.main_layout.addLayout(self.labeling_layout)

        # Navigation buttons
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Audio")
        self.prev_button.clicked.connect(self.load_previous_audio)
        self.prev_button.setFixedHeight(36)
        self.nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton(
            f"Next Audio ({self.shortcuts.get('next_audio', '')})"
        )
        self.next_button.setIcon(QIcon(os.path.join(self.icons_path, "next.svg")))
        self.next_button.setIconSize(QSize(20, 20))
        self.next_button.clicked.connect(self.load_next_audio)
        self.next_button.setFixedHeight(36)
        self.nav_layout.addWidget(self.next_button)
        self.main_layout.addLayout(self.nav_layout)

        self.update_timer = QTimer(self)
        self.update_timer.setInterval(50)  # Update every 50ms
        self.update_timer.timeout.connect(self.update_playback_line)
        self.update_timer.start()

        # Keyboard shortcuts
        if sc := self.shortcuts.get("play_pause"):
            QShortcut(QKeySequence(sc), self, activated=self.toggle_playback)
        if sc := self.shortcuts.get("mark_start"):
            QShortcut(QKeySequence(sc), self, activated=self.mark_start)
        if sc := self.shortcuts.get("mark_end"):
            QShortcut(QKeySequence(sc), self, activated=self.mark_end)
        if sc := self.shortcuts.get("next_audio"):
            QShortcut(QKeySequence(sc), self, activated=self.load_next_audio)

    def select_audio_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Audio Folder")
        if folder_path:
            self.audio_files = get_audio_files_in_folder(
                folder_path, CONFIG["AUDIO_EXTENSIONS"]
            )

            if not self.audio_files:
                self.status_label.setText(
                    "No supported audio files found in selected folder."
                )
                return

            self.current_audio_index = -1
            self.load_next_audio()  # Load the first audio

    def load_audio(self, index):
        if not (0 <= index < len(self.audio_files)):
            return

        audio_path = self.audio_files[index]
        self.status_label.setText(f"Loading: {os.path.basename(audio_path)}")

        try:
            with sf.SoundFile(audio_path) as f:
                self.current_samplerate = f.samplerate
                frames = f.frames
                self.current_audio_data = np.empty(frames, dtype="float32")
                block = 65536
                read = 0
                self.load_progress.show()
                while read < frames:
                    chunk = f.read(min(block, frames - read), dtype="float32")
                    if chunk.ndim > 1:
                        chunk = chunk[:, 0]
                    length = len(chunk)
                    self.current_audio_data[read : read + length] = chunk
                    read += length
                    self.load_progress.setValue(int((read / frames) * 100))
                    QApplication.processEvents()
                self.load_progress.hide()
            self.current_audio_index = index
            self.playback_position = 0
            self.position_slider.setRange(0, len(self.current_audio_data) - 1)
            self.position_slider.setValue(0)
            duration = len(self.current_audio_data) / self.current_samplerate
            size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            self.metadata_label.setText(
                f"{self.current_samplerate} Hz | {duration:.2f}s | {size_mb:.2f} MB"
            )
            (
                self.base_spectrogram,
                self.spectrogram_bounds,
            ) = generate_spectrogram_pixmap(
                self.current_audio_data, self.current_samplerate
            )
            self.update_spectrogram()
            self.stop_playback()
            self.status_label.setText(f"Loaded: {os.path.basename(audio_path)}")
            self.check_if_labeled(audio_path)
        except Exception as e:
            self.status_label.setText(
                f"Error loading {os.path.basename(audio_path)}: {e}"
            )
            self.current_audio_data = None
            self.current_samplerate = None
            self.base_spectrogram = None

    def load_next_audio(self):
        self.load_audio(self.current_audio_index + 1)

    def load_previous_audio(self):
        self.load_audio(self.current_audio_index - 1)

    def update_spectrogram(self):
        if self.current_audio_data is None:
            self.spectrogram_label.setText("No audio data to display spectrogram.")
            return

        if self.base_spectrogram is None:
            (
                self.base_spectrogram,
                self.spectrogram_bounds,
            ) = generate_spectrogram_pixmap(
                self.current_audio_data, self.current_samplerate
            )

        pixmap = draw_annotations(
            self.base_spectrogram,
            self.annotations,
            len(self.current_audio_data),
            self.current_samplerate,
            self.spectrogram_bounds,
        )
        pixmap = draw_playback_line(
            pixmap,
            self.playback_position,
            len(self.current_audio_data),
            self.spectrogram_bounds,
        )
        self.spectrogram_label.setPixmap(pixmap)

    def toggle_playback(self):
        if self.current_audio_data is None:
            return

        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        if self.current_audio_data is None:
            return

        self.play_pause_button.setText(
            f"Pause ({self.shortcuts.get('play_pause', '')})"
        )
        self.play_pause_button.setIcon(QIcon(os.path.join(self.icons_path, "pause.svg")))
        self.is_playing = True

        # Ensure playback starts from current position
        start_frame = self.playback_position
        remaining_frames = len(self.current_audio_data) - start_frame

        if remaining_frames <= 0:
            self.playback_position = 0
            start_frame = 0
            remaining_frames = len(self.current_audio_data)

        self.playback_stream_id += 1
        current_id = self.playback_stream_id
        self.playback_stream = sd.OutputStream(
            samplerate=self.current_samplerate,
            channels=1,
            callback=self.audio_callback,
            finished_callback=lambda: self.playback_finished(current_id),
        )
        self.playback_stream.start()

    def stop_playback(self, reset_position: bool = False):
        if self.playback_stream:
            # Increment the stream id so any pending finished callbacks are ignored
            self.playback_stream_id += 1
            stream = self.playback_stream
            self.playback_stream = None
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass
        self.play_pause_button.setText(
            f"Play ({self.shortcuts.get('play_pause', '')})"
        )
        self.play_pause_button.setIcon(QIcon(os.path.join(self.icons_path, "play.svg")))
        self.is_playing = False
        if reset_position:
            self.playback_position = 0
            self.position_slider.setValue(0)
            self.update_playback_line()

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)

        chunk_end = self.playback_position + frames
        if chunk_end > len(self.current_audio_data):
            # Pad with zeros if we're at the end of the audio
            frames_to_copy = len(self.current_audio_data) - self.playback_position
            outdata[:frames_to_copy, 0] = self.current_audio_data[
                self.playback_position : chunk_end
            ]
            outdata[frames_to_copy:, 0] = 0.0
            raise sd.CallbackStop  # Stop playback
        else:
            outdata[:, 0] = self.current_audio_data[self.playback_position : chunk_end]

        self.playback_position += frames
        self.position_slider.setValue(self.playback_position)

    def playback_finished(self, finished_id):
        if finished_id != self.playback_stream_id:
            return
        if not self.is_playing:
            return
        self.stop_playback(reset_position=True)

    def set_playback_position(self, value):
        self.playback_position = value
        if self.is_playing:
            self.stop_playback()
            self.start_playback()
        self.update_playback_line()

    def update_playback_line(self):
        if self.current_audio_data is None:
            return

        if self.base_spectrogram is None:
            (
                self.base_spectrogram,
                self.spectrogram_bounds,
            ) = generate_spectrogram_pixmap(
                self.current_audio_data, self.current_samplerate
            )

        pixmap = draw_annotations(
            self.base_spectrogram,
            self.annotations,
            len(self.current_audio_data),
            self.current_samplerate,
            self.spectrogram_bounds,
        )
        pixmap = draw_playback_line(
            pixmap,
            self.playback_position,
            len(self.current_audio_data),
            self.spectrogram_bounds,
        )
        self.spectrogram_label.setPixmap(pixmap)

    def mark_start(self):
        if self.current_audio_data is None:
            return
        self.temp_start_time = self.playback_position / self.current_samplerate
        self.status_label.setText(f"Start marked at {self.temp_start_time:.2f}s")

    def mark_end(self):
        if self.current_audio_data is None or self.temp_start_time is None:
            return
        end_time = self.playback_position / self.current_samplerate
        start = min(self.temp_start_time, end_time)
        end = max(self.temp_start_time, end_time)
        if end - start > 0.1:
            category = self.category_selector.currentText()
            self.annotations.append((start, end, category))
            self.status_label.setText(
                f"Segment {start:.2f}s to {end:.2f}s added."
            )
            self.update_spectrogram()
        self.temp_start_time = None

    def save_labels_and_cut(self):
        if not self.annotations:
            self.status_label.setText("No annotations to save.")
            return

        current_audio_filename = os.path.basename(
            self.audio_files[self.current_audio_index]
        )
        base_name, _ = os.path.splitext(current_audio_filename)
        output_dir = os.path.join(
            os.path.dirname(self.audio_files[self.current_audio_index]), "labeled_cuts"
        )
        create_directory_if_not_exists(output_dir)

        for i, (start_time, end_time, category) in enumerate(self.annotations):
            category_dir = os.path.join(output_dir, category)
            create_directory_if_not_exists(category_dir)

            output_path = os.path.join(
                category_dir, f"{base_name}_cut_{i}_{category}.wav"
            )
            cut_audio_segment(
                self.current_audio_data,
                self.current_samplerate,
                start_time,
                end_time,
                output_path,
            )
            self.status_label.setText(f"Saved cut to: {output_path}")

        log_labeled_audio(
            self.audio_files[self.current_audio_index], self.labeled_audios
        )
        self.annotations = []  # Clear annotations after saving
        self.status_label.setText(
            f"Audio '{current_audio_filename}' labeled and cuts saved."
        )
        self.show_popup("Cuts saved successfully")

    def check_if_labeled(self, audio_path):
        if audio_path in self.labeled_audios:
            self.status_label.setText(
                f"Loaded: {os.path.basename(audio_path)} (ALREADY LABELED)"
            )
        else:
            self.status_label.setText(f"Loaded: {os.path.basename(audio_path)}")

    def spectrogram_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Placeholder for handling mouse press to start selection
            print(f"Mouse pressed at: {event.position().x()}, {event.position().y()}")
            self.selection_start_x = event.position().x()
            self.selection_start_time = self.x_to_time(event.position().x())

    def spectrogram_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Placeholder for handling mouse release to end selection
            print(f"Mouse released at: {event.position().x()}, {event.position().y()}")
            self.selection_end_x = event.position().x()
            self.selection_end_time = self.x_to_time(event.position().x())

            # Ensure start_time is always less than end_time
            start = min(self.selection_start_time, self.selection_end_time)
            end = max(self.selection_start_time, self.selection_end_time)

            if end - start > 0.1:  # Ensure a minimum selection duration
                category = self.category_selector.currentText()
                self.annotations.append((start, end, category))
                self.status_label.setText(f"Selected: {start:.2f}s to {end:.2f}s")
                self.update_spectrogram()  # Redraw with selection

    def x_to_time(self, x_coordinate):
        # This is a simplified conversion. A more accurate one would depend on
        # the actual width of the spectrogram image and the total duration of the audio.
        # Assuming spectrogram_label width maps to audio duration.
        if self.current_audio_data is None or self.spectrogram_label.pixmap() is None:
            return 0

        if self.spectrogram_bounds is not None:
            left, _, width, _ = self.spectrogram_bounds
            x_coordinate = max(0, x_coordinate - left)
            spectrogram_width = width
        else:
            spectrogram_width = self.spectrogram_label.pixmap().width()

        audio_duration = len(self.current_audio_data) / self.current_samplerate

        if spectrogram_width == 0:
            return 0

        time_per_pixel = audio_duration / spectrogram_width
        return x_coordinate * time_per_pixel

    def show_popup(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Info")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        QTimer.singleShot(1500, msg.close)
        msg.show()

    def closeEvent(self, event):
        if self.playback_stream:
            self.playback_stream.stop()
            self.playback_stream.close()
        event.accept()
