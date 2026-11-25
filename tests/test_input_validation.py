"""Reject inputs Demucs cannot normalize, without touching user files."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import soundfile as sf

from producer_toolkit.cli import main
from producer_toolkit.processor.demucs_processor import extract_stems


class InputValidationTests(unittest.TestCase):
    def test_silent_constant_cancelled_and_nonfinite_inputs_never_start_model(self):
        tone = np.sin(np.arange(4410) * 0.1)
        fixtures = {
            'silence': np.zeros((4410, 2)),
            'constant': np.full((4410, 2), 0.2),
            'cancelled': np.column_stack([tone, -tone]),
            'nan': np.full((4410, 2), np.nan),
            'infinite': np.full((4410, 2), np.inf),
        }
        for name, samples in fixtures.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                source = root / 'input.wav'
                sf.write(source, samples, 44100, subtype='FLOAT')
                original = source.read_bytes()
                output = root / 'output'
                output.mkdir()
                sentinel = output / 'unrelated.txt'
                sentinel.write_text('preserve')
                with patch('producer_toolkit.processor.demucs_processor.subprocess.run') as run:
                    with self.assertRaisesRegex(ValueError, 'silent|constant|finite'):
                        extract_stems(source, output, analyze_features=False)
                    self.assertEqual(run.call_count, 0, 'Invalid input must not start Demucs')
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(list(output.iterdir()), [sentinel])

    def test_very_quiet_varying_audio_is_not_treated_as_silence(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'quiet.wav'
            sf.write(source, np.sin(np.arange(4410) * 0.1) * 1e-12, 44100, subtype='FLOAT')
            with patch('producer_toolkit.processor.demucs_processor.subprocess.run',
                       side_effect=RuntimeError('model reached')) as run:
                with self.assertRaisesRegex(RuntimeError, 'model reached'):
                    extract_stems(source, Path(folder) / 'output', analyze_features=False)
                run.assert_called_once()

    def test_cli_reports_silence_as_failure_without_creating_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'silence.wav'
            sf.write(source, np.zeros((4410, 2)), 44100)
            with patch('producer_toolkit.processor.demucs_processor.subprocess.run') as run:
                self.assertEqual(main([str(source), '-s', '-o', str(root / 'output')]), 1)
                self.assertEqual(run.call_count, 0, 'Invalid input must not start Demucs')
            self.assertFalse(any((root / 'output').iterdir()))
