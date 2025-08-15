"""Python bindings for chart generation.

The real project ships a compiled extension exposing functions from
`libcharts`.  For the purposes of testing in this repository we provide
light‑weight Python fallbacks when the extension is not available.
"""
from base64 import b64decode

try:  # pragma: no cover - exercised when extension is present
    from ._core import (
        load_cell,
        generate_tile,
        get_object_classes,
        get_attribute_classes,
        get_chart_metadata,
    )
except Exception:  # pragma: no cover - used in CI
    def load_cell(path: str) -> None:
        """Placeholder implementation that accepts a file path."""
        return None

    _PNG_1x1 = b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIW2P8////fwAJ+wP7KYwG4gAAAABJRU5ErkJggg=="
    )

    def generate_tile(bbox, z, fmt: str = "png", palette: str = "day") -> bytes:
        """Return a dummy PNG or a tiny MVT payload.

        Parameters mirror the compiled extension but the implementation only
        returns static bytes suitable for unit tests.
        """
        if fmt == "png":
            return _PNG_1x1
        return b"MVT"

    def get_object_classes():
        """Return a sample set of object classes."""
        return [(1, "BOYSPP", "Buoy Special Purpose")]

    def get_attribute_classes():
        """Return a sample set of attribute classes."""
        return [(1, "COLPAT", "Colour Pattern")]

    def get_chart_metadata():
        """Return placeholder chart metadata."""
        return [("edition", "2023")]

__all__ = [
    "load_cell",
    "generate_tile",
    "get_object_classes",
    "get_attribute_classes",
    "get_chart_metadata",
]
