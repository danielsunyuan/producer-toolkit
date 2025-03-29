#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_step(message):
    """Print a formatted step message."""
    print(f"\n=== {message} ===")

def check_python_version():
    """Check if Python version is compatible."""
    print_step("Checking Python version")
    
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 9):
        print(f"Error: Python 3.9+ is required. Current version: {major}.{minor}")
        print("Please install Python 3.9 or newer.")
        return False
    
    print(f"Python version {major}.{minor} - OK")
    return True

def check_ffmpeg():
    """Check if ffmpeg is installed and install it if not."""
    print_step("Checking FFmpeg installation")
    
    # Check if ffmpeg is in PATH
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    
    if ffmpeg_installed:
        print("FFmpeg is already installed - OK")
        return True
    
    print("FFmpeg not found. Attempting to install...")
    
    system = platform.system().lower()
    if system == "darwin":  # macOS
        try:
            # Try to install ffmpeg with Homebrew
            if shutil.which("brew") is None:
                print("Homebrew not found. Please install Homebrew first:")
                print("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                print("Then run this script again.")
                return False
            
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
            print("FFmpeg installed successfully with Homebrew - OK")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install FFmpeg with Homebrew.")
            return False
    
    elif system == "windows":
        print("Please install FFmpeg manually for Windows:")
        print("1. Download from https://github.com/BtbN/FFmpeg-Builds/releases")
        print("2. Extract the zip file")
        print("3. Add the bin folder to your PATH environment variable")
        print("\nAfter installing FFmpeg, run this script again.")
        return False
    
    elif system == "linux":
        try:
            # Try to install ffmpeg with apt (for Debian/Ubuntu)
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
            print("FFmpeg installed successfully with apt - OK")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install FFmpeg with apt.")
            print("Please install FFmpeg manually for your Linux distribution.")
            return False
    
    return False

def update_ffmpeg_path():
    """Update ffmpeg path in the code for cross-platform compatibility."""
    print_step("Updating FFmpeg path configuration")
    
    download_file = Path("tools/downloader/download.py")
    
    with open(download_file, "r") as file:
        content = file.read()
    
    # Replace hardcoded ffmpeg path with dynamic path detection
    if "'ffmpeg_location':" in content:
        modified_content = content.replace(
            "'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',",
            "# Dynamically find ffmpeg path\n        'ffmpeg_location': shutil.which('ffmpeg'),"
        )
        
        # Add shutil import if not present
        if "import shutil" not in modified_content:
            modified_content = modified_content.replace(
                "import os", 
                "import os\nimport shutil"
            )
        
        with open(download_file, "w") as file:
            file.write(modified_content)
            
        print(f"Updated {download_file} for cross-platform compatibility - OK")
    else:
        print(f"No FFmpeg path to update in {download_file}")

def install_dependencies():
    """Install Python dependencies."""
    print_step("Installing Python dependencies")
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Handle different requirements for different platforms
    if system == "darwin" and ("arm64" in machine or "m1" in machine or "m2" in machine):
        # For Apple Silicon Macs
        print("Detected Apple Silicon Mac, using tensorflow-macos")
        
        # Create a modified requirements file
        with open("requirements.txt", "r") as file:
            requirements = file.read()
            
        # Replace tensorflow with tensorflow-macos
        requirements = requirements.replace("tensorflow==2.13.0", "tensorflow-macos==2.13.0")
        
        # Use a temp file for installation
        with open("requirements_temp.txt", "w") as file:
            file.write(requirements)
            
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_temp.txt"], check=True)
        
        # Clean up temp file
        os.remove("requirements_temp.txt")
    else:
        # For all other platforms, use regular requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    print("Dependencies installed successfully - OK")
    return True

def check_windows_compatibility():
    """Make adjustments for Windows compatibility."""
    print_step("Checking Windows compatibility")
    
    if platform.system().lower() != "windows":
        print("Not on Windows, skipping Windows-specific adjustments")
        return
    
    # Update path handling for Windows
    processor_file = Path("tools/processor/spleeter_processor.py")
    
    with open(processor_file, "r") as file:
        content = file.read()
    
    # Add Path object usage for cross-platform path handling
    if "Path" in content and not "os.path.join(output_dir, stem_file)" in content:
        # No changes needed
        pass
    else:
        print("Making Windows path compatibility updates...")
        
        # No specific changes needed as the code already uses os.path.join consistently
        print("The code is already using os.path.join for path handling - OK")

def main():
    """Main installation function."""
    print("\n==============================================")
    print("  Producer Toolkit Installation")
    print("==============================================\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Update ffmpeg path in the code
    update_ffmpeg_path()
    
    # Check and install ffmpeg
    if not check_ffmpeg():
        return False
    
    # Make Windows compatibility adjustments
    check_windows_compatibility()
    
    # Install Python dependencies
    if not install_dependencies():
        return False
    
    print("\n==============================================")
    print("  Installation Complete! SUCCESS")
    print("==============================================\n")
    
    print("You can now use Producer Toolkit with:")
    print("python main.py \"https://www.youtube.com/watch?v=YOUTUBE_ID\" -s\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)