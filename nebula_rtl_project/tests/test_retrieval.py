from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# 2. Load the same embedding model
# ---------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# ---------------------------------------------------------
# 3. Connect to the existing Chroma database
# ---------------------------------------------------------

vector_store = Chroma(
    collection_name="verilog_optimization",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)


# ---------------------------------------------------------
# 4. Create a test query
# ---------------------------------------------------------

query = """
The RTL design has a negative-slack critical timing path caused by
a deep combinational arithmetic expression.

The expression contains multiple chained addition operations in a
single clock cycle. There are seven addition operations combining
eight input operands.

Find RTL optimization techniques that reduce the combinational logic
depth of a chain of additions while preserving functional equivalence.
"""


# ---------------------------------------------------------
# 5. Retrieve the most relevant chunks
# ---------------------------------------------------------

results = vector_store.similarity_search_with_score(
    query,
    k=3
)


# ---------------------------------------------------------
# 6. Print the results
# ---------------------------------------------------------

print("\nQUERY:")
print(query.strip())
print("\n" + "=" * 70)
print("RETRIEVED RESULTS")
print("=" * 70)

for i, (document, score) in enumerate(results, start=1):
    print(f"\nResult {i}")
    print(f"Source: {document.metadata.get('source')}")
    print(f"Technique: {document.metadata.get('technique')}")
    print(f"Score: {score:.4f}")
    print("-" * 70)
    print(document.page_content)
    print("-" * 70)
