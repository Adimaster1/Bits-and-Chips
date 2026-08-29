from __future__ import annotations

from .retriever import RetrievalResult


class RAGContextBuilder:

    """
    Converts ranked retrieval results into
    structured context for the LLM.
    """

    def build(
        self,
        results: list[RetrievalResult],
    ) -> str:

        if not results:
            return (
                "No relevant timing optimization "
                "examples were retrieved."
            )

        sections = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            features = result.features

            section = [
                f"===== SIMILAR CASE {index} =====",
                f"Retrieval Score: "
                f"{result.score:.4f}",
                "",
                features.to_text(),
            ]

            if result.reasons:
                section.extend(
                    [
                        "",
                        "Why Retrieved:",
                        *[
                            f"- {reason}"
                            for reason in result.reasons
                        ],
                    ]
                )

            sections.append(
                "\n".join(section)
            )

        return "\n\n".join(sections)