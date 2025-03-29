#!/usr/bin/env python3
"""
Test Runner for Producer Toolkit

This script provides a convenient way to run all or specific tests.

Usage:
    python -m tests.run_tests [--all|--offline|--local]
    
Options:
    --all       Run all tests (offline and local)
    --offline   Run offline tests only (using sample files)
    --local     Run local tests (with YouTube download)
    
If no option is specified, offline tests will be run by default.

Examples:
    python -m tests.run_tests --all        # Run all tests
    python -m tests.run_tests --offline    # Run offline tests only
    python -m tests.run_tests --local      # Run local tests with YouTube download
"""

import sys
import os
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
    
    args = parser.parse_args()
    
    # Default to offline if no option specified
    if not (args.all or args.offline or args.local):
        args.offline = True
        
    return args

def run_test_module(module_name):
    """Import and run the specified test module."""
    print(f"\n{'=' * 60}")
    print(f"Running {module_name}")
    print(f"{'=' * 60}")
    
    try:
        # Import the module dynamically
        test_module = importlib.import_module(module_name)
        
        # If the module has a run_tests function, call it
        if hasattr(test_module, "run_tests"):
            test_module.run_tests()
        else:
            print(f"ERROR: {module_name} does not have a run_tests function")
    except Exception as e:
        print(f"ERROR running {module_name}: {str(e)}")

def main():
    """Main entry point."""
    args = get_args()
    
    if args.all or args.offline:
        run_test_module("tests.local.test_offline")
        
    if args.all or args.local:
        # For local tests, allow specifying a YouTube URL
        if len(sys.argv) > 2 and not sys.argv[-1].startswith('--'):
            url = sys.argv[-1]
            # Import the test_local module
            import tests.local.test_local as test_local
            test_local.run_tests(url)
        else:
            run_test_module("tests.local.test_local")
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()