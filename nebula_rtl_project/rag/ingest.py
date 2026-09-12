from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def retrieve_unique_documents(vector_store, query, k=3, fetch_k=10):
    """
    Retrieve relevant chunks while avoiding duplicate source documents.
    """

    results = vector_store.similarity_search_with_score(
        query,
        k=fetch_k
    )

    unique_results = []
    seen_sources = set()

    for document, distance in results:

        source = document.metadata.get("source", "unknown")

        if len(unique_results) >= k:
            break

        if source not in seen_sources:
            unique_results.append((document, distance))
            seen_sources.add(source)

    return unique_results

def main():
# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

    KNOWLEDGE_DIR = Path("knowledge")
    CHROMA_DIR = "chroma_db"

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# 2. Load all Markdown files
# ---------------------------------------------------------

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        loaded_docs = loader.load()

        # Add useful metadata
        for doc in loaded_docs:
            doc.metadata["source"] = file_path.name
            doc.metadata["technique"] = file_path.stem

        documents.extend(loaded_docs)

    print(f"Loaded {len(documents)} documents.")


# ---------------------------------------------------------
# 3. Split documents into smaller chunks
# ---------------------------------------------------------

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Split into {len(chunks)} chunks.")


# ---------------------------------------------------------
# 4. Create the embedding model
# ---------------------------------------------------------

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# ---------------------------------------------------------
# 5. Create Chroma database and store the chunks
# ---------------------------------------------------------

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="verilog_optimization",
        persist_directory=CHROMA_DIR,
    )

    print("\nIngestion complete!")
    print(f"Chroma database saved to: {CHROMA_DIR}")

if __name__ == "__main__":
    main()
