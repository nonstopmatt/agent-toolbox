#!/usr/bin/env bash
# Bring changes made to the GitHub repo (from another machine or a cloud session) into
# this toolbox and into the live skills, then rebuild. The reverse of sync.sh.
# Run it before sync.sh whenever the repo changed elsewhere: sync.sh copies the live
# skills over my-skills/, so without this step it would undo the remote edits.
#   --dry-run   show what would change, touch nothing
set -euo pipefail
TB="$(cd "$(dirname "$0")/.." && pwd)"
SK="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1

if (( DRY )); then
  git -C "$TB" fetch -q origin
  echo "== incoming commits"; git -C "$TB" log --oneline HEAD..@{u} || true
else
  git -C "$TB" pull -q --ff-only && echo "pulled: $(git -C "$TB" log -1 --format='%h %s')"
fi

BK="$HOME/.claude/backups/skills-$(date +%Y%m%d-%H%M%S)"
for d in "$TB"/my-skills/*/; do
  s="$(basename "$d")"
  # Only refresh skills that are already live. A new one waits for the user (bootstrap.sh adds them).
  [[ -d "$SK/$s" ]] || { echo "skip  $s (not live here)"; continue; }
  if diff -rq -x __pycache__ "$d" "$SK/$s" >/dev/null 2>&1; then
    echo "same  $s"; continue
  fi
  if (( DRY )); then echo "would update  $s"; continue; fi
  mkdir -p "$BK" && cp -R "$SK/$s" "$BK/$s"
  rsync -a --delete --exclude __pycache__ "$d" "$SK/$s/"
  echo "updated  $s"
done
[[ -d "$BK" ]] && echo "previous live copies kept in $BK"
(( DRY )) && exit 0

"$TB/bin/build-catalog.sh" >/dev/null && echo "catalog rebuilt"
python3 "$TB/bin/library.py" index | tail -1
