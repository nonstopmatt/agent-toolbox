#!/usr/bin/env python3
"""Sweep the WHOLE library, then search it by meaning.

  library.py index              rebuild index/library.jsonl from every source (+ local embeddings)
  library.py health             write index/health.json: what is usable right now
  library.py profile            write a card per tool (does / use_when / not_for / input / output / needs)
                                from its FULL source with a local model; only new or changed tools
  library.py find "<goal>"      ranked candidates from every kind, with coverage + understanding lines
      --named "Claude Design,Higgsfield"   tools the user asked for: always shown, never dropped
      -n 40                                how many overall; each kind also gets a quota
      --json                               machine output for a sweep subagent
  library.py eval               ledger replay: of the tools that worked for a goal, how many find surfaces

Sources (all optional, missing ones are skipped and reported):
  toolbox catalog (full descriptions read from each SKILL.md / agent file, not the truncated line),
  live skills (~/.claude/skills), extra skill/design-system roots and memory dirs from
  library-sources.json, MCP servers (names only), connectors seen in the live session
  (index/session.txt), API key NAMES (never contents), capabilities.md chains, and free
  websites (catalog/websites.md, generated from websites.json) as kind `website`.

Embeddings come from a local Ollama model (default nomic-embed-text). If Ollama is down the
search falls back to keyword scoring and says so, it never silently narrows.
"""
import glob, hashlib, json, math, os, re, shutil, subprocess, sys, time, urllib.request

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
IDX = os.path.join(TB, "index"); os.makedirs(IDX, exist_ok=True)
LIB, HEALTH = (os.path.join(IDX, f) for f in ("library.jsonl", "health.json"))
def emb_file(c): return os.path.join(IDX, "embeddings-" + re.sub(r"[^\w.-]", "_", c["embed_model"]) + ".json")  # one cache per model
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
    # Chosen by `library.py eval` 2026-10-03 over the cards: median rank of the tool that worked 23 vs 60 for
    # nomic-embed-text (with or without its search_query/search_document prefixes).
    "embed_model": "qwen3-embedding:8b",
    "embed_query_prefix": "Instruct: Given a goal a person wants done, retrieve the tools (skills, agents, apps, "
                          "scripts, connectors) that would directly help accomplish it\nQuery: ",
    "embed_doc_prefix": "",
    "quota_x": 2,                   # per-kind quota multiplier: x2 surfaced 41% of the tools that worked vs 30% at x1
    # Jev-style judge (find --judge): any TypeSafe System One endpoint. Eval 2026-10-03 (qwen3, quota x2), surfaced /
    # median rank / top-10 of 93: no judge 38/23/32; tev1-16k batch 48 41/22/34; tev1-16k batch 8 42/19/35 (~20 s a
    # search); tinyjev 0.6B 42/21/26 (2.4 s).
    # tinyjev: judge_url http://127.0.0.1:8077/v1/systemone, judge_model TinyJev-0.6B, judge_start
    # ["~/toolbox/venvs/tinyjev/bin/tinyjev", "serve", "TinyJev-0.6B", "--backend", "mlx"]. Hosted Jev: its URL + judge_key_env.
    "judge_url": "http://127.0.0.1:11434/v1/systemone",   # Ollama 0.35+ decision models
    # Ollama scores a request's questions as ONE prompt (48 cards ~ 8k tokens), past tev1:4b's 2,050 window, so
    # the judge needs the 16k derivative: a Modelfile of "FROM tev1:4b" + "PARAMETER num_ctx 16384", then
    # `ollama create tev1-16k -f <that file>` (create does not read stdin); loadouts/jev-compaction-local.sh does it
    "judge_model": "tev1-16k",
    "judge_key_env": "",            # NAME of the env var holding a bearer key (e.g. TYPESAFE_API_KEY), never the key
    "judge_start": [],              # command to launch a local judge server when it is down; Ollama is always up
    "judge_batch": 8,               # questions per request: Ollama packs them into one prompt and big batches interfere
    "judge_weight": 0.5,            # final = (1 - w) * retrieval + w * judge
    "judge_pool": 3,                # judge this many times each kind's quota, so it can promote what embeddings missed
    "profile_model": "gemma4:e4b",    # writes the tool cards; beat qwen2.5:14b on specificity at equal speed; local, free, private (2026-10-03)
    "ollama": "http://127.0.0.1:11434",
}
# per-kind quota in `find` so one kind can never crowd out the rest
QUOTA = {"skill": 10, "agent": 6, "mcp": 4, "connector": 3, "plugin": 3, "design-system": 4,
         "note": 6, "app": 3, "key": 3, "script": 4, "cli": 3, "website": 5}

