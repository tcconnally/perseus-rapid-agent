# Claims Audit — perseus-rapid-agent

**Date:** 2026-06-12 · **Audited:** README.md, AGENTS.md vs code on `main`
**Rule applied:** judges forgive small scope; they punish discovered fiction.

## Findings (ranked by judge visibility)

### CRITICAL — Engram quickstart crashes against current engram-rs

- **Claim:** README quickstart: `MEMORY_BACKEND=engram python -m agent.main` (also "Engram-rs (self-hosted), same API").
- **Reality:** `EngramMemoryBackend` shells out to CLI verbs (`store`, `recall`, …) that no longer exist — engram-rs v0.5.0 exposes only `engram serve`. Live run today: `RuntimeError: Engram recall failed: error: unrecognized subcommand 'recall'`. The demo crashes on screen on any machine with a current engram install.
- **Fix options:** pin a documented engram-rs version in README/setup, or port the backend to the engram serve API, or default the demo to a backend that works.

### HIGH — "Gemini-powered" but no Gemini call exists in the repo

- **Claim:** "A Gemini-powered agent…" (README line 7, AGENTS.md stack).
- **Reality:** Zero Gemini/Vertex SDK usage anywhere in `agent/`. The design intent is that Google Cloud Agent Builder supplies the LLM and calls these tools — defensible, but if a judge asks "show me the Gemini integration," the honest answer is "there isn't one in this repo."
- **Fix:** one README sentence making the division of labor explicit ("Gemini reasoning is provided by Agent Builder; this repo is the memory/tool layer it calls").

### MEDIUM — "Hybrid search (semantic + keyword + vector)" overstates the backend

- **Claim:** README "Why Elastic?": hybrid semantic + keyword + vector.
- **Reality:** `elastic_memory.py` does keyword search always and ELSER semantic search when the deployment supports it. No vector/kNN field, no RRF fusion. `search_method` reports "hybrid" when semantic is on, but "vector" is fiction.
- **Fix:** say "keyword + ELSER semantic (when available)".

### MEDIUM — "ES|QL for custom memory queries" / "ES|QL aggregations"

- **Claim:** README operations table says `reflect` uses ES|QL aggregations.
- **Reality:** `reflect()` uses standard search aggregations, not ES|QL.

### RESOLVED (previously HIGH) — Elastic backend is now real

The "Elastic Agent Builder MCP memory backend → stub" gap from the deep-dive
review was fixed by [PR #7](https://github.com/tcconnally/perseus-rapid-agent/pull/7):
`ElasticMemoryBackend` now creates a real index (semantic mapping with plain
fallback) and performs real searches via elasticsearch-py.

### RESOLVED (previously CRITICAL) — MemoryEntry crash

`id: str = ""` ordered after required fields on `main`; 11/11 tests pass.

## Verified claims

- Backend swap via one env var — both backends implement the same `MemoryBackend` interface. ✓
- Persistent memory across sessions — real store/recall through Elastic (verified) or engram (blocked by the CRITICAL above). ✓/⚠
- Tests — `tests/test_demo_paths.py` 11 passed. ✓
