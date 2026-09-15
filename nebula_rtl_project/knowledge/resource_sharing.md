# Resource Sharing (Time-Multiplexed Functional Units) for RTL Area Optimization

## Problem

Instantiating a separate functional unit — such as an adder, multiplier, or comparator — for each use in RTL wastes area when those uses are mutually exclusive in time, since most of the duplicated hardware sits idle.

## When to use it

Use resource sharing when multiple operations of the same type occur in mutually exclusive branches (for example, different arms of an `if`/`case`, or operations spread across different states of an FSM), and the resulting area or power savings outweigh the added multiplexer and control overhead.

## Optimization strategy

Replace duplicated functional units with a single shared unit, and use a multiplexer, controlled by the relevant condition or FSM state, to route the correct operands to it in each cycle.

## Example

### Before

Two logically separate additions are described for two mutually exclusive modes.

```verilog
always @(*) begin
    if (mode == 1'b0)
        result = a + b;
    else
        result = c + d;
end
```

### After

The operands are multiplexed ahead of a single shared adder, making the sharing explicit.

```verilog
wire [31:0] operand_x, operand_y;

assign operand_x = (mode == 1'b0) ? a : c;
assign operand_y = (mode == 1'b0) ? b : d;

assign result = operand_x + operand_y; // single shared adder
```

## Trade-offs

* Reduces area by eliminating duplicate functional units, at the cost of added multiplexer and control logic.
* Can lengthen the combinational path (mux delay plus operation delay) compared to a dedicated unit for each use.
* Only valid when the operations sharing a unit are genuinely mutually exclusive in time.
* Can become a throughput bottleneck if the shared resource is needed by more states or branches than it can service in the available cycles.
* Simple, small operations like this example are often merged automatically by synthesis; explicit sharing matters most for larger operators such as multipliers.

## Key idea

Resource sharing trades a small amount of added multiplexing and control logic for reduced area, by reusing one functional unit across operations that are guaranteed never to execute at the same time.
