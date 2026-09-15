# Register Retiming for RTL Timing Optimization

## Problem

Combinational logic between two pipeline registers is sometimes unbalanced: one stage contains significantly more logic than an adjacent stage. Even though the total amount of combinational logic across the pipeline is reasonable, the critical path is determined by the single heaviest stage.

## When to use it

Use retiming when a timing report shows one pipeline stage is much slower than its neighbors, and the total pipeline latency (number of cycles) should stay the same. Retiming redistributes existing registers rather than adding new ones, which distinguishes it from pipelining.

## Optimization strategy

Move registers across combinational logic boundaries — without changing functional behavior or overall latency — so that combinational delay is balanced more evenly between stages. Logic can be moved backward (before a register) or forward (after a register) as long as the same computation still completes within the same number of clock cycles.

## Example

### Before

The first stage performs a multiply and an add; the second stage performs only a simple mask. The two stages are unbalanced.

```verilog
always @(posedge clk) begin
    stage1 <= (a * b) + c;    // heavy: multiply then add
    stage2 <= stage1 & mask;  // light: simple AND
end
```

### After

The addition is moved across the register boundary into the second stage, balancing the two stages while keeping the same two-cycle latency and the same result.

```verilog
reg [31:0] mult_reg;

always @(posedge clk) begin
    mult_reg <= a * b;                 // heavy stage now does only the multiply
    stage2   <= (mult_reg + c) & mask; // add + mask combined in the second stage
end
```

## Trade-offs

* Balances combinational delay across stages without changing total pipeline latency.
* Requires functional equivalence to be preserved; manual retiming should be checked with simulation or formal equivalence checking.
* Many synthesis tools offer automatic sequential retiming as a compile option, but explicit RTL retiming makes the intended stage boundaries clear and portable across tools.
* Only valid when moving logic does not change which cycle a result is expected to appear on for any observing logic outside the retimed region.

## Key idea

Retiming redistributes existing registers around combinational logic to balance stage delays, without adding new registers or changing total pipeline latency — unlike pipelining, which explicitly increases latency to reduce per-stage delay.
