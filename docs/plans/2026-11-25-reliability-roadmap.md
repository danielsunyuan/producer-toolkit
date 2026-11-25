# PTK reliability roadmap implementation plan

> **For Codex:** Follow executing-plans task by task, keeping each verified stage in a separate commit.

**Goal:** Make the existing local PTK workflow reliable and reproducibly installable before adding a thin local interface.

**Architecture:** Retain the canonical CLI and Demucs backend. Validate inputs before work, stage complete outputs before publication, and keep all cleanup scoped to job-owned paths. Use pyproject.toml for package metadata and checked-in per-platform dependency locks for release verification.

**Tech stack:** Python 3.11, unittest, yt-dlp, FFmpeg, Demucs, GitHub Actions; macOS and native Windows/Cronos.

## Sequence and acceptance

1. Finish Windows PR #7 after confirming green checks. Verify merge and clean main.
2. Silent/non-finite input: write failing tests; reject silent/constant or invalid decoded samples before model invocation. Verify quiet valid audio still proceeds, original/sentinel preservation, and a real CLI silent-input check.
3. Installation: remove duplicated setup metadata; keep requirements.txt as an install entry point. Generate platform-specific dependency locks and test wheel contents plus installation outside the source tree in isolated environments. Keep downloader upgrades documented separately from a tested lock.
4. Publication: write failure/concurrency tests. Copy to a private sibling stage, fsync, then publish without clobbering. Publish stem directories as a complete job under a cooperative destination lock; leave only clearly private staging after an uncatchable termination. Never auto-delete another job's files.
5. Resources: add explicit CLI limits for duration, download size and reserved disk space, with conservative defaults and explicit overrides. Validate local input and download metadata; enforce byte limits while downloading; fail before expensive work where possible. Reject URL credentials and redact query/auth material from saved provenance. Keep the tool local; do not claim hosted-service SSRF protection.
6. Release checks: run the full offline suite and installed-wheel checks across macOS/Linux/Windows on pushes and PRs. Add a declared MIT licence, third-party/model notices, security reporting guidance and a redacted Git-history secret scan. Record unresolved licence or distribution questions rather than inventing assurances.
7. Interface: use the user's chosen local interface, sharing the same CLI/backend. Validate error/progress handling and keep it unexposed to the network. If no preference arrives, start with a minimal local desktop window; packaging as a signed app is a separate release milestone.

## Verification and delivery

For each stage: red test, smallest fix, focused tests, then relevant regression checks; commit only after passing. Verify real inference separately from mocked tests. Update Notion with actual outcomes and any remaining limitations. Use a reviewable PR for the combined, ordered commits and do not claim a public release or signed installer.
