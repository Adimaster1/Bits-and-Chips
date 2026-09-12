# Pipelining for RTL Timing Optimization

## Core idea

Pipelining improves timing by deliberately inserting sequential
registers between parts of a computation.

Unlike combinational restructuring, pipelining does not primarily
reduce the logical complexity of an operation. Instead, it divides a
computation across multiple clock cycles so that each pipeline stage
contains less combinational delay.

## When pipelining is appropriate

Use pipelining when:

- A combinational computation cannot meet the required clock period
  even after reasonable RTL restructuring.
- Additional clock-cycle latency is acceptable.
- Intermediate results can be stored in registers.
- Increasing clock frequency or throughput is more important than
  producing the final result within the original number of cycles.

Pipelining is particularly appropriate for datapaths containing
multiple stages of computation between sequential registers.

## When NOT to use pipelining

Pipelining may not be appropriate when:

- The output must be produced with the same cycle latency.
- Adding registers changes the required interface behavior.
- A simpler combinational restructuring can solve the timing problem.
- The timing problem is caused by an inefficient structure that can
  be directly optimized without adding sequential stages.

## Optimization strategy

Divide the original combinational computation into multiple stages.

Insert intermediate registers between these stages so that each stage
only needs to complete within one clock period.

For example:

Input
  ↓
Combinational Stage 1
  ↓
Pipeline Register
  ↓
Combinational Stage 2
  ↓
Output Register

The total computation may take multiple clock cycles, but the
combinational delay of each individual stage is reduced.

## Example

### Before

always @(posedge clk) begin
    result <= (a + b + c + d) * e;
end

The additions and multiplication must contribute to the timing of the
same sequential path.

### After

reg [31:0] partial_sum;

always @(posedge clk) begin
    partial_sum <= a + b + c + d;
    result <= partial_sum * e;
end

The computation is now divided across sequential stages.

## Trade-offs
Reduces combinational delay per clock cycle.
Can support a higher clock frequency.
Introduces additional registers.
Increases area and clock power.
Usually increases the number of clock cycles required for a result
to propagate from input to output.

## Key distinction
Pipelining improves timing by changing the sequential architecture of
the design and distributing computation across multiple clock cycles.

It should not be confused with combinational restructuring techniques,
such as adder-tree balancing, which attempt to reduce logic depth
without necessarily changing clock-cycle latency.