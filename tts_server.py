import os
import uuid
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

app = Flask(__name__)
CORS(app)

TTS_OUTPUT_DIR = "tts_output"
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

# Load model at startup (uses ~2GB VRAM)
print(" Loading Chatterbox TTS model on CUDA...")
start_time = time.time()
model = ChatterboxTTS.from_pretrained(device="cuda")
load_time = time.time() - start_time
print(f" Chatterbox TTS loaded in {load_time:.1f}s")


@app.route("/api/tts/generate", methods=["POST"])
def generate_speech():
   
    try:
        data = request.json
        text = data.get("text", "")
        exaggeration = data.get("exaggeration", 0.5)
        cfg = data.get("cfg", 0.5)
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400
        
        if len(text) > 500:
            text = text[:500] + "..."
        
        print(f"🎙️ Generating speech: '{text[:50]}...'")
        
        wav = model.generate(text, exaggeration=exaggeration, cfg_weight=cfg)
        
        # Save to file
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(TTS_OUTPUT_DIR, filename)
        ta.save(filepath, wav, model.sr)
        
        print(f" Audio saved: {filepath}")
        
        return jsonify({
            "success": True,
            "audio_url": f"http://localhost:8001/api/tts/audio/{filename}",
            "filename": filename
        })
        
    except Exception as e:
        print(f" TTS Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tts/audio/<filename>", methods=["GET"])
def serve_audio(filename):
    filepath = os.path.join(TTS_OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype="audio/wav")
    return jsonify({"error": "File not found"}), 404


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({"status": "ok", "model": "ChatterboxTTS", "device": "cuda"})


if __name__ == "__main__":
    print("=" * 50)
    print("Chatterbox TTS Microservice")
    print(f" Output dir: {TTS_OUTPUT_DIR}")
    print(" Running on http://localhost:8001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=8001, debug=False)
