# Producer Toolkit 1.1.1

Download reference audio and prepare aligned stems for music production. The canonical command is `ptk`; `u` and `pt` use the same implementation.

YouTube downloads require a current `yt-dlp[default]` (including its matching EJS solver) and Deno or Node 22+. PTK enables an available runtime automatically. The 1.1.1 repair was verified with yt-dlp 2026.10.26, EJS 0.8.0 and Node 25.2.1 by downloading Fine — Days Incomplete. To refresh the downloader in this checkout, use `.venv/bin/python -m pip install --upgrade 'yt-dlp[default]'` from the project directory.

## Install

Python 3.11 is the tested version. Install system FFmpeg and a JavaScript runtime (Deno or Node 22+) for YouTube extraction. On macOS with Homebrew:

```sh
brew install python@3.11 ffmpeg deno
git clone https://github.com/danielsunyuan/producer-toolkit.git
cd producer-toolkit
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
ptk --help
ptk doctor
```

On Linux, install Python 3.11, FFmpeg and Deno using your system's supported installation method, then follow the clone/environment/package steps above.

On Windows, install Python 3.11 and put FFmpeg/ffprobe and Deno or Node 22+ on PATH. From Command Prompt in the cloned repository:

```bat
scripts\windows\install.bat
scripts\windows\run_toolkit.bat --help
scripts\windows\run_toolkit.bat "C:\Music\song.wav" -s -n 2 -o "C:\Music\PTK"
```

The installer creates or reuses this checkout's `.venv`, installs PTK and runs diagnostics. It stops on failure and does not change system PATH. The launcher uses that environment and passes all arguments and the CLI exit status through; its defaults match `ptk`. Both scripts return without pausing. Run them from an existing Command Prompt to keep errors visible. Windows 10 CPU regression and generated-audio separation checks have passed; live-site downloads and GPU processing have not been verified on Windows.

Installation registers `ptk`, `u` and `pt`; check for existing commands before installing. The first separation downloads the pretrained htdemucs checkpoint. Processing runs locally; downloads and the initial model fetch require network access.

For development, use `python -m pip install -e .` instead. The optional `activate.sh` and `bin/` wrappers activate this checkout without replacing a global command. Existing Mac launchers remain available for the original local setup.

## Music workflow

```sh
# Single track → stereo 44.1 kHz / 24-bit WAV in Downloads
u "URL" -a

# URL → preserved source WAV + four aligned stems
ptk "URL" -s

# Local audio → four stems; original remains intact
ptk "/path/to/song.wav" -s -o "$HOME/Music/PTK"

# Vocals and accompaniment
ptk "/path/to/song.wav" -s -n 2 -o "$HOME/Music/PTK"
# Legacy aliases -acca and -inst both produce this two-stem pair.

# Skip estimated BPM/key metadata
ptk "/path/to/song.wav" -s --no-analysis

# Estimate tempo/key without changing the file
ptk "/path/to/song.wav" --analyze

# Compatible MP4 (H.264/AAC), preserving the best resolution and frame rate
ptk "URL" -v

# Best source streams, without lossy conversion
ptk "URL" -v --video-quality best
```

CPU is the default for compatibility. `--device mps` and `--device cuda` are available for environments that support them; only explicitly tested configurations should be treated as verified.

Downloads use title plus source ID to reduce name collisions, and save only the media file by default. Add `--metadata` to also save a provenance JSON sidecar. Stem folders contain stable stem filenames and `manifest.json`. Outputs are never silently overwritten: choose another output directory for a rerun. Every requested stem must exist and have matching length, sample rate and channel count before success is reported. Only job-owned temporary storage is cleaned up.

BPM/key are estimates. Failed detection is `null`/`unknown`, not an invented 120 BPM or C. WAV conversion does not restore detail absent from the source. Separation requires a model checkpoint; the doctor command reports whether htdemucs is cached without loading or downloading it.

Playlist-only inputs are rejected. A single video link with playlist parameters processes only that video. The local experimental transcript/playlist additions in the previous checkout have not been integrated into this release; those original files remain untouched. Spleeter and the unrelated legacy directory-tree flag are not part of this repaired CLI.

## Video quality modes

`ptk "URL" -v` defaults to **Compatible MP4** (`--video-quality compatible`):

- Select the highest available resolution and frame-rate tier, including 4K. Prefer an H.264 stream in that same tier and an AAC audio stream when available; do not fall back to lower resolution or frame rate merely to avoid conversion.
- Check the downloaded codecs with ffprobe. H.264 8-bit 4:2:0 (`yuv420p`) and AAC are copied. A compatible MP4 is kept unchanged; compatible streams in another container are remuxed without re-encoding.
- Otherwise convert only the incompatible streams: video uses software H.264 (`libx264`, CRF 18, slow preset, 8-bit 4:2:0), and audio uses AAC at 320 kb/s. Existing AAC audio is copied. Video dimensions and frame timing are retained; there is no forced frame rate, downscale or upscale. Silent sources remain silent.

Conversion takes extra time, may produce substantially larger files, and introduces a generation of loss in the streams that are encoded. H.264/AAC improves editor compatibility, but does not guarantee import into every editor/version. **Final Cut Pro import has not been verified.** HDR-to-SDR tone mapping is not implemented; use best-source mode to retain original HDR precision rather than relying on this 8-bit conversion for HDR delivery.

`ptk "URL" -v --video-quality best` selects **Best source quality**: keep the highest-tier source video and best available audio without lossy conversion. Split streams are merged into MKV using stream copy; a single muxed source keeps its container. The extension follows the actual container rather than forcing `.mp4`. AV1, VP9, Opus and other source formats may not import into some video editors. Supply an output directory so PTK can choose the appropriate filename/container.

Both modes keep the single-video policy and refuse media output collisions (and sidecar collisions when `--metadata` is enabled). Existing files are untouched. Downloaded intermediates belong to the temporary job and are removed after success/failure; choose best-source mode when you want a retained source-quality download. When requested with `--metadata`, the JSON sidecar records the mode, selected format IDs/codecs/resolution/frame rate, any lossless download merge, probed input/output properties, and per-stream copy/encoding decisions with conversion settings. Source-format metadata can be incomplete; the probed properties describe the actual downloaded media. Sidecars exclude stream URLs and authentication headers.

FFmpeg (including ffprobe, libx264 and AAC encoding support) is required. `--video-quality` is accepted only with `-v`; audio and stem commands retain their existing behavior.

## Verification

```sh
python -m unittest tests.test_safe_workflow tests.test_audio_analyzer tests.test_video_download -v
```

Offline regression tests verify preservation of unrelated files, missing/partial stems, failing subprocesses, sanitized downloader paths, playlist rejection, conflicting flags, and output collisions. They are separate from real-model and live-download smoke tests. The verified local configuration is macOS / Python 3.11 / CPU. A generated audio fixture has also exercised real two/four-stem inference; automated regression tests alone do not establish music separation quality or live-site reliability.

## How it works

The CLI selects a download, local analysis or separation operation. yt-dlp resolves a single source into job-specific temporary storage; FFmpeg converts audio. Demucs runs through the same Python interpreter as PTK. SoundFile checks output metadata before files are published, while librosa provides optional tempo/key estimates. Exclusive file creation prevents silent replacement; failure cleanup removes only artifacts created by that job.

This project integrates pretrained Demucs models; it does not train a separation model. There is no supported GUI, transcript mode, batch playlist mode or native Ableton project export. Use media you own or have permission to process.

See [testing instructions](tests/README.md), [verification results](docs/VERIFICATION.md) and [release notes](CHANGELOG.md).
