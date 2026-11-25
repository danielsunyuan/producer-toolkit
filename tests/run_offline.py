"""Run the complete offline suite, optionally against an installed wheel."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

MODULES = [
    'tests.test_safe_workflow', 'tests.test_audio_analyzer', 'tests.test_video_download',
    'tests.test_input_validation', 'tests.test_packaging', 'tests.test_publication',
    'tests.test_limits', 'tests.test_windows_launchers',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed', action='store_true', help='Copy tests outside the checkout to test site-packages')
    options = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    allowed = {
        'PATH', 'HOME', 'USERPROFILE', 'SYSTEMROOT', 'SYSTEMDRIVE', 'WINDIR', 'COMSPEC',
        'PATHEXT', 'TEMP', 'TMP', 'TMPDIR', 'HOMEDRIVE', 'HOMEPATH', 'APPDATA', 'LOCALAPPDATA',
        'PROGRAMDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)', 'NUMBER_OF_PROCESSORS',
        'PROCESSOR_ARCHITECTURE', 'LANG', 'LC_ALL', 'DISPLAY', 'XAUTHORITY',
        'TORCH_HOME', 'NUMBA_CACHE_DIR', 'MPLCONFIGDIR', 'SSL_CERT_FILE',
    }
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    environment.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PTK_SOURCE_ROOT=str(source))
    command = [sys.executable, '-m', 'unittest', *MODULES, '-v']
    if not options.installed:
        return subprocess.run(command, cwd=source, env=environment).returncode
    with tempfile.TemporaryDirectory(prefix='ptk-installed-tests-') as folder:
        root = Path(folder)
        shutil.copytree(source / 'tests', root / 'tests', ignore=shutil.ignore_patterns('resources', '__pycache__'))
        check = subprocess.run([sys.executable, '-c',
            "import pathlib,producer_toolkit; p=pathlib.Path(producer_toolkit.__file__).resolve(); "
            "assert 'site-packages' in p.parts, p; print('Installed package:',p)"], cwd=root, env=environment)
        if check.returncode:
            return check.returncode
        return subprocess.run(command, cwd=root, env=environment).returncode


if __name__ == '__main__':
    raise SystemExit(main())
