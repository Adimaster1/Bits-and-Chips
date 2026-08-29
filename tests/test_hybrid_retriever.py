from src.rag.feature_builder import (
    TimingFeatures,
)

from src.rag.retriever import (
    HybridTimingRetriever,
)


def make_documents():

    return [

        TimingFeatures(
            startpoint="a",
            endpoint="result",
            slack=-0.40,
            path_delay=3.10,
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
                "addition critical path "
                "sum result"
            ),
        ),

        TimingFeatures(
            startpoint="x",
            endpoint="out",
            slack=-0.35,
            path_delay=3.20,
            fanout=5,
            logic_depth=7,
            ast_dependencies=[
                "x",
                "add_out",
                "out",
            ],
            ast_operators=[
                "Plus",
            ],
            rtl_text=(
                "addition critical path "
                "add_out out"
            ),
        ),

        TimingFeatures(
            startpoint="clk",
            endpoint="control",
            slack=1.20,
            path_delay=1.00,
            fanout=1,
            logic_depth=2,
            ast_dependencies=[
                "clk",
                "control",
            ],
            ast_operators=[],
            rtl_text=(
                "clock control logic"
            ),
        ),
    ]


def make_query():

    return TimingFeatures(
        startpoint="a",
        endpoint="result",
        slack=-0.42,
        path_delay=3.15,
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
            "addition critical path "
            "sum result"
        ),
    )


def test_retriever_creation():

    retriever = HybridTimingRetriever(
        make_documents()
    )

    assert len(
        retriever.documents
    ) == 3


def test_weights_must_sum_to_one():

    try:

        HybridTimingRetriever(
            make_documents(),
            timing_weight=0.5,
            structural_weight=0.5,
            dependency_weight=0.5,
            lexical_weight=0.5,
        )

        assert False

    except ValueError:
        assert True


def test_retrieve_returns_top_k():

    retriever = HybridTimingRetriever(
        make_documents()
    )

    query = make_query()

    results = retriever.retrieve(
        query,
        top_k=2,
    )

    assert len(results) == 2


def test_best_match_is_relevant():

    retriever = HybridTimingRetriever(
        make_documents()
    )

    query = make_query()

    results = retriever.retrieve(
        query,
        top_k=3,
    )

    assert (
        results[0].features.startpoint
        == "a"
    )

    assert (
        results[0].features.endpoint
        == "result"
    )


def test_scores_are_sorted():

    retriever = HybridTimingRetriever(
        make_documents()
    )

    results = retriever.retrieve(
        make_query(),
        top_k=3,
    )

    scores = [
        result.score
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_score_components_exist():

    retriever = HybridTimingRetriever(
        make_documents()
    )

    result = retriever.retrieve(
        make_query(),
        top_k=1,
    )[0]

    assert 0.0 <= result.timing_score <= 1.0
    assert 0.0 <= result.structural_score <= 1.0
    assert 0.0 <= result.dependency_score <= 1.0
    assert 0.0 <= result.lexical_score <= 1.0
