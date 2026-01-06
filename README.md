# `Efficient 24x7 Image`

Optimized YouTube 24/7 streaming script that reduces costs from ~$2 to ~$0.20 by eliminating unnecessary video processing.

![stream](https://github.com/user-attachments/assets/91ca2f03-b4d5-4cf3-bb3b-2ff4e473fe92)

![graph](https://github.com/user-attachments/assets/83ce4a4c-a6e8-4467-8e78-b92ca33fb49b)

![env](https://github.com/user-attachments/assets/63738a6d-1625-41a6-a8ab-03a92cfb0a80)

## Key Optimizations

1. **Smart Download (`yt-dlp`)**: Forces YouTube to provide a 1080p H.264 file specifically, ensuring the video is already in the perfect format for streaming.

2. **Direct Stream Copy (`ffmpeg`)**: Uses `-c copy` to remove all video processing. Instead of "reading, decoding, resizing, re-encoding, and sending," it now just "reads and sends," reducing CPU usage by ~99%.

## Prerequisites

- Python 3.7+
- FFmpeg installed and available in your PATH
- YouTube stream key
- YouTube video ID to stream

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your credentials:
   ```
   STREAM_KEY=your_youtube_stream_key_here
   YouTube_ID=your_youtube_video_id_here
   ```

3. Run the stream:
   ```bash
   python stream.py
   ```

## Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t youtube-stream .
   ```

2. Run the container with environment variables:
   ```bash
   docker run -d --name youtube-stream \
     -e STREAM_KEY=your_youtube_stream_key_here \
     -e YouTube_ID=your_youtube_video_id_here \
     youtube-stream
   ```

   Or use a `.env` file (make sure it's in the same directory):
   ```bash
   docker run -d --name youtube-stream \
     --env-file .env \
     youtube-stream
   ```

3. View logs:
   ```bash
   docker logs -f youtube-stream
   ```

4. Stop the container:
   ```bash
   docker stop youtube-stream
   docker rm youtube-stream
   ```

## How It Works

The script downloads a YouTube video in the exact format needed (1080p H.264 MP4) and streams it directly to YouTube's RTMP server using stream copy mode, which requires minimal CPU resources since no re-encoding occurs.

## Notes

- The video will loop infinitely
- Press `Ctrl+C` to stop the stream (or `docker stop` if using Docker)
- Ensure FFmpeg is installed: `ffmpeg -version` (included in Docker image)
