"""CM93 portrayal rules for zoom bands and SCAMIN filtering."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
import yaml

_BASE = Path(__file__).resolve().parent

with open(_BASE / "config" / "portrayal" / "cm93_schemas.yml", "r", encoding="utf-8") as f:
    _SCHEMAS = yaml.safe_load(f)
with open(_BASE / "config" / "portrayal" / "scamin.yml", "r", encoding="utf-8") as f:
    _SCAMIN: Dict[str, Dict[str, int]] = yaml.safe_load(f)


def zoom_band_for(objl: str) -> str | None:
    """Return the name of the zoom band containing ``objl`` or ``None``."""
    for band in _SCHEMAS.get("bands", []):
        if objl in band.get("members", []):
            return band.get("name")
    return None


def apply_scamin(objl: str, z: int) -> bool:
    """Return ``True`` if object class ``objl`` should be shown at zoom ``z``."""
    rule: Dict[str, int] | None = _SCAMIN.get(objl)
    if not rule:
        return True
    return rule["zmin"] <= z <= rule["zmax"]
