#!/usr/bin/env bash
# Generate ~/toolbox/TOOLS-MEMORY.md and ~/toolbox/catalog/<category>.md (no AI).
set -euo pipefail
TB="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$TB" <<'PY'
import json, re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TB = Path(sys.argv[1])
CATALOG = TB / "catalog"
CATALOG.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    "web-design", "frontend-code", "backend-data", "marketing-copy",
    "social-content", "video-audio", "research", "security-review",
    "memory-context", "agent-orchestration", "business-ops", "misc",
]

RULES = [
    ("web-design", r"design|figma|css|tailwind|ui\b|ux\b|layout|typography|color|brand|wireframe|html|stylesheet|shadcn|daisy"
                   r"|accessib|section 508|wcag|canva|poster|deck|slide|mockup|theme|icon|logo|polish|alignment|spacing"),
    ("frontend-code", r"react|next\.?js|vue|svelte|frontend|component|typescript|javascript|tsx|jsx|vite|webpack|browser|dom"
                      r"|three\.?js|webgl|shader|playwright|cypress|chrome.?devtools|swiftui|swift\b|hand.?tracking|gesture|flutter|mobile app|ios\b|xcode"
                      r"|prototyp|realtime collab|websocket|animation|animate|motion"),
    ("backend-data", r"backend|api\b|database|sql|postgres|sqlite|mongo|redis|server|fastapi|django|rails|graphql|prisma|supabase|auth"
                     r"|network|cisco|juniper|firmware|embedded|rtos|esp32|php|laravel|filament|drupal|wordpress|cms\b"
                     r"|rust|kubernetes|terraform|devops|sre\b|site reliability|slo\b|platform engineer|airtable|firebase"
                     r"|vercel|gitlab|github|sentry|datadog|schema|migration|data pipeline|etl\b|spreadsheet|xlsx"),
    ("marketing-copy", r"market|copywrit|seo|landing|campaign|email.?market|conversion|positioning|messaging|brand.?voice"
                       r"|prospect|lead.?gen|outreach|apollo|clay\b|lusha|zoominfo|mailchimp|advertis|display buyer|programmatic"
                       r"|blog|newsletter|lead.?magnet|similarweb|crunchbase|writing|prose|article|draft"),
    ("social-content", r"social|twitter|x\.com|instagram|tiktok|linkedin|facebook|thread|post|content.?calend"
                       r"|reddit|discord|carousel|caption|reel\b|short.?form|community|\big-[a-z]"),
    ("video-audio", r"video|audio|ffmpeg|youtube|podcast|music|davinci|resolve|comfy|voice|speech|tts|whisper|edit.?reel"
                    r"|unreal|metal\b|3d\b|render|photogrammetr|drone|scene|frame\b|clip\b|zoom\b|otter|fireflies|granola|transcri"),
    ("research", r"research|search|scrape|crawl|firecrawl|browse|arxiv|paper|investigate|osint|web.?fetch"
                 r"|geograph|gis\b|spatial|geoai|cartograph|map\b|pubmed|biorxiv|chembl|benchling|biorender|clinical|trials"
                 r"|anthropolog|ethnograph|narratolog|psycholog|consensus|wiley|synapse|owkin|exa\b|evidence|benchmark"
                 r"|analytics|data analys|feedback synthes|tool evaluat|study abroad"),
    ("security-review", r"secur|vulnerab|owasp|pentest|audit|threat|cve|sast|lint.?sec|trailofbits|diff.?review"
                        r"|secret|credential|privacy|gdpr|ccpa|complian|legal|test automation|qa\b|test result|test analys"
                        r"|code.?review|bug|debug|diagnos"),
    ("memory-context", r"memory|memwal|claude-mem|context|compact|summar|rag\b|embedding|chroma|vector"
                       r"|knowledge|onboard.?engineer|codebase onboard|serena|docs\b|document generat|guru|notion|obsidian"),
    ("agent-orchestration", r"agent|orchestr|multi.?agent|swarm|crew|supervisor|subagent|workflow|hook|skill.?router"
                            r"|prompt engineer|prompt\b|sequential.?thinking|gstack|spec\b|plan\b|scaffold|tdd\b|implement"
                            r"|zapier|emergent|tessl|morph|glif|skill.?creator|router|retrospectiv|questionnaire|re-?pitch|teach"),
    ("business-ops", r"crm|invoice|contract|sales|ops\b|calendar|notion|linear|slack|stripe|billing|pipeline|client"
                     r"|financ|account|bookkeep|controller|tax\b|fp&a|budget|payroll|expense|procure|supply chain|inventory"
                     r"|hr\b|recruit|resume|hiring|onboarding|employee|talent|customer service|customer success|retail|return"
                     r"|project manag|operations|organizational|change management|chief|executive|shepherd|sprint|studio"
                     r"|quickbooks|xero|myob|zoho|paypal|square|ramp|gusto|expensify|docusign|asana|monday|clickup|trello"
                     r"|hubspot|close\b|intercom|gong|calendly|dropbox|box\b|telegram|imessage|whatsapp|microsoft.?365"
                     r"|shopify|wix\b|korean business|business culture|consultant|strategist|nudge|docx|\bpdf\b|word document"),
]

