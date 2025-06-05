# Dockerfile (api_agent)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY data_ingestion/api_agent/ data_ingestion/api_agent/
EXPOSE 8001
CMD ["uvicorn", "data_ingestion.api_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]