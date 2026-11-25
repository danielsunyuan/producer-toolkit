"""The desktop interface delegates to the canonical CLI without a shell."""
from pathlib import Path
import sys
import tempfile
import time
import unittest

from producer_toolkit.desktop import Desktop, OPERATIONS, command_for


class DesktopCommandTests(unittest.TestCase):
    def test_every_operation_builds_a_canonical_cli_command(self):
        for operation in OPERATIONS:
            command = command_for('song & reference!.wav', operation, 'output with spaces', metadata=True, analyze=False)
            self.assertEqual(command[:4], [sys.executable, '-m', 'producer_toolkit', 'song & reference!.wav'])
            self.assertTrue(all(isinstance(value, str) for value in command))
        stems = command_for('song.wav', 'Vocals + accompaniment', 'output', analyze=False)
        self.assertIn('--no-analysis', stems)
        self.assertEqual(stems[stems.index('-n') + 1], '2')

    def test_empty_input_or_unknown_operation_does_not_start_a_job(self):
        for source, operation, output in [('', 'Four stems', 'output'), ('file', 'unknown', 'output'),
                                          ('file', 'Four stems', '')]:
            with self.assertRaises(ValueError):
                command_for(source, operation, output)


class DesktopWindowTests(unittest.TestCase):
    def setUp(self):
        try:
            import tkinter as tk
            self.root = tk.Tk()
            self.root.withdraw()
        except (ImportError, RuntimeError) as error:
            self.skipTest(f'Tk/display unavailable: {type(error).__name__}')
        except Exception as error:
            if type(error).__name__ == 'TclError':
                self.skipTest('Tk/display unavailable')
            raise
        self.window = Desktop(self.root)
        def cleanup():
            self.window.busy = False  # Never open a modal dialog when a test times out.
            self.window.close()
        self.addCleanup(cleanup)

    def test_real_cli_failure_returns_window_to_ready_state(self):
        with tempfile.TemporaryDirectory() as folder:
            self.window.source.set(str(Path(folder) / 'missing.wav'))
            self.window.output.set(str(Path(folder) / 'output'))
            self.window.run()
            self.assertTrue(self.window.busy)
            deadline = time.monotonic() + 20
            while self.window.busy and time.monotonic() < deadline:
                self.root.update()
                time.sleep(.02)
            self.assertFalse(self.window.busy, 'Desktop worker did not finish')
            self.assertEqual(str(self.window.run_button['state']), 'normal')
            self.assertIn('Failed', self.window.status.get())
            self.assertIn('PTK:', self.window.log.get('1.0', 'end'))

class ChildEnvironmentTests(unittest.TestCase):
    def test_workers_do_not_inherit_unrelated_service_credentials(self):
        import os
        from unittest.mock import patch
        from producer_toolkit.runtime import process_environment
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'fixture-only', 'GITHUB_TOKEN': 'fixture-only',
                                      'NOTION_API_KEY': 'fixture-only', 'TORCH_HOME': 'model-cache'}):
            environment = process_environment()
        self.assertTrue(set(environment).isdisjoint({'OPENAI_API_KEY', 'GITHUB_TOKEN', 'NOTION_API_KEY'}),
                        'Service credentials must not be forwarded to media workers')
        self.assertEqual(environment['TORCH_HOME'], 'model-cache')