# MCP servers are catalogued from the server NAME alone (Phase 0 stopped the script
# reading commands, args and URLs, because that is how a bearer token reached a catalog
# file). A name carries no description, so the keyword rules above miss most of them:
# this map is the name-level truth, and anything not in it falls through to the rules.
MCP_NAMES = {
    "airtable": ["backend-data"], "apollo": ["marketing-copy"], "apollo-io": ["marketing-copy"],
    "asana": ["business-ops"], "atlassian": ["business-ops"], "atlassian-rovo": ["business-ops"],
    "benchling": ["research"], "biorender": ["research"], "biorxiv": ["research"],
    "box": ["business-ops"], "c-trials": ["research"], "calendly": ["business-ops"],
    "canva": ["web-design"], "chembl": ["research"], "chrome-devtools": ["frontend-code"],
    "clay": ["marketing-copy"], "clickup": ["business-ops"], "close": ["business-ops"],
    "common-room": ["marketing-copy"], "consensus": ["research"],
    "creative_production_mcp": ["video-audio"], "crunchbase": ["research"],
    "dataAnalyticsWidgets": ["research"], "datadog": ["backend-data"],
    "discord": ["social-content"], "docusign": ["business-ops"], "dramaclaw": ["video-audio"],
    "dropbox": ["business-ops"], "emergent": ["agent-orchestration"], "exa": ["research"],
    "expensify": ["business-ops"], "fakechat": ["social-content"], "firebase": ["backend-data"],
    "fireflies": ["video-audio"], "framer": ["web-design"], "github": ["backend-data"],
    "gitlab": ["backend-data"], "glif": ["video-audio"], "gmail": ["business-ops"],
    "gong": ["business-ops"], "google-drive": ["business-ops"], "google_drive": ["business-ops"], "google drive": ["business-ops"],
    "graft": ["backend-data"], "granola": ["video-audio"], "guru": ["memory-context"],
    "gusto": ["business-ops"], "higgsfield": ["video-audio"], "hubspot": ["business-ops"],
    "imessage": ["business-ops"], "intercom": ["business-ops"],
    "intuit-mailchimp": ["marketing-copy"], "intuit-quickbooks": ["business-ops"],
    "laravel-boost": ["backend-data"], "lusha": ["marketing-copy"],
    "microsoft-365": ["business-ops"], "mobbin": ["web-design"], "monday": ["business-ops"],
    "monday-com": ["business-ops"], "morph-mcp": ["agent-orchestration"], "myob": ["business-ops"],
    "ot": ["misc"], "otter-ai": ["video-audio"], "outreach": ["marketing-copy"],
    "owkin": ["research"], "paypal": ["business-ops"], "pencil": ["web-design"],
    "playwright": ["frontend-code"], "pubmed": ["research"], "quiverquant": ["research"],
    "ramp": ["business-ops"], "remote": ["business-ops"], "ringex-chat": ["business-ops"],
    "sentry": ["backend-data"], "sequential-thinking": ["agent-orchestration"],
    "serena": ["memory-context"], "shopify": ["business-ops"], "similarweb": ["research"],
    "square": ["business-ops"], "synapse": ["research"], "telegram": ["business-ops"],
    "terraform": ["backend-data"], "tessl": ["agent-orchestration"], "tools": ["misc"],
    "trello": ["business-ops"], "vercel": ["backend-data"], "wiley": ["research"],
    "wix": ["web-design"], "xcodebuildmcp": ["frontend-code"], "xero": ["business-ops"],
    "zapier": ["business-ops"], "zoho-books": ["business-ops"], "zoho-desk": ["business-ops"],
    "zoho-projects": ["business-ops"], "zoom": ["video-audio"], "zoom-docs-mcp": ["business-ops"],
    "zoom-mcp": ["video-audio"], "zoom-whiteboard-mcp": ["web-design"],
    "zoominfo": ["marketing-copy"],
}

