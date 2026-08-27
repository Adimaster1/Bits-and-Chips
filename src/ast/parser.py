from __future__ import annotations

from pathlib import Path
from typing import Any

from pyverilog.vparser.parser import parse


class VerilogASTParser:
    """
    Parse Verilog RTL into a normalized AST representation.

    The output is a recursive Python dictionary so downstream
    modules do not need to directly depend on PyVerilog AST objects.
    """

    def __init__(self, include_dirs: list[str] | None = None):
        self.include_dirs = include_dirs or []

    def parse_file(self, file_path: str | Path) -> dict[str, Any]:
        """
        Parse a Verilog file.

        Parameters
        ----------
        file_path:
            Path to a Verilog source file.

        Returns
        -------
        dict
            Normalized AST tree.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Verilog file not found: {file_path}"
            )

        ast, directives = parse(
            [str(file_path)],
            preprocess_include=self.include_dirs,
        )

        return {
            "source_file": str(file_path.resolve()),
            "directives": directives,
            "ast": self._normalize_node(ast),
        }

    def _normalize_node(self, node: Any) -> Any:
        """
        Convert a PyVerilog AST node into JSON-friendly Python data.
        """

        if node is None:
            return None

        if isinstance(node, (str, int, float, bool)):
            return node

        if isinstance(node, (list, tuple)):
            return [
                self._normalize_node(item)
                for item in node
            ]

        result: dict[str, Any] = {
            "node_type": node.__class__.__name__
        }

        attributes = self._extract_attributes(node)

        if attributes:
            result["attributes"] = attributes

        children = []

        if hasattr(node, "children"):
            try:
                for child in node.children():
                    children.append(
                        self._normalize_node(child)
                    )
            except Exception:
                pass

        if children:
            result["children"] = children

        return result

    def _extract_attributes(self, node: Any) -> dict[str, Any]:
        """
        Extract useful scalar attributes from a PyVerilog AST node.

        Complex child nodes are excluded because they are represented
        separately in the recursive `children` field.
        """

        attributes: dict[str, Any] = {}

        if not hasattr(node, "__dict__"):
            return attributes

        ignored = {
            "lineno",
        }

        for key, value in node.__dict__.items():

            if key.startswith("_"):
                continue

            if key in ignored:
                continue

            if isinstance(value, (str, int, float, bool)):
                attributes[key] = value

            elif value is None:
                attributes[key] = None

            elif isinstance(value, (list, tuple)):

                scalar_values = []

                for item in value:
                    if isinstance(
                        item,
                        (str, int, float, bool)
                    ):
                        scalar_values.append(item)

                if scalar_values:
                    attributes[key] = scalar_values

        if hasattr(node, "lineno"):
            attributes["line"] = node.lineno

        return attributes
