from llm.verilog_extractor import (
    extract_verilog,
    save_verilog
)


llm_response = """
OPTIMIZED_VERILOG:
module heavy_calculator (
    input wire clk,
    input wire [31:0] a, b, c, d, e, f, g, h,
    output reg [31:0] sum_out
);

    reg [31:0] sum1, sum2, sum3, sum4, sum5, sum6;

    always @(posedge clk) begin
        sum1 = a + b;
        sum2 = c + d;
        sum3 = e + f;
        sum4 = g + h;
        sum5 = sum1 + sum2;
        sum6 = sum3 + sum4;
        sum_out <= sum5 + sum6;
    end

endmodule
"""


verilog_code = extract_verilog(llm_response)


if verilog_code is None:

    print("ERROR: Could not extract Verilog!")

else:

    print("EXTRACTED VERILOG")
    #print(verilog_code)

    #save_verilog(verilog_code, "rtl/optimized_heavy_calculator.v")