#!/usr/bin/env bash
# Validate the exact repository snapshot that users receive from Git.
# Pass an exported index directory to reuse one prepared by bin/sync.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWN_SNAPSHOT=0

if [[ $# -gt 1 ]]; then
  echo "usage: $0 [exported-index-directory]" >&2
  exit 2
fi

if [[ $# -eq 1 ]]; then
  SNAP="$1"
  [[ -d "$SNAP" ]] || { echo "snapshot directory not found: $SNAP" >&2; exit 2; }
else
  SNAP="$(mktemp -d)"
  OWN_SNAPSHOT=1
  git -C "$ROOT" checkout-index -a --prefix="$SNAP/"
fi

cleanup() {
  if (( OWN_SNAPSHOT )); then
    rm -rf "$SNAP"
  fi
}
trap cleanup EXIT

python_count=0
while IFS= read -r -d '' file; do
  python3 -c 'import pathlib, sys; p = pathlib.Path(sys.argv[1]); compile(p.read_bytes(), str(p), "exec")' "$file"
  python_count=$((python_count + 1))
done < <(find "$SNAP" -type f -name '*.py' -print0)

shell_count=0
while IFS= read -r -d '' file; do
  bash -n "$file"
  shell_count=$((shell_count + 1))
done < <(find "$SNAP" -type f -name '*.sh' -print0)

json_count=0
while IFS= read -r -d '' file; do
  python3 -m json.tool "$file" >/dev/null
  json_count=$((json_count + 1))
done < <(find "$SNAP" -type f -name '*.json' -print0)

echo "published snapshot valid: ${python_count} Python, ${shell_count} shell, ${json_count} JSON files"
