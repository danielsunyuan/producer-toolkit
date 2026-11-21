# PTK: local/GitHub audit and music workflow specification

Audit date: 26 October 2026. Status: proposed specification; no runtime migration performed.

## What is actually installed

| Surface | Actual source | State |
| --- | --- | --- |
| `u` on the normal PATH | `/usr/local/bin/u` symlink to `/Users/duan/Documents/Utility/main.py` | Legacy DownloadUtility, local HEAD `67f4eb7`; modified source and untracked Spleeter code. `u --help` works. |
| `pt` on the normal PATH | Base Miniconda console script | Editable installation points at missing `/Users/duan/Projects/producer-toolkit`. `pt --help` fails with `ModuleNotFoundError`. |
| `ptk` in Conda environment `ptk` | `/Users/duan/Code/projects/project.producerTK/producer-toolkit` | Editable install, Python 3.11.14. Absolute-path `ptk --help` works; `pip check` reports no broken requirements. Not on the normal PATH. |
| Older PTK checkout | `/Users/duan/Code/projects/producer-toolkit` | HEAD `e9e2e28`, one commit ahead of GitHub main; additional uncommitted analyzer fallback work and aubio build artifacts. |
| Newer PTK checkout | `/Users/duan/Code/projects/project.producerTK/producer-toolkit` | Local branch `feature/transcript-download`, HEAD `ac39b47`; modified CLI/downloader plus untracked `tests/test_transcript.py`. |
| UI prototype | `/Users/duan/Code/projects/project.producerTK/UI` | Separate non-git directory with copied backend modules, multiple GUI entry points and packaging files. Not established as the active installed interface. |

The remembered `u "URL" -a` is real, but it does not invoke Producer Toolkit.
The legacy downloader launches `conda run -n utility yt-dlp`; its separator invokes a separate `spleeter` environment.
The `utility` environment has yt-dlp `2025.3.4.232844.dev0`; `ptk` has `2025.10.22`. Neither has been verified against a live URL during this audit.

## GitHub versus local code

Repository: <https://github.com/danielsunyuan/producer-toolkit>

Live GitHub branch heads were read through the GitHub connector:

| Branch | Verified HEAD | Meaning |
| --- | --- | --- |
| `main` | `cc018dd917d9b47719fef61d087fc4dcd6c1db2d` | Older packaged Spleeter implementation, `pt` entry point. |
| `feature/demucs-integration` | `ac39b47aec2eba9dd38cca25bd80cdd714c8b6a9` | 34 commits ahead of main; Demucs default, optional Spleeter, librosa analysis, command renamed to `ptk`. |
| `feature/python-package` | `a6b10a45ca9b688278738017738d0db13c5135e5` | Packaging branch already included in main's merge. |

The newer local checkout's committed HEAD exactly matches the live Demucs branch. Its working-tree changes are additional to that branch: three modified tracked files, 482 insertions and 26 deletions, plus an untracked transcript test. They include playlist behavior and transcript support. They must be reviewed and saved separately before any reset, reinstall or consolidation.

The older checkout's committed aubio changes are ancestors of the newer Demucs branch. Its uncommitted analyzer fallback changes still need comparison; do not assume they should be copied over the newer librosa analyzer.

The legacy Utility remote names `danielsunyuan/DownloadUtility`; a request for its `main` commit returned 404. That does not establish whether the repository was renamed, removed, made inaccessible, or uses another default branch. Its live remote state remains unverified.

## Material defects and mismatches

1. **Legacy stem cleanup can delete unrelated files.** `Utility/main.py:stem_download` passes the output directory as both the audio directory and download directory. After processing, `AudioStemExtractor.clear_download_directory` removes every direct child file there. The default is Downloads. This is a source inspection finding; the destructive path was not executed.
2. **Legacy download failures can look like success.** The audio subprocess does not check its return code; the CLI prints “Files ready” regardless. The subprocess also sits outside the links loop, and attempted comma splitting is immediately overwritten.
3. **Legacy modes are misleading.** `-inst` performs work before raising `NotImplementedError`; `-acca` selects two-stem extraction rather than a distinct vocal-only contract. Legacy `-t` means directory tree, while the local PTK extension uses it for transcripts. An alias must not silently reinterpret that flag.
4. **The command depends on the current environment.** `u` uses `/usr/bin/env python`, `pt` points at a stale editable install, and the working `ptk` lives off PATH. These are three independent execution paths.
5. **Newer file handling still needs hardening.** The newer CLI uses the shared system temporary directory for downloads; the separator uses a fixed `_temp_demucs` directory inside the destination. Concurrent jobs can collide. Downloader code scans output folders to infer files instead of consistently returning the exact artifacts produced by the job.
6. **A playlist has no complete result contract.** Local downloader documentation promises playlist support but returns one string; the CLI processes one returned file. Batch downloads and batch stem processing cannot be treated as equivalent. Single-video links containing playlist parameters also need an explicit policy.
7. **Separation may report incomplete success.** The Demucs wrapper skips missing stem files, and two-stem accompaniment errors are warnings. It can announce successful separation without validating all requested outputs. It calls `demucs` through PATH rather than the running Python environment.
8. **Analysis failure is represented as musical fact.** The newer analyzer falls back to `120.0` BPM and `C` on errors. Those values can enter filenames as if detected. Use an explicit unknown/error state and retain editable estimates separately from stable artifact identity.
9. **Documentation and packaging disagree.** Main documents Spleeter/aubio/`pt`; the feature branch uses Demucs/librosa/`ptk`. The newer README says audio-only analysis is off but still shows enhanced audio filenames. Placeholder clone URLs remain. Version `1.0.0` identifies materially different installed implementations. Dependencies and entry points appear in multiple packaging files.
10. **The GUI duplicates backend code.** Continued copying would create another source of drift. A future GUI should import the same package and job API as the CLI.

