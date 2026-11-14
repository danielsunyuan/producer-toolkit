"""Publish artifacts without replacing existing user files."""
import shutil
from pathlib import Path

def publish(source, destination):
    destination = Path(destination)
    with destination.open("xb") as target:
        try:
            with Path(source).open("rb") as incoming:
                shutil.copyfileobj(incoming, target)
        except BaseException:
            destination.unlink(missing_ok=True)
            raise
    return str(destination.resolve())
