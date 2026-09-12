from verification.verilog_validator import validate_verilog


verilog_file = "rtl/optimized_heavy_calculator.v"

top_module = "heavy_calculator"


success, yosys_output = validate_verilog(
    verilog_file=verilog_file,
    top_module=top_module
)


# print("\n" + "=" * 70)
# print("VALIDATION RESULT")
# print("=" * 70)

if success:
    print("SUCCESS: The generated Verilog passed Yosys validation.")
else:
    print("FAILURE: The generated Verilog could not be validated.")


# print("\n" + "=" * 70)
# print("YOSYS OUTPUT")
# print("=" * 70)

# print(yosys_output)