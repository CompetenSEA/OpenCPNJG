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
  "$BIN" probe-iso8211 "$sample"
else
  echo "skipping probe: no .000 files in testdata" >&2
fi

# 2) Probe CM93 dataset if present
CM93_ROOT="$(cd "$SCRIPT_DIR/../testdata" && pwd)/cm93"
if [ -d "$CM93_ROOT" ]; then
  echo "==> Probing CM93 dataset at: $CM93_ROOT"
  set +e
  CM93_JSON="$("$BIN" probe-cm93 "$CM93_ROOT")"
  CM93_RC=$?
  set -e
  echo "$CM93_JSON"

  # simple smoke check: ok:true and cells_total > 0
  echo "$CM93_JSON" | grep -q '"ok":true' || { echo "CM93 probe failed (ok:false)"; exit $CM93_RC; }
  CELLS=$(echo "$CM93_JSON" | sed -n 's/.*"cells_total":\([0-9]\+\).*/\1/p')
  if [ -z "$CELLS" ] || [ "$CELLS" -le 0 ]; then
    echo "CM93 probe found zero cells"; exit 12
  fi
  echo "==> CM93 probe OK: $CELLS cells"
else
  echo "==> No CM93 dataset found at testdata/cm93 (skipping probe)"
fi
