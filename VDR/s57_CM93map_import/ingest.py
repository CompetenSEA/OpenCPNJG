"""Stub ingest script for s57 and CM93 charts using ocpn_min wrapper."""
import subprocess
import sys

def run_wrapper(mode, src):
    cmd = ["../../wrapper/build/ocpn_min", mode, "--src", src]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in proc.stdout:
        sys.stdout.write(line)
    proc.wait()
    return proc.returncode

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: ingest.py <s57|cm93> <src>")
        sys.exit(1)
    rc = run_wrapper(sys.argv[1], sys.argv[2])
    sys.exit(rc)
