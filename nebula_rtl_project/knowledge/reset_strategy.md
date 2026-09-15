# Reset Strategy (Synchronous vs. Asynchronous) for RTL Design

## Problem

The choice of reset style affects timing closure, reset recovery/removal timing, and portability across ASIC and FPGA targets. Careless use of asynchronous resets — particularly on deassertion — can cause metastability or reset-related timing violations.

## When to use it

Choose a reset strategy early, project-wide, during RTL coding. Revisit the decision if timing reports flag reset recovery/removal violations, or if the target flop library does not directly support the chosen style.

## Optimization strategy

* **Synchronous reset** — sampled on the clock edge like any other signal; simpler for static timing analysis, but only takes effect while the clock is toggling, and a large fanout reset condition can add to datapath logic.
* **Asynchronous reset** — takes effect immediately regardless of clock activity, useful for fast initialization, but requires a reset synchronizer on deassertion to avoid recovery/removal violations and metastability.

Best practice when using asynchronous reset: assert asynchronously, but synchronize the deassertion edge to the clock.

## Example

### Before

Asynchronous reset with no deassertion synchronizer — deassertion can occur close to a clock edge and risk a recovery timing violation.

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        data_reg <= 32'd0;
    else
        data_reg <= data_in;
end
```

### After

A reset synchronizer asserts asynchronously but releases reset synchronously to the clock.

```verilog
// Reset synchronizer: asynchronous assert, synchronous deassert
reg rst_sync_ff1, rst_sync_ff2;
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        rst_sync_ff1 <= 1'b0;
        rst_sync_ff2 <= 1'b0;
    end else begin
        rst_sync_ff1 <= 1'b1;
        rst_sync_ff2 <= rst_sync_ff1;
    end
end
wire rst_n_sync = rst_sync_ff2;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        data_reg <= 32'd0;
    else if (!rst_n_sync)
        data_reg <= 32'd0;
    else
        data_reg <= data_in;
end
```

## Trade-offs

* Synchronous reset is simpler to analyze in STA but depends on clock activity and can add to datapath logic.
* Asynchronous reset initializes immediately but needs a deassertion synchronizer and dedicated timing exceptions.
* Using one reset style consistently across a design simplifies verification and reset-domain crossing analysis.

## Key idea

Reset style is a project-wide timing and verification decision: asynchronous resets react immediately but need a deassertion synchronizer, while synchronous resets are easier to analyze but only take effect with clock activity.
