# AGENTS.md — Project Context for AI Agents

## Project Identity
- **Name:** Perseus Memory Agent
- **Purpose:** Google Cloud Rapid Agent Hackathon 2026 submission (Elastic Partner Track)
- **Stack:** Python 3.12, Google Cloud Agent Builder, Elastic MCP, Mimir
- **License:** MIT

## Architecture
- `agent/main.py` — Core agent loop (PerseusMemoryAgent class)
- `agent/memory/` — Abstract MemoryBackend + Elastic + Engram-rs implementations
- `agent/tools/` — MCP tools: project_context, decision_log, knowledge_graph
- `agent/config.py` — Single source of truth; switch backends by changing MEMORY_BACKEND

## Key Design Decisions
1. **Abstract MemoryBackend** — Both Elastic and Engram-rs implement the same interface. Backend swap = one env var.
2. **No heavy deps** — Agent Builder provides Gemini + MCP. Standalone only needs pydantic + python-dotenv.
3. **Session lifecycle** — start_session() loads context → process_message() with recall → end_session() with reflect.
4. **Memory categories** — fact, decision, preference, lesson, link, context

## Conventions
- async/await for all I/O operations
- Type hints on all public methods
- MemoryEntry dataclass for all memory operations
- Tools are stateless; memory backend is the single state holder

## Testing
```bash
# Run the demo (Elastic backend)
python -m agent.main

# Run with Engram-rs
MEMORY_BACKEND=engram python -m agent.main
```
