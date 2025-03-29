# Producer Toolkit

A command-line toolkit for music producers to download audio/video from YouTube and extract stems using Spleeter.

## Features

- Download audio or video from YouTube links
- Extract stems (vocals, drums, bass, other) from audio files
- Clean output format with organized file structure
- Local model storage for faster processing
- Cross-platform support (macOS, Linux, Windows)

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/producer-toolkit.git
cd producer-toolkit
```

2. Run the installation script:
```bash
# On macOS/Linux
python install.py

# On Windows
scripts\windows\install.bat
```

### Basic Usage

```bash
# Extract stems (vocals, drums, bass, other)
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s

# Download audio only
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -a

# Download video
python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -v
```

Windows users can use the provided batch file:
```
scripts\windows\run_toolkit.bat "https://www.youtube.com/watch?v=YOUTUBE_ID" -s
```

## Documentation

Detailed documentation is available in the `docs` directory:

- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions for all platforms
- [Usage Guide](docs/USAGE.md) - Comprehensive usage instructions and examples

## Project Structure

```
.
├── docs/                 # Documentation
├── main.py               # Main CLI entry point
├── install.py            # Cross-platform installation script
├── models/               # Where stem separation models are stored
├── requirements.txt      # Python dependencies
├── scripts/              # Helper scripts
│   └── windows/          # Windows-specific scripts
└── tools/                # Core functionality
    ├── downloader/       # YouTube downloading tools
    └── processor/        # Audio processing tools
```

## First-Time Use

On first run, Spleeter will download pretrained models (approximately 500MB). These will be stored in the `models` directory for future use.

## License

[MIT License](LICENSE)