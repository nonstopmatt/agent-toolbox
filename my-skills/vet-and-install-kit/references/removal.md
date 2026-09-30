# Removal branch [#24]

An uninstall verified where a tool is declared says nothing about where it runs. Every
session opened before the removal keeps its child MCP servers until that session exits, and
clearing a conversation does not restart them.

Check all six, and report each one:

1. **Declared surfaces:** plugin list, MCP list, settings, instruction files (CLAUDE.md,
   AGENTS.md blocks the kit wrote).
2. **Running surfaces:** `ps` for the server command, mapped to parent sessions. Anchor the
   match on the executable field, or the checker matches its own command line.
3. **Runner caches** (npx, uvx, pipx): delete a cache directory only after its manifest shows
   it holds that package alone.
4. **Autostart:** launchd, cron, login items.
5. **Backups that would re-enable it** (settings backups carrying the enabled-plugin flag or
   the marketplace source): report them to Matt, do not delete them.
6. **Respawn check** some seconds after any kill. A cleanup command can die on the signal it
   sent even when every step completed, so re-probe the state rather than reading the exit
   code.

**Done when:** all six have a command and its output, and nothing the kit started is still
running or re-enableable without Matt knowing.
