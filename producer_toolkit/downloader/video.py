"""Video stream selection and codec-aware MP4 preparation."""
import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from ..limits import Limits
from ..runtime import process_environment


def select_video_formats(context, quality="compatible"):
    # yt-dlp supplies formats in ascending preference order. Keep its quality
    # ranking within the highest resolution/frame-rate tier.
    formats = [f for f in context["formats"] if not f.get("has_drm")]
    videos = [f for f in formats if f.get("vcodec") != "none"]
    if not videos:
        raise ValueError("Source has no downloadable video stream.")
    dimensions = lambda f: (f.get("height") or 0, f.get("width") or 0, f.get("fps") or 0)
    best = max(videos, key=lambda f: (dimensions(f), formats.index(f)))
    if quality == "compatible":
        compatible = [f for f in videos if dimensions(f) == dimensions(best)
                      and str(f.get("vcodec")).startswith(("avc1", "avc3", "h264"))]
        if compatible:
            best = compatible[-1]
    audios = [f for f in formats if f.get("acodec") != "none"]
    audio_only = [f for f in audios if f.get("vcodec") == "none"]
    candidates = audio_only or audios
    if quality == "compatible":
        aac = [f for f in candidates if str(f.get("acodec")).startswith(("mp4a", "aac"))]
        candidates = aac or candidates
    audio = candidates[-1] if candidates else None
    if audio is None or audio is best:
        yield best
        return
    # A muxed format may supply only the selected video or audio. Mark the
    # unused stream absent so yt-dlp's stream-copy merger maps exactly one pair.
    video_stream = dict(best, acodec="none")
    audio_stream = dict(audio, vcodec="none")
    yield {
        "format_id": f'{best["format_id"]}+{audio["format_id"]}',
        "ext": "mkv", "requested_formats": [video_stream, audio_stream],
        "protocol": f'{best["protocol"]}+{audio["protocol"]}',
        "vcodec": best["vcodec"], "acodec": audio["acodec"],
        "width": best.get("width"), "height": best.get("height"), "fps": best.get("fps"),
    }


def probe_video(path):
    executable = shutil.which("ffprobe")
    if not executable:
        raise RuntimeError("ffprobe is missing; install the full FFmpeg package.")
    result = subprocess.run([executable, "-v", "error", "-show_streams", "-show_format",
                             "-of", "json", str(path)], check=True, capture_output=True, text=True, env=process_environment())
    data = json.loads(result.stdout)
    videos = [s for s in data["streams"] if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic")]
    audios = [s for s in data["streams"] if s.get("codec_type") == "audio"]
    if not videos:
        raise RuntimeError("Downloaded media contains no video stream.")
    video_fields = ("codec_name", "profile", "pix_fmt", "width", "height", "avg_frame_rate",
                    "r_frame_rate", "duration", "color_transfer", "color_primaries", "color_space")
    audio_fields = ("codec_name", "sample_rate", "channels", "channel_layout", "duration")
    return {
        "container": data["format"]["format_name"],
        "duration": float(data["format"]["duration"]),
        "video": {k: videos[0][k] for k in video_fields if k in videos[0]},
        "audio": {k: audios[0][k] for k in audio_fields if k in audios[0]} if audios else None,
    }


def prepare_video(source, quality, limits=None):
    source = Path(source)
    limits = limits or Limits()
    before = probe_video(source)
    limits.check_duration(before["duration"])
    limits.check_size(source.stat().st_size)
    video_copy = before["video"]["codec_name"] == "h264" and before["video"].get("pix_fmt") == "yuv420p"
    audio_copy = not before["audio"] or before["audio"]["codec_name"] == "aac"
    conversion = {"video": "copy", "audio": "copy" if before["audio"] else "absent",
                  "container": "unchanged"}
    if quality == "best":
        return source, {"input": before, "output": before, "conversion": conversion}
    if video_copy and audio_copy and source.suffix.lower() == ".mp4" and "mp4" in before["container"]:
        return source, {"input": before, "output": before, "conversion": conversion}
    limits.check_disk(source.parent, required=source.stat().st_size * 2)
    destination = source.parent / (source.stem + ".compatible.mp4")
    command = [shutil.which("ffmpeg"), "-nostdin", "-v", "error", "-n", "-i", str(source),
               "-map", "0:v:0", "-map", "0:a:0?", "-map_metadata", "0"]
    command += ["-c:v", "copy"] if video_copy else [
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough"]
    command += ["-c:a", "copy"] if audio_copy else ["-c:a", "aac", "-b:a", "320k"]
    command += ["-movflags", "+faststart", str(destination)]
    subprocess.run(command, check=True, env=process_environment())
    limits.check_size(destination.stat().st_size)
    after = probe_video(destination)
    if after["video"]["codec_name"] != "h264" or (after["audio"] and after["audio"]["codec_name"] != "aac"):
        raise RuntimeError("Conversion did not produce H.264/AAC video.")
    if any(before["video"].get(k) != after["video"].get(k) for k in ("width", "height")):
        raise RuntimeError("Conversion changed the video resolution.")
    old_rate = Fraction(before["video"].get("avg_frame_rate", "0/1"))
    new_rate = Fraction(after["video"].get("avg_frame_rate", "0/1"))
    if abs(float(old_rate - new_rate)) > max(0.05, float(old_rate) * 0.001):
        raise RuntimeError("Conversion changed the video frame rate.")
    if abs(before["duration"] - after["duration"]) > 0.25 or bool(before["audio"]) != bool(after["audio"]):
        raise RuntimeError("Conversion changed the duration or lost audio.")
    conversion.update(video="copy" if video_copy else "libx264",
                      audio=("copy" if audio_copy else "aac") if before["audio"] else "absent",
                      container="remux" if video_copy and audio_copy else "mp4")
    if not video_copy:
        conversion.update(crf=18, preset="slow", pixel_format="yuv420p", frame_rate="passthrough")
    if not audio_copy:
        conversion["audio_bitrate"] = "320k"
    return destination, {"input": before, "output": after, "conversion": conversion}
