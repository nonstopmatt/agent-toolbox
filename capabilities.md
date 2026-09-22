# Capabilities and fallback chains

Every job the toolbox can do, and every tool that can do it, in the order to try them.
**Rule: when a tool fails, move to the next line. Stop only when the chain runs out or the
next step needs the user's yes (spends money, sends, posts, deploys, needs a sign-in).**
Report every attempt. Record account problems with `--failure-type auth|paywall|cap|missing`
so they never count against the tool.

`library.py find` shows the chains whose heading or first lines match the goal. Keep each
chain short, ordered by quality-for-cost, and mark paid or sign-in steps.

## Image generation (logos, illustrations, photos, icons)
1. OpenAI gpt-image-2.5 (key: openai_key) via gen_openai.py, parallel, ~30s each
2. Nano Banana Pro via Gemini API (key: gemini_key); 429 = monthly spend cap
3. Nano Banana Pro / Nano Banana 2 via Replicate (key: replicate_key) through nano.py
4. Local ComfyUI (free, on this Mac, slower)
5. Higgsfield MCP (subscription credits, needs sign-in) or Higgsfield API (billable, explicit yes only)
6. glif MCP (needs sign-in)

## Logo and brand identity
1. Claude Design artifact type (brand boards, lockups, layouts)
2. Image generation chain above for concepts
3. logo-designer skill for the chosen mark as clean SVG, exports via headless Chrome when no SVG converter is installed
4. gstack-design-consultation skill (proposes a full design system)
5. Brand Guardian and Visual Storyteller agents (positioning, rules)
6. Design System artifact type for the finished kit

## Design references and inspiration
1. design-md-library (74 brand DESIGN.md files, grep INDEX.md)
2. Open Design design systems (152) and skills (133)
3. design-inspo skill (115 galleries in ~/design-inspiration)
4. firecrawl-website-design-clone skill (extract a live site's system)
5. claude-in-chrome on the real reference site
6. Mobbin MCP (paid plan required)

## Diagrams and visual explainers
1. diagram-design skill (40 types, editorial rules)
2. artifact-diagramming skill (inline SVG in artifacts)
3. Figma MCP generate_diagram (FigJam)
4. dataviz skill for charts

## UI and page design, mockups
1. taste-skill (mandatory first for websites)
2. impeccable / ui-ux-pro-max skills
3. Claude Design artifact type
4. Pencil MCP (.pen designs)
5. Figma MCP generate_figma_design
6. Magic UI MCP (animated components)

## Web research and scraping
1. WebSearch + WebFetch (built in)
2. research-web skill (parallel investigators; medium depth unless asked)
3. Firecrawl MCP (credits may be out)
4. Nimble API
5. claude-in-chrome for JS-heavy or logged-out pages
6. agent-reach for X, Reddit, Instagram, LinkedIn

## Transcripts (YouTube, audio, video)
1. yt_expert.py transcript (captions first, then mlx_whisper)
2. yt-dlp + mlx_whisper turbo (local, free)
3. transcript-api MCP (was down 2026-09-21)

## Text generation fallback (when an API is out of credits)
1. llm_fallback.py: local Ollama first, then free hosted tiers

## Voice and narration
1. OmniVoice local (free)
2. ElevenLabs (key is TTS-only, ask first)

## AI phone and website receptionists
1. ElevenLabs Agents widget (free 15 min/month tier, needs an account)
2. Retell AI (pay per minute)
3. Vapi web SDK (pay per minute)
4. vb-talk.js free mode (browser speech, no account)

## Video editing and motion
1. DaVinci Resolve MCP (always for Matt's edits)
2. hyperframes skills (motion graphics compositions)
3. video-shotcraft (Remotion promos from real screenshots)

## Browser and computer automation
1. claude-in-chrome (web)
2. computer-use MCP (native Mac apps)
3. computer-agents (UI-TARS locate; Agent S3 live runs need a yes)
4. Yappy (Mac computer-use agent, run by the user)

## PDFs and documents
1. cdp_pdf.py (HTML to PDF through headless Chrome)
2. gstack-make-pdf skill (markdown to PDF)
3. anthropic-skills:pdf / docx / pptx

## Local business leads
1. google-maps-scraper (local Docker, free)
2. ~/lead-scraper (Scrapegraph + Ollama, free)
3. Apify (capped at $75, check limits first, ask before spending)

## Copywriting and voice
1. marketing-skills copywriting / social / cold-email (session-launched plugin; read from cache)
2. b2b-copywriting skill
3. humanizer (file diagnosis) or the-humanizer (channel copy), never both

## Expert advice and strategy
1. expert-intel skill (local expert library, transcripts, web)
2. gstack-office-hours (idea validation)
3. Pricing Analyst / Proposal Strategist agents
