import re


def analyze_rtl_structure(verilog_code: str) -> dict:
    """
    Extract simple structural features from Verilog.

    This is a temporary heuristic-based implementation.
    Later, this can be replaced with an AST-based parser.
    """

    features = {
        "addition_count": 0,
        "multiplication_count": 0,
        "conditional_count": 0,
        "case_count": 0,
        "has_long_addition_chain": False,
    }

    # Count arithmetic operators
    features["addition_count"] = len(
        re.findall(r"\+", verilog_code)
    )

    features["multiplication_count"] = len(
        re.findall(r"\*", verilog_code)
    )

    # Count conditional statements
    features["conditional_count"] = len(
        re.findall(r"\bif\b", verilog_code)
    )

    # Count case statements
    features["case_count"] = len(
        re.findall(r"\bcase\b", verilog_code)
    )

    # Simple heuristic
    if features["addition_count"] >= 3:
        features["has_long_addition_chain"] = True

    return features