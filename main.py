import os
import argparse
from tools.yt_dlp.download import download_audio, download_video

def main():
    """
    Main function to handle downloading and processing of video/audio.
    """
    parser = argparse.ArgumentParser(description="Download and process audio from a link.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Required argument
    parser.add_argument("link", help="Link to download video/audio from")
    
    # Optional arguments
    parser.add_argument("-v", "--video", action="store_true", help="Download Video")
    parser.add_argument("-a", "--audio", action="store_true", help="Download Audio")
    parser.add_argument("-o", "--output-dir", dest="output_dir", help="Specify output directory")

    # Unimplemented features
    parser.add_argument("-s", "--stems", action="store_true", help="(Not implemented) Extract Stems")
    parser.add_argument("-acca", "--accapella", action="store_true", help="(Not implemented) Extract Acapella")
    parser.add_argument("-inst", "--instrumental", action="store_true", help="(Not implemented) Extract Instrumental")

    options = parser.parse_args()

    # Determine the output directory
    output_dir = options.output_dir if options.output_dir else os.path.join(os.path.expanduser("~"), "Downloads")

    options.link = "https://www.youtube.com/watch?v=q6EoRBvdVPQ"

    # Download audio
    if options.audio:
        print("Downloading audio...")
        download_audio(options.link, output_dir)
        print(f"Audio files saved in: {output_dir}")

    # Download video
    elif options.video:
        print("Downloading video...")
        download_video(options.link, output_dir)
        print(f"Video files saved in: {output_dir}")

    # Unimplemented features
    elif options.stems or options.accapella or options.instrumental:
        raise NotImplementedError("This feature is not yet implemented.")

    else:
        print("No valid option selected. Use -a for audio or -v for video.")

if __name__ == "__main__":
    main()


