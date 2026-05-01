# Telecom Support RAG System

An advanced Retrieval-Augmented Generation (RAG) system built to assist telecom support agents with semantic searches of technical documentation, outage procedures, and hardware specifications.

## 🌟 Features
* **Multi-Format Ingestion:** Automatically parses and chunks `.md`, `.txt`, `.pdf`, and `.docx` files.
* **Local Vector Database:** Uses **ChromaDB** for fast, localized, and cost-free vector storage and similarity search.
* **Open-Source Embeddings:** Utilizes HuggingFace's `all-MiniLM-L6-v2` for high-quality, local text embeddings.
* **High-Speed Inference:** Powered by **Groq's LLaMA 3.1 8B** model for lightning-fast, context-aware answers.
* **FastAPI Backend:** Provides robust REST API endpoints (`/query`, `/index-sample-docs`, `/health`) with integrated CORS.
* **React Frontend:** A modern, dynamic UI built with Vite, TailwindCSS, and Lucide React to interface seamlessly with the backend.

## 🏗️ Architecture Stack
* **Frontend:** React, Vite, TailwindCSS, Axios
* **Backend:** Python, FastAPI, Uvicorn
* **AI/ML Layer:** LangChain, HuggingFace (`sentence-transformers`), Groq API
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
