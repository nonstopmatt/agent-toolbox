#!/usr/bin/env python3
"""build_inventory.py - inventory of every Claude Code resource on this Mac.

Scans skills, plugin skills, sub-skills, agents, commands, MCP servers, claude.ai
connectors, hooks, API key NAMES, every user-installed CLI, local Ollama models, the user's
own scripts, listening local services, the expert library and EVERY memory note (the
only place tools that are not skills get documented: ComfyUI, Postiz, the scrapers, the
font and SFX libraries), then writes ~/.claude/tool-inventory/inventory.{json,md} and
memory-notes.md. Shared by /tool-audit and /skill-audit.

Nothing here reads the MEMORY.md index: notes are read straight off disk, so an entry
folded into a hub or dropped from the index is still found. Every category is counted a
second way and the result printed as COVERAGE; a mismatch means the scan is missing
something and the number, not the list, is what to look at first.

What only the live session can see (built-in skills, built-in agents, claude-in-chrome,
computer-use) is passed in with --session and remembered between runs.

SECURITY: only NAMES of keys / env vars / servers are read out. Secret values,
MCP args, env blocks and headers are never stored or printed.

Usage:
  build_inventory.py                     rebuild + summary + what changed since last scan
  build_inventory.py --brief             rebuild + compact category -> names map
  build_inventory.py --match "goal" -n 20   rebuild + ranked candidates for a goal
  build_inventory.py --show a,b,c        full descriptions for named items
  build_inventory.py --cwd /path/to/project   also scan that project's .claude/
  build_inventory.py --session "dataviz,agent:Explore,mcp:computer-use"
                                         names visible in the live session; whatever is
                                         not on disk is recorded as session-only
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
OUT_DIR = os.path.join(CLAUDE, "tool-inventory")
OUT_JSON = os.path.join(OUT_DIR, "inventory.json")
OUT_MD = os.path.join(OUT_DIR, "inventory.md")
SEEN = os.path.join(OUT_DIR, "first_seen.json")
NEW_DAYS = 3
# Machine-specific lookups live outside the repo: {"key_dirs": ["~/.config/<dir>"],
# "extra_pipelines": {"label": "~/path/to/helper"}, "expert_library": "~/<dir>"}.
# Missing file or key = that lookup is skipped.
LOCAL_CFG = os.path.join(HOME, ".config", "toolbox", "tool-audit.json")


def local_cfg():
    try:
        with open(LOCAL_CFG) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


EXPERT_LIB_LABEL = local_cfg().get("expert_library")
EXPERT_LIB = os.path.expanduser(EXPERT_LIB_LABEL) if EXPERT_LIB_LABEL else None
PRUNE = {"node_modules", ".git", ".venv", "venv", "__pycache__", ".trash", "dist", "build"}
NOTES_MD = os.path.join(OUT_DIR, "memory-notes.md")
SESSION_ONLY = os.path.join(OUT_DIR, "session_only.json")
MEMORY_DIRS = os.path.join(CLAUDE, "projects", "*", "memory")
USER_BIN_DIRS = [".local/bin", ".bun/bin", ".cargo/bin", ".docker/bin", "go/bin", ".npm-global/bin"]
SYSTEM_BIN_DIRS = ["/opt/homebrew/bin", "/usr/local/bin"]
NOT_ON_DISK = ("memory-note", "session-skill", "session-agent", "session-mcp")
DECLARED_TOKENS = set()   # launch names of declared MCP servers: compared against `ps`, never stored or printed

# item-side rules: substrings in name+description -> category
CATEGORY_RULES = {
    "advice-strategy": ["expert", "advice", "strategy", "office-hours", "ceo", "brainstorm", "ideate",
                        "grill", "market-research", "pov", "spec", "founder", "pricing"],
    "marketing-copy": ["copy", "marketing", "email", "lead-magnet", "blog", "seo", "humaniz", "psycholog",
                       "signup", "onboarding", "content", "headline", "newsletter"],
    "sales-outreach": ["lead", "outreach", "cold", "prospect", "crm", "instantly", "bad-to-good",
                       "redesign", "pitch", "sales"],
    "research-scrape": ["research", "scrape", "firecrawl", "crawl", "search", "browse", "transcript",
                        "video-insight", "competitive", "intel"],
    "design-ui": ["design", " ui", "ux", "layout", "typeset", "typograph", "color", "animat", "polish",
                  "critique", "taste", "impeccable", "shadcn", "tailwind", "figma", "framer", "pencil",
                  "mobbin", "spline", "logo", "interface", "responsive", "frontend"],
    "media-video-image": ["video", "remotion", "image", "fal-ai", "footage", "motion", "resolve",
                          "trailer", "photoroom", "higgsfield", "glif", "audio", "thumbnail"],
    "code-quality": ["review", "debug", "tdd", "test", "security", "semgrep", "codeql", "simplify",
                     "refactor", "diagnos", "bug", "sarif", "codebase"],
    "ship-deploy": ["ship", "deploy", "land-and", "canary", "qa", "benchmark", "vercel", "git",
                    "commit", "merge", "worktree", "release"],
    "docs-files": ["pdf", "docx", "pptx", "xlsx", "document", "diagram", "slides", "spreadsheet", "dataviz",
                   "chart", "artifact"],
    "agent-system": ["skill", "plugin", "hook", "config", "memory", "context-", "loop", "schedule",
                     "workflow", "mcp", "agent", "keybinding", "permission", "claude-api"],
    "ops-comms": ["gmail", "calendar", "google drive", "google-drive", "inbox", "morning"],
    "finance-trading": ["quiver", "co-invest", "trading", "portfolio", "stock"],
}

# goal-side triggers: words in the user's goal -> categories worth boosting
GOAL_TRIGGERS = {
    "sales-outreach": ["client", "clients", "customer", "lead", "leads", "prospect", "outreach", "cold",
                       "call", "calls", "close", "deal", "pipeline", "sell", "sales", "booking", "pitch"],
    "marketing-copy": ["marketing", "copy", "headline", "landing", "email", "newsletter", "content", "post",
                       "linkedin", "seo", "blog", "ads", "campaign", "launch", "audience", "brand", "hook"],
    "advice-strategy": ["idea", "strategy", "pricing", "price", "offer", "decide", "decision", "plan",
                        "business", "startup", "validate", "positioning", "niche", "grow", "growth",
                        "revenue", "money", "advice", "should", "opener", "script", "objection", "objections",
                        "framework", "tactic", "tactics", "negotiate", "closing"],
    "design-ui": ["website", "site", "page", "design", "layout", "hero", "font", "typography", "color",
                  "mockup", "redesign", "mobile", "responsive", "animation", "logo", "homepage"],
    "media-video-image": ["video", "edit", "clip", "clips", "reel", "thumbnail", "podcast", "episode",
                          "image", "photo", "render", "motion", "trailer", "footage", "audio"],
    "research-scrape": ["research", "find", "scrape", "competitor", "competitors", "market", "transcript",
                        "youtube", "search", "investigate", "compare"],
    "code-quality": ["bug", "error", "fix", "broken", "test", "tests", "review", "refactor", "security",
                     "slow", "crash", "failing"],
    "ship-deploy": ["deploy", "ship", "release", "merge", "production", "vercel", "live", "push"],
    "docs-files": ["pdf", "doc", "deck", "slides", "spreadsheet", "report", "proposal", "invoice", "chart"],
    "agent-system": ["skill", "skills", "plugin", "plugins", "hook", "mcp", "automate", "automation",
                     "workflow", "agent", "agents", "memory", "claude", "connector"],
    "ops-comms": ["email", "inbox", "gmail", "calendar", "meeting", "schedule", "drive"],
    "finance-trading": ["stock", "stocks", "trade", "invest", "portfolio", "crypto"],
}

STOPWORDS = set("the and for with that this from have what when your you are can will want need into "
                "about make help get use using how our out not but all any its it's let's lets them they "
                "then than also just like some more most very plan planned planning direction after before "
                "thinking whether quick ready figure each every week today tomorrow going really thing things".split())

NOTABLE_CLIS = ["gh", "git", "vercel", "node", "npm", "npx", "bun", "uv", "python3", "python3.12", "ffmpeg",
                "yt-dlp", "jq", "rg", "firecrawl", "supabase", "stripe", "wrangler", "docker", "codex",
                "gemini", "claude", "pandoc", "magick", "exiftool", "sqlite3", "curl"]


def read(path, limit=200_000):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return ""


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def parse_frontmatter(text):
    """Minimal YAML frontmatter reader (no PyYAML on the system python)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data, key, buf = {}, None, []

    def flush():
        if key is not None:
            val = " ".join(s for s in buf if s).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            data[key] = val

    for line in text[3:end].strip("\n").split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            flush()
            key, val = m.group(1), m.group(2).strip()
            buf = [] if val in ("|", ">", "|-", ">-", "|+", ">+") else [val]
        elif key is not None:
            buf.append(line.strip())
    flush()
    return data


