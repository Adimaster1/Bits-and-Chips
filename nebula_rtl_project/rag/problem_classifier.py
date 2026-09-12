def identify_primary_problem(rtl_features, timing_features):
    """
    Identify the dominant RTL-level problem contributing to timing.

    This classification determines what type of optimization knowledge
    should be retrieved from the RAG database.
    """

    # ---------------------------------------
    # Priority 1:
    # Deep multi-operand addition
    # ---------------------------------------

    if rtl_features.get("has_long_addition_chain", False):

        return {
            "problem_type": "adder_chain",
            "confidence": "high",
            "description": (
                "The RTL contains a deep multi-operand addition chain "
                "that may create excessive arithmetic logic depth."
            )
        }

    # ---------------------------------------
    # Priority 2:
    # Heavy conditional / mux logic
    # ---------------------------------------

    conditional_count = rtl_features.get(
        "conditional_count",
        0
    )

    if conditional_count >= 3:

        return {
            "problem_type": "mux_chain",
            "confidence": "high",
            "description": (
                "The RTL contains multiple conditional statements that "
                "may infer cascaded multiplexers or priority logic."
            )
        }

    # ---------------------------------------
    # Priority 3:
    # Arithmetic-heavy logic
    # ---------------------------------------

    multiplication_count = rtl_features.get(
        "multiplication_count",
        0
    )

    addition_count = rtl_features.get(
        "addition_count",
        0
    )

    if multiplication_count >= 2:

        return {
            "problem_type": "arithmetic_heavy",
            "confidence": "medium",
            "description": (
                "The RTL contains multiple expensive arithmetic "
                "operations that may contribute to critical-path delay."
            )
        }

    # ---------------------------------------
    # Priority 4:
    # General deep combinational logic
    # ---------------------------------------

    if timing_features.get("has_deep_logic", False):

        return {
            "problem_type": "deep_combinational_logic",
            "confidence": "medium",
            "description": (
                "The critical path contains substantial combinational "
                "logic depth without a clearly dominant RTL pattern."
            )
        }

    # ---------------------------------------
    # Default
    # ---------------------------------------

    return {
        "problem_type": "general_timing",
        "confidence": "low",
        "description": (
            "A timing problem was detected, but no specific dominant "
            "RTL structural pattern was identified."
        )
    }