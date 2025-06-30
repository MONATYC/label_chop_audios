import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt6.QtCore import Qt


def generate_spectrogram_pixmap(audio_data, samplerate):
    """Generate a spectrogram QPixmap for the provided audio.

    Returns
    -------
    tuple
        QPixmap of the spectrogram and a tuple describing the bounding box
        of the actual plotting area in pixel coordinates `(left, top, width, height)`.
    """
    if audio_data is None or len(audio_data) == 0:
        return QPixmap(), None  # Return empty pixmap

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
    renderer = fig.canvas.get_renderer()
    bbox = ax.get_window_extent(renderer=renderer)
    fig_width, fig_height = fig.canvas.get_width_height()
    left = int(bbox.x0)
    right = int(bbox.x1)
    # Convert from matplotlib's origin (bottom left) to pixmap origin (top left)
    top = int(fig_height - bbox.y1)
    bottom = int(fig_height - bbox.y0)
    bounds = (left, top, right - left, bottom - top)
    qimage = QImage(
        buf.tobytes(), buf.shape[1], buf.shape[0], QImage.Format.Format_RGBA8888
    )
    pixmap = QPixmap.fromImage(qimage)
    plt.close(fig)
    return pixmap, bounds


def draw_playback_line(pixmap, playback_position, total_frames, bounds=None):
    """Return a copy of *pixmap* with a red playback line drawn on it.

    Parameters
    ----------
    pixmap : QPixmap
        Image to draw over.
    playback_position : int
        Current frame index in the audio.
    total_frames : int
        Total number of frames of the audio.
    bounds : tuple, optional
        Bounding box of the spectrogram area as `(left, top, width, height)`.
        If provided, the line will be drawn only within this rectangle.
    """
    if pixmap.isNull() or total_frames == 0:
        return pixmap

    pixmap_with_line = QPixmap(pixmap)
    painter = QPainter(pixmap_with_line)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(Qt.GlobalColor.red)
    pen.setWidth(2)
    painter.setPen(pen)

    if bounds is not None:
        left, top, width, height = bounds
        x = int(left + (playback_position / total_frames) * width)
        painter.drawLine(x, top, x, top + height)
    else:
        x = int((playback_position / total_frames) * pixmap.width())
        painter.drawLine(x, 0, x, pixmap.height())

    painter.end()
    return pixmap_with_line


def draw_annotations(pixmap, annotations, total_frames, samplerate, bounds=None):
    """Draw stored annotation regions onto *pixmap*.

    Parameters
    ----------
    pixmap : QPixmap
        Image to draw over.
    annotations : list
        List of `(start, end, category)` tuples in seconds.
    total_frames : int
        Total number of frames in the audio.
    samplerate : int
        Sample rate of the audio.
    bounds : tuple, optional
        Bounding box of the spectrogram area as `(left, top, width, height)`.
        If provided, the lines will be drawn only within this rectangle.
    """
    if pixmap.isNull() or not annotations:
        return pixmap

    annotated = QPixmap(pixmap)
    painter = QPainter(annotated)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(Qt.GlobalColor.green)
    pen.setWidth(2)
    painter.setPen(pen)

    for start, end, _ in annotations:
        if bounds is not None:
            left, top, width, height = bounds
            start_x = int(left + (start * samplerate / total_frames) * width)
            end_x = int(left + (end * samplerate / total_frames) * width)
            painter.drawLine(start_x, top, start_x, top + height)
            painter.drawLine(end_x, top, end_x, top + height)
        else:
            start_x = int((start * samplerate / total_frames) * pixmap.width())
            end_x = int((end * samplerate / total_frames) * pixmap.width())
            painter.drawLine(start_x, 0, start_x, pixmap.height())
            painter.drawLine(end_x, 0, end_x, pixmap.height())

    painter.end()
    return annotated
