from verification.equivalence_validator import validate_equivalence


success, eqy_output = validate_equivalence(
    original_file="sta/unoptimized.v",
    optimized_file="optimized_heavy_calculator.v",
    top_module="heavy_calculator"
)


print("\n" + "=" * 70)
print("EQUIVALENCE VALIDATION RESULT")
print("=" * 70)

if success:

    print(
        "SUCCESS: The optimized design is formally equivalent "
        "to the original design."
    )

else:

    print(
        "FAILURE: The optimized design could not be proven "
        "equivalent to the original design."
    )


print("\n" + "=" * 70)
print("EQY OUTPUT")
print("=" * 70)

print(eqy_output)