# Aubio Integration Features

The Producer Toolkit now includes advanced audio analysis capabilities using [aubio](https://aubio.org/), an open-source audio processing library. This document describes the new musical analysis features.

## Overview

Aubio integration adds automatic BPM (beats per minute) and key detection to the Producer Toolkit. When enabled, all downloaded audio files and separated stems will include musical information in their filenames, making it easier to organize and identify your music files.

## Features

### BPM Detection
- Automatically detects the tempo of audio files
- Uses aubio's robust beat tracking algorithms
- Results are included in filenames (e.g., `song_128bpm_Am.wav`)
- Handles complex rhythms and tempo changes

### Key Detection  
- Identifies the musical key of audio files
- Supports both major and minor keys (e.g., "C", "Am", "F#", "Bbm")
- Uses pitch detection and harmonic analysis
- Results are included in filenames alongside BPM

### Enhanced File Naming
The new naming convention includes musical features:
```
original_title_[BPM]bpm_[KEY].[extension]
```

Examples:
- `My_Song_125bpm_Am.wav`
- `vocals_140bpm_C#.wav`
- `drums_98.5bpm_Dm.wav`

## Usage

### CLI Usage

Musical analysis is enabled by default. Use `--no-analysis` to disable:

```bash
# With analysis (default)
pt "https://youtube.com/watch?v=VIDEO_ID" -s

# Without analysis (faster)
pt "https://youtube.com/watch?v=VIDEO_ID" -s --no-analysis
```

### Python API Usage

```python
from producer_toolkit.analyzer.audio_analyzer import analyze_audio
from producer_toolkit.downloader.download import download_audio
from producer_toolkit.processor.spleeter_processor import extract_stems

# Analyze an existing audio file
bpm, key = analyze_audio("my_song.wav")
print(f"BPM: {bpm}, Key: {key}")

# Download with analysis
audio_file = download_audio("youtube_url", analyze_features=True)

# Extract stems with analysis
extract_stems("audio.wav", "output_dir", analyze_features=True)
```

### Direct Audio Analysis

```python
from producer_toolkit.analyzer.audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer(sample_rate=44100)

# Detect BPM only
bpm = analyzer.detect_bpm("song.wav")

# Detect key only  
key = analyzer.detect_key("song.wav")

# Analyze both
bmp, key = analyzer.analyze("song.wav")
```

## Installation Requirements

### System Dependencies

The aubio integration requires system-level aubio installation:

#### Ubuntu/Debian
```bash
sudo apt-get install libaubio-dev libaubio5 aubio-tools
```

#### macOS (with Homebrew)
```bash
brew install aubio
```

#### Windows
On Windows, aubio will be installed via pip, but may require additional setup.

### Python Dependencies
Aubio is automatically installed as part of the requirements:
```bash
pip install aubio>=0.4.9
```

## Performance Considerations

- Musical analysis adds processing time (typically 10-30% of audio duration)
- BPM detection is generally faster than key detection
- For batch processing, consider using `--no-analysis` flag
- Analysis results are cached to avoid reprocessing

## Accuracy and Limitations

### BPM Detection
- **High accuracy** for music with clear, steady beats
- **Good performance** with electronic, pop, rock genres  
- **Challenging cases**: music with tempo changes, complex rhythms, or ambient/atmospheric content
- **Fallback**: Returns 120.0 BPM if detection fails

### Key Detection
- **Good accuracy** for music with clear harmonic content
- **Best performance** with traditional Western music
- **Challenging cases**: atonal music, heavily distorted audio, or music with frequent key changes
- **Fallback**: Returns "C" if detection fails

### Supported Audio Formats
- WAV (recommended for best accuracy)
- MP3, FLAC, OGG (converted internally)
- Mono and stereo files supported

## Configuration

### AudioAnalyzer Parameters

```python
analyzer = AudioAnalyzer(
    sample_rate=44100,  # Target sample rate for analysis
    hop_size=512        # Analysis window hop size
)
```

### Analysis Settings
- **Sample Rate**: 44.1kHz recommended for music
- **Window Size**: 1024 samples (fixed)
- **Hop Size**: 512 samples (configurable)

## Error Handling

The system gracefully handles analysis errors:

1. **File not found**: Raises `FileNotFoundError`
2. **Corrupted audio**: Falls back to default values
3. **Analysis timeout**: Returns default values after timeout
4. **Memory errors**: Falls back to simpler analysis methods

## Examples

### Complete Workflow

```python
from producer_toolkit.cli import main
import sys

# Download and analyze with stems
sys.argv = ['pt', 'https://youtube.com/watch?v=VIDEO_ID', '-s', '-n', '4']
main()

# Expected output files:
# video_title_128bpm_Am_stems/
#   ├── vocals_128bpm_Am.wav
#   ├── drums_128bmp_Am.wav
#   ├── bass_128bpm_Am.wav
#   └── other_128bpm_Am.wav
```

### Batch Processing

```python
import os
from producer_toolkit.analyzer.audio_analyzer import analyze_audio

audio_files = ['song1.wav', 'song2.wav', 'song3.wav']
results = {}

for audio_file in audio_files:
    if os.path.exists(audio_file):
        bpm, key = analyze_audio(audio_file)
        results[audio_file] = {'bpm': bpm, 'key': key}
        print(f"{audio_file}: {bpm} BPM, {key}")
```

## Troubleshooting

### Common Issues

1. **"aubio not found" error**
   - Install system aubio: `sudo apt install libaubio-dev` (Ubuntu)
   - Install via Homebrew: `brew install aubio` (macOS)

2. **Slow analysis performance**
   - Use `--no-analysis` flag for faster processing
   - Reduce audio quality/sample rate if needed
   - Consider batch processing during off-peak hours

3. **Inaccurate BPM/key detection**
   - Ensure audio quality is good (not heavily compressed)
   - Try with different sections of the audio
   - Some music genres are inherently challenging

4. **Import errors**
   - Verify aubio installation: `python -c "import aubio; print('OK')"`
   - Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Getting Help

For issues specific to aubio integration:
1. Check the [aubio documentation](https://aubio.org/documentation/)
2. Ensure system dependencies are installed
3. Test with known audio files first
4. Consider disabling analysis if having persistent issues

## Technical Details

### Algorithms Used

- **BPM Detection**: Uses aubio's `tempo` object with beat tracking
- **Key Detection**: Combines `pitch` detection with harmonic analysis
- **Preprocessing**: Automatic resampling and mono conversion

### Dependencies
- `aubio>=0.4.9`: Core audio analysis
- `soundfile`: Audio file I/O
- `numpy`: Numerical computations  
- `librosa`: Audio processing utilities (for resampling)

This integration brings professional-grade audio analysis to your music production workflow, making file organization and music library management much easier.
