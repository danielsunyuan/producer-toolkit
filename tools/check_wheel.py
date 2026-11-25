"""Verify release wheels contain PTK code and notices, without private fixtures."""
from pathlib import Path
import sys
import zipfile

wheels = list(Path(sys.argv[1] if len(sys.argv) > 1 else 'dist').glob('*.whl'))
assert wheels, 'No wheel was built'
for wheel in wheels:
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert names and any(name.endswith('/LICENSE') for name in names), 'MIT licence missing from wheel'
        assert not any(name.startswith(('tests/', '.runtime/', '.venv/'))
                       or name.endswith(('.wav', '.mp3', '.mp4', '.pem', '.key')) for name in names)
        print(f'Checked {wheel.name}: code and notices only.')
