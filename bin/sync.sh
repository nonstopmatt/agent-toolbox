#!/usr/bin/env bash
# Rebuild the catalog, scan exactly what would be committed, then commit and push.
# Aborts on any credential, home-folder path or private name in the staged snapshot.
#   --dry-run   stop after the scan and print the file tree; nothing is committed or pushed
set -euo pipefail
TB="$(cd "$(dirname "$0")/.." && pwd)"
cd "$TB"
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1
NAMES="${TOOLBOX_PRIVATE_NAMES:-$HOME/.config/toolbox/private-names.txt}"
[[ -r "$NAMES" ]] || { echo "ABORT: $NAMES is missing (names to block, one per line; may be empty)" >&2; exit 1; }

# Skills whose license restricts listing (e.g. "All rights reserved" with no grant):
# the filters below drop every line that points into them. The list stays in .git/.
EXCL="$(git rev-parse --absolute-git-dir)/public-exclude"
python3 - "$TB" "$EXCL" <<'PY'
import os, re, sys
tb, out = sys.argv[1:]
BAD = re.compile(r"all rights reserved|proprietary|non-?commercial|CC BY-NC|Business Source|Elastic License|PolyForm|Commons Clause", re.I)
GRANT = re.compile(r"Permission is hereby granted|Licensed under the Apache|Redistribution and use in source|ISC License|Mozilla Public|GNU (Affero |Lesser )?General Public", re.I)
dirs = set()
for root, _, files in os.walk(os.path.join(tb, "skills")):
    for f in files:
        if f.upper().startswith("LICENSE"):
            text = open(os.path.join(root, f), errors="replace").read(20000)
            if BAD.search(text) and not GRANT.search(text):
                dirs.add(os.path.relpath(root, tb) + "/")
open(out, "w").write("".join(d + "\n" for d in sorted(dirs)))
print(f"license-restricted skills left out of the repo: {len(dirs)}")
PY

# The clean filters .gitattributes names. required=true: a filter failure stops the add.
# Every committed file: home path -> ~, plugin cache paths hidden, restricted skills dropped.
DROP="{ /usr/bin/grep -vF -f '$EXCL'; test \$? -le 1; }"
# Match only path/glob characters. A broad "anything until whitespace" pattern once
# consumed Python quotes and brackets, leaving the committed source invalid.
PLUG='s|~/\.claude/plugins/cache/[A-Za-z0-9_./@*+%=:~-]*|(local plugin cache)|g'
git config filter.public.clean "sed -e \"s|\$HOME|~|g\" -e '$PLUG' | $DROP"
git config filter.publicjson.clean 'sed -e "s|$HOME|\${HOME}|g"'
git config filter.toolsmem.clean "sed -e \"s|\$HOME|~|g\" -e 's/ — last: .*\$//' | $DROP"
for f in public publicjson toolsmem; do git config "filter.$f.smudge" cat; git config "filter.$f.required" true; done

"$TB/bin/build-catalog.sh" >/dev/null

# Committed plugin list: only the plugins that are enabled, with what they contribute.
# plugins/INDEX.md (every installed plugin, cache paths) stays local and is gitignored, and
# each disabled plugin's catalog line joins the exclude list, so the repo shows what runs.
python3 - plugins/INDEX.md plugins/INDEX.public.md "$EXCL" <<'PY'
import re, sys
src, dst, excl = sys.argv[1:]
out = ["# Plugins", "", "The plugins this toolbox runs, loaded at session start. Everything else is",
       "parked and session-launched with --plugin-dir when a task needs it.", "",
       "| plugin | contributes |", "|---|---|"]
hidden = []
for b in re.split(r"^## ", open(src).read(), flags=re.M)[1:]:
    L = b.strip().splitlines()
    market, name = L[0].strip().split("/", 1)
    co = next((l.split(":", 1)[1].strip() for l in L if "**contributes**" in l), "")
    if any("**enabled**: True" in l for l in L):
        out.append(f"| `{name}@{market}` | {co} |")
    else:
        hidden.append(f"- plugin | {market}/{name} |\n")
open(dst, "w").write("\n".join(out) + "\n")
open(excl, "a").write("".join(hidden))
print(f"plugins: {len(out) - 7} public, {len(hidden)} disabled kept local")
PY

