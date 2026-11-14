#!/bin/zsh
# Run in your normal terminal to activate this fixed checkout for future shells.
PTK_INSTALL_ROOT=${0:A:h}
python3 - "$PTK_INSTALL_ROOT" <<'PY'
from pathlib import Path
import datetime
import shlex
import shutil
import sys
root = Path(sys.argv[1]).resolve()
profile = Path.home() / ".zshrc"
line = "source " + shlex.quote(str(root / "activate.sh"))
old = profile.read_text() if profile.exists() else ""
if line not in old.splitlines():
    if profile.exists():
        backup = profile.with_name(".zshrc.ptk-backup-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        shutil.copy2(profile, backup)
        print("Shell profile backup:", backup)
    with profile.open("a") as stream:
        stream.write("\n# Producer Toolkit: maintained ptk, u and pt commands\n" + line + "\n")
print("PTK is enabled for new Terminal windows.")
print("For this terminal, run: " + line)
PY
result=$?
if [ "$result" -eq 0 ]; then
    source "$PTK_INSTALL_ROOT/activate.sh"
    ptk doctor
fi
read '?Press Return to close…'
exit "$result"
