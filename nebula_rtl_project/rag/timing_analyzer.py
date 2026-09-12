from collections import Counter


def analyze_timing_path(timing_path):
    """
    Analyze a TimingPath object and return structured timing features.
    """

    # ---------------------------------------
    # Basic timing information
    # ---------------------------------------

    is_timing_violation = timing_path.slack < 0

    total_cells = len(timing_path.cells)

    # ---------------------------------------
    # Extract cell types
    # ---------------------------------------

    cell_types = []

    for cell in timing_path.cells:
        cell_types.append(cell.cell_type)

    cell_counts = Counter(cell_types)

    dominant_cell_types = [
        cell_type
        for cell_type, count in cell_counts.most_common(3)
    ]

    # ---------------------------------------
    # Logic family counts
    # ---------------------------------------

    xor_logic_count = sum(
        count
        for cell_type, count in cell_counts.items()
        if "XOR" in cell_type or "XNOR" in cell_type
    )

    aoi_oai_logic_count = sum(
        count
        for cell_type, count in cell_counts.items()
        if "AOI" in cell_type or "OAI" in cell_type
    )

    # ---------------------------------------
    # Find slowest cell
    # ---------------------------------------

    if timing_path.cells:

        slowest_cell = max(
            timing_path.cells,
            key=lambda cell: cell.delay
        )

        slowest_cell_type = slowest_cell.cell_type
        max_cell_delay = slowest_cell.delay

    else:

        slowest_cell_type = "Unknown"
        max_cell_delay = 0.0

    # ---------------------------------------
    # High-level classifications
    # ---------------------------------------

    has_deep_logic = total_cells >= 20

    has_significant_xor_logic = xor_logic_count >= 3

    has_significant_aoi_oai_logic = aoi_oai_logic_count >= 5

    return {
        # Basic timing
        "is_timing_violation": is_timing_violation,
        "slack": timing_path.slack,
        "path_delay": timing_path.path_delay,
        "total_cells": total_cells,

        # Cell analysis
        "dominant_cell_types": dominant_cell_types,
        "slowest_cell_type": slowest_cell_type,
        "max_cell_delay": max_cell_delay,

        # Logic categories
        "xor_logic_count": xor_logic_count,
        "aoi_oai_logic_count": aoi_oai_logic_count,

        # High-level interpretations
        "has_deep_logic": has_deep_logic,
        "has_significant_xor_logic": has_significant_xor_logic,
        "has_significant_aoi_oai_logic":
            has_significant_aoi_oai_logic,
    }


def get_retrieval_timing_context(timing_features):
    """
    Return only timing information useful for semantic retrieval.

    Detailed cell-level information is intentionally excluded because
    the current knowledge base contains RTL-level optimization techniques,
    not individual standard-cell optimization techniques.
    """

    context = []

    if timing_features["is_timing_violation"]:
        context.append(
            f"The design has a timing violation with "
            f"{timing_features['slack']:.3f} ns of negative slack."
        )
    else:
        context.append(
            f"The design currently meets timing with "
            f"{timing_features['slack']:.3f} ns of positive slack."
        )

    context.append(
        f"The critical path delay is "
        f"{timing_features['path_delay']:.3f} ns."
    )

    if timing_features["has_deep_logic"]:
        context.append(
            f"The critical path passes through "
            f"{timing_features['total_cells']} standard cells, "
            f"indicating substantial combinational logic depth."
        )

    return "\n".join(context)