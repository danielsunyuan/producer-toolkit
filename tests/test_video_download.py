"""Video selection and real media contracts; no network or copyrighted fixtures."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from producer_toolkit.cli import main
from producer_toolkit.downloader.download import download_video


def media_format(name, video, audio="none", width=3840, height=2160, fps=60, ext="mp4"):
    return dict(format_id=name, vcodec=video, acodec=audio, width=width, height=height,
                fps=fps, ext=ext, url="https://example.com/" + name, protocol="https")


class FormatSelectionTests(unittest.TestCase):
    def select(self, formats, mode="compatible"):
        from producer_toolkit.downloader.video import select_video_formats
        return list(select_video_formats({"formats": formats}, mode))[0]

    def test_compatible_prefers_avc_at_best_resolution_and_fps(self):
        formats = [media_format("aac", "none", "mp4a.40.2", ext="m4a"),
                   media_format("avc", "avc1.640033"), media_format("av1", "av01.0.13M.08")]
        result = self.select(formats)
        self.assertEqual([f["format_id"] for f in result["requested_formats"]], ["avc", "aac"])

    def test_does_not_drop_4k_or_60fps_to_avoid_conversion(self):
        for lower in [dict(width=1920, height=1080, fps=60), dict(fps=30)]:
            formats = [media_format("aac", "none", "mp4a.40.2", ext="m4a"),
                       media_format("avc", "avc1", **lower), media_format("av1", "av01")]
            self.assertEqual(self.select(formats)["requested_formats"][0]["format_id"], "av1")

    def test_best_keeps_top_video_and_audio_without_codec_preference(self):
        formats = [media_format("aac", "none", "mp4a.40.2", ext="m4a"),
                   media_format("opus", "none", "opus", ext="webm"),
                   media_format("avc", "avc1"), media_format("vp9", "vp9", ext="webm")]
        result = self.select(formats, "best")
        self.assertEqual([f["format_id"] for f in result["requested_formats"]], ["vp9", "opus"])
        self.assertEqual(result["ext"], "mkv")

    def test_best_audio_falls_back_to_muxed_when_video_is_silent(self):
        formats = [media_format("muxed", "avc1", "mp4a.40.2", width=1280, height=720),
                   media_format("silent", "av01")]
        result = self.select(formats, "best")
        self.assertEqual([f["format_id"] for f in result["requested_formats"]], ["silent", "muxed"])
        self.assertEqual(result["requested_formats"][1]["vcodec"], "none")

    def test_audio_only_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "video"):
            self.select([media_format("aac", "none", "mp4a.40.2")])

    def test_cli_passes_best_mode_and_rejects_it_without_video(self):
        with tempfile.TemporaryDirectory() as root:
            with patch("producer_toolkit.downloader.download.download_video", return_value="out.mkv") as download:
                self.assertEqual(main(["https://example.com/id", "-v", "--video-quality", "best", "-o", root]), 0)
                self.assertEqual(download.call_args.kwargs["quality"], "best")
            for flags in ([], ["-a"], ["-s"], ["--analyze"]):
                with self.assertRaises(SystemExit) as error:
                    main(["https://example.com/id", *flags, "--video-quality", "best", "-o", root])
                self.assertEqual(error.exception.code, 2)

    def test_cli_metadata_is_opt_in_for_audio_and_video(self):
        with tempfile.TemporaryDirectory() as root:
            for mode, function in (("-a", "download_audio"), ("-v", "download_video")):
                for enabled in (False, True):
                    with self.subTest(mode=mode, enabled=enabled), patch(
                            "producer_toolkit.downloader.download." + function, return_value="media") as download:
                        args = ["https://example.com/video", mode, "-o", root]
                        if enabled:
                            args.append("--metadata")
                        self.assertEqual(main(args), 0)
                        self.assertEqual(download.call_args.kwargs["metadata"], enabled)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and ffprobe required")
class RealVideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory()
        cls.root = Path(cls.workspace.name)
        cls.avc = cls.root / "compatible.mp4"
        cls.vp9 = cls.root / "source.mkv"
        for path, codec, audio in [(cls.avc, "libx264", "aac"), (cls.vp9, "libvpx-vp9", "libopus")]:
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30000/1001",
                            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "0.6",
                            "-c:v", codec, "-c:a", audio, str(path)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.output = tempfile.TemporaryDirectory()
        self.addCleanup(self.output.cleanup)
        self.out = Path(self.output.name)
        self.sentinel = self.out / "unrelated.mp4"
        self.sentinel.write_bytes(b"preserve")

    def download(self, fixture, quality="compatible", output=None, metadata=True):
        import yt_dlp
        real = yt_dlp.YoutubeDL
        with patch("yt_dlp.YoutubeDL", side_effect=lambda opts: real(dict(opts, enable_file_urls=True, noprogress=True))):
            kwargs = {} if metadata is None else {"metadata": metadata}
            return Path(download_video(fixture.as_uri(), output or self.out, quality=quality, **kwargs))

    def probe(self, path):
        from producer_toolkit.downloader.video import probe_video
        return probe_video(path)

    def test_default_downloads_produce_only_media_in_both_modes(self):
        for quality, source in (("compatible", self.avc), ("best", self.vp9)):
            output = self.out / quality
            result = self.download(source, quality, output=output, metadata=None)
            self.assertEqual([f.resolve() for f in output.iterdir()], [result])
            self.assertTrue(result.is_file())

    def test_compatible_streams_are_not_reencoded(self):
        result = self.download(self.avc)
        self.assertEqual(hashlib.sha256(result.read_bytes()).digest(), hashlib.sha256(self.avc.read_bytes()).digest())
        metadata = json.loads(result.with_suffix(".mp4.json").read_text())
        self.assertEqual(metadata["conversion"]["video"], "copy")
        self.assertEqual(metadata["conversion"]["audio"], "copy")
        self.assertEqual(metadata["conversion"]["container"], "unchanged")
        self.assertTrue(metadata["selected_formats"])

    def test_vp9_opus_automatically_converts_preserving_timing(self):
        original = self.vp9.read_bytes()
        result = self.download(self.vp9)
        before, after = self.probe(self.vp9), self.probe(result)
        self.assertEqual(result.suffix, ".mp4")
        self.assertEqual(after["video"]["codec_name"], "h264")
        self.assertEqual(after["audio"]["codec_name"], "aac")
        self.assertEqual((after["video"]["width"], after["video"]["height"]), (160, 90))
        self.assertEqual(after["video"]["avg_frame_rate"], before["video"]["avg_frame_rate"])
        self.assertAlmostEqual(after["duration"], before["duration"], delta=0.1)
        self.assertEqual(self.vp9.read_bytes(), original)
        metadata = json.loads(result.with_suffix(".mp4.json").read_text())
        self.assertEqual(metadata["conversion"]["video"], "libx264")
        self.assertEqual(metadata["conversion"]["audio"], "aac")
        self.assertEqual(metadata["conversion"]["crf"], 18)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(result), "-f", "null", "-"], check=True)
        self.assertEqual(self.sentinel.read_bytes(), b"preserve")
        self.assertFalse(list(self.out.glob(".ptk-*")))

    def test_best_preserves_source_streams_and_container(self):
        result = self.download(self.vp9, "best")
        self.assertEqual(result.suffix, ".mkv")
        self.assertEqual(result.read_bytes(), self.vp9.read_bytes())
        data = json.loads(result.with_suffix(".mkv.json").read_text())
        self.assertEqual(data["video_quality"], "best")
        self.assertEqual(data["output"]["video"]["codec_name"], "vp9")
        self.assertEqual(data["output"]["audio"]["codec_name"], "opus")
        self.assertEqual(data["conversion"]["video"], "copy")

    def test_collisions_preserve_existing_media_and_sidecar(self):
        for quality, fixture in [("compatible", self.avc), ("best", self.vp9)]:
            with self.subTest(quality=quality):
                result = self.download(fixture, quality)
                original = result.read_bytes()
                sidecar = result.with_suffix(result.suffix + ".json")
                old_metadata = sidecar.read_bytes()
                with self.assertRaises(FileExistsError):
                    self.download(fixture, quality)
                self.assertEqual(result.read_bytes(), original)
                self.assertEqual(sidecar.read_bytes(), old_metadata)
                result.unlink()
                with self.assertRaises(FileExistsError):
                    self.download(fixture, quality)
                self.assertFalse(result.exists())
                self.assertEqual(sidecar.read_bytes(), old_metadata)

    def packet_hashes(self, path, stream):
        result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream,
                                 "-show_packets", "-show_data_hash", "sha256", "-of", "json", str(path)],
                                check=True, capture_output=True, text=True)
        return [packet["data_hash"] for packet in json.loads(result.stdout)["packets"]]

    def test_split_stream_downloads_merge_losslessly_in_both_modes(self):
        import yt_dlp
        from yt_dlp.extractor.common import InfoExtractor
        real = yt_dlp.YoutubeDL
        formats = [
            dict(media_format("aac", "none", "mp4a.40.2", ext="mp4"), url=self.avc.as_uri()),
            dict(media_format("audio-opus", "none", "opus", ext="mkv"), url=self.vp9.as_uri()),
            dict(media_format("avc", "avc1.640028"), url=self.avc.as_uri()),
            dict(media_format("vp9", "vp9", ext="mkv"), url=self.vp9.as_uri()),
        ]
        for fmt in formats:
            fmt.update(width=160, height=90, fps=30000/1001, protocol="file")

        class FixtureIE(InfoExtractor):
            _VALID_URL = r"ptk-fixture:video"

            def _real_extract(self, url):
                return dict(id="video", title="split fixture", formats=formats)

        def client(options):
            result = real(dict(options, enable_file_urls=True, noprogress=True), auto_init=False)
            result.add_info_extractor(FixtureIE())
            return result

        for quality in ("compatible", "best"):
            with self.subTest(quality=quality), patch("yt_dlp.YoutubeDL", side_effect=client):
                result = Path(download_video("ptk-fixture:video", self.out / quality, quality=quality, metadata=True))
                metadata = json.loads(result.with_suffix(result.suffix + ".json").read_text())
                expected = ["avc", "aac"] if quality == "compatible" else ["vp9", "audio-opus"]
                self.assertEqual([f["format_id"] for f in metadata["selected_formats"]], expected)
                self.assertEqual(metadata["conversion"]["video"], "copy")
                self.assertEqual(metadata["conversion"]["audio"], "copy")
                self.assertEqual(metadata["download_merge"], {"container": "mkv", "stream_copy": True})
                self.assertEqual(metadata["output"]["video"]["codec_name"], "h264" if quality == "compatible" else "vp9")
                self.assertEqual(metadata["output"]["audio"]["codec_name"], "aac" if quality == "compatible" else "opus")
                original = self.avc if quality == "compatible" else self.vp9
                self.assertEqual(self.packet_hashes(result, "v:0"), self.packet_hashes(original, "v:0"))
                self.assertEqual(self.packet_hashes(result, "a:0"), self.packet_hashes(original, "a:0"))

    def test_h264_444_is_converted_for_editor_compatibility(self):
        from producer_toolkit.downloader.video import prepare_video
        source = self.out / "h264-444.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(self.avc), "-c:v", "libx264",
                        "-pix_fmt", "yuv444p", "-c:a", "copy", str(source)], check=True)
        output, metadata = prepare_video(source, "compatible")
        self.assertEqual(metadata["output"]["video"]["pix_fmt"], "yuv420p")
        self.assertEqual(metadata["conversion"]["video"], "libx264")
        self.assertEqual(metadata["conversion"]["audio"], "copy")
        best, _ = prepare_video(source, "best")
        self.assertEqual(best, source)
        self.assertNotEqual(output, source)

    def test_only_incompatible_stream_is_encoded(self):
        from producer_toolkit.downloader.video import prepare_video
        for video, audio in [("libvpx-vp9", "aac"), ("libx264", "libopus"), ("libx264", "aac")]:
            with self.subTest(video=video, audio=audio):
                fixture = self.out / (video + audio + ".mkv")
                subprocess.run(["ffmpeg", "-v", "error", "-i", str(self.avc),
                                "-c:v", video, "-c:a", audio, str(fixture)], check=True)
                output, metadata = prepare_video(fixture, "compatible")
                self.assertEqual(metadata["conversion"]["video"], "copy" if video == "libx264" else "libx264")
                self.assertEqual(metadata["conversion"]["audio"], "copy" if audio == "aac" else "aac")
                self.assertEqual(self.probe(output)["audio"]["codec_name"], "aac")

    def test_conversion_failure_publishes_nothing(self):
        from producer_toolkit.downloader.video import prepare_video
        with patch("producer_toolkit.downloader.download.prepare_video", side_effect=RuntimeError("conversion failed")):
            with self.assertRaisesRegex(RuntimeError, "conversion failed"):
                self.download(self.vp9)
        self.assertEqual(list(self.out.iterdir()), [self.sentinel])
        self.assertTrue(callable(prepare_video))

    def test_playlist_rejected_before_downloading_in_both_modes(self):
        for quality in ("compatible", "best"):
            with patch("yt_dlp.YoutubeDL") as factory:
                client = factory.return_value.__enter__.return_value
                client.extract_info.return_value = {"_type": "playlist", "entries": []}
                with self.assertRaises(ValueError):
                    download_video("https://example.com/playlist", self.out, quality=quality)
                self.assertTrue(all(not c.kwargs.get("download") for c in client.extract_info.call_args_list))