def categorize(name, desc):
    """Name hit counts 3, each hit in the first 260 chars of the description counts 1. Keep the best 2."""
    name_l, head = name.lower(), " " + desc.lower()[:260] + " "
    scores = {}
    for c, keys in CATEGORY_RULES.items():
        sc = 0
        for k in keys:
            k = k.strip()
            if re.search(r"(?<![a-z])" + re.escape(k), name_l):
                sc += 3
            if re.search(r"(?<![a-z])" + re.escape(k), head):
                sc += 1
        if sc >= 2:
            scores[c] = sc
    best = sorted(scores, key=lambda c: -scores[c])[:2]
    return best or ["other"]


def skill_item(skill_md, kind, source, name_prefix=""):
    """Claude Code invokes a skill by its FOLDER name, so that is the name we report."""
    fm = parse_frontmatter(read(skill_md, 8000))
    folder = os.path.basename(os.path.dirname(skill_md))
    name = name_prefix + folder
    desc = re.sub(r"\s+", " ", fm.get("description", "")).strip()
    it = {"kind": kind, "name": name, "description": desc, "source": source,
          "path": skill_md.replace(HOME, "~"), "categories": categorize(name, desc)}
    if fm.get("name") and fm["name"] != folder:
        it["alias"] = fm["name"]
    if str(fm.get("disable-model-invocation", "")).lower() == "true":
        it["user_only"] = True  # The user can type /name, Claude cannot invoke it
    return it


def find_skill_mds(root, max_depth):
    """Yield SKILL.md paths under root, following symlinks, pruning junk, deduped by realpath."""
    seen = set()
    root = root.rstrip("/")
    base_depth = root.count(os.sep)
    for cur, dirs, files in os.walk(root, followlinks=True):
        dirs[:] = [d for d in dirs if d not in PRUNE and not d.startswith(".")]
        if cur.count(os.sep) - base_depth >= max_depth:
            dirs[:] = []
        if "SKILL.md" in files:
            p = os.path.join(cur, "SKILL.md")
            rp = os.path.realpath(p)
            if rp not in seen:
                seen.add(rp)
                yield p


def scan_personal_skills(items):
    root = os.path.join(CLAUDE, "skills")
    if not os.path.isdir(root):
        return
    top_real = set()
    for entry in sorted(os.listdir(root)):
        d = os.path.join(root, entry)
        md = os.path.join(d, "SKILL.md")
        if os.path.isfile(md):
            top_real.add(os.path.realpath(md))
            items.append(skill_item(md, "skill", "personal"))
    # sub-skills: SKILL.md files nested inside a skill folder (reachable through their parent)
    for entry in sorted(os.listdir(root)):
        d = os.path.join(root, entry)
        if not os.path.isdir(d) or entry.startswith("."):
            continue
        for md in find_skill_mds(d, 4):
            if os.path.realpath(md) in top_real:
                continue
            top_real.add(os.path.realpath(md))
            kind = "synced-skill" if entry == "synced" else "sub-skill"
            it = skill_item(md, kind, "claude.ai sync" if entry == "synced" else "inside " + entry,
                            name_prefix="anthropic-skills:" if entry == "synced" else "")
            it["parent"] = entry
            items.append(it)


def md_items(folder, kind, source, items, prefix="", enabled=None):
    if os.path.isfile(folder):
        walk = [(os.path.dirname(folder), [], [os.path.basename(folder)])]
    elif os.path.isdir(folder):
        walk = os.walk(folder)
    else:
        return
    for cur, dirs, files in walk:
        dirs[:] = [d for d in dirs if d not in PRUNE]
        for f in sorted(files):
            if f.endswith(".md") and f.upper() not in ("README.MD", "CLAUDE.MD"):
                p = os.path.join(cur, f)
                fm = parse_frontmatter(read(p, 8000))
                name = prefix + (fm.get("name") or f[:-3])
                desc = re.sub(r"\s+", " ", fm.get("description", "")).strip()
                it = {"kind": kind, "name": name, "description": desc, "source": source,
                      "path": p.replace(HOME, "~"), "categories": categorize(name, desc)}
                if enabled is not None:
                    it["enabled"] = enabled
                items.append(it)


