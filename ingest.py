import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

def ingest_docs():
    """
    Loads documents from the data directory, splits them into chunks, 
    and stores them in a local Chroma vector database.
    """
    print("--- Starting Document Ingestion ---")
    
    # 1. Load documents
    data_dir = './data'
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} does not exist.")
        return

    # Load Markdown files
    md_loader = DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader)
    docs = md_loader.load()
    
    # Load Text files
    txt_loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader)
    docs.extend(txt_loader.load())
    
    # Load PDF files
    pdf_loader = DirectoryLoader(data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs.extend(pdf_loader.load())
    
    # Load Word files
    docx_loader = DirectoryLoader(data_dir, glob="**/*.docx", loader_cls=Docx2txtLoader)
    docs.extend(docx_loader.load())

    print(f"Loaded {len(docs)} documents (Markdown, TXT, PDF, DOCX).")

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    print(f"Split documents into {len(splits)} chunks.")

    # 3. Initialize embeddings (Local)
    model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    print(f"Initializing embeddings with model: {model_name}...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # 4. Create and persist Vector DB
    vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    print(f"Storing embeddings in ChromaDB at {vector_db_path}...")
    
    vector_db = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=vector_db_path
    )
    
    print("--- Ingestion Complete ---")

if __name__ == "__main__":
    ingest_docs()
