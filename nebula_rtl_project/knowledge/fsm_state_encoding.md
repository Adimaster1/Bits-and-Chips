# FSM State Encoding for RTL Timing and Area Optimization

## Problem

The choice of state encoding affects both the size of next-state/output decoding logic and the timing of state-transition paths. A poorly chosen encoding can create wide decoders or long combinational paths on state-dependent outputs, or unnecessarily inflate the state register width.

## When to use it

Consider explicit state encoding when designing or optimizing a finite state machine, particularly when timing reports show congestion in next-state logic, or when state-register area or power is a concern on a resource-constrained target.

## Optimization strategy

Choose an encoding scheme based on which resource matters most:

* **Binary encoding** — minimizes state register width (log2(N) bits) but next-state and output decoding logic can be wider and slower as the number of states grows.
* **One-hot encoding** — uses one flop per state, but decoding logic is typically simpler and faster since only one bit is active at a time; commonly preferred on FPGAs, which have abundant flops.
* **Gray encoding** — only one bit changes between adjacent states, useful when FSM outputs feed asynchronous logic and multi-bit switching glitches must be avoided.

## Example

### Before

Encoding is left implicit; the synthesis tool chooses a default (often binary).

```verilog
localparam IDLE = 2'd0, LOAD = 2'd1, RUN = 2'd2, DONE = 2'd3;
reg [1:0] state;
```

### After

Explicit one-hot encoding for a 4-state FSM targeting an FPGA.

```verilog
localparam IDLE = 4'b0001,
           LOAD = 4'b0010,
           RUN  = 4'b0100,
           DONE = 4'b1000;
reg [3:0] state;

// A synthesis directive can also be used to request an encoding style, e.g.:
// (* fsm_encoding = "one_hot" *) reg [3:0] state;
```

## Trade-offs

* One-hot reduces decode logic depth at the cost of more state flops.
* Binary reduces flop count at the cost of decode logic depth as state count grows.
* Gray encoding avoids multi-bit output transitions but can complicate arbitrary (non-adjacent) state jumps.
* The best choice depends on the target technology (ASIC vs. FPGA) and which resource — area, timing, or power — is the binding constraint.

## Key idea

FSM state encoding trades state-register width against next-state/output decoding complexity, and the right choice depends on the target technology and which resource is most constrained.
