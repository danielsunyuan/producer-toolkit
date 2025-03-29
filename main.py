import os
import sys
import argparse
import tempfile
import platform
from pathlib import Path
from tools.downloader.download import download_audio, download_video
from tools.processor.spleeter_processor import extract_stems

def main():
    """
    Main function to handle downloading and processing of video/audio.
    """
    parser = argparse.ArgumentParser(
        description="Download and process audio from a link.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required argument: the YouTube link
    parser.add_argument("link", help="Link to download video/audio from")
    
    # Optional arguments for different operations
    parser.add_argument("-v", "--video", action="store_true", help="Download Video")
    parser.add_argument("-a", "--audio", action="store_true", help="Download Audio")
    parser.add_argument("-s", "--stems", action="store_true", help="Download Audio & Extract Stems")
    parser.add_argument("-o", "--output-dir", dest="output_dir", help="Specify output directory")
    parser.add_argument("-n", "--num-stems", dest="num_stems", type=int, default=2, 
                       choices=[2, 4, 5], help="Number of stems to extract (2, 4, or 5)")
    
    options = parser.parse_args()
    
    # Determine the output directory (default: Downloads folder)
    if options.output_dir:
        output_dir = options.output_dir
    else:
        # Platform-specific Downloads folder
        if platform.system() == "Windows":
            # On Windows, use the user's Downloads folder
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(output_dir):
                # Fallback to Documents folder if Downloads doesn't exist
                output_dir = os.path.join(os.path.expanduser("~"), "Documents")
        else:
            # macOS and Linux
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    if options.audio:
        print("Downloading audio...")
        audio_file = download_audio(options.link, output_dir)
        if audio_file and os.path.exists(audio_file):
            print(f"Audio saved at: {audio_file}")
        else:
            print("Audio download failed.")
    
    elif options.video:
        print("Downloading video...")
        video_file = download_video(options.link, output_dir)
        if video_file and os.path.exists(video_file):
            print(f"Video saved at: {video_file}")
        else:
            print("Video download failed.")
    
    elif options.stems:
        print("Downloading audio for stem separation...")
        
        # Use a well-defined temp directory for download only
        temp_audio_dir = tempfile.gettempdir()  
        
        try:
            print(f"Downloading audio to: {temp_audio_dir} ...")
            final_audio_path = download_audio(options.link, temp_audio_dir)
            
            # Ensure the file exists and is not empty
            if not final_audio_path or not os.path.exists(final_audio_path) or os.path.getsize(final_audio_path) == 0:
                raise ValueError("Download failed or file is empty.")
            
            print(f"Audio downloaded to temp file: {final_audio_path}")
            
            # Get the filename without extension to use as output directory name
            filename = os.path.splitext(os.path.basename(final_audio_path))[0]
            stems_output_dir = os.path.join(output_dir, f"{filename}_stems")
            os.makedirs(stems_output_dir, exist_ok=True)
            
            # Extract stems using Spleeter (defaulting to 4 stems)
            print("Processing audio with Spleeter...")
            extract_stems(
                final_audio_path, 
                stems_output_dir, 
                stem_number=4
            )
            # Don't repeat the success message, it's already printed in extract_stems()
        except Exception as e:
            print(f"Error during processing: {e}")
        finally:
            # Cleanup the temporary audio file
            if final_audio_path and os.path.exists(final_audio_path):
                os.remove(final_audio_path)
                print("Temporary audio file removed.")
    else:
        # Default to audio download if no option is selected
        print("Downloading audio (default)...")
        audio_file = download_audio(options.link, output_dir)
        if audio_file and os.path.exists(audio_file):
            print(f"Audio saved at: {audio_file}")
        else:
            print("Audio download failed.")

if __name__ == "__main__":
    main()