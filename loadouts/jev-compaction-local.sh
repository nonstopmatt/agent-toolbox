#!/usr/bin/env zsh
# loadout: jev-compaction-local — fast-jev-compaction on a LOCAL Jev (Ollama tev1-16k). Written 2026-10-03.
# Session-scoped: nothing here changes ~/.claude. Close the tab and it is gone.
# Compaction keeps tool calls/results verbatim or drops them (no summary); falls back to the built-in summary on
# any error. Toast after /compact: "kept N/M messages" = it worked, "fallback to built-in summary (...)" = why not.
set -e
TB="$HOME/toolbox"
[[ -d "$TB/parked/fast-jev-compaction-local" ]] || python3 "$TB/bin/patch-fast-jev-local.py"
curl -sf -m 3 http://127.0.0.1:11434/api/version >/dev/null || { echo "Ollama is not running: start it, then retry"; exit 1; }
# tev1:4b ships with a 2,050-token window and Ollama never truncates, so compaction needs the 16k derivative
if ! ollama show tev1-16k >/dev/null 2>&1; then
  MF=$(mktemp); printf 'FROM tev1:4b\nPARAMETER num_ctx 16384\n' > "$MF"; ollama create tev1-16k -f "$MF" >/dev/null; rm -f "$MF"
fi
export CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1
export JEV_API_BASE_URL=http://127.0.0.1:11434/v1/systemone   # MUST stay set: without it the hook calls api.typesafe.ai
export JEV_MODEL=tev1-16k JEV_MAX_STATE_TOKENS=10000 JEV_MAX_REQUEST_TOKENS=12000
export TYPESAFE_API_KEY=local                                   # placeholder the hook requires; Ollama ignores it
exec claude --plugin-dir "$TB/parked/fast-jev-compaction-local" "$@"
