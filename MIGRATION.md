# Migration Guide: Old Structure to Python Package

This guide helps you transition from the old Producer Toolkit structure to the new Python package structure.

## What Changed

### Old Structure (Deprecated)
```
tools/
├── downloader/download.py
└── processor/spleeter_processor.py
main.py
install.py
```

### New Structure (Recommended)
```
producer_toolkit/
├── __init__.py
├── cli.py
├── downloader/download.py
└── processor/spleeter_processor.py
setup.py
pyproject.toml
```

## Migration Steps

### 1. Update Import Statements

**Old imports:**
```python
from tools.downloader.download import download_audio, download_video
from tools.processor.spleeter_processor import extract_stems
```

**New imports:**
```python
from producer_toolkit.downloader.download import download_audio, download_video
from producer_toolkit.processor.spleeter_processor import extract_stems
```

### 2. Update Command Usage

**Old command:**
```bash
python main.py "https://youtube.com/watch?v=..." -s
```

**New command (recommended):**
```bash
pt "https://youtube.com/watch?v=..." -s
```

**Legacy command (still works):**
```bash
python main.py "https://youtube.com/watch?v=..." -s
```

### 3. Update Test Files

If you have custom test files, update the import paths:

```python
# Old
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.processor.spleeter_processor import extract_stems

# New
from producer_toolkit.processor.spleeter_processor import extract_stems
```

## Installation Changes

### Old Installation
```bash
python install.py
```

### New Installation
```bash
pip install -e .
```

## Benefits of the New Structure

1. **Global Command**: `pt` command available from anywhere
2. **Standard Python Package**: Follows Python packaging best practices
3. **Easy Distribution**: Can be installed via pip from PyPI (future)
4. **Better Testing**: Proper package structure for testing
5. **Dependency Management**: Better dependency resolution

## Backward Compatibility

- The old `main.py` still works
- The old `tools/` directory is preserved
- Existing scripts continue to function
- Gradual migration is supported

## Troubleshooting

### Import Errors
If you get import errors, ensure you've installed the package:
```bash
pip install -e .
```

### Command Not Found
If `pt` command is not found:
```bash
# Check if it's installed
pip list | grep producer-toolkit

# Reinstall if needed
pip install -e .
```

### Test Failures
If tests fail after migration:
1. Update import statements in test files
2. Ensure package is installed: `pip install -e .`
3. Run tests: `python -m tests.run_tests --offline`

## Support

If you encounter issues during migration:
1. Check this migration guide
2. Review the updated README.md
3. Check the test files for examples
4. Open an issue on GitHub
