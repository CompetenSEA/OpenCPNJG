#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.."; pwd)"
SRC="${REPO_ROOT}/data/s57data"
DEST="${REPO_ROOT}/VDR/server-styling/dist/assets/s52"

# required files (explicit, no wildcards)
REQ=(chartsymbols.xml rastersymbols-day.png S52RAZDS.RLE s57objectclasses.csv s57attributes.csv attdecode.csv)

for f in "${REQ[@]}"; do
  if [[ ! -f "${SRC}/${f}" ]]; then
    echo "missing ${SRC}/${f}" >&2; exit 2
  fi
done

mkdir -p "${DEST}"
python "${REPO_ROOT}/VDR/server-styling/tools/stage_local_assets.py" \
  --repo-data "${SRC}" \
  --dest "${DEST}" \
  --force

echo "Staged S-52/S-57 assets to ${DEST}"
