from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = FastAPI(title="Retriever Agent")

# In-memory storage
news_db = []  # List of dicts: {headline, summary, url}
embeddings = None  # np.ndarray
faiss_index = None
model = SentenceTransformer('all-MiniLM-L6-v2')

class NewsItem(BaseModel):
    headline: str
    summary: Optional[str] = ""
    url: Optional[str] = ""

class IngestRequest(BaseModel):
    news: List[NewsItem]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/ingest")
def ingest_news(req: IngestRequest):
    global news_db, embeddings, faiss_index
    news_db = [item.dict() for item in req.news]
    texts = [f"{item.headline}. {item.summary}" for item in req.news]
    embeddings = model.encode(texts, convert_to_numpy=True)
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(embeddings)
    return {"status": "indexed", "count": len(news_db)}

@app.post("/search")
def search_news(req: SearchRequest):
    if faiss_index is None or embeddings is None or not news_db:
        raise HTTPException(status_code=400, detail="No news indexed yet.")
    query_emb = model.encode([req.query], convert_to_numpy=True)
    D, I = faiss_index.search(query_emb, req.top_k)
    
    # Combine results with their distances
    scored_results = []
    for i, d in zip(I[0], D[0]):
        if i < len(news_db): # Ensure index is valid
            result_item = news_db[i]
            scored_results.append({"news_item": result_item, "distance": float(d)})
    return {"results": scored_results} 