from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import yfinance as yf
import requests
import os
from dotenv import load_dotenv

load_dotenv()
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

app = FastAPI(title="API Agent - Market Data")

@app.get("/price")
def get_current_price(ticker: str = Query(..., description="Stock ticker symbol")):
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")
    return {"ticker": ticker, "price": price}

@app.get("/history")
def get_historical_data(
    ticker: str = Query(..., description="Stock ticker symbol"),
    period: str = Query("1mo", description="Data period, e.g. 1d, 5d, 1mo, 3mo, 1y")
):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return {"ticker": ticker, "history": hist.reset_index().to_dict(orient="records")}

@app.get("/earnings_surprise")
def get_earnings_surprise(ticker: str = Query(..., description="Stock ticker symbol")):
    if not ALPHAVANTAGE_API_KEY:
        raise HTTPException(status_code=500, detail="AlphaVantage API key not set in .env")

    # AlphaVantage Earnings Calendar API
    # Function: EARNINGS_CALENDAR
    # Endpoint: https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol=IBM&horizon=3month&apikey=YOUR_API_KEY
    # NOTE: This API can be slow/rate-limited on the free tier.
    # For this demo, we'll use the EARNINGS (Quarterly Earnings) which gives actual vs. estimated EPS.
    
    url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker}&apikey={ALPHAVANTAGE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if "quarterlyEarnings" not in data or not data["quarterlyEarnings"]:
            return {"ticker": ticker, "earnings_surprises": []}

        surprises = []
        for q_earnings in data["quarterlyEarnings"]:
            try:
                fiscal_date = q_earnings.get("fiscalDateEnding")
                reported_eps = float(q_earnings.get("reportedEPS"))
                estimated_eps = float(q_earnings.get("estimatedEPS"))
                
                if reported_eps is not None and estimated_eps is not None:
                    surprise_abs = reported_eps - estimated_eps
                    surprise_percent = (surprise_abs / estimated_eps) * 100 if estimated_eps != 0 else 0

                    # Determine if it's a beat or missed
                    type_ = "beat" if surprise_abs > 0 else "missed" if surprise_abs < 0 else "met"

                    surprises.append({
                        "fiscal_date": fiscal_date,
                        "reported_eps": reported_eps,
                        "estimated_eps": estimated_eps,
                        "surprise_abs": surprise_abs,
                        "surprise_percent": surprise_percent,
                        "type": type_
                    })
            except (ValueError, TypeError) as e:
                print(f"[API Agent] Error parsing earnings data for {ticker}: {e} - Data: {q_earnings}")
                continue

        return {"ticker": ticker, "earnings_surprises": surprises}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error fetching data from AlphaVantage: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}") 