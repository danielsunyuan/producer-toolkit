# Changelog

## Unreleased — optional download metadata

- Audio and video downloads now save only the media file by default. Use `--metadata` to opt in to the JSON provenance sidecar. Stem manifests are unchanged.

## Unreleased — video compatibility

- Default video downloads to H.264 8-bit 4:2:0 / AAC MP4, preserving the highest available resolution and frame rate. Prefer compatible same-tier streams; copy existing compatible streams and convert incompatible streams automatically.
- Add `-v --video-quality best` for original video/audio codecs without lossy conversion and an appropriate source/MKV container.
- Record selected formats, lossless merges, probed media properties and per-stream conversion decisions in video sidecars.
- Add offline format-selection and real-media regression coverage; retain single-video safeguards, collision protection and existing audio/stem behavior.
- Codec/metadata validation is separate from actual editor import; Final Cut Pro import is not claimed.

## 1.1.1 — working repository consolidation

- Repair YouTube extraction with current yt-dlp default dependencies and JavaScript runtime selection.
- Consolidate `ptk`, `u` and `pt` around one CLI.
- Support local-file separation, two/four stems, analysis and diagnostics.
- Isolate temporary processing jobs, preserve sources and refuse silent output replacement.
- Validate complete stems before publication and propagate processing failures.
- Record provenance and analysis metadata, with unknown results rather than fabricated tempo/key values.
- Cover workflow and analyzer behavior with 34 offline regression tests.

This consolidates the October 2026 local restoration on top of the Demucs integration branch. Older transcript/playlist experiments and the separate GUI prototype are not included.
