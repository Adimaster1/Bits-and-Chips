from langchain_ollama import ChatOllama
from llm.verilog_extractor import extract_verilog

def llm_feed (prompt: str):

    llm = ChatOllama(
    model="qwen3:8b",
    temperature=0)

    response=llm.invoke(prompt)

    extracted_code = extract_verilog(response)

    return extracted_code

def llm_feed_for_testing ():

    response = """
OPTIMIZED_VERILOG:
module heavy_calculator (
    input wire clk,
    input wire [31:0] a, b, c, d, e, f, g, h,
    output reg [31:0] sum_out
);

    wire [32:0] sum1;
    wire [32:0] sum2;
    wire [32:0] sum3;
    wire [32:0] sum4;

    wire [33:0] sum5;
    wire [33:0] sum6;

    wire [34:0] final_sum;

    assign sum1 = {1'b0, a} + {1'b0, b};
    assign sum2 = {1'b0, c} + {1'b0, d};
    assign sum3 = {1'b0, e} + {1'b0, f};
    assign sum4 = {1'b0, g} + {1'b0, h};

    assign sum5 = sum1 + sum2;
    assign sum6 = sum3 + sum4;

    assign final_sum = sum5 + sum6;

    always @(posedge clk) begin
        sum_out <= final_sum[31:0];
    end

endmodule
"""

    extracted_code = extract_verilog(response)

    return extracted_code

if __name__=="__main__":
    llm_feed_for_testing()