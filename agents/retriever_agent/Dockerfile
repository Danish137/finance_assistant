# Dockerfile (retriever_agent)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agents/retriever_agent/ agents/retriever_agent/
EXPOSE 8003
CMD ["uvicorn", "agents.retriever_agent.main:app", "--host", "0.0.0.0", "--port", "8003"] 