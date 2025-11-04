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

