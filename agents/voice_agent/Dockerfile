# Dockerfile (voice_agent)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agents/voice_agent/ agents/voice_agent/
EXPOSE 8006
CMD ["uvicorn", "agents.voice_agent.main:app", "--host", "0.0.0.0", "--port", "8006"] 