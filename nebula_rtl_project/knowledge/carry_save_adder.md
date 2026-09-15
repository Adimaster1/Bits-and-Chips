# Carry-Save Adder (CSA) Trees for Multi-Operand Addition

## Problem

Summing many operands using successive carry-propagate additions — even when organized as a balanced adder tree — still requires each individual addition to fully propagate carries across the operand width, which contributes logic depth at every stage.

## When to use it

Use carry-save reduction when summing three or more operands, such as in multiplier partial-product reduction or wide multi-operand accumulation, and the number of full carry-propagate additions on the critical path needs to be minimized.

## Optimization strategy

Use carry-save adders (3:2 compressors) to reduce three operands to two — a partial sum vector and a shifted carry vector — without propagating carries between bit positions. Chain multiple CSA stages to reduce many operands down to just two, and perform a single full carry-propagate addition only at the very end.

## Example

### Before

Each `+` below is a full carry-propagate addition, even when organized as a tree.

```verilog
assign sum_ab = a + b;
assign sum_cd = c + d;
assign sum    = sum_ab + sum_cd + e; // each + fully propagates carries
```

### After

Carry-save (3:2 compressor) stages defer carry propagation until a single final addition.

```verilog
wire [31:0] csa1_sum, csa1_carry;
wire [31:0] csa2_sum, csa2_carry;

// 3:2 compressor: reduces a, b, c to a sum and carry vector, no carry propagation
assign csa1_sum   = a ^ b ^ c;
assign csa1_carry = ((a & b) | (b & c) | (a & c)) << 1;

// reduce the CSA output together with the remaining operands d and e
assign csa2_sum   = csa1_sum ^ csa1_carry ^ d;
assign csa2_carry = ((csa1_sum & csa1_carry) | (csa1_carry & d) | (csa1_sum & d)) << 1;

// single final carry-propagate addition
assign sum = csa2_sum + csa2_carry + e;
```

## Trade-offs

* Significantly reduces the number of full carry-propagate additions on the critical path for wide multi-operand sums.
* Costs more XOR/AND gates and wider intermediate sum/carry signals than a straightforward adder tree.
* A single carry-propagate addition is still required at the end and remains part of the critical path.
* Most beneficial for wide multi-operand reduction, such as four or more operands or multiplier partial products, rather than simple two- or three-operand sums.

## Key idea

Carry-save adders remove carry propagation from intermediate addition stages by keeping partial sums and carries separate, deferring a single full carry-propagate addition to the end of a multi-operand reduction.
