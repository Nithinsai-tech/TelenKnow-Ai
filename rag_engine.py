import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

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
    
    # 3. Set up the Retriever
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    # 4. Initialize Groq LLM
    llm = ChatGroq(
        temperature=0,
        model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # 5. Define the Prompt Template
    system_prompt = (
        "You are an expert technical support assistant for a telecom provider. "
        "Use the provided context to answer the user's question accurately. "
        "If the answer is not in the context, state that you don't have enough information. "
        "Use bullet points for steps and keep a professional tone."
        "\n\n"
        "Context: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # 6. Create the RAG Chain
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
    
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
