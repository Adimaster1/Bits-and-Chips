from __future__ import annotations

from collections import Counter
from typing import Any

import networkx as nx


class ASTGraphBuilder:
    """
    Convert a normalized AST dictionary into a NetworkX directed graph.

    Edges point:

        parent → child
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._node_counter = 0

    def build(
        self,
        normalized_ast: dict[str, Any],
    ) -> nx.DiGraph:
        """
        Build a directed AST graph.

        Parameters
        ----------
        normalized_ast:
            Output from VerilogASTParser.parse_file().

        Returns
        -------
        networkx.DiGraph
        """

        self.graph.clear()
        self._node_counter = 0

        ast_root = normalized_ast.get("ast")

        if ast_root is None:
            raise ValueError("Normalized AST does not contain 'ast'")

        source_file = normalized_ast.get("source_file")

        self._add_node_recursive(
            ast_root,
            parent_id=None,
            source_file=source_file,
            depth=0,
        )

        return self.graph

    def _add_node_recursive(
        self,
        ast_node: dict[str, Any],
        parent_id: str | None,
        source_file: str | None,
        depth: int,
    ) -> str:
        """
        Recursively add AST nodes to the graph.
        """

        node_id = self._generate_node_id()

        node_type = ast_node.get(
            "node_type",
            "Unknown",
        )

        attributes = ast_node.get(
            "attributes",
            {},
        )

        self.graph.add_node(
            node_id,
            node_type=node_type,
            attributes=attributes,
            source_file=source_file,
            depth=depth,
        )

        if parent_id is not None:

            self.graph.add_edge(
                parent_id,
                node_id,
                relationship="parent_child",
            )

        for child in ast_node.get("children", []):

            self._add_node_recursive(
                child,
                parent_id=node_id,
                source_file=source_file,
                depth=depth + 1,
            )

        return node_id

    def _generate_node_id(self) -> str:

        node_id = f"ast_{self._node_counter}"

        self._node_counter += 1

        return node_id

    def find_by_type(
        self,
        node_type: str,
    ) -> list[str]:
        """
        Return all graph node IDs with a matching AST node type.
        """

        return [
            node_id
            for node_id, data in self.graph.nodes(data=True)
            if data.get("node_type") == node_type
        ]

    def find_by_attribute(
        self,
        attribute: str,
        value: Any,
    ) -> list[str]:
        """
        Find nodes with a matching attribute.
        """

        matches = []

        for node_id, data in self.graph.nodes(data=True):

            attributes = data.get(
                "attributes",
                {},
            )

            if attributes.get(attribute) == value:
                matches.append(node_id)

        return matches

    def get_descendants(
        self,
        node_id: str,
    ) -> list[str]:
        """
        Return all descendants of an AST node.
        """

        if node_id not in self.graph:
            raise KeyError(
                f"Unknown node ID: {node_id}"
            )

        return list(
            nx.descendants(
                self.graph,
                node_id,
            )
        )

    def get_ancestors(
        self,
        node_id: str,
    ) -> list[str]:
        """
        Return all ancestors of an AST node.
        """

        if node_id not in self.graph:
            raise KeyError(
                f"Unknown node ID: {node_id}"
            )

        return list(
            nx.ancestors(
                self.graph,
                node_id,
            )
        )

    def get_node_data(
        self,
        node_id: str,
    ) -> dict[str, Any]:

        if node_id not in self.graph:
            raise KeyError(
                f"Unknown node ID: {node_id}"
            )

        return dict(
            self.graph.nodes[node_id]
        )

    def node_type_counts(self) -> dict[str, int]:
        """
        Count AST node types.
        """

        counts = Counter(
            data.get("node_type", "Unknown")
            for _, data in self.graph.nodes(data=True)
        )

        return dict(counts)

    def max_depth(self) -> int:
        """
        Return maximum AST depth.
        """

        if self.graph.number_of_nodes() == 0:
            return 0

        return max(
            data.get("depth", 0)
            for _, data in self.graph.nodes(data=True)
        )

    def summary(self) -> dict[str, Any]:
        """
        Return a compact graph summary.
        """

        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "max_depth": self.max_depth(),
            "node_types": self.node_type_counts(),
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Export graph into a JSON-serializable dictionary.
        """

        return {
            "nodes": [
                {
                    "id": node_id,
                    **data,
                }
                for node_id, data
                in self.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    **data,
                }
                for source, target, data
                in self.graph.edges(data=True)
            ],
        }
