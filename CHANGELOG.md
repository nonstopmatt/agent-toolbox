# toolbox CHANGELOG

## 2026-10-01 — websites knowledge base, loadouts of up to 10 tools

- `websites.json`: free web apps with no repo, with free tier, account, API, limits and a
  `verified` date per site. Seeded with 15 common ones, all marked `not checked` (the cloud
  session that wrote them couldn't reach the sites). `bin/build-catalog.sh` writes
  `catalog/websites.md` from it; `bin/library.py` indexes each as kind `website` with its own
  search quota, so websites show up in every audit
- `/toolbox-add`: a tool that is only a website is now logged in `websites.json` (Step 2d)
  instead of being turned away. Still no sign-ups, trials or cards
- `/tool-audit`: a loadout is up to 10 tools across at least three kinds (was 2 to 4 picks
  under per-kind caps of 5). Per-kind ceilings: skills 10, agents 10, websites 5, MCP 3,
  plugins 2. A loadout under 10 has to say why. Shortlist widened to 30 to 40, discovery
  proposes up to 10 and runs one web search for free web apps
- `/skill-audit`: up to 10 skills; the ledger accepts `--kind website`
- `bin/pull.sh`: pull repo changes made elsewhere and refresh the live skills before the next
  `sync.sh`, which would otherwise copy the old live skills back over them

## 2026-09-30 — YouTube Ua0APTMVcb8, AI LABS "8 GitHub repos" (7 added, 1 already here)

Full table and claim check: `inbox/youtube-Ua0APTMVcb8-2026-09-30.md`. Nothing installed, no install
script run, nothing in a clone executed. Session-launch MCP configs written for three of them, with
telemetry switched off.

- agent-tool: `reticlehq__reticle` · **mixed license** (Apache-2.0 SDK, FSL-1.1-ALv2 server, paid Enterprise for `ee`) · pinned 96a4d7ab · nothing copied, `mcp-templates/reticle.json` · installer writes MCP config into every agent; SKILL.md says never ask the user, send vendor feedback, ask for a star
- agent-tool: `JayPokale__Chisle` · MIT · pinned 0c21d856 · 3 skills copied · **rival of live Ponytail**; plugin has 3 hooks, one trims tool output, one pings npm
- agent-tool: `ibelick__ui-skills` · MIT · pinned 2eec38c1 · 6 skills copied, `mcp-templates/ui-skills.json` · registry text comes from other authors at run time
- agent-tool: `Q00__ouroboros` · MIT · pinned 9840dbf0 · nothing copied, `mcp-templates/ouroboros.json` · skills tell the agent to star the repo and self-upgrade; PostHog telemetry on by default; 3 hooks
- agent-tool: `FloWritesCode__fwc-swiftui-skills` · MIT · pinned 69f95747 · 2 skills copied · markdown only
- agent-tool: `edonadei__caliper` · MIT · pinned ff72f22b · 2 skills copied · needs the `caliper` CLI; every eval spends usage
- agent-tool: `dmmulroy__anti-slop` · MIT · pinned c44ef22c · 1 skill copied with its rules · JS/TS only, adds dev dependencies to the target repo
- have already: img2threejs (`skills/img2threejs`)
- not added: Manufact (sponsor, hosted service), AI Labs Pro, The Roundup

## 2026-09-21 — whole-library sweep, fallback chains, health check

- `bin/library.py`: `index` (every source, full descriptions, local Ollama embeddings), `health`, `find` (semantic + keyword, per-kind quota, `COVERAGE searched N of N`, `--named` tools never dropped)
- `capabilities.md`: fallback chains per job; the audit walks them on any failure
- `health-overrides.json`: paywalls, spend caps, signed-out connectors
- tool-audit and skill-audit rewritten: sweep the whole library, sweep subagent shortlist, backup per slot, user-named tools mandatory, cross-kind quota
- ledger: `--failure-type auth|paywall|cap|missing|bug|output`; only bug/output count toward FAILED TWICE

## 2026-09-21 — batch B-F: 4 Instagram posts + 1 reel report (14 added)

Tables: `inbox/instagram-{Dcv9HtHDLDZ,Dc-zw_Vicxs,DdfLtWFuETI,DdZN9jvCVHg}-2026-09-21.md`; link F report:
`inbox/usage-extension-2026-09-21.md`. Nothing installed, no install script run, nothing posted on Instagram.

- agent-tool: `AgriciDaniel__claude-ads` · MIT · pinned ac216449 · **34 skills + 25 agents copied** · rival to marketing-skills ads
- agent-tool: `JCodesMore__ai-website-cloner-template` · MIT · pinned 0fc4dca3 · borrow in place
- agent-tool: `hugohe3__ppt-master` · MIT · pinned 2a05498f · 254 MB, borrow in place
- agent-tool: `nowork-studio__notfair-plugin` (was toprank) · MIT · pinned 7270136d · nothing copied: vendor MCP + self-upgrade skill
- agent-tool: `ethanplusai__harvey` · MIT · pinned 822e84e7 · nothing copied · sends real email; keep require_approval on
- application: open-seo (MIT), changedetection.io (Apache-2.0), PaddleOCR (Apache-2.0), AutoHedge (MIT),
  Vibe-Trading (MIT), FinceptTerminal (**AGPL-3.0**), agentic-inbox (Apache-2.0), camofox-browser (MIT),
  Open-Generative-AI (MIT, was Open-Higgsfield-AI) · catalog lines only
- have already: trycompai/crm (`~/vb-crm`), Scrapling, HyperFrames; context-mode repeated in link C under the label "ClawRouter"
- link E: five hosted video sites, no repos, nothing added
- link A follow-ups: context-mode clone removed (catalog line only); open-code-review, worktrunk and i-have-adhd
  marked BORROW-ONLY; ECC's catalog line now says why it is parked (local note, not in the repo)

## 2026-09-21 — batch A: YouTube 1fHsIveXRa8 (12 added)

Full table: `inbox/youtube-1fHsIveXRa8-2026-09-21.md`. Nothing installed, no install script run.

- agent-tool: `alibaba__open-code-review` · Apache-2.0 · pinned 070805f8 · 2 skills copied · needs `ocr` + LLM key
- agent-tool: `ayghri__i-have-adhd` · MIT · pinned 839872f9 · 1 skill copied · plugin form has a SessionStart hook
- agent-tool: `mksglu__context-mode` · **Elastic-2.0** · catalog line only, not cloned · MCP server + 6 hook events
- agent-tool: `max-sixty__worktrunk` · MIT/Apache-2.0 · pinned abd7acaa · 2 skills copied · needs `wt`
- agent-tool: `trainingsites__campus-ai-os` · MIT · pinned 4f169825 · 45 skills not extracted (niche)
- agent-tool: `openai__plugins` · **no license** · pinned 1dc19589 · nothing copied
- application: gods-eye-view (MIT), WeKnora (MIT), Logic-Loop (GPL-3.0), claude-dashboard (MIT),
  deckgauge (**FSL-1.1**), reckoner (GPL-3.0) · catalog lines only
- have already: ECC (`ecc` plugin, disabled), Agent Skills (`agent-skills` plugin, disabled), Claude Code

## 2026-09-21 — Public-readiness fixes

- `plugins/INDEX.md` is local only; the repo gets `plugins/INDEX.public.md` (plugin id,
  enabled from live settings, what it contributes). Catalog plugin lines no longer carry cache paths.
- Skills whose license reserves all rights are dropped from every committed file (4 today).
- `my-skills/` no longer names its owner; tool-audit's machine-specific lookups moved to
  `~/.config/toolbox/tool-audit.json`, which is not committed.

## 2026-09-21 — Prompt 3: private GitHub repo

- Repo holds the index, catalog, manifest, templates, `bin/` (build-catalog, sync,
  bootstrap) and `my-skills/` (tool-audit, skill-audit, toolbox-add,
  self-improvement-report). No third-party code: `agents/`, `skills/`, `sources/`,
  `repos/`, `parked/`, `mcp/` and `inbox/` are gitignored.
- `manifest.json`: commits pinned to full SHAs; added `msitarzewski__agency-agents`
  (the source of `agents/`).
- `bin/sync.sh` scans the staged snapshot (secrets, home paths, private names in
  `~/.config/toolbox/private-names.txt`) and aborts on any hit. Clean filters in
  `.gitattributes` write `~` for home paths and drop Proven "last:" notes in the committed copy.
- `/toolbox-add` now runs `sync.sh` as its last step.

## 2026-09-21 — Phase 5: catalogued the Instagram haul (10 items)

Source: [an Instagram carousel](https://www.instagram.com/p/Dcs-8irjYBN/), filed in
`inbox/instagram-2026-09-20.md`. Nothing was installed. No install script from any
README was run. `manifest.json` and this file were created in this pass, and the
three reference-lists already sitting in `sources/` were backfilled with pinned
commits.

- reference-list: `public-apis__public-apis` · MIT · pinned 4cfe04f7
- reference-list: `punkpeye__awesome-mcp-servers` · MIT · pinned 393b4e9f
- reference-list: `sindresorhus__awesome` · CC0-1.0 · pinned bc98e517
- reference-list: `ripienaar__free-for-dev` · **no LICENSE found, not cloned**, link only
- application: `ollama__ollama` · MIT · pinned 6383a0fa · **already installed**,
  `~/.local/bin/ollama`, daemon answering on 127.0.0.1:11434 (HTTP 200)
- application: `OpenHands__OpenHands` · MIT · pinned a0736482 · needs keys + Docker
- application: `langflow-ai__langflow` · MIT · pinned 5621dcfd · stores provider keys
- application: `Shubhamsaboo__awesome-llm-apps` · Apache-2.0 · pinned 9e860951 · read as reference
- **agent-tool**: `nexu-io__open-design` · Apache-2.0 · pinned ac611540
  - ships 277 skill dirs (163 `skills/`, 114 `design-templates/`) and one MCP server
  - MCP server needs the `od` daemon on PATH: not installed, so not extracted
  - 11 skills extracted (below); the other 266 stay in the repo, borrowable by path
  - 11 of its skills duplicate ones the user already has (taste-skill, ui-ux-pro-max,
    hyperframes, copywriting, critique, marketing-psychology, remotion, …)
- **agent-tool**: `D4Vinci__Scrapling` · BSD-3-Clause · pinned 2b160ee1
  - ships its own agent skill; extracted as `skills/scrapling-official`
  - needs `pip install scrapling` plus browser binaries before anything runs; its
    MCP server is the `scrapling-mcp` console script from that same install
  - anti-bot bypass carries ToS risk, so not for client work without a decision

### Extracted into `skills/` (12, all borrowable, none installed)

| skill | from | why |
|---|---|---|
| `scrapling-official` | Scrapling | anti-bot scraping path while Firecrawl credits are out |
| `social-x-post-card`, `social-reddit-card`, `social-spotify-card` | Open Design | post-card overlays for podcast clips |
| `frame-macos-notification`, `frame-glitch-title`, `frame-light-leak-cinema`, `frame-logo-outro`, `vfx-text-cursor` | Open Design | title, outro and transition frames for clips |
| `chat-motion-overlay` | Open Design | chat-bubble motion from a transcript, ships its own agents |
| `mockup-device-3d` | Open Design | device mockups for client site pitches |
| `resume-modern` | Open Design | single-page A4 resume, for the 2026 job search |

## 2026-09-21 — reference-list: mnfst/awesome-free-llm-apis

- reference-list: `mnfst__awesome-free-llm-apis` · CC0-1.0 · pinned 167013ff · `sources/`
- Why: reference for tuning OmniRoute's free-model ladder (from the "Awesome Free LLM APIs" reel,
  `inbox/usage-extension-2026-09-21.md`; the reel's gateway pitch was discarded, the list kept).
- Not catalogued item by item. Its `scripts/` were not run. Maintained by Manifest, who sell the
  gateway it links to; check each provider's training-on-prompts terms before routing client work.

## 2026-09-21 — captions D/E/F folded in (nothing added)

- Source: `inbox/instagram-captions-2026-09-21.md` (Yappy, read-only).
- D (@seb.ai): names Harvey, Claude Code, GitHub. Harvey was already `repos/ethanplusai__harvey`; caption's
  "nothing gets sent until you approve it" matches `require_approval=True`. No change.
- E (@moh_frame): names nothing. Handle corrected in the inbox file.
- F (@nick_saraev): names FreeLLMAPI, Claude Code, `#omniroute`. **Correction:** FreeLLMAPI is a real repo
  (`tashfeenahmed/freellmapi`, MIT, 27.7k stars), not a misnaming of the mnfst list. Fact-check redone; outcome
  still **discard**, since OmniRoute already does the job locally. Not catalogued.

## 2026-09-29 — my-skills: vet-and-install-kit (new, live)
Matt approved the skill review's recommendation. Source `my-skills/vet-and-install-kit/`, live copy
`~/.claude/skills/vet-and-install-kit/`. Owns vetting, containment and proof for any third-party kit
that will run or be launched, plus removal verification; `/toolbox-add` still owns catalogue-without-running.
Built from observations #1 #6 #19 #21-#24 #37 #38 #40 #42 #45 #53 #54 #69.
Also on 9/29: 20 parked skills in `skills/` got their 2026-09-19 review edits installed (backups in
`~/.claude/skill-updates/2026-09-19-review2/_live-backup-2026-09-29/`).
