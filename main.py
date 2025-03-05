import os
import argparse
import tempfile
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
    
    options = parser.parse_args()
    
    # Determine the output directory.
    # If not provided, default to the user's Downloads folder.
    output_dir = options.output_dir if options.output_dir else os.path.join(os.path.expanduser("~"), "Downloads")
    
    if options.audio:
        print("🎵 Downloading audio...")
        audio_file = download_audio(options.link, output_dir)
        if audio_file and os.path.exists(audio_file):
            print(f"✅ Audio saved at: {audio_file}")
        else:
            print("❌ Audio download failed.")
    
    elif options.video:
        print("🎥 Downloading video...")
        video_file = download_video(options.link, output_dir)
        print(f"✅ Video saved at: {video_file}")
    
    elif options.stems:
        print("🎵 Downloading audio for stem separation...")
        
        # Use OS-managed temporary files/directories for stem separation.
        temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        temp_output_dir = tempfile.mkdtemp(prefix="spleeter_stems_")
        
        try:
            print(f"⬇️ Downloading audio to: {temp_audio_path} ...")
            final_audio_path = download_audio(options.link, temp_audio_path)
            
            # Ensure the file exists and is not empty.
            if not final_audio_path or not os.path.exists(final_audio_path) or os.path.getsize(final_audio_path) == 0:
                raise ValueError("❌ Download failed or file is empty.")
            
            print(f"✅ Audio downloaded to temp file: {final_audio_path}")
            
            # Extract stems using Spleeter.
            print("🎛️ Processing audio with Spleeter...")
            extract_stems(final_audio_path, temp_output_dir, stem_number=2)
            print(f"✅ Stems saved at: {temp_output_dir}")
        except Exception as e:
            print(f"❌ Error during processing: {e}")
        finally:
            # Cleanup the temporary audio file.
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                print("🗑️ Temporary audio file removed.")
    else:
        print("⚠️ No valid option selected. Use -a for audio, -v for video, or -s for stem separation.")

if __name__ == "__main__":
    main()
