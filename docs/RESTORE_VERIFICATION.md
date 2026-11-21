# PTK restoration verification — 27 October 2026

Implemented locally on branch `fix/restore-music-workflow`, based on verified GitHub Demucs branch commit `ac39b47`. No original checkout, global launcher or shell profile has been changed by this session.

## Implemented

- Canonical `ptk` CLI and `u` / `pt` compatibility launchers. Package version is 1.1.0.
- Existing `ptk` Conda interpreter used explicitly by local launchers, so environment activation is unnecessary.
- Per-job download and separation storage; exact sanitized downloader filenames; no search through Downloads; exclusive output creation and rollback of files owned by a failed job.
- Real subprocess failures and missing/partial/mismatched stems return failure. Separation runs under the same Python environment as PTK.
- Downloads preserve sources and produce verified stereo 44.1 kHz / 24-bit WAV plus provenance JSON. Stable stems and JSON analysis metadata avoid renaming artifacts with uncertain estimates.
- Local-file separation, two/four stems, vocal/instrumental pair aliases, optional analysis, doctor diagnostics, lazy imports for help/version.
- Explicit single-item behavior and rejection of playlist-only input before downloading.
- No fallback 120 BPM/C claims on analysis errors.
- Package, main.py and compatibility commands share the same implementation.
- Experimental transcript/playlist source remains in its original checkout; not silently integrated or overwritten.

## Executed checks

- All 34 offline workflow and analyzer tests passed. Tests cover failure cleanup and preservation of sentinel/source files, output collisions, missing stems, duration mismatch, single-item URL handling, sanitized filenames, CLI error status, and nullable analysis results.
- Real cached htdemucs CPU inference: one-second generated stereo fixture produced four decodable, aligned stems; a separate real two-stem run produced vocals and no_vocals; all were 44,100 frames at 44.1 kHz with two channels. The original remained intact. This establishes execution, not separation quality on music.
- Real yt-dlp + FFmpeg pipeline on a local AAC fixture: produced stereo 44.1 kHz PCM_24 WAV. This caught and corrected a postprocessor argument key capitalization issue. File-URL support was enabled only in the test, not the normal CLI.
- Package wheel build passed. The wheel's console entry points include `ptk`, `u` and `pt`.
- Sourcing `activate.sh` in zsh resolved all three commands to this checkout; version and doctor passed.
- Help also works under Python with site packages disabled, without loading the audio/ML stack.
- Installer tested twice against an isolated HOME: original profile preserved, one backup created, activation line added once.
- Git whitespace check passed.

The YouTube/Bandcamp download of **Fine — Days Incomplete** could not run: this session's shell cannot resolve either host. Local HTTP server binding is also restricted. No song file has been downloaded. A song-specific launcher is provided for execution from the user's normal Terminal.

## Starting the repaired app

```sh
source /Users/duan/Documents/Codex/2026-10-26/new-chat/producer-toolkit/activate.sh
u "https://www.youtube.com/watch?v=wg_cpdaBYs8" -a
```

Or run `Download-Days-Incomplete.command`.

For future Terminal windows, the user can run `Install-PTK-Terminal.command`. It backs up `~/.zshrc` before adding one activation line. This step has not been run here because that file is outside this session's writable roots. It leaves the legacy global symlink in place but puts the fixed commands earlier on PATH. Remove that one activation line to undo; existing audio and the old tool are untouched.

The installed yt-dlp is 2025.10.22. Successful local conversion does not guarantee current YouTube extraction; if the normal-terminal song download reports extraction errors, upgrade yt-dlp in the PTK environment and retry. No accelerator configuration or full-length music separation quality has been tested.

## Source and recovery

Original source and local modifications remain at:
- `/Users/duan/Documents/Utility`
- `/Users/duan/Code/projects/producer-toolkit`
- `/Users/duan/Code/projects/project.producerTK/producer-toolkit`
- `/Users/duan/Code/projects/project.producerTK/UI`

A snapshot of the first three working-tree patches and the untracked transcript test is kept under this checkout's ignored `.runtime/original-changes/` folder. These are preservation copies, not merged changes.

No push, pull-request merge or deployment has been performed.

## Installation executed on 27 October

Installed the verified 1.1.0 wheel into this checkout's `.venv`, using system site packages from the existing Python 3.11 PTK environment. Project launchers now select this installed environment. Doctor and all three version checks passed.

The real shell-profile installer was attempted, but the filesystem sandbox denied creation of the backup beside `~/.zshrc`. It stopped before editing the profile. Global command activation is therefore still pending user execution from the normal Terminal. No approval prompt was available for this path.

## YouTube 403 repair — 29 October 2026

The installed downloader was still yt-dlp 2025.10.22. Upgraded this project's environment to yt-dlp[default] 2026.10.26 with matching yt-dlp-ejs 0.8.0, enabled the installed Node 25.2.1 runtime explicitly in API options, and required the current default dependency group for future installs. Deno is preferred when present. PTK version is now 1.1.1. The launcher gives yt-dlp a project-owned cache.

A real YouTube download of wg_cpdaBYs8 completed successfully: Fine — Days Incomplete, 220.629 seconds, 44.1 kHz stereo PCM_24 WAV. The audio is at `sample-downloads/Fine-Days-Incomplete.wav` and has a provenance sidecar. All 34 offline regression tests passed with the updated downloader. Existing global activation loads the changes directly; no shell-profile reinstall is required. Package dependency check passed.
