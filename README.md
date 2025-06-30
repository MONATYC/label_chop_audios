# Audio Labeling Tool

This project provides a simple GUI for labeling and cutting audio files into categorized segments. It was built with **PyQt6** and uses `librosa` and `matplotlib` to display spectrograms while playing back audio.

## Requirements

- Python 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [librosa](https://pypi.org/project/librosa/)
- [sounddevice](https://pypi.org/project/sounddevice/)
- [soundfile](https://pypi.org/project/soundfile/)
- [numpy](https://pypi.org/project/numpy/)
- [matplotlib](https://pypi.org/project/matplotlib/)

Install everything into a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install PyQt6 librosa sounddevice soundfile numpy matplotlib
```

## Running the application

Execute the main script from the repository root:

```bash
python audio_labeling_project/main.py
```

When launched, you can open a folder containing `.wav` or `.mp3` files, navigate between them and mark regions on the spectrogram in **Label Mode**. Press **Save Labels & Cut** to store each labeled region as an individual audio file inside `labeled_cuts/`.

The playback section includes **Play/Pause** and **Stop** buttons. *Play/Pause* halts the audio at the current position so you can resume from the same spot, while *Stop* resets the playback position to the beginning of the file.

When labeling, choose a category for the current segment using the drop-down menu next to the **Label Mode** controls. Selected segments will be saved under that category when you press **Save Labels & Cut**.

