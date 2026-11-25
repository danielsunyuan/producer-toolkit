"""Download one item in private temporary storage; never guess from Downloads."""
import json
import os
import shutil
import tempfile
import sys
from pathlib import Path
from functools import partial
from .video import prepare_video, select_video_formats
from ..files import publish
from ..limits import Limits, public_message, public_url, validate_url
from urllib.parse import urlsplit


class DownloadLogger:
    """Keep signed URL parameters and embedded credentials out of messages."""
    def debug(self, message):
        pass

    def warning(self, message):
        print(f"PTK download: {public_message(message)}", file=sys.stderr)

    error = warning

def _download(url, output_path, audio, video_quality="compatible", write_metadata=False, limits=None):
    if video_quality not in ("compatible", "best"):
        raise ValueError("Video quality must be compatible or best.")
    limits = limits or Limits()
    if urlsplit(url).scheme in ("http", "https"):
        validate_url(url)
    import yt_dlp
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is missing. Install it with: brew install ffmpeg")
    suffix = ".wav" if audio else ".mp4"
    target = Path(output_path or Path.home() / "Downloads").expanduser().resolve()
    explicit_file = target.suffix.lower() in ((".wav",) if audio else (".mp4", ".mkv", ".webm", ".mov")) and not target.is_dir()
    if not audio and explicit_file and video_quality == "best":
        raise ValueError("Best source quality requires an output directory so the container can follow the source.")
    if not audio and explicit_file and target.suffix.lower() != ".mp4":
        raise ValueError("Compatible video output must use an .mp4 filename.")
    directory = target.parent if explicit_file else target
    limits.check_disk(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ptk-download-", dir=directory) as job:
        def progress(data):
            total = 0
            for path in Path(job).rglob('*'):
                try:
                    if path.is_file():
                        total += path.stat().st_size
                except FileNotFoundError:
                    pass  # A downloader may rename a fragment while reporting progress.
            limits.check_size(max(total, data.get('downloaded_bytes', 0)))
            limits.check_disk(directory)

        options = {
            "outtmpl": str(Path(job) / "%(title).150B [%(id)s].%(ext)s"),
            "format": "bestaudio/best" if audio else partial(select_video_formats, quality=video_quality),
            "noplaylist": True, "quiet": True,
            "ffmpeg_location": shutil.which("ffmpeg"),
            "socket_timeout": 20, "retries": 2,
            "max_filesize": limits.max_bytes, "progress_hooks": [progress],
            "logger": DownloadLogger(),
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
            options["merge_output_format"] = "mkv"
            options["format_sort"] = ["res", "fps"]
        with yt_dlp.YoutubeDL(options) as downloader:
            preview = downloader.extract_info(url, download=False)
            if not preview or preview.get("entries") is not None or preview.get("_type") == "playlist":
                raise ValueError("Use a single song/video URL; playlist downloads are not enabled.")
            limits.check_duration(preview.get("duration"))
            limits.check_size(preview.get("filesize") or preview.get("filesize_approx") or 0)
            info = downloader.extract_info(url, download=True)
            if not info or info.get("entries") is not None or info.get("_type") == "playlist":
                raise ValueError("Use a single song/video URL; playlist downloads are not enabled.")
            source = Path(downloader.prepare_filename(info)).resolve()
            if audio:
                source = source.with_suffix(suffix)
        if not source.is_relative_to(Path(job).resolve()):
            raise RuntimeError("Downloader returned a path outside this job.")
        if not source.is_file() or source.stat().st_size == 0:
            raise RuntimeError(f"Download did not produce the expected {suffix} file.")
        limits.check_size(source.stat().st_size)
        metadata = {}
        if audio:
            import soundfile as sf
            details = sf.info(str(source))
            limits.check_duration(details.duration)
            if details.frames == 0:
                raise RuntimeError("Downloaded audio is empty.")
            if (details.samplerate, details.channels, details.subtype) != (44100, 2, "PCM_24"):
                raise RuntimeError("FFmpeg did not produce the requested 44.1 kHz, stereo, 24-bit WAV.")
            metadata.update(sample_rate=details.samplerate, channels=details.channels,
                            frames=details.frames, subtype=details.subtype)
        if not audio:
            selected_fields = ("format_id", "ext", "vcodec", "acodec", "width", "height", "fps", "tbr", "abr", "asr", "audio_channels")
            metadata.update(video_quality=video_quality, selected_formats=[
                {key: fmt[key] for key in selected_fields if key in fmt}
                for fmt in info.get("requested_formats") or [info]])
            metadata["download_merge"] = ({"container": source.suffix.lstrip("."), "stream_copy": True}
                                          if info.get("requested_formats") else None)
            downloaded_name = source.name
            source, processing = prepare_video(source, video_quality, limits=limits)
            metadata.update(processing)
            suffix = source.suffix
            output_name = Path(downloaded_name).with_suffix(suffix).name
        else:
            output_name = source.name
        destination = target if explicit_file else directory / output_name
        from .. import __version__
        metadata.update(schema_version=1, ptk_version=__version__,
                        source_url=public_url(info.get("webpage_url", url)), source_id=info.get("id"),
                        title=info.get("title"), artifact=destination.name)
        staged_manifest = Path(job) / "manifest.json"
        if write_metadata:
            staged_manifest.write_text(json.dumps(metadata, indent=2) + "\n")
        limits.check_disk(directory, required=source.stat().st_size)
        result = publish(source, destination)
        if write_metadata:
            try:
                publish(staged_manifest, destination.with_suffix(suffix + ".json"))
            except BaseException:
                Path(result).unlink(missing_ok=True)
                raise
        return result

def download_audio(url, output_path=None, analyze_features=False, metadata=False, limits=None):
    """Download stereo 44.1 kHz 24-bit WAV without overwriting existing audio."""
    result = _download(url, output_path, True, write_metadata=metadata, limits=limits)
    if analyze_features:
        from ..analyzer.audio_analyzer import analyze_audio
        bpm, key = analyze_audio(result)
        print(f"Estimated tempo: {bpm or 'unknown'}; key: {key or 'unknown'}")
    return result

def download_video(url, output_path=None, quality="compatible", metadata=False, limits=None):
    """Download H.264/AAC MP4 by default, or preserve source streams with best."""
    return _download(url, output_path, False, video_quality=quality, write_metadata=metadata, limits=limits)
