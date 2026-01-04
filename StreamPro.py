import os
import subprocess
import sys
import glob
import yt_dlp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
stream_key = os.environ.get("STREAM_KEY")
if not stream_key:
    print("Error: STREAM_KEY not found in environment variables.")
    sys.exit(1)

youtube_id = os.environ.get("YouTube_ID")
if not youtube_id:
    print("Error: YouTube_ID not found in environment variables.")
    sys.exit(1)

# RTMP URL (YouTube default)
rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

video_path = "video.mp4"
youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"

print(f"Downloading video from YouTube: {youtube_url}")

# --- OPTIMIZATION 1: DOWNLOAD EXACT FORMAT ---
# We request:
# 1. height<=1080: To prevent downloading 4K if we don't need it.
# 2. vcodec^=avc: MUST be H.264 (AVC) to stream to YouTube without re-encoding.
# 3. ext=mp4: Ensures compatible container.
ydl_opts = {
    'format': 'bestvideo[height=1080][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'video.%(ext)s',
    'merge_output_format': 'mp4',
    'quiet': False,
    'no_warnings': False,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.youtube.com/',
    'extractor_args': {
        'youtube': {
            'player_client': ['android'],
        }
    },
}

try:
    # Clean up old files first
    if os.path.exists(video_path):
        os.remove(video_path)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    # Verify file exists
    if not os.path.exists(video_path):
        # Fallback check
        downloaded_files = glob.glob("video.*")
        if downloaded_files:
            video_path = downloaded_files[0]
            print(f"Using downloaded file: {video_path}")
        else:
            print("Error: Downloaded video file not found.")
            sys.exit(1)
    else:
        print(f"Video downloaded successfully: {video_path}")
except Exception as e:
    print(f"Error downloading video: {e}")
    sys.exit(1)

# --- OPTIMIZATION 2: STREAM COPY MODE WITH KEYFRAME FIX ---
# Re-encode with minimal settings to fix keyframe intervals (required by YouTube)
# Using ultrafast preset to minimize CPU while fixing keyframes
ffmpeg_cmd = [
    'ffmpeg',
    '-re',                   # Read input at native frame rate
    '-stream_loop', '-1',    # Loop input infinitely
    '-i', video_path,
    
    # Video encoding settings (minimal CPU usage)
    '-c:v', 'libx264',       # H.264 encoder
    '-preset', 'ultrafast',  # Fastest encoding (lowest CPU, larger file but doesn't matter for streaming)
    '-tune', 'zerolatency',  # Low latency for streaming
    '-g', '120',             # Keyframe every 120 frames (4 seconds at 30fps)
    '-keyint_min', '120',    # Minimum keyframe interval
    '-sc_threshold', '0',    # Disable scene change detection (saves CPU)
    '-b:v', '4500k',         # Bitrate for 1080p (adjust if needed)
    '-maxrate', '4500k',
    '-bufsize', '9000k',
    
    # Audio copy (no re-encoding needed)
    '-c:a', 'copy',
    
    '-f', 'flv',
    '-flvflags', 'no_duration_filesize',
    rtmp_url
]

print("Starting Optimized Stream with command:")
print(" ".join(ffmpeg_cmd))

# Run the command
try:
    subprocess.run(ffmpeg_cmd, check=True)
except KeyboardInterrupt:
    print("Stream stopped by user.")
except Exception as e:
    print(f"Error occurred: {e}")

