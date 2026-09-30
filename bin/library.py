#!/usr/bin/env python3
"""Sweep the WHOLE library, then search it by meaning.

  library.py index              rebuild index/library.jsonl from every source (+ local embeddings)
  library.py health             write index/health.json: what is usable right now
  library.py find "<goal>"      ranked candidates from every kind, with a coverage line
      --named "Claude Design,Higgsfield"   tools the user asked for: always shown, never dropped
      -n 40                                how many overall; each kind also gets a quota
      --json                               machine output for a sweep subagent

Sources (all optional, missing ones are skipped and reported):
  toolbox catalog (full descriptions read from each SKILL.md / agent file, not the truncated line),
  live skills (~/.claude/skills), extra skill/design-system roots and memory dirs from
  library-sources.json, MCP servers (names only), connectors seen in the live session
  (index/session.txt), API key NAMES (never contents), capabilities.md chains.

Embeddings come from a local Ollama model (default nomic-embed-text). If Ollama is down the
search falls back to keyword scoring and says so, it never silently narrows.
"""
import glob, hashlib, json, math, os, re, shutil, subprocess, sys, time, urllib.request

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
IDX = os.path.join(TB, "index"); os.makedirs(IDX, exist_ok=True)
LIB, EMB, HEALTH = (os.path.join(IDX, f) for f in ("library.jsonl", "embeddings.json", "health.json"))
CFG_F = os.path.join(TB, "library-sources.json")
DEFAULT_CFG = {
    "skill_roots": ["~/.claude/skills", "~/.claude/plugins/cache"],
    "design_skill_roots": ["~/Design-Tools/open-design/skills",
                           # Open Design plugins sit one level deeper (plugins/_official/<group>/<name>,
                           # plugins/community/<name>); 431 skills here were invisible until 2026-09-21,
                           # incl. the Awwwards motion skill, hallmark and the WebGL galleries.
                           "~/toolbox/parked/app-sources/nexu-io__open-design/plugins/community",
                           "~/toolbox/parked/app-sources/nexu-io__open-design/plugins/_official/*"],
    "design_system_roots": ["~/Design-Tools/open-design/design-systems"],
    "design_md_index": "~/design-md-library/INDEX.md",
    "memory_globs": ["~/.claude/projects/*/memory/*.md"],
    "key_dirs": ["~/.config/vb"],
    "mcp_configs": ["~/.claude.json", "~/toolbox/mcp/mine/*.json"],
    "embed_model": "nomic-embed-text",
    "ollama": "http://127.0.0.1:11434",
}
# per-kind quota in `find` so one kind can never crowd out the rest
QUOTA = {"skill": 10, "agent": 6, "mcp": 4, "connector": 3, "plugin": 3, "design-system": 4,
         "note": 6, "app": 3, "key": 3}

def cfg():
    c = dict(DEFAULT_CFG)
    if os.path.exists(CFG_F):
        c.update(json.load(open(CFG_F)))
    return c

def ex(p): return os.path.expanduser(p)

def front(path, limit=4000):
    """name + description from YAML front matter, plus the first real paragraph of the body."""
    try: t = open(path, errors="replace").read(limit)
    except OSError: return "", "", ""
    name = desc = ""
    m = re.match(r"---\n(.*?)\n---\n?(.*)", t, re.S)
    body = t
    if m:
        fm, body = m.group(1), m.group(2)
        n = re.search(r"^name:\s*(.+)$", fm, re.M); name = n.group(1).strip().strip("\"'") if n else ""
        d = re.search(r"^description:\s*(\|?)(.*?)(?=^\w[\w-]*:|\Z)", fm, re.M | re.S)
        if d: desc = re.sub(r"\s+", " ", d.group(2)).strip().strip("\"'")
    para = next((p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith(("#", "```", "|", "<"))), "")
    return name, desc, re.sub(r"\s+", " ", para)[:500]