def cfg():
    c = dict(DEFAULT_CFG)
    if os.path.exists(CFG_F):
        c.update(json.load(open(CFG_F)))
    if os.environ.get("LIBRARY_CFG"): c.update(json.loads(os.environ["LIBRARY_CFG"]))   # one-off overrides for experiments
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
            if k == "website":   # path is the URL; the job categories sit in the next column
                cat = parts[4] if len(parts) > 4 else cat
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
    # 4b. the user's own scripts: every script a memory note names by path, plus its sibling scripts (a note
    #     naming one script can be the only trail to the one beside it), ~/.claude/scripts and toolbox/bin.
    pat = re.compile(r"(?:~|/Users/\w+)/[\w./@+-]+?\.(?:py|sh|mjs|js|ts)\b")
    named, mention = set(), {}
    for g in c["memory_globs"]:
        for f in glob.glob(ex(g)):
            body = open(f, errors="replace").read()
            for m in pat.finditer(body):
                sp = os.path.expanduser(m.group(0)) if m.group(0).startswith("~") else m.group(0)
                if os.path.isfile(sp):
                    named.add(sp)
                    line = next((l for l in body.splitlines() if m.group(0) in l), "")
                    mention.setdefault(sp, f"{os.path.basename(f)[:-3]}: {line.strip()[:240]}")
    scripts = set(named)
    for d in {os.path.dirname(x) for x in named} | {ex("~/.claude/scripts"), os.path.join(TB, "bin")}:
        scripts |= {x for x in glob.glob(os.path.join(d, "*")) if x.endswith((".py", ".sh", ".mjs")) and os.path.isfile(x)}
    for sp in sorted(scripts):
        head = re.sub(r"\s+", " ", re.sub(r"^#!.*\n", "", _read(sp, 1200)))[:600]
        add("script", sp.replace(HOME, "~"), (("Named in memory note " + mention[sp] + " | ") if sp in mention else "")
            + "Script header: " + head, sp, "scripts")
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
            kind = ("connector" if name.startswith("claude_ai_") else "app" if name.startswith("builtin:")
                    else "skill" if name.startswith("skill:") else "mcp")
            add(kind, name.removeprefix("skill:"), d or "live in the Claude session", "", "session")
    # 6. API key NAMES only, never contents
    for d in c["key_dirs"]:
        for f in glob.glob(os.path.join(ex(d), "*")):
            b = os.path.basename(f)
            if re.search(r"key|token", b, re.I):
                add("key", b, "credential file present (name only)", "", "keys")
    # 7. the ledger: every tool that ever ran gets its record attached, and tools ONLY the ledger knows
    #    (local CLIs, pipelines, scripts) become searchable from what they actually did.
    led = {}
    for l in (open(LEDGER) if os.path.exists(LEDGER) else []):
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("skill"): led.setdefault(norm(r["skill"].split(":")[-1]), []).append(r)
    byname = {}
    for o in out: byname.setdefault(norm(o["name"].split(":")[-1].split("/")[-1]), []).append(o)
    for t, rs in led.items():
        oc = {}
        for r in rs: oc[r.get("outcome", "?")] = oc.get(r.get("outcome", "?"), 0) + 1
        notes = [r["note"] for r in rs if r.get("note") and r.get("outcome") in ("worked", "mixed")][-3:]
        summary = (", ".join(f"{v} {k}" for k, v in sorted(oc.items())) + " ["
                   + ", ".join(sorted({r.get("situation", "") for r in rs if r.get("situation")})) + "]"
                   + (" | last: " + rs[-1].get("note", "")[:160] if rs[-1].get("note") else ""))
        if t in byname:
            for o in byname[t]: o["ledger"] = summary
        elif len(t) > 3:
            r0 = rs[-1]; before = len(out)
            add(r0.get("kind") or "cli", r0["skill"], "Local tool known from the run ledger. What it did: "
                + " | ".join(notes or [r0.get("note", "")]), "", "ledger")
            if len(out) > before: out[-1]["ledger"] = summary
    # 8. profile cards (library.py profile) ride along so find and the sweep subagent see them
    prof = load_profiles()
    for o in out:
        p = prof.get(f"{o['kind']}|{o['name']}")
        if p: o["card"] = dict(p["card"], basis=p["basis"])
    return out, report

