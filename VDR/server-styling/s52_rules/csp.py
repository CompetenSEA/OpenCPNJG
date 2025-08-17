"""Helpers for decoding S-52 conditional symbology tokens."""
from __future__ import annotations
import re
from typing import List, Optional

def decode(token: str) -> Optional[List[object]]:
    """Translate a CSP ``attrib-code`` token into a MapLibre filter expression.

    Examples
    --------
    >>> decode("QUAPOS01")
    ['==', ['get', 'QUAPOS'], 1]
    >>> decode("WATLEV4NATSUR11")
    ['all', ['==', ['get', 'WATLEV'], 4], ['==', ['get', 'NATSUR'], 11]]
    """
    if not token:
        return None
    token = token.strip().upper()
    parts = re.findall(r"([A-Z]+)(\d+)", token)
    if not parts:
        return None
    filters: List[List[object]] = []
    for attr, val in parts:
        try:
            num = int(val)
        except ValueError:
            continue
        filters.append(["==", ["get", attr], num])
    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return ["all", *filters]

__all__ = ["decode"]
