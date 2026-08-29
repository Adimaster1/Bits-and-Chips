from __future__ import annotations

from collections import defaultdict
from typing import Any

import networkx as nx


class ASTMapper:
    """
    Semantic mapper for the Verilog AST graph.

    Version 2 responsibilities:
        - index modules
        - index always blocks
        - index conditional logic
        - index identifiers/signals
        - identify assignments
        - build signal dependency graph
        - provide local structural context
    """

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

        self._nodes_by_type: dict[str, list[str]] = (
            defaultdict(list)
        )

        self._index_nodes()

        self.dependency_graph = (
            self._build_dependency_graph()
        )

    # ==========================================================
    # INDEXING
    # ==========================================================

    def _index_nodes(self) -> None:
        """
        Build an index by AST node type.
        """

        for node_id, data in self.graph.nodes(
            data=True
        ):
            node_type = data.get(
                "node_type"
            )

            if node_type:
                self._nodes_by_type[
                    node_type
                ].append(node_id)

    def find_by_type(
        self,
        node_type: str,
    ) -> list[str]:
        """
        Return node IDs matching a Verilog AST node type.
        """

        return list(
            self._nodes_by_type.get(
                node_type,
                [],
            )
        )

    # ==========================================================
    # COMMON AST QUERIES
    # ==========================================================

    def module_nodes(self) -> list[str]:
        return self.find_by_type(
            "ModuleDef"
        )

    def always_nodes(self) -> list[str]:
        return self.find_by_type(
            "Always"
        )

    def conditional_nodes(self) -> list[str]:
        return self.find_by_type(
            "IfStatement"
        )

    def identifier_nodes(self) -> list[str]:
        return self.find_by_type(
            "Identifier"
        )

    def assignment_nodes(self) -> list[str]:
        """
        Return blocking/non-blocking/continuous
        assignment nodes.
        """

        assignment_types = {
            "Assign",
            "BlockingSubstitution",
            "NonblockingSubstitution",
        }

        result = []

        for node_type in assignment_types:
            result.extend(
                self.find_by_type(
                    node_type
                )
            )

        return result

    # ==========================================================
    # SIGNAL INDEX
    # ==========================================================

    def get_signal_names(self) -> list[str]:
        """
        Return unique identifiers found in the AST.
        """

        names = set()

        for node_id in self.identifier_nodes():

            data = self.graph.nodes[node_id]

            attributes = data.get(
                "attributes",
                {},
            )

            name = attributes.get(
                "name"
            )

            if name:
                names.add(name)

        return sorted(names)

    def find_signal(
        self,
        name: str,
    ) -> list[str]:
        """
        Find AST identifier nodes representing a signal.
        """

        matches = []

        for node_id in self.identifier_nodes():

            attributes = self.graph.nodes[
                node_id
            ].get(
                "attributes",
                {},
            )

            if attributes.get(
                "name"
            ) == name:
                matches.append(node_id)

        return matches

    # ==========================================================
    # ASSIGNMENT ANALYSIS
    # ==========================================================

    def _assignment_target(
        self,
        assignment_id: str,
    ) -> str | None:
        """
        Find the signal assigned by an assignment node.

        Handles structures such as:

            Assign
              Lvalue
                Identifier(result)
        """

        descendants = nx.descendants(
            self.graph,
            assignment_id,
        )

        # Include direct children too.
        descendants.add(
            assignment_id
        )

        for node_id in descendants:

            data = self.graph.nodes[
                node_id
            ]

            node_type = data.get(
                "node_type"
            )

            if node_type != "Identifier":
                continue

            attributes = data.get(
                "attributes",
                {},
            )

            name = attributes.get(
                "name"
            )

            if not name:
                continue

            # Check whether this identifier
            # belongs to an Lvalue.
            ancestors = nx.ancestors(
                self.graph,
                node_id,
            )

            if any(
                self.graph.nodes[a].get(
                    "node_type"
                )
                == "Lvalue"
                for a in ancestors
            ):
                return name

        return None

    def _assignment_sources(
        self,
        assignment_id: str,
    ) -> list[str]:
        """
        Find source signals used by an assignment.

        Example:

            assign sum = a + b;

        returns:

            ["a", "b"]
        """

        sources = []

        descendants = nx.descendants(
            self.graph,
            assignment_id,
        )

        for node_id in descendants:

            data = self.graph.nodes[
                node_id
            ]

            if data.get(
                "node_type"
            ) != "Identifier":
                continue

            attributes = data.get(
                "attributes",
                {},
            )

            name = attributes.get(
                "name"
            )

            if not name:
                continue

            ancestors = nx.ancestors(
                self.graph,
                node_id,
            )

            # Ignore identifiers belonging
            # to the assignment target.
            is_lvalue = any(
                self.graph.nodes[a].get(
                    "node_type"
                )
                == "Lvalue"
                for a in ancestors
            )

            if not is_lvalue:
                sources.append(name)

        return sorted(
            set(sources)
        )

    # ==========================================================
    # DEPENDENCY GRAPH
    # ==========================================================

    def _build_dependency_graph(
        self,
    ) -> nx.DiGraph:
        """
        Build a signal-level dependency graph.

        Edge direction:

            source_signal -> destination_signal

        Example:

            assign sum = a + b;

        produces:

            a -> sum
            b -> sum
        """

        dependency_graph = nx.DiGraph()

        # Add all known signals as nodes.
        for signal in self.get_signal_names():
            dependency_graph.add_node(
                signal
            )

        for assignment_id in (
            self.assignment_nodes()
        ):

            target = self._assignment_target(
                assignment_id
            )

            if target is None:
                continue

            sources = self._assignment_sources(
                assignment_id
            )

            line = self.graph.nodes[
                assignment_id
            ].get(
                "attributes",
                {},
            ).get(
                "line"
            )

            for source in sources:

                dependency_graph.add_edge(
                    source,
                    target,
                    assignment_node=assignment_id,
                    line=line,
                )

        return dependency_graph

    def get_dependency_graph(
        self,
    ) -> nx.DiGraph:
        """
        Return a copy of the semantic dependency graph.
        """

        return self.dependency_graph.copy()

    # ==========================================================
    # DEPENDENCY QUERIES
    # ==========================================================

    def signal_dependencies(
        self,
        signal: str,
    ) -> list[str]:
        """
        Return direct source signals feeding a signal.
        """

        if signal not in self.dependency_graph:
            return []

        return sorted(
            self.dependency_graph.predecessors(
                signal
            )
        )

    def signal_dependents(
        self,
        signal: str,
    ) -> list[str]:
        """
        Return signals directly driven by a signal.
        """

        if signal not in self.dependency_graph:
            return []

        return sorted(
            self.dependency_graph.successors(
                signal
            )
        )

    def transitive_dependencies(
        self,
        signal: str,
    ) -> list[str]:
        """
        Return all upstream signals contributing
        to a signal.
        """

        if signal not in self.dependency_graph:
            return []

        return sorted(
            nx.ancestors(
                self.dependency_graph,
                signal,
            )
        )

    def transitive_dependents(
        self,
        signal: str,
    ) -> list[str]:
        """
        Return all downstream signals.
        """

        if signal not in self.dependency_graph:
            return []

        return sorted(
            nx.descendants(
                self.dependency_graph,
                signal,
            )
        )
    
    # ==========================================================
    # LOCAL AST CONTEXT
    # ==========================================================

    def ancestors(
        self,
        node_id: str,
    ) -> list[str]:
        """
        Return AST ancestors of a node.
        """

        return list(
            nx.ancestors(
                self.graph,
                node_id,
            )
        )

    def descendants(
        self,
        node_id: str,
    ) -> list[str]:
        """
        Return AST descendants of a node.
        """

        return list(
            nx.descendants(
                self.graph,
                node_id,
            )
        )

    def local_context(
        self,
        node_id: str,
        max_descendants: int = 20,
    ) -> dict[str, Any]:
        """
        Extract compact structural context around a node.
        """

        if node_id not in self.graph:
            raise KeyError(
                f"Unknown AST node: {node_id}"
            )

        target = self.graph.nodes[
            node_id
        ]

        ancestors = []

        for ancestor in self.ancestors(
            node_id
        ):

            data = self.graph.nodes[
                ancestor
            ]

            ancestors.append(
                {
                    "node_id": ancestor,
                    "node_type": data.get(
                        "node_type"
                    ),
                    "attributes": data.get(
                        "attributes",
                        {},
                    ),
                    "depth": data.get(
                        "depth"
                    ),
                }
            )

        descendants = []

        for descendant in self.descendants(
            node_id
        ):

            if len(descendants) >= max_descendants:
                break

            data = self.graph.nodes[
                descendant
            ]

            descendants.append(
                {
                    "node_id": descendant,
                    "node_type": data.get(
                        "node_type"
                    ),
                    "attributes": data.get(
                        "attributes",
                        {},
                    ),
                    "depth": data.get(
                        "depth"
                    ),
                }
            )

        return {
            "target": {
                "node_id": node_id,
                "node_type": target.get(
                    "node_type"
                ),
                "attributes": target.get(
                    "attributes",
                    {},
                ),
                "depth": target.get(
                    "depth"
                ),
            },
            "ancestors": ancestors,
            "descendants": descendants,
        }
