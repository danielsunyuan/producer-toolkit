# Producer Toolkit

A command-line toolkit for music producers to download audio/video from YouTube and extract stems using Demucs (default) or Spleeter.

## Features

- Download audio or video from YouTube links
- Extract stems (vocals, drums, bass, other) from audio files
- Automatic BPM and key detection using librosa
- Enhanced file naming with musical features (e.g., `song_128bpm_Am.wav`)
- Musical analysis for both main files and individual stems
- Clean output format with organized file structure
- Local model storage for faster processing
- Cross-platform support (macOS, Linux, Windows)
- Available as a Python package with global `ptk` command

## Quick Start

### Installation

#### Option 1: Install as Python Package (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/producer-toolkit.git
cd producer-toolkit
```

2. Install the package:
```bash
# Install in development mode (recommended for development)
pip install -e .

# Or install globally (available system-wide)
pip install -e .
```

3. Use the `ptk` command from anywhere:
```bash
ptk --help
```

### Basic Usage

#### Using the `ptk` command (if installed as package):
```bash
# Extract stems with BPM and key analysis (default)
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -s

# Download audio only (no BPM/key analysis)
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -a

# Download video
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -v

# Extract 4 stems with musical analysis (default: Demucs)
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -s

# Extract 2 stems (vocals and accompaniment)
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -s -n 2

# Use Spleeter engine (optional, requires separate installation)
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -s --engine spleeter

# Disable BPM/key analysis for faster processing
ptk "https://www.youtube.com/watch?v=YOUTUBE_ID" -s --no-analysis

# Example output filenames:
# song_title_125bpm_Am.wav (main audio when -a used)
# vocals_125bpm_Am.wav (vocal stem)
# drums_125bpm_Am.wav (drum stem)
```

#### Using the traditional method:
```bash
# Extract stems (vocals, drums, bass, other)
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s

# Download audio only
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -a

# Download video
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -v
```

## Installation

See the [INSTALL.md](INSTALL.md) file for detailed installation instructions.

## Project Structure

```
.
├── producer_toolkit/     # Main Python package
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # Command-line interface
│   ├── downloader/      # YouTube downloading tools
│   └── processor/       # Audio processing tools
│       └── utils/       # Utility functions
├── main.py               # Legacy CLI entry point
├── setup.py              # Python package configuration
├── pyproject.toml        # Modern Python packaging
├── requirements.txt      # Python dependencies
├── INSTALL.md            # Installation guide
├── scripts/              # Helper scripts
│   └── windows/          # Windows-specific scripts
└── tests/                # Test suite
```

## Development

### Running Tests

```bash
# Run all unit tests
python -m tests.run_tests
```

### Package Development

```bash
# Install in development mode
pip install -e .

# Test the package
pt --help
```

## Musical Analysis

The toolkit includes automatic BPM (beats per minute) and key detection using [librosa](https://librosa.org/), a powerful audio analysis library. This feature:

- Analyzes audio files to detect tempo and musical key
- Automatically includes this information in filenames
- Works for both main downloads and individual stems (stems only)
- Can be disabled with `--no-analysis` for faster processing

### Example Output

With musical analysis enabled (default):
```
song_title_128bmp_C.wav           # Main audio file
vocals_128bpm_C.wav               # Vocal stem
drums_128bpm_C.wav                # Drum stem  
bass_128bpm_C.wav                 # Bass stem
other_128bpm_C.wav                # Other instruments stem
```

## First-Time Use

On first run:
1. Demucs will download pretrained models (approximately 2GB for htdemucs model). These will be stored in your home directory under `~/.cache/torch/hub/checkpoints/` by default.
2. Librosa will be used for audio analysis (included with the package).
3. FFmpeg is required for Demucs to work properly - install via conda or system package manager.

## License

[MIT License](LICENSE)