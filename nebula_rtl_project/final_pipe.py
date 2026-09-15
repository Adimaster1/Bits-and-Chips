"""
Complete RTL optimization pipeline from start to end.

Pipeline:
1. Run Yosys + OpenSTA
2. Build a RAG query from timing information and RTL
3. Retrieve relevant optimization knowledge
4. Build an LLM prompt
5. Generate optimized Verilog
6. Validate generated Verilog with Yosys
7. Validate formal equivalence
8. If validation fails, feed the failure back to the LLM
9. Repeat until successful or MAX_ATTEMPTS is reached
10. Save the verified optimized RTL
"""

import os
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from sta.run_analysis import run_pipeline
from rag.query_builder import build_rag_query
from rag.ingest import retrieve_unique_documents
from llm.llm_parser import llm_feed
from verification.verilog_validator import validate_verilog
from verification.equivalence_validator import validate_equivalence


# =========================================================
# Configuration
# =========================================================

CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

VERILOG_FILE = Path("rtl/unoptimized.v")
OPTIMIZED_PATH = Path("rtl/optimized_heavy_calculator.v")
TEMP_PATH = Path("rtl/temp.v")

TOP_MODULE = "heavy_calculator"

# Maximum number of LLM generations, including the first attempt.
MAX_ATTEMPTS = 3


# =========================================================
# Helper: format TimingPath information
# =========================================================

def format_timing_path(timing_path):
    """
    Convert the TimingPath object into readable text for the LLM.

    Uses getattr() so this continues to work if the TimingPath
    dataclass contains slightly different fields.
    """

    startpoint = getattr(timing_path, "startpoint", "Unknown")
    endpoint = getattr(timing_path, "endpoint", "Unknown")
    slack = getattr(timing_path, "slack", "Unknown")
    path_delay = getattr(timing_path, "path_delay", "Unknown")
    cells = getattr(timing_path, "cells", [])

    timing_info = f"""
Startpoint: {startpoint}
Endpoint: {endpoint}
Slack: {slack} ns
Path delay: {path_delay} ns
"""

    if cells:
        timing_info += "\nCells on critical path:\n"

        for cell in cells:
            timing_info += f"- {cell}\n"

    return timing_info


# =========================================================
# Helper: format RAG results
# =========================================================

def format_rag_results(results):

    if not results:
        return "No relevant optimization knowledge was retrieved."

    rag_context = ""

    for i, (document, distance) in enumerate(results, start=1):

        source = document.metadata.get("source", "Unknown source")

        rag_context += f"""
--- Optimization Knowledge {i} ---
Source: {source}

{document.page_content}

"""

    return rag_context

# =========================================================
# Part 6: Create initial LLM prompt
# =========================================================

def build_llm_prompt(
    verilog_code,
    timing_path,
    rag_context
):
    """
    Build the initial prompt given to the LLM.

    The prompt contains:
    - Original RTL
    - Timing information
    - RAG optimization knowledge
    - Optimization requirements
    - Output formatting requirements
    """

    timing_info = format_timing_path(timing_path)

    prompt = f"""
You are an expert RTL optimization engineer.

Your task is to optimize the following Verilog RTL for TIMING while
preserving its exact functional behavior.

============================================================
ORIGINAL VERILOG RTL
============================================================

```verilog
{verilog_code}
````

============================================================
TIMING ANALYSIS
===============

The RTL was synthesized and analyzed using Yosys and OpenSTA.

{timing_info}

The primary objective is to eliminate the timing violation and
improve the critical path delay/slack.

============================================================
RELEVANT RTL OPTIMIZATION KNOWLEDGE
===================================

The following information was retrieved from a knowledge base
using the timing analysis and RTL characteristics:

{rag_context}

============================================================
OPTIMIZATION REQUIREMENTS
=========================

1. Preserve the exact functional behavior of the original RTL.

2. Optimize the RTL primarily for timing.

3. Pay particular attention to the reported critical path and
   the operations/cells contributing to it.

4. Use the retrieved optimization knowledge where appropriate.

5. Do NOT make arbitrary changes unrelated to the timing problem.

6. Do NOT change the module name.

7. Do NOT change the module's input/output interface.

8. Do NOT remove required inputs or outputs.

9. Avoid introducing unnecessary logic.

10. Do not introduce additional pipeline stages unless they are
    genuinely appropriate and functionally safe for this problem.

11. The resulting Verilog must be valid synthesizable Verilog.

12. The resulting design will be checked using Yosys and formal
    equivalence checking, so functional correctness is mandatory.

============================================================
OUTPUT FORMAT
=============

Return ONLY the complete optimized Verilog source code.

Do not include:

* explanations
* markdown fences
* comments outside the Verilog source
* analysis
* discussion of the optimization

The response must begin directly with the Verilog code.
"""

    return prompt


