"""Exercise the batch entry points with a local, network-free package fixture."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(sys.platform == "win32", "Windows batch scripts require cmd.exe")
class WindowsLauncherTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="PTK batch ! ")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        scripts = self.root / "scripts" / "windows"
        scripts.mkdir(parents=True)
        original = Path(os.environ.get("PTK_SOURCE_ROOT", Path(__file__).resolve().parents[1])) / "scripts" / "windows"
        for name in ("install.bat", "run_toolkit.bat"):
            shutil.copy2(original / name, scripts / name)
        (self.root / "requirements").mkdir()
        (self.root / "requirements" / "windows-amd64-py311.txt").write_text("# test fixture\n")
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(self.root / ".venv")],
                       check=True, capture_output=True)
        package = self.root / "producer_toolkit"
        package.mkdir()
        (package / "__init__.py").touch()
        (package / "__main__.py").write_text(
            "import json, pathlib, sys\n"
            "pathlib.Path('cli-args.json').write_text(json.dumps(sys.argv[1:]))\n"
            "raise SystemExit(23 if '--fail' in sys.argv else 0)\n")
        shutil.copytree(package, self.root / ".venv" / "Lib" / "site-packages" / "producer_toolkit")
        pip = self.root / "pip"
        pip.mkdir()
        (pip / "__init__.py").touch()
        (pip / "__main__.py").write_text(
            "import os, pathlib\n"
            "pathlib.Path('pip-called').touch()\n"
            "raise SystemExit(int(os.environ.get('PTK_TEST_PIP_EXIT', '0')))\n")

    def run_batch(self, name, args="", cwd=None, **environment):
        script = self.root / "scripts" / "windows" / name
        return subprocess.run(
            f'"{os.environ.get("COMSPEC", "cmd.exe")}" /d /s /c ""{script}" {args}"',
            cwd=cwd or self.workspace.name, env=dict(os.environ, **environment),
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)

    def test_launcher_forwards_all_arguments_without_changing_modes(self):
        args = ['https://example.com/watch?v=x&list=y!', '-s', '-n', '2',
                '--no-analysis', '--device', 'cpu', '-o', 'output with spaces!']
        result = self.run_batch("run_toolkit.bat", " ".join(f'"{arg}"' for arg in args))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((self.root / "cli-args.json").read_text()), args)

    def test_launcher_propagates_cli_failure(self):
        result = self.run_batch("run_toolkit.bat", "--fail")
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
        self.assertNotIn("Processing complete", result.stdout)

    def test_launcher_preserves_callers_working_directory(self):
        caller = self.root / "caller directory"
        caller.mkdir()
        result = self.run_batch("run_toolkit.bat", '"relative song.wav" -s', cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((caller / "cli-args.json").read_text()), ["relative song.wav", "-s"])

    def test_installer_does_not_report_success_when_installation_fails(self):
        result = self.run_batch("install.bat", PTK_TEST_PIP_EXIT="37")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "pip-called").exists())
        self.assertFalse((self.root / "cli-args.json").exists())
        self.assertNotIn("Installation completed successfully", result.stdout)

    def test_installer_reuses_environment_and_checks_cli(self):
        sentinel = self.root / ".venv" / "preserve.txt"
        sentinel.write_text("existing environment")
        result = self.run_batch("install.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "pip-called").exists())
        self.assertEqual(sentinel.read_text(), "existing environment")
        self.assertEqual(json.loads((self.root / "cli-args.json").read_text()), ["doctor"])
