from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from rag_engine import get_rag_chain
from ingest import ingest_docs

# Global variable for the RAG chain
rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the RAG chain on API startup."""
    global rag_chain
    try:
        rag_chain = get_rag_chain()
        print("RAG Engine successfully initialized.")
    except Exception as e:
        print(f"CRITICAL: RAG Engine failed to initialize: {e}")
    yield

# Initialize FastAPI App
app = FastAPI(
    title="Telecom Support RAG API",
    description="A semantic retrieval system for telecom technical documentation using Groq and ChromaDB.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



# Models
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]

# Endpoints
@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "engine_ready": rag_chain is not None
    }

@app.post("/index-sample-docs")
def index_documents():
    """Endpoint to trigger document ingestion."""
    try:
        ingest_docs()
        
        # Re-initialize the RAG chain with the new data
        global rag_chain
        rag_chain = get_rag_chain()
        
        return {
            "message": "Documents indexed successfully.",
            "details": {"status": "success"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Query the RAG system for a context-aware answer.
    """
    if rag_chain is None:
        raise HTTPException(
            status_code=503, 
            detail="RAG Engine is not initialized. Ensure documents are ingested."
        )
    
    try:
        # Format chat history for LangChain
        formatted_history = []
        for msg in request.chat_history:
            if msg.get("role") == "user" or msg.get("role") == "human":
                formatted_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "ai" or msg.get("role") == "assistant":
                formatted_history.append(AIMessage(content=msg.get("content", "")))

        # Invoke the RAG chain
        result = rag_chain.invoke({
            "input": request.question,
            "chat_history": formatted_history
        })
        
        # Extract source metadata
        sources = []
        if "context" in result:
            sources = list(set([doc.metadata.get("source", "Unknown") for doc in result["context"]]))

        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
