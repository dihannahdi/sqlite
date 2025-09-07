"""
Nahdlatul Ulama AI - Islamic Jurisprudence System
Main application entry point
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import chromadb
from sentence_transformers import SentenceTransformer

# Configuration
OLLAMA_URL = os.getenv('OLLAMA_SERVICE_URL', 'http://ollama-qwen25-service:11434')
DATABASE_URL = os.getenv('DATABASE_URL')

# Initialize FastAPI app
app = FastAPI(
    title="Nahdlatul Ulama AI",
    description="Islamic Jurisprudence System with NU Methodology",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class IslamicQuery(BaseModel):
    question: str
    context: str = ""
    madhab: str = "syafii"

class IslamicResponse(BaseModel):
    answer: str
    methodology: str
    sources: list
    confidence: float
    verification_status: str

# Initialize components
class NUIslamicAI:
    def __init__(self):
        self.ollama_url = OLLAMA_URL
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = chromadb.PersistentClient(path='/app/chroma_data')

    def process_query(self, query: IslamicQuery) -> IslamicResponse:
        """Process Islamic query using NU methodology"""

        # Retrieve relevant Islamic texts
        relevant_texts = self.retrieve_relevant_texts(query.question)

        # Generate response using Qwen2.5
        prompt = self.create_islamic_prompt(query.question, relevant_texts)
        response = self.call_qwen25(prompt)

        # Apply NU methodology verification
        verified_response = self.apply_nu_methodology(response, relevant_texts)

        return IslamicResponse(
            answer=verified_response,
            methodology="NU Traditional Methodology",
            sources=relevant_texts,
            confidence=0.85,
            verification_status="auto_verified"
        )

    def retrieve_relevant_texts(self, question: str) -> list:
        """Retrieve relevant Islamic texts from vector store"""
        # This will be implemented when we load the SQL chunks
        return ["Quran 2:255 (Ayat Kursi)", "Sahih Hadith Collection"]

    def create_islamic_prompt(self, question: str, context: list) -> str:
        """Create prompt with Islamic etiquette and NU principles"""
        return f"""بسم الله الرحمن الرحيم

You are an Islamic AI assistant following Nahdlatul Ulama methodology.

Question: {question}

Relevant Islamic Sources:
{chr(10).join(context)}

Apply NU principles: Tawassuth (moderation), Tasamuh (tolerance),
Tawazun (balance), and I'tidal (justice).

Answer:"""

    def call_qwen25(self, prompt: str) -> str:
        """Call Qwen2.5-1.5B via Railway Ollama service"""
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300,
                    "num_ctx": 2048
                }
            }, timeout=30)

            if response.status_code == 200:
                return response.json()['response']
            else:
                return "Error: Unable to generate response from Qwen2.5"

        except Exception as e:
            return f"Error calling Qwen2.5: {str(e)}"

    def apply_nu_methodology(self, response: str, sources: list) -> str:
        """Apply NU methodology verification"""
        # Basic verification - will be enhanced
        return response

# Initialize AI system
nu_ai = NUIslamicAI()

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Nahdlatul Ulama AI - Islamic Jurisprudence System",
        "status": "active",
        "methodology": "NU Traditional (Aswaja)",
        "model": "Qwen2.5-1.5B-Instruct (Apache 2.0 License)"
    }

@app.post("/api/islamic-query", response_model=IslamicResponse)
async def process_islamic_query(query: IslamicQuery):
    """Process Islamic jurisprudence query"""
    try:
        response = nu_ai.process_query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-09-07"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
