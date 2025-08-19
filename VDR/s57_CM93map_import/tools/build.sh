#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../native"
build_dir=build
rm -rf "$build_dir"
# acceptance: cap number of vendored files
count=$(find ../vendor/opencpn_subset -type f | wc -l)
if [ "$count" -gt 100 ]; then
  echo "Too many vendored files: $count" >&2
  exit 1
fi
# forbidden include scan
if rg "wx/|OpenGL|s52plib|Osenc|Quilt" ../vendor/opencpn_subset >/dev/null; then
  echo "Forbidden include detected" >&2
  exit 1
fi
cmake -S . -B "$build_dir"
cmake --build "$build_dir"
"$build_dir/ocpn_min" --help