def categorize_mcp(name: str):
    base = re.sub(r"__[0-9a-f]{6,}$", "", name)          # dedupe suffix the sweep adds
    return MCP_NAMES.get(base) or MCP_NAMES.get(name) or categorize(name, "")

def categorize(name: str, desc: str):
    text = f"{name} {desc}".lower()
    hits = []
    for cat, pat in RULES:
        if re.search(pat, text, re.I):
            hits.append(cat)
    if not hits:
        return ["misc"]
    # max 2 categories
    return hits[:2]

def parse_agent(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.stem
    desc = ""
    if text.startswith("---"):
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        if m:
            fm = m.group(1)
            dm = re.search(r"^description:\s*[>|]?\s*(.*?)(?=\n[a-zA-Z_]+:|\Z)", fm, re.S | re.M)
            if dm:
                words = re.sub(r"\s+", " ", dm.group(1)).strip().split()
                desc = " ".join(words[:30])
            nm = re.search(r"^name:\s*[\"']?([^\"'\n]+)", fm, re.M)
            if nm:
                name = nm.group(1).strip()
    return name, desc, path.stat().st_size

def parse_mcp(path: Path):
    """Read only non-secret fields. command, args, headers, env and URLs are
    NEVER read into a catalog line: they carry bearer tokens and api keys."""
    data = json.loads(path.read_text())
    servers = data.get("mcpServers") or {}
    rows = []
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            transport = "unknown"
            tools = None
        else:
            if cfg.get("url") or cfg.get("serverUrl"):
                transport = "sse/http"
            elif cfg.get("command"):
                transport = "stdio"
            else:
                transport = cfg.get("type") or "unknown"
            tools = cfg.get("toolCount") or cfg.get("tool_count")
        rows.append((name, transport, tools, path))
    return rows

def regen_plugin_index():
    """Rewrite plugins/INDEX.md from what Claude Code has installed right now, so enabled
    flags and cache paths can't go stale. No installed_plugins.json: keep the file as is."""
    home = Path.home() / ".claude"
    reg = home / "plugins" / "installed_plugins.json"
    if not reg.exists():
        return
    installed = json.loads(reg.read_text()).get("plugins", {})
    try:
        enabled = json.loads((home / "settings.json").read_text()).get("enabledPlugins", {})
    except (OSError, ValueError):
        enabled = {}
    out = ["# Plugin INDEX", "",
           f"Generated {datetime.now():%Y-%m-%d %H:%M} by bin/build-catalog.sh from installed_plugins.json "
           "and settings.json. Cache paths are what `--plugin-dir` would need.", ""]
    for pid in sorted(installed, key=lambda p: p.split("@", 1)[::-1]):
        name, market = pid.split("@", 1)
        ip = Path(installed[pid][0]["installPath"])
        if not ip.is_dir():  # registered version deleted: fall back to the newest one on disk
            vers = sorted((d for d in ip.parent.glob("*") if d.is_dir()), key=lambda d: d.stat().st_mtime) if ip.parent.is_dir() else []
            if not vers:
                continue
            ip = vers[-1]
        try:
            pj = json.loads((ip / ".claude-plugin" / "plugin.json").read_text())
        except (OSError, ValueError):
            pj = {}
        hooks = (ip / "hooks" / "hooks.json").exists() or "hooks" in pj
        mcp = (ip / ".mcp.json").exists() or "mcpServers" in pj
        out += [f"## {market}/{name}", "",
                f"- **enabled**: {enabled.get(pid) is True}",
                f"- **version**: {ip.name}",
                f"- **cache path**: `{ip}`",
                f"- **contributes**: skills={len(list(ip.glob('skills/**/SKILL.md')))}, "
                f"agents={len(list(ip.glob('agents/*.md')))}, hooks={'yes' if hooks else 'no'}, "
                f"mcp={'yes' if mcp else 'no'}, commands={len([f for f in ip.glob('commands/*') if f.is_file()])}", ""]
    (TB / "plugins").mkdir(exist_ok=True)
    (TB / "plugins" / "INDEX.md").write_text("\n".join(out))


def parse_plugin_index():
    regen_plugin_index()
    idx = TB / "plugins" / "INDEX.md"
    rows = []
    if not idx.exists():
        return rows
    text = idx.read_text(encoding="utf-8", errors="replace")
    for b in re.split(r"^## ", text, flags=re.M)[1:]:
        lines = b.strip().splitlines()
        if not lines:
            continue
        pid = lines[0].strip()
        contributes = ""
        cache = ""
        for line in lines[1:]:
            if "**contributes**" in line:
                contributes = line.split(":", 1)[-1].strip()
            if "**cache path**" in line:
                cache = line.split(":", 1)[-1].strip().strip("`")
        rows.append((pid, contributes, cache))
    return rows

items_by_cat = defaultdict(list)  # cat -> list of one-line strings
all_items = []  # for recently added / unmatched
unmatched = []

# Agents
agents_dir = TB / "agents"
recent_paths = []
if agents_dir.is_dir():
    for f in sorted(agents_dir.rglob("*.md")):
        name, desc, size = parse_agent(f)
        cats = categorize(name, desc)
        if cats == ["misc"]:
            unmatched.append(f"agent:{name}")
        line = f"- agent | {name} | {desc[:120]} | {f.relative_to(TB)} | {size}"
        for c in cats:
            items_by_cat[c].append(line)
        all_items.append((f.stat().st_mtime, "agent", name, cats, str(f.relative_to(TB))))
        recent_paths.append(f)

# MCP mine + discovered
for kind, folder in [("mcp-mine", TB / "mcp" / "mine"), ("mcp-discovered", TB / "mcp" / "discovered")]:
    if not folder.is_dir():
        continue
    for f in sorted(folder.glob("*.json")):
        try:
            rows = parse_mcp(f)
        except Exception:
            continue
        for name, transport, tools, path in rows:
            cats = categorize_mcp(name)
            if cats == ["misc"]:
                unmatched.append(f"{kind}:{name}")
            tools_s = f"tools: {tools}" if tools else "tools: ?"
            line = f"- {kind} | {name} | {transport} | {tools_s} | {path.relative_to(TB)}"
            for c in cats:
                items_by_cat[c].append(line)
            all_items.append((f.stat().st_mtime, kind, name, cats, str(path.relative_to(TB))))

# Plugins
# Why a plugin is parked, in the owner's words: plugins/notes.json {"market/name": "note"}.
# Local and gitignored, like INDEX.md, so a disabled plugin's history stays off the repo.
try:
    PLUGIN_NOTES = json.loads((TB / "plugins" / "notes.json").read_text())
except (OSError, ValueError):
    PLUGIN_NOTES = {}
for pid, contributes, cache in parse_plugin_index():
    cats = categorize(pid, contributes)
    if cats == ["misc"]:
        unmatched.append(f"plugin:{pid}")
    note = PLUGIN_NOTES.get(pid, "")
    line = f"- plugin | {pid} | {contributes} | {cache}" + (f" | NOTE: {note}" if note else "")
    for c in cats:
        items_by_cat[c].append(line)
    all_items.append((0, "plugin", pid, cats, cache))

# Skills in toolbox/skills if any
skills_dir = TB / "skills"
if skills_dir.is_dir():
    for f in sorted(skills_dir.rglob("SKILL.md")):
        text = f.read_text(encoding="utf-8", errors="replace")[:4000]
        name = f.parent.name
        desc = ""
        if text.startswith("---"):
            m = re.match(r"^---\n(.*?)\n---", text, re.S)
            if m:
                dm = re.search(r"^description:\s*[>|]?\s*(.*?)(?=\n[a-zA-Z_]+:|\Z)", m.group(1), re.S | re.M)
                if dm:
                    desc = re.sub(r"\s+", " ", dm.group(1)).strip()[:200]
        cats = categorize(name, desc)
        if cats == ["misc"]:
            unmatched.append(f"skill:{name}")
        line = f"- skill | {name} | {desc[:120]} | {f.relative_to(TB)}"
        for c in cats:
            items_by_cat[c].append(line)
        all_items.append((f.stat().st_mtime, "skill", name, cats, str(f.relative_to(TB))))

# Applications and agent-tools from manifest.json. These are not files under toolbox/,
# so nothing else in this script can see them; the manifest is their only record.
# Categories are explicit per entry (hand-reviewed) and fall back to the keyword rules.
man = TB / "manifest.json"
if man.exists():
    try:
        mtools = json.loads(man.read_text()).get("tools", [])
    except Exception:
        mtools = []
    for e in mtools:
        kind = e.get("kind")
        if kind not in ("application", "agent-tool"):
            continue
        name = e.get("name", "?")
        desc = re.sub(r"\s+", " ", e.get("desc", "")).strip()
        cats = e.get("categories") or categorize(name, desc)
        risks = "; ".join(e.get("risks", []))
        warn = re.sub(r"\\s+", " ", e.get("warn", "")).strip()
        line = (f"- {kind} | {name} | {desc[:200]} | {e.get('path','(not cloned)')} | "
                f"{e.get('license','license unknown')}"
                + (f" | WARN: {warn}" if warn else "")
                + f" | risks: {risks[:260]}")
        for c in cats:
            items_by_cat[c].append(line)
        all_items.append((0, kind, name, cats, e.get("path", "(not cloned)")))

# Matches credential VALUES, not the words: "authorization pathway" in an agent
# description and a server literally named openai-api-key-... are not secrets.
SECRET_RE = re.compile(
    r"bearer\s+\S{8,}"
    r"|(?:api[-_]?key|apikey|token|secret|password|authorization)\s*[=:]\s*\S{8,}"
    r"|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{16,}|xox[bapr]-[A-Za-z0-9-]{10,}"
    r"|https?://\S*[?&](?:key|token|api[-_]?key|access_token)=",
    re.I,
)

def assert_clean(name: str, text: str):
    bad = [i for i, l in enumerate(text.splitlines(), 1) if SECRET_RE.search(l)]
    if bad:
        sys.exit(f"ABORT: {name} line(s) {bad} match a credential pattern; not written.")

# Write category files
cat_counts = {}
for cat in CATEGORIES:
    lines = items_by_cat.get(cat, [])
    cat_counts[cat] = len(lines)
    body = [f"# {cat}", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}", f"Count: {len(lines)}", "",
            "Line format: `- kind | name | what it is | path` — and for kind `application` or",
            "`agent-tool`, also `| license | WARN: read this before recommending it | risks: ...`.",
            "Kinds: skill, agent, plugin, mcp-mine, mcp-discovered, application, agent-tool.",
            "Paths are relative to ~/toolbox. Nothing here is installed: borrow it or session-launch it.",
            ""]
    body.extend(lines)
    body.append("")
    out = "\n".join(body) + "\n"
    assert_clean(f"catalog/{cat}.md", out)
    (CATALOG / f"{cat}.md").write_text(out)

