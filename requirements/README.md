# Tested dependency sets

These files pin PTK's runtime dependencies for CPython 3.11. macOS targets Apple Silicon; Windows and Linux target x86-64. Linux requires glibc 2.28 or newer and uses CPU PyTorch wheels. They do not pin FFmpeg, the JavaScript runtime or downloaded model checkpoints, and do not promise byte-identical package builds.

Create an isolated virtual environment, then install the matching file with hash checking before installing PTK without resolving dependencies again:

```sh
python -m pip install --require-hashes -r requirements/macos-arm64-py311.txt
python -m pip install --no-deps .
python -m pip check
```

Use `windows-amd64-py311.txt` or `linux-amd64-py311.txt` on those platforms. Each file records its regeneration command. Regenerate deliberately and run the full offline suite plus real inference before replacing a tested set. Build tools remain governed by pyproject.toml.

The general `pip install .` / `pip install -r requirements.txt` paths use pyproject.toml's compatible version ranges. Those are development installs, not the pinned reference configuration. Updating yt-dlp to repair a live-site extraction issue changes the tested set; record the new version and rerun download checks.

For Linux, retain the explicit `--extra-index-url https://download.pytorch.org/whl/cpu` header after regeneration. uv's CPU backend resolves that source implicitly; pip needs the index stated in the file. Hash checking remains required for every dependency.
