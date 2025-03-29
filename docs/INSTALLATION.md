# Installation Guide

This document provides detailed instructions for installing Producer Toolkit on different platforms.

## System Requirements

- Python 3.9+ recommended
- FFmpeg installed on your system
- At least 1GB free disk space (for model storage)

## Installation Methods

### Automated Installation (Recommended)

#### On macOS and Linux:

```bash
python install.py
```

The installation script will:
- Check your Python version
- Install FFmpeg if it's not already installed (macOS via Homebrew, Linux via apt)
- Install Python dependencies from requirements.txt
- Make platform-specific adjustments for compatibility

#### On Windows:

```
install.bat
```

This will run the automated installation script which guides you through the FFmpeg installation if necessary.

### Manual Installation

If you prefer to install dependencies manually:

1. Install FFmpeg:
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`
   - **Windows**: Download from https://github.com/BtbN/FFmpeg-Builds/releases and add to PATH

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## First-Time Usage

On first run, Spleeter will download pretrained models (approximately 500MB). These will be stored in the `models` directory for future use.

## Troubleshooting

### Common Issues

#### FFmpeg Not Found

Ensure FFmpeg is installed and available in your system PATH.

#### Python Version Issues

If you encounter errors about Python version compatibility, ensure you're using Python 3.9 or newer.

#### Tensorflow Installation

On macOS with Apple Silicon (M1/M2), you may need to use `tensorflow-macos` instead of regular `tensorflow`. The installation script handles this automatically.