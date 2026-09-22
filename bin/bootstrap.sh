#!/usr/bin/env bash
# Disaster recovery: rebuild a toolbox on a fresh machine from this repo.
#   bootstrap.sh [TARGET] [SKILLS_DIR]      defaults: ~/toolbox  ~/.claude/skills
# Clones this repo into TARGET (unless it already is one), re-clones every upstream in
# manifest.json at its pinned commit, rebuilds the catalog, installs my own skills
# (never overwriting one that exists) and lists the MCP templates that need credentials.
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
T="${1:-$HOME/toolbox}"; SK="${2:-$HOME/.claude/skills}"

if [[ ! -d "$T/.git" ]]; then
  URL="${TOOLBOX_REPO:-$(git -C "$SRC" remote get-url origin 2>/dev/null || echo "$SRC")}"
  echo "== clone $URL -> $T"
  git clone -q "$URL" "$T"
fi
T="$(cd "$T" && pwd)"

echo "== upstreams (manifest.json, pinned)"
fails=0
while IFS=$'\t' read -r name url sha path; do
  if [[ "$sha" == "-" ]]; then echo "link  $name  $url (no pinned commit, not cloned)"; continue; fi
  d="$T/$path"
  if [[ -e "$d" ]]; then echo "skip  $path (exists)"; continue; fi
  mkdir -p "$d"
  if git -C "$d" init -q && git -C "$d" remote add origin "$url" \
     && git -C "$d" fetch -q --depth 1 origin "$sha" && git -C "$d" checkout -q FETCH_HEAD; then
    echo "ok    $path @ ${sha:0:12}"
  else
    echo "FAIL  $path ($url @ $sha)"; fails=$((fails + 1))
  fi
done < <(python3 - "$T/manifest.json" <<'PY'
import json, sys
tools = json.load(open(sys.argv[1]))["tools"]
for t in sorted(tools, key=lambda t: len(t["path"])):   # parents before sub-paths
    ok = t.get("commit") and not t["path"].startswith("(")
    print("\t".join([t["name"], t["url"], t["commit"] if ok else "-", t["path"]]))
PY
)

echo "== catalog"
before="$(cat "$T"/catalog/*.md | grep -c '^- ' || true)"
"$T/bin/build-catalog.sh" | tail -2
after="$(cat "$T"/catalog/*.md | grep -c '^- ' || true)"
echo "catalog entries: $after rebuilt from what is on disk, $before in the committed copy."
(( after >= before )) || echo "  The committed index lists tools not restored here. See it with: git -C $T diff --stat -- catalog"

echo "== my skills -> $SK"
mkdir -p "$SK"
for d in "$T"/my-skills/*/; do
  s="$(basename "$d")"
  if [[ -e "$SK/$s" ]]; then echo "skip  $s (exists)"; else cp -R "$d" "$SK/$s" && echo "ok    $s"; fi
done

echo "== MCP templates that need credentials"
for f in "$T"/mcp-templates/*.json; do
  vars="$(grep -o '\${[A-Z0-9_]*}' "$f" | sort -u | grep -v '^\${HOME}$' | tr '\n' ' ' || true)"
  [[ -n "$vars" ]] && echo "$(basename "$f" .json): $vars"
done

echo "== not restorable from the manifest"
echo "agents/  re-install from repos/msitarzewski__agency-agents (./scripts/install.sh --tool claude-code), then move the files into agents/"
echo "skills/  third-party skills with no upstream recorded yet; see docs/SETUP.md"
(( fails == 0 )) || { echo "$fails upstream(s) failed" >&2; exit 1; }
