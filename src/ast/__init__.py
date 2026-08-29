"""
AST analysis package for Timing-RAG.

This package is intentionally independent of OpenSTA.

Pipeline:
    Verilog RTL
        ↓
    VerilogASTParser
        ↓
    Normalized AST
        ↓
    ASTGraphBuilder
        ↓
    NetworkX Graph

The mapper module provides lookup utilities that can later
connect timing/netlist information to RTL AST nodes.
"""

from .parser import VerilogASTParser
from .graph import ASTGraphBuilder
from .mapper import ASTMapper

__all__ = [
    "VerilogASTParser",
    "ASTGraphBuilder",
    "ASTMapper",
]
