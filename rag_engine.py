import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

# Load environment variables
load_dotenv()

def get_rag_chain():
    """
    Initializes and returns the RAG (Retrieval-Augmented Generation) chain.
    """
    # 1. Initialize embeddings (must match the one used in ingest.py)
    model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    # 2. Load the existing Vector DB
    vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    if not os.path.exists(vector_db_path):
        raise FileNotFoundError(f"Vector DB not found at {vector_db_path}. Please run ingest.py first.")
        
    vector_db = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embeddings
    )
    
    # 3. Set up the Chroma Retriever
    chroma_retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    # 4. Set up the BM25 Keyword Retriever
    print("Building BM25 keyword index...")
    all_docs_data = vector_db.get()
    
    docs = []
    for doc, meta in zip(all_docs_data.get('documents', []), all_docs_data.get('metadatas', [])):
        if doc is not None:
            docs.append(Document(page_content=doc, metadata=meta or {}))
            
    if docs:
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 3
        
        # Combine into Ensemble Retriever (Hybrid Search)
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5]
        )
    else:
        # Fallback if DB is technically empty
        ensemble_retriever = chroma_retriever
    
    # 4. Initialize Groq LLM
    llm = ChatGroq(
        temperature=0,
        model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # 5. History-Aware Retriever
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm, ensemble_retriever, contextualize_q_prompt
    )

    # 6. Define the Prompt Template
    system_prompt = (
        "You are an expert technical support assistant for a telecom provider. "
        "Use the provided context to answer the user's question accurately. "
        "IMPORTANT: Your response MUST be beautifully structured using Markdown. "
        "Use appropriate headings (###), bullet points, and bold text to organize the information. "
        "Explain any telecom jargon simply so that a non-technical reader can easily understand it. "
        "If the answer is not in the context, state that you don't have enough information. "
        "\n\n"
        "Context: {context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # 7. Create the RAG Chain
    combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, combine_docs_chain)
    
    return rag_chain

if __name__ == "__main__":
    # Quick test if run directly
    try:
        print("Testing RAG Engine...")
        chain = get_rag_chain()
        query = "How do I configure OSPF on V-Series routers?"
        response = chain.invoke({"input": query})
        print(f"\nQuery: {query}")
        print(f"Answer:\n{response['answer']}")
    except Exception as e:
        print(f"Error during test: {e}")
