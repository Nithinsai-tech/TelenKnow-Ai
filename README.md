# Telecom Support RAG System

An advanced Retrieval-Augmented Generation (RAG) system built to assist telecom support agents with semantic searches of technical documentation, outage procedures, and hardware specifications.

## 🌟 Core Features
* **Multi-Format Ingestion:** Automatically parses and chunks `.md`, `.txt`, `.pdf`, and `.docx` files.
* **Local Vector Database:** Uses **ChromaDB** for fast, localized, and cost-free vector storage and similarity search.
* **Open-Source Embeddings:** Utilizes HuggingFace's `all-MiniLM-L6-v2` for high-quality, local text embeddings.
* **High-Speed Inference:** Powered by **Groq's LLaMA 3.1 8B** model for lightning-fast, context-aware answers.
* **FastAPI Backend:** Provides robust REST API endpoints (`/query`, `/index-sample-docs`, `/health`) with integrated CORS.
* **React Frontend:** A modern, dynamic UI built with Vite, TailwindCSS, and Lucide React to interface seamlessly with the backend.

---

## 🚀 Recent Upgrades (v2.0)

We have significantly upgraded the core architecture to provide an enterprise-grade user experience:

### 1. 🧠 Conversation Memory (History-Aware Retrieval)
The RAG engine is no longer stateless! It actively tracks the context of your conversation, allowing you to ask natural follow-up questions.
- **Under the hood:** We implemented LangChain's `create_history_aware_retriever`. When you ask a follow-up question (e.g., *"What is step 2?"*), the AI reads the chat history and silently rewrites your question into a standalone query (e.g., *"What is step 2 of configuring OSPF?"*) before searching the database. 

### 2. 🔍 Hybrid Search (Semantic + Keyword)
Pure semantic search is great for understanding meaning, but it can miss highly specific technical terms. We upgraded the retrieval system to use **Hybrid Search**.
- **Under the hood:** We integrated the `rank_bm25` algorithm to perform exact-keyword matching. Every time the engine starts, it builds a lightning-fast in-memory BM25 index from your ChromaDB chunks. When a question is asked, an `EnsembleRetriever` runs both searches simultaneously and merges the results using Reciprocal Rank Fusion (RRF). This guarantees we never miss specific error codes, exact voltages, or part numbers!

### 3. ✨ Beautiful Markdown UI Rendering
Raw text dumps have been completely eliminated. The frontend now actively parses the AI's output and renders proper HTML typography.
- **Under the hood:** We integrated `react-markdown` and the `@tailwindcss/typography` plugin. The AI is explicitly instructed via prompt engineering to use professional formatting, bullet points, and beginner-friendly language to explain telecom jargon, resulting in a highly polished, readable chat interface.

---

## 🏗️ Architecture Stack
* **Frontend:** React, Vite, TailwindCSS (with Typography plugin), Axios, React-Markdown
* **Backend:** Python, FastAPI, Uvicorn
* **AI/ML Layer:** LangChain, HuggingFace (`sentence-transformers`), Groq API, Rank-BM25
* **Database:** ChromaDB (Local persistence)

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Node.js & npm
* A Groq API Key

### Backend Setup
1. Clone the repository and navigate to the project root.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
   VECTOR_DB_PATH=./chroma_db
   GROQ_MODEL_NAME=llama-3.1-8b-instant
   ```
4. Start the FastAPI server:
   ```bash
   python main.py
   ```
   *The backend will run on `http://localhost:8000`.*

### Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend will run on `http://localhost:5173`.*

## 📖 Usage
1. **Add Knowledge:** Place your technical manuals, SOPs, and hardware specifications inside the `data/` folder.
2. **Index Documents:** Click the **"Index Sample Docs"** button in the React UI (or send a POST request to `/index-sample-docs`). This will chunk and embed the documents into ChromaDB.
3. **Query:** Use the chat interface to ask technical questions. The AI will retrieve the most relevant chunks from your documents and generate a precise answer.

## 📝 License
This project is for educational and demonstrative purposes.