# ---------------------------------------------------------------- embeddings
def embed(texts, c):
    body = json.dumps({"model": c["embed_model"], "input": texts}).encode()
    r = urllib.request.urlopen(urllib.request.Request(c["ollama"] + "/api/embed", data=body,
                               headers={"Content-Type": "application/json"}), timeout=300)
    return json.load(r)["embeddings"]

def text_of(it):
    """What gets embedded and keyword-scored: the profile card when there is one (what the tool DOES and
    the goals it serves, read from its full source), else the front-matter blurb. not_for stays out on
    purpose: embedding "not for cold email" pulls the item TOWARD cold-email goals."""
    p = it.get("card")
    if not p: return f"{it['kind']} {it['name']}: {it['desc']}"
    return (f"{it['kind']} {it['name']}: {p.get('does', '')} Use when: {'; '.join(p.get('use_when', []))}. "
            f"Input: {p.get('input', '')}. Output: {p.get('output', '')}. {it['desc'][:300]}")
def h(s): return hashlib.sha1(s.encode()).hexdigest()[:16]

def cmd_index(a):
    if os.path.exists(LIB): shutil.copy(LIB, LIB + ".bak")  # index/ is gitignored: keep one previous copy
    c = cfg(); its, rep = items()
    with open(LIB, "w") as fh:
        for it in its: fh.write(json.dumps(it) + "\n")
    EMB = emb_file(c); ekey = lambda it: h(c["embed_doc_prefix"] + text_of(it))
    cache = json.load(open(EMB)) if os.path.exists(EMB) else {}
    need = [it for it in its if ekey(it) not in cache]
    ok = True
    try:
        for i in range(0, len(need), 64):
            batch = need[i:i + 64]
            for it, v in zip(batch, embed([c["embed_doc_prefix"] + text_of(x)[:2000] for x in batch], c)):
                cache[ekey(it)] = [round(x, 5) for x in v]
    except Exception as e:
        ok = False; print(f"embeddings skipped ({e}); find will use keyword scoring", file=sys.stderr)
    keep = {ekey(it) for it in its}
    json.dump({k: v for k, v in cache.items() if k in keep}, open(EMB, "w"))
    kinds = {}
    for it in its: kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    print(f"indexed {len(its)} items | by source: {rep} | by kind: {kinds} | embeddings {'ok' if ok else 'MISSING'}")

# ---------------------------------------------------------------- profile
# A card per tool, written by a local model from the tool's FULL source, so `find` matches on what a
# tool does instead of its name and a 30-word blurb. Cached by source hash: re-runs only touch new or
# changed tools. Notes and keys are skipped (notes are already written as summaries; keys are names).
PROF = os.path.join(IDX, "profiles.json")
PROFILE_KINDS = ("mcp", "connector", "plugin", "app", "cli", "script", "agent", "skill", "design-system")
CARD_V = "card-v1"   # bump when CARD_PROMPT changes in meaning: every card is rewritten on the next profile run
CARD_PROMPT = """You are cataloguing one tool in a developer's toolbox so another AI agent can decide, for a given task, whether this tool is the right one. Read the SOURCE and write a JSON card. Be concrete and specific to THIS tool: name the actual mechanism, files, services and outputs. Generic phrases like "helps with tasks" are useless. Use only what the SOURCE says; where it is silent write "unknown".

JSON keys:
"does": 2-3 sentences, what it actually does and how.
"use_when": 4-8 short task requests a user might type that this tool serves well, e.g. "write a cold email sequence for plumbers".
"not_for": 1-4 jobs it looks like it covers but does not, or where another kind of tool is better.
"input": what you give it.
"output": what you get back (file, page, answer, edit, video...).
"needs": API keys, CLIs, apps, sign-ins or paid services it requires, or "nothing".

KIND: {kind}
NAME: {name}
SOURCE:
{source}"""

