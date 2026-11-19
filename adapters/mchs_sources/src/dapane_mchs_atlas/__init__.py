"""Opt-in MCHS/Atlas exact transport; the existing Rust kernel owns valuation."""

from ._validation import AdapterError, loads
from .adapter import evaluate, prepare

__all__ = ["AdapterError", "evaluate", "loads", "prepare"]
__version__ = "0.1.0"
