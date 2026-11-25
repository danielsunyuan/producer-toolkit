"""Canonical CLI, also used by the compatibility u entry point."""
import argparse
import importlib.metadata
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse
from . import __version__
from .limits import Limits, public_message, validate_url

def doctor():
    print(f"PTK {__version__}\nPython: {sys.executable}\nSource: {Path(__file__).resolve().parent}")
    print(f"FFmpeg: {shutil.which('ffmpeg') or 'MISSING (brew install ffmpeg)'}")
    for name in ("yt-dlp", "yt-dlp-ejs", "demucs", "torch", "torchaudio", "librosa", "soundfile"):
        try:
            version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            version = "MISSING"
        print(f"{name}: {version}")
    print(f"YouTube JS runtime: {shutil.which('deno') or shutil.which('node') or 'MISSING (install Deno or Node 22+)'}")
    torch_home = Path(os.environ.get("TORCH_HOME", Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "torch"))
    checkpoint = torch_home / "hub" / "checkpoints" / "955717e8-8726e21a.th"
    print(f"htdemucs checkpoint: {checkpoint} ({'cached' if checkpoint.is_file() else 'not cached; downloads on first separation'})")
    print("Diagnostics do not test live downloads or model inference.")
    return 0 if shutil.which("ffmpeg") and all(importlib.util.find_spec(n) for n in ("yt_dlp", "demucs", "soundfile")) else 1

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["doctor"]:
        return doctor()
    parser = argparse.ArgumentParser(prog="ptk", description="Download audio and prepare aligned stems for music production.")
    parser.add_argument("source", help="Video URL or local audio file")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("-a", "--audio", action="store_true", help="Download WAV audio (default)")
    modes.add_argument("-v", "--video", action="store_true", help="Download compatible H.264/AAC MP4 video")
    modes.add_argument("-s", "--stems", action="store_true", help="Extract stems from a URL or local audio")
    modes.add_argument("-acca", "--accapella", action="store_true", help="Extract vocals and accompaniment")
    modes.add_argument("-inst", "--instrumental", action="store_true", help="Extract accompaniment and vocals")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path.home() / "Downloads")
    parser.add_argument("-n", "--num-stems", type=int, choices=(2, 4), default=4)
    parser.add_argument("--no-analysis", action="store_true", help="Skip estimated BPM/key metadata")
    parser.add_argument("--analyze", action="store_true", help="Analyze local audio without separation")
    parser.add_argument("--engine", choices=("demucs",), default="demucs")
    parser.add_argument("--device", choices=("cpu", "mps", "cuda"), default="cpu")
    parser.add_argument("--video-quality", choices=("compatible", "best"), default=None,
                        help="With -v: compatible (default) preserves resolution/fps, converts if needed; best copies source streams (container may vary); AV1/VP9 may not import into some editors")
    parser.add_argument("--metadata", action="store_true", help="Save an optional JSON sidecar alongside downloaded media")
    parser.add_argument("--max-duration", type=float, default=3600, help="Maximum media duration in seconds (default: 3600)")
    parser.add_argument("--max-size-mb", type=float, default=2048, help="Maximum media size in MiB (default: 2048)")
    parser.add_argument("--min-free-mb", type=float, default=1024, help="Reserved free disk space in MiB (default: 1024)")
    parser.add_argument("--version", action="version", version=f"PTK {__version__}")
    options = parser.parse_args(argv)
    if options.video_quality is not None and not options.video:
        parser.error("--video-quality requires -v/--video")
    try:
        limits = Limits(options.max_duration, int(options.max_size_mb * 1024**2), int(options.min_free_mb * 1024**2))
        is_url = urlparse(options.source).scheme in ("http", "https")
        if is_url:
            validate_url(options.source)
        local = None if is_url else Path(options.source).expanduser().resolve(strict=True)
        if options.analyze:
            if is_url or options.video or options.stems or options.accapella or options.instrumental:
                parser.error("--analyze takes a local audio file without a separation flag")
            import soundfile as sf
            limits.check_duration(sf.info(str(local)).duration)
            limits.check_size(local.stat().st_size)
            from .analyzer.audio_analyzer import analyze_audio
            bpm, key = analyze_audio(str(local))
            print(json.dumps({"status": "estimated" if bpm is not None and key is not None else "unknown", "bpm": bpm, "key": key}, indent=2))
            return 0
        output = options.output_dir.expanduser().resolve()
        output.mkdir(parents=True, exist_ok=True)
        if options.stems or options.accapella or options.instrumental:
            from .processor.demucs_processor import extract_stems
            if local is None:
                from .downloader.download import download_audio
                print("Downloading source audio…", flush=True)
                local = Path(download_audio(options.source, output, analyze_features=False, metadata=options.metadata, limits=limits))
            stem_output = output / (local.stem + "_stems")
            print(f"Separating stems using {options.device}…", flush=True)
            extract_stems(str(local), str(stem_output),
                          stem_number=2 if options.accapella or options.instrumental else options.num_stems,
                          analyze_features=not options.no_analysis, device=options.device, limits=limits)
            print(f"Stems ready: {stem_output}")
        elif is_url:
            from .downloader.download import download_audio, download_video
            result = download_video(options.source, output, quality=options.video_quality or "compatible", metadata=options.metadata, limits=limits) if options.video else download_audio(options.source, output, analyze_features=False, metadata=options.metadata, limits=limits)
            print(f"Saved: {result}")
        else:
            parser.error("For local audio use -s (stems) or --analyze; the source is never modified.")
        return 0
    except (Exception, KeyboardInterrupt) as error:
        print(f"PTK: {public_message(error)}", file=sys.stderr)
        return 130 if isinstance(error, KeyboardInterrupt) else 1

if __name__ == "__main__":
    raise SystemExit(main())