def _read(p, n):
    try: return open(p, errors="replace").read(n)
    except OSError: return ""

def _clip(t, n=14000):
    """Long files: keep the head, then every heading after it, so a 60k skill still shows its full scope."""
    if len(t) <= n: return t
    heads = [l for l in t[n:].splitlines() if l.startswith("#")]
    return t[:n] + "\n...\n[later sections]\n" + "\n".join(heads[:80])

def _session_tools():
    out, f = {}, os.path.join(IDX, "session-tools.txt")   # "server | tool, tool, ..." from the live session
    for l in (open(f) if os.path.exists(f) else []):
        if " | " in l and not l.startswith("#"):
            k, _, v = l.partition(" | "); out[k.strip()] = v.strip()
    return out

def _marketplace():
    """Plugin blurbs by name, plus the toolbox manifest and the hand-kept mcp-products.json (no secrets in any)."""
    out = {"_manifest": [], "_products": {}}
    for f, key, pick in (("manifest.json", "_manifest", lambda j: j.get("tools", [])),
                         ("mcp-products.json", "_products", lambda j: j)):
        try: out[key] = pick(json.load(open(os.path.join(TB, f))))
        except (OSError, ValueError): pass
    for f in glob.glob(os.path.join(HOME, ".claude/plugins/marketplaces/*/.claude-plugin/marketplace.json")):
        try:
            for p in json.load(open(f)).get("plugins", []):
                if p.get("name"): out[p["name"]] = p.get("description") or ""
        except (OSError, ValueError): pass
    return out

def source_of(it, st, mk):
    """(basis, text) for one item. MCP configs under ~/toolbox/mcp are NEVER read here: they hold tokens.
    MCP understanding comes from the live session's tool list and marketplace blurbs instead."""
    k, p = it["kind"], it.get("path", "")
    if it.get("src") == "ledger": return "ledger", it["desc"]
    full = p if p.startswith("/") else os.path.join(TB, p) if p else ""
    if k == "script" and os.path.isfile(full):
        return "full-file", it["desc"][:400] + "\n\nSCRIPT SOURCE:\n" + _clip(_read(full, 60000), 8000)
    if k in ("skill", "agent", "design-system") and os.path.isfile(full):
        t = _clip(_read(full, 200000), 6000 if k == "design-system" else 14000)
        if k == "skill":
            d = os.path.dirname(full)
            extra = sorted(os.path.relpath(x, d) for x in glob.glob(os.path.join(d, "*", "*")) if os.path.isfile(x))[:40]
            if extra: t += "\n\nFILES SHIPPED WITH IT: " + ", ".join(extra)
        return "full-file", t
    if k == "plugin" and os.path.isdir(full):
        try: pj = json.loads(_read(os.path.join(full, ".claude-plugin", "plugin.json"), 20000) or "{}")
        except ValueError: pj = {}
        parts = [f"plugin.json description: {pj.get('description', '')}", it["desc"]]
        for sk in sorted(glob.glob(os.path.join(full, "skills", "*", "SKILL.md")))[:60]:
            n, d, _ = front(sk); parts.append(f"skill {n}: {d[:200]}")
        for ag in sorted(glob.glob(os.path.join(full, "agents", "*.md")))[:20]:
            n, d, _ = front(ag); parts.append(f"agent {n or os.path.basename(ag)}: {d[:200]}")
        cmds = [os.path.basename(c)[:-3] for c in glob.glob(os.path.join(full, "commands", "*.md"))]
        if cmds: parts.append("commands: " + ", ".join(sorted(cmds)[:40]))
        readme = next((r for r in glob.glob(os.path.join(full, "README*"))), "")
        if readme: parts.append("README:\n" + _read(readme, 4000))
        return "plugin-tree", "\n".join(parts)
    if k == "app":
        parts = [it["desc"]]
        readme = next((r for r in glob.glob(os.path.join(full, "README*"))), "") if os.path.isdir(full) else ""
        if readme: parts.append("README:\n" + _read(readme, 6000))
        if it["name"] in st: parts.append("Tools it exposes: " + st[it["name"]])
        return ("readme" if readme else "catalog-line"), "\n".join(parts)
    if k in ("mcp", "connector"):
        base = re.sub(r"__[0-9a-f]{6,}$", "", it["name"]).replace("claude_ai_", "")
        parts = [it["desc"]]; basis = "name-only"
        tools = st.get(it["name"]) or st.get(base)
        man = next((e for e in mk["_manifest"] if e.get("name", "").lower().endswith("__" + base.lower())), None)
        known = mk["_products"].get(base, "")
        for label, val, b in (("Tools it exposes (from the live session)", tools, "session-tools"),
                              ("Toolbox manifest", man and man.get("desc"), "manifest"),
                              ("Marketplace description", mk.get(base), "marketplace"),
                              ("What the product is", known if not known.startswith("unknown") else "", "known-product")):
            if val:
                parts.append(f"{label}: {val}")
                if basis == "name-only": basis = b
        return basis, "\n".join(parts)
    return ("blurb", it["desc"]) if it["desc"].strip() else ("", "")

