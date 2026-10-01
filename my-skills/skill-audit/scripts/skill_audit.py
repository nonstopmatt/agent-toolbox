#!/usr/bin/env python3
"""skill_audit.py - pick skills for a goal, run them, remember what worked.

Reads the live library through tool-audit's build_inventory.py (a fresh filesystem
walk every call, never a cache), scores every item against the goal, blends in what
the ledger has learned, deliberately reserves slots for skills that have never been
tried, and prints a run plan split into what may be run automatically and what has
to be asked about first.

  plan      --goal "..." [--situation tag] [-n 10] [--explore 1] [--cwd .]
  record    --skill NAME --situation tag --outcome worked|mixed|failed|skipped
            [--goal "..."] [--note "..."] [--mode exploit|explore]
  report    [--situation tag]        scoreboard, also written to scoreboard.md
  untried   [-n 30] [--goal "..."]   skills with no ledger history
  situations                          the tag vocabulary

The workspace is pinned to ~/.claude/skill-audit and never derived from the cwd.
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import time

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
WORKSPACE = os.path.join(CLAUDE, "skill-audit")          # pinned, never cwd-derived
LEDGER = os.path.join(WORKSPACE, "ledger.jsonl")
SITUATIONS_MD = os.path.join(WORKSPACE, "situations.md")
SCOREBOARD = os.path.join(WORKSPACE, "scoreboard.md")
INVENTORY = os.path.join(CLAUDE, "skills", "tool-audit", "scripts", "build_inventory.py")
_SIBLING = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                         "tool-audit", "scripts", "build_inventory.py"))
if os.path.isfile(_SIBLING):          # same file when installed; lets a staged copy test against its staged twin
    INVENTORY = _SIBLING
SKILL_ROOTS = [os.path.join(CLAUDE, "skills"), os.path.join(CLAUDE, "plugins")]

OUTCOMES = ("worked", "mixed", "failed", "skipped")
OUTCOME_VALUE = {"worked": 1.0, "mixed": 0.5, "failed": 0.0}   # "skipped" does not score

# ---------------------------------------------------------------- safety tiers
# Anything that leaves the machine, spends money, or cannot be undone is ASK, however
# well it scores. These mirror rules the user already has in CLAUDE.md and memory: never an
# unprompted cold send, Higgsfield only on an explicit yes, BuildPartner only when named.
ASK_NAME = (
    "ship", "deploy", "land-and", "commit", "push", "pr", "release", "publish",
    "send", "email", "gmail", "outreach", "cold", "dm", "post", "signup",
    "higgsfield", "fal-ai", "glif", "photoroom", "replicate",
    "trading", "co-invest", "order", "buy", "sell", "invest",
    "delete", "trash", "merge", "worktree", "canary", "freeze", "unfreeze",
    "cron", "schedule", "loop", "remote",
)
# Matched as whole phrases, not substrings: "sends per reach" in a Reels skill must not
# read as "this sends something". A false ask is cheap; a false auto-run is not, so these
# stay deliberately concrete rather than broad.
ASK_DESC = (
    "sends an email", "send an email", "sends the email", "sends a message",
    "deploys to", "deploy to production", "pushes to", "opens a pr", "creates a pr",
    "publishes to", "posts to", "charges", "billable", "costs credits", "spends credits",
    "irreversible", "cannot be undone", "goes live",
)
NEVER_AUTO = ("buildpartner",)   # CLAUDE.md: only when the user names BuildPartner

# Things Claude can actually invoke, versus things that are merely available to it.
RUNNABLE = ("skill", "plugin-skill", "synced-skill", "plugin-command", "command",
            "plugin-agent", "agent", "session-skill", "session-agent")
RESOURCE = ("mcp-server", "connector", "session-mcp")
NOTE = "memory-note"      # never a pick: surfaced beside the picks, because notes are where
                          # local tools that are not skills (and the rules about them) live


def load_inventory(cwd, session=""):
    spec = importlib.util.spec_from_file_location("build_inventory", INVENTORY)
    if spec is None or spec.loader is None:
        sys.exit("cannot load %s" % INVENTORY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build(cwd, session), mod


# ---------------------------------------------------------------- text matching
def stem(w):
    for suf in ("ings", "ing", "ies", "ers", "er", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def words(text, stopwords):
    out = []
    for w in re.findall(r"[a-z][a-z0-9]{2,}", text.lower()):
        if w not in stopwords:
            out.append(w)
    return out


def name_tokens(name):
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if len(t) > 2]


def relevance(item, goal_words, goal_stems, goal_cats):
    """Bidirectional and stem-aware, because 'instagram reels' must reach `ig-reel`.

    Observation 0005: the old scorer missed thirteen ig-* skills for a reels goal,
    because "reels" is not a substring of "ig-reel" and "instagram" is in neither the
    name nor a category trigger. Matching stems in both directions fixes that class.
    """
    name_l = item["name"].lower()
    desc_l = item.get("description", "").lower()
    ntoks = name_tokens(item["name"])
    nstems = {stem(t) for t in ntoks}
    dstems = {stem(w) for w in re.findall(r"[a-z][a-z0-9]{2,}", desc_l)}

    score = 0.0
    hits = []
    for w, s in zip(goal_words, goal_stems):
        # Containment only between long tokens. Allowed on short ones, "form" matches
        # "for" and a reels goal recommends /writing-for-agents with a straight face.
        loose = len(s) >= 5 and any(len(t) >= 5 and (s in t or t in s) for t in nstems)
        if w in name_l or s in nstems or loose:
            score += 3.0
            hits.append(w)
    score += min(4.0, sum(1.0 for s in goal_stems if s in dstems))
    score += 2.0 * len(goal_cats & set(item.get("categories", [])))
    return score, hits


def rarity(goal_stems, items):
    """How unusual each goal word is across the library. 'comfyui' appears in two items and
    'podcast' in sixty, so the first is what the goal is ABOUT and the second is scenery.
    Without this a note about the one local tool that fits is buried under every note that
    merely mentions the project it would be used on."""
    df = dict.fromkeys(goal_stems, 0)
    for i in items:
        text = (i["name"] + " " + i.get("description", "")).lower()
        for s in df:
            if s in text:
                df[s] += 1
    return {s: 1.0 + 3.0 * (1.0 - min(n, 40) / 40.0) for s, n in df.items()}


def note_score(item, goal_stems, weight):
    name_l = item["name"].lower()
    desc_l = item.get("description", "").lower()
    score, hits = 0.0, []
    for s in goal_stems:
        if s in name_l:
            score += 3.0 * weight[s]
            hits.append(s)
        elif s in desc_l:
            score += 1.0 * weight[s]
            hits.append(s)
    return score, hits


# ---------------------------------------------------------------- ledger
def read_ledger():
    rows = []
    if not os.path.exists(LEDGER):
        return rows
    with open(LEDGER) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass           # one bad line never costs the whole history
    return rows


def append_ledger(row):
    os.makedirs(WORKSPACE, exist_ok=True)
    with open(LEDGER, "a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def stats(rows, situation=None):
    """Laplace-smoothed win rate per skill and per (skill, situation)."""
    agg = {}
    for r in rows:
        if r.get("outcome") not in OUTCOME_VALUE:
            continue
        if situation and r.get("situation") != situation:
            continue
        a = agg.setdefault(r["skill"], {"n": 0, "w": 0.0, "last": ""})
        a["n"] += 1
        a["w"] += OUTCOME_VALUE[r["outcome"]]
        a["last"] = max(a["last"], r.get("date", ""))
    for a in agg.values():
        a["rate"] = (a["w"] + 1.0) / (a["n"] + 2.0)      # prior: one win, one loss
    return agg


def load_situations():
    tags = []
    if os.path.exists(SITUATIONS_MD):
        for line in open(SITUATIONS_MD):
            m = re.match(r"^\|\s*([a-z][a-z0-9-]+)\s*\|", line)
            if m and m.group(1) != "tag":
                tags.append(m.group(1))
    return tags


# ---------------------------------------------------------------- safety
def tier(item):
    """'auto' = advisory / read-only, safe to run unasked. 'ask' = confirm first."""
    name_l = item["name"].lower()
    desc_l = item.get("description", "").lower()
    if any(k in name_l for k in NEVER_AUTO):
        return "ask", "BuildPartner runs only when the user names it"
    if item.get("user_only"):
        return "ask", "user-only: the user types it, Claude cannot invoke it"
    if item["kind"] not in RUNNABLE:
        return "ask", "%s - available to Claude, but not a skill it can run" % item["kind"]
    for k in ASK_NAME:
        if k in name_tokens(item["name"]):
            return "ask", "name says '%s': may leave the machine or cost money" % k
    for k in ASK_DESC:
        if k in desc_l:
            return "ask", "description says '%s'" % k
    return "auto", ""


# ---------------------------------------------------------------- coverage guard
def coverage_check(goal_words, goal_stems, picks, inv):
    """Distinguish 'nothing scored' from 'nothing exists' (observations 0005, 0010).

    A recommender never says "I could not see the library", it says "here are the best
    three". So count the population a second way, off the filesystem directly, and warn
    on any goal noun that no installed skill NAME carries.
    """
    lines = []
    # Count the same population a second way, straight off the filesystem: one level of
    # ~/.claude/skills holding a SKILL.md. Comparing that against every SKILL.md anywhere
    # under ~/.claude would compare a shelf to a warehouse and cry wolf every run.
    root = SKILL_ROOTS[0]
    on_disk = 0
    if os.path.isdir(root):
        on_disk = sum(1 for e in os.listdir(root)
                      if os.path.isfile(os.path.join(root, e, "SKILL.md")))
    counted = sum(1 for i in inv["items"]
                  if i["kind"] == "skill" and i["source"].startswith("personal"))
    lines.append("personal skills: inventory %d | directories on disk %d" % (counted, on_disk))
    if on_disk and counted < on_disk * 0.9:
        lines.append("SCAN SUSPECT - the disk has %d and the inventory reported %d; list "
                     "%s directly before trusting this plan" % (on_disk, counted, root))

    all_name_stems = set()
    for i in inv["items"]:
        if i["kind"] != NOTE:
            all_name_stems |= {stem(t) for t in name_tokens(i["name"])}
    # Containment only between long tokens, as in relevance(): unrestricted, the "com" in
    # "wordpress.com" covers "comfyui" and the one word that matters is never reported.
    orphan = [(w, s) for w, s in zip(goal_words, goal_stems)
              if s not in all_name_stems
              and not any((len(s) >= 4 and s in t) or (len(t) >= 5 and t in s) for t in all_name_stems)]
    # Second step: a word no skill carries is often a LOCAL TOOL (ComfyUI, Postiz, a scraper),
    # and those are documented in memory notes, not in the skill library.
    uncovered = []
    for w, s in orphan:
        at_word_start = re.compile(r"(?<![a-z0-9])" + re.escape(s))   # "roll" must not match "scroll"
        notes = [i for i in inv["items"] if i["kind"] == NOTE]
        named = sorted(i["name"] for i in notes if at_word_start.search(i["name"].lower().replace("_", " ")))
        said = sorted(i["name"] for i in notes if i["name"] not in named
                      and at_word_start.search(i.get("description", "").lower()))
        if len(named) > 6:
            continue                       # a whole project's worth of notes: a topic word, not a missing tool
        if named:
            lines.append("no skill carries '%s', but memory notes are named for it (a local tool, project or "
                         "record outside the skill library) - read: %s" % (w, ", ".join(named)))
        elif 0 < len(said) <= 4:
            lines.append("no skill carries '%s'; memory notes mention it: %s" % (w, ", ".join(said)))
        elif not said:
            uncovered.append(w)
    if uncovered:
        lines.append("no skill NAME and no memory note carries: %s - if one of these is the heart "
                     "of the goal, the library may simply not cover it; say so rather than "
                     "offering the nearest match" % ", ".join(uncovered[:8]))
    picked = {p["item"]["name"] for p in picks}
    if not picked:
        lines.append("zero candidates scored - verify by listing %s directly before "
                     "concluding the library has nothing" % SKILL_ROOTS[0])
    return lines


# ---------------------------------------------------------------- plan
def cmd_plan(args):
    inv, mod = load_inventory(args.cwd, args.session)
    rows = read_ledger()
    glob_stats = stats(rows)
    sit_stats = stats(rows, args.situation) if args.situation else {}

    gw = words(args.goal, mod.STOPWORDS)
    gs = [stem(w) for w in gw]
    wset = set(gw) | set(gs)
    goal_cats = {c for c, trig in mod.GOAL_TRIGGERS.items() if wset & set(trig)}

    scored, notes = [], []
    weight = rarity(gs, inv["items"])
    for i in inv["items"]:
        if i.get("enabled") is False or i["kind"] == "sub-skill":
            continue
        if i["kind"] == NOTE:
            rel, hits = note_score(i, gs, weight)
            if hits:
                notes.append((rel, i))
            continue
        rel, hits = relevance(i, gw, gs, goal_cats)
        if rel <= 0:
            continue
        g = glob_stats.get(i["name"])
        s = sit_stats.get(i["name"])
        n = g["n"] if g else 0
        learned = 0.0
        if s and s["n"]:
            learned += 6.0 * (s["rate"] - 0.5)      # this situation counts double
        if g and g["n"]:
            learned += 3.0 * (g["rate"] - 0.5)
        explore = 2.5 if n == 0 else (1.0 if n == 1 else 0.0)
        scored.append({
            "item": i, "rel": rel, "hits": hits, "learned": learned,
            "explore": explore, "n": n,
            "rate_all": g["rate"] if g else None,
            "n_sit": s["n"] if s else 0,
            "rate_sit": s["rate"] if s else None,
            "total": rel + learned + explore,
        })
    scored.sort(key=lambda d: (-d["total"], d["item"]["name"]))

    # Observation 0005: the old scan printed a 38-item "new in 3 days" list and nothing
    # ever crossed it against the goal, so a skill installed that morning could not win.
    # Intersect explicitly instead of "considering" it, and boost what survives.
    try:
        recent_names = {i["name"] for i in mod.track_first_seen(inv)}
    except Exception:
        recent_names = set()
    for d in scored:
        if d["item"]["name"] in recent_names:
            d["recent"] = True
            d["total"] += 2.0
    scored.sort(key=lambda d: (-d["total"], d["item"]["name"]))

    # Exploitation slots first, then reserved slots for genuinely untried skills, so a
    # skill can never win purely by having been picked often. Untried candidates must
    # still be relevant - exploration is trying a new tool on a real job, not a lottery.
    picks, seen = [], set()
    for d in scored:
        if len(picks) >= args.n:
            break
        picks.append(dict(d, mode="exploit"))
        seen.add(d["item"]["name"])
    added = 0
    for d in scored:
        if added >= args.explore:
            break
        if (d["n"] == 0 and d["item"]["name"] not in seen and d["rel"] >= 4.0
                and d["hits"] and tier(d["item"])[0] == "auto"):
            picks.append(dict(d, mode="explore"))
            seen.add(d["item"]["name"])
            added += 1

    print("# skill-audit plan")
    print("goal: %s" % args.goal)
    print("situation: %s" % (args.situation or "(untagged - pass --situation for sharper picks)"))
    n_notes = sum(1 for i in inv["items"] if i["kind"] == NOTE)
    print("library: %d items + %d memory notes, generated %s" % (len(inv["items"]) - n_notes, n_notes, inv["generated"]))
    print("ledger: %d runs over %d skills" % (len(rows), len(glob_stats)))
    print()

    auto, ask = [], []
    for p in picks:
        t, why = tier(p["item"])
        (auto if t == "auto" else ask).append((p, why))

    def show(p, why=""):
        i = p["item"]
        bits = ["rel %.0f" % p["rel"]]
        if p["rate_sit"] is not None:
            bits.append("this situation: %d run%s %.0f%%" % (
                p["n_sit"], "" if p["n_sit"] == 1 else "s", 100 * p["rate_sit"]))
        if p["rate_all"] is not None:
            bits.append("overall %d run%s %.0f%%" % (p["n"], "" if p["n"] == 1 else "s",
                        100 * p["rate_all"]))
        else:
            bits.append("NEVER TRIED")
        tag = " [EXPERIMENT]" if p["mode"] == "explore" else ""
        if p.get("recent"):
            tag += " [JUST INSTALLED]"
        print("- `/%s` (%s)%s - %s" % (i["name"], ", ".join(bits), tag,
                                       (i.get("description") or "")[:150]))
        if why:
            print("    ASK FIRST: %s" % why)

    print("## Run these now (advisory / read-only)")
    if auto:
        for p, _ in auto:
            show(p)
    else:
        print("- none scored into the auto tier")
    print()
    print("## Ask the user before running (writes, sends, spends, or deploys)")
    if ask:
        for p, why in ask:
            show(p, why)
    else:
        print("- none")
    print()
    recent_hits = [d for d in scored if d.get("recent")]
    if recent_hits:
        print("## Installed in the last 3 days and relevant to this goal")
        for d in recent_hits[:5]:
            print("- `/%s` (rel %.0f)%s" % (d["item"]["name"], d["rel"],
                  "" if d["item"]["name"] in {p["item"]["name"] for p in picks}
                  else " - scored but did not make the cut; consider it anyway"))
        print()

    print("## Memory notes that bear on this goal (read the file before running anything it covers)")
    notes.sort(key=lambda t: (-t[0], t[1]["name"]))
    for rel, i in notes[:6]:
        print("- `%s` (%s, rel %.0f) %s" % (i["name"], i["source"], rel, (i.get("description") or "")[:170]))
        print("    %s" % i["path"])
    if not notes:
        print("- none matched; ~/.claude/tool-inventory/memory-notes.md lists all %d" % n_notes)
    print()
    print("## Coverage check")
    for line in coverage_check(gw, gs, picks, inv) + mod.coverage_lines(inv):
        print("- " + line)
    print()
    print("## After running, record each one")
    for p in picks:
        print("  skill_audit.py record --skill %s --situation %s --outcome worked|mixed|failed|skipped --mode %s"
              % (p["item"]["name"], args.situation or "TAG", p["mode"]))
    return 0


def cmd_record(args):
    if args.outcome not in OUTCOMES:
        sys.exit("outcome must be one of: %s" % ", ".join(OUTCOMES))
    tags = load_situations()
    if tags and args.situation not in tags:
        print("note: '%s' is not in situations.md (%s)" % (args.situation, ", ".join(tags)),
              file=sys.stderr)
    row = {
        "ts": int(time.time()),
        "date": time.strftime("%Y-%m-%d"),
        "skill": args.skill,
        "situation": args.situation,
        "outcome": args.outcome,
        "mode": args.mode,
        "goal": args.goal,
        "note": args.note,
        "kind": args.kind,
    }
    if args.loadout:
        row["loadout"] = args.loadout
    if args.failure_type:
        row["failure_type"] = args.failure_type   # auth/paywall/cap are account problems, not tool faults
    append_ledger(row)
    print("recorded: %s / %s / %s" % (args.skill, args.situation, args.outcome))
    return 0


def cmd_report(args):
    rows = read_ledger()
    if not rows:
        print("ledger is empty - nothing has been recorded yet, so every skill is untried "
              "and every recommendation is relevance-only.")
        return 0
    lines = []
    lines.append("# skill-audit scoreboard")
    lines.append("")
    lines.append("%d runs, %s to %s. Regenerated by `skill_audit.py report`; do not hand-edit."
                 % (len(rows), min(r.get("date", "") for r in rows),
                    max(r.get("date", "") for r in rows)))
    lines.append("")

    g = stats(rows)
    lines.append("## Overall (smoothed rate, so one lucky run does not top the table)")
    lines.append("")
    lines.append("| skill | runs | worked | rate | last |")
    lines.append("|---|---|---|---|---|")
    for name, a in sorted(g.items(), key=lambda kv: (-kv[1]["rate"], -kv[1]["n"])):
        lines.append("| `%s` | %d | %.1f | %.0f%% | %s |" % (name, a["n"], a["w"],
                                                             100 * a["rate"], a["last"]))
    lines.append("")

    by_sit = {}
    for r in rows:
        by_sit.setdefault(r.get("situation", "untagged"), []).append(r)
    lines.append("## Best in each situation")
    lines.append("")
    for sit in sorted(by_sit):
        s = stats(by_sit[sit])
        if not s:
            continue
        top = sorted(s.items(), key=lambda kv: (-kv[1]["rate"], -kv[1]["n"]))[:5]
        lines.append("**%s** (%d runs): %s" % (sit, len(by_sit[sit]),
                     ", ".join("`%s` %.0f%% of %d" % (n, 100 * a["rate"], a["n"])
                               for n, a in top)))
    lines.append("")

    losers = [(n, a) for n, a in g.items() if a["n"] >= 3 and a["rate"] < 0.4]
    if losers:
        lines.append("## Stop reaching for these")
        lines.append("")
        for n, a in sorted(losers, key=lambda kv: kv[1]["rate"]):
            lines.append("- `%s`: %d runs, %.0f%%. Three tries is enough to stop guessing."
                         % (n, a["n"], 100 * a["rate"]))
        lines.append("")

    exp = [r for r in rows if r.get("mode") == "explore"]
    if exp:
        kept = {r["skill"] for r in exp if r.get("outcome") == "worked"}
        lines.append("## Experiments")
        lines.append("")
        lines.append("%d experimental runs over %d skills; %d earned a place: %s"
                     % (len(exp), len({r["skill"] for r in exp}), len(kept),
                        ", ".join("`%s`" % k for k in sorted(kept)) or "none yet"))
        lines.append("")

    out = "\n".join(lines)
    os.makedirs(WORKSPACE, exist_ok=True)
    open(SCOREBOARD, "w").write(out + "\n")
    print(out)
    print("\n(written to %s)" % SCOREBOARD.replace(HOME, "~"))
    return 0


def cmd_untried(args):
    inv, mod = load_inventory(args.cwd, args.session)
    inv["items"] = [i for i in inv["items"] if i["kind"] != NOTE]
    tried = {r["skill"] for r in read_ledger()}
    gw = words(args.goal, mod.STOPWORDS) if args.goal else []
    gs = [stem(w) for w in gw]
    cats = {c for c, t in mod.GOAL_TRIGGERS.items() if (set(gw) | set(gs)) & set(t)} if gw else set()
    out = []
    for i in inv["items"]:
        if i.get("enabled") is False or i["kind"] == "sub-skill" or i["name"] in tried:
            continue
        rel = relevance(i, gw, gs, cats)[0] if gw else 0.0
        out.append((rel, i))
    out.sort(key=lambda t: (-t[0], t[1]["name"]))
    print("%d items with no ledger history (of %d in the library)"
          % (len(out), len(inv["items"])))
    for rel, i in out[: args.n]:
        mark = " rel %.0f" % rel if rel else ""
        print("- `%s` (%s)%s %s" % (i["name"], i["kind"], mark,
                                    (i.get("description") or "")[:110]))
    return 0


def cmd_situations(args):
    tags = load_situations()
    print("\n".join(tags) if tags else "no situations.md found at " + SITUATIONS_MD)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan")
    p.add_argument("--goal", required=True)
    p.add_argument("--situation", default="")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--explore", type=int, default=1)
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--session", default="", help="names visible in the live session (see build_inventory.py --session)")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("record")
    p.add_argument("--skill", required=True)
    p.add_argument("--situation", required=True)
    p.add_argument("--outcome", required=True)
    p.add_argument("--mode", default="exploit")
    p.add_argument("--goal", default="")
    p.add_argument("--note", default="")
    p.add_argument("--kind", default="skill",
                   choices=["skill", "agent", "mcp", "plugin", "cli", "note", "connector", "design-system", "app", "key", "website"],
                   help="what kind of tool this row is about (one ledger, all kinds)")
    p.add_argument("--loadout", default="", help="loadout name, when the row came from one")
    p.add_argument("--failure-type", default="", choices=["", "auth", "paywall", "cap", "missing", "bug", "output"],
                   help="why it failed: auth/paywall/cap/missing are account or setup problems and do not count "
                        "against the tool; bug/output do")
    p.set_defaults(fn=cmd_record)

    p = sub.add_parser("report")
    p.add_argument("--situation", default="")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("untried")
    p.add_argument("-n", type=int, default=30)
    p.add_argument("--goal", default="")
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--session", default="")
    p.set_defaults(fn=cmd_untried)

    p = sub.add_parser("situations")
    p.set_defaults(fn=cmd_situations)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
