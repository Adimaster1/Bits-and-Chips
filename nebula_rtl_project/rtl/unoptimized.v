module heavy_calculator (
    input wire clk,
    input wire [31:0] a, b, c, d, e, f, g, h,
    output reg [31:0] sum_out
);
    always @(posedge clk) begin
        sum_out <= a + b + c + d + e + f + g + h; 
    end
endmodule