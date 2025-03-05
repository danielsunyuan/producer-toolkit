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
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Highest quality video + audio
        'merge_output_format': 'mp4',  # Ensure MP4 output
        'outtmpl': output_path,  # Set output file path
        'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Updated FFmpeg path
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
        output_path = '%(title)s'  # Without extension
        # Build the final path for the return value
        return_path = '%(title)s.wav'
    elif os.path.isdir(output_path):
        # If output_path is a directory, build the output path
        output_path = os.path.join(output_path, '%(title)s')
        # And store the directory for the return value
        output_dir = output_path
        return_path = output_path + '.wav'
    else:
        # If a specific filename was given
        return_path = output_path + '.wav' if not output_path.endswith('.wav') else output_path

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Best available audio
        'outtmpl': output_path,  # Output template
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
        'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Updated FFmpeg path
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # Get the actual title to build the correct return path
        if info_dict and 'title' in info_dict:
            # Replace the template with the actual title
            if '%(title)s' in return_path:
                return_path = return_path.replace('%(title)s', info_dict['title'])

    return return_path


def test():
    # Example usage (commented out for import usage)
    video_url = "https://www.youtube.com/watch?v=q6EoRBvdVPQ"
    download_video(video_url)  # Download video as MP4
    download_audio(video_url)  # Download audio as WAV