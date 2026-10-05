# memory-context

Generated: 2026-10-04 20:32 
Count: 60

Line format: `- kind | name | what it is | path` — and for kind `application` or
`agent-tool`, also `| license | WARN: read this before recommending it | risks: ...`.
Kinds: skill, agent, plugin, mcp-mine, mcp-discovered, application, agent-tool.
Paths are relative to ~/toolbox. Nothing here is installed: borrow it or session-launch it.

- agent | codebase-memory-auditor | Bounded-scope graph audit with check_index_coverage and source read/grep fallback. | agents/codebase-memory-auditor.md | 1963
- agent | codebase-memory-scout | Fast positive, provisional graph lookup with check_index_coverage and source read/grep fallback. | agents/codebase-memory-scout.md | 1784
- agent | codebase-memory | Default task-directed graph verification with check_index_coverage and source read/grep fallback. | agents/codebase-memory.md | 1925
- agent | Data Consolidation Agent | AI agent that consolidates extracted sales data into live reporting dashboards with territory, rep, and pipeline summari | agents/data-consolidation-agent.md | 2393
- agent | Codebase Onboarding Engineer | Expert developer onboarding specialist who helps new engineers understand unfamiliar codebases fast by reading source co | agents/engineering-codebase-onboarding-engineer.md | 9569
- agent | Knowledge Graph Engineer | Structures information and capabilities into interconnected nodes (entities) and edges (relationships) — enabling dynami | agents/engineering-knowledge-graph-engineer.md | 23440
- agent | RAG Pipeline Engineer | Production RAG specialist focused on chunking strategy, retrieval quality, hybrid search, re-ranking, and eval-driven it | agents/engineering-rag-pipeline-engineer.md | 18250
- agent | Technical Writer | Expert technical writer specializing in developer documentation, API references, README files, and tutorials. Transforms | agents/engineering-technical-writer.md | 14210
- agent | Clinical Evidence Agent | Evidence standards and clinical credibility framework for AI agents operating in healthcare contexts. Defines how to dis | agents/healthcare-clinical-evidence-agent.md | 10273
- agent | Healthcare Innovation Strategist | Strategic narrative architect for healthcare founders operating at the intersection of clinical credibility, healthcare  | agents/healthcare-innovation-strategist.md | 20366
- agent | Language Translator | Real-time Spanish ↔ English translation specialist with cultural context, regional dialect awareness, travel phrase guid | agents/language-translator.md | 16086
- agent | Legal Document Review | Comprehensive legal document review specialist for contracts, litigation documents, and real estate agreements — summari | agents/legal-document-review.md | 24728
- agent | Meeting Notes Specialist | Extract structured decisions, action items, and open questions from meeting transcripts or rough notes into a clean 4-se | agents/project-management-meeting-notes-specialist.md | 5616
- agent | skill-reviewer | "Fresh-context reviewer for Claude Ads skill and agent routing, progressive disclosure, prompt contracts, safety boundar | agents/skill-reviewer.md | 862
- agent | Document Generator | Expert document creation specialist who generates professional PDF, PPTX, DOCX, and XLSX files using code-based approach | agents/specialized-document-generator.md | 2437
- agent | Executive Summary Generator | Consultant-grade AI specialist trained to think and communicate like a senior strategy consultant. Transforms complex bu | agents/support-executive-summary-generator.md | 8992
- agent | ZK Steward | "Knowledge-base steward in the spirit of Niklas Luhmann's Zettelkasten. Default perspective: Luhmann; switches to domain | agents/zk-steward.md | 10892
- mcp-mine | codebase-memory-mcp | stdio | tools: ? | mcp/mine/codebase-memory-mcp.json
- mcp-mine | context7 | sse/http | tools: ? | mcp/mine/context7.json
- mcp-discovered | claude-mem-local | stdio | tools: ? | mcp/discovered/claude-mem-local.json
- mcp-discovered | claude-mem-remote | sse/http | tools: ? | mcp/discovered/claude-mem-remote.json
- mcp-discovered | context7 | stdio | tools: ? | mcp/discovered/context7.json
- mcp-discovered | context7 | sse/http | tools: ? | mcp/discovered/context7__84927827.json
- mcp-discovered | context7 | stdio | tools: ? | mcp/discovered/context7__f4d4dcf1.json
- mcp-discovered | guru | sse/http | tools: ? | mcp/discovered/guru.json
- mcp-discovered | memory | stdio | tools: ? | mcp/discovered/memory.json
- mcp-discovered | memwal | stdio | tools: ? | mcp/discovered/memwal.json
- mcp-discovered | memwal | stdio | tools: ? | mcp/discovered/memwal__75ed1c34.json
- mcp-discovered | notion | sse/http | tools: ? | mcp/discovered/notion.json
- mcp-discovered | notion | sse/http | tools: ? | mcp/discovered/notion__a9441077.json
- mcp-discovered | serena | stdio | tools: ? | mcp/discovered/serena.json
- mcp-discovered | serena | stdio | tools: ? | mcp/discovered/serena__a9aee352.json
- skill | blog-write | Write new blog articles from scratch optimized for Google rankings and AI citations. Generates full articles with templa | skills/blog/blog-write/SKILL.md
- skill | codebase-memory | "Run whole-repo structural audits against the codebase knowledge graph: dead code, unused functions, high fan-out, refac | skills/codebase-memory/SKILL.md
- skill | colorize | Add strategic color to features that are too monochromatic or lack visual interest, making interfaces more engaging and  | skills/colorize/SKILL.md
- skill | firecrawl-crawl | Bulk extract content from an entire website or site section. Use this skill when the user wants to crawl a site, extract | skills/firecrawl-crawl/SKILL.md
- skill | firecrawl-knowledge-base | Build a knowledge base from web content with Firecrawl. Use for local reference docs, RAG-ready chunks, fine-tuning data | skills/firecrawl-knowledge-base/SKILL.md
- skill | firecrawl-research-papers | Find and synthesize research papers, whitepapers, PDFs, technical reports, and academic sources with Firecrawl. Use when | skills/firecrawl-research-papers/SKILL.md
- skill | firecrawl-shop | Research products across the web with Firecrawl and produce a shopping recommendation or cart-ready summary. Use when th | skills/firecrawl-shop/SKILL.md
- skill | frame-glitch-title | "Digital glitch, chromatic offset, and data-corruption title frame for video transitions or cyberpunk heroes." | skills/frame-glitch-title/SKILL.md
- skill | grill-with-docs | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. disable-model | skills/grill-with-docs/SKILL.md
- skill | gstack-context-restore | Restore working context saved earlier by /context-save. (gstack) allowed-tools: - Bash - Read - Glob - Grep - AskUserQue | skills/gstack-context-restore/SKILL.md
- skill | gstack-context-save | Save working context. (gstack) allowed-tools: - Bash - Read - Write - Glob - Grep - AskUserQuestion | skills/gstack-context-save/SKILL.md
- skill | handoff | Compact the current conversation into a handoff document for another agent to pick up. argument-hint: "What will the nex | skills/handoff/SKILL.md
- skill | docs | 'docs (living docs people share, comment on and edit; use only when the user asks for one: names a doc, document, page,  | skills/synced/85db74e3-76a3-48a0-876f-c239652a5108_68586651-6f3d-4164-8a0f-076d8fc4ffed/docs/SKILL.md
- skill | import-memory | Import a memory export from another AI assistant into Claude's memory — conversationally, additively, and with the conte | skills/synced/85db74e3-76a3-48a0-876f-c239652a5108_68586651-6f3d-4164-8a0f-076d8fc4ffed/import-memory/SKILL.md
- skill | understand-chat | "Ask questions about a codebase using an EXISTING understand knowledge graph. LANE: requires .ua/knowledge-graph.json to | skills/understand-chat/SKILL.md
- skill | understand-dashboard | "Launch the interactive web dashboard for an EXISTING understand knowledge graph. LANE: requires .ua/knowledge-graph.jso | skills/understand-dashboard/SKILL.md
- skill | understand-diff | "Analyse a git diff or pull request against an EXISTING understand knowledge graph to surface affected components and ri | skills/understand-diff/SKILL.md
- skill | understand-domain | Extract business domain knowledge from a codebase and generate an interactive domain flow graph. Works standalone (light | skills/understand-domain/SKILL.md
- skill | understand-explain | "Deep-dive explanation of one file, function or module, enriched by an EXISTING understand knowledge graph. LANE: requir | skills/understand-explain/SKILL.md
- skill | understand-knowledge | Analyze a Karpathy-pattern LLM wiki knowledge base and generate an interactive knowledge graph with entity extraction, i | skills/understand-knowledge/SKILL.md
- skill | understand-onboard | "Generate an onboarding guide for someone joining a project, from an EXISTING understand knowledge graph. LANE: requires | skills/understand-onboard/SKILL.md
- skill | vfx-text-cursor | "Cursor light trail, chromatic rays, and directional flares for word-by-word quote reveals in video intros." | skills/vfx-text-cursor/SKILL.md
- agent-tool | mksglu__context-mode | Context-window saver: runs tool work in a sandbox MCP server and returns only the answer to the main session. 23.8k stars. | (not cloned) | Elastic-2.0 (source-available) | WARN: Never enable. If wanted, the user decides and installs it themselves. | risks: NOT CLONED on purpose: catalog line only. MCP server + hooks on SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact and Stop, the stacking that broke this setup on 9/20; Elastic License 2.0: source-available, not open source, not redistributabl
- application | Tencent__WeKnora | Document knowledge platform: RAG plus knowledge graph over your files. Docker app. 28.2k stars. | (not cloned) | MIT (third-party parts differ) | risks: Docker stack; UI and docs largely Chinese; lookalike: xiaohuangpin/WeKnora-pro, not chosen
- agent-tool | tamaratran__fast-jev-compaction | Claude Code function-hook plugin that replaces the compaction summary with Jev decisions: every tool call/result is scored keep/truncate/drop in fast requests, kept content stays verbatim, user and as | repos/tamaratran__fast-jev-compaction | MIT | WARN: DO NOT INSTALL GLOBALLY (replay verdict 2026-10-04). Local backend fails or is slower on real long sessions. Revisit only with hosted Jev (paid, 25k state) or if Ollama lifts its 64 KiB / 64-question caps. | risks: needs TYPESAFE_API_KEY (paid); sends the whole conversation (texts, tool inputs, abridged results) to api.typesafe.ai on every compaction; hooks/fast-jev.ts builds requests without baseUrl, so the hook cannot use a local System One server without a one-line pa

