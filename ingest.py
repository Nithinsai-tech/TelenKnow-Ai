import os
import traceback
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
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
    data_dir = "./data"
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' does not exist.")
        return

    docs = []

    # Load Markdown files
    try:
        md_loader = DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader)
        md_docs = md_loader.load()
        docs.extend(md_docs)
        print(f"  Loaded {len(md_docs)} Markdown file(s).")
    except Exception as e:
        print(f"ERROR loading Markdown files: {e}")
        traceback.print_exc()
        raise

    # Load Text files
    try:
        txt_loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader)
        txt_docs = txt_loader.load()
        docs.extend(txt_docs)
        print(f"  Loaded {len(txt_docs)} TXT file(s).")
    except Exception as e:
        print(f"ERROR loading TXT files: {e}")
        traceback.print_exc()
        raise

    # Load PDF files
    try:
        pdf_loader = DirectoryLoader(data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
        pdf_docs = pdf_loader.load()
        docs.extend(pdf_docs)
        print(f"  Loaded {len(pdf_docs)} PDF file(s).")
    except Exception as e:
        print(f"ERROR loading PDF files: {e}")
        traceback.print_exc()
        raise

    # Load Word (.docx) files
    try:
        docx_loader = DirectoryLoader(
            data_dir, glob="**/*.docx", loader_cls=Docx2txtLoader
        )
        docx_docs = docx_loader.load()
        docs.extend(docx_docs)
        print(f"  Loaded {len(docx_docs)} DOCX file(s).")
    except Exception as e:
        print(f"ERROR loading DOCX files: {e}")
        traceback.print_exc()
        raise

    print(f"Total documents loaded: {len(docs)}")

    if not docs:
        print("No documents found. Ingestion aborted.")
        return

    # 2. Split documents into chunks
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        splits = text_splitter.split_documents(docs)
        print(f"Split into {len(splits)} chunk(s).")
    except Exception as e:
        print(f"ERROR splitting documents: {e}")
        traceback.print_exc()
        raise

    # 3. Initialize embeddings
    try:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        print(f"Loading embedding model: {model_name} ...")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        print("Embedding model loaded.")
    except Exception as e:
        print(f"ERROR loading embedding model: {e}")
        traceback.print_exc()
        raise

    # 4. Create and persist Vector DB
    try:
        vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")
        print(f"Storing embeddings in ChromaDB at '{vector_db_path}' ...")
        Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=vector_db_path,
        )
        print("ChromaDB updated successfully.")
    except Exception as e:
        print(f"ERROR creating/updating ChromaDB: {e}")
        traceback.print_exc()
        raise

    print("--- Ingestion Complete ---")


if __name__ == "__main__":
    ingest_docs()