# My own skills: the repo copy mirrors the live ones.
for s in tool-audit skill-audit toolbox-add self-improvement-report; do
  rsync -a --delete --exclude __pycache__ "$HOME/.claude/skills/$s/" "my-skills/$s/"
done

git add -A
git add --renormalize .   # re-run the filters on unchanged files too
SNAP="$(mktemp -d)"; trap 'rm -rf "$SNAP"' EXIT
git checkout-index -a --prefix="$SNAP/"   # the filtered blobs, i.e. what GitHub would get
"$TB/bin/validate-public-snapshot.sh" "$SNAP"

GL=""
if command -v gitleaks >/dev/null; then
  GL="$SNAP.gitleaks.json"
  gitleaks dir "$SNAP" --no-banner --exit-code 0 --report-format json --report-path "$GL" >/dev/null 2>&1 || true
fi

python3 - "$SNAP" "$TB/bin/secret-allowlist.txt" "$NAMES" "$HOME" "$GL" <<'PY'
import json, os, re, sys
snap, allow_f, names_f, home, gl = sys.argv[1:6]
SECRET = re.compile(
    r"bearer\s+[A-Za-z0-9._~+/-]{16,}"
    r"|(?:api[-_]?key|apikey|token|secret|password|authorization)\s*[=:]\s*['\"]?(?!process\.env|os\.environ|var\.)[A-Za-z0-9._~+/-]{16,}"
    r"|sk-[A-Za-z0-9_-]{16,}|gh[opsu]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
    r"|xox[bapr]-[A-Za-z0-9-]{10,}|fc-[0-9a-f]{32}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|https?://\S*[?&](?:key|token|secret|api[-_]?key|access_token)=[^$&\s{]",
    re.I)
allow = {l.split("#")[0].strip() for l in open(allow_f)} - {""} if os.path.exists(allow_f) else set()
names = [l.strip() for l in open(names_f) if l.strip() and not l.startswith("#")]
NAME = re.compile(r"\b(?:%s)\b" % "|".join(map(re.escape, names)), re.I) if names else None
hits = []
for root, _, files in os.walk(snap):
    for fn in files:
        p = os.path.join(root, fn); rel = os.path.relpath(p, snap)
        try: lines = open(p, encoding="utf-8").read().splitlines()
        except UnicodeDecodeError: continue
        for i, l in enumerate(lines, 1):
            why = ("secret" if SECRET.search(l) else "home path" if home in l
                   else "private name" if NAME and NAME.search(l) else None)
            if why and f"{rel}:{i}" not in allow:
                hits.append(f"{why:12} {rel}:{i}")
if gl and os.path.exists(gl):
    for f in json.load(open(gl)) or []:
        rel = os.path.relpath(f["File"], snap)
        if f"{rel}:{f['StartLine']}" not in allow:
            hits.append(f"{'gitleaks':12} {rel}:{f['StartLine']} ({f['RuleID']})")
if hits:
    print("\n".join(["ABORT: the staged snapshot is not clean. Nothing committed."] + hits), file=sys.stderr)
    sys.exit(1)
print(f"scan clean: {sum(len(f) for _, _, f in os.walk(snap))} files, "
      f"{'gitleaks + ' if gl else ''}pattern scan, {len(names)} private names")
PY

if (( DRY )); then
  git ls-files | awk -F/ '{ if (NF == 1) print $0; else { d = $1; n[d]++; if (n[d] <= 6) print "  " $0; else if (n[d] == 7) print "  " d "/..." } }'
  echo "files staged: $(git ls-files | wc -l | tr -d ' ')  (dry run: not committed, not pushed)"
  exit 0
fi

if ! git diff --cached --quiet; then
  msg="$(sed -n 's/^## //p' CHANGELOG.md | head -1)"
  git commit -q -m "toolbox: ${msg:-sync}"
  echo "committed: $(git log -1 --format='%h %s')"
fi
if git remote get-url origin >/dev/null 2>&1; then
  git push -q -u origin HEAD && echo "pushed to $(git remote get-url origin)"
else
  echo "no origin remote: committed locally only"
fi
