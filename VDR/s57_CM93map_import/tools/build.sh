#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/vendor_opencpn.py --ocpn ../../
mkdir -p native/build && cd native/build
cmake .. && make -j$(nproc)
./ocpn_min