# Websites: free web apps with no repo (websites.json, written by /toolbox-add). They get
# their own file instead of joining the job categories, so a hosted tool is never mistaken
# for something on the shelf. library.py indexes every line as kind `website`.
web_lines = []
wf = TB / "websites.json"
if wf.exists():
    try:
        sites = json.loads(wf.read_text()).get("sites", [])
    except Exception:
        sites = []
    for s in sorted(sites, key=lambda s: s.get("name", "").lower()):
        does = re.sub(r"\s+", " ", s.get("does", "")).strip()
        cats = s.get("categories") or categorize(s.get("name", ""), does)
        meta = (f"free: {s.get('free', '?')} · account: {s.get('account', '?')} · "
                f"api: {'yes' if s.get('api') else 'no'}"
                + (f" · limits: {s['limits']}" if s.get("limits") else "")
                + f" · verified: {s.get('verified', 'not checked')}")
        risks = "; ".join(s.get("risks", []))
        web_lines.append(f"- website | {s.get('name', '?')} | {does[:200]} · {meta} | {s.get('url', '?')} | "
                         f"{', '.join(cats)}" + (f" | risks: {risks[:200]}" if risks else ""))
        all_items.append((0, "website", s.get("name", "?"), cats, s.get("url", "?")))
web_body = ["# websites", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}", f"Count: {len(web_lines)}", "",
            "Free or freemium web apps with no repo. Source of truth: websites.json (edit that, not this file).",
            "Line format: `- website | name | what it does · free · account · api · limits · verified | url | categories | risks`.",
            "Use one by opening it (WebFetch, claude-in-chrome) or through its API. Never sign up, start a",
            "trial or enter a card without the user's yes, and never upload client material under NDA.",
            ""] + web_lines + [""]
