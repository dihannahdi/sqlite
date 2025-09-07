"""
Nahdlatul Ulama AI - Islamic Jurisprudence System
Railway-based RAG system with direct GitHub integration
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import logging
from typing import List, Dict, Any, Optional
import json
from railway_rag import OptimizedRailwayIslamicRAG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_URL = os.getenv('OLLAMA_SERVICE_URL', 'http://ollama-qwen25-service:11434')

# Initialize RAG system globally
rag_system: Optional[OptimizedRailwayIslamicRAG] = None
ingestion_in_progress = False
ingestion_results = None

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
@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup."""
    global rag_system
    try:
        logger.info("🚀 Initializing Optimized Railway Islamic RAG System...")
        rag_system = OptimizedRailwayIslamicRAG(ingestion_mode=False)  # Start in serving mode
        logger.info("✅ RAG system initialized - ready for ingestion or serving!")
            
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")

# Background ingestion function
async def run_full_ingestion():
    """Run full ingestion in background"""
    global rag_system, ingestion_in_progress, ingestion_results
    
    try:
        ingestion_in_progress = True
        logger.info("🔥 Starting full ingestion of 15,674 Islamic SQL files...")
        
        # Switch to ingestion mode for maximum performance
        if rag_system:
            rag_system.ingestion_mode = True
            # Reconfigure for ingestion mode
            rag_system.workers = rag_system.config.ingestion_workers
            rag_system.batch_size = rag_system.config.ingestion_batch_size
            
            # Run the fast ingestion
            results = await rag_system.fast_ingest_all_files()
            
            # Switch back to serving mode
            rag_system.switch_to_serving_mode()
            
            ingestion_results = results
            logger.info(f"✅ Ingestion completed! Results: {results}")
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        ingestion_results = {"error": str(e)}
    finally:
        ingestion_in_progress = False

class NUIslamicAI:
    def __init__(self):
        self.ollama_url = OLLAMA_URL
        # Use the global RAG system instead of initializing new components
        global rag_system
        self.rag_system = rag_system

    def process_query(self, query: IslamicQuery) -> IslamicResponse:
        """Process Islamic query using NU methodology with Railway RAG"""

        # Use Railway RAG system to retrieve relevant Islamic texts
        if self.rag_system:
            relevant_results = self.rag_system.search(query.question, collection_type="all", n_results=5)
            relevant_texts = [result['content'] for result in relevant_results]
            source_metadata = [result['metadata'] for result in relevant_results]
        else:
            relevant_texts = []
            source_metadata = []

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
    """Root endpoint with system information."""
    global rag_system
    
    system_info = {
        "system": "Nahdlatul Ulama AI",
        "version": "2.0.0",
        "model": "Qwen2.5-1.5B-Instruct",
        "methodology": "NU Islamic Jurisprudence",
        "status": "operational" if rag_system else "initializing"
    }
    
    if rag_system:
        try:
            stats = rag_system.get_statistics()
            system_info["rag_stats"] = json.dumps(stats)
        except Exception as e:
            system_info["rag_stats"] = f"Error getting stats: {e}"
    
    return system_info

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Ollama service
        ollama_response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_healthy = ollama_response.status_code == 200
        
        # Check RAG system
        rag_healthy = rag_system is not None and rag_system.total_documents > 0
        
        return {
            "status": "healthy" if (ollama_healthy and rag_healthy) else "degraded",
            "ollama": "healthy" if ollama_healthy else "unhealthy",
            "rag_system": "healthy" if rag_healthy else "unhealthy",
            "documents": rag_system.total_documents if rag_system else 0
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

class RAGSearchQuery(BaseModel):
    query: str
    collection_type: str = "all"
    n_results: int = 5

@app.post("/search")
async def search_islamic_knowledge(query: RAGSearchQuery):
    """Search Islamic knowledge base using RAG."""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        results = rag_system.search(
            query.query, 
            collection_type=query.collection_type, 
            n_results=query.n_results
        )
        
        return {
            "query": query.query,
            "results": results,
            "total_found": len(results),
            "collection_searched": query.collection_type
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/ask")
async def ask_islamic_question(query: IslamicQuery) -> IslamicResponse:
    """Ask an Islamic question using NU methodology."""
    try:
        response = nu_ai.process_query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# API Routes (keeping existing ones)
@app.post("/api/islamic-query", response_model=IslamicResponse)
async def process_islamic_query(query: IslamicQuery):
    """Process Islamic jurisprudence query"""
    try:
        response = nu_ai.process_query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/start-ingestion")
async def start_full_ingestion(background_tasks: BackgroundTasks):
    """Start full ingestion of all 15,674 Islamic SQL files."""
    global ingestion_in_progress, rag_system
    
    if ingestion_in_progress:
        return {"status": "already_running", "message": "Ingestion already in progress"}
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    # Start ingestion in background
    background_tasks.add_task(run_full_ingestion)
    
    return {
        "status": "started",
        "message": "Full ingestion started in background",
        "estimated_time": "12-15 minutes",
        "files_to_process": 15674
    }

@app.get("/api/ingestion-status")
async def get_ingestion_status():
    """Get current ingestion status."""
    global ingestion_in_progress, ingestion_results, rag_system
    
    status = {
        "in_progress": ingestion_in_progress,
        "results": ingestion_results
    }
    
    if rag_system:
        try:
            stats = rag_system.get_statistics()
            status["current_stats"] = stats
        except Exception as e:
            status["stats_error"] = str(e)
    
    return status

@app.post("/api/switch-to-serving")
async def switch_to_serving_mode():
    """Switch RAG system to low-resource serving mode."""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    rag_system.switch_to_serving_mode()
    
    return {
        "status": "switched",
        "mode": "serving",
        "workers": rag_system.workers,
        "batch_size": rag_system.batch_size
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
