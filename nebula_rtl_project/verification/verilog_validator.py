import subprocess


def validate_verilog(
    verilog_file: str,
    top_module: str
):
    """
    Validate a Verilog design using Yosys.

    The function checks whether Yosys can:

    1. Read the Verilog file.
    2. Elaborate the specified top module.
    3. Run basic synthesis preparation.

    Returns:
        (success, output)

        success: True if Yosys completed successfully.
        output: Yosys stdout/stderr messages.
    """

    yosys_command = [
        "yosys",
        "-p",
        f"""
        read_verilog {verilog_file};
        hierarchy -check -top {top_module};
        proc;
        opt;
        check;
        """
    ]

    try:
        result = subprocess.run(
            yosys_command,
            capture_output=True,
            text=True
        )

        output = result.stdout + "\n" + result.stderr

        if result.returncode == 0:

            #print("\n" + "=" * 70)
            print("YOSYS VALIDATION PASSED")
            #print("=" * 70)

            return True, output

        else:

            #print("\n" + "=" * 70)
            print("YOSYS VALIDATION FAILED")
            #print("=" * 70)

            return False, output

    except FileNotFoundError:

        error_message = (
            "Yosys executable was not found. "
            "Make sure Yosys is installed and available in PATH."
        )

        print(error_message)

        return False, error_message