"""Resource checks must fail before expensive work and preserve user files."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import io
from contextlib import redirect_stderr
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import soundfile as sf

from producer_toolkit.cli import main
from producer_toolkit.downloader.download import download_audio
from producer_toolkit.processor.demucs_processor import extract_stems
from producer_toolkit import limits as policy


class LimitsTests(unittest.TestCase):
    def test_invalid_limits_and_embedded_url_credentials_are_rejected(self):
        for kwargs in ({'max_duration': 0}, {'max_bytes': -1}, {'reserve_bytes': -1},
                       {'max_duration': float('inf')}, {'max_duration': float('nan')}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                policy.Limits(**kwargs)
        with self.assertRaises(ValueError):
            policy.validate_url('https://user:password@example.com/video')
        with self.assertRaises(ValueError):
            policy.validate_url('https://example.com/\nvideo')
        self.assertEqual(policy.public_url('https://u:p@example.com/video?token=secret#private'),
                         'https://example.com/video')

    def test_download_messages_do_not_repeat_private_url_parameters(self):
        from producer_toolkit.downloader.download import DownloadLogger
        output = io.StringIO()
        with redirect_stderr(output):
            DownloadLogger().error('Failed https://u:p@example.com/video?token=private-token#private')
        self.assertNotIn('private-token', output.getvalue())
        self.assertNotIn('u:p@', output.getvalue())

    def test_local_duration_and_disk_checks_prevent_model_invocation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'tone.wav'
            sf.write(source, np.sin(np.arange(44100) * .1), 44100)
            original = source.read_bytes()
            with patch('producer_toolkit.processor.demucs_processor.subprocess.run') as run:
                with self.assertRaisesRegex(ValueError, 'duration'):
                    extract_stems(source, root / 'output', limits=policy.Limits(max_duration=.5))
                with patch('producer_toolkit.limits.shutil.disk_usage', return_value=SimpleNamespace(free=1)):
                    with self.assertRaisesRegex(OSError, 'space'):
                        extract_stems(source, root / 'output')
                self.assertEqual(run.call_count, 0)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse((root / 'output').exists())

    def test_download_metadata_limit_and_progress_limit_publish_nothing(self):
        for duration, progressive in ((7200, False), (1, True)):
            with self.subTest(duration=duration), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                sentinel = root / 'unrelated.wav'
                sentinel.write_bytes(b'keep')
                def factory(options):
                    d = MagicMock()
                    d.__enter__.return_value = d
                    def extract(url, download):
                        if download and progressive:
                            options['progress_hooks'][0]({'downloaded_bytes': 1024})
                        return {'id': 'example', 'duration': duration}
                    d.extract_info.side_effect = extract
                    return d
                with patch('yt_dlp.YoutubeDL', side_effect=factory):
                    with self.assertRaises(ValueError):
                        download_audio('https://example.com/video', root,
                                       limits=policy.Limits(max_duration=60, max_bytes=100))
                self.assertEqual(list(root.iterdir()), [sentinel])

    def test_cli_passes_limits_and_rejects_credentials_before_downloading(self):
        with tempfile.TemporaryDirectory() as folder, patch(
                'producer_toolkit.downloader.download.download_audio', return_value='file') as download:
            self.assertEqual(main(['https://example.com/video', '-a', '-o', folder,
                                   '--max-duration', '30', '--max-size-mb', '10', '--min-free-mb', '0']), 0)
            limits = download.call_args.kwargs['limits']
            self.assertEqual((limits.max_duration, limits.max_bytes, limits.reserve_bytes), (30, 10*1024*1024, 0))
            download.reset_mock()
            self.assertEqual(main(['https://u:p@example.com/video', '-a', '-o', folder]), 1)
            self.assertEqual(download.call_count, 0)
