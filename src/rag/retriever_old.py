from __future__ import annotations

from dataclasses import dataclass

from .feature_builder import TimingFeatures


@dataclass
class RetrievalResult:

    features: TimingFeatures

    score: float

    reasons: list[str]


class TimingRetriever:

    def __init__(
        self,
        documents: list[TimingFeatures],
    ):
        self.documents = documents

    def _timing_similarity(
        self,
        query: TimingFeatures,
        candidate: TimingFeatures,
    ) -> float:

        slack_distance = abs(
            query.slack
            - candidate.slack
        )

        delay_distance = abs(
            query.path_delay
            - candidate.path_delay
        )

        return (
            1.0
            / (
                1.0
                + slack_distance
                + delay_distance
            )
        )

    def _dependency_similarity(
        self,
        query: TimingFeatures,
        candidate: TimingFeatures,
    ) -> float:

        query_deps = set(
            query.ast_dependencies
            or []
        )

        candidate_deps = set(
            candidate.ast_dependencies
            or []
        )

        if not query_deps:
            return 0.0

        intersection = (
            query_deps
            & candidate_deps
        )

        union = (
            query_deps
            | candidate_deps
        )

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _structural_similarity(
        self,
        query: TimingFeatures,
        candidate: TimingFeatures,
    ) -> float:

        if (
            query.logic_depth is None
            or candidate.logic_depth is None
        ):
            return 0.0

        depth_distance = abs(
            query.logic_depth
            - candidate.logic_depth
        )

        return 1.0 / (
            1.0 + depth_distance
        )

    def score(
        self,
        query: TimingFeatures,
        candidate: TimingFeatures,
    ) -> tuple[float, list[str]]:

        timing = (
            self._timing_similarity(
                query,
                candidate,
            )
        )

        dependency = (
            self._dependency_similarity(
                query,
                candidate,
            )
        )

        structural = (
            self._structural_similarity(
                query,
                candidate,
            )
        )

        score = (
            0.5 * timing
            + 0.3 * dependency
            + 0.2 * structural
        )

        reasons = []

        if timing > 0.5:
            reasons.append(
                "similar timing characteristics"
            )

        if dependency > 0:
            reasons.append(
                "overlapping RTL dependencies"
            )

        if structural > 0.5:
            reasons.append(
                "similar logic depth"
            )

        return score, reasons

    def retrieve(
        self,
        query: TimingFeatures,
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        results = []

        for document in self.documents:

            score, reasons = self.score(
                query,
                document,
            )

            results.append(
                RetrievalResult(
                    features=document,
                    score=score,
                    reasons=reasons,
                )
            )

        results.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return results[:top_k]