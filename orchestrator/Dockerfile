# Dockerfile (orchestrator)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY orchestrator/ orchestrator/
COPY agents/ agents/
COPY data_ingestion/ data_ingestion/
EXPOSE 8000
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]