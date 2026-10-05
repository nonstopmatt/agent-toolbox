# toolbox CHANGELOG

## 2026-10-05 — resolved 3 tools from the Instagram batch; OmniSocials launcher saved
- agent-tool `guillaumemeyer__watermarks-remover` · 1181fd4 · MIT · serves: agency marketing, content production · ships 2 skills (clean-user-facing-text copied to skills/; remove-ai-marks needs the repo's service), 1 plugin hook (not enabled) · risks: PostToolUse hook in the plugin form, a SynthID watermark-stealing research module, keep required AI disclosures
- website AI Model Watch (aimodelwatch.dev): free JSON API of model prices, context windows and deprecations, no key; the MIT dataset repo is cited, not cloned
- website Ghost (gotghost.io): website-to-MCP-tools, 500 free generations a month; claims MIT but no public repo found. TryGhost/Ghost (the publishing platform) is a different product and was not added
- an OmniSocials MCP session launcher in `loadouts/` (private, left out of the public snapshot); reads its key from a file, holds none
- still unresolved from the batch: Swokei

## 2026-10-04 — i-have-adhd live; OpenClaude removed
- `ayghri__i-have-adhd` promoted from borrow-only to live at the user's request: skill folder only (no plugin, no hook), `disable-model-invocation` kept, so it runs on `/i-have-adhd` until "stop adhd mode"; proven with one headless run from another folder
- `Twigpine__openclaude` removed from the manifest at the user's request (its NOTICE says it derives from Anthropic's proprietary Claude Code)
- Switchyard: not installing; stitch-skills: shelved (no Stitch API key)

