"""Offline regression tests for file ownership, real output contracts and CLI failures."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf
from producer_toolkit.cli import main
from producer_toolkit.files import publish
from producer_toolkit.downloader.download import download_audio
from producer_toolkit.processor.demucs_processor import extract_stems

class SafeWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.source = self.root / "input.wav"
        sf.write(str(self.source), np.zeros((4410, 2)), 44100)
        self.original = self.source.read_bytes()
        self.output = self.root / "outputs"
        self.output.mkdir()
        self.sentinel = self.output / "unrelated.wav"
        self.sentinel.write_bytes(b"never delete me")

    def assert_preserved(self):
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(self.sentinel.read_bytes(), b"never delete me")
        self.assertFalse(list(self.output.glob(".ptk-*")))

    def fake_demucs(self, command, **kwargs):
        job = Path(command[command.index("-o") + 1])
        destination = job / "htdemucs" / self.source.stem
        destination.mkdir(parents=True)
        names = ("vocals", "no_vocals") if "--two-stems" in command else ("vocals", "drums", "bass", "other")
        for name in names:
            sf.write(str(destination / (name + ".wav")), np.zeros((4410, 2)), 44100)
        return subprocess.CompletedProcess(command, 0)

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run")
    def test_complete_stems_and_metadata(self, run):
        run.side_effect = self.fake_demucs
        extract_stems(self.source, self.output, analyze_features=False)
        self.assertEqual(len(list(self.output.glob("*.wav"))), 5)
        self.assertEqual(json.loads((self.output / "manifest.json").read_text())["analysis"]["status"], "disabled")
        self.assertIn("-m", run.call_args.args[0])
        self.assert_preserved()

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run")
    def test_two_stems(self, run):
        run.side_effect = self.fake_demucs
        extract_stems(self.source, self.output, stem_number=2, analyze_features=False)
        self.assertTrue((self.output / "no_vocals.wav").is_file())
        self.assertFalse((self.output / "drums.wav").exists())
        self.assert_preserved()

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run")
    def test_missing_stem_does_not_publish_partial_outputs(self, run):
        def incomplete(command, **kwargs):
            self.fake_demucs(command, **kwargs)
            job = Path(command[command.index("-o") + 1])
            (job / "htdemucs" / "input" / "bass.wav").unlink()
        run.side_effect = incomplete
        with self.assertRaises(Exception):
            extract_stems(self.source, self.output, analyze_features=False)
        self.assertEqual(list(self.output.iterdir()), [self.sentinel])
        self.assert_preserved()

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run")
    def test_wrong_duration_rejected(self, run):
        def wrong(command, **kwargs):
            self.fake_demucs(command, **kwargs)
            job = Path(command[command.index("-o") + 1])
            sf.write(str(job / "htdemucs/input/bass.wav"), np.zeros((44100, 2)), 44100)
        run.side_effect = wrong
        with self.assertRaises(RuntimeError):
            extract_stems(self.source, self.output, analyze_features=False)
        self.assert_preserved()
        self.assertEqual(list(self.output.iterdir()), [self.sentinel])

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run", side_effect=subprocess.CalledProcessError(1, "demucs"))
    def test_failed_subprocess_preserves_files(self, run):
        with self.assertRaises(subprocess.CalledProcessError):
            extract_stems(self.source, self.output, analyze_features=False)
        self.assert_preserved()

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run")
    def test_existing_stem_prevents_inference_and_overwrite(self, run):
        (self.output / "vocals.wav").write_bytes(b"existing")
        with self.assertRaises(FileExistsError):
            extract_stems(self.source, self.output)
        run.assert_not_called()
        self.assertEqual((self.output / "vocals.wav").read_bytes(), b"existing")
        self.assert_preserved()

    def test_publish_never_clobbers(self):
        with self.assertRaises(FileExistsError):
            publish(self.source, self.sentinel)
        self.assert_preserved()

    @patch("yt_dlp.YoutubeDL")
    def test_download_uses_sanitized_filename_not_raw_title(self, factory):
        def make_downloader(options):
            from unittest.mock import MagicMock
            downloader = MagicMock()
            downloader.__enter__.return_value = downloader
            produced = Path(options["outtmpl"]).parent / "sanitized [id].m4a"
            def extract(url, download):
                if download:
                    sf.write(str(produced.with_suffix(".wav")), np.zeros((4410, 2)), 44100, subtype="PCM_24")
                return {"title": "raw/title:unsafe?", "id": "id"}
            downloader.extract_info.side_effect = extract
            downloader.prepare_filename.return_value = str(produced)
            return downloader
        factory.side_effect = make_downloader
        result = Path(download_audio("https://example.com/video", self.output))
        self.assertEqual(result.name, "sanitized [id].wav")
        self.assertTrue(result.with_suffix(".wav.json").is_file())
        self.assert_preserved()

    @patch("yt_dlp.YoutubeDL")
    def test_playlist_rejected_before_download(self, factory):
        downloader = factory.return_value.__enter__.return_value
        downloader.extract_info.return_value = {"_type": "playlist", "entries": []}
        with self.assertRaises(ValueError):
            download_audio("https://example.com/playlist", self.output)
        self.assertTrue(all(not call.kwargs.get("download") for call in downloader.extract_info.call_args_list))
        self.assert_preserved()

    def test_unknown_flags_and_conflicting_modes_fail(self):
        for args in ([str(self.source), "-t"], [str(self.source), "-a", "-s"]):
            with self.assertRaises(SystemExit) as raised:
                main(args)
            self.assertEqual(raised.exception.code, 2)

    def test_missing_source_returns_failure(self):
        self.assertEqual(main([str(self.root / "missing.wav"), "-s"]), 1)
        self.assert_preserved()

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg required for real conversion smoke test")
    def test_real_yt_dlp_and_ffmpeg_conversion(self):
        import yt_dlp
        fixture = self.root / "mono-48khz.m4a"
        subprocess.run([shutil.which("ffmpeg"), "-loglevel", "error", "-i", str(self.source),
                        "-ar", "48000", "-ac", "1", "-c:a", "aac", str(fixture)], check=True)
        real = yt_dlp.YoutubeDL
        with patch("yt_dlp.YoutubeDL", side_effect=lambda opts: real(dict(opts, enable_file_urls=True, noprogress=True))):
            result = download_audio(fixture.as_uri(), self.output)
        metadata = sf.info(result)
        self.assertEqual((metadata.samplerate, metadata.channels, metadata.subtype), (44100, 2, "PCM_24"))
        self.assert_preserved()

    def test_silence_does_not_invent_tempo_or_key(self):
        from producer_toolkit.analyzer.audio_analyzer import analyze_audio
        self.assertEqual(analyze_audio(str(self.source)), (None, None))

    @patch("producer_toolkit.processor.demucs_processor.subprocess.run")
    def test_publish_collision_rolls_back_only_current_job(self, run):
        run.side_effect = self.fake_demucs
        def collision(source, destination):
            if Path(destination).name == "drums.wav":
                Path(destination).write_bytes(b"another job owns this")
            return publish(source, destination)
        with patch("producer_toolkit.processor.demucs_processor.publish", side_effect=collision):
            with self.assertRaises(FileExistsError):
                extract_stems(self.source, self.output, analyze_features=False)
        self.assertFalse((self.output / "vocals.wav").exists())
        self.assertEqual((self.output / "drums.wav").read_bytes(), b"another job owns this")
        self.assert_preserved()
