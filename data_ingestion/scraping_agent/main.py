from fastapi import FastAPI, Query
import yfinance as yf

app = FastAPI(title="Scraping Agent - Asia Tech News")

@app.get("/news")
def get_todays_news(ticker: str = Query(..., description="Stock ticker symbol")):
    stock = yf.Ticker(ticker)
    news_items = stock.news
    articles = []
    for item in news_items:
        content = item.get("content", {})
        headline = content.get("title", "")
        url = ""
        if content.get("canonicalUrl") and content["canonicalUrl"].get("url"):
            url = content["canonicalUrl"]["url"]
        elif content.get("clickThroughUrl") and content["clickThroughUrl"].get("url"):
            url = content["clickThroughUrl"]["url"]
        articles.append({
            "headline": headline,
            "url": url
        })
    return {"ticker": ticker, "news": articles} 