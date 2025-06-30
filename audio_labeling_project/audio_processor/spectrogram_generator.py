import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt6.QtCore import Qt


def generate_spectrogram_pixmap(audio_data, samplerate):
    """Generate a spectrogram QPixmap for the provided audio."""
    if audio_data is None or len(audio_data) == 0:
        return QPixmap()  # Return empty pixmap

    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    librosa.display.specshow(
        librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max),
        sr=samplerate,
        x_axis="time",
        y_axis="log",
        ax=ax,
    )

    ax.set_title("Spectrogram")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    plt.tight_layout()

    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    qimage = QImage(
        buf.tobytes(), buf.shape[1], buf.shape[0], QImage.Format.Format_RGBA8888
    )
    pixmap = QPixmap.fromImage(qimage)
    plt.close(fig)
    return pixmap


def draw_playback_line(pixmap, playback_position, total_frames):
    """Return a copy of *pixmap* with a red playback line drawn on it."""
    if pixmap.isNull() or total_frames == 0:
        return pixmap

    pixmap_with_line = QPixmap(pixmap)
    painter = QPainter(pixmap_with_line)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(Qt.GlobalColor.red)
    pen.setWidth(2)
    painter.setPen(pen)
    x = int((playback_position / total_frames) * pixmap.width())
    painter.drawLine(x, 0, x, pixmap.height())
    painter.end()
    return pixmap_with_line
