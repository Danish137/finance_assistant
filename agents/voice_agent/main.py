from fastapi import FastAPI, Response
from pydantic import BaseModel
import pyttsx3
import os
import base64
from fastapi import HTTPException

app = FastAPI(title="Voice Agent - Text-to-Speech")

class SpeakRequest(BaseModel):
    text: str
    output_filename: str = "output.wav"

@app.post("/speak")
def speak_text(req: SpeakRequest):
    engine = pyttsx3.init()
    # Set properties (optional)
    # engine.setProperty('rate', 150)    # Speed percent (can be 100-300)
    # engine.setProperty('volume', 0.9)  # Volume 0-1

    output_path = os.path.join("audio_outputs", req.output_filename)
    os.makedirs("audio_outputs", exist_ok=True)

    engine.save_to_file(req.text, output_path)
    engine.runAndWait()

    # Read the generated WAV file and encode it to base64
    with open(output_path, "rb") as audio_file:
        encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

    # Clean up the generated audio file
    os.remove(output_path)

    return {"status": "success", "audio_base64": encoded_audio, "message": f"Audio saved to {output_path}"}

# TODO: Speech-to-Text (STT) integration (e.g., using whisper.cpp or a cloud API)
# This would be a separate endpoint if needed for voice input to the orchestrator. 