"""
Uses a manual prompt just to test the model connection. Verilog code is given as
raw text, not pulled from the actual file.
"""

from langchain_ollama import ChatOllama


# Connect to the locally running Ollama model
llm = ChatOllama(
    model="qwen3:8b",
    temperature=0
)

verilog_code = """
module heavy_calculator (
    input wire clk,
    input wire [31:0] a, b, c, d, e, f, g, h,
    output reg [31:0] sum_out
);

    always @(posedge clk) begin
        sum_out <= a + b + c + d + e + f + g + h;
    end

endmodule
"""


# ==========================================
# PROMPT
# ==========================================

prompt = f"""
You are an expert RTL and Verilog optimization engineer.

Analyze the following Verilog module and optimize it to reduce
combinational logic depth while preserving its functional behavior.

IMPORTANT CONSTRAINTS:

1. Preserve the module interface exactly.
2. Preserve cycle-by-cycle functional behavior.
3. Do NOT add pipeline stages or registers.
4. The output must remain synthesizable by Yosys.
5. Focus on reducing the depth of the multi-operand addition.
6. Any newly introduced intermediate signals used solely for arithmetic 
restructuring must be combinational signals declared as wires and assigned outside clocked 
always blocks. Do not introduce state-holding intermediate registers.

SEQUENTIAL LOGIC CONSTRAINTS:

Do not add, remove, or modify pipeline stages.

Do not introduce new registers, flip-flops, or clocked state.

The optimized RTL must preserve cycle-by-cycle functional behavior.

All structural arithmetic intermediate results should be implemented
using combinational logic where appropriate.

Do not place intermediate combinational calculations inside a
posedge-triggered always block unless they are explicitly present as
sequential state in the original design.

ORIGINAL VERILOG:

{verilog_code}

Analyze the arithmetic structure and determine whether the additions
can be reorganized into a more balanced structure.

Return your answer in EXACTLY this format:

EXPLANATION:
<brief explanation>

OPTIMIZED_VERILOG:
<complete Verilog module>

Do not include any additional text after the Verilog block.
"""

# Send a simple test prompt
response = llm.invoke(prompt)


print("\n" + "=" * 60)
print("OLLAMA RESPONSE")
print("=" * 60)

print(response.content)