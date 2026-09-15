"""
Complete pipeline from start to end.
"""

import os
import shutil                                                       #used for deleting folders
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

from sta.run_analysis import run_pipeline
from rag.query_builder import build_rag_query
from rag.ingest import retrieve_unique_documents
from llm.llm_parser import (llm_feed, llm_feed_for_testing)
from verification.verilog_validator import validate_verilog
from verification.equivalence_validator import validate_equivalence


def main():

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
    #print(query)


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

# 6. Create LLM prompt

# 7. Feed prompt to LLM and write generated code to temporary file

    OPTIMIZED_PATH = Path("rtl/optimized_heavy_calculator.v")
    TEMP_PATH=Path("rtl/temp.v")
    opt_code = llm_feed_for_testing()                        #remove for_testing in actual

    with open(str(TEMP_PATH), "w") as file:
        file.write(opt_code)

# 8. Verify generated code

    success, yosys_output = validate_verilog(
    verilog_file=str(TEMP_PATH), top_module="heavy_calculator")

    if not success:
        exit()

    if (os.path.exists("equivalence_check")):
        shutil.rmtree("equivalence_check")

    success, eqy_output = validate_equivalence(
    original_file=str(VERILOG_FILE),
    optimized_file=str(TEMP_PATH),
    top_module="heavy_calculator")

    if not success:
        exit()

    os.remove(str(TEMP_PATH))
    with open(str(OPTIMIZED_PATH), "w") as file:
        file.write(opt_code)
    

if __name__=="__main__":
    main()