from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


def _node_label(node_id: str, data: dict) -> str:
    """
    Create a readable label for an AST node.
    """

    node_type = data.get("node_type", "Unknown")
    attributes = data.get("attributes", {})

    name = attributes.get("name")
    line = attributes.get("line")

    parts = [node_type]

    if name:
        parts.append(f"name={name}")

    if line is not None:
        parts.append(f"line={line}")

    return "\\n".join(parts)


def visualize_ast(
    graph: nx.DiGraph,
    output_file: str | Path,
    title: str = "Verilog AST",
) -> None:
    """
    Render the complete AST graph.
    """

    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(24, 18)
    )

    pos = nx.nx_agraph.graphviz_layout(
        graph,
        prog="dot",
    )

    labels = {
        node_id: _node_label(
            node_id,
            data,
        )
        for node_id, data
        in graph.nodes(data=True)
    }

    nx.draw(
        graph,
        pos,
        labels=labels,
        with_labels=True,
        node_size=1800,
        font_size=6,
        arrows=True,
    )

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def visualize_subgraph(
    graph: nx.DiGraph,
    root_node: str,
    output_file: str | Path,
    ancestor_levels: int = 3,
    descendant_levels: int = 4,
    title: str = "AST Subgraph",
) -> None:
    """
    Render a local AST region around a node.
    """

    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ancestors = nx.ancestors(
        graph,
        root_node,
    )

    descendants = nx.descendants(
        graph,
        root_node,
    )

    # Select ancestors by distance.
    selected_ancestors = []

    for node in ancestors:

        try:
            distance = nx.shortest_path_length(
                graph,
                node,
                root_node,
            )
        except nx.NetworkXNoPath:
            continue

        if distance <= ancestor_levels:
            selected_ancestors.append(node)

    # Select descendants by distance.
    selected_descendants = []

    for node in descendants:

        try:
            distance = nx.shortest_path_length(
                graph,
                root_node,
                node,
            )
        except nx.NetworkXNoPath:
            continue

        if distance <= descendant_levels:
            selected_descendants.append(node)

    nodes = {
        root_node,
        *selected_ancestors,
        *selected_descendants,
    }

    subgraph = graph.subgraph(nodes).copy()

    plt.figure(
        figsize=(18, 12)
    )

    pos = nx.nx_agraph.graphviz_layout(
        subgraph,
        prog="dot",
    )

    labels = {
        node_id: _node_label(
            node_id,
            data,
        )
        for node_id, data
        in subgraph.nodes(data=True)
    }

    nx.draw(
        subgraph,
        pos,
        labels=labels,
        with_labels=True,
        node_size=2200,
        font_size=7,
        arrows=True,
    )

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def visualize_dependency_graph(
    dependency_graph: nx.DiGraph,
    output_file: str | Path,
    title: str = "RTL Signal Dependency Graph",
) -> None:
    """
    Render the semantic signal dependency graph.
    """

    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(14, 10)
    )

    pos = nx.spring_layout(
        dependency_graph,
        seed=42,
    )

    nx.draw(
        dependency_graph,
        pos,
        with_labels=True,
        node_size=3000,
        font_size=10,
        arrows=True,
    )

    edge_labels = {}

    for source, target, data in (
        dependency_graph.edges(
            data=True
        )
    ):

        line = data.get("line")

        if line is not None:
            edge_labels[
                (source, target)
            ] = f"line {line}"

    nx.draw_networkx_edge_labels(
        dependency_graph,
        pos,
        edge_labels=edge_labels,
        font_size=8,
    )

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()