def mcp_entry(name, cfg, scope):
    """Names + transport only. Never args/env/headers (they can hold tokens)."""
    cfg = cfg if isinstance(cfg, dict) else {}
    for v in [str(cfg.get("command", ""))] + [a for a in (cfg.get("args") or []) if isinstance(a, str)]:
        if v and not v.startswith("-") and "=" not in v and len(v) < 120:   # package or script names only
            v = re.sub(r"(?<=.)@[^@/]+$", "", v.rstrip("/")).lower()
            DECLARED_TOKENS.update({v, os.path.basename(v)})
    if cfg.get("url"):
        host = re.sub(r"^https?://([^/]+).*$", r"\1", str(cfg["url"]))
        transport = "remote: " + host
    else:
        transport = "local: " + os.path.basename(str(cfg.get("command", "?")))
    return {"kind": "mcp-server", "name": name, "description": transport, "source": scope,
            "path": "", "categories": categorize(name, "")}


def manifest_paths(root, manifest, key, default):
    """The default folder plus whatever plugin.json names under `key` (a string or a list)."""
    v = manifest.get(key)
    rels = [default] + ([v] if isinstance(v, str) else [x for x in v if isinstance(x, str)] if isinstance(v, list) else [])
    out, seen = [], set()
    for r in rels:
        p = os.path.normpath(os.path.join(root, r))
        if p.startswith(os.path.normpath(root)) and os.path.exists(p) and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def scan_plugins(items, plugins_meta):
    installed = load_json(os.path.join(CLAUDE, "plugins", "installed_plugins.json")).get("plugins", {})
    enabled = load_json(os.path.join(CLAUDE, "settings.json")).get("enabledPlugins", {})
    for pid, installs in sorted(installed.items()):
        inst = installs[0] if isinstance(installs, list) and installs else installs
        path = (inst or {}).get("installPath", "")
        on = bool(enabled.get(pid, False))
        short = pid.split("@")[0]
        manifest = {}
        for cand in (".claude-plugin/plugin.json", "plugin.json"):
            manifest = load_json(os.path.join(path, cand))
            if manifest:
                break
        hooks = manifest.get("hooks") if isinstance(manifest.get("hooks"), dict) else {}
        if not hooks:
            hooks = load_json(os.path.join(path, "hooks", "hooks.json")).get("hooks", {})
        plugins_meta.append({"id": pid, "enabled": on, "version": (inst or {}).get("version", ""),
                             "description": manifest.get("description", ""),
                             "hook_events": sorted(hooks.keys()) if isinstance(hooks, dict) else []})
        if not os.path.isdir(path):
            continue
        src = "plugin " + short + ("" if on else " (DISABLED)")
        seen_md = set()
        for sd in manifest_paths(path, manifest, "skills", "skills"):
            direct = os.path.join(sd, "SKILL.md")
            for md in ([direct] if os.path.isfile(direct) else find_skill_mds(sd, 3) if os.path.isdir(sd) else []):
                if os.path.realpath(md) in seen_md:
                    continue
                seen_md.add(os.path.realpath(md))
                it = skill_item(md, "plugin-skill", src, name_prefix=short + ":")
                it["enabled"] = on
                items.append(it)
        for cd in manifest_paths(path, manifest, "commands", "commands"):
            md_items(cd, "plugin-command", src, items, prefix=short + ":", enabled=on)
        for ad in manifest_paths(path, manifest, "agents", "agents"):
            md_items(ad, "plugin-agent", src, items, prefix=short + ":", enabled=on)
        servers = {}
        ms = manifest.get("mcpServers")
        if isinstance(ms, dict):
            servers.update(ms)
        elif isinstance(ms, str):          # a path to a JSON file, which a dict-only reader silently skips
            j = load_json(os.path.join(path, ms))
            servers.update((j.get("mcpServers") if isinstance(j.get("mcpServers"), dict) else j) or {})
        servers.update(load_json(os.path.join(path, ".mcp.json")).get("mcpServers", {}) or {})
        for name, cfg in servers.items():
            e = mcp_entry(short + ":" + name, cfg, src)
            e["enabled"] = on
            items.append(e)


def scan_mcp(items, cwd):
    cj = load_json(os.path.join(HOME, ".claude.json"))
    for name, cfg in (cj.get("mcpServers") or {}).items():
        items.append(mcp_entry(name, cfg, "user scope"))
    for proj, pdata in (cj.get("projects") or {}).items():
        for name, cfg in ((pdata or {}).get("mcpServers") or {}).items():
            items.append(mcp_entry(name, cfg, "project " + proj.replace(HOME, "~")))
    for name in cj.get("claudeAiMcpEverConnected") or []:
        items.append({"kind": "connector", "name": str(name), "description": "claude.ai connector (account-level)",
                      "source": "claude.ai", "path": "", "categories": categorize(str(name), "")})
    if cwd:
        for name, cfg in (load_json(os.path.join(cwd, ".mcp.json")).get("mcpServers") or {}).items():
            items.append(mcp_entry(name, cfg, "project .mcp.json"))


def scan_hooks():
    out = []
    hooks = load_json(os.path.join(CLAUDE, "settings.json")).get("hooks", {}) or {}
    for event, groups in hooks.items():
        for g in groups or []:
            for h in g.get("hooks", []):
                cmd = str(h.get("command") or h.get("prompt") or h.get("url") or "")
                out.append({"event": event, "what": os.path.basename(cmd.split(" ")[0])[:60]})
    return out


