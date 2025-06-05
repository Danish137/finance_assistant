from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd

app = FastAPI(title="Analysis Agent - Risk & Earnings")

class PortfolioData(BaseModel):
    total_aum: float
    asia_tech_holdings_today: float
    asia_tech_holdings_yesterday: float

class NewsItem(BaseModel):
    headline: str
    summary: Optional[str] = ""
    url: Optional[str] = ""

class EarningsSurpriseItem(BaseModel):
    fiscal_date: str
    reported_eps: float
    estimated_eps: float
    surprise_abs: float
    surprise_percent: float
    type: str
    ticker: str

class AnalysisRequest(BaseModel):
    portfolio: PortfolioData
    news: List[NewsItem]
    earnings_surprises: List[EarningsSurpriseItem] = []

@app.post("/analyze")
def analyze_market_brief(req: AnalysisRequest):
    # 1. Calculate Asia Tech Allocation
    asia_tech_allocation = (req.portfolio.asia_tech_holdings_today / req.portfolio.total_aum) * 100
    asia_tech_allocation_yesterday = (req.portfolio.asia_tech_holdings_yesterday / req.portfolio.total_aum) * 100
    allocation_change = asia_tech_allocation - asia_tech_allocation_yesterday

    processed_earnings_surprises = []
    if req.earnings_surprises:
        # Convert to DataFrame for easier processing
        df_all_earnings = pd.DataFrame([es.model_dump() for es in req.earnings_surprises])
        
        # Ensure fiscal_date is datetime for proper sorting
        df_all_earnings['fiscal_date'] = pd.to_datetime(df_all_earnings['fiscal_date'])
        
        # Sort by fiscal_date (descending) and then drop duplicates by ticker
        # This keeps the most recent entry for each ticker
        df_recent_earnings = df_all_earnings.sort_values(by=['ticker', 'fiscal_date'], ascending=[True, False])\
                                            .drop_duplicates(subset=['ticker'], keep='first')
        
        for _, es_item in df_recent_earnings.iterrows():
            company_name = "Unknown Company"
            if es_item.ticker == "TSM":
                company_name = "TSMC"
            elif es_item.ticker == "005930.KS":
                company_name = "Samsung"

            processed_earnings_surprises.append({
                "company": company_name,
                "type": es_item.type,
                "percentage": es_item.surprise_percent # Use the percentage directly
            })

    # Example of using pandas for quantitative analysis
    if processed_earnings_surprises:
        df_earnings = pd.DataFrame(processed_earnings_surprises)
        # For demonstration, calculate average surprise percentage (can be further expanded)
        avg_surprise_percent = df_earnings['percentage'].mean()
        print(f"[Analysis Agent] Pandas DataFrame created for earnings: {df_earnings.head()}")
        print(f"[Analysis Agent] Average earnings surprise: {avg_surprise_percent:.2f}%")

    # Regional sentiment is a placeholder for now
    regional_sentiment = "neutral with a cautionary tilt due to rising yields."

    return {
        "asia_tech_allocation": asia_tech_allocation,
        "allocation_change": allocation_change,
        "earnings_surprises": processed_earnings_surprises,
        "regional_sentiment": regional_sentiment
    } 