#!/usr/bin/env python3
"""
Shim module to make `import_enc` importable as a top-level module in CI and tests.

It re-exports everything from VDR/chart-tiler/tools/import_enc.py by temporarily
adding the chart-tiler folder to sys.path (the folder name contains a hyphen,
so it cannot be imported as a normal package).
"""
from __future__ import annotations
import sys
from pathlib import Path

# Add .../VDR/chart-tiler to sys.path so `from tools import import_enc` resolves
CHART_TILER_DIR = Path(__file__).resolve().parent / "chart-tiler"
if str(CHART_TILER_DIR) not in sys.path:
    sys.path.insert(0, str(CHART_TILER_DIR))

# Re-export public API
from tools.import_enc import *  # type: ignore  # noqa: F401,F403
