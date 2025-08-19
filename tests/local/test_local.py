#!/usr/bin/env python3
"""
Local Testing Script for Producer Toolkit

This script tests the download and processing functionalities of the Producer Toolkit
on your local machine using actual YouTube links.

Instructions:
1. Activate your conda environment: conda activate producer-toolkit
2. Run this script: python -m tests.local.test_local
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

# Import toolkit functions
from producer_toolkit.downloader.download import download_audio, download_video
from producer_toolkit.processor.spleeter_processor import extract_stems

# Default test video (Yee)
YOUTUBE_LINK = "https://youtu.be/q6EoRBvdVPQ?si=C6YYCgtwWr2oVnMr"

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
    
    # Create subdirectories for different test outputs
    audio_dir = test_dir / "audio"
    video_dir = test_dir / "video"
    stems_dir = test_dir / "stems"
    
    for directory in [audio_dir, video_dir, stems_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    return {
        "base": test_dir,
        "audio": audio_dir,
        "video": video_dir,
        "stems": stems_dir
    }

def test_audio_download(youtube_link, output_dir):
    """Test audio download functionality."""
    print_step("Testing Audio Download")
    start_time = time.time()
    
    try:
        print(f"Downloading audio from: {youtube_link}")
        audio_file = download_audio(youtube_link, str(output_dir))
        
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file) / (1024 * 1024)  # Size in MB
            print(f"✅ SUCCESS: Audio downloaded to {audio_file}")
            print(f"   File size: {file_size:.2f} MB")
            print(f"   Time taken: {time.time() - start_time:.2f} seconds")
            return audio_file
        else:
            print(f"❌ ERROR: Audio download failed - file not found")
            return None
    except Exception as e:
        print(f"❌ ERROR: Audio download failed with exception: {str(e)}")
        return None

def test_video_download(youtube_link, output_dir):
    """Test video download functionality."""
    print_step("Testing Video Download")
    start_time = time.time()
    
    try:
        print(f"Downloading video from: {youtube_link}")
        video_file = download_video(youtube_link, str(output_dir))
        
        # The download_video function returns the pattern, not the actual filename
        # Let's find the actual video file
        video_files = list(output_dir.glob("*.mp4"))
        if video_files:
            video_file = video_files[0]
            file_size = os.path.getsize(video_file) / (1024 * 1024)  # Size in MB
            print(f"✅ SUCCESS: Video downloaded to {video_file}")
            print(f"   File size: {file_size:.2f} MB")
            print(f"   Time taken: {time.time() - start_time:.2f} seconds")
            return video_file
        else:
            print(f"❌ ERROR: Video download failed - file not found")
            return None
    except Exception as e:
        print(f"❌ ERROR: Video download failed with exception: {str(e)}")
        return None

def test_stem_extraction(audio_file, output_dir, stem_number=2):
    """Test stem extraction functionality."""
    print_step(f"Testing Stem Extraction ({stem_number} stems)")
    start_time = time.time()
    
    if not audio_file or not os.path.exists(audio_file):
        print(f"❌ ERROR: Cannot extract stems - input audio file not found")
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

def run_tests(youtube_link):
    """Run all tests."""
    print_step("Starting Local Producer Toolkit Tests")
    print(f"Testing with YouTube link: {youtube_link}")
    print(f"Date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {sys.version}")
    
    # Set up test directories
    dirs = setup_test_directories()
    
    # Test audio download
    audio_file = test_audio_download(youtube_link, dirs["audio"])
    
    # Test video download
    video_file = test_video_download(youtube_link, dirs["video"])
    
    # Test stem extraction (only if audio download succeeded)
    stem_success = False
    if audio_file:
        stem_success = test_stem_extraction(audio_file, dirs["stems"], stem_number=2)
    
    # Print summary
    print_step("Test Summary")
    print(f"Audio Download: {'✅ SUCCESS' if audio_file else '❌ FAILED'}")
    print(f"Video Download: {'✅ SUCCESS' if video_file else '❌ FAILED'}")
    print(f"Stem Extraction: {'✅ SUCCESS' if stem_success else '❌ FAILED'}")
    print(f"\nOutput files are located in: {dirs['base'].absolute()}")
    
    # Return overall success status for the test runner
    return bool(audio_file) and bool(video_file) and stem_success

if __name__ == "__main__":
    # Allow overriding the YouTube link from command line
    youtube_link = sys.argv[1] if len(sys.argv) > 1 else YOUTUBE_LINK
    run_tests(youtube_link)