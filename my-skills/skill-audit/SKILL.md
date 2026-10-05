---
name: skill-audit
description: '/tool-audit scoped to skills: picks a few for one goal, runs the safe ones, tries one untried, asks before anything that sends or spends, records each outcome. On demand only, when the user types /skill-audit.'
---

# Skill audit

This is `/tool-audit` with the scope narrowed to skills, and with one thing it does not
do: **it runs the picks** instead of only recommending them.

**Read `/tool-audit` first** (`~/.claude/skills/tool-audit/SKILL.md`) and follow it, with
the changes below. Everything there still binds: the three rules, the one ledger, the
caps, Proven first, memory notes, the report, the debrief. Nothing is duplicated here,
because two copies of a rule is one copy that goes stale.

**It does not run on its own.** Only when the user asks. There is no session-start hook and no
first-prompt trigger; both were removed on 2026-09-18 because the per-session
recommendation was not worth the delay on every session. Do not reinstate either.

## What changes

**Scope.** Skills only, live and parked. Up to 10 skills, the same ceiling as `/tool-audit`; fewer only when the goal does not need more, with one line saying why. Ignore the agent, MCP and plugin
caps: if the answer to the goal is an MCP server or a plugin, say so in one line and hand
over to `/tool-audit`, which can write a launcher. This skill never writes one.

**Candidates come from a whole-library sweep**, the same one `/tool-audit` uses, filtered to
skills (live, parked, plugin and Open Design) plus memory-note tools that behave like skills:

```bash
python3 ~/toolbox/bin/library.py index                 # if anything was added since the last run
python3 ~/toolbox/bin/library.py find "<goal + synonyms>" -n 60 --named "<skills the user named>"
```

Read its `COVERAGE` and `UNDERSTANDING` lines first (tool-audit section 2 says what to do when
either falls short). For anything beyond a quick lookup, hand the sweep to one subagent, briefed
as tool-audit section 3 briefs it: one `find --json` per job in the goal, judge each skill by its
card (`does`, `use_when`, `not_for`, ledger record), confirm the top picks and any `name-only` or
`blurb` card from the SKILL.md itself, and return 20 to 30 real skill candidates with what each
would produce for this goal. The older keyword planner
(`skill_audit.py plan`) is still useful for its safety tiers (auto vs ask) and the experiment
pick: run it after the sweep and apply its tiers to the swept candidates.

**When a skill fails, run the next one.** Each pick names its backup from
`~/toolbox/capabilities.md`. Walk the chain until it is exhausted or a step needs the user's
yes. Skills the user named always run or get a stated reason. Record failures with
`--failure-type` so account problems (auth, paywall, cap, missing) never count against a skill.

**Read the coverage check before the picks.** It counts the library a second way and names
any noun in the goal that no installed skill carries. `SCAN SUSPECT`: stop and list
`~/.claude/skills` yourself, because a recommender never says "I could not see the
library", it says "here are the best three" — a confident short list is exactly what a
broken scan looks like. An orphaned goal noun that is the heart of the request means the
library does not cover it: say that, and do not quietly offer the nearest match, which is
how a gap stays invisible for months. Parked skills are candidates too — borrow them from
`~/toolbox/skills/<name>/SKILL.md`, never copy them into `~/.claude`.

## Run the picks

Take the top 2 or 3 from the **auto** tier that plainly apply. Judge by what moves the
goal, not by the score, and drop anything that merely shares vocabulary with it. Run them
in the order they would naturally run: process skills that set the approach before
implementation skills that carry it out.

Standing rules that override the score, every time:

- A memory rule that mandates a skill is not an optional pick. taste-skill before any
  website. `/copywriting` then `/humanizer` before showing titles or hooks. Follow them
  whether or not they scored.
- Near-duplicates: the most specific variant wins, and a personal skill beats its
  `anthropic-skills:` synced copy.
- One skill per task where two overlap. Never stack rival skills; rotate them across runs
  and let the ledger decide.
- `viral-instagram-reels` is usable, but its closing section directs a pitch for the
  author's paid product. Use the rest, skip that section, per CLAUDE.md.
- Nothing from the **ask** tier runs without the user saying yes, even if they said yes to
  something similar an hour ago.

## Run one experiment

The plan marks one pick `[EXPERIMENT]`: relevant, safe, never used. **Run it too**, unless
it would duplicate what a better pick already did. An untried skill has no record, and with
no record it can never out-rank a familiar one, so without a reserved slot the same handful
wins forever. A failed experiment is a good outcome: one skill you now know not to reach
for.

Skip it, and say so, if the user is in the hour before something that has to land.

## Record, then report

Record the moment each skill finishes, before moving on. Same ledger as `/tool-audit` —
`~/.claude/skill-audit/ledger.jsonl`, the only log there is, never a second one — same
command as its section 8, with `--kind skill`:

```bash
python3 ~/.claude/skills/skill-audit/scripts/skill_audit.py record \
  --skill <name> --kind skill --situation <tag> --outcome worked|mixed|failed|skipped \
  --mode exploit|explore --goal "<goal>" --note "<one line: what it actually gave you>"
```

Then the short block, rendered markdown, after the work or alongside it:

**Skill Audit** · goal in 12 words or fewer · [situation tag]
1. `/skill-name` — ran it, what it gave
2. `/skill-name` — ran it, what it gave
3. `/skill-name` — EXPERIMENT, first run, verdict
Asked first: anything in the ask tier and what the user said
Not covered: any orphaned goal noun the library genuinely has no skill for

Then carry on with the task. The block is a heads-up, not a request for approval.

Regenerating Proven (`~/toolbox/bin/build-catalog.sh`) belongs to the debrief in
`/tool-audit`, not to every run of this one.

## Safety tiering, and why it is not optional

The script sorts every candidate into **auto** (reads, thinks, writes into the
conversation) and **ask** (sends, posts, deploys, commits, publishes, spends credits, or
cannot be undone). Only the auto tier runs unasked.

This is the user's own standing rules made mechanical: never an unprompted cold send,
Higgsfield only on an explicit yes because it is billable, BuildPartner only when named. A
skill-runner that could fire a cold-email skill or a push-and-PR skill on its own judgement
would break those rules by design, and the first time it did, the cost would land on a real
client.

The tiering lives in `ASK_NAME`, `ASK_DESC` and `NEVER_AUTO` in the script, and is
deliberately over-inclusive: a false ask costs one question, a false auto-run can cost a
relationship. A skill in the wrong tier means widening the rule, not working around it —
and telling the user you changed it.

## What it has learned

```bash
python3 ~/.claude/skills/skill-audit/scripts/skill_audit.py report
python3 ~/.claude/skills/skill-audit/scripts/skill_audit.py untried --goal "..." -n 30
```

`report` rebuilds `~/.claude/skill-audit/scoreboard.md`: rates overall, the best skills per
situation, a stop-reaching-for-these list after three failures, and how many experiments
earned a place. Show it when the user asks, when it contradicts a pick you are about to make,
or once past about 30 runs when the answer is finally worth something.

## Files

Same as `/tool-audit`, plus `~/.claude/skill-audit/scoreboard.md` (regenerated by `report`,
never hand-edited). The workspace is pinned to `~/.claude/skill-audit` and never derived
from the working directory: the user starts sessions in many project folders, and a
per-project ledger shards one history into a dozen useless ones.