def items():
    c = cfg(); out, seen, report = [], set(), {}
    def add(kind, name, desc, path="", src=""):
        key = (kind, name.lower())
        if not name: return
        if key in seen:   # keep the richer description when two sources name the same tool
            for o in out:
                if (o["kind"], o["name"].lower()) == key and len(desc) > len(o["desc"]): o["desc"] = desc.strip()[:1500]
            return
        seen.add(key); out.append({"kind": kind, "name": name, "desc": desc.strip()[:1500], "path": path, "src": src})
        report[src] = report.get(src, 0) + 1
    # 1. toolbox catalog, descriptions re-read in full from the file itself
    for f in sorted(glob.glob(os.path.join(TB, "catalog", "*.md"))):
        cat = os.path.basename(f)[:-3]
        for line in open(f, errors="replace"):
            if not line.startswith("- ") or "|" not in line: continue
            parts = [p.strip() for p in line[2:].split("|")]
            if len(parts) < 3: continue
            kind, name, desc = parts[0], parts[1], parts[2]
            path = parts[3] if len(parts) > 3 else ""
            full = os.path.join(TB, path) if path and not path.startswith("/") else path
            if full and os.path.isfile(full):
                _, d2, para = front(full); desc = (d2 or desc) + (" " + para if para else "")
            k = {"mcp-mine": "mcp", "mcp-discovered": "mcp", "application": "app", "agent-tool": "app"}.get(kind, kind)
            add(k, name, f"[{cat}] {desc}", path, "catalog")
    # 2. live + extra skill roots
    for root in c["skill_roots"] + c["design_skill_roots"]:
        src = "design-skills" if root in c["design_skill_roots"] else "live-skills"
        # plugin caches nest skills at <plugin>/<pkg>/<version>/skills/<name>/SKILL.md, so walk them fully;
        # add() dedupes by name, so older cached versions of the same skill collapse into one row.
        deep = "plugins/cache" in root
        for f in sorted(glob.glob(os.path.join(ex(root), "**" if deep else "*", "SKILL.md"), recursive=deep), reverse=deep):
            n, d, para = front(f); add("skill", n or os.path.basename(os.path.dirname(f)), d + " " + para, f, src)
    # 3. design systems
    for root in c["design_system_roots"]:
        for f in glob.glob(os.path.join(ex(root), "*", "*.md")):
            t = open(f, errors="replace").read(1500)
            cat = re.search(r"Category:\s*(.+)", t); first = re.search(r"\n\n([^#>\n].+)", t)
            add("design-system", "open-design/" + os.path.basename(os.path.dirname(f)),
                (cat.group(1) if cat else "") + ". " + (first.group(1) if first else ""), f, "design-systems")
    mi = ex(c["design_md_index"])
    if os.path.exists(mi):
        for line in open(mi, errors="replace"):
            m = re.match(r"\|\s*([\w.\-]+)\s*\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|", line)
            if m and m.group(1) != "name":
                add("design-system", "design-md/" + m.group(1), m.group(3), os.path.join(os.path.dirname(mi), m.group(2)), "design-md")
    # 4. memory notes: local tools, limits and rules that are not skills
    for g in c["memory_globs"]:
        for f in glob.glob(ex(g)):
            if os.path.basename(f) == "MEMORY.md": continue
            n, d, _ = front(f, 1500); add("note", n or os.path.basename(f)[:-3], d, f, "memory")
    # 5. MCP servers (names only) and connectors seen in the session
    for g in c["mcp_configs"]:
        for f in glob.glob(ex(g)):
            try: j = json.load(open(f))
            except Exception: continue
            for n in (j.get("mcpServers") or {}) if isinstance(j, dict) else {}:
                add("mcp", n, "MCP server configured in " + os.path.basename(f), f, "mcp")
    sess = os.path.join(IDX, "session.txt")
    if os.path.exists(sess):
        for line in open(sess):
            n = line.strip()
            if not n or n.startswith("#"): continue
            name, _, d = n.partition(" | ")
            kind = "connector" if name.startswith("claude_ai_") else "app" if name.startswith("builtin:") else "mcp"
            add(kind, name, d or "live in the Claude session", "", "session")
    # 6. API key NAMES only, never contents
    for d in c["key_dirs"]:
        for f in glob.glob(os.path.join(ex(d), "*")):
            b = os.path.basename(f)
            if re.search(r"key|token", b, re.I):
                add("key", b, "credential file present (name only)", "", "keys")
    return out, report

# ---------------------------------------------------------------- embeddings
def embed(texts, c):
    body = json.dumps({"model": c["embed_model"], "input": texts}).encode()
    r = urllib.request.urlopen(urllib.request.Request(c["ollama"] + "/api/embed", data=body,
                               headers={"Content-Type": "application/json"}), timeout=300)
    return json.load(r)["embeddings"]

def text_of(it): return f"{it['kind']} {it['name']}: {it['desc']}"
def h(s): return hashlib.sha1(s.encode()).hexdigest()[:16]

def cmd_index(a):
    if os.path.exists(LIB): shutil.copy(LIB, LIB + ".bak")  # index/ is gitignored: keep one previous copy
    c = cfg(); its, rep = items()
    with open(LIB, "w") as fh:
        for it in its: fh.write(json.dumps(it) + "\n")
    cache = json.load(open(EMB)) if os.path.exists(EMB) else {}
    need = [it for it in its if h(text_of(it)) not in cache]
    ok = True
    try:
        for i in range(0, len(need), 64):
            batch = need[i:i + 64]
            for it, v in zip(batch, embed([text_of(x)[:2000] for x in batch], c)):
                cache[h(text_of(it))] = [round(x, 5) for x in v]
    except Exception as e:
        ok = False; print(f"embeddings skipped ({e}); find will use keyword scoring", file=sys.stderr)
    keep = {h(text_of(it)) for it in its}
    json.dump({k: v for k, v in cache.items() if k in keep}, open(EMB, "w"))
    kinds = {}
    for it in its: kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    print(f"indexed {len(its)} items | by source: {rep} | by kind: {kinds} | embeddings {'ok' if ok else 'MISSING'}")

