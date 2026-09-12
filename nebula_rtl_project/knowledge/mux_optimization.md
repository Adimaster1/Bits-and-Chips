# Multiplexer Optimization for RTL Timing

## Problem

Deeply nested conditional statements can infer cascaded multiplexers. A signal may need to pass through multiple levels of mux logic before reaching the output, increasing combinational delay and potentially creating a critical timing path.

This is especially problematic when many conditions are checked sequentially.

## When to use it

Consider mux optimization when timing reports identify a critical path containing multiple levels of multiplexers or when RTL contains long chains of nested `if` or `else if` statements.

It is particularly useful when the conditions are mutually exclusive and can be decoded or selected more efficiently.

## Optimization strategy

Reduce unnecessary mux depth by restructuring conditional logic into a more balanced or direct selection structure.

Using a `case` statement for mutually exclusive selection conditions can make the intended mux structure clearer and may allow synthesis tools to implement the logic more efficiently.

## Example

### Before

A long chain of conditional statements can infer cascaded mux logic.

```verilog
always @(*) begin
    if (sel == 2'd0)
        result = input0;
    else if (sel == 2'd1)
        result = input1;
    else if (sel == 2'd2)
        result = input2;
    else
        result = input3;
end
```

Each condition is evaluated as part of a sequential priority chain.

### After

Use a `case` statement when the selection values are mutually exclusive.

```verilog
always @(*) begin
    case (sel)
        2'd0:    result = input0;
        2'd1:    result = input1;
        2'd2:    result = input2;
        default: result = input3;
    endcase
end
```

This describes a direct selection between the inputs rather than an intentional priority chain.

## Additional example: avoid unnecessary priority logic

### Before

```verilog
always @(*) begin
    if (cond0)
        result = input0;
    else if (cond1)
        result = input1;
    else if (cond2)
        result = input2;
    else
        result = input3;
end
```

If the conditions are guaranteed to be mutually exclusive, the priority behavior may be unnecessary.

### After

The conditions can be encoded into a selector and used with a direct `case` statement.

```verilog
always @(*) begin
    case ({cond2, cond1, cond0})
        3'b001:  result = input0;
        3'b010:  result = input1;
        3'b100:  result = input2;
        default: result = input3;
    endcase
end
```

The exact implementation should depend on the intended functional behavior. Do not remove priority logic if priority between conditions is required.

## Trade-offs

* Can reduce mux depth and improve critical-path timing.
* May make the RTL easier for synthesis tools to optimize.
* Incorrectly converting priority logic into parallel selection can change functionality.
* The best structure depends on whether conditions are mutually exclusive or priority-dependent.

## Key idea

Mux optimization improves timing by reducing unnecessary cascaded selection logic while preserving the intended priority and functional behavior.

