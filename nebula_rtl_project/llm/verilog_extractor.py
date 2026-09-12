import re
import os

def extract_verilog(llm_response):
    """
    Extract Verilog code from an LLM response.

    Supports responses in either:

    ```verilog
    ...
    ```

    or plain OPTIMIZED_VERILOG:
    ...
    """

    # First try to find a Verilog markdown block
    match = re.search(
        r"```verilog\s*(.*?)```",
        llm_response,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    # Try a generic code block
    match = re.search(
        r"```\s*(.*?)```",
        llm_response,
        re.DOTALL
    )

    if match:
        return match.group(1).strip()

    # Fall back to finding content after OPTIMIZED_VERILOG
    match = re.search(
        r"OPTIMIZED_VERILOG:\s*(.*)",
        llm_response,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


def save_verilog(verilog_code, output_path):
    """
    Save extracted Verilog to a file.
    """

    with open(output_path, "w") as file:
        file.write(verilog_code)

    print(f"Optimized Verilog saved to: {output_path}")