def card_of(it, basis, src, c):
    if basis == "name-only":   # a model asked about a bare name invents use cases, and those then match real goals
        return {"does": f"Unknown: only the name '{it['name']}' is on record. Add a line to mcp-products.json if you know it.",
                "use_when": [], "not_for": [], "input": "unknown", "output": "unknown", "needs": "unknown"}
    body = json.dumps({"model": c["profile_model"], "stream": False, "format": "json", "think": False,  # thinking: 5x the tokens, same card
                       "options": {"num_ctx": 8192, "temperature": 0.1},
                       "messages": [{"role": "user", "content": CARD_PROMPT.format(
                           kind=it["kind"], name=it["name"], source=src)}]}).encode()
    for attempt in (1, 2):   # gemma occasionally stops mid-string (~0.3% of cards); one retry clears most
        r = urllib.request.urlopen(urllib.request.Request(c["ollama"] + "/api/chat", data=body,
                                   headers={"Content-Type": "application/json"}), timeout=600)
        try: card = json.loads(json.load(r)["message"]["content"]); break
        except ValueError:
            if attempt == 2: raise
    for f in ("use_when", "not_for"):   # small models sometimes return a string where a list belongs
        if isinstance(card.get(f), str): card[f] = [card[f]]
    return {k: card.get(k, "unknown") for k in ("does", "use_when", "not_for", "input", "output", "needs")}

def load_profiles(): return json.load(open(PROF)) if os.path.exists(PROF) else {}

