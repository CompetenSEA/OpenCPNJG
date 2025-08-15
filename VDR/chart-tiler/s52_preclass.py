from __future__ import annotations

"""Minimal S-52 Day palette pre-classification."""

from typing import Dict, Any, Optional


class S52PreClassifier:
    """Apply a very small subset of S-52 conditional symbology rules."""

    def __init__(
        self,
        sc: float,
        colors: Dict[str, str],
        symbols: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.sc = float(sc)
        self.colors = colors
        self.symbols = symbols or {}
        # Hooks for future use: lookups, priorities, etc.

    def classify(self, objl: str, props: Dict[str, Any]) -> Dict[str, Any]:
        """Return style helper attributes based on object and properties."""

        if objl == "DEPARE":
            d1 = props.get("DRVAL1")
            d2 = props.get("DRVAL2")
            values = [v for v in (d1, d2) if isinstance(v, (int, float))]
            is_shallow = min(values) < self.sc if values else False
            if is_shallow:
                token = "DEPVS" if "DEPVS" in self.colors else "DEPIT1"
                return {"fillToken": token, "isShallow": True, "depthBand": "VS"}
            max_val = max(values) if values else -9999
            if max_val >= self.sc:
                return {"fillToken": "DEPDW", "isShallow": False, "depthBand": "DW"}
            return {"isShallow": False, "depthBand": "DW"}

        if objl == "DEPCNT":
            is_safety = float(props.get("VALDCO", -9999)) == self.sc
            is_low_acc = float(props.get("QUAPOS", 0)) >= 2
            role = "safety" if is_safety else "normal"
            return {"isSafety": is_safety, "isLowAcc": is_low_acc, "role": role}

        if objl == "SOUNDG":
            valsou = props.get("VALSOU")
            is_shallow = isinstance(valsou, (int, float)) and valsou < self.sc
            return {"isShallow": is_shallow}

        if objl in {"OBSTRN", "WRECKS", "UWTROC", "ROCKS"}:
            icon = self._hazard_icon(objl, props)
            if icon and (not self.symbols or icon in self.symbols):
                return {"hazardIcon": icon}
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
        shallow = isinstance(valsou, (int, float)) and valsou < self.sc
        drying = watlev_int in {1, 2}
        dangerous = shallow or drying
        if not dangerous:
            return None
        if objl == "WRECKS" and shallow:
            return "DANGER51"
        if objl == "ROCKS" and not drying:
            return "ROCKS01"
        return "ISODGR51"
