# Architecture — Perseus Memory Agent

## Overview

Perseus Memory Agent wraps Gemini's reasoning with persistent memory. The agent learns about your project across sessions, recalls relevant context on demand, and compounds knowledge over time. It's backend-agnostic — the same agent code works with Elastic (managed cloud) or Engram-rs (self-hosted open source).

## System Design

```
┌──────────────────────────────────────────────────────────────┐
│                     Google Cloud Agent Builder                 │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Perseus Memory Agent                   │ │
│  │                                                         │ │
│  │  ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │ │
│  │  │  Gemini  │◄──►│   Perseus    │◄──►│   Memory     │  │ │
│  │  │  3 Pro   │    │  Memory      │    │   Backend    │  │ │
│  │  │          │    │  Agent       │    │              │  │ │
│  │  └──────────┘    └──────┬───────┘    └──────┬───────┘  │ │
│  │                         │                   │          │ │
│  │              ┌──────────┴──────────┐  ┌─────┴──────┐  │ │
│  │              │     MCP Tools       │  │            │  │ │
│  │              │  • Project Context  │  │  Elastic   │  │ │
│  │              │  • Decision Log     │  │  (MCP)     │  │ │
│  │              │  • Knowledge Graph  │  │            │  │ │
│  │              └─────────────────────┘  └────────────┘  │ │
│  │                                                         │ │
│  │              ┌─────────────────────┐                    │ │
│  │              │    Engram-rs        │  ← OSS alternative │ │
│  │              │    (SQLite)         │                    │ │
│  │              └─────────────────────┘                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Memory Backend Interface

Both backends implement `MemoryBackend` with four operations:

```
MemoryBackend
├── remember(entry) → entry_id    # Store a fact/decision/preference
├── recall(query, filters) → []   # Semantic + keyword search
├── forget(entry_id) → bool       # Remove outdated info
├── reflect(project) → insights   # Cross-reference, find patterns
└── health_check() → status       # Backend connectivity
```

### Elastic Backend
- **Search:** Hybrid (ELSER semantic + BM25 keyword + vector)
- **Storage:** Elasticsearch Serverless on Google Cloud
- **Analysis:** ES|QL for pattern detection, aggregation
- **Connection:** MCP server in Kibana Agent Builder

### Engram-rs Backend
- **Search:** SQLite FTS5 full-text search
- **Storage:** Single SQLite file (`mnemosyne.db`)
- **Analysis:** SQL queries for cross-referencing
- **Connection:** Local CLI subprocess

## Session Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  START       │     │  PROCESS     │     │  END         │
│  SESSION     │────►│  MESSAGES    │────►│  SESSION     │
│              │     │              │     │              │
│ • Load       │     │ • Recall     │     │ • Reflect    │
│   context    │     │   relevant   │     │   on new     │
│ • List       │     │   memories   │     │   knowledge  │
│   decisions  │     │ • Check      │     │ • Compound   │
│ • Summarize  │     │   past       │     │   insights   │
│   knowledge  │     │   decisions  │     │ • Store      │
│ • Find       │     │ • Learn new  │     │   session    │
│   patterns   │     │   facts      │     │   summary    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Memory Categories

| Category | Purpose | Example |
|---|---|---|
| `fact` | Objective project information | "Uses PostgreSQL 16 with pgvector 0.7" |
| `decision` | Architectural choices + rationale | "Chose pgvector over Pinecone to reduce dependencies" |
| `preference` | Coding conventions, style choices | "Use Black with 100 char line length" |
| `lesson` | Things learned from experience | "pgvector index needs weekly REINDEX for performance" |
| `link` | Relationships between memories | "Decision-X was motivated by Fact-Y" |

## MCP Tool Interface

The agent exposes these tools via MCP for Gemini to call:

| Tool | Operation | MCP Equivalent |
|---|---|---|
| `set_project_context` | Store stack + conventions | Elastic `index_document` |
| `get_project_context` | Recall project state | Elastic `search` (hybrid) |
| `log_decision` | Record decision + rationale | Elastic `index_document` |
| `recall_decisions` | Find relevant past decisions | Elastic `search` with filters |
| `find_patterns` | Cross-reference knowledge | Elastic `esql_query` |
| `summarize_knowledge` | Overview of all memories | Elastic `search` aggregation |

## Configuration

Single `.env` file controls everything:

```bash
# Backend selection (one line swap)
MEMORY_BACKEND=elastic|engram

# Elastic (cloud)
ELASTIC_CLOUD_ID=...
ELASTIC_API_KEY=*** Engram (self-hosted)
ENGRAM_BIN=engram
ENGRAM_DB_PATH=~/.hermes/mnemosyne/data/mnemosyne.db

# Agent behavior
MAX_CONTEXT_TOKENS=32000
RECALL_COUNT=10
AUTO_REFLECT=true
```

## Why This Architecture

1. **Backend agnosticism** — The MemoryBackend ABC means Elastic and Engram-rs are interchangeable. This matters for the hackathon because it shows Elastic as the managed solution AND Engram-rs as the OSS alternative, both usable with the same agent.

2. **Memory categories** — Separating facts from decisions from preferences lets the agent retrieve the right TYPE of information for each query. "What database?" → fact. "Why that database?" → decision.

3. **Session lifecycle** — start/process/end mirrors how developers actually work. Load context on start, process during, reflect on end.

4. **Tool composability** — Each tool is independent and stateless. Memory backend is the single state holder. This makes the agent easy to extend — add a new tool without touching existing ones.
