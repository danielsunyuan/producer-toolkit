# Producer Toolkit Tests

This directory contains tests for the Producer Toolkit application.

## Test Directory Structure

- `local/` - Local test scripts for development and testing
  - `test_local.py` - Tests that download from YouTube and perform stem extraction
  - `test_offline.py` - Tests that use pre-downloaded sample files without YouTube access
- `ci/` - Continuous Integration test resources and scripts
  - `resources/` - Test files used in CI workflows
  - `scripts/` - Scripts for CI testing
    - `run_ci_test.py` - Script to run CI tests locally (simulates GitHub Actions workflow)
- `resources/` - Test resources for local testing
  - `sample.wav` - Sample audio file for offline testing
- `output/` - Generated during testing (gitignored)
  - `audio/` - Downloaded audio files
  - `video/` - Downloaded video files
  - `stems/` - Extracted stems

## Running Tests

### Setup

1. Activate the conda environment:
   ```bash
   conda activate producer-toolkit
   ```

2. If you don't have a conda environment yet, create one:
   ```bash
   conda create -n producer-toolkit python=3.9
   conda activate producer-toolkit
   python install.py
   ```

### Run Local Tests

Use the test runner to run all or specific tests:

```bash
# Run offline tests only (no YouTube download)
python -m tests.run_tests --offline

# Run local tests (with YouTube download)
python -m tests.run_tests --local

# Run all tests
python -m tests.run_tests --all

# Run local tests with a specific YouTube URL
python -m tests.run_tests --local "https://www.youtube.com/watch?v=VIDEO_ID"
```

Or run individual test modules directly:

```bash
# Run the offline test
python -m tests.local.test_offline

# Run the local test with YouTube download
python -m tests.local.test_local
```

### Run CI Tests Locally

To run the CI tests that simulate what happens in GitHub Actions:

```bash
# Run CI tests (simulates GitHub Actions workflow)
python -m tests.ci.scripts.run_ci_test
```

This will:
1. Generate test audio and video files
2. Test the audio download functionality
3. Test the video download functionality 
4. Test the stem extraction functionality

The CI tests use the same parameters and mock files that the GitHub Actions workflow uses.

## Adding New Tests

1. Add test files to the appropriate directory (`local/`, etc.)
2. If adding resources, place them in the `resources/` directory
3. Update this README as needed

## Notes for Cross-Platform Testing

- For Windows users, the paths should work correctly with the `Path` object
- The test output is stored in the `tests/output/` directory
- Sample resources are included for offline testing without internet access