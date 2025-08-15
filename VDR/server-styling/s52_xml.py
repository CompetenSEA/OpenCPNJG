from __future__ import annotations

"""Helpers to parse small subsets of the S-52 ``chartsymbols.xml`` file."""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any

Element = ET.Element


def _int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_day_colors(root: Element) -> Dict[str, str]:
    """Return mapping of colour token -> ``#RRGGBB`` for the Day palette."""

    table = None
    for tbl in root.findall(".//color-table"):
        name = (tbl.get("name") or tbl.get("id") or "").upper()
        if name in {"DAY_BRIGHT", "DAY"}:
            table = tbl
            break
    if table is None:
        raise ValueError("DAY_BRIGHT colour table not found")

    colours: Dict[str, str] = {}
    for elem in table.findall("color"):
        token = elem.get("name") or elem.get("token")
        r = elem.get("r") or elem.get("red")
        g = elem.get("g") or elem.get("green")
        b = elem.get("b") or elem.get("blue")
        if token and r and g and b:
            try:
                colours[token] = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            except ValueError:
                continue
    return colours


def parse_symbols(root: Element) -> Dict[str, Dict[str, Any]]:
    """Return mapping of symbol name -> metadata for bitmap symbols."""

    symbols: Dict[str, Dict[str, Any]] = {}
    for sym in root.findall(".//symbols/symbol"):
        name = sym.get("name") or sym.get("id")
        if not name:
            name_elem = sym.find("name")
            if name_elem is not None:
                name = name_elem.text or ""
        if not name:
            continue

        bitmap = sym.find("bitmap")
        if bitmap is None:
            continue
        w = _int(bitmap.get("width")) or 0
        h = _int(bitmap.get("height")) or 0
        gl = bitmap.find("graphics-location")
        x = _int(gl.get("x")) if gl is not None else _int(bitmap.get("x")) or 0
        y = _int(gl.get("y")) if gl is not None else _int(bitmap.get("y")) or 0

        entry: Dict[str, Any] = {"w": w, "h": h, "x": x, "y": y}

        hotspot = sym.find("hotspot") or sym.find("pivot")
        if hotspot is not None:
            ax = _int(hotspot.get("x"))
            ay = _int(hotspot.get("y"))
            if ax is not None and ay is not None:
                entry["anchor"] = (ax, ay)

        rot = sym.get("rotatable") or sym.get("rotate")
        if rot is not None:
            entry["rotate"] = str(rot).lower() in {"1", "true", "yes"}

        symbols[name] = entry
    return symbols


def _norm_pattern(pattern: str | None) -> str:
    if not pattern:
        return "solid"
    p = pattern.lower()
    if "dash" in p and "dot" in p:
        return "dashdot"
    if "dash" in p:
        return "dash"
    if "dot" in p:
        return "dot"
    return "solid"


def parse_linestyles(root: Element) -> Dict[str, Dict[str, Any]]:
    """Return mapping of line style name -> metadata."""

    styles: Dict[str, Dict[str, Any]] = {}
    for ls in root.findall(".//line-styles/line-style"):
        name = ls.get("name") or ls.get("id")
        if not name:
            name = ls.findtext("name")
        if not name:
            continue
        color = ls.get("color-ref") or ls.get("colour-ref") or ls.get("color")
        if color is None:
            color = ls.findtext("color-ref") or ls.findtext("colour-ref")
        width_val = ls.get("width") or ls.get("thickness")
        try:
            width = float(width_val) if width_val is not None else 1.0
        except ValueError:
            width = 1.0
        pattern = _norm_pattern(ls.get("pattern"))
        styles[name] = {"color-token": color, "width": width, "pattern": pattern}
    return styles


def parse_patterns(root: Element) -> Dict[str, Dict[str, Any]]:
    """Return mapping of pattern name -> metadata for bitmap or vector patterns."""

    patterns: Dict[str, Dict[str, Any]] = {}
    for pat in root.findall(".//patterns/pattern"):
        name = pat.get("name") or pat.get("id") or pat.findtext("name")
        if not name:
            continue
        bitmap = pat.find("bitmap")
        if bitmap is not None:
            w = _int(bitmap.get("width")) or 0
            h = _int(bitmap.get("height")) or 0
            gl = bitmap.find("graphics-location")
            x = _int(gl.get("x")) if gl is not None else _int(bitmap.get("x")) or 0
            y = _int(gl.get("y")) if gl is not None else _int(bitmap.get("y")) or 0
            patterns[name] = {"type": "bitmap", "w": w, "h": h, "x": x, "y": y}
        else:
            patterns[name] = {"type": "vector"}
    return patterns


def parse_lookups(root: Element) -> List[Dict[str, Any]]:
    """Return list of lookup dictionaries."""

    lookups: List[Dict[str, Any]] = []
    for lu in root.findall(".//lookups/lookup"):
        obj = lu.get("name") or lu.get("object") or lu.get("id")
        if not obj:
            obj_elem = lu.find("object") or lu.find("name")
            if obj_elem is not None:
                obj = obj_elem.text or ""
        objl = (obj or "").strip().upper()
        if not objl:
            continue
        table = lu.findtext("table-name", default="")
        disp = lu.findtext("disp-prio", default="")
        instr = lu.findtext("instruction", default="")
        lookups.append({"objl": objl, "table": table, "disp_prio": disp, "instruction": instr})
    return lookups


__all__ = [
    "parse_day_colors",
    "parse_symbols",
    "parse_linestyles",
    "parse_patterns",
    "parse_lookups",
]
