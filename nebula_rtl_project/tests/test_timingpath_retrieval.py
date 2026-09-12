from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

from sta.run_analysis import run_pipeline
from rag.query_builder import (build_rag_query, build_rag_query_with_debug)

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


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# 1. Run Yosys + OpenSTA and get TimingPath
# ---------------------------------------------------------

timing_path = run_pipeline()

if timing_path is None:
    print("Pipeline failed. Cannot perform retrieval.")
    exit()


# ---------------------------------------------------------
# 2. Convert TimingPath into a RAG query
# ---------------------------------------------------------

VERILOG_FILE = Path("rtl/unoptimized.v")
verilog_code=VERILOG_FILE.read_text()
query = build_rag_query(timing_path, verilog_code)               #Change to debug for summary

#print("\n" + "=" * 70)
print("GENERATED RAG QUERY")
# print("=" * 70)
# print(query)


# ---------------------------------------------------------
# 3. Load embedding model
# ---------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# ---------------------------------------------------------
# 4. Connect to existing Chroma database
# ---------------------------------------------------------

vector_store = Chroma(
    collection_name="verilog_optimization",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)


# ---------------------------------------------------------
# 5. Retrieve relevant optimization knowledge
# ---------------------------------------------------------

results = retrieve_unique_documents(
    vector_store,
    query,
    k=3,
    fetch_k=10
)


# ---------------------------------------------------------
# 6. Display results
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("RETRIEVED OPTIMIZATION KNOWLEDGE")
print("=" * 70)

for i, (document, score) in enumerate(results, start=1):
    print(f"\nRESULT {i}")
    print(f"Source: {document.metadata.get('source')}")
    print(f"Technique: {document.metadata.get('technique')}")
    print(f"Similarity score: {score:.4f}")
    print("-" * 70)
    print(document.page_content)