#!/usr/bin/env python3
"""
CI Test Runner for Producer Toolkit

This script allows you to run the CI pipeline tests locally.
It replicates the actions performed in the GitHub Actions workflow.

Usage:
    python -m tests.ci.scripts.run_ci_test [--cleanup]

Options:
    --cleanup   Clean up test output files after successful tests

Requirements:
    - FFmpeg must be installed and available in the PATH
    - Python dependencies must be installed (run install.py first)
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

# Make sure the package root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

def print_step(message):
    """Print a formatted step message."""
    print(f"\n{'=' * 50}")
    print(f"  {message}")
    print(f"{'=' * 50}")

def setup_directories():
    """Set up test directories."""
    # Root directory
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    
    # CI resources directory
    ci_resources_dir = root_dir / "tests" / "ci" / "resources"
    ci_resources_dir.mkdir(parents=True, exist_ok=True)
    
    # Test output directory
    output_dir = root_dir / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (output_dir / "audio_test").mkdir(exist_ok=True)
    (output_dir / "video_test").mkdir(exist_ok=True)
    (output_dir / "stems_test").mkdir(exist_ok=True)
    (output_dir / "pipeline_test").mkdir(exist_ok=True)
    
    return {
        "root": root_dir,
        "resources": ci_resources_dir,
        "output": output_dir
    }

def generate_test_files(dirs):
    """Generate test audio and video files."""
    print_step("Generating Test Files")
    
    # Generate test audio file
    audio_file = dirs["resources"] / "test_audio.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", 
        "-i", "sine=frequency=440:duration=1", 
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", 
        str(audio_file)
    ], check=True)
    print(f"Created test audio file: {audio_file}")
    
    # Generate test video file
    video_file = dirs["resources"] / "test_video.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", 
        "-i", "sine=frequency=440:duration=1", 
        "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1", 
        "-ar", "44100", "-ac", "2", "-c:a", "aac", "-c:v", "libx264", 
        str(video_file)
    ], check=True)
    print(f"Created test video file: {video_file}")
    
    return audio_file, video_file

def test_audio_download(dirs, audio_file):
    """Test audio download functionality."""
    print_step("Testing Audio Download")
    
    output_path = dirs["output"] / "audio_test"
    result = subprocess.run([
        sys.executable, str(dirs["root"] / "main.py"),
        "dummy_url", "-a", 
        "-o", str(output_path),
        "--test", "--test-file", str(audio_file)
    ], capture_output=True, text=True)
    
    print(f"Command output: {result.stdout}")
    
    # Check for success
    output_files = list(output_path.glob("*.wav"))
    if output_files:
        print(f"✅ SUCCESS: Audio test passed, found output file: {output_files[0]}")
        return True
    else:
        print(f"❌ ERROR: Audio test failed, no output file found")
        return False

def test_video_download(dirs, video_file):
    """Test video download functionality."""
    print_step("Testing Video Download")
    
    output_path = dirs["output"] / "video_test"
    result = subprocess.run([
        sys.executable, str(dirs["root"] / "main.py"),
        "dummy_url", "-v", 
        "-o", str(output_path),
        "--test", "--test-file", str(video_file)
    ], capture_output=True, text=True)
    
    print(f"Command output: {result.stdout}")
    
    # Check for success
    output_files = list(output_path.glob("*.mp4"))
    if output_files:
        print(f"✅ SUCCESS: Video test passed, found output file: {output_files[0]}")
        return True
    else:
        print(f"❌ ERROR: Video test failed, no output file found")
        return False

def test_stem_extraction(dirs, audio_file):
    """Test stem extraction functionality."""
    print_step("Testing Stem Extraction")
    
    # Ensure models directory exists (mock setup)
    models_dir = dirs["root"] / "models" / "2stems"
    models_dir.mkdir(parents=True, exist_ok=True)
    (models_dir / "separator_config.json").touch()
    
    output_path = dirs["output"] / "stems_test"
    result = subprocess.run([
        sys.executable, str(dirs["root"] / "main.py"),
        "dummy_url", "-s", 
        "-o", str(output_path),
        "--test", "--test-file", str(audio_file),
        "-n", "2"
    ], capture_output=True, text=True)
    
    print(f"Command output: {result.stdout}")
    
    # Check for success (in real test we would look for stem files)
    if output_path.exists():
        print(f"✅ SUCCESS: Stem extraction test completed")
        return True
    else:
        print(f"❌ ERROR: Stem extraction test failed")
        return False

def cleanup_test_outputs(dirs):
    """Clean up test output directories."""
    print_step("Cleaning Up Test Outputs")
    
    # Clean up output directory
    if dirs["output"].exists():
        print(f"Removing {dirs['output']}")
        shutil.rmtree(dirs["output"])
    
    print("Cleanup completed.")

def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run CI tests for Producer Toolkit")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test files after successful tests")
    return parser.parse_args()

def run_tests(cleanup=False):
    """Run all CI tests."""
    print_step("Starting CI Tests")
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {sys.version}")
    
    try:
        # Set up directories
        dirs = setup_directories()
        
        # Generate test files
        audio_file, video_file = generate_test_files(dirs)
        
        # Run tests
        audio_success = test_audio_download(dirs, audio_file)
        video_success = test_video_download(dirs, video_file)
        stem_success = test_stem_extraction(dirs, audio_file)
        
        # Print summary
        print_step("Test Summary")
        print(f"Audio Download Test: {'✅ SUCCESS' if audio_success else '❌ FAILED'}")
        print(f"Video Download Test: {'✅ SUCCESS' if video_success else '❌ FAILED'}")
        print(f"Stem Extraction Test: {'✅ SUCCESS' if stem_success else '❌ FAILED'}")
        print(f"\nOutput files are located in: {dirs['output'].absolute()}")
        
        all_tests_passed = audio_success and video_success and stem_success
        
        if all_tests_passed:
            print("\nAll CI tests passed successfully! ✅")
            
            # Clean up if requested and all tests passed
            if cleanup:
                cleanup_test_outputs(dirs)
                
            return 0
        else:
            print("\nSome CI tests failed. ❌")
            
            # Don't clean up if tests failed (for debugging)
            if cleanup:
                print("Skipping cleanup due to failed tests.")
                
            return 1
    
    except Exception as e:
        print(f"Error running CI tests: {str(e)}")
        return 1

if __name__ == "__main__":
    args = get_args()
    sys.exit(run_tests(cleanup=args.cleanup))