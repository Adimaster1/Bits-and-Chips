from src.rag import (
    TimingFeatures,
    HybridTimingRetriever,
    RAGContextBuilder,
)


def test_complete_timing_rag_pipeline():

    # ---------------------------------
    # Historical optimization examples
    # ---------------------------------

    documents = [

        TimingFeatures(
            startpoint="old_a",
            endpoint="old_result",
            slack=-0.50,
            path_delay=3.20,
            fanout=4,
            logic_depth=7,
            ast_dependencies=[
                "old_a",
                "old_sum",
                "old_result",
            ],
            ast_operators=[
                "Plus",
            ],
            rtl_text=(
                "addition critical path"
            ),
        ),

        TimingFeatures(
            startpoint="clk",
            endpoint="ctrl",
            slack=1.50,
            path_delay=1.10,
            fanout=1,
            logic_depth=2,
            ast_dependencies=[
                "clk",
                "ctrl",
            ],
            rtl_text=(
                "clock control"
            ),
        ),
    ]

    # ---------------------------------
    # Current critical path
    # ---------------------------------

    query = TimingFeatures(
        startpoint="a",
        endpoint="result",
        slack=-0.42,
        path_delay=3.18,
        fanout=4,
        logic_depth=7,
        ast_dependencies=[
            "a",
            "sum",
            "result",
        ],
        ast_operators=[
            "Plus",
        ],
        rtl_text=(
            "addition critical path"
        ),
    )

    # ---------------------------------
    # Retrieve
    # ---------------------------------

    retriever = HybridTimingRetriever(
        documents
    )

    results = retriever.retrieve(
        query,
        top_k=1,
    )

    assert len(results) == 1

    best = results[0]

    assert (
        best.features.startpoint
        == "old_a"
    )

    # ---------------------------------
    # Build LLM context
    # ---------------------------------

    builder = RAGContextBuilder()

    context = builder.build(
        results
    )

    # ---------------------------------
    # Verify final context
    # ---------------------------------

    assert (
        "old_a" in context
    )

    assert (
        "old_result" in context
    )

    assert (
        "Slack:" in context
    )

    assert (
        "Path Delay:" in context
    )
