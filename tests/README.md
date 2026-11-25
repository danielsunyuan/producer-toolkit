# Testing Producer Toolkit

Install the package in a Python 3.11 environment with system FFmpeg available.

## Offline regression suite

```sh
python tests/run_offline.py
```

The workflow and analyzer tests exercise file preservation, collisions, single-item URL behavior, partial or mismatched stems, subprocess failures and nullable analysis results. Fixtures are generated in temporary directories. One test uses real yt-dlp/FFmpeg conversion on a local fixture; downloads and model inference are mocked in the remaining workflow tests.

## Manual smoke checks

```sh
ptk --help
ptk --version
ptk doctor
ptk "/path/to/owned-audio.wav" -s --no-analysis -o ./smoke-four
ptk "/path/to/owned-audio.wav" -s -n 2 --no-analysis -o ./smoke-two
```

Real separation requires the pretrained model, downloads it on first use and can take substantially longer than the offline suite. Check the exported files, manifest and source preservation. Use a permitted single-video URL to separately verify live downloading.

The older `test_integration.py` contains network/model tests and is not part of the offline regression command. Unrestricted test discovery can invoke those expensive operations. No music-quality benchmark or accelerator compatibility is implied by the offline tests.

## Windows batch scripts

On Windows, run `python -m unittest tests.test_windows_launchers -v`. These network-free tests exercise the real batch scripts with a temporary virtual environment and fixture modules for pip and the CLI. They verify argument forwarding, paths with spaces/exclamation marks, failure exit status, environment reuse and installation failure handling. They do not replace a real package-installation check. The tests skip on other platforms.

## Video regression coverage

`tests.test_video_download` adds synthetic format ladders and generated local FFmpeg fixtures. It checks same-tier H.264 preference, 4K/high-frame-rate fallback without downscaling, best-source selection, real split-stream merging, codec-aware copy/remux/encoding, 4:4:4 conversion, fractional frame rate/duration/audio preservation, originals, output/sidecar collisions, failure cleanup and playlist rejection. Local fixture URLs are enabled only in tests. Both FFmpeg and ffprobe are required for real-media checks; those checks are skipped when unavailable. No live-site or editor-import claim follows from these tests.

For release verification, install the built wheel into an isolated environment and run `python tests/run_offline.py --installed`. The runner copies tests outside the checkout, verifies imports come from site-packages, and passes only test-relevant environment variables to child processes. It avoids inheriting unrelated service credentials. GitHub Actions runs this check against the locked macOS/Windows/Linux dependency sets.

Real CPU inference is opt-in: `python tools/smoke_inference.py` generates a one-second tone and checks both stem modes, complete decoding/alignment and source preservation. GitHub workflow dispatch exposes the same optional check. `python tools/smoke_desktop.py` performs a real desktop analysis job; a desktop display/Tk is required. Neither is a music-quality benchmark.
