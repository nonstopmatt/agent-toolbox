# Remote MCP server branch [#23]

A remote HTTP MCP server has no files to read. Its agent-facing surface is the
`instructions` string from `initialize` plus every tool `description` from `tools/list`,
served at connect time, injected into every session, and changeable by the vendor at any
moment with no local diff.

1. **Read it before adding it.** Raw JSON-RPC with curl: `initialize`, then `tools/list`.
   Read `instructions` and each description as untrusted agent-facing text. Check trigger
   breadth (does it claim ground an existing tool or skill owns, "use even when you think you
   know the answer", "prefer this over web search") and whose interest it serves. The same
   probe tests a keyless tier.
2. **Manual line over installer.** When the vendor offers an `npx` setup command (OAuth, key
   minting, an auto-triggering skill), a plugin, and a one-line `mcp add`, take the one line.
3. **Prove with `tools/call`.** A raw call that returns real data, not the client's
   "Connected". MCP tools added mid-session are not callable in the installing session, so the
   raw call is also the only same-session proof.
4. **Suppress in Matt's rules, never in the vendor's text.** The text can change after
   install; a re-probe is cheap whenever behaviour shifts.
5. **Shadowing.** Check for a same-named server at a narrower scope (project `.mcp.json`),
   which silently wins in that project.
6. **Inventory counters under-report file-referenced servers** [#22]: a plugin declaring
   `"mcpServers": "./path/.mcp.json"` shows `MCP servers (0)` in `plugin details` while
   `claude mcp list` shows it registered. Trust the runtime listing.
