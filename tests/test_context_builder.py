from src.rag.feature_builder import (
    TimingFeatures,
)

from src.rag.retriever import (
    HybridTimingRetriever,
)

from src.rag.context_builder import (
    RAGContextBuilder,
)


def test_context_builder():

    document = TimingFeatures(
        startpoint="a",
        endpoint="result",
        slack=-0.42,
        path_delay=3.18,
        logic_depth=7,
        fanout=4,
        ast_dependencies=[
            "a",
            "sum",
            "result",
        ],
    )

    retriever = HybridTimingRetriever(
        [document]
    )

    results = retriever.retrieve(
        document,
        top_k=1,
    )

    builder = RAGContextBuilder()

    context = builder.build(
        results
    )

    assert (
        "CRITICAL RTL TIMING PATH"
        in context
    )

    assert (
        "Slack: -0.42 ns"
        in context
    )

    assert (
        "Logic Depth: 7"
        in context
    )

    assert (
        "a -> sum -> result"
        in context
    )


def test_empty_context():

    builder = RAGContextBuilder()

    context = builder.build([])

    assert (
        "No relevant timing optimization"
        in context
    )
