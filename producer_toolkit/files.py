"""Publish artifacts without replacing existing user files."""
import shutil
import os
import tempfile
import json
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def output_lock(directory):
    """Serialize PTK stem jobs; never steal a possibly active or stale lock."""
    lock = Path(directory) / ".ptk-lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise FileExistsError("Output is locked by another or interrupted PTK job. Choose a new output folder.") from None
    owner = lock / "owner.json"
    try:
        owner.write_text(json.dumps({"pid": os.getpid(), "started": time.time()}))
        yield
    finally:
        owner.unlink(missing_ok=True)
        lock.rmdir()

def publish(source, destination):
    destination = Path(destination)
    stage = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".ptk-publish-",
                                         dir=destination.parent, delete=False) as target:
            stage = Path(target.name)
            with Path(source).open("rb") as incoming:
                shutil.copyfileobj(incoming, target)
            target.flush()
            os.fsync(target.fileno())
        # Linking a completed sibling file is atomic and refuses existing names.
        # APFS, NTFS and ext4 support this; unsupported filesystems fail safely.
        os.link(stage, destination)
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)
    return str(destination.resolve())
