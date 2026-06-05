from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.chains import create_retrieval_chain
import json
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
        raise
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
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],  # Specific dev origins
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
    confidence: Optional[float] = None
    sources_meta: Optional[List[Dict[str, Optional[object]]]] = []

# Endpoints
@app.get("/health")
def health():
    """Health check endpoint."""
    status = {
        "status": "healthy" if rag_chain is not None else "unhealthy",
        "engine_ready": rag_chain is not None
    }
    if rag_chain is None:
        status["message"] = "RAG Engine not initialized. Check server logs for startup errors."
    return status

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
            detail="RAG Engine is not initialized. Please click 'Index Sample Docs' or ensure the backend started successfully."
        )
    
    try:
        print(f"Processing query: {request.question}")
        
        # Format chat history for LangChain
        formatted_history = []
        for msg in request.chat_history:
            if msg.get("role") == "user" or msg.get("role") == "human":
                formatted_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "ai" or msg.get("role") == "assistant":
                formatted_history.append(AIMessage(content=msg.get("content", "")))

        # Invoke the RAG chain
        print("Invoking RAG chain...")
        result = rag_chain.invoke({
            "input": request.question,
            "chat_history": formatted_history
        })
        print(f"RAG chain response received")
        
        # Default empty
        answer_text = ""
        confidence = None
        sources_display = []
        sources_meta = []

        # The chain's `answer` may be plain text or a JSON string following our stricter prompt.
        raw_answer = result.get("answer", "") if isinstance(result, dict) else ""

        # Try to parse JSON output from the model. Handle nested JSON strings robustly.
        try:
            parsed = json.loads(raw_answer)
            if isinstance(parsed, str):
                try:
                    parsed = json.loads(parsed)
                except Exception:
                    pass

            if isinstance(parsed, dict):
                ans_field = parsed.get("answer", "")
                confidence = parsed.get("confidence")
                sources_meta = parsed.get("sources", []) or []

                if isinstance(ans_field, dict):
                    lines = [f"{k}: {v}" for k, v in ans_field.items()]
                    answer_text = "\n".join(lines)
                else:
                    answer_text = str(ans_field)
            else:
                answer_text = raw_answer or ""
        except Exception:
            answer_text = raw_answer or ""

        # If model didn't return structured sources, extract metadata from retrieval context
        if not sources_meta and isinstance(result, dict) and "context" in result:
            for doc in result["context"]:
                meta = getattr(doc, "metadata", {}) if hasattr(doc, "metadata") else doc.get("metadata", {})
                source_name = meta.get("source") or meta.get("filename") or "Unknown"
                chunk = meta.get("chunk") or meta.get("page") or None
                similarity = meta.get("score") or meta.get("similarity") or None
                sources_meta.append({"source": source_name, "chunk": chunk, "similarity": similarity})

        # Build human-friendly sources display lines
        for s in sources_meta:
            src = s.get("source", "Unknown")
            chunk = s.get("chunk")
            sim = s.get("similarity")
            parts = [f"Source: {src}"]
            if chunk is not None:
                parts.append(f"Chunk: {chunk}")
            if sim is not None:
                try:
                    parts.append(f"Similarity: {float(sim):.2f}")
                except Exception:
                    parts.append(f"Similarity: {sim}")
            sources_display.append(": ".join(parts))

        if not sources_display and sources_meta:
            sources_display = [f"Source: {s.get('source', 'Unknown')}" for s in sources_meta]

        if not answer_text or answer_text.strip() == "":
            answer_text = "Insufficient context."
            confidence = 0.0

        return QueryResponse(
            question=request.question,
            answer=answer_text,
            sources=sources_display,
            confidence=confidence,
            sources_meta=sources_meta
        )
    except Exception as e:
        print(f"ERROR processing query: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8002)
