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
        # State to track safety contour when exact match missing
        self._nearest_cnt: Optional[tuple[float, Dict[str, Any]]] = None
        self._has_exact_safety = False

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
            depth = float(props.get("VALDCO", -9999))
            is_safety = depth == self.cfg.safety
            is_low_acc = float(props.get("QUAPOS", 0)) >= 2
            role = "safety" if is_safety else "normal"
            result = {"isSafety": is_safety, "isLowAcc": is_low_acc, "role": role}
            diff = abs(depth - self.cfg.safety)
            if is_safety:
                self._has_exact_safety = True
            else:
                if self._nearest_cnt is None or diff < self._nearest_cnt[0]:
                    self._nearest_cnt = (diff, result)
            return result

        if objl == "SOUNDG":
            valsou = props.get("VALSOU")
            is_shallow = isinstance(valsou, (int, float)) and valsou < self.cfg.safety
            return {"isShallow": is_shallow}

        if objl in {"OBSTRN", "WRECKS", "UWTROC", "ROCKS"}:
            icon = self._hazard_icon(objl, props)
            if icon and (not self.symbols or icon in self.symbols):
                result: Dict[str, Any] = {"hazardIcon": icon}
                if self.cfg.hazardBuffer is not None:
                    result["hazardBuffer"] = self.cfg.hazardBuffer
                meta = self.symbols.get(icon) if self.symbols else None
                if meta and meta.get("anchor"):
                    w = meta.get("w", 0)
                    h = meta.get("h", 0)
                    ax, ay = meta["anchor"]
                    offx = int(round(w / 2 - ax))
                    offy = int(round(h / 2 - ay))
                    result["hazardOffX"] = offx
                    result["hazardOffY"] = offy
                watlev = props.get("WATLEV")
                if watlev is not None:
                    try:
                        result["hazardWatlev"] = int(watlev)
                    except (TypeError, ValueError):
                        pass
                return result
            return {}

        if objl.startswith("BCN") or objl.startswith("BOY"):
            # determine category attribute CAT*
            cat_val = None
            for k, v in props.items():
                if k.startswith("CAT"):
                    cat_val = v
                    break
            icon = f"{objl}_{cat_val}" if cat_val is not None else objl
            result: Dict[str, Any] = {"navaidIcon": icon}
            orient = props.get("ORIENT")
            if isinstance(orient, (int, float)):
                result["orient"] = float(orient)
            name = props.get("OBJNAM") or props.get("NOBJNM")
            if name:
                result["name"] = name
            return result

        if objl in {"CBLARE", "PIPARE"}:
            pattern = props.get("lnstl") or props.get("LSTYLE")
            if pattern in {"dash", "dot", "dashdot"}:
                return {"linePattern": pattern}
            return {}

        # LNDARE/COALNE and other objects use static styling
        return {}

    def finalize(self) -> None:
        """Apply post-processing once all features have been classified."""

        if self._has_exact_safety or not self._nearest_cnt:
            return
        _, result = self._nearest_cnt
        result["isSafety"] = True
        result["role"] = "safety"

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
