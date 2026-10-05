#!/usr/bin/env python3
"""Make a local-endpoint copy of tamaratran/fast-jev-compaction. Re-run after every upstream pull.

Upstream's hook always calls api.typesafe.ai (hooks/fast-jev.ts drops baseUrl even though src/ supports it).
This copies the pinned clone to ~/toolbox/parked/fast-jev-compaction-local and makes the hook read
JEV_API_BASE_URL and JEV_MODEL from the environment, so compaction can run on a local System One server
(Ollama 0.35+ decision models) and nothing leaves the Mac. Every anchor is asserted: an upstream change
that moves one fails loudly instead of shipping a half-patched hook.
"""
import os, shutil, sys

SRC = os.path.expanduser("~/toolbox/repos/tamaratran__fast-jev-compaction")
DST = os.path.expanduser("~/toolbox/parked/fast-jev-compaction-local")
EDITS = [
    ("export type HookConfig = CompactOptions & {\n  apiKey?: string;",
     "export type HookConfig = CompactOptions & {\n  apiKey?: string;\n  baseUrl?: string;"),
    ("export function jevAsker(fetchFn: HookFetch, apiKey: string, model: string): JevAsker {",
     "export function jevAsker(fetchFn: HookFetch, apiKey: string, model: string, baseUrl?: string): JevAsker {"),
    ("const request = buildJevRequest({ apiKey, model }, state, questions);",
     "const request = buildJevRequest({ apiKey, model, baseUrl }, state, questions);"),
    ("jevAsker(fetchFn, config.apiKey, config.model)",
     "jevAsker(fetchFn, config.apiKey, config.model, config.baseUrl)"),
    ("const config = { ...configured, apiKey: await getApiKey($, configured) };",
     "const config = { ...configured, apiKey: await getApiKey($, configured),\n"
     "        baseUrl: (await $.env.get('JEV_API_BASE_URL')) || undefined,\n"
     "        model: (await $.env.get('JEV_MODEL')) || configured.model,\n"
     "        // Ollama's /v1/systemone caps a body at 64 KiB: the launcher lowers upstream's 25k/30k token budgets\n"
     "        maxStateTokens: Number(await $.env.get('JEV_MAX_STATE_TOKENS')) || configured.maxStateTokens,\n"
     "        maxRequestTokens: Number(await $.env.get('JEV_MAX_REQUEST_TOKENS')) || configured.maxRequestTokens };\n"
     "      // the launcher's placeholder key must never reach api.typesafe.ai with a real transcript\n"
     "      if (config.apiKey === 'local' && !config.baseUrl) throw new Error('local key without JEV_API_BASE_URL: not calling TypeSafe');"),
]

if os.path.exists(DST): shutil.rmtree(DST)
shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns(".git", "node_modules", "demo"))
p = os.path.join(DST, "hooks", "fast-jev.ts"); s = open(p).read()
for old, new in EDITS:
    if s.count(old) != 1: sys.exit(f"ABORT: anchor not found exactly once in hooks/fast-jev.ts: {old[:70]!r}")
    s = s.replace(old, new)
open(p, "w").write(s)
print(f"patched copy at {DST} ({len(EDITS)} edits)")
