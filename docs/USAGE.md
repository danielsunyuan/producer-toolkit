# Usage Guide

This document provides detailed instructions for using Producer Toolkit.

## Basic Commands

### Download Audio

Download the audio track from a YouTube video:

```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -a
```

### Download Video

Download the video from YouTube:

```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -v
```

### Extract Stems

Download the audio and extract stems (vocals, drums, bass, other):

```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s
```

### Specify Output Directory

You can specify a custom output directory:

```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s -o ~/Desktop
```

### Choosing Stem Count

You can specify the number of stems to extract (2, 4, or 5):

```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s -n 4
```

- `-n 2`: Vocals and accompaniment
- `-n 4`: Vocals, drums, bass, and other
- `-n 5`: Vocals, drums, bass, piano, and other

## Windows Usage

On Windows, you can use the provided batch file:

```
run_producer_toolkit.bat "https://www.youtube.com/watch?v=YOUTUBE_ID" -s
```

## Output Files

The audio stems will be saved in a directory named after the video title:

- **vocals.wav** - Contains the isolated vocals
- **drums.wav** - Contains the isolated drums
- **bass.wav** - Contains the isolated bass
- **other.wav** - Contains everything else
- **piano.wav** - Contains isolated piano (only with 5-stem model)

For the 2-stem separation, you get:
- **vocals.wav** - Contains the isolated vocals
- **accompaniment.wav** - Contains all instrumental parts

## Advanced Usage

### Processing Local Files

You can also process local audio files by modifying the spleeter_processor.py script directly:

```python
from tools.processor.spleeter_processor import extract_stems

# Process a local audio file
extract_stems("path/to/your/audio.wav", "output_directory", stem_number=4)
```