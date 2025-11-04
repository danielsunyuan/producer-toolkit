#!/usr/bin/env python3
"""
Simple Test Runner for Producer Toolkit

Usage:
    python -m tests.run_tests
"""

import sys
import os
import subprocess
from pathlib import Path

# Make sure the package root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

def run_unit_tests():
    """Run unit tests using unittest (standard library, no dependencies)."""
    print("Running unit tests...")
    print("=" * 50)

    # Use unittest (standard library, no extra dependencies needed)
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests/", "-v"],
                          capture_output=True, text=True)
    
    # Print test output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode == 0:
        print("\n✅ All unit tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

def main():
    """Main test execution function."""
    print("Producer Toolkit Test Runner")
    print("=" * 40)

    success = run_unit_tests()

    # Final status
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)
    print("=" * 50)

if __name__ == "__main__":
    main()