# =========================================================
# Feedback prompt
# =========================================================

def build_feedback_prompt(
original_prompt,
previous_code,
failure_type,
failure_output,
attempt_number
):
    """
Build a retry prompt after Yosys or formal equivalence
validation has failed.

```
The original optimization task is retained, while the
verification failure is added as feedback.
    """

    prompt = f"""

{original_prompt}

============================================================
VERIFICATION FEEDBACK
=====================

This is optimization attempt {attempt_number}.

The previously generated RTL FAILED verification.

Failure type:
{failure_type}

## Verification output:
## {failure_output}

Previous generated RTL:
{previous_code}

YOUR TASK:
Generate a corrected and improved version of the optimized RTL.

You MUST address the verification failure described above.

Important:

1. Preserve the original module name and interface.
2. Preserve exact functional behavior.
3. Continue optimizing for timing.
4. Do not repeat the same mistake that caused the previous
   verification failure.
5. The new RTL must be synthesizable by Yosys.
6. The new RTL must pass formal equivalence against the original RTL.
7. Return ONLY the complete Verilog source code.
8. Do not include markdown code fences.
9. Do not include explanations or analysis.

Generate the corrected Verilog now.
"""


    return prompt


# =========================================================
# Helper: clean temporary files/directories
# =========================================================

def cleanup():

    if TEMP_PATH.exists():
        TEMP_PATH.unlink()

    if os.path.exists("equivalence_check"):
        shutil.rmtree("equivalence_check")

# =========================================================
# Main pipeline
# =========================================================

def main():

    print("STARTING RTL OPTIMIZATION PIPELINE")

# ---------------------------------------------------------
# 1. Run Yosys + OpenSTA and get TimingPath
# ---------------------------------------------------------

    print("\n[1/8] Running Yosys + OpenSTA...")

    timing_path = run_pipeline()

    if timing_path is None:
        print("Pipeline failed. Cannot perform retrieval.")
        return

    print("Timing analysis completed.")

# ---------------------------------------------------------
# 2. Read original Verilog
# ---------------------------------------------------------

    if not VERILOG_FILE.exists():
        print(f"Error: RTL file not found: {VERILOG_FILE}")
        return

    verilog_code = VERILOG_FILE.read_text()

# ---------------------------------------------------------
# 3. Convert TimingPath into a RAG query
# ---------------------------------------------------------

    print("\n[2/8] Building RAG query...")

    query = build_rag_query(timing_path,verilog_code)

    print("RAG query generated.")

