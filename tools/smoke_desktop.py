"""Exercise a real desktop analysis job on generated audio; optionally hold for visual review."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time
import tkinter as tk

import numpy as np
import soundfile as sf
from producer_toolkit.desktop import Desktop
from producer_toolkit.limits import public_message

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--hold', type=int, default=0, help='Seconds to hold a completed window open for visual review')
args = parser.parse_args()
passed = False
with tempfile.TemporaryDirectory(prefix='ptk-desktop-smoke-') as folder:
    source = Path(folder) / 'generated audio.wav'
    sf.write(source, np.sin(np.arange(44100) * .1) * .1, 44100)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    root = tk.Tk()
    root.geometry('850x650')
    window = Desktop(root)
    window.source.set(str(source))
    window.operation.set('Analyze local audio')
    window.output.set(str(Path(folder) / 'output'))
    started = time.monotonic()
    root.after(150, window.run)
    def finish():
        global passed
        if not window.busy and time.monotonic() - started > 1:
            passed = window.status.get() == 'Finished' and hashlib.sha256(source.read_bytes()).hexdigest() == before
            print(json.dumps({'desktop_status': window.status.get(), 'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == before}), flush=True)
            if not passed:
                print(public_message(window.log.get('1.0', 'end')), flush=True)
            root.after(max(0, args.hold) * 1000, window.close)
        elif time.monotonic() - started > 180:
            print('Desktop smoke timed out', flush=True)
            root.destroy()
        else:
            root.after(100, finish)
    root.after(300, finish)
    root.mainloop()
raise SystemExit(0 if passed else 1)
