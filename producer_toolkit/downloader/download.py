"""Download one item in private temporary storage; never guess from Downloads."""
import json
import os
import shutil
import tempfile
from pathlib import Path
from ..files import publish

def _download(url, output_path, audio):
    import yt_dlp
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is missing. Install it with: brew install ffmpeg")
    suffix = ".wav" if audio else ".mp4"
    target = Path(output_path or Path.home() / "Downloads").expanduser().resolve()
    explicit_file = target.suffix.lower() == suffix and not target.is_dir()
    directory = target.parent if explicit_file else target
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ptk-download-", dir=directory) as job:
        options = {
            "outtmpl": str(Path(job) / "%(title).150B [%(id)s].%(ext)s"),
            "format": "bestaudio/best" if audio else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "noplaylist": True, "quiet": True,
            "ffmpeg_location": shutil.which("ffmpeg"),
            "socket_timeout": 20, "retries": 2,
        }
        if os.environ.get("PTK_CACHE_DIR"):
            options["cachedir"] = os.environ["PTK_CACHE_DIR"]
        # Modern YouTube extraction needs an explicitly enabled JS runtime.
        # Deno is preferred; Node is already available on many producer Macs.
        for runtime in ("deno", "node"):
            executable = shutil.which(runtime)
            if executable:
                options["js_runtimes"] = {runtime: {"path": executable}}
                break
        if audio:
            options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]
            options["postprocessor_args"] = {"extractaudio+ffmpeg_o": ["-ar", "44100", "-ac", "2", "-c:a", "pcm_s24le"]}
        else:
            options["merge_output_format"] = "mp4"
            options["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
        with yt_dlp.YoutubeDL(options) as downloader:
            preview = downloader.extract_info(url, download=False)
            if not preview or preview.get("entries") is not None or preview.get("_type") == "playlist":
                raise ValueError("Use a single song/video URL; playlist downloads are not enabled.")
            info = downloader.extract_info(url, download=True)
            if not info or info.get("entries") is not None or info.get("_type") == "playlist":
                raise ValueError("Use a single song/video URL; playlist downloads are not enabled.")
            source = Path(downloader.prepare_filename(info)).with_suffix(suffix).resolve()
        if not source.is_relative_to(Path(job).resolve()):
            raise RuntimeError("Downloader returned a path outside this job.")
        if not source.is_file() or source.stat().st_size == 0:
            raise RuntimeError(f"Download did not produce the expected {suffix} file.")
        metadata = {}
        if audio:
            import soundfile as sf
            details = sf.info(str(source))
            if details.frames == 0:
                raise RuntimeError("Downloaded audio is empty.")
            if (details.samplerate, details.channels, details.subtype) != (44100, 2, "PCM_24"):
                raise RuntimeError("FFmpeg did not produce the requested 44.1 kHz, stereo, 24-bit WAV.")
            metadata.update(sample_rate=details.samplerate, channels=details.channels,
                            frames=details.frames, subtype=details.subtype)
        destination = target if explicit_file else directory / source.name
        from .. import __version__
        metadata.update(schema_version=1, ptk_version=__version__,
                        source_url=info.get("webpage_url", url), source_id=info.get("id"),
                        title=info.get("title"), artifact=destination.name)
        staged_manifest = Path(job) / "manifest.json"
        staged_manifest.write_text(json.dumps(metadata, indent=2) + "\n")
        result = publish(source, destination)
        try:
            publish(staged_manifest, destination.with_suffix(suffix + ".json"))
        except BaseException:
            Path(result).unlink(missing_ok=True)
            raise
        return result

def download_audio(url, output_path=None, analyze_features=False):
    """Download stereo 44.1 kHz 24-bit WAV without overwriting existing audio."""
    result = _download(url, output_path, True)
    if analyze_features:
        from ..analyzer.audio_analyzer import analyze_audio
        bpm, key = analyze_audio(result)
        print(f"Estimated tempo: {bpm or 'unknown'}; key: {key or 'unknown'}")
    return result

def download_video(url, output_path=None):
    return _download(url, output_path, False)