def cmd_profile(a):
    from concurrent.futures import ThreadPoolExecutor
    c = cfg(); its, _ = items(); st, mk = _session_tools(), _marketplace()
    prof = load_profiles(); todo = []
    for it in its:
        if it["kind"] not in PROFILE_KINDS or (a.only and a.only.lower() not in it["name"].lower()): continue
        basis, src = source_of(it, st, mk)
        if not src: continue
        key = f"{it['kind']}|{it['name']}"   # new prompt or model = new cards; name-only cards never touch the model
        sh = h(("fixed" if basis == "name-only" else c["profile_model"] + CARD_V) + src)
        if prof.get(key, {}).get("hash") != sh or a.force: todo.append((key, sh, basis, src, it))
    # cheapest, least-known kinds first; the 321 Open Design skills and the design systems last
    todo.sort(key=lambda j: (PROFILE_KINDS.index(j[4]["kind"]) if j[4]["kind"] != "design-system" else 99,
                             j[4].get("src") == "design-skills"))
    todo = todo[:a.limit] if a.limit else todo
    print(f"profile: {len(todo)} to write with {c['profile_model']} ({len(prof)} cached)", flush=True)
    done, t0, fails = 0, time.time(), 0
    def work(job):
        key, sh, basis, src, it = job
        try: return key, {"hash": sh, "basis": basis, "model": c["profile_model"],
                          "date": time.strftime("%Y-%m-%d"), "card": card_of(it, basis, src, c)}
        except Exception as e: return key, e
    with ThreadPoolExecutor(a.workers) as ex:
        for key, res in ex.map(work, todo):
            done += 1
            if isinstance(res, Exception): fails += 1; print(f"  FAIL {key}: {res}", flush=True); continue
            prof[key] = res
            if done % 10 == 0 or done == len(todo):
                tmp = PROF + ".tmp"; json.dump(prof, open(tmp, "w")); os.replace(tmp, PROF)
                el = time.time() - t0
                print(f"  {done}/{len(todo)} | {el / done:.1f}s each | ~{(len(todo) - done) * el / done / 60:.0f} min left", flush=True)
    tmp = PROF + ".tmp"; json.dump(prof, open(tmp, "w")); os.replace(tmp, PROF)
    print(f"profile done: {done - fails} written, {fails} failed, {len(prof)} cards total. Next: library.py index")

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
    try:   # the find --judge model must exist where judge_url points (Ollama answers 400/404 otherwise)
        if ":11434" in c["judge_url"]:
            tags = [m["name"] for m in json.load(urllib.request.urlopen(c["ollama"] + "/api/tags", timeout=3))["models"]]
            ok = any(t.split(":")[0] == c["judge_model"].split(":")[0] and (":" not in c["judge_model"] or t == c["judge_model"]) for t in tags)
            out["items"]["judge"] = {"status": "ok" if ok else "missing",
                                     "fix": "" if ok else f"model {c['judge_model']} not in Ollama: see judge_model in library.py"}
    except Exception: out["items"]["judge"] = {"status": "down"}
    over = os.path.join(TB, "health-overrides.json")   # hand-kept: paywalls, caps, signed-out connectors
    if os.path.exists(over):
        for k, v in json.load(open(over)).items(): out["items"][k] = v
    json.dump(out, open(HEALTH, "w"), indent=1)
    bad = {k: v for k, v in out["items"].items() if v.get("status") != "ok"}
    print(f"health: {len(out['items'])} checked, {len(bad)} not usable: " + ", ".join(f"{k}={v.get('status')}" for k, v in bad.items()))

# ---------------------------------------------------------------- find
def tokens(s): return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2]

def load():
    if not os.path.exists(LIB): sys.exit("no index yet: run `library.py index`")
    its = [json.loads(l) for l in open(LIB)]
    df = {}
    for it in its:
        for w in set(tokens(text_of(it))): df[w] = df.get(w, 0) + 1
    EMB = emb_file(cfg())
    return its, (json.load(open(EMB)) if os.path.exists(EMB) else {}), df

def judge_text(it):
    p = it.get("card")
    if not p: return f"{it['kind']} {it['name']}: {it['desc'][:500]}"
    return (f"{it['kind']} {it['name']}: {p.get('does', '')} Use when: {'; '.join(p.get('use_when', [])[:4])}. "
            f"Not for: {'; '.join(p.get('not_for', [])[:2])}")

def judge(goal, its, c):
    """Jev-style typed judgment: P(this tool directly serves the goal) per item, from any System One endpoint.
    One noul question per item, batched; a local server in judge_start is launched detached if it is down."""
    hdr = {"Content-Type": "application/json"}
    key = os.environ.get(c.get("judge_key_env") or "", "")
    if key: hdr["Authorization"] = "Bearer " + key
    def post(body):
        req = urllib.request.Request(c["judge_url"], json.dumps(body).encode(), hdr)
        return json.load(urllib.request.urlopen(req, timeout=300))["answers"]
    def ask(batch):
        qs = {str(j): {"type": "noul", "instructions": "Would this tool directly help accomplish the goal? " + judge_text(it)}
              for j, it in enumerate(batch)}
        body = {"model": c["judge_model"], "state": {"goal": goal}, "questions": qs}
        try: return post(body)
        except urllib.error.URLError as e:
            if not c.get("judge_start") or isinstance(e, urllib.error.HTTPError): raise
            subprocess.Popen([ex(x) for x in c["judge_start"]], stdout=open(os.path.join(IDX, "judge.log"), "a"),
                             stderr=subprocess.STDOUT, start_new_session=True)   # outlives this process
            for _ in range(90):
                time.sleep(2)
                try: return post(body)
                except urllib.error.URLError: pass
            raise
    out = {}
    bs = c.get("judge_batch", 8)
    for i in range(0, len(its), bs):
        batch = its[i:i + bs]; ans = ask(batch)
        for j, it in enumerate(batch): out[(it["kind"], it["name"])] = float(ans[str(j)]["noul"])
    return out

