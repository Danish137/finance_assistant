# API Agent (Market Data)

This FastAPI microservice provides endpoints to fetch real-time and historical market data using yfinance.

## Endpoints
- `/price?ticker=TSLA` — Get current price for a ticker
- `/history?ticker=TSLA&period=1mo` — Get historical data for a ticker (default: 1 month)

## Usage
Run with:
```
uvicorn data_ingestion.api_agent.main:app --reload --port 8001
``` 