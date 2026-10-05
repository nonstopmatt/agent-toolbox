# SETUP: for the coding agent reading this

You are setting up a tool shelf for a person who collects a lot of agent tools (skills, agent personas, MCP servers, plugins, whole applications). The failure this prevents: every installed tool adds text to every prompt, so an agent with everything installed starts each session nearly full, compacts constantly and gets worse. The fix is to keep tools **parked** outside your live configuration and bring in only what one task needs.

## The one rule

**Nothing installs into your live config.** Your live config is whatever your harness loads at session start: for Claude Code, `~/.claude/skills`, `~/.claude/agents`, the plugin list and the MCP server list. For other agents, the equivalent directories and config files. New tools go onto the shelf. When one proves itself over several tasks, the person promotes it by hand.

## How it works

1. **Park everything.** The shelf is one folder (`~/toolbox`). Third-party code goes in `repos/`, `sources/`, `agents/`, `skills/` or `parked/`, all gitignored. MCP server configs with real credentials go in `mcp/` (gitignored). `mcp-templates/` holds the same configs with `${VAR}` placeholders.
2. **Index it.** `bin/build-catalog.sh` reads the shelf (no AI, files only) and writes `TOOLS-MEMORY.md` plus one `catalog/<job>.md` per category. Each line is `kind | name | what it is | path`. Applications and agent-tools also carry their license and risks.
3. **Sweep the whole library, every task.** `bin/library.py index` builds one search index over everything: the catalog (with full descriptions read from each file, not truncated lines), live and plugin skills, any extra skill or design-system folders, notes that describe local tools, MCP servers, the live session's connectors and built-ins (listed in `index/session.txt`), free websites from `websites.json`, and the names of your credential files (never their contents). `bin/library.py profile` then has a local Ollama model (default `gemma4:e4b`, thinking off, about 3s a tool) read each tool's full source and write a card: what it does, when to use it, when not, input, output, what it needs. Cards are cached by source hash, so later runs only touch new or changed tools. `index` embeds each item's card with a local Ollama model, so it costs nothing and nothing leaves the machine. `bin/library.py find "<goal>" --named "<tools the person asked for>"` searches all of it by meaning plus keywords, gives every kind of tool a quota so skills can't crowd out agents or MCP servers, and prints a `COVERAGE searched N of N` line. If Ollama is down it says so and falls back to keywords instead of quietly narrowing. Paths are configurable in `library-sources.json`; missing sources are skipped.
4. **Shortlist with a subagent.** For anything bigger than a quick lookup, one subagent opens the file behind each plausible candidate and returns 30 to 40 real options with what each needs to run. Reading happens there, so breadth costs your main context nothing.
5. **Pick a loadout of up to 10 tools with a backup per slot.** Up to 10 tools across at least three kinds (skills, agents, websites, MCP servers, plugins), with at most 3 MCP servers, 2 plugins and 5 websites, because servers and plugins load their tool definitions every turn. The caps limit what runs, never what is searched, and a loadout under 10 says why the rest would not help. Free websites with no repo live in `websites.json` and are searched like everything else. `bin/library.py health` plus `health-overrides.json` mark what is usable right now (paywalled, over a spend cap, signed out). `capabilities.md` lists, for each job, every tool that can do it in order. **When a tool fails, walk its chain to the next one**, and stop only when the chain is exhausted or the next step needs the person's approval. Tools the person names are mandatory: run them or say exactly why not.
6. **Borrow or session-launch.** Borrow a skill or agent by reading its file and following it for this task. Session-launch an MCP server or plugin for one terminal only, for example `claude --mcp-config <file>` or `claude --plugin-dir <path>` from a script in `loadouts/`. Never write them into the live config.
7. **Debrief into a ledger.** After the task, append one JSON line per tool used: what it was for, whether it helped, and for a failure, why (`auth`, `paywall`, `cap` and `missing` are account problems and never count against the tool; `bug` and `output` do). The Proven section of `TOOLS-MEMORY.md` is generated from that ledger, so what works rises to the top by itself.

Anything that sends, posts, deploys, commits, publishes or spends credits needs the person's approval every time, however well the tool scored.

## Adopting it

1. Clone this repo to `~/toolbox`.
2. Run `bin/bootstrap.sh`. It re-clones every upstream in `manifest.json` at its pinned commit, rebuilds the catalog, copies the skills in `my-skills/` into your skills directory (pass a second argument for a non-Claude agent; it never overwrites an existing skill), and lists the MCP templates that need credentials.
3. Put credentials in environment variables or a key file that a loadout script exports. Never put them in a URL or in command arguments, since those end up in logs and process lists.
4. Add tools with the `toolbox-add` skill. It clones into quarantine, runs no install script, reads the repo, and records the upstream, license and pinned commit in `manifest.json`.

Two parts of the original shelf can't be rebuilt from the manifest yet. `agents/` came from `msitarzewski/agency-agents` through its installer, so run that installer from `repos/` and move the output into `agents/`. The original toolbox also holds skills from packs whose origin wasn't recorded. Those aren't in this repo, and bootstrap rebuilds only what `manifest.json` tracks, so expect a smaller toolbox than the one this repo came from.

## Keeping a public copy clean

`bin/sync.sh` rebuilds the catalog, stages the repo, and scans the exact staged snapshot before committing. It checks for credential patterns (and uses gitleaks if installed), home-folder paths, and a private list of names kept outside the repo (`~/.config/toolbox/private-names.txt`). Any hit aborts the sync. Known false positives go in `bin/secret-allowlist.txt` as `path:line`. Clean filters in `.gitattributes` make sure the committed copy never contains your home path, and they strip the task notes from the Proven list.

## Agent-agnostic notes

The layout is plain files: markdown, JSON and shell. Skills follow the `SKILL.md` convention (YAML frontmatter with `name` and `description`, then instructions), which several agents read. The Claude Code specifics are the paths above and the `--mcp-config` and `--plugin-dir` flags. On another agent, swap in its equivalent for "load this for one session only".
