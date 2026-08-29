from pathlib import Path

from src.ast import (
    ASTGraphBuilder,
    ASTMapper,
    VerilogASTParser,
)

from src.ast.visualize import (
    visualize_ast,
    visualize_subgraph,
    visualize_dependency_graph,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RTL_FILE = (
    PROJECT_ROOT
    / "data"
    / "rtl"
    / "sample_alu.v"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ast_visualizations"
)


def main():

    print("=" * 70)
    print("TIMING-RAG AST VISUALIZATION")
    print("=" * 70)

    # --------------------------------------------------
    # PARSE
    # --------------------------------------------------

    parser = VerilogASTParser()

    normalized_ast = parser.parse_file(
        RTL_FILE
    )

    # --------------------------------------------------
    # BUILD GRAPH
    # --------------------------------------------------

    builder = ASTGraphBuilder()

    graph = builder.build(
        normalized_ast
    )

    mapper = ASTMapper(
        graph
    )

    # --------------------------------------------------
    # 1. FULL AST
    # --------------------------------------------------

    full_ast_file = (
        OUTPUT_DIR
        / "sample_alu_full_ast.png"
    )

    print(
        "\n[1] Full AST:"
    )

    visualize_ast(
        graph,
        full_ast_file,
        title="sample_alu.v — Full Verilog AST",
    )

    print(
        full_ast_file
    )

    # --------------------------------------------------
    # 2. MODULE SUBGRAPH
    # --------------------------------------------------

    modules = mapper.module_nodes()

    if modules:

        module_file = (
            OUTPUT_DIR
            / "sample_alu_module_ast.png"
        )

        print(
            "\n[2] Module AST:"
        )

        visualize_subgraph(
            graph,
            modules[0],
            module_file,
            ancestor_levels=1,
            descendant_levels=8,
            title="sample_alu.v — Module AST",
        )

        print(
            module_file
        )

    # --------------------------------------------------
    # 3. CONTROL LOGIC
    # --------------------------------------------------

    conditionals = (
        mapper.conditional_nodes()
    )

    if conditionals:

        control_file = (
            OUTPUT_DIR
            / "sample_alu_control_ast.png"
        )

        print(
            "\n[3] Control-flow AST:"
        )

        visualize_subgraph(
            graph,
            conditionals[0],
            control_file,
            ancestor_levels=4,
            descendant_levels=6,
            title="sample_alu.v — Control Logic",
        )

        print(
            control_file
        )

    # --------------------------------------------------
    # 4. DEPENDENCY GRAPH
    # --------------------------------------------------

    dependency_file = (
        OUTPUT_DIR
        / "sample_alu_dependencies.png"
    )

    print(
        "\n[4] Signal Dependency Graph:"
    )

    visualize_dependency_graph(
        mapper.get_dependency_graph(),
        dependency_file,
        title="sample_alu.v — RTL Signal Dependencies",
    )

    print(
        dependency_file
    )

    # --------------------------------------------------
    # DONE
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE")
    print("=" * 70)

    print(
        f"\nImages generated in:\n{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
