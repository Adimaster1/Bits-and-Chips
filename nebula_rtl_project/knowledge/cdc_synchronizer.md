# Clock Domain Crossing (CDC) Synchronization for RTL Design

## Problem

A signal generated in one clock domain and sampled directly by a register in a different, asynchronous clock domain can violate the receiving flop's setup/hold time. This can cause metastability, allowing an unpredictable value to propagate into downstream logic.

## When to use it

Use CDC synchronization whenever a signal crosses from one clock domain into a different, asynchronous or unrelated-phase clock domain — including status flags, single-bit control signals, and pulses. Multi-bit buses need additional techniques (gray-coded pointers, handshaking, or an asynchronous FIFO) rather than a plain synchronizer, since individual bits are not guaranteed to settle together.

## Optimization strategy

Insert two or more sequential flops in the receiving clock domain so a metastable value has time to resolve before it is used by downstream logic.

## Example

### Before

A signal crosses clock domains with no synchronization — unsafe.

```verilog
// domain A
always @(posedge clkA) begin
    flag_a <= condition;
end

// domain B - unsafe direct use of a signal from domain A
always @(posedge clkB) begin
    flag_b <= flag_a;  // possible metastability
end
```

### After

A two-flop synchronizer in the receiving domain gives a metastable value time to resolve.

```verilog
// domain A
always @(posedge clkA) begin
    flag_a <= condition;
end

// domain B - two-flop synchronizer
reg flag_sync1, flag_sync2;
always @(posedge clkB) begin
    flag_sync1 <= flag_a;
    flag_sync2 <= flag_sync1;
end
// flag_sync2 is the synchronized signal, safe to use in domain B
```

## Trade-offs

* Adds latency (typically two or more clock cycles in the receiving domain) before the signal can be used.
* Only safe for single-bit or gray-coded signals; multi-bit buses or pulses that must not be dropped require handshake or FIFO-based CDC structures.
* Synchronizer flops typically need explicit false-path or CDC-specific timing constraints, since normal setup/hold analysis does not apply across asynchronous clock domains.

## Key idea

A two-flop synchronizer gives a metastable signal time to resolve before it is used downstream, but only handles single-bit or gray-coded crossings — wider buses or pulses that must not be missed require handshake or FIFO-based CDC techniques.
