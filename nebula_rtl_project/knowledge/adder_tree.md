# Adder Tree Optimization for RTL Timing

## Problem

Adding many values sequentially can create a long chain of additions. Each addition must wait for the result of the previous addition, increasing the combinational logic depth and potentially creating a critical timing path.

For example, calculating the sum of eight values using a serial chain requires several dependent additions.

## When to use it

Use an adder tree when summing multiple independent values, especially when the number of operands is large and the sum is on a critical timing path.

This technique is commonly useful in arithmetic-heavy hardware such as digital signal processing, dot-product engines, counters, and accumulation logic.

## Optimization strategy

Instead of adding values one after another, organize the additions as a balanced tree.

Independent pairs of values are added in parallel, and their results are combined in later levels. This reduces the logic depth from approximately linear in the number of operands to logarithmic.

## Example

### Before

A serial addition chain creates multiple dependent additions.

```verilog
assign sum = a + b + c + d + e + f + g + h;
```

Conceptually, this may create a long chain of additions:

```text
((((((a + b) + c) + d) + e) + f) + g) + h
```

### After

Use intermediate signals to explicitly describe a balanced adder tree.

```verilog
wire [31:0] sum_ab;
wire [31:0] sum_cd;
wire [31:0] sum_ef;
wire [31:0] sum_gh;

wire [31:0] sum_abcd;
wire [31:0] sum_efgh;

assign sum_ab = a + b;
assign sum_cd = c + d;
assign sum_ef = e + f;
assign sum_gh = g + h;

assign sum_abcd = sum_ab + sum_cd;
assign sum_efgh = sum_ef + sum_gh;

assign sum = sum_abcd + sum_efgh;
```

The first four additions can occur in parallel, followed by two additions, and finally one addition.

## Trade-offs

* Reduces the depth of the addition logic and can improve timing.
* May use more intermediate signals or require additional registers when pipelined.
* Can increase routing complexity.
* Modern synthesis tools may automatically rebalance simple addition expressions, but explicitly structuring the RTL can make the intended architecture clearer.

## Key idea

An adder tree improves timing by performing independent additions in parallel rather than creating a long sequence of dependent additions.

