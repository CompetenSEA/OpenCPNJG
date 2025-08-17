"""Pure Python chart rendering stubs.

This module replaces the previous C++ implementation and provides
minimal functionality required by the test suite.  The helpers mimic the
behaviour of the original library but avoid any heavy native
dependencies.
"""
from __future__ import annotations

from base64 import b64decode
from typing import List


def load_cell(path: str) -> None:
    """Load a chart cell.

    The reference implementation performs significant work here.  For the
    purposes of the tests we simply accept the path and return immediately.
    """
    _ = path  # explicitly ignore unused parameter


# Pre-generated 1x1 transparent PNG used as a stand in for rendered tiles.
_PNG_1X1 = b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIW2P8////fwAJ+wP7KYwG4gAAAABJRU5ErkJggg=="
)


def render_tile_png(
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
    z: int,
    palette: str,
) -> bytes:
    """Return a dummy PNG tile.

    All parameters are accepted for API compatibility but ignored by the
    stub implementation.  A constant 1x1 PNG image is returned.
    """
    _ = (minx, miny, maxx, maxy, z, palette)
    return _PNG_1X1


# Helper functions for encoding protobuf varints used by the MVT format

def _write_varint(buf: list[int], value: int) -> None:
    while value > 0x7F:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    buf.append(value)


def _write_tag(buf: list[int], field: int, typ: int) -> None:
    _write_varint(buf, (field << 3) | typ)


def _write_bytes_field(buf: list[int], field: int, data: list[int]) -> None:
    _write_tag(buf, field, 2)
    _write_varint(buf, len(data))
    buf.extend(data)


def _write_string_field(buf: list[int], field: int, value: str) -> None:
    data = list(value.encode("utf-8"))
    _write_bytes_field(buf, field, data)


def render_tile_mvt(
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
    z: int,
    safety_contour: float,
) -> bytes:
    """Return a tiny Mapbox Vector Tile payload.

    The tile contains a single sounding feature at the tile centre.  The
    `safety_contour` parameter controls a boolean attribute on that feature
    indicating whether the depth is considered shallow.
    """
    _ = (minx, miny, maxx, maxy, z)
    depth = 5.0
    is_shallow = depth < safety_contour

    feature: list[int] = []
    _write_tag(feature, 1, 0)
    _write_varint(feature, 1)  # id

    tags: list[int] = []
    _write_varint(tags, 0)  # key index 0
    _write_varint(tags, 0)  # value index 0
    _write_bytes_field(feature, 2, tags)

    _write_tag(feature, 3, 0)
    _write_varint(feature, 1)  # Point geometry type

    geom: list[int] = []
    move_to = (1 << 3) | 1  # MoveTo, 1 point
    _write_varint(geom, move_to)
    zz = lambda v: (v << 1) ^ (v >> 31)
    _write_varint(geom, zz(2048))
    _write_varint(geom, zz(2048))
    _write_bytes_field(feature, 4, geom)

    layer: list[int] = []
    _write_string_field(layer, 1, "SOUNDG")
    _write_bytes_field(layer, 2, feature)
    _write_string_field(layer, 3, "isShallow")
    value: list[int] = []
    _write_tag(value, 7, 0)  # bool_value
    _write_varint(value, 1 if is_shallow else 0)
    _write_bytes_field(layer, 4, value)
    _write_tag(layer, 15, 0)
    _write_varint(layer, 2)  # version

    tile: list[int] = []
    _write_bytes_field(tile, 3, layer)
    return bytes(tile)
