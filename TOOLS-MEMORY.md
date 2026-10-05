# TOOLS-MEMORY (toolbox index)

How to use: read this file first for orientation; open only the category file you need under catalog/.
Do not load every catalog/*.md into context. Prefer loadouts/ for curated enable-lists.
Secrets live in mcp/mine (gitignored); share only mcp-templates/.
Regenerate with: ~/toolbox/bin/build-catalog.sh
Agents are parked here; live ~/.claude/agents stays empty unless you copy a loadout.

## Categories

- **web-design** (219): UI/UX, layouts, brand, CSS/design systems. → `catalog/web-design.md`
- **frontend-code** (138): React/Next and browser UI implementation. → `catalog/frontend-code.md`
- **backend-data** (164): APIs, databases, auth, server code. → `catalog/backend-data.md`
- **marketing-copy** (140): SEO, campaigns, positioning, landing copy. → `catalog/marketing-copy.md`
- **social-content** (60): Social posts and channel content. → `catalog/social-content.md`
- **video-audio** (98): Video/audio edit, generation, voice. → `catalog/video-audio.md`
- **research** (149): Search, scrape, investigate, papers. → `catalog/research.md`
- **security-review** (90): Audits, SAST, vuln review. → `catalog/security-review.md`
- **memory-context** (69): Memory, compaction, RAG/context tools. → `catalog/memory-context.md`
- **agent-orchestration** (186): Agents, skills routing, multi-agent flows. → `catalog/agent-orchestration.md`
- **business-ops** (163): CRM, sales, ops, billing, client work. → `catalog/business-ops.md`
- **misc** (27): Uncategorized or cross-cutting tools. → `catalog/misc.md`
- **websites** (37): free web apps with no repo, any job. → `catalog/websites.md` (from websites.json)

## Review dates

- (none open. The 2026-10-04 marketing-skills review was settled early on
  2026-09-21: disabled and moved to session-launch via --plugin-dir, because its
  50 descriptions were 52% of the skill-listing budget. See plugins/INDEX.md.)

## Proven

- cli `gpt-image-2.5` — 6 wins, 2 fail [design-visual, website-design]
- skill `the-humanizer` — 5 wins [content-social, cold-outreach, cold-outreach-copy]
- skill `humanizer` — 4 wins [copywriting, sales-call, client-delivery]
- skill `design-motion-principles` — 4 wins [website-design, website-build, design-visual]
- cli `mlx_whisper` — 4 wins [client-delivery, ops-automation, content-social]
- skill `claude-in-chrome` — 3 wins [research]
- skill `expert-intel` — 3 wins [planning-strategy, sales-call, cold-outreach]
- agent `research-worker` — 3 wins [client-delivery, research]
- skill `animate` — 3 wins [website-design, website-build]
- skill `impeccable` — 3 wins [website-build, client-delivery]
- cli `D4Vinci__Scrapling` — 3 wins [research]
- skill `toolbox-add` — 3 wins [ops-automation, code-build]
- skill `dataviz` — 3 wins [client-delivery, website-build]
- skill `writing-for-agents` — 2 wins [ops-automation, code-build]
- skill `diagram-design` — 2 wins [client-delivery]
- skill `artifact-capabilities` — 2 wins [client-delivery, design-visual]
- skill `agent-reach` — 2 wins [research, ops-automation]
- cli `library.py` — 2 wins [website-design, code-debug]
- skill `delight` — 2 wins [website-design, website-build]
- skill `hyperframes-animation` — 2 wins [website-design, website-build]
- cli `web_fetch.py` — 2 wins [research, ops-automation]
- skill `marketing-skills:customer-research` — 2 wins [planning-strategy]
- skill `marketing-skills:copywriting` — 2 wins [cold-outreach-copy, copywriting]
- agent `general-purpose` — 2 wins [research, code-build]
- mcp `claude-in-chrome` — 2 wins [ops-automation]

## Sources

- public-apis__public-apis — https://github.com/public-apis/public-apis (MIT, pinned 4cfe04f7) `sources/public-apis__public-apis`
- punkpeye__awesome-mcp-servers — https://github.com/punkpeye/awesome-mcp-servers (MIT, pinned 393b4e9f) `sources/punkpeye__awesome-mcp-servers`
- sindresorhus__awesome — https://github.com/sindresorhus/awesome (CC0-1.0, pinned bc98e517) `sources/sindresorhus__awesome`
- ripienaar__free-for-dev — https://github.com/ripienaar/free-for-dev (none found, pinned unpinned) `(not cloned)`
- mnfst__awesome-free-llm-apis — https://github.com/mnfst/awesome-free-llm-apis (CC0-1.0, pinned 167013ff) `sources/mnfst__awesome-free-llm-apis`
- jleesubai-sys__pipeline-pack-gist — https://gist.github.com/jleesubai-sys/e72229efc4fef3252570da5a1436e5ee (none found, pinned ed53e9ad) `sources/jleesubai-sys__pipeline-pack-gist`
- public-api-lists__public-api-lists — https://github.com/public-api-lists/public-api-lists (MIT, pinned 6491e2fb) `sources/public-api-lists__public-api-lists`

## Recently added

- skill: upskill [social-content, agent-orchestration] `skills/upskill/SKILL.md`
- skill: job-scraper [social-content, research] `skills/job-scraper/SKILL.md`
- skill: job-application-assistant [marketing-copy, social-content] `skills/job-application-assistant/SKILL.md`
- skill: gsap-utils [frontend-code] `skills/gsap-utils/SKILL.md`
- skill: gsap-timeline [frontend-code] `skills/gsap-timeline/SKILL.md`
- skill: gsap-scrolltrigger [frontend-code] `skills/gsap-scrolltrigger/SKILL.md`
- skill: gsap-react [frontend-code, memory-context] `skills/gsap-react/SKILL.md`
- skill: gsap-plugins [backend-data] `skills/gsap-plugins/SKILL.md`
- skill: gsap-performance [web-design, frontend-code] `skills/gsap-performance/SKILL.md`
- skill: gsap-frameworks [frontend-code] `skills/gsap-frameworks/SKILL.md`
- skill: gsap-core [frontend-code, backend-data] `skills/gsap-core/SKILL.md`
- skill: replica-test [frontend-code, research] `skills/replica-test/SKILL.md`
- skill: replica-recon [frontend-code, research] `skills/replica-recon/SKILL.md`
- skill: replica-launch [marketing-copy] `skills/replica-launch/SKILL.md`
- skill: replica-entrepreneur [backend-data, social-content] `skills/replica-entrepreneur/SKILL.md`
- skill: replica-diff [web-design] `skills/replica-diff/SKILL.md`
- skill: replica-design [web-design, frontend-code] `skills/replica-design/SKILL.md`
- skill: replica-deploy [web-design, frontend-code] `skills/replica-deploy/SKILL.md`
- skill: replica-build [research] `skills/replica-build/SKILL.md`
- skill: replica-brand [web-design, frontend-code] `skills/replica-brand/SKILL.md`

