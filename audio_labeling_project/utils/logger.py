import json
import os
from config import CONFIG


def load_labels_data():
    """Load stored label details for audios."""
    path = CONFIG.get("LABELS_FILE", "memlog/labels.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return {}


def save_labels_for_audio(audio_path, annotations, labels_data, cut_files=None):
    """Save annotation list for an audio file and track generated cuts."""
    entry = labels_data.get(audio_path, {})
    if isinstance(entry, list):
        entry = {"annotations": entry}
    if not isinstance(entry, dict):
        entry = {}
    entry["annotations"] = annotations
    if cut_files is not None:
        entry["cuts"] = cut_files
    labels_data[audio_path] = entry
    path = CONFIG.get("LABELS_FILE", "memlog/labels.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(labels_data, f, indent=4)


def remove_labels_for_audio(audio_path, labels_data):
    """Remove saved annotations and associated cuts for an audio file."""
    entry = labels_data.get(audio_path)
    if entry is None:
        return False

    if isinstance(entry, dict):
        for cut_path in entry.get("cuts", []):
            try:
                if os.path.exists(cut_path):
                    os.remove(cut_path)
            except OSError:
                pass

    del labels_data[audio_path]
    path = CONFIG.get("LABELS_FILE", "memlog/labels.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(labels_data, f, indent=4)
    return True


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


def remove_labeled_audio(audio_path, labeled_audios_dict, labels_data=None):
    """Remove an entry from the labeled audios log and stored labels."""
    removed = False
    if audio_path in labeled_audios_dict:
        del labeled_audios_dict[audio_path]
        log_path = CONFIG["LOG_FILE"]
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(labeled_audios_dict, f, indent=4)
        removed = True

    if labels_data is not None:
        removed |= remove_labels_for_audio(audio_path, labels_data)

    return removed
