"""Opt-in real CPU inference on generated audio; no music-quality claim."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import numpy as np
import soundfile as sf
from producer_toolkit.runtime import process_environment
from producer_toolkit.limits import public_message

results = []
with tempfile.TemporaryDirectory(prefix='ptk-model-smoke-') as folder:
    root = Path(folder)
    source = root / 'generated tone with spaces.wav'
    t = np.arange(44100) / 44100
    wave = .15 * np.sin(2*np.pi*440*t) + .05 * np.sin(2*np.pi*880*t)
    sf.write(source, np.column_stack([wave, wave]), 44100, subtype='PCM_24')
    original = hashlib.sha256(source.read_bytes()).hexdigest()
    for count in (2, 4):
        output = root / f'output {count}'
        command = [sys.executable, '-m', 'producer_toolkit', str(source), '-s', '-n', str(count),
                   '--no-analysis', '-o', str(output)]
        started = time.monotonic()
        log = root / f'{count}.log'
        with log.open('w', encoding='utf-8') as stream:
            result = subprocess.run(command, cwd=root, env=process_environment(),
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=600)
        if result.returncode:
            print(public_message(log.read_text(encoding='utf-8', errors='replace')[-5000:]))
            raise SystemExit(result.returncode)
        stems = output / (source.stem + '_stems')
        names = ['vocals', 'no_vocals'] if count == 2 else ['vocals', 'drums', 'bass', 'other']
        for name in names:
            samples, rate = sf.read(stems / (name + '.wav'), always_2d=True)
            assert samples.shape == (44100, 2) and rate == 44100 and np.isfinite(samples).all()
        assert (stems / 'manifest.json').is_file()
        assert not (stems / '.ptk-lock').exists()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == original
        results.append({'stems': count, 'seconds': round(time.monotonic()-started, 2),
                        'decoded_aligned_finite': True, 'source_unchanged': True})
        print(json.dumps(results[-1]), flush=True)
print('Real CPU model smoke passed; generated fixture only.')