def scan_key_names():
    """Key / env-var NAMES only."""
    keys = {}
    for kd in local_cfg().get("key_dirs", []):
        d = os.path.expanduser(kd)
        if os.path.isdir(d):
            keys[kd] = sorted(f for f in os.listdir(d) if ".bak" not in f and not f.startswith("."))
    try:
        entries = sorted(os.listdir(HOME))
    except OSError:
        entries = []
    for entry in entries:
        d = os.path.join(HOME, entry)
        if entry.startswith(".") or not os.path.isdir(d):
            continue
        for envname in (".env", ".env.local"):
            p = os.path.join(d, envname)
            if os.path.isfile(p):
                names = sorted(set(re.findall(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]{2,})\s*=", read(p), re.M)))
                if names:
                    keys["~/" + entry + "/" + envname] = names
    return keys


def path_dirs():
    """The agent shell's PATH is shorter than the user's (no ~/.docker/bin, no Homebrew), so ask a
    login shell once and add the usual user bin folders. Without this `docker` reads as missing."""
    try:
        out = subprocess.run(["zsh", "-lc", "print -r -- $PATH"], capture_output=True, text=True,
                             timeout=20).stdout.strip().splitlines()
        login = out[-1] if out else ""
    except Exception:
        login = ""
    parts = (os.environ.get("PATH", "") + os.pathsep + login).split(os.pathsep)
    parts += [os.path.join(HOME, d) for d in USER_BIN_DIRS] + SYSTEM_BIN_DIRS
    seen, dirs = set(), []
    for p in parts:
        if p and p not in seen and os.path.isdir(p):
            seen.add(p)
            dirs.append(p)
    return dirs


def scan_clis(dirs):
    path = os.pathsep.join(dirs)
    return {c: bool(shutil.which(c, path=path)) for c in NOTABLE_CLIS}


def scan_user_clis(dirs):
    """Every executable in a bin folder the user (not macOS) populates. A fixed list of 27 names
    cannot see ollama, solvent, agent-reach or whatever was installed yesterday."""
    out = {}
    for d in dirs:
        if not (d.startswith(HOME) or d in SYSTEM_BIN_DIRS):
            continue
        try:
            names = sorted(f for f in os.listdir(d) if not f.startswith(".")
                           and os.path.isfile(os.path.join(d, f)) and os.access(os.path.join(d, f), os.X_OK))
        except OSError:
            names = []
        if names:
            out[d.replace(HOME, "~")] = names
    return out


def scan_ollama():
    """Local models, read off disk so it works whether or not the server is up."""
    lib = os.path.join(HOME, ".ollama", "models", "manifests", "registry.ollama.ai", "library")
    out = []
    if os.path.isdir(lib):
        for m in sorted(os.listdir(lib)):
            tags = sorted(t for t in os.listdir(os.path.join(lib, m)) if not t.startswith(".")) if os.path.isdir(os.path.join(lib, m)) else []
            out += [m + ":" + t for t in tags] or [m]
    return out


def scan_scripts():
    """the user's own helper scripts: name + the first line that says what it does."""
    out, root = [], os.path.join(CLAUDE, "scripts")
    if not os.path.isdir(root):
        return out
    for f in sorted(os.listdir(root)):
        p = os.path.join(root, f)
        if not os.path.isfile(p) or f.startswith("."):
            continue
        what = ""
        for line in read(p, 1500).split("\n")[:14]:
            t = line.strip().strip('"').strip("'").lstrip("#").strip()
            if t and not t.startswith("!") and not t.startswith(("import ", "from ", "set -")):
                what = t
                break
        out.append({"name": "~/.claude/scripts/" + f, "what": what[:140]})
    return out


def scan_memory_notes(items):
    """Every memory note in every project memory folder, straight off disk. Returns files seen."""
    seen_files = 0
    for d in sorted(glob.glob(MEMORY_DIRS)):
        proj = os.path.basename(os.path.dirname(d))
        if "tmp" in proj:                      # scratchpad sessions
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.md"))):
            stem = os.path.basename(p)[:-3]
            if stem == "MEMORY":
                continue
            seen_files += 1
            text = read(p, 6000)
            fm = parse_frontmatter(text)
            m = re.search(r"(?<![a-z_])type:\s*([a-z]+)", fm.get("metadata", "") + " " + ("type: " + fm["type"] if fm.get("type") else ""))
            mtype = m.group(1) if m else (stem.split("_")[0] if stem.split("_")[0] in ("reference", "project", "feedback", "user") else "untyped")
            desc = re.sub(r"\s+", " ", fm.get("description", "")).strip()
            if not desc:                       # older notes have no frontmatter: first real line of the body
                body = text.split("\n---", 2)[-1] if text.startswith("---") else text
                desc = next((re.sub(r"\s+", " ", l).strip("# ").strip() for l in body.split("\n") if l.strip() and not l.startswith("---")), "")
            name = stem if proj == "-Users-matt" else proj.strip("-").replace("Users-matt-", "") + "/" + stem
            it = {"kind": "memory-note", "name": name, "description": desc, "source": "memory (" + mtype + ")",
                  "path": p.replace(HOME, "~"), "categories": categorize(stem.replace("_", "-"), desc), "mtype": mtype}
            if fm.get("name") and fm["name"] != stem:
                it["alias"] = fm["name"]
            items.append(it)
    return seen_files


def scan_listening():
    """What is answering on a local port right now (proc:port). Ephemeral browser ports dropped."""
    try:
        out = subprocess.run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return []
    found = set()
    for line in out.splitlines()[1:]:
        f = line.split()
        if len(f) < 9:
            continue
        port = f[8].rsplit(":", 1)[-1]
        if port.isdigit() and int(port) < 49152 and f[0] not in ("ControlCe", "CommCente", "rapportd", "sharingd"):
            found.add("%s:%s" % (f[0].replace("\\x20", " "), port))
    return sorted(found, key=lambda x: int(x.rsplit(":", 1)[-1]))


GENERIC_LAUNCH = {"npm", "exec", "npx", "node", "python", "python3", "uvx", "uv", "run", "bunx", "bun", "env", "mcp", "serve", "server"}


def launch_tokens(argv):
    """Names that identify WHAT is being launched, generic runner words removed."""
    out = set()
    for v in argv[:5]:
        if not v or v.startswith("-") or "=" in v or len(v) > 160:
            continue
        v = re.sub(r"(?<=.)@[^@/]+$", "", v.rstrip("/")).lower()
        out |= {v, os.path.basename(v)}
    return {t for t in out if t and t not in GENERIC_LAUNCH}


def etime_seconds(e):
    days, _, rest = e.partition("-") if "-" in e else ("0", "", e)
    parts = [int(x) for x in rest.split(":") if x.isdigit()]
    while len(parts) < 3:
        parts.insert(0, 0)
    return int(days) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def scan_undeclared_servers():
    """MCP servers still running that no config declares.

    A stdio MCP server is a direct child of a `claude` process; the user's dev servers hang off
    launchd or a shell, so parentage separates the two cleanly. Observation 0024: an
    uninstalled plugin's server kept running under sessions opened before the uninstall, so
    its tools stayed live while every config said it was gone. Names only, never arguments."""
    try:
        out = subprocess.run(["ps", "-Ao", "pid=,ppid=,etime=,command="], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return []
    rows = [l.split(None, 3) for l in out.splitlines() if len(l.split(None, 3)) == 4]
    rows = [r for r in rows if not r[3].startswith("(")]          # defunct processes print as "(name)"
    exe = {pid: os.path.basename(cmd.split()[0]) for pid, _, _, cmd in rows if cmd.split()}
    declared = {t for t in DECLARED_TOKENS if t not in GENERIC_LAUNCH}
    agg = {}
    for pid, ppid, etime, cmd in rows:
        argv = cmd.split()
        if exe.get(ppid) != "claude" or not argv:
            continue
        if os.path.basename(argv[0]) in ("zsh", "bash", "sh", "caffeinate", "claude") or argv[1:2] == ["-e"]:
            continue
        toks = launch_tokens(argv)
        if not toks or toks & declared:
            continue
        name = sorted(toks, key=lambda t: ("/" in t, len(t)))[0]
        a = agg.setdefault(name, {"name": name, "count": 0, "oldest": etime})
        a["count"] += 1
        if etime_seconds(etime) > etime_seconds(a["oldest"]):
            a["oldest"] = etime
    return sorted(agg.values(), key=lambda x: x["name"])


def apply_session(items, session_arg):
    """Skills, agents and servers that exist only inside the live session (built into Claude Code
    or the desktop app) cannot be found on disk. The caller passes the names it can see; whatever
    the disk scan lacks is kept as session-only, and remembered so a later run still has it."""
    saved = load_json(SESSION_ONLY)
    if session_arg:
        # Compare like with like, among ENABLED items only: a skill called `explore` must not hide
        # the built-in agent `Explore`, nor a disabled plugin's `security-review` the built-in one.
        fam = {"session-skill": ("skill", "plugin-skill", "synced-skill", "command", "plugin-command"),
               "session-agent": ("agent", "plugin-agent"), "session-mcp": ("mcp-server", "connector")}
        live = [i for i in items if i.get("enabled") is not False]
        have_by = {k: {i["name"].lower() for i in live if i["kind"] in kinds} for k, kinds in fam.items()}
        have_by["session-mcp"] |= {n.split(":")[-1] for n in have_by["session-mcp"]}   # plugin servers print as plugin:server
        have = set()
        # A long-running session still lists skills that were retired after it started. Those are
        # gone, not built in, so they must not be recorded as session-only.
        retired = os.path.join(CLAUDE, "skills-retired")
        for pat in (os.path.join(retired, "*", "SKILL.md"), os.path.join(retired, "*", "*", "SKILL.md")):
            have |= {os.path.basename(os.path.dirname(p)).lower() for p in glob.glob(pat)}
        names = []
        for raw in session_arg.split(","):
            raw = raw.strip()
            if not raw:
                continue
            kind, name = ("session-agent", raw[6:]) if raw.lower().startswith("agent:") else \
                         ("session-mcp", raw[4:]) if raw.lower().startswith("mcp:") else ("session-skill", raw)
            if name.lower() not in have_by[kind] and name.lower() not in have:
                names.append({"kind": kind, "name": name})
        saved = {"date": time.strftime("%Y-%m-%d"), "names": names}
        with open(SESSION_ONLY, "w", encoding="utf-8") as f:
            json.dump(saved, f, indent=1)
    for n in saved.get("names", []):
        items.append({"kind": n["kind"], "name": n["name"], "source": "live session only (not on disk)", "path": "",
                      "description": "built into Claude Code or the app; description is in the session's own tool/skill list",
                      "categories": categorize(n["name"], "")})
    return saved.get("date", "")


def coverage(inv, memory_files):
    """Count every category a second way. A scan never says 'I could not see it', it just
    returns a shorter list, so the second count is the only thing that can notice."""
    rows = []

    def row(label, got, disk):
        rows.append({"what": label, "inventory": got, "independent": disk, "ok": got >= disk})

    its = inv["items"]
    root = os.path.join(CLAUDE, "skills")
    disk = sum(1 for e in os.listdir(root) if os.path.isfile(os.path.join(root, e, "SKILL.md"))) if os.path.isdir(root) else 0
    row("personal skills", sum(1 for i in its if i["kind"] == "skill" and i["source"] == "personal"), disk)
    ag = [f for f in glob.glob(os.path.join(CLAUDE, "agents", "**", "*.md"), recursive=True)
          if os.path.basename(f).upper() not in ("README.MD", "CLAUDE.MD")]
    row("personal agents", sum(1 for i in its if i["kind"] == "agent" and i["source"] == "personal"), len(ag))
    row("memory notes", sum(1 for i in its if i["kind"] == "memory-note"), memory_files)
    installed = load_json(os.path.join(CLAUDE, "plugins", "installed_plugins.json")).get("plugins", {})
    row("plugins", len(inv["plugins"]), len(installed))
    cj = load_json(os.path.join(HOME, ".claude.json"))
    row("user-scope MCP servers", sum(1 for i in its if i["kind"] == "mcp-server" and i["source"] == "user scope"),
        len(cj.get("mcpServers") or {}))
    empty = [p["id"] for p in inv["plugins"] if p["enabled"]
             and not any(i["source"].startswith("plugin " + p["id"].split("@")[0]) for i in its) and not p["hook_events"]]
    return {"rows": rows, "ok": all(r["ok"] for r in rows), "enabled_plugins_contributing_nothing": empty}


def scan_expert_library():
    info = {"path": EXPERT_LIB_LABEL or "not configured", "repos": [], "transcripts": 0}
    if not EXPERT_LIB:
        return info
    repos = os.path.join(EXPERT_LIB, "repos")
    if os.path.isdir(repos):
        info["repos"] = sorted(d for d in os.listdir(repos) if os.path.isdir(os.path.join(repos, d)))
    tr = os.path.join(EXPERT_LIB, "transcripts")
    if os.path.isdir(tr):
        info["transcripts"] = len([f for f in os.listdir(tr) if f.endswith(".md")])
    return info


def scan_projects():
    """Top-level project folders in ~ (names only)."""
    out = []
    try:
        entries = sorted(os.listdir(HOME))
    except OSError:
        return out
    for e in entries:
        d = os.path.join(HOME, e)
        if e.startswith(".") or not os.path.isdir(d) or e in ("Library", "Applications", "Movies", "Music", "Pictures", "Public"):
            continue
        marks = [m for m in ("CLAUDE.md", ".git", "package.json", "pyproject.toml", "requirements.txt") if os.path.exists(os.path.join(d, m))]
        if marks:
            out.append({"name": "~/" + e, "has_claude_md": "CLAUDE.md" in marks})
    return out


def scan_pipelines():
    """Local, free pipelines that a PATH check misses."""
    checks = {
        "yt_expert.py (YouTube search + transcripts)": os.path.join(CLAUDE, "skills", "expert-intel", "scripts", "yt_expert.py"),
        "ffmpeg (~/.local/bin)": os.path.join(HOME, ".local", "bin", "ffmpeg"),
        "uv (~/.local/bin)": os.path.join(HOME, ".local", "bin", "uv"),
    }
    checks.update({k: os.path.expanduser(v) for k, v in local_cfg().get("extra_pipelines", {}).items()})
    out = {k: os.path.exists(v) for k, v in checks.items()}
    wp = "/Library/Developer/CommandLineTools/usr/bin/python3"
    ok = False
    if os.path.exists(wp):
        try:
            import subprocess
            ok = subprocess.run([wp, "-c", "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('mlx_whisper') else 1)"],
                                capture_output=True, timeout=10).returncode == 0
        except Exception:
            ok = False
    out["mlx_whisper local transcription (CLT python)"] = ok
    return out


def build(cwd=None, session=""):
    items, plugins_meta = [], []
    DECLARED_TOKENS.clear()
    scan_personal_skills(items)
    scan_plugins(items, plugins_meta)
    md_items(os.path.join(CLAUDE, "agents"), "agent", "personal", items)
    md_items(os.path.join(CLAUDE, "commands"), "command", "personal", items)
    if cwd and os.path.realpath(cwd) != os.path.realpath(HOME):
        proj = os.path.join(cwd, ".claude")
        if os.path.isdir(os.path.join(proj, "skills")):
            for md in find_skill_mds(os.path.join(proj, "skills"), 3):
                items.append(skill_item(md, "skill", "project " + cwd.replace(HOME, "~")))
        md_items(os.path.join(proj, "agents"), "agent", "project", items)
        md_items(os.path.join(proj, "commands"), "command", "project", items)
    scan_mcp(items, cwd)
    memory_files = scan_memory_notes(items)
    session_date = apply_session(items, session)
    best = {}
    for it in items:
        k = ident(it)
        if k not in best or (best[k].get("enabled") is False and it.get("enabled") is not False):
            best[k] = it
    items = list(best.values())
    skill_names = {i["name"] for i in items if i["kind"] == "skill"}
    items = [i for i in items if not (i["kind"] == "command" and i["name"] in skill_names)]
    dirs = path_dirs()
    inv = {"generated": time.strftime("%Y-%m-%d %H:%M"), "items": items, "plugins": plugins_meta,
           "hooks": scan_hooks(), "key_names": scan_key_names(), "clis": scan_clis(dirs),
           "user_clis": scan_user_clis(dirs), "ollama_models": scan_ollama(), "scripts": scan_scripts(),
           "listening": scan_listening(), "undeclared_servers": scan_undeclared_servers(),
           "session_only_as_of": session_date,
           "expert_library": scan_expert_library(),
           "projects": scan_projects(), "pipelines": scan_pipelines()}
    inv["coverage"] = coverage(inv, memory_files)
    return inv


def coverage_lines(inv):
    cov = inv["coverage"]
    bad = [r for r in cov["rows"] if not r["ok"]]
    if bad:
        out = ["COVERAGE MISMATCH - the scan is missing something; check these before trusting any list:"]
        out += ["  %s: inventory %d, independent count %d" % (r["what"], r["inventory"], r["independent"]) for r in bad]
    else:
        out = ["COVERAGE ok - " + ", ".join("%s %d/%d" % (r["what"], r["inventory"], r["independent"]) for r in cov["rows"])]
    if cov["enabled_plugins_contributing_nothing"]:
        out.append("enabled plugins that contributed no item (hooks-only or unread layout): " + ", ".join(cov["enabled_plugins_contributing_nothing"]))
    if not inv.get("session_only_as_of"):
        out.append("SESSION-ONLY NOT CHECKED - built-in skills, built-in agents, claude-in-chrome and computer-use are not on "
                   "disk; rerun with --session \"<every skill, agent:Name and mcp:server you can see>\"")
    else:
        out.append("session-only list as of %s (%d names); pass --session again to refresh it" % (
            inv["session_only_as_of"], sum(1 for i in inv["items"] if i["kind"].startswith("session-"))))
    if inv.get("undeclared_servers"):
        out.append("RUNNING BUT UNDECLARED - MCP servers alive under a claude session that no config declares (an uninstalled "
                   "tool whose old sessions never restarted; do not recommend its tools, tell the user): " +
                   ", ".join("%s x%d, oldest %s" % (u["name"], u["count"], u["oldest"]) for u in inv["undeclared_servers"]))
    return out


def ident(it):
    return it["kind"] + "::" + it["name"]


def diff(prev, cur):
    a = {ident(i) for i in prev.get("items", [])}
    b = {ident(i) for i in cur.get("items", [])}
    return sorted(b - a), sorted(a - b)


def counts(inv):
    """kind -> 'enabled' or 'enabled/total' when some are disabled."""
    tot, on = {}, {}
    for it in inv["items"]:
        tot[it["kind"]] = tot.get(it["kind"], 0) + 1
        if it.get("enabled") is not False:
            on[it["kind"]] = on.get(it["kind"], 0) + 1
    return {k: (str(on.get(k, 0)) if on.get(k, 0) == v else "%d enabled of %d" % (on.get(k, 0), v)) for k, v in tot.items()}


def tags(i):
    t = ""
    if i.get("user_only"):
        t += " [user-only: the user types it, Claude cannot invoke]"
    if i["name"].startswith("buildpartner:"):
        t += " [only when the user names BuildPartner]"
    return t


def track_first_seen(inv):
    """Stable 'new' detection: remember the day each item first appeared. Returns items new in the last NEW_DAYS."""
    seen = load_json(SEEN)
    first_run = not seen
    today = time.strftime("%Y-%m-%d")
    recent = []
    for it in inv["items"]:
        k = ident(it)
        if k not in seen:
            seen[k] = "baseline" if first_run else today
        it["first_seen"] = seen[k]
        if seen[k] != "baseline" and it.get("enabled") is not False and it["kind"] != "sub-skill" \
                and it["kind"] not in NOT_ON_DISK:
            try:
                age = (time.mktime(time.strptime(today, "%Y-%m-%d")) - time.mktime(time.strptime(seen[k], "%Y-%m-%d"))) / 86400
            except ValueError:
                age = 999
            if age <= NEW_DAYS:
                recent.append(it)
    with open(SEEN, "w", encoding="utf-8") as f:
        json.dump(seen, f)
    return recent


def trunc(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def write_md(inv, recent):
    L = ["# Tool inventory", "", "Generated " + inv["generated"] + " by build_inventory.py. Names only, no secrets.", "",
         "How to invoke: skill = `/name` or the Skill tool. agent / plugin-agent = Agent tool with that subagent_type (no slash). "
         "sub-skill = reached through its parent skill. [user-only] = only the user can type it.", ""]
    L.append("**Counts:** " + ", ".join(k + " " + str(v) for k, v in sorted(counts(inv).items())))
    L += [""] + ["**" + c.split(" - ")[0] + "**" + (" - " + c.split(" - ", 1)[1] if " - " in c else "") for c in coverage_lines(inv)]
    if recent:
        L += ["", "**New in the last %d days:** " % NEW_DAYS + ", ".join(i["name"] for i in recent[:80])]
    L += ["", "## Plugins"]
    for p in inv["plugins"]:
        L.append("- %s %s [%s] hooks: %s" % (p["id"], p["version"], "on" if p["enabled"] else "OFF",
                                             ", ".join(p["hook_events"]) or "none"))
    order = ["skill", "plugin-skill", "synced-skill", "agent", "plugin-agent", "command", "plugin-command",
             "mcp-server", "connector", "sub-skill"]
    for kind in order:
        group = [i for i in inv["items"] if i["kind"] == kind and i.get("enabled") is not False]
        if not group:
            continue
        L += ["", "## " + kind + " (" + str(len(group)) + ")"]
        if kind == "sub-skill":
            parents = {}
            for i in group:
                parents.setdefault(i.get("parent", "?"), []).append(i["name"])
            for par, names in sorted(parents.items()):
                L.append("- **%s** (%d): %s" % (par, len(names), trunc(", ".join(sorted(names)), 700)))
            continue
        for i in sorted(group, key=lambda x: x["name"].lower()):
            L.append("- `%s`%s [%s] %s" % (i["name"], tags(i), ",".join(i["categories"]), trunc(i["description"], 130)))
    off = {}
    for i in inv["items"]:
        if i.get("enabled") is False:
            off.setdefault(i["source"], []).append(i["name"].split(":", 1)[-1])
    if off:
        L += ["", "## Installed but DISABLED (names only; enable the plugin to use)"]
        for src, names in sorted(off.items()):
            L.append("- **%s** (%d): %s" % (src, len(names), trunc(", ".join(sorted(set(names))), 1800)))
        L.append("- full list with descriptions: `build_inventory.py --disabled <plugin-name>`")
    L += ["", "## Hooks (settings.json)"] + ["- %s -> %s" % (h["event"], h["what"]) for h in inv["hooks"]]
    L += ["", "## API key / env var NAMES (values never read out)"]
    for where, names in inv["key_names"].items():
        for k in range(0, len(names), 60):      # a Read truncates lines over 2000 characters; chunk long name lists
            L.append("- %s%s: %s" % (where, "" if k == 0 else " (cont.)", ", ".join(names[k:k + 60])))
    L += ["", "## CLIs", "- on PATH (login shell + user bin folders): " + ", ".join(c for c, ok in inv["clis"].items() if ok),
          "- missing: " + ", ".join(c for c, ok in inv["clis"].items() if not ok)]
    L += ["", "## Every user-installed CLI, by folder"] + ["- %s (%d): %s" % (d, len(n), ", ".join(n)) for d, n in inv["user_clis"].items()]
    L += ["", "## Local LLMs (Ollama, on disk)", "- " + (", ".join(inv["ollama_models"]) or "none")]
    L += ["", "## The user's scripts (~/.claude/scripts)"] + ["- `%s` %s" % (x["name"], x["what"]) for x in inv["scripts"]]
    L += ["", "## Listening on a local port right now (process:port)", "- " + (", ".join(inv["listening"]) or "nothing, or lsof unavailable")]
    so = [i for i in inv["items"] if i["kind"].startswith("session-")]
    L += ["", "## Session-only: built into Claude Code or the app, not on disk (%d, as of %s)" % (len(so), inv.get("session_only_as_of") or "never checked"),
          "- " + (", ".join("`%s`%s" % (i["name"], {"session-agent": " (agent)", "session-mcp": " (server)"}.get(i["kind"], "")) for i in so) or "not checked yet: pass --session")]
    notes = [i for i in inv["items"] if i["kind"] == "memory-note"]
    bytype = {}
    for i in notes:
        bytype[i["mtype"]] = bytype.get(i["mtype"], 0) + 1
    L += ["", "## Memory notes (%d): %s" % (len(notes), ", ".join("%s %d" % kv for kv in sorted(bytype.items()))),
          "- full list, one line each, in `~/.claude/tool-inventory/memory-notes.md`. Read its reference and project sections: they are the "
          "only record of local tools that are not skills (ComfyUI, Postiz, scrapers, font and SFX libraries, API limits)."]
    L += ["", "## Local pipelines (free, not on PATH)"] + ["- %s: %s" % (k, "ready" if ok else "MISSING") for k, ok in inv["pipelines"].items()]
    L += ["", "## Local projects in ~ (* = has its own CLAUDE.md)",
          "- " + ", ".join(p["name"] + ("*" if p["has_claude_md"] else "") for p in inv["projects"])]
    el = inv["expert_library"]
    L += ["", "## Expert library (%s)" % el["path"],
          "- %d repos, %d cached transcripts" % (len(el["repos"]), el["transcripts"]),
          "- repos: " + (", ".join(el["repos"]) or "none yet")]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    N = ["# Memory notes", "", "Generated " + inv["generated"] + ". Every note in every project memory folder, read off disk "
         "(the MEMORY.md index is not consulted, so folded or unindexed notes are here too). `name` - what it says.", ""]
    for mtype, title in (("reference", "Reference: tools, APIs, pipelines, libraries, limits"), ("project", "Projects: what exists and where"),
                         ("feedback", "Feedback: standing rules"), ("user", "User"), ("untyped", "Untyped")):
        group = sorted((i for i in notes if i["mtype"] == mtype), key=lambda x: x["name"].lower())
        if group:
            N += ["## %s (%d)" % (title, len(group))] + ["- `%s` - %s" % (i["name"], trunc(i["description"], 170)) for i in group] + [""]
    with open(NOTES_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(N) + "\n")


def print_brief(inv):
    invocable = [i for i in inv["items"] if i["kind"] in ("skill", "plugin-skill", "synced-skill", "agent",
                                                          "plugin-agent", "command", "plugin-command")
                 and i.get("enabled") is not False]
    bycat = {}
    for i in invocable:
        for c in i["categories"]:
            bycat.setdefault(c, []).append(i["name"])
    print("## Category map (%d invocable skills/agents/commands)" % len(invocable))
    for c in sorted(bycat):
        print("- %s (%d): %s" % (c, len(bycat[c]), ", ".join(sorted(set(bycat[c])))))
    servers = sorted({i["name"] for i in inv["items"] if i["kind"] in ("mcp-server", "connector")
                      and i.get("enabled") is not False})
    print("- MCP servers + connectors (%d): %s" % (len(servers), ", ".join(servers)))


def print_match(inv, goal, n):
    words = [w for w in re.findall(r"[a-z][a-z0-9-]{2,}", goal.lower()) if w not in STOPWORDS]
    wset = set(words)
    goal_cats = {c for c, trig in GOAL_TRIGGERS.items() if wset & set(trig)}
    scored, notes = [], []
    # rarity: 'comfyui' appears in two items and 'podcast' in sixty, so the rare word is what the
    # goal is about. Used for notes only, where one specific local tool must not be buried.
    df = dict.fromkeys(wset, 0)
    for i in inv["items"]:
        text = (i["name"] + " " + i["description"]).lower()
        for w in df:
            if w in text:
                df[w] += 1
    rare = {w: 1.0 + 3.0 * (1.0 - min(n, 40) / 40.0) for w, n in df.items()}
    for i in inv["items"]:
        if i.get("enabled") is False or i["kind"] == "sub-skill":
            continue
        name_l, desc_l = i["name"].lower(), i["description"].lower()
        if i["kind"] == "memory-note":
            ns = sum(rare[w] * (3 if w in name_l else 1 if w in desc_l else 0) for w in wset)
            if ns:
                notes.append((ns, i))
            continue
        s = sum(3 for w in wset if w in name_l) + min(4, sum(1 for w in wset if w in desc_l))
        s += 2 * len(goal_cats & set(i["categories"]))
        if i["name"].startswith("buildpartner:"):
            s -= 4  # only when the user names it; expert-intel is the default
        if s:
            scored.append((s, i))
    scored.sort(key=lambda t: (-t[0], t[1]["name"]))
    notes.sort(key=lambda t: (-t[0], t[1]["name"]))
    print("## Candidates for: " + trunc(goal, 120))
    print("(goal categories: %s) keyword pre-filter only, judge relevance yourself" % (", ".join(sorted(goal_cats)) or "none"))
    for s, i in scored[:n]:
        print("- `%s` (%s, score %d)%s %s" % (i["name"], i["kind"], s, tags(i), trunc(i["description"], 200)))
    if not scored:
        print("- no keyword matches; use the category map")
    print("## Memory notes for: " + trunc(goal, 120) + " (local tools, limits and rules that are not skills; read the file before relying on it)")
    for s, i in notes[:max(5, n // 2)]:
        print("- `%s` (%s, score %d) %s" % (i["name"], i["source"], s, trunc(i["description"], 200)))
    if not notes:
        print("- none matched by keyword; memory-notes.md has the full list")


def print_status(inv):
    servers = sorted({i["name"] for i in inv["items"] if i["kind"] in ("mcp-server", "connector") and i.get("enabled") is not False})
    keys = sorted({n for names in inv["key_names"].values() for n in names})
    print("## On hand")
    print("- MCP servers + connectors (file scan; live connection state is in your session): " + ", ".join(servers))
    print("- API key / env NAMES: " + trunc(", ".join(keys), 700))
    print("- CLIs: " + ", ".join(c for c, ok in inv["clis"].items() if ok))
    print("- every user-installed CLI: " + trunc(", ".join(sorted({n for names in inv["user_clis"].values() for n in names})), 900))
    print("- local LLMs (Ollama): " + (", ".join(inv["ollama_models"]) or "none"))
    print("- scripts: " + ", ".join(os.path.basename(x["name"]) for x in inv["scripts"]))
    print("- listening now: " + trunc(", ".join(inv["listening"]), 500))
    print("- local pipelines: " + ", ".join(k for k, ok in inv["pipelines"].items() if ok))
    el = inv["expert_library"]
    print("- expert library: %d repos, %d transcripts (%s)" % (len(el["repos"]), el["transcripts"], el["path"]))


def print_disabled(inv, plugin):
    for i in sorted(inv["items"], key=lambda x: x["name"]):
        if i.get("enabled") is False and plugin.lower() in i["source"].lower():
            print("- `%s` (%s) %s" % (i["name"], i["kind"], trunc(i["description"], 200)))


def print_show(inv, names):
    want = {n.strip().lower() for n in names.split(",") if n.strip()}
    for i in inv["items"]:
        if i["name"].lower() in want or i["name"].lower().split(":")[-1] in want:
            print("### %s (%s, %s)\n%s\npath: %s\n" % (i["name"], i["kind"], i["source"],
                                                       i["description"] or "(no description)", i["path"]))


def main():
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped into head
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--match", action="append", default=[], help="a goal; repeat once per sub-goal")
    ap.add_argument("--status", action="store_true", help="compact list of servers, key names, CLIs, pipelines")
    ap.add_argument("--disabled", default="", help="list a disabled plugin's items with descriptions")
    ap.add_argument("-n", type=int, default=20)
    ap.add_argument("--show", default="")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--session", default="", help="comma list of names visible in the live session: skills plain, "
                                                  "agents as agent:Name, servers as mcp:name")
    a = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    inv = build(a.cwd, a.session)
    recent = track_first_seen(inv)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=1)
    write_md(inv, recent)

    if a.show:
        print_show(inv, a.show)
        return
    if a.disabled:
        print_disabled(inv, a.disabled)
        return
    print("Inventory %s | %s" % (inv["generated"], ", ".join(k + " " + str(v) for k, v in sorted(counts(inv).items()))))
    for line in coverage_lines(inv):
        print(line)
    if recent:
        print("NEW in the last %d days (%d): %s" % (NEW_DAYS, len(recent), trunc(", ".join(i["name"] for i in recent), 900)))
    if a.brief:
        print_brief(inv)
    for goal in a.match:
        print_match(inv, goal, a.n)
    if a.status:
        print_status(inv)
    if not (a.brief or a.match or a.status):
        print("Full report: " + OUT_MD.replace(HOME, "~") + " + " + NOTES_MD.replace(HOME, "~"))


if __name__ == "__main__":
    sys.exit(main())
