#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.."; pwd)"
SRC="${REPO_ROOT}/data/s57data"
DEST="${REPO_ROOT}/VDR/server-styling/dist/assets/s52"
LOCK="${REPO_ROOT}/VDR/server-styling/opencpn-assets.lock"

# required files (explicit, no wildcards)
REQ=(chartsymbols.xml rastersymbols-day.png S52RAZDS.RLE s57objectclasses.csv s57attributes.csv attdecode.csv)

for f in "${REQ[@]}"; do
  if [[ ! -f "${SRC}/${f}" ]]; then
    echo "missing ${SRC}/${f}" >&2; exit 2
  fi
done

# verify checksums against lock file manifest
declare -A LOCKSUM
if [[ ! -f "${LOCK}" ]]; then
  echo "missing lock file ${LOCK}" >&2; exit 3
fi
in_manifest=0
while IFS='=' read -r key val; do
  [[ -z "${key}" ]] && continue
  if [[ "${key}" == "[manifest]" ]]; then
    in_manifest=1
    continue
  fi
  if [[ ${in_manifest} -eq 1 ]]; then
    LOCKSUM["${key}"]="${val}"
  fi
done < "${LOCK}"

for f in "${REQ[@]}"; do
  if [[ -z "${LOCKSUM[${f}]:-}" ]]; then
    echo "no checksum for ${f} in lock file" >&2; exit 4
  fi
  sum=$(sha256sum "${SRC}/${f}" | awk '{print $1}')
  if [[ "${sum}" != "${LOCKSUM[${f}]}" ]]; then
    echo "checksum mismatch for ${f}" >&2; exit 5
  fi
done

mkdir -p "${DEST}"
python "${REPO_ROOT}/VDR/server-styling/tools/stage_local_assets.py" \
  --repo-data "${SRC}" \
  --dest "${DEST}" \
  --force

echo "Staged S-52/S-57 assets to ${DEST}"
