# Dockerfile (analysis_agent)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agents/analysis_agent/ agents/analysis_agent/
EXPOSE 8004
CMD ["uvicorn", "agents.analysis_agent.main:app", "--host", "0.0.0.0", "--port", "8004"] 