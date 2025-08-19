"""
Producer Toolkit - A command-line toolkit for music producers.

This package provides tools for downloading audio/video from YouTube
and extracting stems using Spleeter.
"""

__version__ = "1.0.0"
__author__ = "Daniel"
__description__ = "A command-line toolkit for music producers to download audio/video from YouTube and extract stems using Spleeter"

from . import downloader
from . import processor

__all__ = ["downloader", "processor"]
