from __future__ import annotations
import os, re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Minimal Entry protocol (as yielded by walk)
class _EntryProto:  # typed duck
    logical_path: str
    container_chain: List[str]
    kind: str
    size: int
    danger: Optional[str]

SEMANTIC_RE = re.compile(r"^(\d{6}),(\d{6}),([^,]+),([^.,]+)\.(\w+)$")

def _parse_semantic_name(name: str):
    m = SEMANTIC_RE.match(name)
    if not m:
        return None, None, None
    date, timestr, chan, imo, ext = m.groups()
    try:
        dt = datetime.strptime(date + timestr, "%y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        dt = None
    return dt, chan, ext.lower()

def classify(entries: List[_EntryProto], profile_id: str) -> Dict[str, Dict]:
    """Pure, side-effect-free classification based on vendor profile."""
    classified: Dict[str, Dict] = {}

    # gather tar headers (for content_hint) when needed
    tar_headers: Dict[str, List[str]] = defaultdict(list)
    if profile_id == "tar_series_by_channel":
        for e in entries:
            if e.container_chain and e.container_chain[-1].endswith(".tar"):
                tar_path = "/".join(e.container_chain)
                tar_headers[tar_path].append(e.logical_path)

    for e in entries:
        full_path = "/".join(e.container_chain + [e.logical_path]) if e.container_chain else e.logical_path
        parent = ("/".join(e.container_chain + [os.path.dirname(e.logical_path)]) if "/" in e.logical_path
                  else ("/".join(e.container_chain) if e.container_chain else None))
        rec = {
            "logical_path": full_path,
            "parent_logical": parent,
            "depth": len(e.container_chain) + (1 if e.logical_path else 0),
            "kind": e.kind,
            "size_bytes": e.size,
            "category": None,
            "time_hint_utc": None,
            "channel_label": None,
            "content_hint": None,
            "sha256": None,
            "danger": getattr(e, "danger", None),
        }

        ext = os.path.splitext(e.logical_path)[1].lower()

        if profile_id == "minute_zip_grid":
            if ext == ".txt":
                rec["category"] = "nmea_chunk"
            elif ext == ".wav":
                rec["category"] = "audio_channel"
            elif ext in {".png", ".bmp"}:
                rec["category"] = "radar_image"

        elif profile_id == "tar_series_by_channel":
            if e.kind == "tar":
                if e.logical_path.startswith("nmea/"):
                    rec["category"] = "nmea_chunk"
                elif e.logical_path.startswith("frame/"):
                    rec["category"] = "vendor_frame_tar"
                elif e.logical_path.startswith("voice/"):
                    rec["category"] = "audio_channel_container"
                if full_path in tar_headers:
                    rec["content_hint"] = ",".join(sorted(tar_headers[full_path])[:5])

        elif profile_id == "flat_semantic_names":
            base = os.path.basename(e.logical_path)
            dt, chan, extname = _parse_semantic_name(base)
            if dt:
                rec["time_hint_utc"] = dt
                rec["channel_label"] = chan
                if chan.startswith(("M", "V")):
                    rec["category"] = "audio_channel"
                elif chan == "R1":
                    rec["category"] = "radar_image"
                elif chan in {"DD", "SL"}:
                    rec["category"] = "vendor_log_text"

        else:
            # generic + heuristics
            base = os.path.basename(e.logical_path)
            if base.lower() == "alerthistory.log":
                rec["category"] = "conning_alert_log"
            elif base.startswith("Index."):
                rec["category"] = "vendor_index"

        classified[full_path] = rec

    return classified
