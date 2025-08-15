from __future__ import annotations

"""Minimal S-52 Day palette pre-classification."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ContourConfig:
    safety: float = 10.0
    shallow: float = 5.0
    deep: float = 30.0
    hazardBuffer: float | None = None


class S52PreClassifier:
    """Apply a very small subset of S-52 conditional symbology rules."""

    def __init__(
        self,
        config: ContourConfig | float,
        colors: Dict[str, str],
        symbols: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        if isinstance(config, ContourConfig):
            self.cfg = config
        else:
            sc = float(config)
            self.cfg = ContourConfig(safety=sc, shallow=sc, deep=sc)
        self.colors = colors
        self.symbols = symbols or {}
        # Hooks for future use: lookups, priorities, etc.

    def classify(self, objl: str, props: Dict[str, Any]) -> Dict[str, Any]:
        """Return style helper attributes based on object and properties."""

        if objl == "DEPARE":
            d1 = props.get("DRVAL1")
            d2 = props.get("DRVAL2")
            values = [v for v in (d1, d2) if isinstance(v, (int, float))]
            min_val = min(values) if values else None
            max_val = max(values) if values else None
            is_shallow = (min_val is not None) and (min_val < self.cfg.safety)
            if is_shallow:
                token = "DEPVS" if "DEPVS" in self.colors else "DEPIT1"
            elif max_val is not None and max_val >= self.cfg.safety:
                token = "DEPDW"
            else:
                token = None
            if min_val is not None and min_val < self.cfg.shallow:
                band = "VS"
            elif max_val is not None and max_val >= self.cfg.deep:
                band = "DW"
            else:
                band = "IM"
            result: Dict[str, Any] = {"isShallow": is_shallow, "depthBand": band}
            if token:
                result["fillToken"] = token
            return result

        if objl == "DEPCNT":
            is_safety = float(props.get("VALDCO", -9999)) == self.cfg.safety
            is_low_acc = float(props.get("QUAPOS", 0)) >= 2
            role = "safety" if is_safety else "normal"
            return {"isSafety": is_safety, "isLowAcc": is_low_acc, "role": role}

        if objl == "SOUNDG":
            valsou = props.get("VALSOU")
            is_shallow = isinstance(valsou, (int, float)) and valsou < self.cfg.safety
            return {"isShallow": is_shallow}

        if objl in {"OBSTRN", "WRECKS", "UWTROC", "ROCKS"}:
            icon = self._hazard_icon(objl, props)
            if icon and (not self.symbols or icon in self.symbols):
                result: Dict[str, Any] = {"hazardIcon": icon}
                meta = self.symbols.get(icon) if self.symbols else None
                if meta and meta.get("anchor"):
                    w = meta.get("w", 0)
                    h = meta.get("h", 0)
                    ax, ay = meta["anchor"]
                    offx = int(round(w / 2 - ax))
                    offy = int(round(h / 2 - ay))
                    result["hazardOffX"] = offx
                    result["hazardOffY"] = offy
                return result
            return {}

        # LNDARE/COALNE and other objects use static styling
        return {}

    # ------------------------------------------------------------------
    def _hazard_icon(self, objl: str, props: Dict[str, Any]) -> Optional[str]:
        valsou = props.get("VALSOU")
        watlev = props.get("WATLEV")
        try:
            watlev_int = int(watlev)
        except (TypeError, ValueError):
            watlev_int = None
        shallow = isinstance(valsou, (int, float)) and valsou < self.cfg.safety
        drying = watlev_int in {1, 2}
        dangerous = shallow or drying
        if not dangerous:
            return None
        if objl == "WRECKS" and shallow:
            return "DANGER51"
        if objl == "ROCKS" and not drying:
            return "ROCKS01"
        return "ISODGR51"
