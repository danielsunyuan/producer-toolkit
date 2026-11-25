"""Separate in job-owned storage and publish only complete, verified stems."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from .. import __version__
from ..files import publish

def extract_stems(audio_path, output_dir, stem_number=4, models_dir=None,
                  analyze_features=True, device="cpu"):
    import soundfile as sf
    import numpy as np
    if stem_number not in (2, 4):
        raise ValueError("Demucs supports 2 or 4 stems.")
    source = Path(audio_path).expanduser().resolve(strict=True)
    original = sf.info(str(source))
    if original.frames == 0:
        raise ValueError("Input audio is empty.")
    first = None
    varying = False
    for block in sf.blocks(str(source), blocksize=65536, dtype="float64", always_2d=True):
        if not np.isfinite(block).all():
            raise ValueError("Input audio contains non-finite samples.")
        mono = block.mean(axis=1)
        if first is None:
            first = mono[0]
        varying = varying or bool(np.any(mono != first))
    if not varying:
        raise ValueError("Input audio is silent or constant after mixing to mono; separation needs a varying signal.")
    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    names = ["vocals", "no_vocals"] if stem_number == 2 else ["vocals", "drums", "bass", "other"]
    targets = [destination / (name + ".wav") for name in names] + [destination / "manifest.json"]
    if any(path.exists() for path in targets):
        raise FileExistsError("Stem outputs already exist. Choose another output directory.")
    with tempfile.TemporaryDirectory(prefix=".ptk-stems-", dir=destination) as job:
        command = [sys.executable, "-m", "demucs.separate", "-n", "htdemucs",
                   "--device", device, "--float32", "-o", job]
        if stem_number == 2:
            command += ["--two-stems", "vocals"]
        command.append(str(source))
        environment = os.environ.copy()
        if models_dir:
            environment["TORCH_HOME"] = str(Path(models_dir).expanduser().resolve())
        subprocess.run(command, check=True, env=environment)
        generated = Path(job) / "htdemucs" / source.stem
        reference = None
        for name in names:
            metadata = sf.info(str(generated / (name + ".wav")))
            if metadata.frames == 0 or abs(metadata.duration - original.duration) > 0.05:
                raise RuntimeError(f"Stem is empty or has wrong duration: {name}")
            signature = (metadata.frames, metadata.samplerate, metadata.channels)
            if reference is not None and signature != reference:
                raise RuntimeError("Stem lengths, sample rates or channel counts do not match.")
            reference = signature
        analysis = {"status": "disabled", "bpm": None, "key": None}
        if analyze_features:
            try:
                from ..analyzer.audio_analyzer import analyze_audio
                bpm, key = analyze_audio(str(source))
                analysis = {"status": "estimated" if bpm is not None and key is not None else "unknown", "bpm": bpm, "key": key}
            except Exception as error:
                analysis = {"status": "unknown", "bpm": None, "key": None, "error": str(error)}
        manifest = {
            "schema_version": 1, "ptk_version": __version__, "source": str(source),
            "engine": "demucs", "model": "htdemucs", "device": device,
            "analysis": analysis, "artifacts": [name + ".wav" for name in names],
            "frames": reference[0], "sample_rate": reference[1], "channels": reference[2],
        }
        (generated / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        created = []
        try:
            for target in targets:
                created.append(publish(generated / target.name, target))
        except BaseException:
            for path in created:
                Path(path).unlink(missing_ok=True)
            raise
    return str(destination)
