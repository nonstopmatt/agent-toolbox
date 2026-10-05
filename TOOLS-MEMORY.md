# TOOLS-MEMORY (toolbox index)

How to use: read this file first for orientation; open only the category file you need under catalog/.
Do not load every catalog/*.md into context. Prefer loadouts/ for curated enable-lists.
Secrets live in mcp/mine (gitignored); share only mcp-templates/.
Regenerate with: ~/toolbox/bin/build-catalog.sh
Agents are parked here; live ~/.claude/agents stays empty unless you copy a loadout.

## Categories

- **web-design** (190): UI/UX, layouts, brand, CSS/design systems. → `catalog/web-design.md`
- **frontend-code** (108): React/Next and browser UI implementation. → `catalog/frontend-code.md`
- **backend-data** (131): APIs, databases, auth, server code. → `catalog/backend-data.md`
- **marketing-copy** (132): SEO, campaigns, positioning, landing copy. → `catalog/marketing-copy.md`
- **social-content** (53): Social posts and channel content. → `catalog/social-content.md`
- **video-audio** (80): Video/audio edit, generation, voice. → `catalog/video-audio.md`
- **research** (128): Search, scrape, investigate, papers. → `catalog/research.md`
- **security-review** (80): Audits, SAST, vuln review. → `catalog/security-review.md`
- **memory-context** (60): Memory, compaction, RAG/context tools. → `catalog/memory-context.md`
- **agent-orchestration** (151): Agents, skills routing, multi-agent flows. → `catalog/agent-orchestration.md`
- **business-ops** (146): CRM, sales, ops, billing, client work. → `catalog/business-ops.md`
- **misc** (9): Uncategorized or cross-cutting tools. → `catalog/misc.md`
- **websites** (15): free web apps with no repo, any job. → `catalog/websites.md` (from websites.json)

## Review dates

- (none open. The 2026-10-04 marketing-skills review was settled early on
  2026-09-21: disabled and moved to session-launch via --plugin-dir, because its
  50 descriptions were 52% of the skill-listing budget. See plugins/INDEX.md.)

## Proven

- cli `gpt-image-2.5` — 6 wins, 2 fail [design-visual, website-design]
- skill `the-humanizer` — 4 wins [content-social, cold-outreach, cold-outreach-copy]
- skill `design-motion-principles` — 4 wins [website-design, website-build, design-visual]
- skill `claude-in-chrome` — 3 wins [research]
- skill `expert-intel` — 3 wins [planning-strategy, sales-call, cold-outreach]
- skill `humanizer` — 3 wins [copywriting, sales-call, client-delivery]
- agent `research-worker` — 3 wins [client-delivery, research]
- skill `animate` — 3 wins [website-design, website-build]
- cli `D4Vinci__Scrapling` — 3 wins [research]
- skill `writing-for-agents` — 2 wins [ops-automation, code-build]
- skill `diagram-design` — 2 wins [client-delivery]
- skill `artifact-capabilities` — 2 wins [client-delivery, design-visual]
- cli `library.py` — 2 wins [website-design, code-debug]
- skill `delight` — 2 wins [website-design, website-build]
- skill `hyperframes-animation` — 2 wins [website-design, website-build]
- skill `impeccable` — 2 wins [website-build, client-delivery]
- skill `marketing-skills:customer-research` — 2 wins [planning-strategy]
- skill `toolbox-add` — 2 wins [ops-automation, code-build]
- agent `general-purpose` — 2 wins [research, code-build]
- cli `mlx_whisper` — 2 wins [client-delivery]
- skill `dataviz` — 2 wins [client-delivery]
- skill `social` — 2 wins, 1 fail [content-social]
- skill `task-observer` — 1 win [ops-automation]
- skill `update-config` — 1 win [ops-automation]
- skill `Pricing Analyst` — 1 win [planning-strategy]

## Sources

- public-apis__public-apis — https://github.com/public-apis/public-apis (MIT, pinned 4cfe04f7) `sources/public-apis__public-apis`
- punkpeye__awesome-mcp-servers — https://github.com/punkpeye/awesome-mcp-servers (MIT, pinned 393b4e9f) `sources/punkpeye__awesome-mcp-servers`
- sindresorhus__awesome — https://github.com/sindresorhus/awesome (CC0-1.0, pinned bc98e517) `sources/sindresorhus__awesome`
- ripienaar__free-for-dev — https://github.com/ripienaar/free-for-dev (none found, pinned unpinned) `(not cloned)`
- mnfst__awesome-free-llm-apis — https://github.com/mnfst/awesome-free-llm-apis (CC0-1.0, pinned 167013ff) `sources/mnfst__awesome-free-llm-apis`

## Recently added

- mcp-mine: ui-skills [web-design] `mcp/mine/ui-skills.json`
- mcp-mine: ouroboros [misc] `mcp/mine/ouroboros.json`
- mcp-mine: reticle [misc] `mcp/mine/reticle.json`
- skill: install-anti-slop [misc] `skills/install-anti-slop/SKILL.md`
- skill: grill-skill [web-design, agent-orchestration] `skills/grill-skill/SKILL.md`
- skill: evaluate-skill [security-review, agent-orchestration] `skills/evaluate-skill/SKILL.md`
- skill: chisle-review [misc] `skills/chisle-review/SKILL.md`
- skill: chisle-audit [marketing-copy, security-review] `skills/chisle-audit/SKILL.md`
- skill: chisle [marketing-copy] `skills/chisle/SKILL.md`
- skill: improve-ui [web-design, research] `skills/improve-ui/SKILL.md`
- skill: fixing-motion-performance [web-design, frontend-code] `skills/fixing-motion-performance/SKILL.md`
- skill: fixing-metadata [web-design, marketing-copy] `skills/fixing-metadata/SKILL.md`
- skill: fixing-accessibility [web-design, security-review] `skills/fixing-accessibility/SKILL.md`
- skill: create-design-md [web-design] `skills/create-design-md/SKILL.md`
- skill: baseline-ui [web-design] `skills/baseline-ui/SKILL.md`
- skill: swiftui-iphone-duo [web-design, frontend-code] `skills/swiftui-iphone-duo/SKILL.md`
- skill: swiftui-liquid-glass [web-design, frontend-code] `skills/swiftui-liquid-glass/SKILL.md`
- skill: gstack-browse [frontend-code, research] `skills/gstack-browse/SKILL.md`
- mcp-mine: scrapling [misc] `mcp/mine/scrapling.json`
- agent: visual-designer [web-design, business-ops] `agents/visual-designer.md`

