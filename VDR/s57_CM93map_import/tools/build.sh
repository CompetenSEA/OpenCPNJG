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
if [ -f ../../testdata/sample.000 ]; then
  ./ocpn_min --probe ../../testdata/sample.000
else
  echo "skipping probe: no sample.000" >&2
fi
