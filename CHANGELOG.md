# Changelog

## 1.1.1 — working repository consolidation

- Repair YouTube extraction with current yt-dlp default dependencies and JavaScript runtime selection.
- Consolidate `ptk`, `u` and `pt` around one CLI.
- Support local-file separation, two/four stems, analysis and diagnostics.
- Isolate temporary processing jobs, preserve sources and refuse silent output replacement.
- Validate complete stems before publication and propagate processing failures.
- Record provenance and analysis metadata, with unknown results rather than fabricated tempo/key values.
- Cover workflow and analyzer behavior with 34 offline regression tests.

This consolidates the October 2026 local restoration on top of the Demucs integration branch. Older transcript/playlist experiments and the separate GUI prototype are not included.
