import os
import subprocess
import sys
import glob
import time  # Added for sleep delay
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
ydl_opts = {
    'format': 'bestvideo[height=360][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best',
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

# --- OPTIMIZATION 2: STREAMING LOOP WITH RETRY LOGIC ---
# We wrap the FFmpeg command in a loop to handle crashes automatically.

while True:
    print("\n--- Starting Stream ---")
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-re',                # Read input at native frame rate
        '-stream_loop', '-1', # Loop input infinitely
        '-i', video_path,
        
        # Video encoding settings (minimal CPU for 360p)
        '-c:v', 'libx264',       # H.264 encoder
        '-preset', 'ultrafast',  # Fastest encoding (lowest CPU)
        '-tune', 'zerolatency',  # Low latency for streaming
        
        # UPDATED: Changed GOP to 60 (2 seconds at 30fps) for better stability
        '-g', '60',              
        '-keyint_min', '60',     
        
        '-sc_threshold', '0',    # Disable scene change detection (saves CPU)
        '-b:v', '800k',          # Bitrate for 360p
        '-maxrate', '800k',
        '-bufsize', '1600k',     # Buffer size (2x bitrate)
        
        # Audio encoding
        '-c:a', 'aac',
        '-b:a', '128k',
        '-ar', '44100',
        '-ac', '2',
        
        '-f', 'flv',
        '-flvflags', 'no_duration_filesize',
        rtmp_url
    ]

    try:
        # Run FFmpeg. This call blocks until FFmpeg exits (crashes or stops).
        subprocess.run(ffmpeg_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f"\n[Error] Stream crashed with exit code {e.returncode}.")
        print("Restarting in 5 seconds...")
        time.sleep(5) # Wait before restarting to avoid spamming the server
        continue # Restart the loop
        
    except KeyboardInterrupt:
        print("\nStream stopped manually by user.")
        break # Exit the loop and end the script
        
    except Exception as e:
        print(f"\n[Unexpected Error] {e}")
        print("Restarting in 5 seconds...")
        time.sleep(5)
        continue
