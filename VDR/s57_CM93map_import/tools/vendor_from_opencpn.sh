#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
OCPN=""
OUT="$ROOT_DIR/vendor/opencpn_subset/src"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ocpn) OCPN="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --commit) COMMIT="$2"; shift 2;;
    *) echo "Unknown option $1"; exit 1;;
  esac
done
if [[ -z "$OCPN" ]]; then
  for d in "$ROOT_DIR/../../OpenCPN" "$ROOT_DIR/../../opencpn"; do
    [[ -d "$d" ]] && OCPN="$d" && break
  done
fi
[[ -d "$OCPN" ]] || { echo "OpenCPN root not found"; exit 2; }

SEEDS=()
while IFS= read -r f; do SEEDS+=("$f"); done < <(find "$OCPN/libs/iso8211" -type f \( -name '*.c' -o -name '*.cpp' -o -name '*.h' \))
while IFS= read -r f; do SEEDS+=("$f"); done < <(find "$OCPN/gui/src" -type f -iname 'cm93*.*')
while IFS= read -r f; do SEEDS+=("$f"); done < <(find "$OCPN/gui/include" -type f -iname 'cm93*.*')
while IFS= read -r f; do SEEDS+=("$f"); done < <(find "$OCPN/gui/src" -type f -iname 's57*.*')
while IFS= read -r f; do SEEDS+=("$f"); done < <(find "$OCPN/gui/include" -type f -iname 's57*.*')
[[ ${#SEEDS[@]} -gt 0 ]] || { echo "No seeds found"; exit 3; }

python3 "$ROOT_DIR/tools/crawl_includes.py" --root "$OCPN" --seeds "${SEEDS[@]}" --out "$ROOT_DIR/vendor/vendor_filelist.cmake" > "$ROOT_DIR/vendor/crawl.log"

rm -rf "$OUT"
mkdir -p "$OUT"
while IFS= read -r rel; do
  src="$OCPN/$rel"
  if [[ ! -f "$src" ]]; then echo "missing $rel" >> "$ROOT_DIR/vendor/crawl.log"; continue; fi
  dst="$OUT/$rel"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  perl -0 -i -pe 's/#\s*include\s*[<"]wx\/[^>\"]+[>"]/#include "wx\/wx.h"/g' "$dst" || true
  perl -0 -i -pe 's/#\s*include\s*[<"]s52s57.h[>"]/#include "ocpn\/s52s57.h"/g' "$dst" || true
  perl -0 -i -pe 's/#\s*include\s*[<"]([A-Za-z0-9_\/]*glChartCanvas[^>\"]+)[>"]/#if 0\n#include "\1"\n#endif/g' "$dst" || true
  perl -0 -i -pe 's/#\s*include\s*[<"]([A-Za-z0-9_\/]*(Quilt|Osenc|Senc)[^>\"]+)[>"]/#if 0\n#include "\1"\n#endif/g' "$dst" || true
  if grep -qi 'gdal' "$dst"; then
    echo "GDAL reference in $rel" >> "$ROOT_DIR/docs/BUILD_NOTES.md"
  fi
done < "$ROOT_DIR/vendor/vendor_filelist.cmake"

SHA=$(git -C "$OCPN" rev-parse HEAD)
{
  echo "OpenCPN path: $OCPN"
  echo "Commit: $SHA"
  echo
  echo "| File | SHA256 |"
  echo "| --- | --- |"
} > "$ROOT_DIR/docs/PROVENANCE.md"
while IFS= read -r rel; do
  sha=$(sha256sum "$OCPN/$rel" | cut -d' ' -f1)
  echo "| $rel | $sha |" >> "$ROOT_DIR/docs/PROVENANCE.md"
done < "$ROOT_DIR/vendor/vendor_filelist.cmake"

python3 "$ROOT_DIR/tools/make_vendor_map.py" --src-root "$OUT" --out "$ROOT_DIR/docs/VENDOR_MAP.md"

count=$(wc -l < "$ROOT_DIR/vendor/vendor_filelist.cmake")
echo "Vendored $count files" >> "$ROOT_DIR/docs/BUILD_NOTES.md"
