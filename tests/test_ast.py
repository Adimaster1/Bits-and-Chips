from pathlib import Path

from src.ast import (
    ASTGraphBuilder,
    ASTMapper,
    VerilogASTParser,
)


def test_verilog_ast_pipeline():

    rtl_file = (
        Path(__file__)
        .parent
        .parent
        / "data"
        / "rtl"
        / "sample_alu.v"
    )

    parser = VerilogASTParser()

    normalized_ast = parser.parse_file(
        rtl_file
    )

    assert "ast" in normalized_ast

    builder = ASTGraphBuilder()

    graph = builder.build(
        normalized_ast
    )

    assert graph.number_of_nodes() > 0

    mapper = ASTMapper(graph)

    modules = mapper.module_nodes()

    assert len(modules) > 0

    always_blocks = mapper.always_blocks()

    assert len(always_blocks) > 0

    conditional_nodes = mapper.conditional_nodes()

    assert len(conditional_nodes) > 0
