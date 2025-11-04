# Migration Guide: Spleeter to Demucs

This document outlines the migration from Spleeter to Demucs for stem separation in Producer Toolkit.

## What Changed?

### 1. **Stem Separation Engine**
- **Before**: Spleeter (TensorFlow-based)
- **After**: Demucs (PyTorch-based, specifically htdemucs model)

### 2. **Dependencies**
- **Removed**: 
  - `spleeter==2.3.2`
  - `tensorflow==2.13.0`
  - `norbert==0.2.1`
  
- **Added**:
  - `demucs>=4.0.0`
  - `torch>=2.0.0`
  - `torchaudio>=2.0.0`

### 3. **Default Number of Stems**
- **Before**: 2 stems (vocals, accompaniment)
- **After**: 4 stems (vocals, drums, bass, other)

### 4. **Supported Stem Configurations**
- **Before**: 2, 4, or 5 stems
- **After**: 2 or 4 stems
  - **2 stems**: vocals + no_vocals (accompaniment mix)
  - **4 stems**: vocals, drums, bass, other

### 5. **Model Storage**
- **Before**: Models stored in `models/` directory in project root
- **After**: Models stored in `~/.cache/torch/hub/checkpoints/` by default

### 6. **Model Size**
- **Before**: ~500MB for Spleeter models
- **After**: ~2GB for htdemucs model (first download only)

## Why Demucs?

Demucs offers several advantages:

1. **Better Quality**: Hybrid Transformer Demucs (htdemucs) provides state-of-the-art source separation
2. **Active Development**: Actively maintained by Meta Research (Facebook AI)
3. **Modern Architecture**: Uses hybrid spectrogram-waveform approach with transformers
4. **Better Separation**: Particularly improved drum and bass separation
5. **No TensorFlow**: Lighter dependency stack with PyTorch

## Installation

### Fresh Install

```bash
# Create conda environment (recommended)
conda create -n producer-toolkit python=3.11 -y
conda activate producer-toolkit

# Install FFmpeg (required for Demucs)
conda install -c conda-forge ffmpeg -y

# Install the toolkit
cd producer-toolkit
pip install -e .
```

### Updating Existing Installation

```bash
# Activate your environment
conda activate producer-toolkit  # or source .venv/bin/activate

# Install FFmpeg if not already installed
conda install -c conda-forge ffmpeg -y

# Update dependencies
pip uninstall spleeter tensorflow -y
pip install -r requirements.txt
```

## Usage Changes

### Command Line Interface

**Before (Spleeter)**:
```bash
# Default was 2 stems
pt "YOUTUBE_URL" -s

# 4 stems required explicit flag
pt "YOUTUBE_URL" -s -n 4
```

**After (Demucs)**:
```bash
# Default is now 4 stems
pt "YOUTUBE_URL" -s

# 2 stems (vocals + accompaniment)
pt "YOUTUBE_URL" -s -n 2
```

### API Usage (Python)

**Before**:
```python
from producer_toolkit.processor.spleeter_processor import extract_stems

extract_stems(
    audio_path="song.wav",
    output_dir="output/",
    stem_number=4  # 2, 4, or 5
)
```

**After**:
```python
from producer_toolkit.processor.demucs_processor import extract_stems

extract_stems(
    audio_path="song.wav",
    output_dir="output/",
    stem_number=4  # 2 or 4 only
)
```

## Output Differences

### 2 Stems Mode

**Spleeter**: 
- `vocals.wav`
- `accompaniment.wav`

**Demucs**:
- `vocals.wav`
- `no_vocals.wav` (mixed from drums + bass + other)

### 4 Stems Mode

**Both produce the same**:
- `vocals.wav`
- `drums.wav`
- `bass.wav`
- `other.wav`

## Performance Comparison

| Feature | Spleeter | Demucs (htdemucs) |
|---------|----------|-------------------|
| Speed | Faster (~1-2x realtime) | Slower (~0.3-0.5x realtime) |
| Quality | Good | Excellent |
| GPU Support | Yes (TensorFlow) | Yes (PyTorch) |
| Model Size | ~500MB | ~2GB |
| Bass Separation | Good | Excellent |
| Drum Separation | Good | Excellent |
| Vocal Quality | Good | Excellent |

## Troubleshooting

### FFmpeg Issues

If you get errors about FFmpeg or torchcodec:

```bash
# Install FFmpeg via conda
conda install -c conda-forge ffmpeg -y

# Or on macOS with Homebrew
brew install ffmpeg

# Or on Ubuntu/Debian
sudo apt-get install ffmpeg
```

### Model Download Issues

If model downloads fail:

```bash
# Models are downloaded to ~/.cache/torch/hub/checkpoints/
# Check available space
df -h ~

# Clear cache if needed
rm -rf ~/.cache/torch/hub/checkpoints/
```

### Memory Issues

Demucs requires more memory than Spleeter:

- **Minimum**: 4GB RAM
- **Recommended**: 8GB+ RAM
- **GPU**: Reduces processing time significantly

## Rollback Instructions

If you need to rollback to Spleeter:

```bash
# Switch back to main branch
git checkout main

# Reinstall old dependencies
pip uninstall demucs torch torchaudio -y
pip install spleeter==2.3.2 tensorflow==2.13.0
```

## FAQ

**Q: Why is Demucs slower?**  
A: Demucs uses a more sophisticated model architecture (Hybrid Transformer) which provides better quality but takes longer to process.

**Q: Can I use GPU to speed up processing?**  
A: Yes! If you have a CUDA-compatible GPU, Demucs will automatically use it. Install PyTorch with CUDA support:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Q: What happened to 5 stems mode?**  
A: Demucs htdemucs model produces 4 stems. For piano-specific separation, you'd need to use a different Demucs model variant.

**Q: Are my old Spleeter models still needed?**  
A: No, you can safely remove the `models/` directory from the project root. Demucs stores models in a different location.

## Additional Resources

- [Demucs GitHub](https://github.com/facebookresearch/demucs)
- [Demucs Paper](https://arxiv.org/abs/2111.03600)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)

## Support

If you encounter issues during migration, please:

1. Check the troubleshooting section above
2. Ensure FFmpeg is properly installed
3. Verify Python version is 3.8-3.11
4. Open an issue on GitHub with error details

