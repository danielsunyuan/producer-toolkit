# Producer Toolkit

A command-line toolkit for music producers to download audio/video from YouTube and extract stems using Spleeter.

## Features

- Download audio or video from YouTube links
- Extract stems (vocals, drums, bass, other) from audio files
- Clean output format with organized file structure
- Local model storage for faster processing
- Cross-platform support (macOS, Linux, Windows)
- Available as a Python package with global `pt` command

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

3. Use the `pt` command from anywhere:
```bash
pt --help
```

#### Option 2: Traditional Installation

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

#### Using the `pt` command (if installed as package):
```bash
# Extract stems (vocals, drums, bass, other)
pt "https://www.youtube.com/watch?v=YOUTUBE_ID" -s

# Download audio only
pt "https://www.youtube.com/watch?v=YOUTUBE_ID" -a

# Download video
pt "https://www.youtube.com/watch?v=YOUTUBE_ID" -v

# Extract 4 stems
pt "https://www.youtube.com/watch?v=YOUTUBE_ID" -s -n 4
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
├── producer_toolkit/     # Main Python package
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # Command-line interface
│   ├── downloader/      # YouTube downloading tools
│   └── processor/       # Audio processing tools
├── main.py               # Legacy CLI entry point
├── install.py            # Cross-platform installation script
├── setup.py              # Python package configuration
├── pyproject.toml        # Modern Python packaging
├── models/               # Where stem separation models are stored
├── requirements.txt      # Python dependencies
├── scripts/              # Helper scripts
│   └── windows/          # Windows-specific scripts
├── tests/                # Test suite
└── tools/                # Legacy tools directory (deprecated)
```

## Development

### Running Tests

```bash
# Run offline tests
python -m tests.run_tests --offline

# Run all tests
python -m tests.run_tests --all

# Run local tests with YouTube download
python -m tests.run_tests --local
```

### Package Development

```bash
# Install in development mode
pip install -e .

# Test the package
pt --help
```

## First-Time Use

On first run, Spleeter will download pretrained models (approximately 500MB). These will be stored in the `models` directory for future use.

## License

[MIT License](LICENSE)