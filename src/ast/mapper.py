from __future__ import annotations

from typing import Any

import networkx as nx


class ASTMapper:
    """
    Utility class for mapping RTL identifiers to AST graph nodes.

    This class is intentionally independent from OpenSTA.

    Future timing integration can provide:
        - instance names
        - net names
        - signal names

    and use this class to locate relevant RTL structures.
    """

    def __init__(
        self,
        graph: nx.DiGraph,
    ):
        self.graph = graph

    def find_identifier(
        self,
        name: str,
    ) -> list[str]:
        """
        Find AST nodes whose attributes contain a matching identifier.
        """

        matches = []

        for node_id, data in self.graph.nodes(data=True):

            attributes = data.get(
                "attributes",
                {},
            )

            for key, value in attributes.items():

                if value == name:

                    matches.append(node_id)

                elif isinstance(value, list) and name in value:

                    matches.append(node_id)

        return list(set(matches))

    def find_nodes_at_line(
        self,
        line_number: int,
    ) -> list[str]:
        """
        Find AST nodes associated with a source line.
        """

        return [
            node_id
            for node_id, data in self.graph.nodes(data=True)
            if data.get(
                "attributes",
                {},
            ).get("line") == line_number
        ]

    def get_context(
        self,
        node_id: str,
        ancestor_levels: int = 3,
        descendant_levels: int = 3,
    ) -> dict[str, Any]:
        """
        Extract local AST context around a node.

        Useful later for constructing targeted RAG context.
        """

        if node_id not in self.graph:
            raise KeyError(
                f"Unknown AST node: {node_id}"
            )

        ancestors = self._limited_traversal(
            node_id=node_id,
            direction="up",
            max_depth=ancestor_levels,
        )

        descendants = self._limited_traversal(
            node_id=node_id,
            direction="down",
            max_depth=descendant_levels,
        )

        return {
            "target": self._serialize_node(node_id),
            "ancestors": [
                self._serialize_node(node)
                for node in ancestors
            ],
            "descendants": [
                self._serialize_node(node)
                for node in descendants
            ],
        }

    def _limited_traversal(
        self,
        node_id: str,
        direction: str,
        max_depth: int,
    ) -> list[str]:

        visited = []
        frontier = [
            (node_id, 0)
        ]

        seen = {
            node_id
        }

        while frontier:

            current, depth = frontier.pop(0)

            if depth >= max_depth:
                continue

            if direction == "up":
                neighbors = list(
                    self.graph.predecessors(current)
                )
            else:
                neighbors = list(
                    self.graph.successors(current)
                )

            for neighbor in neighbors:

                if neighbor in seen:
                    continue

                seen.add(neighbor)

                visited.append(neighbor)

                frontier.append(
                    (
                        neighbor,
                        depth + 1,
                    )
                )

        return visited

    def _serialize_node(
        self,
        node_id: str,
    ) -> dict[str, Any]:

        data = dict(
            self.graph.nodes[node_id]
        )

        return {
            "node_id": node_id,
            "node_type": data.get(
                "node_type"
            ),
            "attributes": data.get(
                "attributes",
                {}
            ),
            "depth": data.get(
                "depth"
            ),
        }

    def module_nodes(self) -> list[str]:
        """
        Return all ModuleDef nodes.
        """

        return [
            node_id
            for node_id, data in self.graph.nodes(data=True)
            if data.get("node_type") == "ModuleDef"
        ]

    def always_blocks(self) -> list[str]:
        """
        Return all Always blocks.
        """

        return [
            node_id
            for node_id, data in self.graph.nodes(data=True)
            if data.get("node_type") == "Always"
        ]

    def conditional_nodes(self) -> list[str]:
        """
        Return conditional AST nodes.

        Includes:
        - IfStatement
        - CaseStatement
        """

        conditional_types = {
            "IfStatement",
            "CaseStatement",
        }

        return [
            node_id
            for node_id, data in self.graph.nodes(data=True)
            if data.get("node_type")
            in conditional_types
        ]
