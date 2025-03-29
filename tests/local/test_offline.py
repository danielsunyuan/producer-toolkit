#!/usr/bin/env python3
"""
Offline Testing Script for Producer Toolkit

This script tests the stem extraction functionality without downloading from YouTube.
It uses the sample audio file provided in the tests/resources directory.

Instructions:
1. Activate your conda environment: conda activate producer-toolkit
2. Run this script: python -m tests.local.test_offline
"""

import os
import sys
import time
import platform
import shutil
from pathlib import Path
from datetime import datetime

# Make sure the package root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import toolkit function for stem extraction
from tools.processor.spleeter_processor import extract_stems

def print_step(message):
    """Print a formatted step message."""
    print(f"\n{'=' * 50}")
    print(f"  {message}")
    print(f"{'=' * 50}")

def setup_test_directories():
    """Set up test directories."""
    # Create tests/output directory at the same level as local/
    test_dir = Path(__file__).resolve().parent.parent / "output"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create stems directory
    stems_dir = test_dir / "stems"
    stems_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "base": test_dir,
        "stems": stems_dir
    }

def test_stem_extraction(audio_file, output_dir, stem_number=2):
    """Test stem extraction functionality."""
    print_step(f"Testing Stem Extraction ({stem_number} stems)")
    start_time = time.time()
    
    if not audio_file or not os.path.exists(audio_file):
        print(f"❌ ERROR: Cannot extract stems - input audio file not found: {audio_file}")
        return False
    
    try:
        print(f"Extracting {stem_number} stems from: {audio_file}")
        extract_stems(audio_file, str(output_dir), stem_number=stem_number)
        
        # Check for expected output files based on stem_number
        if stem_number == 2:
            expected_stems = ["vocals.wav", "accompaniment.wav"]
        elif stem_number == 4:
            expected_stems = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]
        elif stem_number == 5:
            expected_stems = ["vocals.wav", "drums.wav", "bass.wav", "piano.wav", "other.wav"]
        
        # Convert output_dir to Path if it's a string
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
            
        missing_stems = []
        for stem in expected_stems:
            stem_path = output_dir / stem
            if not stem_path.exists():
                missing_stems.append(stem)
        
        if not missing_stems:
            print(f"✅ SUCCESS: Stems extracted to {output_dir}")
            print(f"   Extracted stems: {', '.join(expected_stems)}")
            print(f"   Time taken: {time.time() - start_time:.2f} seconds")
            return True
        else:
            print(f"❌ ERROR: Some stems are missing: {', '.join(missing_stems)}")
            return False
    except Exception as e:
        print(f"❌ ERROR: Stem extraction failed with exception: {str(e)}")
        return False

def run_tests(force_fail=False):
    """Run all tests."""
    print_step("Starting Offline Producer Toolkit Tests")
    print(f"Date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {sys.version}")
    
    # Set up test directories
    dirs = setup_test_directories()
    
    # Get the sample audio file path
    resources_dir = Path(__file__).resolve().parent.parent / "resources"
    sample_audio = resources_dir / "sample.wav"
    
    print(f"Using sample audio file: {sample_audio}")
    
    # Test stem extraction (convert paths to strings)
    stem_success = test_stem_extraction(str(sample_audio), str(dirs["stems"]), stem_number=2)
    
    # For testing cleanup behavior with failing tests
    if force_fail:
        print("⚠️ Forcing test failure for cleanup testing")
        stem_success = False
    
    # Print summary
    print_step("Test Summary")
    print(f"Stem Extraction: {'✅ SUCCESS' if stem_success else '❌ FAILED'}")
    print(f"\nOutput files are located in: {dirs['base'].absolute()}")
    
    # Return test result for the test runner
    return stem_success

if __name__ == "__main__":
    run_tests()