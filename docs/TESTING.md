# Testing Guide

## Quick Test

Run all unit tests:

```bash
conda activate ptk
python -m tests.run_tests
```

Or use unittest directly:

```bash
conda activate ptk
python -m unittest discover tests/ -v
```

## Test Structure

The test suite is located in the `tests/` directory:

```
tests/
├── __init__.py
├── run_tests.py          # Simple test runner
├── test_audio_analyzer.py # Audio analysis tests
├── test_integration.py    # Integration tests (download, stem extraction)
└── resources/
    ├── sample.wav        # Test audio file
    └── Yee.wav           # Demo audio file for integration tests
```

## Running Specific Tests

### Run a specific test file:

```bash
python -m unittest tests.test_audio_analyzer -v
```

### Run a specific test class:

```bash
python -m unittest tests.test_audio_analyzer.TestAudioAnalyzer -v
```

### Run a specific test method:

```bash
python -m unittest tests.test_audio_analyzer.TestAudioAnalyzer.test_detect_bpm_with_valid_audio -v
```

### Run integration tests:

```bash
# Test local file stem extraction (4-stem and 2-stem)
python -m unittest tests.test_integration.TestLocalAudioFile -v

# Test YouTube download (requires internet, can be skipped with SKIP_YOUTUBE_TESTS=true)
python -m unittest tests.test_integration.TestYouTubeDownload -v

# Test full pipeline (download → extract stems)
python -m unittest tests.test_integration.TestFullPipeline -v

# Skip YouTube tests if you don't want to download from internet
SKIP_YOUTUBE_TESTS=true python -m unittest tests.test_integration -v
```

## Manual Testing

### Test the CLI command:

```bash
# Test help
ptk --help

# Test audio download (no BPM/key analysis)
ptk "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a

# Test stem extraction (with BPM/key analysis)
ptk "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s

# Test with different options
ptk "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s -n 2 --engine demucs
```

### Test individual components:

```python
# Test audio analyzer
python -c "
from producer_toolkit.analyzer.audio_analyzer import analyze_audio
bpm, key = analyze_audio('tests/resources/sample.wav')
print(f'BPM: {bpm}, Key: {key}')
"
```

## What's Tested

The test suite covers:

### Unit Tests (`test_audio_analyzer.py`):
- ✅ AudioAnalyzer initialization
- ✅ BPM detection with valid audio files
- ✅ Key detection with valid audio files
- ✅ Error handling (non-existent files, corrupted files)
- ✅ Filename generation with features
- ✅ Convenience functions

### Integration Tests (`test_integration.py`):
- ✅ YouTube audio download (optional, requires internet)
- ✅ 4-stem extraction (vocals, drums, bass, other) with BPM/key analysis
- ✅ 2-stem extraction (vocals, no_vocals) with BPM/key analysis
- ✅ Full pipeline: download → analyze → extract stems
- ✅ Local file processing using `tests/resources/Yee.wav`

## Troubleshooting

### Tests fail with import errors:

```bash
# Make sure package is installed
pip install -e .
```

### Tests fail with librosa warnings:

These are expected warnings from librosa and can be ignored. The tests should still pass.

### Tests timeout:

Some tests may take longer if librosa needs to process audio. This is normal for audio analysis tests.

### Integration tests require internet:

The YouTube download tests require internet access. You can skip them by setting:
```bash
SKIP_YOUTUBE_TESTS=true python -m unittest tests.test_integration -v
```

### Demo file for integration tests:

The `tests/resources/Yee.wav` file is used for testing stem extraction. It's a 2.3MB demo file downloaded from YouTube that can be used to test:
- 4-stem extraction (vocals, drums, bass, other)
- 2-stem extraction (vocals, no_vocals)
- BPM and key detection

This file is kept in the repository for testing purposes but can be re-downloaded if needed:
```bash
ptk "https://www.youtube.com/watch?v=q6EoRBvdVPQ&pp=ygUDeWVl" -a
```

