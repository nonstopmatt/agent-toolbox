# TOOLS-MEMORY (toolbox index)

How to use: read this file first for orientation; open only the category file you need under catalog/.
Do not load every catalog/*.md into context. Prefer loadouts/ for curated enable-lists.
Secrets live in mcp/mine (gitignored); share only mcp-templates/.
Regenerate with: ~/toolbox/bin/build-catalog.sh
Agents are parked here; live ~/.claude/agents stays empty unless you copy a loadout.

## Categories

- **web-design** (179): UI/UX, layouts, brand, CSS/design systems. → `catalog/web-design.md`
- **frontend-code** (100): React/Next and browser UI implementation. → `catalog/frontend-code.md`
- **backend-data** (131): APIs, databases, auth, server code. → `catalog/backend-data.md`
- **marketing-copy** (129): SEO, campaigns, positioning, landing copy. → `catalog/marketing-copy.md`
- **social-content** (53): Social posts and channel content. → `catalog/social-content.md`
- **video-audio** (80): Video/audio edit, generation, voice. → `catalog/video-audio.md`
- **research** (124): Search, scrape, investigate, papers. → `catalog/research.md`
- **security-review** (76): Audits, SAST, vuln review. → `catalog/security-review.md`
- **memory-context** (59): Memory, compaction, RAG/context tools. → `catalog/memory-context.md`
- **agent-orchestration** (142): Agents, skills routing, multi-agent flows. → `catalog/agent-orchestration.md`
- **business-ops** (146): CRM, sales, ops, billing, client work. → `catalog/business-ops.md`
- **misc** (4): Uncategorized or cross-cutting tools. → `catalog/misc.md`

## Review dates

- (none open. The 2026-10-04 marketing-skills review was settled early on
  2026-09-21: disabled and moved to session-launch via --plugin-dir, because its
  50 descriptions were 52% of the skill-listing budget. See plugins/INDEX.md.)

## Proven

- cli `gpt-image-2.5` — 5 wins, 1 fail [design-visual, website-design]
- skill `humanizer` — 3 wins [copywriting, sales-call, client-delivery]
- skill `the-humanizer` — 3 wins [content-social, cold-outreach]
- skill `claude-in-chrome` — 2 wins [research]
- skill `expert-intel` — 2 wins [planning-strategy, sales-call]
- skill `diagram-design` — 2 wins [client-delivery]
- agent `research-worker` — 2 wins [client-delivery, research]
- skill `artifact-capabilities` — 2 wins [client-delivery, design-visual]
- skill `animate` — 2 wins [website-design, website-build]
- skill `delight` — 2 wins [website-design, website-build]
- skill `design-motion-principles` — 2 wins [website-design, website-build]
- skill `hyperframes-animation` — 2 wins [website-design, website-build]
- skill `social` — 2 wins, 1 fail [content-social]
- skill `task-observer` — 1 win [ops-automation]
- skill `update-config` — 1 win [ops-automation]
- skill `writing-for-agents` — 1 win [ops-automation]
- skill `Pricing Analyst` — 1 win [planning-strategy]
- agent `Pricing Analyst` — 1 win [client-delivery]
- agent `Proposal Strategist` — 1 win [client-delivery]
- skill `copywriting` — 1 win [client-delivery]
- skill `yt-script` — 1 win [content-social]
- skill `b2b-copywriting` — 1 win [cold-outreach]
- skill `web-design-guidelines` — 1 win [design-visual]
- cli `nano-banana-replicate` — 1 win [design-visual]
- note `reference_flat_brand_icon_sets` — 1 win [design-visual]

## Sources

- public-apis__public-apis — https://github.com/public-apis/public-apis (MIT, pinned 4cfe04f7) `sources/public-apis__public-apis`
- punkpeye__awesome-mcp-servers — https://github.com/punkpeye/awesome-mcp-servers (MIT, pinned 393b4e9f) `sources/punkpeye__awesome-mcp-servers`
- sindresorhus__awesome — https://github.com/sindresorhus/awesome (CC0-1.0, pinned bc98e517) `sources/sindresorhus__awesome`
- ripienaar__free-for-dev — https://github.com/ripienaar/free-for-dev (none found, pinned unpinned) `(not cloned)`
- mnfst__awesome-free-llm-apis — https://github.com/mnfst/awesome-free-llm-apis (CC0-1.0, pinned 167013ff) `sources/mnfst__awesome-free-llm-apis`

## Recently added

- agent: visual-designer [web-design, business-ops] `agents/visual-designer.md`
- agent: source-verifier [research] `agents/source-verifier.md`
- agent: skill-reviewer [memory-context, agent-orchestration] `agents/skill-reviewer.md`
- agent: research-worker [backend-data, research] `agents/research-worker.md`
- agent: release-verifier [research, security-review] `agents/release-verifier.md`
- agent: format-adapter [business-ops] `agents/format-adapter.md`
- agent: creative-strategist [marketing-copy, business-ops] `agents/creative-strategist.md`
- agent: copy-writer [marketing-copy, agent-orchestration] `agents/copy-writer.md`
- agent: audit-youtube [web-design, backend-data] `agents/audit-youtube.md`
- agent: audit-x [web-design, backend-data] `agents/audit-x.md`
- agent: audit-tracking [backend-data, marketing-copy] `agents/audit-tracking.md`
- agent: audit-tiktok [backend-data, social-content] `agents/audit-tiktok.md`
- agent: audit-snapchat [web-design, backend-data] `agents/audit-snapchat.md`
- agent: audit-regulatory-compliance [backend-data, marketing-copy] `agents/audit-regulatory-compliance.md`
- agent: audit-reddit [web-design, backend-data] `agents/audit-reddit.md`
- agent: audit-policy-compliance [web-design, backend-data] `agents/audit-policy-compliance.md`
- agent: audit-pinterest [web-design, backend-data] `agents/audit-pinterest.md`
- agent: audit-microsoft [backend-data, marketing-copy] `agents/audit-microsoft.md`
- agent: audit-meta [backend-data, research] `agents/audit-meta.md`
- agent: audit-linkedin [backend-data, marketing-copy] `agents/audit-linkedin.md`

