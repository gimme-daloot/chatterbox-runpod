# Chatterbox TTS RunPod Endpoint

Accepts base64 audio as reference for voice cloning.

## Input
```json
{
  "input": {
    "prompt": "Text to speak",
    "audio_base64": "base64-encoded WAV"
  }
}
```

## Output
```json
{
  "audio_base64": "base64-encoded WAV",
  "sample_rate": 24000
}
```
