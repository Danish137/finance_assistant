import os
import logging
import requests
import base64
from dotenv import load_dotenv
from groq import Groq
import gradio as gr
import numpy as np
import soundfile as sf
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load GROQ API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Please check your .env file.")

ORCHESTRATOR_URL = "http://127.0.0.1:8007"

# Transcription function
def transcribe_with_groq(audio_filepath):
    client = Groq(api_key=GROQ_API_KEY)

    if not os.path.exists(audio_filepath):
        return "Audio file not found."

    try:
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=audio_file,
                language="en"
            )
        return transcription.text
    except Exception as e:
        return f"Error transcribing audio: {e}"

# Main function to handle audio and generate brief
def process_audio_and_generate_brief(audio):
    print("[Gradio App DEBUG] ***Function process_audio_and_generate_brief entered!***")
    print(f"[Gradio App DEBUG] Raw audio input: {audio is not None}")
    # audio is a tuple: (sample_rate, numpy array)
    if audio is None:
        print("[Gradio App DEBUG] Audio input is None.")
        return "Please record audio first.", None, None

    # Save uploaded audio as WAV to temp file
    audio_output_dir = "audio_outputs"
    os.makedirs(audio_output_dir, exist_ok=True)
    temp_audio_file = os.path.join(audio_output_dir, "user_query_recording.wav")

    # Gradio gives audio as (sample_rate, np_array)
    sample_rate, audio_data = audio
    sf.write(temp_audio_file, audio_data, sample_rate)
    print(f"[Gradio App DEBUG] Audio saved to: {temp_audio_file}")

    # Transcribe
    transcribed_text = transcribe_with_groq(temp_audio_file)
    print(f"[Gradio App DEBUG] Transcribed text from Groq: '{transcribed_text}'")
    if transcribed_text.startswith("Error") or transcribed_text == "Audio file not found.":
        return transcribed_text, None, None

    # Call Orchestrator
    params = {"user_query": transcribed_text} if transcribed_text else {}
    print(f"[Gradio App DEBUG] Sending params to Orchestrator: {params}")
    try:
        response = requests.post(f"{ORCHESTRATOR_URL}/generate_market_brief", json=params)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        print(f"[Gradio App DEBUG] Received response from Orchestrator. Status: {response.status_code}")
        print(f"[Gradio App DEBUG] Response JSON: {response.json()}")
        brief_data = response.json()

        if brief_data.get("status") in ["success", "fallback_success"]:
            text_brief = brief_data.get("brief_text", "No brief text available.")
            audio_brief_path = None # Will store the path to the temporary audio file
            if brief_data.get("audio_base64"):
                audio_bytes = base64.b64decode(brief_data["audio_base64"])
                print(f"[Gradio App DEBUG] First 12 bytes of decoded audio: {audio_bytes[:12].hex()}")

                # Use io.BytesIO to read the base64-decoded bytes as a file
                audio_io = io.BytesIO(audio_bytes)
                
                try:
                    # Read the audio data and sample rate. Assuming WAV from Voice Agent.
                    audio_data_np, sample_rate_sf = sf.read(audio_io)
                    
                    # Convert audio data to float32, which is a common requirement for Gradio/soundfile
                    audio_data_np = audio_data_np.astype(np.float32)

                    # Save the audio data to a temporary WAV file
                    audio_output_dir = "audio_outputs"
                    os.makedirs(audio_output_dir, exist_ok=True)
                    audio_brief_path = os.path.join(audio_output_dir, "brief_audio_output.wav")
                    
                    sf.write(audio_brief_path, audio_data_np, sample_rate_sf)
                    print(f"[Gradio App DEBUG] Audio brief saved to: {audio_brief_path}")

                except Exception as e:
                    print(f"[Gradio App ERROR] Error processing or saving audio brief: {e}")
                    audio_brief_path = None # Ensure it's None if saving fails

            return transcribed_text, text_brief, audio_brief_path # Return the path to the file
        else:
            return f"Failed to generate brief: {brief_data.get('detail', 'Unknown error')}", None, None

    except requests.exceptions.ConnectionError:
        return "Could not connect to the Orchestrator. Please ensure it is running.", None, None
    except Exception as e:
        return f"An error occurred: {e}", None, None


def echo_text(text):
    print(f"[Gradio App DEBUG - Simple Test] Received text: '{text}'")
    return f"Hello from Gradio! You said: {text}"


with gr.Blocks() as demo:
    gr.Markdown("# Multi-Agent Finance Assistant")

    audio_input = gr.Audio(label="Speak your query", sources="microphone")
    transcribed_text_output = gr.Textbox(label="Transcribed Text", interactive=False)
    text_brief_output = gr.Textbox(label="Market Brief", interactive=False)
    audio_brief_output = gr.Audio(label="Audio Brief", interactive=False, autoplay=True)

    audio_input.change(
        fn=process_audio_and_generate_brief,
        inputs=audio_input,
        outputs=[transcribed_text_output, text_brief_output, audio_brief_output]
    )

    gr.Markdown("---")
    gr.Markdown("### Agent Status Check (Ensure all agents are running in their terminals):")
    gr.Markdown(f"- **API Agent:** {ORCHESTRATOR_URL.replace(':8000', ':8001')}")
    gr.Markdown(f"- **Scraping Agent:** {ORCHESTRATOR_URL.replace(':8000', ':8002')}")
    gr.Markdown(f"- **Retriever Agent:** {ORCHESTRATOR_URL.replace(':8000', ':8003')}")
    gr.Markdown(f"- **Analysis Agent:** {ORCHESTRATOR_URL.replace(':8000', ':8004')}")
    gr.Markdown(f"- **Language Agent:** {ORCHESTRATOR_URL.replace(':8000', ':8005')}")
    gr.Markdown(f"- **Voice Agent:** {ORCHESTRATOR_URL.replace(':8000', ':8006')}")
    gr.Markdown(f"- **Orchestrator:** {ORCHESTRATOR_URL}")

if __name__ == "__main__":
    demo.launch(share=False, debug=True, show_error=True, server_name="0.0.0.0", server_port=7860)

