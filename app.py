import os
import requests
import time
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile

# Load environment variables
load_dotenv()
hf_token = os.getenv("HUGGINGFACE_TOKEN")
if not hf_token:
    raise ValueError("HUGGINGFACE_TOKEN not found in .env file")

class ASRInterface:
    def __init__(self):
        self.available_models = {
            "loko99/whisper_tiny_kannada": "Whisper Tiny KN",
            "loko99/whisper_small_kannada": "Whisper Small KN",
            "loko99/whisper_turbo_kannada": "Whisper Turbo KN",
            "openai/whisper-tiny": "Whisper Tiny",
            "openai/whisper-small": "Whisper Small",
            "openai/whisper-large-v3-turbo": "Whisper Large V3 Turbo",
            "openai/whisper-large-v3": "Whisper Large V3",
        }
        self.headers = {"Authorization": f"Bearer {hf_token}"}
    
    def call_whisper_api(self, audio_path: str, model_name: str, max_retries: int = 5) -> dict:
        """Make a direct API call with the audio file with retry mechanism"""
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Set payload with Kannada language
        payload = {
            "language": "kn",  # Always use Kannada
            "task": "transcribe"
        }
        
        # Implement retry with exponential backoff
        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(
                    api_url, 
                    headers=self.headers, 
                    json=payload,
                    data=audio_bytes,
                    timeout=30  # Add timeout to prevent hanging requests
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    return {"error": "Invalid Hugging Face token. Please check your token in the .env file."}
                elif response.status_code == 503:
                    # Service unavailable - likely the model is loading or rate limited
                    wait_time = 2 ** retries  # Exponential backoff: 1, 2, 4, 8, 16 seconds
                    retries += 1
                    if retries < max_retries:
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            "error": "The model service is currently unavailable. This could be due to high demand or the model is still loading. Please try again in a few minutes."
                        }
                else:
                    return {"error": f"Error {response.status_code}: {response.text}"}
            
            except requests.exceptions.Timeout:
                retries += 1
                if retries < max_retries:
                    time.sleep(2 ** retries)
                    continue
                return {"error": "Request timed out. The server might be under heavy load. Please try again later."}
            
            except requests.exceptions.RequestException as e:
                return {"error": f"Network error: {str(e)}"}
        
        return {"error": "Maximum retries reached. Service is unavailable."}
    
    def process_long_audio(self, audio_path: str, model_name: str, chunk_size_ms: int = 10000, overlap_ms: int = 1000) -> str:
        """Process longer audio files by splitting into chunks with overlap"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)
            audio_length_ms = len(audio)
            
            # If audio is short enough, process directly
            if audio_length_ms <= chunk_size_ms:
                result = self.call_whisper_api(audio_path, model_name)
                if "error" in result:
                    return result["error"]
                return result.get("text", "No transcription found")
            
            # For longer audio, process in chunks
            transcription = ""
            with tempfile.TemporaryDirectory() as temp_dir:
                chunk_start = 0
                
                while chunk_start < audio_length_ms:
                    # Extract chunk
                    chunk_end = min(chunk_start + chunk_size_ms, audio_length_ms)
                    chunk = audio[chunk_start:chunk_end]
                    
                    # Save chunk as temp file
                    chunk_file = os.path.join(temp_dir, f"chunk_{chunk_start}.wav")
                    chunk.export(chunk_file, format="wav")
                    
                    # Transcribe chunk
                    result = self.call_whisper_api(chunk_file, model_name)
                    
                    if "error" in result:
                        return result["error"]
                    
                    # Append transcription
                    chunk_text = result.get("text", "")
                    transcription += " " + chunk_text
                    
                    # Move to next chunk with overlap
                    chunk_start += (chunk_size_ms - overlap_ms)
            
            return transcription.strip()
            
        except Exception as e:
            return f"Error processing audio: {str(e)}"
    
    def transcribe(self, audio_path: str, model_name: str) -> str:
        """Main transcription function that handles any audio length"""
        try:
            transcription = self.process_long_audio(audio_path, model_name)
            return transcription
        except Exception as e:
            return f"Error during transcription: {str(e)}"

# Initialize Flask app
app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize ASR interface
asr = ASRInterface()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', models=asr.available_models)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Handle transcription requests"""
    try:
        # Check if the required files are provided
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get model selection
        model_name = request.form.get('model')
        if not model_name or model_name not in asr.available_models:
            return jsonify({"error": "Invalid model selection"}), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(file_path)
        
        # Process the audio
        transcription = asr.transcribe(file_path, model_name)
        
        # Clean up: remove the file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({"transcription": transcription})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve  # added import for waitress
    serve(app, host='0.0.0.0', port=7860)  # using waitress to serve the app