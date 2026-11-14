#!/usr/bin/env python3
"""Compatibility entry point; all behavior lives in the package CLI."""
from producer_toolkit.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
