from __future__ import annotations

"""Very small raster tile renderer used for tests.

The renderer only understands DEPARE polygons and DEPCNT lines.  It relies on
Pillow when available; if the dependency is missing a ``RasterMVPUnavailable``
exception is raised so callers can gracefully fall back to the placeholder
image.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import io

try:  # pragma: no cover - optional dependency
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore


class RasterMVPUnavailable(RuntimeError):
    pass


@dataclass
class _Bbox:
    left: float
    bottom: float
    right: float
    top: float


def _tile_bbox(z: int, x: int, y: int) -> _Bbox:
    import math

    n = 2.0 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi - 2.0 * math.pi * y / n)))
    lat_bottom = math.degrees(
        math.atan(math.sinh(math.pi - 2.0 * math.pi * (y + 1) / n))
    )
    return _Bbox(lon_left, lat_bottom, lon_right, lat_top)


def _to_px(bbox: _Bbox, lon: float, lat: float) -> tuple[float, float]:
    x = (lon - bbox.left) / (bbox.right - bbox.left) * 256.0
    y = (bbox.top - lat) / (bbox.top - bbox.bottom) * 256.0
    return x, y


def _hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return r, g, b, 255


def render_tile(z: int, x: int, y: int, features: List[Dict[str, Any]], colors: Dict[str, str]) -> bytes:
    if Image is None or ImageDraw is None:
        raise RasterMVPUnavailable("Pillow not installed")

    bbox = _tile_bbox(z, x, y)
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def draw_polygon(geom: Dict[str, Any], color: str) -> None:
        coords = []
        for lon, lat in geom.get("coordinates", [])[0]:
            coords.append(_to_px(bbox, lon, lat))
        if coords:
            draw.polygon(coords, fill=_hex_to_rgba(color))

    def draw_line(geom: Dict[str, Any], color: str, width: int = 1, dash: bool = False) -> None:
        pts = [_to_px(bbox, lon, lat) for lon, lat in geom.get("coordinates", [])]
        draw.line(pts, fill=_hex_to_rgba(color), width=width)

    for feat in features:
        props = feat.get("properties", {})
        objl = props.get("OBJL")
        geom = feat.get("geometry", {})
        if objl == "DEPARE":
            token = props.get("fillToken")
            if token and token in colors:
                draw_polygon(geom, colors[token])
        elif objl == "DEPCNT":
            width = 1
            color = colors.get("DEPCN", "#000000")
            dash = False
            if props.get("role") == "safety":
                color = colors.get("DEPSC", color)
                width = 2
            if props.get("isLowAcc"):
                dash = True
            draw_line(geom, color, width=width, dash=dash)

    out = Image.new("RGBA", img.size)
    out.paste(img, (0, 0))
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()
