# Perseus Rapid Agent — Elastic Partner Track

**One env var. Cloud to self-hosted. Same agent, zero code changes.**

A Gemini-powered agent with persistent project memory. Switches between Elastic Cloud (ELSER semantic search, ES|QL, Kibana) and Engram-rs (local SQLite+FTS5) by changing one environment variable. Built for the [Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/) — Elastic Partner Track.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Hackathon: Elastic Partner Track](https://img.shields.io/badge/hackathon-Elastic%20Partner%20Track-teal)]()

## The Dual-Backend Architecture

```
                  MemoryBackend (abstract)
                 /                      \
    Elastic Cloud (MCP)          Engram-rs (local)
    · ELSER semantic search      · SQLite + FTS5
    · ES|QL reflect queries      · Sub-millisecond recall
    · Kibana dashboard           · Zero cloud deps
    · Managed, scalable          · Self-hosted, MIT
```

| | Elastic (Cloud) | Engram-rs (Local) |
|---|---|---|
| **Search** | ELSER semantic | FTS5 keyword |
| **Queries** | ES|QL structured | SQL |
| **Dashboard** | Kibana | None |
| **Deps** | Elastic Cloud account | Zero |
| **Swap cost** | `MEMORY_BACKEND=elastic` | `MEMORY_BACKEND=engram` |

## Why Semantic Search Matters

```
Query: "how to build fast"
Memory: "we use Rust for speed"

Engram (Keyword):  ✗ MISS — "build fast" ≠ "Rust for speed"
Elastic (ELSER):   ✓ MATCH (0.84) — ELSER understands Rust is fast
```

Hybrid search finds what keywords miss. The dual-backend architecture lets you choose.

## Quick Start

```bash
# Clone and install
git clone https://github.com/tcconnally/perseus-rapid-agent.git
cd perseus-rapid-agent
pip install -r requirements.txt

# Elastic Cloud (partner track)
export MEMORY_BACKEND=elastic
export ELASTIC_CLOUD_ID=...
python -m agent.main

# Engram-rs (self-hosted, zero cloud)
export MEMORY_BACKEND=engram
python -m agent.main
```

## Demo: 3-Minute Walkthrough

1. **Session 1** — Developer tells agent about their project stack
2. **Session 2** — Agent recalls project context without being reminded
3. **Session 3** — Agent compounds knowledge, notices a pattern from past sessions
4. **Backend Switch** — Same code, swap Elastic → Engram-rs, memory persists

## Hackathon Details

- **Platform:** Google Cloud Rapid Agent Hackathon on Devpost
- **Track:** Elastic Partner Track
- **License:** MIT

---

[Website](https://perseus.observer/rapid-agent/) · [Engram-rs](https://github.com/tcconnally/engram-rs)
