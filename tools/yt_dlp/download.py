import yt_dlp

def download_video(url):
    """
    Downloads a YouTube video in MP4 format with the best available quality.
    
    Args:
        url (str): YouTube video URL
    """
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Best quality video + audio
        'merge_output_format': 'mp4',  # Force MP4 output
        'outtmpl': '%(title)s',  # Save file as video title (yt-dlp will add .mp4)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])  # Start download

def download_audio(url):
    """
    Downloads a YouTube video's audio and converts it to MP3.
    
    Args:
        url (str): YouTube video URL
    """
    ydl_opts = {
        'format': 'bestaudio/best',  # Best available audio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Convert to MP3
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # 192 kbps bitrate
        }],
        'outtmpl': '%(title)s',  # Save file as video title (yt-dlp will add .mp3)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])  # Start download

# Example usage
video_url = "https://www.youtube.com/watch?v=q6EoRBvdVPQ"

# Call one of these functions depending on what you need:
# download_video(video_url)  # Download video as MP4
download_audio(video_url)  # Download audio as MP3