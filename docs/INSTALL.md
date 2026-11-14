# Installation and troubleshooting

Follow the [README installation steps](../README.md#install) for Python 3.11, system FFmpeg and a supported YouTube JavaScript runtime. Use an isolated environment so PTK does not alter other audio applications.

## Diagnose the active installation

```sh
ptk --version
ptk doctor
python -m pip check
```

Diagnostics print the selected interpreter, source directory, dependencies, FFmpeg, runtime and model-cache status. They do not download anything or run inference. If a different command is selected, activate the intended virtual environment and check `command -v ptk`.

## YouTube extraction

```sh
python -m pip install --upgrade 'yt-dlp[default]'
```

Keep yt-dlp and its EJS dependencies current and make Deno or Node 22+ available. Some sources require authentication or restrict downloading; successful extraction is source-dependent. Playlist-only inputs are unsupported.

## Stem separation

The first separation fetches the pretrained htdemucs checkpoint. Allow network access and check available disk space. If fetching fails, retry after resolving the reported connection error; do not delete unrelated cached models.

CPU is the default and tested path. MPS/CUDA are optional and require a compatible system; compatibility and speed are not guaranteed. Existing outputs are preserved: choose a fresh output directory to repeat a job.

## Analysis

Tempo and key are estimates. Unknown results remain unknown. WAV conversion does not restore detail absent from a compressed source.

Spleeter, transcript extraction and the older directory-tree utility are not supported by this CLI. The separate GUI prototype is not part of the installation.