web_out = "\n".join(web_body) + "\n"
assert_clean("catalog/websites.md", web_out)
(CATALOG / "websites.md").write_text(web_out)

# Write unmatched list for report
(CATALOG / "_unmatched.txt").write_text("\n".join(unmatched) + ("\n" if unmatched else ""))

# TOOLS-MEMORY.md max 200 lines
blurb = {
    "web-design": "UI/UX, layouts, brand, CSS/design systems.",
    "frontend-code": "React/Next and browser UI implementation.",
    "backend-data": "APIs, databases, auth, server code.",
    "marketing-copy": "SEO, campaigns, positioning, landing copy.",
    "social-content": "Social posts and channel content.",
    "video-audio": "Video/audio edit, generation, voice.",
    "research": "Search, scrape, investigate, papers.",
    "security-review": "Audits, SAST, vuln review.",
    "memory-context": "Memory, compaction, RAG/context tools.",
    "agent-orchestration": "Agents, skills routing, multi-agent flows.",
    "business-ops": "CRM, sales, ops, billing, client work.",
    "misc": "Uncategorized or cross-cutting tools.",
}

mem = []
mem.append("# TOOLS-MEMORY (toolbox index)")
mem.append("")
mem.append("How to use: read this file first for orientation; open only the category file you need under catalog/.")
mem.append("Do not load every catalog/*.md into context. Prefer loadouts/ for curated enable-lists.")
mem.append("Secrets live in mcp/mine (gitignored); share only mcp-templates/.")
mem.append("Regenerate with: ~/toolbox/bin/build-catalog.sh")
mem.append("Agents are parked here; live ~/.claude/agents stays empty unless you copy a loadout.")
mem.append("")
mem.append("## Categories")
mem.append("")
for cat in CATEGORIES:
    mem.append(f"- **{cat}** ({cat_counts.get(cat, 0)}): {blurb[cat]} → `catalog/{cat}.md`")