# ---------------------------------------------------------------- health
def cmd_health(a):
    c = cfg(); out = {"checked": time.strftime("%Y-%m-%d %H:%M"), "items": {}}
    def zwhich(b):
        return subprocess.run(["zsh", "-lc", f"command -v {b}"], capture_output=True).returncode == 0
    try: urllib.request.urlopen(c["ollama"] + "/api/tags", timeout=3); ol = "ok"
    except Exception: ol = "down"
    out["items"]["ollama"] = {"status": ol}
    for b in ("gh", "vercel", "yt-dlp", "gitleaks", "ffmpeg", "node", "docker"):
        out["items"][b] = {"status": "ok" if zwhich(b) else "missing"}
    over = os.path.join(TB, "health-overrides.json")   # hand-kept: paywalls, caps, signed-out connectors
    if os.path.exists(over):
        for k, v in json.load(open(over)).items(): out["items"][k] = v
    json.dump(out, open(HEALTH, "w"), indent=1)
    bad = {k: v for k, v in out["items"].items() if v.get("status") != "ok"}
    print(f"health: {len(out['items'])} checked, {len(bad)} not usable: " + ", ".join(f"{k}={v.get('status')}" for k, v in bad.items()))

# ---------------------------------------------------------------- find
def tokens(s): return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2]

def cmd_find(a):
    c = cfg()
    if not os.path.exists(LIB): sys.exit("no index yet: run `library.py index`")
    its = [json.loads(l) for l in open(LIB)]
    cache = json.load(open(EMB)) if os.path.exists(EMB) else {}
    health = json.load(open(HEALTH))["items"] if os.path.exists(HEALTH) else {}
    q = a.goal; qt = set(tokens(q)); mode = "semantic+keyword"
    try: qv = embed([q], c)[0]; qn = math.sqrt(sum(x * x for x in qv))
    except Exception: qv = None; mode = "KEYWORD ONLY (Ollama down: run `ollama serve`)"
    df = {}
    for it in its:
        for w in set(tokens(text_of(it))): df[w] = df.get(w, 0) + 1
    N = len(its)
    def score(it):
        t = tokens(text_of(it)); kw = sum(math.log(N / df.get(w, N)) for w in qt if w in t) / (1 + len(qt))
        sem = 0.0
        v = cache.get(h(text_of(it)))
        if qv is not None and v:
            sem = sum(x * y for x, y in zip(qv, v)) / (qn * math.sqrt(sum(y * y for y in v)) + 1e-9)
        return 0.75 * sem + 0.25 * min(kw, 1.0)
    ranked = sorted(its, key=score, reverse=True)
    picked, per = [], {}
    for it in ranked:
        k = it["kind"]
        if per.get(k, 0) < QUOTA.get(k, 3) and len(picked) < a.n:
            picked.append(it); per[k] = per.get(k, 0) + 1
    named = [n.strip() for n in a.named.split(",") if n.strip()]
    for n in named:   # user-named tools are never dropped
        hit = sorted((it for it in its if n.lower() in (it["name"] + " " + it["desc"]).lower()),
                     key=lambda it: (n.lower() not in it["name"].lower(), it["kind"] == "note"))
        for it in reversed(hit[:2]):
            if it not in picked: picked.insert(0, dict(it, named=True))
        if not hit: picked.insert(0, {"kind": "?", "name": n, "desc": "NAMED BY USER but not found in the library: say so, then look for it live", "path": "", "named": True})
    caps = []
    cf = os.path.join(TB, "capabilities.md")
    if os.path.exists(cf):
        for block in re.split(r"^## ", open(cf).read(), flags=re.M)[1:]:
            head, *rest = block.splitlines()
            if set(tokens(head + " " + " ".join(rest[:2]))) & qt: caps.append("## " + head + "\n" + "\n".join(l for l in rest if l.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7."))))
    kinds = {}
    for it in its: kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    age_h = (time.time() - os.path.getmtime(LIB)) / 3600
    cov = f"COVERAGE searched {N} of {N} items ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}) | mode: {mode} | returned {len(picked)} | index built {age_h:.0f}h ago" + (" (STALE: run library.py index)" if age_h > 24 else "")
    if a.json:
        print(json.dumps({"coverage": cov, "candidates": [dict(it, score=round(score(it), 3), health=health.get(it["name"], {})) for it in picked], "capabilities": caps})); return
    print(cov)
    for it in picked:
        hs = health.get(it["name"], {}).get("status")
        flag = (" [NAMED]" if it.get("named") else "") + (f" [{hs.upper()}]" if hs and hs != "ok" else "")
        print(f"- {it['kind']:13} {it['name']}{flag}  ({score(it):.2f})\n    {it['desc'][:220]}\n    {it['path'].replace(HOME, '~')}")
    if caps: print("\nFALLBACK CHAINS that match this goal (walk them in order on any failure):\n" + "\n\n".join(caps))

def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0]); s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("index").set_defaults(fn=cmd_index)
    s.add_parser("health").set_defaults(fn=cmd_health)
    f = s.add_parser("find"); f.add_argument("goal"); f.add_argument("-n", type=int, default=40)
    f.add_argument("--named", default=""); f.add_argument("--json", action="store_true"); f.set_defaults(fn=cmd_find)
    a = p.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
