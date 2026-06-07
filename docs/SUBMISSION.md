# Devpost Description — perseus-cmzeu9 (Google Cloud Rapid Agent Hackathon)

Copy these sections into the Devpost form. Demo video to upload: demo/demo_video.mp4

---

## Project Name
```
Perseus Memory Agent — Elastic Partner Track
```

## Elevator Pitch (max 200 chars)

```
Your AI agent shouldn't have amnesia. Perseus gives Gemini agents persistent memory across sessions — remembering your stack, decisions, and lessons. Elastic (cloud) or Engram-rs (self-hosted, MIT), same API.
```

---

## What It Does

Perseus Memory Agent gives AI agents persistent, evolving memory so they remember project context across sessions. Instead of re-explaining your tech stack, conventions, and architectural decisions every time you start a new session, the agent recalls everything it learned about your project — even from weeks ago.

Key capabilities:
- **Remembers project context** — stack, conventions, architecture, preferences
- **Logs decisions with rationale** — why pgvector over Pinecone? The agent remembers
- **Compounds knowledge** — spots patterns across sessions, surfaces insights
- **Swappable backends** — Elastic (managed cloud) or Engram-rs (self-hosted MIT), one config line
- **Hybrid search** — ELSER semantic + BM25 keyword for accurate recall via Elastic

The demo shows 3 sessions:
1. **Session 1** — agent learns project context from scratch
2. **Session 2** — agent recalls prior knowledge, logs decisions with rationale
3. **Session 3** — agent compounds everything, backend swap Elastic → Engram-rs

---

## How I Built It

Built with **Gemini 3 Pro** in **Google Cloud Agent Builder**, connected to **Elastic Agent Builder** via MCP for the memory layer:

1. **Elastic MCP tools** — Three tools in Elastic Agent Builder: `search_memory` (hybrid ELSER + BM25), `store_memory`, `delete_memory`. Exposed as MCP endpoints the Gemini agent calls directly.

2. **Memory abstraction layer** — Abstract `MemoryBackend` interface in Python. Two implementations: `ElasticMemoryBackend` (Elasticsearch via MCP) and `EngramMemoryBackend` (Engram-rs CLI / SQLite). Same API surface, swap backends by changing one environment variable.

3. **Agent tools** — Three MCP-callable tools: `ProjectContextTool` (manage project stack/conventions), `DecisionLogTool` (log and recall architectural decisions with rationale), `KnowledgeGraphTool` (cross-reference memories, find patterns, compound knowledge).

4. **Session lifecycle** — `start_session()` loads all relevant context from Elastic. `process_message()` enriches every prompt with hybrid search results. `end_session()` reflects on new knowledge and compounds insights.

5. **Backend-agnostic** — The abstract interface means the same agent code works with Elastic (managed) or Engram-rs (self-hosted). Demo shows the swap live.

---

## Why Elastic

Elastic Agent Builder was the natural choice because it's the only partner with a built-in **context layer for memory and insights**:

- **Hybrid search** (ELSER semantic + BM25 keyword) gives accurate recall that pure vector search or pure keyword search can't match alone
- **ES|QL** enables complex memory queries without custom code
- **MCP server** makes tools immediately available to Gemini — no custom integration layer needed
- **Elasticsearch** scales from hackathon demo to production without changing the API

---

## What's Next

- **Multi-project awareness** — Agent recognizes cross-project patterns (e.g., "you use this same auth pattern in 3 repos")
- **Memory confidence decay** — Facts automatically lose confidence if unverified, prompting re-verification
- **MCP-native Engram-rs** — Direct MCP server in Engram-rs so it plugs into Agent Builder without the CLI wrapper

---

## Built With

- **Google Cloud Agent Builder** (Gemini 3 Pro)
- **Elastic Cloud** (Elasticsearch, ELSER, BM25)
- **Elastic Agent Builder** (MCP tools)
- **Engram-rs** (Self-hosted memory, MIT, Rust + SQLite + FTS5)
- **Python 3.12** (Pydantic, async/await)
- **MCP** (Model Context Protocol)
