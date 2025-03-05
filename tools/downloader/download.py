import os
import yt_dlp

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
        'format': 'bv+ba/best',  # Best video + best audio
        'merge_output_format': 'mp4',  # Ensure MP4 output
        'outtmpl': output_path,  # Set output file path
        'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Updated FFmpeg path
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return output_path

def download_audio(url, output_path=None):
    """
    Downloads a YouTube video's audio and converts it to WAV.

    Args:
        url (str): YouTube video URL.
        output_path (str, optional): Custom file path or directory (default: video title).

    Returns:
        str: Path to the downloaded WAV file.
    """
    if output_path is None:
        output_path = '%(title)s.wav'  # Default filename
    elif os.path.isdir(output_path):
        # If output_path is a directory, append the default filename pattern
        output_path = os.path.join(output_path, '%(title)s.wav')

    ydl_opts = {
        'format': 'bestaudio/best',  # Best available audio
        'outtmpl': output_path,  # Set output file path
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Convert to WAV
            'preferredcodec': 'wav',
            'preferredquality': '192',  # 192 kbps
        }],
        'postprocessor_args': ["-ar", "44100", "-ac", "2"],  # Ensure 44.1kHz, stereo
        'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Updated FFmpeg path
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return output_path

# Example usage
video_url = "https://www.youtube.com/watch?v=q6EoRBvdVPQ"

# Call one of these functions depending on what you need:
download_video(video_url)  # Download video as MP4
# download_audio(video_url)  # Download audio as WAV