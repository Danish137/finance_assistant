# Multi-Agent Finance Assistant

A modular, open-source finance assistant designed to deliver personalized, spoken morning market briefs. This project leverages a multi-agent orchestration framework, Retrieval-Augmented Generation (RAG), and a robust voice pipeline to provide portfolio managers with concise, actionable insights into risk exposure and earnings surprises in Asia tech stocks.

## Features

*   **Spoken Market Briefs:** Delivers audio summaries of market conditions and key events.
*   **Multi-Agent Architecture:** Specialized FastAPI microservices for API integration, web scraping, data retrieval, analytics, natural language generation, and text-to-speech.
*   **Data Ingestion:** Gathers financial data via APIs (yfinance, AlphaVantage) and web scraping (Yahoo Finance News).
*   **RAG Implementation:** Utilizes vector embeddings (Sentence-Transformers) and a vector store (FAISS) for efficient information retrieval.
*   **Dynamic Querying:** Supports user-specified queries for personalized brief generation.
*   **Open-Source & Free:** Built entirely with open-source and free-to-use technologies.

## Architecture

The system is composed of a Streamlit frontend, a central Orchestrator, and several specialized FastAPI microservices acting as agents.

```mermaid
graph TD;
    User[User] -->|Voice/Text Query| StreamlitApp(Streamlit App);
    StreamlitApp -->|Generate Brief Request| Orchestrator(Orchestrator Service);

    Orchestrator --> APIAgent(API Agent);
    Orchestrator --> ScrapingAgent(Scraping Agent);
    Orchestrator --> RetrieverAgent(Retriever Agent);
    Orchestrator --> AnalysisAgent(Analysis Agent);
    Orchestrator --> LanguageAgent(Language Agent);
    Orchestrator --> VoiceAgent(Voice Agent);

    APIAgent --> YF[yfinance / AlphaVantage APIs];
    ScrapingAgent --> YahooNews[Yahoo Finance News];
    RetrieverAgent --> FAISS[FAISS Vector Store];
    RetrieverAgent --> SBERT[Sentence-Transformers];
    AnalysisAgent --> Pandas[Pandas / Numpy];
    LanguageAgent --> LLM[LLM (LangChain)];
    VoiceAgent --> PyTTSX3[pyttsx3];

    Orchestrator -->|Brief Text & Audio| StreamlitApp;
    StreamlitApp -->|Spoken Brief| User;
```
**Note:** If the diagram above does not render correctly, you can copy the Mermaid code block and paste it into an online Mermaid editor (e.g., [Mermaid Live Editor](https://mermaid.live/)) to view the diagram.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Danish137/finance_assistant.git
    cd finance_assistant
    ```
2.  **Create and activate a virtual environment (Conda recommended):**
    ```bash
    conda create -n finance-assistant python=3.9 -y
    conda activate finance-assistant
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file and add your API keys. Specifically, you will need:
        *   `ALPHAVANTAGE_API_KEY` for the API Agent (earnings surprise data).
        *   `GROQ_API_KEY` for the Streamlit app's speech-to-text transcription.

## Running the Application

This project runs as a collection of microservices. You need to start each agent in a separate terminal, and then start the Streamlit frontend.

**Important:** For each terminal, navigate to the respective directory and activate your `finance-assistant` conda environment before running the command.

1.  **Start the Orchestrator (from project root):**
    ```bash
    uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
    ```
2.  **Start the API Agent (from `data_ingestion/api_agent`):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ```
3.  **Start the Scraping Agent (from `data_ingestion/scraping_agent`):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8002 --reload
    ```
4.  **Start the Retriever Agent (from `agents/retriever_agent`):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8003 --reload
    ```
5.  **Start the Analysis Agent (from `agents/analysis_agent`):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8004 --reload
    ```
6.  **Start the Language Agent (from `agents/language_agent`):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8005 --reload
    ```
7.  **Start the Voice Agent (from `agents/voice_agent`):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8006 --reload
    ```
8.  **Start the Streamlit App (from `streamlit_app` directory):**
    ```bash
    streamlit run app.py
    ```

## Framework & Toolkit Choices

This project prioritizes open-source and free solutions where possible, while also selecting robust and performant libraries for each task.

*   **API Interactions:** `yfinance` for basic stock data, `AlphaVantage` for more detailed financial metrics like earnings surprises.
*   **Web Scraping:** `requests` and `BeautifulSoup` for static HTML parsing (demonstrated in `html_parser_util.py`), and `yfinance.Ticker().news` for direct news fetching.
*   **Vector Store & Embeddings:** `FAISS-cpu` (CPU-only version for local development/deployment simplicity) for efficient similarity search and `sentence-transformers` for generating high-quality embeddings.
*   **Data Analysis:** `pandas` and `numpy` for data manipulation and analysis, particularly for processing and filtering financial data.
*   **Language Models & Orchestration:** `LangChain` is the chosen framework for interfacing with Large Language Models (LLMs) and building retrieval-augmented generation (RAG) pipelines. `LangGraph` and `CrewAI` were considered for agent orchestration, but the current Orchestrator service directly manages the agent interactions for simplicity and explicit control over the flow.
*   **Text-to-Speech:** `pyttsx3` provides a local, offline text-to-speech solution compatible with Windows, addressing prior issues with `openai-whisper` and `coqui-tts` build errors.
*   **Backend Services:** `FastAPI` is used for building the RESTful microservices due to its high performance, ease of use, and automatic documentation.
*   **Frontend:** `Streamlit` provides a rapid development environment for the interactive web application.

## Deployment

This application is designed for containerized deployment, primarily using Docker. A `Dockerfile` is provided in the root directory.

Recommended deployment platforms for this multi-service architecture include:

*   **Google Cloud Run:** Ideal for serverless container deployment, automatically scales, and handles inter-service communication efficiently.
*   **AWS App Runner:** A similar service to Cloud Run, offering simplified container deployment and scaling.

Each agent would typically be deployed as a separate service on these platforms, with the Orchestrator configured to call their respective internal service URLs.

## Performance Benchmarks

*(Placeholder for future performance benchmarking results, e.g., brief generation time, transcription speed, agent response times.)* 