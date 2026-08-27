from pathlib import Path

from src.ast import (
    ASTGraphBuilder,
    ASTMapper,
    VerilogASTParser,
)
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RTL_FILE = (
    PROJECT_ROOT
    / "data"
    / "rtl"
    / "sample_alu.v"
)

def test_missing_file():

    parser = VerilogASTParser()

    with pytest.raises(FileNotFoundError):

        parser.parse_file(
            "does_not_exist.v"
        )

def build_pipeline():
    """
    Shared helper that builds the complete AST pipeline.
    """

    parser = VerilogASTParser()

    normalized_ast = parser.parse_file(RTL_FILE)

    builder = ASTGraphBuilder()

    graph = builder.build(normalized_ast)

    mapper = ASTMapper(graph)

    return normalized_ast, builder, graph, mapper


def test_parser_output():
    """
    Test:
        Verilog file → normalized AST
    """

    normalized_ast, _, _, _ = build_pipeline()

    assert "source_file" in normalized_ast
    assert "ast" in normalized_ast

    assert normalized_ast["ast"]["node_type"] == "Source"


def test_graph_creation():
    """
    Test:
        normalized AST → NetworkX graph
    """

    _, builder, graph, _ = build_pipeline()

    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

    summary = builder.summary()

    assert summary["nodes"] > 0
    assert summary["edges"] > 0
    assert summary["max_depth"] > 0


def test_module_detection():
    """
    Verify that the module can be found.
    """

    _, builder, _, mapper = build_pipeline()

    modules = mapper.module_nodes()

    assert len(modules) == 1

    module_data = builder.get_node_data(modules[0])

    assert module_data["node_type"] == "ModuleDef"

    assert (
        module_data["attributes"]["name"]
        == "sample_alu"
    )


def test_always_block_detection():
    """
    Verify sequential logic detection.
    """

    _, builder, _, mapper = build_pipeline()

    always_blocks = mapper.always_blocks()

    assert len(always_blocks) >= 1

    for node_id in always_blocks:

        data = builder.get_node_data(node_id)

        assert data["node_type"] == "Always"


def test_conditional_detection():
    """
    Verify nested IfStatements are detected.
    """

    _, builder, _, mapper = build_pipeline()

    conditionals = mapper.conditional_nodes()

    assert len(conditionals) >= 1

    for node_id in conditionals:

        data = builder.get_node_data(node_id)

        assert data["node_type"] in {
            "IfStatement",
            "CaseStatement",
        }


def test_find_by_type():
    """
    Test graph type-based queries.
    """

    _, builder, _, _ = build_pipeline()

    if_nodes = builder.find_by_type(
        "IfStatement"
    )

    assert len(if_nodes) >= 1


def test_identifier_lookup():
    """
    Test mapper identifier search.
    """

    _, _, _, mapper = build_pipeline()

    matches = mapper.find_identifier(
        "sample_alu"
    )

    assert len(matches) >= 1


def test_ancestor_descendant_queries():
    """
    Verify parent-child graph relationships.
    """

    _, builder, graph, mapper = build_pipeline()

    modules = mapper.module_nodes()

    module_id = modules[0]

    descendants = builder.get_descendants(
        module_id
    )

    assert len(descendants) > 0

    descendant_id = descendants[0]

    ancestors = builder.get_ancestors(
        descendant_id
    )

    assert len(ancestors) > 0


def test_local_context_extraction():
    """
    Test AST context extraction around an IfStatement.
    """

    _, builder, _, mapper = build_pipeline()

    if_nodes = builder.find_by_type(
        "IfStatement"
    )

    assert len(if_nodes) > 0

    context = mapper.get_context(
        if_nodes[0],
        ancestor_levels=3,
        descendant_levels=3,
    )

    assert "target" in context
    assert "ancestors" in context
    assert "descendants" in context

    assert (
        context["target"]["node_type"]
        == "IfStatement"
    )


def test_graph_export():
    """
    Verify graph can be exported into JSON-friendly data.
    """

    _, builder, graph, _ = build_pipeline()

    exported = builder.to_dict()

    assert "nodes" in exported
    assert "edges" in exported

    assert len(exported["nodes"]) == (
        graph.number_of_nodes()
    )

    assert len(exported["edges"]) == (
        graph.number_of_edges()
    )


def test_ast_pipeline_end_to_end():
    """
    Complete integration test.

    Verilog
        ↓
    Parser
        ↓
    Normalized AST
        ↓
    Graph
        ↓
    Mapper
        ↓
    Context extraction
    """

    normalized_ast, builder, graph, mapper = (
        build_pipeline()
    )

    assert normalized_ast["ast"] is not None

    assert graph.number_of_nodes() > 0

    modules = mapper.module_nodes()

    assert len(modules) > 0

    always_blocks = mapper.always_blocks()

    assert len(always_blocks) > 0

    if_nodes = builder.find_by_type(
        "IfStatement"
    )

    assert len(if_nodes) > 0

    context = mapper.get_context(
        if_nodes[0]
    )

    assert context["target"]["node_type"] == (
        "IfStatement"
    )
