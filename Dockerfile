# Root Dockerfile that delegates to orchestrator/Dockerfile
FROM python:3.10-slim-buster

WORKDIR /app

# Copy the orchestrator folder contents into /app
COPY orchestrator/ .

# Copy all necessary files from the root (since build context is .)
COPY requirements.txt .
COPY gradio_app/ ./gradio_app/
COPY audio_outputs/ ./audio_outputs/
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["python", "gradio_app/app.py", "--host", "0.0.0.0", "--port", "7860", "--share", "False"]
