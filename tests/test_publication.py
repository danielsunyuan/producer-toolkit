"""Publication must never expose a partially copied final artifact."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from producer_toolkit import files


class PublicationTests(unittest.TestCase):
    def test_partial_copy_is_private_and_interrupt_removes_only_own_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'source'
            source.write_bytes(b'complete audio')
            destination = root / 'final.wav'
            sentinel = root / 'unrelated.wav'
            sentinel.write_bytes(b'keep')
            def interrupted(incoming, target):
                target.write(b'partial')
                target.flush()
                self.assertFalse(destination.exists(), 'A partial copy must not have the final name')
                raise KeyboardInterrupt()
            with patch('producer_toolkit.files.shutil.copyfileobj', side_effect=interrupted):
                with self.assertRaises(KeyboardInterrupt):
                    files.publish(source, destination)
            self.assertFalse(destination.exists())
            self.assertEqual(sentinel.read_bytes(), b'keep')
            self.assertEqual(source.read_bytes(), b'complete audio')
            self.assertFalse(list(root.glob('.ptk-*')))

    def test_concurrent_publish_has_one_complete_winner(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sources = [root / 'one', root / 'two']
            for i, source in enumerate(sources):
                source.write_bytes(bytes([i + 1]) * 1024 * 1024)
            destination = root / 'final.wav'
            def publish(source):
                try:
                    files.publish(source, destination)
                    return True
                except FileExistsError:
                    return False
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(publish, sources))
            self.assertEqual(sum(results), 1)
            self.assertIn(destination.read_bytes(), [p.read_bytes() for p in sources])
            self.assertFalse(list(root.glob('.ptk-*')))

    def test_process_killed_during_copy_leaves_no_partial_final_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'source'
            source.write_bytes(b'complete')
            destination = root / 'final.wav'
            marker = root / 'copy-started'
            code = f'''
from pathlib import Path
import time
from unittest.mock import patch
from producer_toolkit.files import publish

def copy(incoming, target):
    target.write(b'partial')
    target.flush()
    Path({str(marker)!r}).touch()
    time.sleep(60)

with patch('producer_toolkit.files.shutil.copyfileobj', side_effect=copy):
    publish({str(source)!r}, {str(destination)!r})
'''
            process = subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
            try:
                deadline = time.monotonic() + 15
                while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(marker.exists(), 'Child copy did not start')
                self.assertFalse(destination.exists(), 'Abrupt termination could leave a partial final file')
            finally:
                process.kill()
                process.wait(timeout=10)
            self.assertFalse(destination.exists())
            self.assertEqual(source.read_bytes(), b'complete')

    def test_output_lock_blocks_another_job_and_is_removed_on_interrupt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sentinel = root / 'unrelated'
            sentinel.write_text('keep')
            with self.assertRaises(KeyboardInterrupt):
                with files.output_lock(root):
                    with self.assertRaisesRegex(FileExistsError, 'locked'):
                        with files.output_lock(root):
                            self.fail('A second job acquired the same output')
                    raise KeyboardInterrupt()
            self.assertEqual(list(root.iterdir()), [sentinel])

    def test_existing_lock_is_preserved_for_manual_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = Path(folder) / '.ptk-lock'
            lock.mkdir()
            owner = lock / 'owner.json'
            owner.write_text('existing job')
            with self.assertRaises(FileExistsError):
                with files.output_lock(folder):
                    self.fail('Must not steal an existing lock')
            self.assertEqual(owner.read_text(), 'existing job')
