import soundfile as sf
import os


def cut_audio_segment(audio_data, samplerate, start_time, end_time, output_path):
    """
    Cuts a segment from audio data and saves it to a file.

    Args:
        audio_data (np.ndarray): The full audio data.
        samplerate (int): The sample rate of the audio.
        start_time (float): Start time of the segment in seconds.
        end_time (float): End time of the segment in seconds.
        output_path (str): Path to save the cut audio file.
    """
    start_frame = int(start_time * samplerate)
    end_frame = int(end_time * samplerate)

    cut_audio = audio_data[start_frame:end_frame]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, cut_audio, samplerate)