# ---------------------------------------------------------
# 4. Load embedding model
# ---------------------------------------------------------

    print("\n[3/8] Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# ---------------------------------------------------------
# 5. Connect to existing Chroma database
# ---------------------------------------------------------

    print("\n[4/8] Connecting to Chroma database...")

    vector_store = Chroma(
    collection_name="verilog_optimization",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

# ---------------------------------------------------------
# 6. Retrieve relevant optimization knowledge
# ---------------------------------------------------------

    print("\n[5/8] Retrieving optimization knowledge...")

    results = retrieve_unique_documents(
    vector_store,
    query,
    k=3,
    fetch_k=10)

    rag_context = format_rag_results(results)

    print(f"Retrieved {len(results)} relevant knowledge chunks.")

# ---------------------------------------------------------
# 7. Build initial LLM prompt
# ---------------------------------------------------------

    print("\n[6/8] Building LLM prompt...")

    prompt = build_llm_prompt(
    verilog_code,
    timing_path,
    rag_context
)

    print("LLM prompt generated.")

# ---------------------------------------------------------
# 8. LLM generation + verification feedback loop
# ---------------------------------------------------------

    print("\n[7/8] Starting LLM optimization and verification loop...")

    current_prompt = prompt
    opt_code = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print(f"OPTIMIZATION ATTEMPT {attempt}/{MAX_ATTEMPTS}")

        cleanup()

    # -----------------------------------------------------
    # Generate optimized Verilog
    # -----------------------------------------------------

        print("Generating optimized RTL using LLM...")

        try:
            opt_code = llm_feed(current_prompt)
        except Exception as e:
            print(f"LLM generation failed: {e}")

            if attempt == MAX_ATTEMPTS:
                print("Maximum attempts reached.")
                break

            continue

        if not opt_code or not opt_code.strip():
            print("LLM returned empty output.")

            if attempt == MAX_ATTEMPTS:
                print("Maximum attempts reached.")
                break

            current_prompt = build_feedback_prompt(
            prompt,
            "",
            "LLM returned empty output",
            "The LLM returned an empty response.",
            attempt
        )

            continue

    # -----------------------------------------------------
    # Write generated RTL to temporary file
    # -----------------------------------------------------

        TEMP_PATH.write_text(opt_code)

        print(f"Generated RTL written to {TEMP_PATH}")

    # -----------------------------------------------------
    # Yosys validation
    # -----------------------------------------------------

        print("\nRunning Yosys Verilog validation...")

        yosys_success, yosys_output = validate_verilog(
        verilog_file=str(TEMP_PATH),
        top_module=TOP_MODULE
    )

        if not yosys_success:

            print("\nYOSYS VALIDATION FAILED.")
            print(yosys_output)

        if attempt == MAX_ATTEMPTS:
            print("Maximum attempts reached.")
            cleanup()
            break

        # Feed Yosys failure back to LLM.
            current_prompt = build_feedback_prompt(
            original_prompt=prompt,
            previous_code=opt_code,
            failure_type="Yosys Verilog/Synthesis Validation Failure",
            failure_output=yosys_output,
            attempt_number=attempt + 1
        )

            print("\nSending Yosys failure feedback back to LLM...")
            continue

        print("Yosys validation PASSED.")

    # -----------------------------------------------------
    # Formal equivalence validation
    # -----------------------------------------------------

        print("\nRunning formal equivalence checking...")

    # Make sure any stale EQY directory is removed before
    # running the formal checker.
        if os.path.exists("equivalence_check"):
            shutil.rmtree("equivalence_check")

        eq_success, eqy_output = validate_equivalence(
        original_file=str(VERILOG_FILE),
        optimized_file=str(TEMP_PATH),
        top_module=TOP_MODULE
    )

        if not eq_success:

            print("\nFORMAL EQUIVALENCE FAILED.")
            print(eqy_output)

            if attempt == MAX_ATTEMPTS:
                print("Maximum attempts reached.")
                cleanup()
                break

        # Feed formal equivalence failure back to LLM.
            current_prompt = build_feedback_prompt(
                original_prompt=prompt,
                previous_code=opt_code,
                failure_type="Formal Equivalence Failure",
                failure_output=eqy_output,
                attempt_number=attempt + 1)

            print("\nSending formal equivalence failure feedback back to LLM...")
            continue

    # -----------------------------------------------------
    # Both checks passed
    # -----------------------------------------------------

        print("\nFORMAL EQUIVALENCE PASSED.")
        print("Generated RTL is functionally equivalent to the original.")

    # -----------------------------------------------------
    # Save verified optimized RTL
    # -----------------------------------------------------

        print("\n[8/8] Saving verified optimized RTL...")

        OPTIMIZED_PATH.write_text(opt_code)

        cleanup()

        print("\nRTL OPTIMIZATION SUCCESSFUL")
        print(f"Verified optimized RTL saved to: {OPTIMIZED_PATH}")
        print(f"Successful attempt: {attempt}")

        break

# ---------------------------------------------------------
# If loop somehow finishes without success
# ---------------------------------------------------------

    print("RTL OPTIMIZATION FAILED")
    print(f"No verified RTL was produced after {MAX_ATTEMPTS} attempts.")

    cleanup()

if __name__ == "__main__":
    main()