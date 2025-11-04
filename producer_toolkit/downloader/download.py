import os
import shutil
import yt_dlp
import tempfile
import sys
from io import StringIO
from ..analyzer.audio_analyzer import analyze_audio, generate_filename_with_features

def download_video(url, output_path=None):
    """
    Downloads a YouTube video in MP4 format with the highest available quality.

    Args:
        url (str): YouTube video URL.
        output_path (str, optional): Custom file path or directory (default: video title).

    Returns:
        str: Path to the downloaded MP4 file.
    """
    if output_path is None:
        output_path = '%(title)s.mp4'  # Default filename
    elif os.path.isdir(output_path):
        # If output_path is a directory, append the default filename pattern
        output_path = os.path.join(output_path, '%(title)s.mp4')

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Highest quality video + audio
        'merge_output_format': 'mp4',  # Ensure MP4 output
        'outtmpl': output_path,  # Set output file path
        'noplaylist': True,  # Only download the video, not the entire playlist
        # Dynamically find ffmpeg path
        'ffmpeg_location': shutil.which('ffmpeg'),
        'postprocessor_args': [
            # Video quality
            '-c:v', 'libx264', '-crf', '17', '-preset', 'veryslow',
            # Audio quality
            '-c:a', 'aac', '-b:a', '320k',
            # General
            '-movflags', '+faststart'
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return output_path


def download_audio(url, output_path=None, analyze_features=True):
    """
    Downloads a YouTube video's audio and converts it to WAV with BPM and key analysis.

    Args:
        url (str): YouTube video URL.
        output_path (str, optional): Custom file path or directory (default: video title).
        analyze_features (bool): Whether to analyze BPM and key for filename (default: True).

    Returns:
        str: Path to the downloaded WAV file.
    """
    # Use a temporary directory for initial download if we need to analyze features
    if analyze_features and output_path is not None and not os.path.isdir(output_path):
        # If a specific file path is given and we want to analyze, use temp dir first
        temp_dir = tempfile.gettempdir()
        temp_output = os.path.join(temp_dir, '%(title)s')
        temp_return_path = '%(title)s.wav'
        final_output_dir = os.path.dirname(output_path) if output_path else os.getcwd()
    else:
        if output_path is None:
            temp_output = '%(title)s'  # Without extension
            # Build the final path for the return value
            temp_return_path = '%(title)s.wav'
            final_output_dir = os.getcwd()
        elif os.path.isdir(output_path):
            # If output_path is a directory, build the output path
            temp_output = os.path.join(output_path, '%(title)s')
            temp_return_path = os.path.join(output_path, '%(title)s.wav')
            final_output_dir = output_path
        else:
            # If a specific filename was given
            temp_output = output_path.replace('.wav', '') if output_path.endswith('.wav') else output_path
            temp_return_path = output_path + '.wav' if not output_path.endswith('.wav') else output_path
            final_output_dir = os.path.dirname(output_path) if output_path else os.getcwd()

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Best available audio
        'outtmpl': temp_output,  # Output template
        'noplaylist': True,  # Only download the video, not the entire playlist
        'quiet': True,  # Suppress yt-dlp output
        'no_warnings': True,  # Suppress warnings
        'verbose': False,  # No verbose output
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Convert to WAV
            'preferredcodec': 'wav',
            'preferredquality': '320',  # Highest quality
        }],
        'postprocessor_args': [
            "-ar", "44100",  # 44.1kHz sample rate
            "-ac", "2",      # Stereo
            "-c:a", "pcm_s24le",  # 24-bit depth
        ],
        # Dynamically find ffmpeg path
        'ffmpeg_location': shutil.which('ffmpeg'),
        # Suppress progress hooks
        'progress_hooks': [],
    }

    # Suppress all yt-dlp output completely
    import logging
    import warnings
    
    # Suppress logging
    logging.getLogger('yt_dlp').setLevel(logging.CRITICAL)
    
    # Suppress warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # Use quiet mode and suppress progress
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
    
    # Get the actual title to build the correct return path
    if info_dict and 'title' in info_dict:
            # Replace the template with the actual title
            if '%(title)s' in temp_return_path:
                temp_file_path = temp_return_path.replace('%(title)s', info_dict['title'])
            else:
                temp_file_path = temp_return_path

    # If we don't need to analyze features, return the temp file path as is
    if not analyze_features:
        return temp_file_path

    # Analyze audio features if the file exists
    if os.path.exists(temp_file_path):
        try:
            from ..utils.loading import Spinner
            spinner = Spinner("🎵 Analyzing audio features (BPM and key)")
            spinner.start()
            bpm, key = analyze_audio(temp_file_path)
            spinner.stop(f"✅ Detected: {bpm} BPM, Key: {key}")
            
            # Generate enhanced filename
            original_filename = os.path.basename(temp_file_path)
            enhanced_filename = generate_filename_with_features(original_filename, bpm, key)
            
            # Create final path
            final_file_path = os.path.join(final_output_dir, enhanced_filename)
            
            # Move/rename the file if needed
            if temp_file_path != final_file_path:
                os.makedirs(final_output_dir, exist_ok=True)
                shutil.move(temp_file_path, final_file_path)
                print(f"File saved with features: {enhanced_filename}")
            
            return final_file_path
            
        except Exception as e:
            print(f"Warning: Audio analysis failed ({str(e)}), keeping original filename")
            # If analysis fails, just return the original file
            return temp_file_path
    else:
        print(f"Warning: Downloaded file not found at {temp_file_path}")
        return temp_file_path


def test():
    # Example usage (commented out for import usage)
    video_url = "https://www.youtube.com/watch?v=q6EoRBvdVPQ"
    download_video(video_url)  # Download video as MP4
    download_audio(video_url)  # Download audio as WAV