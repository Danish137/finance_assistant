# Dockerfile (scraping_agent)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY data_ingestion/scraping_agent/ data_ingestion/scraping_agent/
COPY data_ingestion/html_parser_util.py data_ingestion/html_parser_util.py
EXPOSE 8002
CMD ["uvicorn", "data_ingestion.scraping_agent.main:app", "--host", "0.0.0.0", "--port", "8002"] 