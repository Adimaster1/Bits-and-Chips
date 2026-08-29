from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class TimingFeatures:
    """
    Unified timing-aware feature vector used by the RAG pipeline.

    Values coming from OpenSTA are kept separate from structural
    features derived from the RTL AST.
    """

    slack: float = 0.0

    # Timing decomposition
    gate_delay: float = 0.0
    net_delay: float = 0.0

    # Structural/timing features
    fanout: int = 0
    logic_depth: int = 0

    # AST-derived information
    ast_structure: str = ""

    # Optional path information
    startpoint: str = ""
    endpoint: str = ""

    # Number of cells on the timing path
    gate_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Return the feature vector as a dictionary."""
        return asdict(self)

    def to_vector(self):
        """
        Return the numerical feature vector.

        AST structure is intentionally excluded because it is symbolic/textual.
        """
        return [
            self.slack,
            self.gate_delay,
            self.net_delay,
            self.fanout,
            self.logic_depth,
            self.gate_count,
        ]


def build_timing_features(
    timing_path: Optional[Any] = None,
    logic_cone: Optional[Dict[str, Any]] = None,
    ast_structure: str = "",
    fanout: Optional[int] = None,
    logic_depth: Optional[int] = None,
) -> TimingFeatures:
    """
    Combine OpenSTA timing information with AST structural information.

    This is the bridge between the STA and AST branches of the pipeline.

    Parameters
    ----------
    timing_path:
        Object returned by the OpenSTA parser. Expected to expose:
        startpoint, endpoint, slack, path_delay and cells.

    logic_cone:
        AST-derived logic cone information.

    ast_structure:
        Human-readable AST representation.

    fanout:
        Explicit fanout if already calculated.

    logic_depth:
        Explicit AST logic depth if already calculated.
    """

    logic_cone = logic_cone or {}

    # ---------------------------------------------------------
    # OpenSTA features
    # ---------------------------------------------------------

    slack = float(getattr(timing_path, "slack", 0.0) or 0.0)

    path_delay = float(
        getattr(timing_path, "path_delay", 0.0) or 0.0
    )

    startpoint = str(
        getattr(timing_path, "startpoint", "") or ""
    )

    endpoint = str(
        getattr(timing_path, "endpoint", "") or ""
    )

    cells = getattr(timing_path, "cells", []) or []

    gate_count = len(cells)

    # ---------------------------------------------------------
    # AST structural features
    # ---------------------------------------------------------

    if fanout is None:
        fanout = logic_cone.get("fanout", 0)

    if logic_depth is None:
        logic_depth = logic_cone.get("logic_depth", 0)

    fanout = int(fanout or 0)
    logic_depth = int(logic_depth or 0)

    # ---------------------------------------------------------
    # Delay decomposition
    #
    # If OpenSTA has already provided gate/net delay fields,
    # use them. Otherwise retain 0 rather than inventing values.
    # ---------------------------------------------------------

    gate_delay = float(
        getattr(timing_path, "gate_delay", 0.0) or 0.0
    )

    net_delay = float(
        getattr(timing_path, "net_delay", 0.0) or 0.0
    )

    # If no explicit decomposition exists, path_delay remains
    # available through the overall timing information.
    #
    # We intentionally do NOT fabricate gate/net delay values.

    return TimingFeatures(
        slack=slack,
        gate_delay=gate_delay,
        net_delay=net_delay,
        fanout=fanout,
        logic_depth=logic_depth,
        ast_structure=ast_structure,
        startpoint=startpoint,
        endpoint=endpoint,
        gate_count=gate_count,
    )


def timing_features_to_context(features: TimingFeatures) -> str:
    """
    Convert timing features into compact RAG-readable context.
    """

    return (
        f"Slack: {features.slack:.4f} ns\n"
        f"Gate delay: {features.gate_delay:.4f} ns\n"
        f"Net delay: {features.net_delay:.4f} ns\n"
        f"Fanout: {features.fanout}\n"
        f"Logic depth: {features.logic_depth}\n"
        f"Gate count: {features.gate_count}\n"
        f"Startpoint: {features.startpoint}\n"
        f"Endpoint: {features.endpoint}\n"
        f"AST structure: {features.ast_structure}"
    )