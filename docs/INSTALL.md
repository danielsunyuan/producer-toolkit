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

### Librosa (REQUIRED for BPM/Key Detection)
Librosa is used for accurate BPM and key detection. It's actively maintained and works seamlessly with modern NumPy versions.

**Installation:**
Librosa is automatically installed when you run `pip install -e .`. No additional setup is required.

**Features:**
- ✅ Actively maintained and regularly updated
- ✅ Works with modern NumPy versions (no compilation issues)
- ✅ Good accuracy for BPM and key detection
- ✅ Excellent documentation and community support

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

### Librosa Installation Issues
If you encounter issues with librosa:

1. **Ensure all dependencies are installed**:
   ```bash
   pip install numpy scipy scikit-learn numba
   pip install librosa
   ```

2. **On macOS with Apple Silicon**, librosa should work out of the box with conda/pip installations.

3. **Performance Note**: Librosa is slightly slower than aubio but provides excellent accuracy and modern compatibility.
