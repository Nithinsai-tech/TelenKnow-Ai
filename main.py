from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage
import json
from rag_engine import get_rag_chain

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
    description="A semantic retrieval system for telecom technical documentation.",
    version="1.0.0",
    lifespan=lifespan,
)

# -------------------------------------------------------
# CORS — allow ALL origins so Vercel and localhost work
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Models
# -------------------------------------------------------
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    confidence: Optional[float] = None
    sources_meta: Optional[List[Dict[str, Optional[object]]]] = []


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy" if rag_chain is not None else "unhealthy",
        "engine_ready": rag_chain is not None,
    }


@app.post("/index-sample-docs")
def index_documents():
    """
    Documents are pre-indexed in the chroma_db folder committed to GitHub.
    Re-indexing on Railway exceeds available memory on the free tier.
    This endpoint confirms the existing index is ready.
    """
    global rag_chain
    if rag_chain is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Engine not initialized.",
        )
    return {
        "message": "Documents already indexed and ready.",
        "details": {"status": "success"},
    }


@app.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Query the RAG system for a context-aware answer."""
    if rag_chain is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Engine not initialized.",
        )

    try:
        print(f"Processing query: {request.question}")

        # Format chat history
        formatted_history = []
        for msg in request.chat_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role in ("user", "human"):
                formatted_history.append(HumanMessage(content=content))
            elif role in ("ai", "assistant"):
                formatted_history.append(AIMessage(content=content))

        result = rag_chain.invoke({
            "input": request.question,
            "chat_history": formatted_history,
        })

        answer_text = ""
        confidence = None
        sources_display = []
        sources_meta = []

        raw_answer = result.get("answer", "") if isinstance(result, dict) else ""

        # Try to parse JSON output from the model
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
                    answer_text = "\n".join(f"{k}: {v}" for k, v in ans_field.items())
                else:
                    answer_text = str(ans_field)
            else:
                answer_text = raw_answer or ""
        except Exception:
            answer_text = raw_answer or ""

        # Fall back to context metadata if model didn't return structured sources
        if not sources_meta and isinstance(result, dict) and "context" in result:
            for doc in result["context"]:
                meta = (
                    getattr(doc, "metadata", {})
                    if hasattr(doc, "metadata")
                    else doc.get("metadata", {})
                )
                sources_meta.append({
                    "source": meta.get("source") or meta.get("filename") or "Unknown",
                    "chunk": meta.get("chunk") or meta.get("page"),
                    "similarity": meta.get("score") or meta.get("similarity"),
                })

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

        if not answer_text or not answer_text.strip():
            answer_text = "Insufficient context."
            confidence = 0.0

        return QueryResponse(
            question=request.question,
            answer=answer_text,
            sources=sources_display,
            confidence=confidence,
            sources_meta=sources_meta,
        )

    except Exception as e:
        import traceback
        print(f"ERROR processing query: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)