import subprocess
import os


def create_eqy_config(
    original_file: str,
    optimized_file: str,
    top_module: str,
    config_file: str = "verification/equivalence_check.eqy"
):
    """
    Creates an EQY configuration file for checking strict
    cycle-by-cycle equivalence between two Verilog designs.
    """

    config = f"""
[gold]
read_verilog {original_file}
prep -top {top_module}

[gate]
read_verilog {optimized_file}
prep -top {top_module}

[strategy simple]
use sat
depth 10
"""

    with open(config_file, "w") as file:
        file.write(config.strip())

    return config_file


def validate_equivalence(
    original_file: str,
    optimized_file: str,
    top_module: str
):
    """
    Run formal equivalence checking using EQY.

    Returns:
        success (bool): True if designs are proven equivalent.
        output (str): Complete EQY output.
    """

    config_file = create_eqy_config(
        original_file=original_file,
        optimized_file=optimized_file,
        top_module=top_module
    )

    #print("\n" + "=" * 70)
    #print("RUNNING FORMAL EQUIVALENCE CHECK")
    #print("=" * 70)

    # print(f"Original RTL:  {original_file}")
    # print(f"Optimized RTL: {optimized_file}")
    # print(f"Top module:    {top_module}")

    try:

        result = subprocess.run(
            ["eqy", config_file],
            capture_output=True,
            text=True
        )

        output = result.stdout + "\n" + result.stderr

        # EQY returns 0 when the proof passes
        if result.returncode == 0:

            #print("\n" + "=" * 70)
            print("FORMAL EQUIVALENCE CHECK PASSED")
            #print("=" * 70)

            return True, output

        else:

            #print("\n" + "=" * 70)
            print("FORMAL EQUIVALENCE CHECK FAILED")
            #print("=" * 70)

            return False, output

    except FileNotFoundError:

        error_message = (
            "EQY executable was not found. "
            "Make sure EQY is installed and available in PATH."
        )

        print(error_message)

        return False, error_message