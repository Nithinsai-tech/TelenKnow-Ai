import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_classic.chains import (
    create_retrieval_chain,
    create_history_aware_retriever
)
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain
)
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

# Load environment variables
load_dotenv()


def get_rag_chain():
    """
    Initializes and returns the RAG chain.
    """

    # Validate API key
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set in .env file."
        )

    # ---------------------------------------------------
    # 1. Initialize Embeddings
    # ---------------------------------------------------

    model_name = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "all-MiniLM-L6-v2"
    )

    print(f"Loading embeddings model: {model_name}")

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )

    # ---------------------------------------------------
    # 2. Load Vector Database
    # ---------------------------------------------------

    vector_db_path = os.getenv(
        "VECTOR_DB_PATH",
        "./chroma_db"
    )

    if not os.path.exists(vector_db_path):
        raise FileNotFoundError(
            f"Vector DB not found at {vector_db_path}"
        )

    vector_db = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embeddings
    )

    # ---------------------------------------------------
    # 3. Chroma Retriever
    # ---------------------------------------------------

    chroma_retriever = vector_db.as_retriever(
        search_kwargs={"k": 2}
    )

    # ---------------------------------------------------
    # 4. BM25 Retriever
    # ---------------------------------------------------

    print("Building BM25 keyword index...")

    all_docs_data = vector_db.get()

    docs = []

    for doc, meta in zip(
        all_docs_data.get("documents", []),
        all_docs_data.get("metadatas", [])
    ):

        if doc is not None:
            docs.append(
                Document(
                    page_content=doc,
                    metadata=meta or {}
                )
            )

    if docs:

        bm25_retriever = BM25Retriever.from_documents(docs)

        bm25_retriever.k = 2

        # Hybrid Retrieval
        ensemble_retriever = EnsembleRetriever(
            retrievers=[
                bm25_retriever,
                chroma_retriever
            ],
            weights=[0.5, 0.5]
        )

    else:
        ensemble_retriever = chroma_retriever

    # ---------------------------------------------------
    # 5. Initialize LLM
    # ---------------------------------------------------

    print(
        f"Initializing Groq LLM with model: "
        f"{os.getenv('GROQ_MODEL_NAME', 'llama-3.1-8b-instant')}"
    )

    llm = ChatGroq(
        temperature=0,
        model_name=os.getenv(
            "GROQ_MODEL_NAME",
            "llama-3.1-8b-instant"
        ),
        groq_api_key=groq_api_key
    )

    # ---------------------------------------------------
    # 6. History Aware Retriever
    # ---------------------------------------------------

    contextualize_q_system_prompt = (
        "Given chat history and the latest user question, "
        "reformulate the question into a standalone question "
        "if needed. Do not answer the question."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm,
        ensemble_retriever,
        contextualize_q_prompt
    )

    # ---------------------------------------------------
    # 7. Main System Prompt
    # ---------------------------------------------------

    system_prompt = (
        "You are a document-grounded telecom retrieval system. "

        "Using ONLY the provided Context, produce a single "
        "JSON object and nothing else. "

        "Response schema: "
        "{{"
        "\"answer\": <string or object>, "
        "\"confidence\": <float 0-1 or null>, "
        "\"sources\": ["
        "{{"
        "\"source\": <string>, "
        "\"chunk\": <int|null>, "
        "\"page\": <int|null>, "
        "\"similarity\": <float|null>"
        "}}"
        "]"
        "}} "

        "Do NOT include explanations, narration, filler text, "
        "or commentary. "

        "Do NOT use phrases like "
        "'According to the context', "
        "'This section mentions', "
        "'As an AI assistant'. "

        "Keep answers concise, factual, and extraction-focused. "

        "For exact-value or specification questions, "
        "return only short factual values. "

        "If multiple facts are required, "
        "return answer as key-value JSON. "

        "If the answer does not exist in the provided context, "
        "return exactly: "
        "{{"
        "\"answer\": "
        "\"I cannot find the answer in the uploaded documents.\", "
        "\"confidence\": 0.0, "
        "\"sources\": []"
        "}} "

        "\n\nContext: {context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    # ---------------------------------------------------
    # 8. Create RAG Chain
    # ---------------------------------------------------

    combine_docs_chain = create_stuff_documents_chain(
        llm,
        qa_prompt
    )

    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        combine_docs_chain
    )

    return rag_chain


# ---------------------------------------------------
# Main Test
# ---------------------------------------------------

if __name__ == "__main__":

    try:

        print("Testing RAG Engine...")

        chain = get_rag_chain()

        query = "What is the nominal voltage?"

        response = chain.invoke({
            "input": query,
            "chat_history": []
        })

        print(f"\nQuery: {query}")
        print(f"\nAnswer:\n{response['answer']}")

    except Exception as e:
        print(f"Error during test: {e}")