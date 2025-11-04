# Installation Guide

## Quick Install (Conda - Recommended)

```bash
# Navigate to the project
cd /Users/duan/Code/projects/project.producerTK/producer-toolkit

# Create conda environment
conda create -n producer-toolkit python=3.11 -y
conda activate producer-toolkit

# Install FFmpeg (REQUIRED for Demucs)
conda install -c conda-forge ffmpeg -y

# Install the package
pip install -e .
```

## Full Installation with Both Engines

### Option 1: Demucs Only (Default - Recommended)

```bash
# Create conda environment
conda create -n producer-toolkit python=3.11 -y
conda activate producer-toolkit

# Install FFmpeg
conda install -c conda-forge ffmpeg -y

# Install the package (includes Demucs)
pip install -e .
```

### Option 2: Both Demucs and Spleeter

```bash
# Create conda environment
conda create -n producer-toolkit python=3.11 -y
conda activate producer-toolkit

# Install FFmpeg
conda install -c conda-forge ffmpeg -y

# Install the package
pip install -e .

# Install Spleeter (optional - for faster processing)
pip install spleeter tensorflow
```

## Using the Environment

```bash
# Activate the environment
conda activate producer-toolkit

# Use the tool
pt "YOUTUBE_URL" -s
```

## Required Dependencies

### FFmpeg (REQUIRED)
```bash
conda install -c conda-forge ffmpeg -y
```

### Aubio (REQUIRED for BPM/Key Detection)
Aubio is required for accurate BPM and key detection. The toolkit does not use fallbacks.

**Installation Order:**
1. Install numpy first (required for aubio compilation):
   ```bash
   pip install numpy
   ```

2. Then install aubio:
   ```bash
   pip install aubio
   ```

**If pip install fails:**
- **macOS (Recommended)**: Use Homebrew which includes Python bindings:
  ```bash
  brew install aubio
  ```
- **Linux**: Use system package manager:
  ```bash
  sudo apt-get install aubio-tools python3-aubio
  ```

## Troubleshooting

### FFmpeg Missing
```bash
conda install -c conda-forge ffmpeg -y
```

### Spleeter Not Found
```bash
pip install spleeter tensorflow
```

### Demucs Model Download Issues
```bash
# Clear cache if needed
rm -rf ~/.cache/torch/hub/checkpoints/
```

### Aubio Build Issues
If `pip install aubio` fails due to compilation errors:

1. **macOS**: Use Homebrew (recommended):
   ```bash
   brew install aubio
   ```
   The Homebrew version includes Python bindings and avoids compilation issues.

2. **Ensure numpy is installed first**:
   ```bash
   pip install numpy
   pip install aubio
   ```

3. **Check system dependencies**:
   - macOS: Ensure Xcode Command Line Tools are installed
   - Linux: Install build essentials: `sudo apt-get install build-essential`

**Note**: Aubio is required - there are no fallbacks. The toolkit will fail to start if aubio is not available.
