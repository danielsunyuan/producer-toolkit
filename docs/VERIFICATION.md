# Verification — 14 November 2026

## Clean installed package

Created a Python 3.11 virtual environment without inherited site packages and installed PTK with `python -m pip install .`. Tests imported the installed package from site-packages, independently of the source checkout.

- 34 offline workflow/analyzer tests passed (67.651 seconds).
- Real htdemucs CPU processing of a one-second generated stereo fixture produced four stems, then a separate two-stem run produced vocals and accompaniment.
- All six WAVs decoded with 44,100 frames, stereo channels and a 44.1 kHz sample rate. The source SHA-256 remained unchanged.
- `ptk --version` returned 1.1.1; `pip check` reported no broken requirements.
- Shell wrapper syntax and version checks passed; `git diff --check` passed.

Resolved clean-environment versions included Demucs 4.1.0, PyTorch 2.15.0, torchaudio 2.11.1, torchcodec 0.17.0, yt-dlp 2026.10.26, EJS 0.8.0, librosa 0.11.0 and SoundFile 0.12.1 on Apple Silicon macOS. Model assets were fetched or reused through the model backend's cache.

The pre-existing macOS environment also passed the same 34 tests, using Demucs 4.0.1 and PyTorch/torchaudio 2.9.0.

## Limits

This validates installation and pipeline execution, not musical separation quality. No new live-site download, full-length music benchmark, accelerator run, Windows run or Ableton import test was performed in this verification. GitHub CI results should be checked separately; local checks do not establish remote CI success.
