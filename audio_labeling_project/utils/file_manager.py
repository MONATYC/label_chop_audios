import os


def get_audio_files_in_folder(folder_path, extensions):
    """
    Retrieves a list of audio files with specified extensions from a folder.

    Args:
        folder_path (str): The path to the folder.
        extensions (list): A list of allowed audio file extensions (e.g., ['.wav', '.mp3']).

    Returns:
        list: A list of full paths to the audio files.
    """
    audio_files = []
    if os.path.isdir(folder_path):
        for f in os.listdir(folder_path):
            if any(f.lower().endswith(ext) for ext in extensions):
                audio_files.append(os.path.join(folder_path, f))
    return audio_files


def create_directory_if_not_exists(path):
    """
    Creates a directory if it does not already exist.

    Args:
        path (str): The path of the directory to create.
    """
    os.makedirs(path, exist_ok=True)
