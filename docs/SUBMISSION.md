# Devpost Submission — Perseus Memory Agent

## Step 1: Manage Team ✅
- **Team:** tcconnally (solo)

---

## Step 2: Project Overview

### Project Name
```
Perseus Memory Agent
```

### Elevator Pitch (max 200 chars)
```
Your AI agent shouldn't have amnesia. Perseus gives Gemini agents persistent memory across sessions — remembering your stack, decisions, and lessons. Elastic (cloud) or Engram-rs (self-hosted), same API.
```

---

## Step 3: Project Details

### What It Does
Perseus Memory Agent gives AI agents persistent, evolving memory so they remember project context across sessions. Instead of re-explaining your tech stack, conventions, and architectural decisions every time you start a new session, the agent recalls everything it learned about your project — even from weeks ago.

Key capabilities:
- **Remembers project context** — stack, conventions, architecture, preferences
- **Logs decisions with rationale** — why pgvector over Pinecone? The agent remembers
- **Compounds knowledge** — spots patterns across sessions, surfaces insights
- **Swappable backends** — Elastic (managed cloud) or Engram-rs (self-hosted MIT), one config line

### How I Built It
Built with Gemini 3 Pro in Google Cloud Agent Builder, connected to Elastic Agent Builder via MCP for the memory layer:

1. **Elastic MCP tools** — Defined three tools in Elastic Agent Builder: `search_memory` (hybrid semantic + keyword), `store_memory`, `delete_memory`. These are exposed as MCP endpoints that the Gemini agent calls.

2. **Memory abstraction layer** — Wrote an abstract `MemoryBackend` interface in Python. Two implementations: `ElasticMemoryBackend` (uses Elasticsearch via MCP) and `EngramMemoryBackend` (uses Engram-rs CLI / SQLite). Same API surface, swap back by changing one environment variable.

3. **Agent tools** — Built three MCP-callable tools: `ProjectContextTool` (manage project stack/conventions), `DecisionLogTool` (log and recall architectural decisions with rationale), `KnowledgeGraphTool` (cross-reference memories, find patterns, compound knowledge).

4. **Session lifecycle** — `start_session()` loads all relevant context from memory. `process_message()` enriches every prompt with recalled memories. `end_session()` reflects on new knowledge and compounds insights.

### Why Elastic
Elastic Agent Builder was the natural choice because it's the only partner with a built-in **context layer for memory and insights**. The hybrid search (ELSER semantic + BM25 keyword) gives accurate recall. ES|QL enables complex memory queries without custom code. And the MCP server makes tools immediately available to Gemini.

### What's Next
- **Multi-project awareness** — Agent recognizes cross-project patterns (e.g., "you use this same auth pattern in 3 repos")
- **Memory confidence decay** — Facts automatically lose confidence if unverified, prompting re-verification
- **MCP-native Engram-rs** — Direct MCP server in Engram-rs so it plugs into Agent Builder without the CLI wrapper

---

## Step 4: Additional Info

### GitHub Repository
```
https://github.com/tcconnally/perseus-rapid-agent
```

### Hosted Project URL
_(fill in after deploying on Google Cloud Agent Builder)_

### Demo Video
_(upload to YouTube or attach)_

### Partner Track
**Elastic**

### Open Source License
MIT — visible in repo root and About section

---

## Step 5: Submit ✅

### Checklist
- [ ] Public GitHub repo with MIT license at top
- [ ] Hosted demo on Google Cloud Agent Builder
- [ ] ~3 minute demo video
- [ ] Elastic MCP integration demonstrated
- [ ] All Devpost form fields completed
