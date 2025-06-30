import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


def generate_spectrogram_pixmap(audio_data, samplerate, playback_position=None):
    """
    Generates a spectrogram from audio data and returns it as a QPixmap.

    Args:
        audio_data (np.ndarray): The audio data.
        samplerate (int): The sample rate of the audio.
        playback_position (int, optional): Current playback position in frames.
                                           If provided, a vertical line will be drawn.

    Returns:
        QPixmap: The spectrogram as a QPixmap.
    """
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

    if playback_position is not None and samplerate > 0:
        time_position = playback_position / samplerate
        ax.axvline(x=time_position, color="r", linestyle="--", linewidth=2)

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
