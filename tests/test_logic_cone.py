from pathlib import Path

from src.ast import (
    VerilogASTParser,
    ASTGraphBuilder,
    ASTMapper,
)

from src.rag import TimingFeatures

def build_timing_features(
    timing_path,
    logic_cone: dict | None = None,
    gate_delay: float | None = None,
    net_delay: float | None = None,
    fanout: int | None = None,
    logic_depth: int | None = None,
    rtl_text: str = "",
) -> TimingFeatures:

    logic_cone = logic_cone or {}

    return TimingFeatures(
        startpoint=timing_path.startpoint,
        endpoint=timing_path.endpoint,

        slack=timing_path.slack,
        path_delay=timing_path.path_delay,

        gate_delay=gate_delay,
        net_delay=net_delay,

        fanout=fanout,
        logic_depth=logic_depth,

        cells=timing_path.cells,

        ast_dependencies=logic_cone.get(
            "signals",
            [],
        ),

        ast_nodes=logic_cone.get(
            "paths",
            [],
        ),

        ast_operators=logic_cone.get(
            "operators",
            [],
        ),

        source_lines=logic_cone.get(
            "source_lines",
            [],
        ),

        rtl_text=rtl_text,
    )