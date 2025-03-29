#!/usr/bin/env python3
"""
Test Runner for Producer Toolkit

This script provides a convenient way to run all or specific tests.

Usage:
    python -m tests.run_tests [--all|--offline|--local] [--cleanup] [YOUTUBE_URL]
    
Options:
    --all       Run all tests (offline and local)
    --offline   Run offline tests only (using sample files)
    --local     Run local tests (with YouTube download)
    --cleanup   Clean up test output files after successful tests
    --fail      Force failure (for testing cleanup behavior)
    
If no option is specified, offline tests will be run by default.

Examples:
    python -m tests.run_tests --all                      # Run all tests
    python -m tests.run_tests --offline                  # Run offline tests only
    python -m tests.run_tests --local                    # Run local tests with YouTube download
    python -m tests.run_tests --local --cleanup          # Run local tests and clean up after
    python -m tests.run_tests --local YOUTUBE_URL        # Run local tests with specific URL
"""

import sys
import os
import shutil
import argparse
import importlib
from pathlib import Path

# Make sure the package root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Producer Toolkit tests")
    
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--all", action="store_true", help="Run all tests")
    test_group.add_argument("--offline", action="store_true", help="Run offline tests only")
    test_group.add_argument("--local", action="store_true", help="Run local tests with YouTube download")
    
    parser.add_argument("--cleanup", action="store_true", help="Clean up test files after successful tests")
    parser.add_argument("--fail", action="store_true", help="Force failure (for testing cleanup behavior)")
    parser.add_argument("youtube_url", nargs="?", help="YouTube URL for testing (optional)")
    
    args = parser.parse_args()
    
    # Default to offline if no option specified
    if not (args.all or args.offline or args.local):
        args.offline = True
        
    return args

def cleanup_test_outputs():
    """Clean up test output directories."""
    print("\nCleaning up test outputs...")
    
    # Get paths
    test_dir = Path(__file__).resolve().parent
    output_dir = test_dir / "output"
    
    # Clean up output directory
    if output_dir.exists():
        print(f"Removing {output_dir}")
        shutil.rmtree(output_dir)
    
    print("Cleanup completed.")

def run_test_module(module_name, force_fail=False):
    """Import and run the specified test module."""
    print(f"\n{'=' * 60}")
    print(f"Running {module_name}")
    print(f"{'=' * 60}")
    
    try:
        # Import the module dynamically
        test_module = importlib.import_module(module_name)
        
        # If the module has a run_tests function, call it
        if hasattr(test_module, "run_tests"):
            # Apply force fail only to the offline test
            if force_fail and module_name == "tests.local.test_offline":
                result = test_module.run_tests(force_fail=True)
            else:
                result = test_module.run_tests()
            return result if result is not None else True
        else:
            print(f"ERROR: {module_name} does not have a run_tests function")
            return False
    except Exception as e:
        print(f"ERROR running {module_name}: {str(e)}")
        return False

def main():
    """Main entry point."""
    args = get_args()
    
    all_tests_passed = True
    
    if args.all or args.offline:
        offline_result = run_test_module("tests.local.test_offline", force_fail=args.fail)
        all_tests_passed = all_tests_passed and offline_result
        
    if args.all or args.local:
        # For local tests, allow specifying a YouTube URL
        if args.youtube_url:
            # Import the test_local module
            import tests.local.test_local as test_local
            local_result = test_local.run_tests(args.youtube_url)
            all_tests_passed = all_tests_passed and (local_result is not False)
        else:
            local_result = run_test_module("tests.local.test_local")
            all_tests_passed = all_tests_passed and local_result
    
    print("\nAll tests completed.")
    
    # Clean up if requested and all tests passed
    if args.cleanup and all_tests_passed:
        cleanup_test_outputs()
    elif args.cleanup and not all_tests_passed:
        print("\nSkipping cleanup due to failed tests.")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())