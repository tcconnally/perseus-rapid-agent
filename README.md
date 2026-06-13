# Perseus Memory Agent

> **Google Cloud Rapid Agent Hackathon 2026 — Elastic Partner Track**
>
> *"Your agents shouldn't have amnesia."*

An agent that builds **persistent project context** across sessions — remembering decisions, preferences, domain knowledge, and codebase facts so developers never have to repeat themselves.

Built for **Google Cloud Agent Builder** (+ **Elastic Agent Builder MCP**) for the hackathon, with **Mimir** as the open-source, self-hosted memory alternative.

---

## The Problem

Every time you start a new session with an AI coding agent, you spend the first 10 minutes re-explaining your project. Your stack. Your conventions. Your decisions. The agent has amnesia.

## The Solution

**Perseus Memory Agent** gives agents persistent, evolving memory:

- **Remembers** your project stack, conventions, and architectural decisions
- **Recalls** past debugging sessions and their resolutions
- **Compounds** knowledge — the agent gets smarter about YOUR codebase over time
- **Switches backends** — Elastic (managed) or Engram-rs (self-hosted), same API

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Google Cloud Agent Builder             │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Perseus Memory Agent                  │  │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ Gemini  │  │  Context │  │  Memory Backend  │  │  │
│  │  │  3 Pro  │◄─┤  Manager ├──┤  ┌────────────┐  │  │  │
│  │  │         │  │          │  │  │ Elastic    │  │  │  │
│  │  └─────────┘  └──────────┘  │  │ (MCP)      │  │  │  │
│  │       │                     │  ├────────────┤  │  │  │
│  │       ▼                     │  │ Engram-rs  │  │  │  │
│  │  ┌──────────┐               │  │ (OSS alt)  │  │  │  │
│  │  │  MCP     │               │  └────────────┘  │  │  │
│  │  │  Tools   │               └──────────────────┘  │  │
│  │  └──────────┘                                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Memory Operations

| Operation | Description | Elastic Backend | Engram-rs Backend |
|---|---|---|---|
| `remember` | Store facts, decisions, context | Elasticsearch index | SQLite via engram CLI |
| `recall` | Semantic search over memory | Elastic hybrid search | Engram text search |
| `forget` | Prune outdated/incorrect facts | Delete by ID | Remove entry |
| `reflect` | Cross-reference and synthesize | ES|QL aggregations | SQL queries |

---

## Quick Start

### Prerequisites

- Google Cloud project with **Vertex AI Agent Builder** enabled
- Elastic Cloud account (free trial: [cloud.elastic.co](https://cloud.elastic.co))
- Or: [Engram-rs](https://github.com/tcconnally/engram-rs) installed locally

### Setup

```bash
# Clone the repo
git clone https://github.com/tcconnally/perseus-rapid-agent.git
cd perseus-rapid-agent

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run the agent
python -m agent.main
```

See [`setup/`](setup/) for detailed GCP, Elastic, and local setup guides.

---

## Demo: 3-Minute Walkthrough

1. **Session 1** — Developer tells agent about their project stack
2. **Session 2** — Agent recalls project context without being reminded
3. **Session 3** — Agent compounds knowledge, notices a pattern from past sessions
4. **Backend Switch** — Same code, swap Elastic → Engram-rs, memory persists

See [`demo/demo_script.md`](demo/demo_script.md) for the full script.

---

## Project Structure

```
perseus-rapid-agent/
├── agent/
│   ├── main.py                  # Agent entry point
│   ├── config.py                # Configuration
│   ├── memory/
│   │   ├── backend.py           # Abstract memory interface
│   │   ├── elastic_memory.py    # Elastic (MCP) implementation
│   │   └── engram_memory.py     # Engram-rs implementation
│   └── tools/
│       ├── project_context.py   # Project context management
│       ├── decision_log.py      # Decision logging & recall
│       └── knowledge_graph.py   # Knowledge compounding
├── demo/
│   ├── demo_script.md           # 3-minute demo script
│   └── demo_session.md          # Example session transcript
├── setup/
│   ├── gcp_setup.md             # Google Cloud setup
│   ├── elastic_setup.md         # Elastic Cloud setup
│   └── local_setup.md           # Local Engram-rs setup
├── docs/
│   ├── ARCHITECTURE.md          # Technical architecture
│   └── SUBMISSION.md            # Full hackathon submission text
├── requirements.txt
├── .env.example
├── AGENTS.md
├── LICENSE                      # MIT
└── README.md
```

---

## Why Elastic?

Elastic Agent Builder provides the **context layer for memory & insights** — the exact infrastructure an agent needs to build retrievable intelligence over time:

- **Hybrid search** (semantic + keyword + vector) for accurate recall
- **ES|QL** for custom memory queries without extra code
- **Write-back** — agent outputs stored directly in Elasticsearch
- **MCP native** — tools are immediately available via MCP server

## Why Engram-rs?

For developers who want the same persistent memory without cloud dependencies:

- **Self-hosted** — runs on your own hardware
- **MIT licensed** — fully open source
- **Same API surface** — swap backends, zero code changes
- **SQLite-backed** — simple, reliable, no infrastructure

---

## Hackathon Details

- **Platform:** [Google Cloud Rapid Agent Hackathon on Devpost](https://rapid-agent.devpost.com/)
- **Track:** Elastic
- **Deadline:** June 11, 2026
- **License:** MIT
