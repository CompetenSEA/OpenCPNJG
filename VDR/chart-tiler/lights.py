"""Helpers for CM93 light features."""

from __future__ import annotations

import math
from typing import Dict

import zlib
from shapely.geometry import Point, Polygon, MultiPolygon, LineString

# OpenCPN builds light sector arcs from attributes like SECTR1/SECTR2, VALNMR
# and COLOUR, defaulting to yellow 2.5 NM and marking leading sectors via
# CATLIT【F:docs/opencpn_cm93_notes.md†L11】
# Light description strings concatenate LITCHR, SIGGRP, colour initials and
# range/period information before display【F:docs/opencpn_cm93_notes.md†L12】

NM_TO_DEG = 1.0 / 60.0


def _arc(center: Point, radius_deg: float, start: float, end: float) -> Polygon:
    if start > end:
        end += 360.0
    step = 10.0
    coords = [(center.x, center.y)]
    angle = start
    while angle < end:
        rad = math.radians(angle)
        coords.append(
            (
                center.x + radius_deg * math.sin(rad),
                center.y + radius_deg * math.cos(rad),
            )
        )
        angle += step
    rad = math.radians(end)
    coords.append(
        (
            center.x + radius_deg * math.sin(rad),
            center.y + radius_deg * math.cos(rad),
        )
    )
    coords.append((center.x, center.y))
    return Polygon(coords)


def build_light_sectors(point: Point, attrs: Dict[str, float]) -> MultiPolygon | LineString:
    """Return sector geometry for a light.

    If SECTR1/SECTR2 are present a wedge is returned as ``MultiPolygon``;
    otherwise a simple range line is emitted.
    """

    r_nm = float(attrs.get("VALNMR", 2.5))
    radius_deg = r_nm * NM_TO_DEG
    sectr1 = attrs.get("SECTR1")
    sectr2 = attrs.get("SECTR2")

    if sectr1 is None or sectr2 is None:
        end = Point(
            point.x,
            point.y + radius_deg,
        )
        return LineString([point, end])

    poly = _arc(point, radius_deg, float(sectr1), float(sectr2))
    return MultiPolygon([poly])


def build_light_character(attrs: Dict[str, object]) -> int:
    """Create a dictionary coded light description.

    The resulting integer is a stable CRC32 of the composed string so that
    labels can use compact codes in the label plane.
    """

    parts: list[str] = []
    for key in ["LITCHR", "SIGGRP", "COLOUR", "SIGPER", "VALNMR"]:
        val = attrs.get(key)
        if val:
            if key == "COLOUR":
                parts.append(str(val)[0].upper())
            else:
                parts.append(str(val))
    if attrs.get("SECTR1") is not None and attrs.get("SECTR2") is not None:
        parts.append(f"{attrs['SECTR1']}-{attrs['SECTR2']}")

    text = " ".join(parts)
    return zlib.crc32(text.encode("utf-8")) & 0xFFFFFFFF


__all__ = ["build_light_sectors", "build_light_character"]

