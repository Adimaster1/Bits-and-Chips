# Clock Gating for RTL Power Optimization

## Problem

Registers implemented with a feedback multiplexer to "hold" their value are still clocked every cycle. Even when the enable condition is false, the clock tree continues to toggle every flop, consuming dynamic power for no functional benefit.

## When to use it

Use clock gating when a register or block of registers only needs to update on a subset of cycles (e.g., an enable-controlled datapath, or a functional unit that is idle for extended periods), and power reduction is a design priority.

## Optimization strategy

Instead of holding a register's value by feeding its own output back into its data input, gate the clock itself using a technology-specific integrated clock gating (ICG) cell, so the register's clock pin only toggles when an update is actually needed.

## Example

### Before

The register is always clocked; the enable only controls what value is loaded.

```verilog
always @(posedge clk) begin
    if (enable)
        data_reg <= data_in;
    else
        data_reg <= data_reg;  // still clocked every cycle, just reloads itself
end
```

### After

An integrated clock gating cell gates the clock so the register is only clocked when `enable` is asserted.

```verilog
wire gated_clk;

// Typically instantiated from a technology-specific ICG cell,
// not implemented as raw combinational gating (which can glitch).
CLOCK_GATE_CELL u_icg (
    .CLK    (clk),
    .ENABLE (enable),
    .GCLK   (gated_clk)
);

always @(posedge gated_clk) begin
    data_reg <= data_in;
end
```

## Trade-offs

* Reduces dynamic power by preventing unnecessary clocking of registers that aren't updating.
* Requires a glitch-free ICG cell; a raw combinational AND of clock and enable is generally unsafe and should be avoided.
* Adds a gated clock domain that must be handled correctly in static timing analysis and clock tree synthesis.
* Many synthesis tools can automatically infer clock gating from common enable-mux RTL patterns, but explicit ICG instantiation guarantees the intended structure is used.

## Key idea

Clock gating saves power by preventing the clock from toggling registers that don't need to update, rather than repeatedly reloading the same value into a register through a feedback multiplexer.
