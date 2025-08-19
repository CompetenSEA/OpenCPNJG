#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
python3 tools/vendor_opencpn.py --ocpn ../..
mkdir -p native/build
pushd native/build >/dev/null
cmake ..
make -j$(nproc) VERBOSE=1 | tee build.log
if grep ocpn_min build.log | grep -E 'ogr|wx|GL|Osenc'; then
  echo "forbidden symbols in link line" >&2; exit 1; fi
popd >/dev/null
BIN="$(pwd)/native/build/ocpn_min"
sample=$(find testdata -type f -name '*.000' | head -n1 || true)
if [ -n "$sample" ]; then
  "$BIN" dump-s57 --src "$sample" | head -n3
else
  echo "skipping dump-s57: no .000 files in testdata" >&2
fi

CM93_ROOT="$(cd "$SCRIPT_DIR/../testdata" && pwd)/cm93"
if [ -d "$CM93_ROOT" ]; then
  "$BIN" dump-cm93 --src "$CM93_ROOT" | head -n3
else
  echo "skipping dump-cm93: no dataset" >&2
fi
