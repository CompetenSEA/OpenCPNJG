#!/usr/bin/env python3
"""Scan project licenses using scancode-toolkit and emit an SPDX summary."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict
import sys


def run_scancode(scan_path: Path) -> Dict:
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        cmd = [
            "scancode",
            "--quiet",
            "--json-pp",
            tmp.name,
            str(scan_path),
        ]
        subprocess.run(cmd, check=True)
        data = json.loads(Path(tmp.name).read_text())
    return data


def build_spdx(data: Dict) -> Dict:
    files = []
    unknown = []
    for entry in data.get("files", []):
        lic = entry.get("license_expression") or "NOASSERTION"
        path = entry.get("path")
        files.append({"fileName": path, "licenseConcluded": lic})
        if lic in {"unknown", "NOASSERTION"}:
            unknown.append(path)
    spdx = {
        "SPDXVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "files": files,
    }
    return spdx, unknown


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    parser.add_argument(
        "--output", type=Path, help="Write SPDX JSON to file instead of stdout"
    )
    args = parser.parse_args()

    data = run_scancode(Path(args.path))
    spdx, unknown = build_spdx(data)

    out = json.dumps(spdx, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(out)
    else:
        print(out)
    if unknown:
        for path in unknown:
            print(f"Unknown license for {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
