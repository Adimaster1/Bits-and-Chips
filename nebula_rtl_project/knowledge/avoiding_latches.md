# Avoiding Unintended Latches in Combinational RTL

## Problem

In a combinational `always @(*)` block, if an output is not assigned a value on every possible execution path — for example, a missing `else` or a `case` statement without a `default` — synthesis infers a latch to hold the previous value on the uncovered path. Unintended latches are transparent, hard to constrain in static timing analysis, can introduce glitches, and are almost never the intended design.

## When to use it

Review any combinational `always @(*)` block for complete signal coverage, especially during RTL linting or whenever a synthesis or lint report flags an inferred latch.

## Optimization strategy

Ensure every output assigned within a combinational block has a defined value on every possible path through the block — either by giving it a default assignment before any conditional logic, or by covering every case explicitly with `else` and `default` branches.

## Example

### Before

No `default` branch: for `sel == 2'd3`, `result` is left unspecified, so a latch is inferred.

```verilog
always @(*) begin
    case (sel)
        2'd0: result = input0;
        2'd1: result = input1;
        2'd2: result = input2;
        // no default - result undefined when sel == 2'd3
    endcase
end
```

### After

A default assignment before the `case` guarantees `result` is defined on every path, so the block synthesizes as purely combinational logic.

```verilog
always @(*) begin
    result = input0; // default assignment covers every path
    case (sel)
        2'd0: result = input0;
        2'd1: result = input1;
        2'd2: result = input2;
        2'd3: result = input3;
    endcase
end
```

## Trade-offs

* Adding a default assignment is a low-cost fix and is a robust pattern for larger `case` statements with many outputs.
* An explicit `default` branch can be used instead when every distinct case value should be reachable and documented individually.
* Lint tools can catch most latch inference automatically, but reviewing RTL by hand is still useful for larger blocks that assign several signals conditionally.

## Key idea

Every output of a combinational `always` block must be assigned on every execution path; otherwise synthesis infers a latch, which is almost always unintended and complicates timing closure.
