"""
RunPod Serverless Handler for Chatterbox TTS
Accepts base64 audio as reference (no YouTube dependency)
"""

import runpod
import torch
import torchaudio
import base64
import tempfile
import os

model = None

def initialize_model():
    global model
    if model is None:
        from chatterbox.tts import ChatterboxTTS
        model = ChatterboxTTS.from_pretrained(device="cuda")
    return model

def audio_tensor_to_base64(audio_tensor, sample_rate=24000):
    """Convert audio tensor to base64 WAV"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name

    if audio_tensor.dim() == 1:
        audio_tensor = audio_tensor.unsqueeze(0)

    torchaudio.save(temp_path, audio_tensor.cpu(), sample_rate)

    with open(temp_path, "rb") as f:
        audio_bytes = f.read()

    os.unlink(temp_path)
    return base64.b64encode(audio_bytes).decode()

def handler(event):
    """
    Input:
        - prompt: Text to synthesize
        - audio_base64: Base64-encoded reference audio (WAV)
        - sample_rate: Sample rate of input audio (default 24000)

    Output:
        - audio_base64: Base64-encoded output WAV
        - sample_rate: 24000
    """
    try:
        input_data = event.get("input", {})
        prompt = input_data.get("prompt", "")
        audio_b64 = input_data.get("audio_base64", "")
        input_sr = input_data.get("sample_rate", 24000)

        if not prompt:
            return {"error": "No prompt provided"}
        if not audio_b64:
            return {"error": "No audio_base64 provided"}

        # Decode base64 audio to temp file
        audio_bytes = base64.b64decode(audio_b64)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_input = f.name

        # Load audio
        reference_audio, sr = torchaudio.load(temp_input)
        os.unlink(temp_input)

        # Resample to 24kHz if needed
        if sr != 24000:
            reference_audio = torchaudio.functional.resample(reference_audio, sr, 24000)

        # Initialize model
        tts = initialize_model()

        # Generate
        output_wav = tts.generate(
            text=prompt,
            audio_prompt=reference_audio,
        )

        # Convert to base64
        output_b64 = audio_tensor_to_base64(output_wav, 24000)

        return {
            "audio_base64": output_b64,
            "sample_rate": 24000
        }

    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
