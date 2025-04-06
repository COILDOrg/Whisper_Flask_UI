---
title: Whisper Kannada
emoji: 🌖
colorFrom: yellow
colorTo: indigo
sdk: docker
pinned: false
---
Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Kannada ASR Transcription Interface

This project provides a web interface for transcribing audio files to Kannada text using Whisper models. It supports both audio file uploads and live recording from the browser.

## Features

- **Model Selection:** Choose from various Whisper models for transcription
- **Audio Upload:** Upload audio files in formats like MP3, WAV, M4A, and FLAC
- **Live Recording:** Record audio directly from the browser using the microphone
- **Transcription Results:** Displays the transcribed text with a copy-to-clipboard feature
- **Error Handling:** User-friendly error messages for common issues
- **Theme Toggle:** Switch between light and dark themes

## Requirements

- Python 3.11
- Flask
- pydub
- python-dotenv
- Requests
- waitress
- ffmpeg

## Setup

1. **Clone the repository and navigate to directory**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate  # On Windows
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment:**
   - Create a `.env` file with your Hugging Face API token for accessing private repo/models:

   ```
   HUGGINGFACE_TOKEN=your_token_here
   ```

## Running the Application

Start the application with `python app.py` and access the interface at `http://127.0.0.1:7860`

## Docker

Build: `docker build -t kannada-asr .`
Run: `docker run -d -p 7860:7860 kannada-asr`

