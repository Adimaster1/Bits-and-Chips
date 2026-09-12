from rag.rtl_analyzer import analyze_rtl_structure
from rag.timing_analyzer import (
    analyze_timing_path,
    get_retrieval_timing_context
)
from rag.problem_classifier import identify_primary_problem


def build_rag_query(timing_path, verilog_code):
    """
    Build a focused semantic query for RAG retrieval.

    The query prioritizes the likely RTL-level root cause of the
    timing problem rather than including every extracted feature.
    """

    # =======================================
    # Step 1: Analyze RTL
    # =======================================

    rtl_features = analyze_rtl_structure(
        verilog_code
    )

    # =======================================
    # Step 2: Analyze timing
    # =======================================

    timing_features = analyze_timing_path(
        timing_path
    )

    # =======================================
    # Step 3: Identify primary problem
    # =======================================

    problem = identify_primary_problem(
        rtl_features,
        timing_features
    )

    problem_type = problem["problem_type"]

    # =======================================
    # Step 4: Generate focused query
    # =======================================

    query_parts = []

    # ---------------------------------------
    # ADDER CHAIN
    # ---------------------------------------

    if problem_type == "adder_chain":

        addition_count = rtl_features.get(
            "addition_count",
            0
        )

        query_parts.append(
            f"""
PRIMARY RTL OPTIMIZATION PROBLEM:

The design contains a deep multi-operand addition structure with
approximately {addition_count} addition operations.

Multiple independent values are being combined in a timing-critical
combinational path. The current arithmetic structure may create
sequentially dependent additions and excessive logic depth.

Find RTL optimization techniques specifically for reducing the depth
of multi-operand addition and improving arithmetic critical paths.

Relevant concepts include balanced arithmetic structures, parallel
addition, and adder-tree implementations.
"""
        )

    # ---------------------------------------
    # MUX CHAIN
    # ---------------------------------------

    elif problem_type == "mux_chain":

        conditional_count = rtl_features.get(
            "conditional_count",
            0
        )

        query_parts.append(
            f"""
PRIMARY RTL OPTIMIZATION PROBLEM:

The RTL contains approximately {conditional_count} conditional
statements that may create cascaded multiplexers or deep priority
logic.

Find RTL optimization techniques for reducing multiplexer depth and
restructuring nested conditional logic while preserving the intended
functional behavior and priority relationships.
"""
        )

    # ---------------------------------------
    # ARITHMETIC HEAVY
    # ---------------------------------------

    elif problem_type == "arithmetic_heavy":

        query_parts.append(
            """
PRIMARY RTL OPTIMIZATION PROBLEM:

The RTL contains multiple expensive arithmetic operations on a
timing-critical path.

Find RTL-level optimization techniques for reducing arithmetic
critical-path delay through restructuring, parallel computation,
or decomposition of expensive operations.
"""
        )

    # ---------------------------------------
    # DEEP COMBINATIONAL LOGIC
    # ---------------------------------------

    elif problem_type == "deep_combinational_logic":

        query_parts.append(
            """
PRIMARY RTL OPTIMIZATION PROBLEM:

The design contains a deep combinational critical path without a
single clearly identifiable RTL structure causing the delay.

Find RTL optimization techniques for reducing combinational logic
depth, simplifying logic, restructuring operations, or splitting
long critical paths.
"""
        )

    # ---------------------------------------
    # GENERAL TIMING
    # ---------------------------------------

    else:

        query_parts.append(
            """
PRIMARY RTL OPTIMIZATION PROBLEM:

The design has a timing violation, but the dominant RTL-level cause
has not yet been clearly identified.

Find general RTL-level techniques for improving critical-path timing
while preserving functional behavior.
"""
        )

    # =======================================
    # Step 5: Add timing evidence
    # =======================================

    timing_context = get_retrieval_timing_context(
        timing_features
    )

    query_parts.append(
        f"""
SUPPORTING TIMING EVIDENCE:

{timing_context}
"""
    )

    # =======================================
    # Step 6: Add optimization constraints
    # =======================================

    if problem_type in [
        "adder_chain",
        "mux_chain",
        "arithmetic_heavy"
    ]:

        query_parts.append(
            """
OPTIMIZATION CONSTRAINTS:

Preserve the functional behavior of the original RTL.

Prioritize structural RTL optimizations that reduce combinational
logic depth without adding additional clock-cycle latency.
"""
        )

    else:

        query_parts.append(
            """
OPTIMIZATION CONSTRAINTS:

Preserve the functional behavior of the original RTL.

Consider structural RTL optimization first. If necessary, consider
techniques such as pipelining when additional latency is acceptable.
"""
        )

    # =======================================
    # Return final query
    # =======================================

    return "\n".join(query_parts)

def build_rag_query_with_debug(timing_path, verilog_code):

    rtl_features = analyze_rtl_structure(verilog_code)

    timing_features = analyze_timing_path(
        timing_path
    )

    problem = identify_primary_problem(
        rtl_features,
        timing_features
    )

    print("\n" + "=" * 70)
    print("RTL FEATURES")
    print("=" * 70)

    for key, value in rtl_features.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("TIMING FEATURES")
    print("=" * 70)

    for key, value in timing_features.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("PRIMARY PROBLEM IDENTIFIED")
    print("=" * 70)

    print(f"Type: {problem['problem_type']}")
    print(f"Confidence: {problem['confidence']}")
    print(f"Description: {problem['description']}")

    # Generate the normal query
    return build_rag_query(
        timing_path,
        verilog_code
    )