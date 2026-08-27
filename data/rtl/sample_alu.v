module sample_alu (
    input wire clk,
    input wire rst,
    input wire enable,
    input wire [7:0] a,
    input wire [7:0] b,
    output reg [7:0] result
);

    wire [7:0] sum;
    wire [7:0] diff;

    assign sum  = a + b;
    assign diff = a - b;

    always @(posedge clk) begin
        if (rst) begin
            result <= 8'd0;
        end
        else if (enable) begin
            if (a > b)
                result <= sum;
            else
                result <= diff;
        end
    end

endmodule
