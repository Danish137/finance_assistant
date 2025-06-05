# Dockerfile (language_agent)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agents/language_agent/ agents/language_agent/
EXPOSE 8005
CMD ["uvicorn", "agents.language_agent.main:app", "--host", "0.0.0.0", "--port", "8005"] 