def search(q, n, its, cache, df, c, use_judge=False):
    """Rank the whole library for one goal; return (picked under per-kind quota, score fn, mode)."""
    qt = set(tokens(q)); mode = "semantic+keyword"; N = len(its)
    try: qv = embed([c["embed_query_prefix"] + q], c)[0]; qn = math.sqrt(sum(x * x for x in qv))
    except Exception: qv = None; mode = "KEYWORD ONLY (Ollama down: run `ollama serve`)"
    sc = {}
    for it in its:
        t = tokens(text_of(it)); kw = sum(math.log(N / df.get(w, N)) for w in qt if w in t) / (1 + len(qt))
        sem = 0.0
        v = cache.get(h(c["embed_doc_prefix"] + text_of(it)))
        if qv is not None and v:
            sem = sum(x * y for x, y in zip(qv, v)) / (qn * math.sqrt(sum(y * y for y in v)) + 1e-9)
        sc[(it["kind"], it["name"])] = 0.75 * sem + 0.25 * min(kw, 1.0)
    score = lambda it: sc.get((it["kind"], it["name"]), 0.0)
    ranked = sorted(its, key=score, reverse=True)
    if use_judge:
        pool, per = [], {}
        for it in ranked:
            k = it["kind"]
            if k != "key" and per.get(k, 0) < QUOTA.get(k, 3) * c["judge_pool"]:
                pool.append(it); per[k] = per.get(k, 0) + 1
        t0 = time.time()
        try:
            jp = judge(q, pool, c); w = c["judge_weight"]
            for it in pool:
                key = (it["kind"], it["name"]); sc[key] = (1 - w) * sc[key] + w * jp[key]
            ranked = sorted(its, key=score, reverse=True)
            mode += f" + judge {c['judge_model']} ({len(pool)} judged in {time.time() - t0:.1f}s)"
        except Exception as e:
            mode += f" | JUDGE OFF ({type(e).__name__}: {str(e)[:80]}): ranked on retrieval only"
    picked, per = [], {}
    for it in ranked:
        k = it["kind"]
        if per.get(k, 0) < QUOTA.get(k, 3) * c.get("quota_x", 1) and len(picked) < n:
            picked.append(it); per[k] = per.get(k, 0) + 1
    return picked, score, mode

def cmd_find(a):
    c = cfg()
    its, cache, df = load()
    health = json.load(open(HEALTH))["items"] if os.path.exists(HEALTH) else {}
    q = a.goal; qt = set(tokens(q)); N = len(its)
    picked, score, mode = search(q, a.n, its, cache, df, c, a.judge)
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
    want = [it for it in its if it["kind"] in PROFILE_KINDS]; have = sum(1 for it in want if it.get("card"))
    thin = sum(1 for it in want if it.get("card", {}).get("basis") == "name-only")
    cov = f"COVERAGE searched {N} of {N} items ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}) | mode: {mode} | returned {len(picked)} | index built {age_h:.0f}h ago" + (" (STALE: run library.py index)" if age_h > 24 else "") \
        + f"\nUNDERSTANDING profiled {have} of {len(want)} tools from their source ({thin} from name only)" \
        + ("" if have == len(want) else f" | {len(want) - have} UNPROFILED: matched on blurb only, run `library.py profile`")
    if a.json:
        slim = lambda it: {k: v for k, v in it.items() if not (k == "desc" and it.get("card"))}   # the card supersedes the blurb
        print(json.dumps({"coverage": cov, "candidates": [dict(slim(it), score=round(score(it), 3), health=health.get(it["name"], {})) for it in picked], "capabilities": caps})); return
    print(cov)
    for it in picked:
        hs = health.get(it["name"], {}).get("status")
        flag = (" [NAMED]" if it.get("named") else "") + (f" [{hs.upper()}]" if hs and hs != "ok" else "")
        p = it.get("card")
        what = (f"DOES: {p['does']}\n    NOT FOR: {'; '.join(p.get('not_for', []))[:200]}\n    NEEDS: {p.get('needs', '')}"
                if p else f"(no card) {it['desc'][:220]}")
        print(f"- {it['kind']:13} {it['name']}{flag}  ({score(it):.2f})\n    {what}"
              + (f"\n    LEDGER: {it['ledger']}" if it.get("ledger") else "") + f"\n    {it['path'].replace(HOME, '~')}")
    if caps: print("\nFALLBACK CHAINS that match this goal (walk them in order on any failure):\n" + "\n\n".join(caps))

