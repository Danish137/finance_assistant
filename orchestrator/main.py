from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="Orchestrator - Market Brief Workflow")

# --- Agent Endpoints (Update these if your agents run on different ports/hosts) ---
API_AGENT_URL = "http://api-agent.railway.internal"
SCRAPING_AGENT_URL = "http://scraping-agent.railway.internal"
RETRIEVER_AGENT_URL = "http://retriever-agent.railway.internal"
ANALYSIS_AGENT_URL = "http://analysis-agent.railway.internal"
LANGUAGE_AGENT_URL = "http://language-agent.railway.internal"
VOICE_AGENT_URL = "http://voice-agent.railway.internal"

# Mock data for portfolio (since we don't have a live API yet)
MOCK_PORTFOLIO_DATA = {
    "total_aum": 1000.0,
    "asia_tech_holdings_today": 220.0,
    "asia_tech_holdings_yesterday": 180.0
}

@app.post("/generate_market_brief")
async def generate_market_brief(user_query: Optional[str] = None):
    try:
        # 1. Get Portfolio Data (Mocked for now)
        portfolio_data = MOCK_PORTFOLIO_DATA
        print(f"[Orchestrator] Using mock portfolio data: {portfolio_data}")

        # 2. Call Scraping Agent to get news
        # Ticker symbols for Asia tech stocks (example)
        asia_tech_tickers = ["TSM", "005930.KS"] # TSMC, Samsung Electronics
        all_news = []

        # Collect earnings surprises from API Agent
        all_earnings_surprises = []
        for ticker in asia_tech_tickers:
            print(f"[Orchestrator] Calling API Agent for earnings surprise on {ticker}...")
            try:
                earnings_response = requests.get(f"{API_AGENT_URL}/earnings_surprise?ticker={ticker}")
                earnings_response.raise_for_status()
                earnings_data = earnings_response.json().get("earnings_surprises", [])
                # Add company ticker to each earnings surprise for easier processing later
                for item in earnings_data:
                    item["ticker"] = ticker
                all_earnings_surprises.extend(earnings_data)
            except requests.exceptions.RequestException as e:
                print(f"[Orchestrator] Warning: Could not retrieve earnings for {ticker}: {e}")
                continue

        print(f"[Orchestrator] Retrieved {len(all_earnings_surprises)} earnings surprises from API Agent.")

        # Manually inject Samsung's mock earnings surprise as AlphaVantage does not provide it for 005930.KS
        mock_samsung_earnings = {
            "fiscal_date": "2024-06-30",
            "reported_eps": 1.50,
            "estimated_eps": 1.47,
            "surprise_abs": 0.03,
            "surprise_percent": 2.04,
            "type": "beat",
            "ticker": "005930.KS" # Ensure the ticker matches what's expected by Analysis Agent for Samsung
        }
        all_earnings_surprises.append(mock_samsung_earnings)
        print("[Orchestrator] Injected mock Samsung earnings surprise for demo purposes.")

        for ticker in asia_tech_tickers:
            print(f"[Orchestrator] Calling Scraping Agent for news on {ticker}...")
            scraping_response = requests.get(f"{SCRAPING_AGENT_URL}/news?ticker={ticker}")
            scraping_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            news_data = scraping_response.json().get("news", [])
            # Add a basic summary for each news item, as yfinance news often lacks detailed summaries
            for item in news_data:
                item["summary"] = item["headline"] # For now, use headline as summary for ingestion
            all_news.extend(news_data)
        print(f"[Orchestrator] Retrieved {len(all_news)} news items from Scraping Agent.\nFull news from Scraping Agent: {all_news[:2] if len(all_news) > 2 else all_news}") # Print first 2 or all

        if not all_news:
            raise HTTPException(status_code=500, detail="No news retrieved from Scraping Agent.")

        # 3. Call Retriever Agent to ingest news
        print("[Orchestrator] Ingesting news into Retriever Agent...")
        ingest_response = requests.post(f"{RETRIEVER_AGENT_URL}/ingest", json={"news": all_news})
        ingest_response.raise_for_status()
        print("[Orchestrator] News ingested into Retriever Agent.")

        # 4. Call Retriever Agent to search for relevant news
        # Queries based on the portfolio manager's prompt
        if user_query:
            main_search_query = user_query
            print(f"[Orchestrator] Using user-provided query for general news search: {user_query}")
        else:
            main_search_query = "risk exposure in Asia tech stocks today"
            print(f"[Orchestrator] Using default query for general news search: {main_search_query}")

        query_earnings_surprises = "earnings surprises in Asia tech stocks"

        print(f"[Orchestrator] Searching Retriever Agent for: {main_search_query}")
        search_risk_response = requests.post(f"{RETRIEVER_AGENT_URL}/search", json={"query": main_search_query, "top_k": 5})
        search_risk_response.raise_for_status()
        # Retrieve results; each item is now {'news_item': {...}, 'distance': float}
        risk_results_with_scores = search_risk_response.json().get("results", [])

        print(f"[Orchestrator] Searching Retriever Agent for: {query_earnings_surprises}")
        search_earnings_response = requests.post(f"{RETRIEVER_AGENT_URL}/search", json={"query": query_earnings_surprises, "top_k": 5})
        search_earnings_response.raise_for_status()
        earnings_results_with_scores = search_earnings_response.json().get("results", [])

        combined_relevant_news = []
        seen_urls = set()
        CONFIDENCE_THRESHOLD = 1.5 # Adjusted threshold: Lower distance means higher confidence. Increased to be less strict.

        # Process results with scores and filter by confidence
        for search_result_list in [risk_results_with_scores, earnings_results_with_scores]:
            for scored_item in search_result_list:
                news_item = scored_item.get("news_item")
                distance = scored_item.get("distance", float('inf'))

                if news_item and news_item.get("url") and distance < CONFIDENCE_THRESHOLD:
                    if news_item["url"] not in seen_urls:
                        combined_relevant_news.append(news_item)
                        seen_urls.add(news_item["url"])

        print(f"[Orchestrator] Retrieved {len(combined_relevant_news)} relevant news items (above threshold) from Retriever Agent.\nRelevant news for Analysis Agent: {combined_relevant_news}")

        # Fallback logic: if no relevant news items are found after filtering by confidence
        if not combined_relevant_news:
            generated_brief_text = "Today's market brief is limited due to low confidence in retrieving relevant information. Please try a different query or check data sources for more details."
            print(f"[Orchestrator] Triggering fallback: {generated_brief_text}")
            voice_filename = "fallback_brief.wav" # A different filename for fallback audio
            voice_payload = {"text": generated_brief_text, "output_filename": voice_filename}
            voice_response = requests.post(f"{VOICE_AGENT_URL}/speak", json=voice_payload)
            voice_response.raise_for_status()
            print(f"[Orchestrator] Fallback voice brief generated: {voice_filename}")

            return {
                "status": "fallback_success",
                "brief_text": generated_brief_text,
                "audio_file": voice_filename
            }
        else:
            # Continue with the normal workflow (original code from here)
            # 5. Call Analysis Agent
            print("[Orchestrator] Calling Analysis Agent...")
            analysis_payload = {
                "portfolio": portfolio_data,
                "news": combined_relevant_news,
                "earnings_surprises": all_earnings_surprises # Pass structured earnings data
            }
            analysis_response = requests.post(f"{ANALYSIS_AGENT_URL}/analyze", json=analysis_payload)
            analysis_response.raise_for_status()
            analysis_output = analysis_response.json()
            print(f"[Orchestrator] Analysis Agent output: {analysis_output}")

            # 6. Call Language Agent
            print("[Orchestrator] Calling Language Agent...")
            language_payload = analysis_output # Direct pass of analysis output
            language_response = requests.post(f"{LANGUAGE_AGENT_URL}/generate_brief", json=language_payload)
            language_response.raise_for_status()
            generated_brief_text = language_response.json().get("brief", "")
            print(f"[Orchestrator] Generated brief: {generated_brief_text}")

            # 7. Call Voice Agent
            print("[Orchestrator] Calling Voice Agent...")
            voice_filename = "market_brief.wav" # Original brief filename
            voice_payload = {"text": generated_brief_text, "output_filename": voice_filename}
            voice_response = requests.post(f"{VOICE_AGENT_URL}/speak", json=voice_payload)
            voice_response.raise_for_status()
            # Retrieve the base64 encoded audio from the voice agent response
            audio_base64 = voice_response.json().get("audio_base64", "")
            print(f"[Orchestrator] Voice brief generated. Audio Base64 length: {len(audio_base64) if audio_base64 else 0}")

            return {
                "status": "success",
                "brief_text": generated_brief_text,
                "audio_file": voice_filename, # Keep for backward compatibility if needed, though audio_base64 is preferred
                "audio_base64": audio_base64 # Pass base64 audio to frontend
            }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable or error in agent communication: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}") 