## Proposed product contract

PTK is a local preparation tool for music production: bring in reference audio, separate stems, estimate tempo/key, and export predictable files ready to drag into Ableton. Keep the CLI as the first supported interface. Revisit the GUI after this pipeline is reliable.

### Commands

Preserve the familiar commands as compatibility interfaces:

```sh
ptk "URL" -a
u "URL" -a
ptk "URL" -s -n 4
ptk "URL" -s -n 2
```

Proposed explicit interface for future implementation:

```sh
ptk doctor
ptk download "URL" --audio --output ./references
ptk separate ./reference.wav --stems 4 --output ./session
ptk analyze ./reference.wav
ptk prepare "URL" --stems 4 --output ./session
```

`download`, `separate`, `analyze`, `prepare`, and `doctor` are proposed commands, not currently implemented. Local file separation must be a normal production command, not hidden behind `--test-file`.

`ptk` is the canonical entry point. `u` delegates to the same CLI for the supported music flags. Legacy-only tree handling must fail with an explanatory migration message. Keep the old utility source available during migration; do not blindly repoint its symlink.

### Output and safety

- Each job owns a unique temporary directory and a destination identified by title plus source ID (or local file hash). Preserve original filenames in metadata.
- Default audio output stays WAV; record actual sample rate, channel count, subtype and duration. WAV conversion does not restore information absent from the source.
- Keep stable `source.wav` and stem names such as `vocals.wav`, `drums.wav`, `bass.wav`, `other.wav`, and `no_vocals.wav`. Make any BPM/key filename suffix opt-in.
- Export a `manifest.json` containing source URL/ID or local path/hash, job ID, PTK version and commit, backend/model, processing settings, artifacts, analysis status, estimates, errors and timestamps. Store source provenance; never copy authentication material into manifests.
- Preserve sources by default. Clean up only job-owned temporary files. No directory-wide deletion and no silent replacement of unrelated files. Reruns use an explicit overwrite policy or new job directory.
- Return all produced artifacts, including per-item results for batches. Use the downloader's metadata/hooks rather than a search for the newest existing file.
- A normal URL processes one item. Require explicit playlist opt-in, with a preview or item limit. Record partial failures and return an appropriate failure status.
- Verify every requested stem exists, is nonempty and decodable, with compatible channel counts, sample rates and durations. Only then mark the job successful.
- Analysis failure produces `unknown`, never an invented 120 BPM/C result. Allow manual tempo/key corrections. Treat tempo and key as estimates; do not imply a calibrated confidence score without validation.
- Align all stems at time zero. Validate imports into Ableton before promising DAW readiness. Native Ableton project generation, automatic warping, MIDI extraction and model training are outside the first release.

### Installation and diagnostics

Use one package metadata source and one reproducible macOS/Python environment. Start from the existing working Python 3.11 PTK environment as evidence, then verify a clean install before choosing final dependency constraints. Keep basic download dependencies separate from optional separation/analysis dependencies where practical; `--help` and diagnostics should work without loading models.

`ptk doctor` should show executable, Python, imported package path, package version, commit/dirty state when available, FFmpeg, downloader and separation versions, model/cache location and writability, and actionable missing-dependency messages. It must not download models or media unless explicitly requested.

## Ordered implementation and acceptance checks

1. **Preserve and select sources.** Save each checkout's local diffs/untracked source, review the transcript/playlist changes independently, and establish a maintained branch based on `feature/demucs-integration`. Do not fold GUI copies or aubio build artifacts into it.
2. **Fix file ownership and job results first.** Introduce isolated temporary jobs, exact artifact tracking and strict success/failure handling. Regression tests must put unrelated sentinel files beside outputs and prove they survive both success and failure. Test concurrent same-title jobs and missing/partial stems without real inference.
3. **Unify installation and commands.** Add `doctor`, canonical `ptk`, documented `u` compatibility and clear flag errors. Verify clean-environment install plus `--help` without heavy optional dependencies. Review the migration diff before changing the machine's existing launchers.
4. **Make the music workflow complete.** Support local files, two/four stems, explicit analysis, manifests and safe reruns. Test metadata and error handling offline; use a generated fixture to verify file format/duration/alignment. Run one separately identified real-model smoke test and a permitted-source download test; mocked tests alone cannot establish inference or live-site reliability.
5. **Release and migrate.** Update README and usage examples together, use a version that distinguishes the release from today's divergent `1.0.0` installs, add macOS CI/package smoke checks, and verify the launchers resolve to the intended installed release. Merge and installation are separate steps after reviewing the changes.
6. **Optional GUI.** Reuse the same package/job API; do not maintain a copied backend.

## Verification completed in this audit

- Live GitHub repository metadata and branch heads read through the connector.
- Compared local committed history with the verified main and Demucs heads.
- Read legacy download/separation/cleanup code and newer CLI/downloader/analyzer/separator code.
- `u --help`: passed.
- Normal-PATH `pt --help`: failed due to missing imported package.
- Absolute-path `/Users/duan/miniconda3/envs/ptk/bin/ptk --help`: passed, including the local transcript flags.
- PTK environment `python -m pip check`: passed. This checks installed dependency metadata, not inference correctness.
- No live download, model inference, destructive cleanup, global install, launcher edit, GitHub push or merge performed.

This document lives in a separate workspace checkout on `docs/ptk-formalisation`, based on the committed Demucs branch. The existing installations and their uncommitted changes remain in place. A shell network clone was unavailable, so this checkout was cloned locally; its base commit was independently matched against the live GitHub branch head.
