"""Simple ingestion helper for the ocpn_min wrapper.

The script executes the ultra‑mini OpenCPN wrapper and streams the emitted
NDJSON lines to stdout.  When ``--gzip`` is supplied the stream is transparently
decompressed before forwarding.  The function is intentionally small – the
calling process is responsible for piping the output to PostGIS or further
processing.
"""

from __future__ import annotations

import argparse
import gzip
import subprocess
import sys


def run_wrapper(args: argparse.Namespace) -> int:
    cmd = ["../../wrapper/build/ocpn_min", args.mode, "--src", args.src]
    if args.bbox:
        cmd += ["--bbox", args.bbox]
    if args.full_attrs:
        cmd.append("--full-attrs")
    if args.gzip:
        cmd.append("--gzip")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stream = gzip.GzipFile(fileobj=proc.stdout) if args.gzip else proc.stdout

    for raw in stream:
        # Forward lines to stdout; caller may capture and import to PostGIS.
        sys.stdout.buffer.write(raw)

    proc.wait()
    sys.stderr.buffer.write(proc.stderr.read())
    return proc.returncode


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run ocpn_min wrapper")
    p.add_argument("mode", choices=["s57", "cm93"], help="reader mode")
    p.add_argument("src", help="path to chart source")
    p.add_argument("--bbox", help="optional bbox minx,miny,maxx,maxy")
    p.add_argument("--full-attrs", action="store_true", help="emit full attribute list")
    p.add_argument("--gzip", action="store_true", help="wrapper emits gzip to stdout")
    return p.parse_args()


if __name__ == "__main__":
    ns = parse_cli()
    sys.exit(run_wrapper(ns))
