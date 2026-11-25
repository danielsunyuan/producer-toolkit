"""Local resource policy and privacy-safe source references."""
from dataclasses import dataclass
import math
from pathlib import Path
import re
import shutil
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit


@dataclass(frozen=True)
class Limits:
    max_duration: float = 3600
    max_bytes: int = 2 * 1024**3
    reserve_bytes: int = 1024**3

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.max_duration, self.max_bytes, self.reserve_bytes)):
            raise ValueError('Resource limits must be finite.')
        if self.max_duration <= 0 or self.max_bytes <= 0 or self.reserve_bytes < 0:
            raise ValueError('Duration and size limits must be positive; reserved disk space cannot be negative.')

    def check_duration(self, seconds):
        if seconds is not None and (not math.isfinite(seconds) or seconds < 0 or seconds > self.max_duration):
            raise ValueError('Media exceeds the duration limit; use --max-duration to explicitly allow a longer job.')

    def check_size(self, size):
        if size > self.max_bytes:
            raise ValueError('Media exceeds the size limit; use --max-size-mb to explicitly allow a larger job.')

    def check_disk(self, path, required=0):
        path = Path(path).resolve()
        while not path.exists():
            path = path.parent
        if shutil.disk_usage(path).free < self.reserve_bytes + required:
            raise OSError('Not enough free disk space for this job and the reserved margin. Choose another drive or adjust --min-free-mb.')


def validate_url(url):
    try:
        parts = urlsplit(url)
        invalid = (parts.scheme not in ('http', 'https') or not parts.hostname
                   or parts.username is not None or parts.password is not None
                   or any(ord(c) < 33 or ord(c) == 127 for c in url))
        parts.port  # Also validate port syntax without repeating the input in errors.
    except ValueError:
        invalid = True
    if invalid:
        raise ValueError('Use an HTTP(S) URL without embedded credentials or control characters.')


def public_url(url):
    try:
        parts = urlsplit(url)
        query = ''
        if parts.hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            video_id = parse_qs(parts.query).get('v', [''])[0]
            if re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
                query = urlencode({'v': video_id})
        return urlunsplit((parts.scheme, parts.netloc.rsplit('@', 1)[-1], parts.path, query, ''))
    except ValueError:
        return '[redacted URL]'


def public_message(message):
    return re.sub(r'[A-Za-z][A-Za-z0-9+.-]*://[^\s]+', lambda match: public_url(match.group(0)), str(message))