mem.append(f"- **websites** ({len(web_lines)}): free web apps with no repo, any job. → `catalog/websites.md` (from websites.json)")
mem.append("")
mem.append("## Review dates")
mem.append("")
mem.append("- (none open. The 2026-10-04 marketing-skills review was settled early on")
mem.append("  2026-09-21: disabled and moved to session-launch via --plugin-dir, because its")
mem.append("  50 descriptions were 52% of the skill-listing budget. See plugins/INDEX.md.)")
mem.append("")
mem.append("## Proven")
mem.append("")
# Generated from the ONE ledger, so a rebuild can never wipe it and nothing hand-edits
# this file. /tool-audit debrief appends a row, then runs this script.
LEDGER = Path.home() / ".claude" / "skill-audit" / "ledger.jsonl"
proven = {}
if LEDGER.exists():
    for line in LEDGER.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        key = (r.get("kind", "skill"), r.get("skill", ""))
        if not key[1]:
            continue
        d = proven.setdefault(key, {"worked": 0, "mixed": 0, "failed": 0,
                                    "situations": [], "last": "", "note": ""})
        oc = r.get("outcome", "")
        if oc == "failed" and r.get("failure_type") in ("auth", "paywall", "cap", "missing"):
            oc = "blocked"   # account/setup problem, not the tool's fault: never counts toward FAILED TWICE
        if oc in d:
            d[oc] += 1
        s = r.get("situation", "")
        if s and s not in d["situations"]:
            d["situations"].append(s)
        if oc in ("worked", "mixed", "failed"):
            d["last"] = r.get("goal", "") or d["last"]
            d["note"] = r.get("note", "") or d["note"]
