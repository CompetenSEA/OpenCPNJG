#!/usr/bin/env bash
# Stage runtime assets for production:
#  - OpenCPN S-52/S-57 files from repo-root data/s57data (or fallback to /VDR/BAUV/data/s57data)
#  - BAUV viewer public resources and fonts from /VDR/BAUV/src/tileserver/**
#  - Write a SHA-256 manifest at VDR/staged_assets_manifest.json
#
# USAGE:
#   bash VDR/scripts/stage_assets_all.sh [--dry-run] [--force]
#
# ENV (optional):
#   S57_ASSETS_DIR=/abs/path/to/data/s57data  # overrides default detection

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.."; pwd)"       # .../VDR
TOP_ROOT="$(cd "${REPO_ROOT}/.."; pwd)"           # repo root (contains VDR/ and data/)
BAUV_DIR="${REPO_ROOT}/BAUV"                      # /VDR/BAUV mirror of BAUV-Maps
DEFAULT_S57_DIR="${TOP_ROOT}/data/s57data"        # OpenCPN assets
S57_DIR="${S57_ASSETS_DIR:-${DEFAULT_S57_DIR}}"
ALLOWLIST="${REPO_ROOT}/tools/allowlist.txt"

DEST_BASE="${REPO_ROOT}"
STYLING="${DEST_BASE}/server-styling/dist"
S52_DEST="${STYLING}/assets/s52"
FONTS_DEST="${STYLING}/fonts/bauv"
PUBLIC_DEST="${STYLING}/public/resources"
MANIFEST="${DEST_BASE}/staged_assets_manifest.json"

DRY=0
FORCE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1;;
    --force)   FORCE=1;;
    -h|--help) echo "Usage: $0 [--dry-run] [--force]"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
  shift
done

say(){ echo "==> $*"; }
do_cmd(){ if [[ $DRY -eq 1 ]]; then echo "[dry-run] $*"; else eval "$@"; fi; }

host_allowed(){
  local url="$1"
  local host
  host=$(python - <<'PY'
from urllib.parse import urlparse
import sys
print(urlparse(sys.argv[1]).hostname or '')
PY
"$url")
  grep -Fxq "$host" "$ALLOWLIST" || {
    echo "Host '$host' not in allowlist" >&2
    exit 5
  }
}

if [[ -d "${BAUV_DIR}/.git" ]]; then
  url=$(git -C "${BAUV_DIR}" config --get remote.origin.url 2>/dev/null || true)
  [[ -n "$url" ]] && host_allowed "$url"
fi

# --- 1) Stage S-52/S-57 core
if [[ ! -f "${S57_DIR}/chartsymbols.xml" && -f "${BAUV_DIR}/data/s57data/chartsymbols.xml" ]]; then
  S57_DIR="${BAUV_DIR}/data/s57data"
fi
if [[ ! -f "${S57_DIR}/chartsymbols.xml" ]]; then
  echo "ERROR: chartsymbols.xml not found in ${DEFAULT_S57_DIR} or ${BAUV_DIR}/data/s57data" >&2
  exit 3
fi

REQ=(chartsymbols.xml rastersymbols-day.png S52RAZDS.RLE s57objectclasses.csv s57attributes.csv attdecode.csv)
for f in "${REQ[@]}"; do
  if [[ ! -f "${S57_DIR}/${f}" ]]; then
    echo "missing ${S57_DIR}/${f}" >&2; exit 4
  fi
done

say "Staging OpenCPN S-52/S-57 from: ${S57_DIR}"
mkdir -p "${S52_DEST}"
PY="${DEST_BASE}/server-styling/tools/stage_local_assets.py"
CMD="python '${PY}' --repo-data '${S57_DIR}' --dest '${S52_DEST}'"
[[ $FORCE -eq 1 ]] && CMD="${CMD} --force"
do_cmd "${CMD}"

# Optional extras
for extra in rastersymbols-dusk.png rastersymbols-dark.png; do
  if [[ -f "${S57_DIR}/${extra}" ]]; then
    say "Copy extra: ${extra}"
    do_cmd "cp -p '${S57_DIR}/${extra}' '${S52_DEST}/${extra}'"
  fi
done

# --- 2) Stage BAUV fonts (.ttf)
FONTS_SRC="${BAUV_DIR}/src/tileserver/fonts"
if [[ -d "${FONTS_SRC}" ]]; then
  say "Staging BAUV fonts from: ${FONTS_SRC}"
  do_cmd "mkdir -p '${FONTS_DEST}'"
  if command -v rsync >/dev/null 2>&1; then
    RSYNC="rsync -a --include='*/' --include='*.ttf' --exclude='*' '${FONTS_SRC}/' '${FONTS_DEST}/'"
    [[ $DRY -eq 1 ]] && RSYNC="${RSYNC} --dry-run --info=NAME"
    do_cmd "${RSYNC}"
  else
    if [[ $DRY -eq 1 ]]; then
      find "${FONTS_SRC}" -type f -name '*.ttf' -print
    else
      while IFS= read -r -d '' f; do
        rel="${f#"${FONTS_SRC}/"}"
        dst="${FONTS_DEST}/${rel}"
        mkdir -p "$(dirname "${dst}")"
        cp -p "${f}" "${dst}"
      done < <(find "${FONTS_SRC}" -type f -name '*.ttf' -print0)
    fi
  fi
else
  say "No BAUV fonts at ${FONTS_SRC}; skipping."
fi

# --- 3) Stage BAUV viewer public resources
RES_SRC="${BAUV_DIR}/src/tileserver/public/resources"
if [[ -d "${RES_SRC}" ]]; then
  say "Staging BAUV public resources from: ${RES_SRC}"
  do_cmd "mkdir -p '${PUBLIC_DEST}'"
  if command -v rsync >/dev/null 2>&1; then
    RSYNC="rsync -a '${RES_SRC}/' '${PUBLIC_DEST}/'"
    [[ $DRY -eq 1 ]] && RSYNC="${RSYNC} --dry-run --info=NAME"
    do_cmd "${RSYNC}"
  else
    if [[ $DRY -eq 1 ]]; then
      find "${RES_SRC}" -type f -print
    else
      (cd "${RES_SRC}" && tar cf - .) | (cd "${PUBLIC_DEST}" && tar xpf -)
    fi
  fi
else
  say "No BAUV public resources at ${RES_SRC}; skipping."
fi

# --- 4) Write manifest
say "Writing manifest: ${MANIFEST}"
if [[ $DRY -eq 1 ]]; then
  echo "[dry-run] generate manifest"
else
  python - "${MANIFEST}" "${STYLING}" <<'PY'
import hashlib, json, os, sys
man, root = sys.argv[1], sys.argv[2]
items = []
for r, _, files in os.walk(root):
  for n in files:
    p = os.path.join(r, n)
    h = hashlib.sha256()
    with open(p, 'rb') as f:
      for chunk in iter(lambda: f.read(8192), b''):
        h.update(chunk)
    items.append({"path": os.path.relpath(p, os.path.dirname(root)), "sha256": h.hexdigest()})
with open(man, 'w', encoding='utf-8') as fh:
  json.dump({"count": len(items), "files": items}, fh, indent=2, sort_keys=True)
print(f"Manifest wrote {len(items)} files -> {man}")
PY
fi

say "Staging complete. You can now remove /VDR/BAUV if desired."
