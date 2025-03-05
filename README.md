# Producer Toolkit

A command-line toolkit for music producers to download audio/video from YouTube and extract stems using Spleeter.

## Features

- Download audio or video from YouTube links
- Extract stems (vocals, drums, bass, other) from audio files
- Clean output format with organized file structure
- Local model storage for faster processing

## Installation

### Requirements

- Python 3.9+ recommended
- ffmpeg installed on your system

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/producer-toolkit.git
cd producer-toolkit
```

2. Create a conda environment (recommended):
```bash
conda create -n producer python=3.9
conda activate producer
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

Download audio:
```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -a
```

Download video:
```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -v
```

Extract stems:
```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s
```

Specify output directory:
```bash
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s -o ~/Desktop
```

### Output

The audio stems will be saved in a directory named after the video title:
- vocals.wav - Contains the isolated vocals
- drums.wav - Contains the isolated drums
- bass.wav - Contains the isolated bass
- other.wav - Contains everything else

## First-Time Use

On first run, Spleeter will download pretrained models (approximately 500MB). These will be stored in the `models` directory for future use.

## License

[MIT License](LICENSE)