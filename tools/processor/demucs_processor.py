"""
Legacy compatibility module for demucs_processor.

This module exists to maintain backwards compatibility with the old import path.
New code should import from producer_toolkit.processor.demucs_processor instead.
"""

import sys
import os

# Add parent directory to path to allow importing from producer_toolkit
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import everything from the new location
from producer_toolkit.processor.demucs_processor import *

if __name__ == "__main__":
    print("Warning: Using legacy import path. Please update imports to use 'producer_toolkit.processor.demucs_processor'")