# ---------------------------------------------------------------- eval
LEDGER = os.path.join(HOME, ".claude", "skill-audit", "ledger.jsonl")

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

def cmd_eval(a):
    """Replay the ledger: for every (goal, tool) that worked, does `find` on that goal surface the tool?
    The ledger is the only ground truth we have for "the right tool for this goal"."""
    c = cfg(); its, cache, df = load()
    pairs = {}
    for l in open(LEDGER):
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("outcome") in ("worked", "mixed") and r.get("goal") and r.get("skill"):
            pairs[(r["goal"], r["skill"])] = r
    rows, unmatched, ledger_only, memo = [], set(), set(), {}
    for (goal, tool), r in pairs.items():
        t = norm(tool.split(":")[-1])
        # ledger-only items are built FROM these goals, so matching them would grade the test against itself
        hits = [it for it in its if it["kind"] not in ("note", "key") and it.get("src") != "ledger" and len(t) > 3 and
                (norm(it["name"].split(":")[-1].split("/")[-1]) == t)]
        if not hits:
            if not any(norm(it["name"].split(":")[-1].split("/")[-1]) == t for it in its): unmatched.add(tool)
            else: ledger_only.add(tool)
            continue
        if goal not in memo: memo[goal] = search(goal, a.n, its, cache, df, c, a.judge)   # one search per goal
        picked, score, _ = memo[goal]
        best = None
        for it in hits:
            rank = 1 + sum(1 for o in its if o["kind"] == it["kind"] and score(o) > score(it))
            found = any((p["kind"], p["name"]) == (it["kind"], it["name"]) for p in picked)
            if best is None or (found, -rank) > (best[0], -best[1]): best = (found, rank, it)
        rows.append((goal, tool, *best))
    found = sum(1 for r in rows if r[2])
    ranks = sorted(r[3] for r in rows)
    print(f"EVAL ledger replay: {len(rows)} (goal, tool) pairs scored | {len(ledger_only)} ledger-only tools skipped "
          f"(their card is built from these goals) | {len(unmatched)} not in the index")
    print(f"  surfaced by find -n {a.n}: {found}/{len(rows)} = {found / max(1, len(rows)):.0%}"
          f" | rank within its kind: median {ranks[len(ranks) // 2] if ranks else '-'}, top-10 {sum(1 for x in ranks if x <= 10)},"
          f" top-20 {sum(1 for x in ranks if x <= 20)} of {len(rows)}")
    if a.show:
        for goal, tool, f, rank, it in sorted(rows, key=lambda r: r[3]):
            print(f"  {'HIT ' if f else 'MISS'} #{rank:<4} {it['kind']:6} {tool:28} <- {goal[:70]}")
        print("  not in index:", ", ".join(sorted(unmatched)))

def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0]); s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("index").set_defaults(fn=cmd_index)
    s.add_parser("health").set_defaults(fn=cmd_health)
    pr = s.add_parser("profile"); pr.add_argument("--limit", type=int, default=0); pr.add_argument("--only", default="")
    pr.add_argument("--workers", type=int, default=2); pr.add_argument("--force", action="store_true")
    pr.set_defaults(fn=cmd_profile)
    f = s.add_parser("find"); f.add_argument("goal"); f.add_argument("-n", type=int, default=120)
    f.add_argument("--named", default=""); f.add_argument("--json", action="store_true")
    f.add_argument("--judge", action="store_true", help="rerank with a Jev-style System One judge (judge_url)"); f.set_defaults(fn=cmd_find)
    e = s.add_parser("eval"); e.add_argument("-n", type=int, default=120); e.add_argument("--show", action="store_true")
    e.add_argument("--judge", action="store_true")
    e.set_defaults(fn=cmd_eval)
    a = p.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
