# Use Python slim image as base
FROM python:3.11-slim

# Install FFmpeg and necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY stream.py .

# Create directory for video files
RUN mkdir -p /app/videos

# Set environment variables (can be overridden at runtime)
ENV STREAM_KEY=""
ENV YouTube_ID="oY7SfTpyRco"

# Run the streaming script
CMD ["python", "stream.py"]

