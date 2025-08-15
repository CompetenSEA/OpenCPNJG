from __future__ import annotations

"""Minimal S-52 Day palette pre-classification."""

from typing import Dict, Any


class S52PreClassifier:
    """Apply a very small subset of S-52 conditional symbology rules."""

    def __init__(self, chartsymbols_xml: str, sc: float, colors: Dict[str, str]):
        self.sc = float(sc)
        self.colors = colors
        self.chartsymbols_xml = chartsymbols_xml
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
                return {"fillToken": token, "isShallow": True}
            max_val = max(values) if values else -9999
            if max_val >= self.sc:
                return {"fillToken": "DEPDW", "isShallow": False}
            return {"isShallow": False}

        if objl == "DEPCNT":
            is_safety = float(props.get("VALDCO", -9999)) == self.sc
            is_low_acc = float(props.get("QUAPOS", 0)) >= 2
            return {"isSafety": is_safety, "isLowAcc": is_low_acc}

        if objl == "SOUNDG":
            valsou = props.get("VALSOU")
            is_shallow = isinstance(valsou, (int, float)) and valsou < self.sc
            return {"isShallow": is_shallow}

        # LNDARE/COALNE and other objects use static styling
        return {}
