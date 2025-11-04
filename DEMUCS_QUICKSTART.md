# Demucs Quick Start Guide

## Installation

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

## Basic Usage

```bash
# Extract 4 stems (vocals, drums, bass, other) - DEFAULT
pt "YOUTUBE_URL" -s

# Extract 2 stems (vocals, no_vocals/accompaniment)
pt "YOUTUBE_URL" -s -n 2

# Download audio only with BPM/key analysis
pt "YOUTUBE_URL" -a

# Disable BPM/key analysis for faster processing
pt "YOUTUBE_URL" -s --no-analysis
```

## Testing with Local Files

```bash
# Test with the example file
pt --test --test-file "/Users/duan/Code/projects/project.producerTK/prodTK/demucs/example.wav" -s -o ~/Downloads
```

## Key Features

✅ **State-of-the-art quality** - Hybrid Transformer Demucs (htdemucs)  
✅ **4 stem separation** - vocals, drums, bass, other  
✅ **BPM & key detection** - Automatic musical analysis with aubio  
✅ **Enhanced filenames** - e.g., `vocals_128bpm_Am.wav`  
✅ **2 stem mode** - Quick vocal extraction with accompaniment mix

## Output Structure

### 4 Stems Mode (Default)
```
song_title_stems/
├── vocals_128bpm_C.wav
├── drums_128bpm_C.wav
├── bass_128bpm_C.wav
└── other_128bpm_C.wav
```

### 2 Stems Mode
```
song_title_stems/
├── vocals_128bpm_C.wav
└── no_vocals_128bpm_C.wav  (mixed from drums + bass + other)
```

## Performance Notes

- **First run**: Downloads ~2GB htdemucs model (one-time)
- **Processing speed**: ~2-3 minutes per song on M1 Mac
- **GPU acceleration**: Automatic if PyTorch detects CUDA
- **Memory usage**: ~4-8GB RAM recommended

## Comparison with Spleeter

| Feature | Spleeter | Demucs |
|---------|----------|---------|
| Quality | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| Speed | Fast | Moderate |
| Bass Sep. | Good | Excellent |
| Drum Sep. | Good | Excellent |
| Model Size | 500MB | 2GB |
| Active Dev | ❌ No | ✅ Yes |

## Troubleshooting

### FFmpeg Error
```bash
# Install FFmpeg
conda install -c conda-forge ffmpeg -y
```

### Model Download Fails
```bash
# Clear cache and retry
rm -rf ~/.cache/torch/hub/checkpoints/
```

### Memory Issues
- Close other applications
- Use 2 stem mode instead of 4
- Use `--no-analysis` flag

## Branch Info

- **Branch**: `feature/demucs-integration`
- **Status**: Ready for testing
- **Merge to main**: After validation

## What Changed?

1. ✅ Replaced Spleeter with Demucs
2. ✅ Updated dependencies (PyTorch instead of TensorFlow)
3. ✅ Changed default from 2 to 4 stems
4. ✅ Added migration documentation
5. ✅ Maintained backward compatibility in imports
6. ✅ Updated README and all documentation

See `DEMUCS_MIGRATION.md` for complete migration details.