ranked = sorted(proven.items(), key=lambda kv: (-kv[1]["worked"], kv[1]["failed"]))
lines = []
for (kind, name), d in ranked:
    sit = ", ".join(d["situations"][:3]) or "untagged"
    if d["failed"] >= 2 and d["worked"] == 0:
        lines.append(f"- FAILED TWICE: {kind} `{name}` [{sit}] — {d['note'][:90]}")
    elif d["worked"]:
        plural = "" if d["worked"] == 1 else "s"
        lines.append(f"- {kind} `{name}` — {d['worked']} win{plural}"
                     + (f", {d['failed']} fail" if d["failed"] else "")
                     + f" [{sit}] — last: {d['last'][:70]}")
if lines:
    mem.extend(lines[:25])
else:
    mem.append("(empty — nothing has been recorded in the ledger yet)")
mem.append("")
mem.append("## Sources")
mem.append("")
# Reference lists. Generated from manifest.json (falls back to the directory) so nothing
# is hand-written into this file, which every rebuild overwrites. Never catalogued:
# /tool-audit greps these only when the toolbox has nothing for a goal.
man = TB / "manifest.json"
src_lines = []
if man.exists():
    try:
        tools = json.loads(man.read_text()).get("tools", [])
    except Exception:
        tools = []
    for e in tools:
        if e.get("kind") == "reference-list":
            src_lines.append(f"- {e.get('name','?')} — {e.get('url','?')} "
                             f"({e.get('license','license unknown')}, pinned {str(e.get('commit') or 'unpinned')[:8]}) "
                             f"`{e.get('path','sources/?')}`")
if not src_lines:
    sdir = TB / "sources"
    for d in sorted(p for p in sdir.glob("*") if p.is_dir()) if sdir.exists() else []:
        src_lines.append(f"- {d.name} `sources/{d.name}` (not in manifest.json yet)")
mem.extend(src_lines or ["(none)"])
mem.append("")
mem.append("## Recently added")
mem.append("")
recent = sorted(all_items, key=lambda x: x[0], reverse=True)[:20]
if not recent:
    mem.append("(none)")
else:
    for mtime, kind, name, cats, rel in recent:
        mem.append(f"- {kind}: {name} [{', '.join(cats)}] `{rel}`")
mem.append("")

# enforce max 200 lines
if len(mem) > 200:
    mem = mem[:199] + ["… truncated to 200 lines"]
mem_out = "\n".join(mem) + "\n"
assert_clean("TOOLS-MEMORY.md", mem_out)
(TB / "TOOLS-MEMORY.md").write_text(mem_out)

# meta
meta = {
    "generated": datetime.now().isoformat(),
    "counts": dict(cat_counts, websites=len(web_lines)),
    "total_lines_tools_memory": len(mem),
    "unmatched": len(unmatched),
    "unmatched_sample": unmatched[:60],
}
(CATALOG / "_build-meta.json").write_text(json.dumps(meta, indent=2))
print(json.dumps(meta, indent=2)[:2000])
print("TOOLS-MEMORY lines:", len(mem))
print("TOOLS-MEMORY bytes:", (TB / "TOOLS-MEMORY.md").stat().st_size)
PY
