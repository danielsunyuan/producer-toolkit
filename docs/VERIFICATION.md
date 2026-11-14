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


# Video compatibility verification — 15 November 2026

The video change is based on the working-repository consolidation at `e5510c2`. Audio download and stem processing implementations remain unchanged apart from the shared downloader's video-specific branches.

- All 49 relevant tests passed: the existing 34 workflow/analyzer tests plus 15 video regression tests. Video tests use generated local media and synthetic format ladders, without live-site dependence.
- Real yt-dlp split-stream downloads and FFmpeg merges passed in both modes. Video and audio packet SHA-256 sequences matched the selected input streams after merging/remuxing, establishing that these paths did not re-encode them.
- Compatible H.264/AAC MP4 was byte-identical to its downloaded input. VP9/Opus converted to H.264/AAC with matching dimensions, fractional frame rate and duration. Mixed-codec tests verified that only incompatible streams were encoded; H.264 4:4:4 was converted to 8-bit 4:2:0. Best-source mode kept the original codecs/container and identical file bytes for a single muxed source.
- Output/sidecar collisions, playlist rejection, failure cleanup and source/unrelated-file preservation passed in both modes. CLI tests covered explicit best-source selection and rejection of the video-only option on audio/stem commands.

## Existing 4K AV1 source

A two-second stream-copy excerpt was made from the user's existing `5GhhVHpPR_M` download; the original SHA-256 was unchanged. The new download/preparation workflow processed this excerpt, and was also repeated through a freshly rebuilt/installed package imported from site-packages. The full song was not reconverted or downloaded again.

| Property | Input excerpt | Compatible output |
| --- | --- | --- |
| Container | MP4 | MP4 |
| Video | AV1, yuv420p | H.264 High, yuv420p |
| Dimensions | 3840 × 2160 | 3840 × 2160 |
| Frame rate | 24000/1001 (23.976 fps) | 24000/1001 (23.976 fps) |
| Video duration | 2.002000 s | 2.002000 s |
| Container duration | 2.020136 s | 2.020136 s |
| Audio | AAC, 44.1 kHz, stereo | AAC, 44.1 kHz, stereo, copied |

AAC packet bytes were identical before/after conversion (SHA-256 of stream-copied ADTS). The compatible output passed full FFmpeg decoding. Best-source output was byte-identical to the AV1 excerpt. Conversion used libx264 CRF 18, slow preset, and copied the original AAC. Checks ran on Apple Silicon macOS with FFmpeg/ffprobe 7.1.1 and yt-dlp 2026.10.26.

This is codec/media validation, **not a Final Cut Pro import test**. No fresh live YouTube extraction, full-song conversion, HDR tone-mapping test, accelerator run or remote CI result is claimed for this change. The 8-bit compatibility conversion does not implement HDR-to-SDR tone mapping.
