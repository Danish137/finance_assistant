# Scraping Agent (Asia Tech News)

This FastAPI microservice provides an endpoint to fetch today's news headlines for a given Asia tech stock ticker from Yahoo Finance.

## Endpoint
- `/news?ticker=TSM` — Get today's news headlines for a ticker

## Usage
Run with:
```
uvicorn data_ingestion.scraping_agent.main:app --reload --port 8002
``` 