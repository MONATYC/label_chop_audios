import json
import os
from config import CONFIG


def load_labeled_audios_log():
    """
    Loads the log of already labeled audio files.

    Returns:
        dict: A dictionary where keys are audio file paths and values are True if labeled.
    """
    log_path = CONFIG["LOG_FILE"]
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return json.load(f)
    else:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        return {}


def log_labeled_audio(audio_path, labeled_audios_dict):
    """
    Logs an audio file as labeled.

    Args:
        audio_path (str): The path of the audio file to log.
        labeled_audios_dict (dict): The dictionary containing labeled audio paths.
    """
    labeled_audios_dict[audio_path] = True
    log_path = CONFIG["LOG_FILE"]
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(labeled_audios_dict, f, indent=4)
