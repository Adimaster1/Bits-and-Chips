from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class TimingFeatures:
    """
    Unified timing + RTL representation used by
    the Timing-RAG retriever.
    """

    startpoint: str
    endpoint: str

    slack: float
    path_delay: float

    gate_delay: float | None = None
    net_delay: float | None = None

    fanout: int | None = None
    logic_depth: int | None = None

    cells: list[str] | None = None

    ast_dependencies: list[str] | None = None
    ast_nodes: list[str] | None = None
    ast_operators: list[str] | None = None

    control_conditions: list[str] | None = None
    source_lines: list[int] | None = None

    rtl_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_text(self) -> str:
        """
        Convert the structured representation into
        retrieval/LLM-friendly text.
        """

        lines = [
            "CRITICAL RTL TIMING PATH",
            f"Startpoint: {self.startpoint}",
            f"Endpoint: {self.endpoint}",
            f"Slack: {self.slack} ns",
            f"Path Delay: {self.path_delay} ns",
        ]

        if self.gate_delay is not None:
            lines.append(
                f"Gate Delay: {self.gate_delay} ns"
            )

        if self.net_delay is not None:
            lines.append(
                f"Net Delay: {self.net_delay} ns"
            )

        if self.fanout is not None:
            lines.append(
                f"Fanout: {self.fanout}"
            )

        if self.logic_depth is not None:
            lines.append(
                f"Logic Depth: {self.logic_depth}"
            )

        if self.cells:
            lines.extend(
                [
                    "",
                    "Cell Path:",
                    " -> ".join(self.cells),
                ]
            )

        if self.ast_dependencies:
            lines.extend(
                [
                    "",
                    "AST Dependencies:",
                    " -> ".join(
                        self.ast_dependencies
                    ),
                ]
            )

        if self.ast_operators:
            lines.extend(
                [
                    "",
                    "AST Operators:",
                    ", ".join(
                        self.ast_operators
                    ),
                ]
            )

        if self.control_conditions:
            lines.extend(
                [
                    "",
                    "Control Conditions:",
                    *self.control_conditions,
                ]
            )

        if self.source_lines:
            lines.extend(
                [
                    "",
                    "RTL Source Lines:",
                    ", ".join(
                        map(
                            str,
                            self.source_lines,
                        )
                    ),
                ]
            )

        if self.rtl_text:
            lines.extend(
                [
                    "",
                    "RTL Context:",
                    self.rtl_text,
                ]
            )

        return "\n".join(lines)