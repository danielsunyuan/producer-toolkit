"""
Processor module for Producer Toolkit.

Provides functionality for audio processing and stem separation using Demucs.
"""

from .demucs_processor import extract_stems

__all__ = ["extract_stems"]
