from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

_PROFILES_PATH = Path(__file__).with_name("profiles.yaml")

def _load_profile_ids() -> List[str]:
    if yaml is None:
        return []
    try:
        with _PROFILES_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return []
    profs = data.get("profiles", []) or []
    return [p.get("id") for p in profs if isinstance(p, dict) and p.get("id")]

def detect_profile(upload_path: str, *, signals=None, entries=None) -> Dict[str, Any]:
    if signals is None:
        signals = {}
    if entries is None:
        entries = []
    profiles = set(_load_profile_ids())
    vendor = "generic"
    if signals.get("flat", {}).get("semantic_comma_names") and (
        "flat_semantic_names" in profiles or not profiles
    ):
        vendor = "flat_semantic_names" if "flat_semantic_names" in profiles else "generic"
    elif signals.get("packaging", {}).get("minute_zip_grid") and (
        "minute_zip_grid" in profiles or not profiles
    ):
        vendor = "minute_zip_grid" if "minute_zip_grid" in profiles else "generic"
    elif "generic_fallback" in profiles:
        vendor = "generic_fallback"
    return {"vendor": vendor, "signals": signals, "entries": entries}

def classify_entries(entries: List[Any], vendor: str) -> Dict[str, Any]:
    from ingest_pkg.classifier import classify  # lazy to avoid circular import
    if entries is None or vendor is None:
        raise ValueError("entries and vendor required")
    return classify(entries, vendor)
