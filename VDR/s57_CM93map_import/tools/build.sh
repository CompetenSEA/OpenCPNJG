#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/vendor_opencpn.py --ocpn ../..
mkdir -p native/build && cd native/build
cmake ..
make -j$(nproc) VERBOSE=1 | tee build.log
if grep ocpn_min build.log | grep -E 'ogr|wx|GL|Osenc'; then
  echo "forbidden symbols in link line" >&2; exit 1; fi
./ocpn_min --help
sample=$(find ../../testdata -type f -name '*.000' | head -n1 || true)
if [ -n "$sample" ]; then
  ./ocpn_min --probe "$sample"
else
  echo "skipping probe: no .000 files in testdata" >&2
fi
