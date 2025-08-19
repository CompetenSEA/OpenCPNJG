#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
OCPN=${1:-}
if [[ -z "$OCPN" ]]; then
  for d in "$ROOT_DIR/../../OpenCPN" "$ROOT_DIR/../../opencpn"; do
    [[ -d "$d" ]] && OCPN="$d" && break
  done
fi
[[ -d "$OCPN" ]] || { echo "OpenCPN root not found"; exit 2; }

"$ROOT_DIR/tools/vendor_from_opencpn.sh" --ocpn "$OCPN"

mkdir -p "$ROOT_DIR/native/build" && cd "$ROOT_DIR/native/build"
cmake ..
cmake --build . -j

./ocpn_min || { echo "ocpn_min failed"; exit 1; }
