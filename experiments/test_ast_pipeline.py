import json
from pathlib import Path

from src.ast import (
    ASTGraphBuilder,
    ASTMapper,
    VerilogASTParser,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RTL_FILE = (
    PROJECT_ROOT
    / "data"
    / "rtl"
    / "sample_alu.v"
)


def main():

    print("\n" + "=" * 70)
    print("TIMING-RAG AST MODULE INTEGRATION TEST")
    print("=" * 70)

    # --------------------------------------------------
    # 1. PARSE
    # --------------------------------------------------

    print("\n[1] PARSING VERILOG")

    parser = VerilogASTParser()

    normalized_ast = parser.parse_file(
        RTL_FILE
    )

    print(
        "Source:",
        normalized_ast["source_file"]
    )

    print(
        "Root node:",
        normalized_ast["ast"]["node_type"]
    )

    # --------------------------------------------------
    # 2. GRAPH
    # --------------------------------------------------

    print("\n[2] BUILDING AST GRAPH")

    builder = ASTGraphBuilder()

    graph = builder.build(
        normalized_ast
    )

    summary = builder.summary()

    print(
        json.dumps(
            summary,
            indent=2
        )
    )

    # --------------------------------------------------
    # 3. MAPPER
    # --------------------------------------------------

    print("\n[3] MAPPER QUERIES")

    mapper = ASTMapper(graph)

    print("\nModules:")

    for node_id in mapper.module_nodes():

        print(
            node_id,
            builder.get_node_data(node_id)
        )

    print("\nAlways blocks:")

    for node_id in mapper.always_blocks():

        print(
            node_id,
            builder.get_node_data(node_id)
        )

    print("\nConditional nodes:")

    conditional_nodes = (
        mapper.conditional_nodes()
    )

    for node_id in conditional_nodes:

        print(
            node_id,
            builder.get_node_data(node_id)
        )

    # --------------------------------------------------
    # 4. CONTEXT
    # --------------------------------------------------

    print("\n[4] LOCAL CONTEXT")

    if conditional_nodes:

        target = conditional_nodes[0]

        context = mapper.get_context(
            target,
            ancestor_levels=3,
            descendant_levels=3,
        )

        print(
            json.dumps(
                context,
                indent=2,
            )
        )

    # --------------------------------------------------
    # 5. GRAPH EXPORT
    # --------------------------------------------------

    print("\n[5] EXPORTING GRAPH")

    output_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "sample_alu_ast_graph.json"
    )

    exported_graph = builder.to_dict()

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            exported_graph,
            f,
            indent=2,
        )

    print(
        f"Graph exported to:\n{output_file}"
    )

    print("\n" + "=" * 70)
    print("AST PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