## 2026-10-04 — added 100 repos/apps and 22 websites from 48 Instagram posts
- source: 48 posts the user saved (47 links + 1 screenshot), read with agent-reach (OpenCLI), yt-dlp captions, local whisper and Vision OCR; full table in `inbox/instagram-batch-2026-10-04.md`
- not added: 5 discarded (prank, novelty, ToS-risky, pirated font), 2 duplicates, 4 unresolved names, 14 set aside (gig marketplaces, piracy), 40 already on the shelf, 3 only named in memory notes
- nothing installed; agent-tools shallow-cloned and pinned, applications catalogued only
- application `inovector__mixpost` · not cloned · MIT (Lite); Pro and Enterprise are commercial · free Lite publishes only to Facebook Pages, Mastodon and X: no Instagram, LinkedIn, YouTube or TikTok
- reference-list `jleesubai-sys__pipeline-pack-gist` · ed53e9ad · none found · no license: read for ideas, do not republish
- agent-tool `CodeAbra__iai-personal-memory-engine` · c400059a · MIT · duplicates the user's own MEMORY.md auto-memory system and task-observer log: running both would create two separate automatic memory layers wri
- agent-tool `K-Dense-AI__scientific-agent-skills` · 15498840 · MIT · creator (K-Dense-AI) flags its own README as a funnel toward their paid co-scientist desktop app - the skill pack itself stays MIT/open
- agent-tool `JuliusBrussee__caveman` · 65719433 · Apache-2.0 · RIVAL of the user's live Ponytail plugin (same persistent-mode concept, same 'stop X / normal mode' switch) and of the parked Chisle skill - all
- agent-tool `buildwithneej__onefifty` · not cloned · none (not a repo; posted verbatim on a lead-magnet landing page) · no license, no repo, no stars to verify: distributed as a copy-paste lead-magnet, not an open-source release
- agent-tool `buildwithneej__dumbo` · not cloned · none (not a repo; posted verbatim on a lead-magnet landing page) · no license, no repo, no stars; same informal lead-magnet distribution as onefifty
- agent-tool `better-auth__better-icons` · 033316ec · MIT · needs `npm install -g better-icons` (or an npx/bunx prefix) to actually run the CLI - the skill does nothing until that install happens, whi
- agent-tool `petergyang__no-ai-slop` · 000650b1 · MIT · RIVAL of the user's existing stop-slop and humanizer/the-humanizer skills (same job: scrub AI prose tells) - per his rival-skills rule, rotate a
- agent-tool `jalaalrd__anti-ai-slop-writing` · 63255f9b · none found (no LICENSE file in repo; GitHub reports no SPDX id; confirmed by a 404 on /contents/LICENSE) · no license file in the repo: catalogued but NOT copied into ~/toolbox/skills per the toolbox-add rule - not safe to reuse in client work wit
- agent-tool `Jakeschincariol__replica-skill` · 77c9436f · MIT · small repo (391-393 stars) despite being presented as a breakout tool in the post - verify it still performs as demoed before relying on it 
- agent-tool `nyldn__claude-octopus` · df134e7e · MIT · the user's note says he's most interested in an 'I have ADHD' skill from this post - checked the FULL skill list in this repo (63 skills) and th
- agent-tool `cloudflare__security-audit-skill` · c1c8a8c1 · MIT · pure guidance skill, no install/CLI needed, no hooks found in the repo
- agent-tool `tt-a1i__archify` · 3c4e4a50 · MIT · needs its Node CLI (`node bin/archify.mjs ...`) to actually generate anything - the skill does nothing until that's set up; no npm install w
- agent-tool `anthropics__financial-services` · 574ed362 · Apache-2.0 · these are Managed-Agent-cookbook configs (agent.yaml + subagents), not plain SKILL.md files - nothing copied into ~/toolbox/skills since the
- agent-tool `Imbad0202__academic-research-skills` · 6ab4b03b · CC BY-NC 4.0 (GitHub reports NOASSERTION; LICENSE file names Creative Commons Attribution-NonCommercial 4.0 International) · license is Creative Commons Attribution-NonCommercial 4.0 - bars commercial use, so it cannot be reused in any paid client or agency work; c
- agent-tool `MadsLorentzen__ai-job-search` · 52f84e0f · MIT · overlaps conceptually with the user's own job-hunt sheet (Francis Place, 2026 job search project) but is a separate, unrelated tool - not a dupl
- agent-tool `google-labs-code__stitch-skills` · 0337446d · Apache-2.0 · needs the Stitch MCP server to do anything design-related: sign in free at stitch.withgoogle.com with a Google account, open Stitch settings
- agent-tool `greensock__gsap-skills` · aed9cfd3 · MIT · none found - pure MIT documentation/guidance skills, no install, no hooks, no network calls
- agent-tool `NandhaKishorM__laya` · 8a6e1328 · Apache-2.0 · No API key needed (confirmed, local model) so the earlier claim holds.
- agent-tool `google__ax` · ac233282 · Apache-2.0 · Requires a Kubernetes cluster with Agent Substrate pre-installed, plus `ko` and a container registry; nothing runs without that infra.
- agent-tool `vectorize-io__hindsight` · f7dd3f4f · MIT · Picked over several same-named unrelated projects (browser-forensics tool, Mozilla's deprecated pipeline, an RL technique, a different Claud
- agent-tool `danielmiessler__Fabric` · 0bd12965 · MIT · Brings its own API-key management for whichever LLM backend is configured; keys are the user's own, read from env/config, no telemetry found
- agent-tool `coderamp-labs__gitingest` · 4e259a02 · MIT · README credits PostHog analytics as a dependency of its own hosted site, not something that touches a local clone or sends the user's data anywh
- agent-tool `VisionForge-OU__foreman` · 92d7f797 · MIT · Low-confidence identity match: the original post's screenshot shows a site called 'ThruWire' ('The AI checkpoint system'), but thruwire.com 
- agent-tool `lirantal__repolyze` · 74309468 · Apache-2.0 · Multiple unrelated same-named repos exist (MxCorpIn/Repolyze 200 stars MIT, maximgorbatyuk/repolyze 10 stars); picked lirantal/repolyze as t
- application `hydra-db__hydradb` · not cloned · AGPL-3.0 · AGPL-3.0: any modified/hosted version must be released under the same license — fine for internal use, relevant only if ever offered as a ho
- agent-tool `opendatalab__MinerU` · ed50cc15 · Apache-2.0 + attribution addendum · Collects anonymous usage/diagnostic telemetry by default (command usage, success/failure rates, timing buckets — not document contents or fi
- application `searxng__searxng` · not cloned · AGPL-3.0 · AGPL-3.0: a hosted/modified instance offered to others must share source.
- application `reactive-resume__reactive-resume` · not cloned · MIT · Full self-hosted stack (needs its own DB/services to run); not a quick single-binary install.
- application `suwayomi__suwayomi-server` · not cloned · MPL-2.0 · Needs a running server/Docker; not a quick single install.
- application `libretranslate__libretranslate` · not cloned · AGPL-3.0 · AGPL-3.0: a hosted/modified instance offered to others must share source.
- application `archivebox__archivebox` · not cloned · MIT · Needs Docker/a server to run; not a quick single binary.
- application `localsend__localsend` · not cloned · Apache-2.0 · none noted
- application `dani-garcia__vaultwarden` · not cloned · AGPL-3.0 · AGPL-3.0: a hosted/modified instance offered to others must share source.
- application `freecodecamp__freecodecamp` · not cloned · BSD-3-Clause · This is the live site's own source code, not a thing to self-host for personal use; the actual value is the hosted freecodecamp.org site/cur
- application `tensorflow__tensorflow` · not cloned · Apache-2.0 · Heavyweight to install/use meaningfully (GPU drivers, large deps); not something to pip install casually without a concrete ML task.
- agent-tool `NVIDIA__OpenShell` · 71c3cd95 · Apache-2.0 · Install is `curl install.sh | sh` then `openshell sandbox create` — per toolbox-add rules this was NOT run, only cloned and read.
- application `omacom__omarchy` · not cloned · MIT · Full-disk installer: the original post claims it wipes the drive; not confirmed in this repo's own README (no wipe warning found there), but
- agent-tool `cactus-compute__needle` · 9571a58b · Apache-2.0 · install-only value: nothing runs without `pip install cactus-needle`
- agent-tool `NVIDIA-NeMo__Switchyard` · c8848511 · Apache-2.0 · Switchyard supplies ROUTING ONLY -- it brings zero model providers or free-tier credits of its own; you still need your own API keys/free-ti
- agent-tool `magnitudedev__magnitude` · 44af293b · Apache-2.0 · medium confidence: same org/repo/domain as the post but a different product -- confirm current scope before recommending it for anything
- agent-tool `barbajs__barba` · a7c99a55 · MIT · last pushed 2024-12-02 -- maintenance looks slow; verify it still works with current build tooling before using it in a client build
- application `langgenius__dify` · not cloned · Dify Open Source License (modified Apache-2.0 with added conditions) · license is a MODIFIED Apache-2.0, not plain Apache: it explicitly requires a commercial license to run Dify as a multi-tenant SaaS backend f
- agent-tool `pipecat-ai__pipecat` · 4be4ff10 · BSD-2-Clause · install-only value: it's a framework, not a running service -- needs real build work (telephony/transport provider, STT/TTS keys) before it 
- application `nocodb__nocodb` · not cloned · Sustainable Use License (non-OSI; core is free to use, restricts competing-service resale) · license is the Sustainable Use License, not MIT/Apache -- free to self-host and use, but restricts reselling it as a competing hosted servic
- application `knadh__listmonk` · not cloned · AGPL-3.0 · AGPL-3.0: if modified and run as a network service for others, the source of those modifications must be made available
- application `makeplane__plane` · not cloned · AGPL-3.0 · AGPL-3.0: modifications run as a network service for others must have their source made available
- application `chatwoot__chatwoot` · not cloned · MIT (core); enterprise/ directory separately licensed · core is MIT, but the enterprise/ directory ships under a separate, more restrictive license -- check which features fall there before promis
- application `activepieces__activepieces` · not cloned · MIT (core); packages/ee/ directory separately licensed · core is MIT, but packages/ee/ (enterprise) ships under a separate license -- check which pieces you actually need fall outside it
- application `documenso__documenso` · not cloned · AGPL-3.0 · AGPL-3.0: modifications run as a network service for others must have their source made available
- agent-tool `HKUDS__CLI-Anything` · 34f51953 · Apache-2.0 · install-only value: each skill wraps `pip install cli-anything-hub` + `cli-hub install <name>`, nothing runs until that's done
- agent-tool `jingyaogong__minimind` · f659b557 · Apache-2.0 · needs real GPU rental and a full training run to produce anything -- install-only value
- agent-tool `NVIDIA__SkillSpector` · 4a550627 · Apache-2.0 · install notice in its own README: 'This project will download and install additional third-party open source software projects' -- real setu
- agent-tool `Automattic__harper` · 51b843dc · Apache-2.0 · the the local inventory check hit on 'Harper' in the user's notes is a false positive (substring of 'sharper'), confirmed by direct grep -- not already installed
- agent-tool `m-bain__whisperX` · 771b4a14 · BSD-2-Clause · local run needs a real ASR model + alignment model download and a working PyTorch/CUDA or CPU setup -- not a zero-setup drop-in
- agent-tool `vercel-labs__skills` · 18f96ea1 · MIT · sends telemetry to add-skill.vercel.sh on every skill install/remove/update by default (src/telemetry.ts) -- phones home unless disabled
- reference-list `public-api-lists__public-api-lists` · 6491e2fb · MIT · none noted
- agent-tool `SWivid__F5-TTS` · 28325256 · MIT · the user's own OmniVoice narration / likeness-clone work is explicitly PAUSED with lip-sync spend UNAPPROVED per memory -- F5-TTS is a different
- application `paperclipai__paperclip` · not cloned · MIT · full stack (pnpm, Docker, server+UI+workers), needs Node 24.11+, not a quick drop-in
- application `FujiwaraChoki__MoneyPrinterV2` · not cloned · AGPL-3.0 · AGPL-3.0: any hosted/modified version must share source -- fine for personal use, a blocker if ever offered as a client-facing service
- agent-tool `mvschwarz__openrig` · bd82e199 · Apache-2.0 · needs `npm install -g @openrig/cli`, Node 22/24, and tmux -- an install step, not run as-is
- application `jegly__Box` · not cloned · Apache-2.0 · GitHub API reports license as NOASSERTION despite a LICENSE file in the repo; read the file directly: it is the standard Apache-2.0 text wit
- application `eigent-ai__eigent` · not cloned · Apache-2.0 · README advertises 'MCP Integration' and 'Skill Integration' -- these mean Eigent can CONSUME external MCP servers/skills as a client, not th
- application `getmaxun__maxun` · not cloned · AGPL-3.0 · AGPL-3.0, full Docker-compose stack with Postgres and a browser service -- a deployment, not a quick clone
- application `plausible__analytics` · not cloned · AGPL-3.0 · AGPL-3.0 self-hosted stack (Elixir/Postgres/Clickhouse) -- a deployment, not a quick install
- application `AppFlowy-IO__AppFlowy` · not cloned · AGPL-3.0 · AGPL-3.0
- application `penpot__penpot` · not cloned · MPL-2.0 · self-hosted Docker stack to run it yourself; otherwise free hosted tier at penpot.app
- application `n8n-io__n8n` · not cloned · Sustainable Use License 1.0 (source-available, not OSI open source) · GitHub reports license as NOASSERTION; the repo's own LICENSE.md is the 'Sustainable Use License' -- free to self-host and run, but restrict
- application `calcom__cal.diy` · not cloned · MIT · repo's own docs flag this as personal use only, not for commercial/enterprise deployment -- don't offer it to clients as a hosted booking to
- application `bitwarden__clients` · not cloned · GPL-3.0 (default; code under /bitwarden_license uses the proprietary Bitwarden License v1.0) · GitHub reports license as NOASSERTION; repo's own LICENSE.txt splits it: GPL-3.0 by default, proprietary Bitwarden License v1.0 only inside 
- application `Louis-CFM__coucou` · not cloned · MIT · native desktop app installed from a Releases zip/DMG, not a skill/MCP/library -- cataloged as application even though it is tightly coupled 
- agent-tool `t8y2__dbx` · 558b22b7 · Apache-2.0 · the skill requires the `dbx` CLI binary installed first (`brew install --cask dbx`) -- install-only without it
- application `deepseek-ai__deepseek-harness` · not cloned · MIT · DeepSeek's own docs recommend a throwaway machine (no security audit yet) -- did not independently re-verify this specific wording, but a SA
- application `THU-MAIC__OpenMAIC` · not cloned · MIT · self-hosted (pnpm dev) or hosted at open.maic.chat -- the hosted option avoids any local install but is a third-party service
- application `debpalash__VoiceStudio` · not cloned · AGPL-3.0 · AGPL-3.0
- application `oblien__openship` · not cloned · Apache-2.0 · self-hosted PaaS stack -- a deployment, not a quick install
- application `polarsource__polar` · not cloned · Apache-2.0 · billing/payments infra -- test thoroughly before touching real money
- application `pocketbase__pocketbase` · not cloned · MIT · single binary -- very low install friction if the user wants it (brew or direct download), but genuinely an application he'd run, not an agent-t
- application `appwrite__appwrite` · not cloned · BSD-3-Clause · self-hosted Docker stack -- a deployment, not a quick clone; or use their managed cloud
- application `stablyai__orca` · not cloned · MIT · has an 'Enterprise' nav item on its site; no pricing wall found on the core desktop download, but the enterprise tier itself was not charact
- application `syi0808__screenize` · not cloned · Apache-2.0 · Repo itself says development is currently paused — unclear if it still builds on current macOS; verify before relying on it.
- application `LingyiChen-AI__DeepDiagram` · not cloned · AGPL-3.0 · AGPL-3.0: any modified version you deploy for others must also be open-sourced — a real constraint if this were ever white-labeled for a cli
- application `cline__cline` · not cloned · Apache-2.0 · A direct alternative to Claude Code itself; running it means routing agentic coding work through a separate tool/ecosystem
- application `aaif-goose__goose` · not cloned · Apache-2.0 · Repo recently moved orgs (was block/goose, now aaif-goose/goose under the Agentic AI Foundation) — bookmark the new URL, old links may redir
- application `Significant-Gravitas__AutoGPT` · not cloned · MIT (outside autogpt_platform/) + Polyform Shield License (inside autogpt_platform/) · GitHub reports license as NOASSERTION because the repo is split: the core agent code is MIT, but the newer 'autogpt_platform' folder (the ac
- application `usenotra__notra` · not cloned · AGPL-3.0 · AGPL-3.0 copyleft applies if you modify and host it for clients
- application `openinterpreter__openinterpreter` · not cloned · Apache-2.0 · This is a full relaunch/rewrite under the same name/repo slug — distinct from the older Python 'open-interpreter' project many people alread
- application `open-webui__open-webui` · not cloned · Open WebUI License (custom, BSD-3-style + branding lock) · License is NOT a clean OSI license: it is BSD-3-style PLUS a clause that bars removing/altering 'Open WebUI' branding in any deployment or d
- application `janhq__jan` · not cloned · Apache-2.0 (per LICENSE file; GitHub API reports NOASSERTION) · GitHub shows the license as NOASSERTION, but the actual LICENSE file is a standard Apache-2.0 copyright notice from Menlo Research — worth n
- application `OpenWhispr__openwhispr` · not cloned · MIT · none noted
- application `tashfeenahmed__freellmapi` · not cloned · MIT · Its own repo description says 'Personal experimentation only' — read that before pointing any client-facing or paid workflow at it
- application `iv-org__invidious` · not cloned · AGPL-3.0 · Requires Docker self-hosting; public instances exist but using someone else's instance isn't 'having' this tool
- application `dream-num__univer` · not cloned · Apache-2.0 (core OSS); Univer Pro is a separate paid commercial license · This is a developer SDK/framework (like Univer Workspace is built on top of it) — there's no out-of-the-box 'point Claude at this' use, it's
- application `CapSoftware__Cap` · not cloned · AGPL-3.0 (core) + MIT (cap-camera*/scap-* crates only) · AGPL-3.0 on the main codebase (camera-capture crates only are MIT) — copyleft applies if you modify and redistribute/host it
- application `OpnForm__OpnForm` · not cloned · AGPL-3.0 (except api/app/Enterprise, under its own license) · AGPL-3.0 outside the Enterprise directory — copyleft applies to any modified, redistributed/hosted version
- application `usestrix__strix` · not cloned · Apache-2.0 · Only ever point this at apps the user owns or has explicit authorization to test — running it against a client's live site without the
- application `invoke-ai__InvokeAI` · not cloned · Apache-2.0 · Different tool from the user's existing local image stack (ComfyUI inside OpenMontage) — a genuine alternative, not already in use, would need i
- application `upscayl__upscayl` · not cloned · AGPL-3.0 · AGPL-3.0 copyleft applies to any modified/redistributed version
- agent-tool `busabase__busabase` · e5e65fd9 · MIT · No static skill files exist in the repo to borrow: the 'Agent Skill' onboarding prompt it hands a connecting agent is generated at runtime a
- website Mixpost · https://mixpost.app · freemium · verified: 2026-10-04 mixpost.app/pricing
- website Manus · https://manus.im · freemium · verified: not checked (manus.im/pricing is a JS-rendered page; three fetch methods via web_fetch.py all returned only nav chrome, no pricing figures in the actual fetched text)
- website Soro - SEO Autopilot & Content · https://apps.shopify.com/soro · paid · verified: 2026-10-04 apps.shopify.com/soro
- website Codiv (OpenJev) · https://codiv.ai · freemium · verified: 2026-10-04 codiv.ai
- website PhoText · https://photext.shop · freemium · verified: 2026-10-04 photext.shop
- website SoBrief · https://sobrief.com · freemium · verified: 2026-10-04 sobrief.com
- website Privnote · https://privnote.com · free · verified: 2026-10-04 privnote.com
- website Perchance · https://perchance.org · free · verified: 2026-10-04 perchance.org
- website OmniSocials · https://www.omnisocials.com · trial · verified: 2026-10-04 omnisocials.com/pricing
- website Exa Websets · https://exa.ai/websets · freemium · verified: 2026-10-04 exa.ai/pricing
- website Componentry · https://componentry.dev · free · verified: 2026-10-04 componentry.dev
- website Space UI · https://spaceui.one · freemium · verified: 2026-10-04 spaceui.one (pricing subpage blocked, read from homepage)
- website Skecher UI · https://skecher-ui.com · free · verified: 2026-10-04 skecher-ui.com
- website Planes · https://useplanes.com · paid · verified: 2026-10-04 useplanes.com
- website Arc UI · https://uiarc.dev · freemium · verified: 2026-10-04 uiarc.dev
- website Unicorn Studio · https://unicorn.studio · freemium · verified: 2026-10-04 unicorn.studio (pricing section)
- website 21st.dev · https://21st.dev · freemium · verified: 2026-10-04 21st.dev (pricing table not confirmed)
- website Jitter · https://jitter.video · freemium · verified: 2026-10-04 jitter.video/pricing
- website animos · https://animos.app · freemium · verified: 2026-10-04 animos.app (no pricing table found on this fetch)
- website OKSURF Google News API · https://ok.surf · free · verified: 2026-10-04 ok.surf
- website QuickChart · https://quickchart.io · freemium · verified: 2026-10-04 quickchart.io
- website IPLocate · https://iplocate.io · freemium · verified: 2026-10-04 iplocate.io/pricing

## 2026-10-04 — websites knowledge base, loadouts of up to 10 tools
- ported by hand from a 2026-10-01 cloud session, which had pushed them only to the public agent-toolbox repo
- `websites.json`: free web apps with no repo (free tier, account, API, limits and a verified date per site). 15 starter sites, all `not checked`. `bin/build-catalog.sh` writes `catalog/websites.md` from it; `bin/library.py` indexes each as kind `website` (quota 5), with no card: the catalog line is the description
- `/toolbox-add`: a tool that is only a website goes into `websites.json` (Step 2d) instead of being turned away. Still no sign-ups, trials or cards
- `/tool-audit`: a loadout is up to 10 tools across at least three kinds (skills 10, agents 10, websites 5, MCP 3, plugins 2), and a loadout under 10 says why. Shortlist 30 to 40; discovery proposes up to 10 and runs one web search for free web apps
- `/skill-audit`: up to 10 skills; the ledger takes `--kind website`
- `bin/patch-fast-jev-local.py` is now committed: `loadouts/jev-compaction-local.sh` runs it, so a fresh clone could not start that loadout

## 2026-10-04 — fast-jev-compaction replay verdict: not for global install
- replayed 9 real long-session compactions through the plugin on local Ollama tev1-16k: 6 failed (history over the 10k budget forced by Ollama's 64 KiB cap; >64 questions per request), the 3 that ran were 68-140 s vs 4-16 s built-in
- 12% of deleted tool results were touched again after the compaction; 2 of 30 kept results ever used
- built-in history (140 compactions): manual /compact median 27 s vs auto 100 s; context size does not predict duration

## 2026-10-03 — library.py understands every tool: cards from full source, qwen3 embeddings, ledger eval, local Jev judge
- `library.py profile`: local gemma4:e4b writes a card per tool (does / use_when / not_for / input / output / needs) from its full source, cached by hash; 2,198 tools carded
- index adds the user's scripts (every script a memory note names + siblings, ~/.claude/scripts, bin/) and ledger-only tools; each hit shows its ledger record
- embeddings: qwen3-embedding:8b with an instruct query prefix; per-kind quota x2; find -n 120
- `library.py eval`: ledger replay. Tool that worked, surfaced for its goal: 25% (9/21 index) -> 41% (cards + qwen3) -> 45% with `--judge`
- `find --judge`: Jev-style rerank via any TypeSafe System One endpoint; default local Ollama 0.35.1 tev1-16k, batches of 8
- capabilities.md: typed-decisions and compaction chains; loadouts/jev-compaction-local.sh; bin/patch-fast-jev-local.py

## 2026-10-03 — added browser-use__jev-ultrafast, jkudish__jev-mcp, tamaratran__fast-jev-compaction (agent-tools)
- https://github.com/browser-use/jev-ultrafast · 1231850a · MIT · fast browser agent on TypeSafe's Jev; does not read or rank tools
- https://github.com/jkudish/jev-mcp · d6876335 · MIT · 12 typed-judgment MCP tools (verify, screen, find, rerank, classify, decide, compare, extract, audit, review, gate, noul)
- https://github.com/tamaratran/fast-jev-compaction · e3f262a7 · MIT · Claude Code plugin: Jev-pruned verbatim compaction
- serves: tool-audit rerank (jev-mcp), compaction (fast-jev-compaction), browser automation (jev-ultrafast)
- ships: 1 skill (jev-mcp skills/jev, not copied), 1 MCP server, 1 function-hook plugin, 0 agents
- risks: all three need a paid Jev provider key (none on this Mac); the compaction hook sends the whole conversation to api.typesafe.ai, ignores baseUrl, and forces compaction at 60% context; jev-mcp's skill says to call the paid verify tools "even when the answer looks obvious"; jev-ultrafast drives the signed-in Chrome profile
- installed: nothing. fast-jev-compaction live install held for a backend decision

## 2026-10-03 — added ankit-aglawe__tinyjev (agent-tool, installed in a toolbox venv)
- https://github.com/ankit-aglawe/tinyjev · fec868b6 · MIT · local Jev-style decision server (System One API) on MLX
- serves: tool-audit judging (library.py find --judge), any System One client
- ships: python package + CLI; 0 skills, 0 agents, 0 MCP
- risks: loopback server with no auth; 0.6B is fast (~25 ms per judgment) but a weak tool-relevance judge here; rejects fast-jev-compaction's payload
- installed: ~/toolbox/venvs/tinyjev (uv, Python 3.12, mlx), weights in the HuggingFace cache. Nothing under ~/.claude

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
