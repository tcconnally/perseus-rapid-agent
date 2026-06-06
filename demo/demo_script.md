# 3-Minute Demo Script — Perseus Memory Agent

## Video Structure: 5 Scenes, ~35 seconds each

---

### Scene 1: The Problem (0:00–0:35)

**Visual:** Screen recording of a terminal. Developer types: "What database are we using?"

**Narration:**
> "Every developer knows this pain. You start a new session with your AI coding agent, and the first thing you have to do is re-explain your entire project. What stack are we on? What database? What decisions did we make last week? The agent has amnesia."

**Visual:** Switch to generic AI agent response: "I don't have context about your project. Could you tell me about your database setup?"

**Narration:**
> "That's the problem Perseus Memory Agent solves. Persistent, evolving memory for AI agents — so they remember your project across sessions."

---

### Scene 2: Session 1 — Teaching the Agent (0:35–1:10)

**Visual:** Google Cloud Agent Builder interface. Show Gemini 3 Pro with Elastic MCP tools connected.

**Narration:**
> "In session one, I tell the agent about my project. Tech stack, coding conventions, architectural decisions."

**Visual steps:**
1. Type: "I'm working on hermes-agent. It's a Python 3.12 project using FastAPI, PostgreSQL with pgvector, and the Claude API."
2. Agent responds: "Got it. Storing 5 facts to memory via Elastic."
3. Type: "We use Black for formatting, 100 char lines, and async/await everywhere."
4. Agent: "Stored 3 coding conventions."
5. Type: "We chose pgvector over Pinecone to keep everything self-hosted."
6. Agent: "Decision logged with rationale and alternatives."

**Narration:**
> "Everything the agent learns is stored persistently in Elasticsearch via MCP tools. Next session, it remembers."

---

### Scene 3: Session 2 — The Agent Remembers (1:10–1:45)

**Visual:** New Agent Builder session (show it's a fresh session — close and reopen).

**Narration:**
> "Next day. Fresh session. I ask the agent a question without providing any context."

**Visual:**
1. Type: "I need to add a new endpoint. What database are we using and why?"
2. Agent calls `recall` MCP tool → sees "pgvector" results
3. Agent responds: "You're using PostgreSQL with pgvector for vector storage. You chose this over Pinecone on June 3rd to keep everything self-hosted. The connection string is configured in your .env. As for the new endpoint, which route prefix?"

**Narration:**
> "No re-explaining. No repeated context. The agent remembers what database we use AND why we chose it. That's the power of persistent memory."

---

### Scene 4: Session 3 — Knowledge Compounds (1:45–2:15)

**Visual:** Continue session. Show knowledge compounding.

**Narration:**
> "Over multiple sessions, the agent doesn't just remember — it compounds knowledge. It spots patterns."

**Visual:**
1. Show `find_patterns` tool output — the agent identifies: "You've had 3 performance issues related to async connection pooling. Consider implementing a connection pool monitor."
2. Agent proactively surfaces: "I notice you consistently use Pydantic v2 for all new models, but the user-service still has 4 v1 models. Want me to flag those for migration?"
3. Show knowledge summary: "I know 47 facts, 12 decisions, 8 conventions about this project across 5 sessions."

**Narration:**
> "The agent gets smarter about your codebase over time. It's not just memory — it's institutional knowledge."

---

### Scene 5: Backend Swap — Elastic ⇄ Engram-rs (2:15–2:50)

**Visual:** Split screen. Left: Elastic Cloud dashboard. Right: local terminal with Engram-rs.

**Narration:**
> "And here's the best part. The hackathon uses Elastic for the memory backend. But if you want the same persistent memory without cloud dependencies..."

**Visual:**
1. Change one line: `MEMORY_BACKEND=elastic` → `MEMORY_BACKEND=engram`
2. Run the exact same agent code
3. Agent works identically — stores facts, recalls them, compounds knowledge

**Narration:**
> "...you swap one config line to Engram-rs — our open-source, MIT-licensed, SQLite-backed memory system. Same API. Same behavior. Zero cloud dependencies. Run it on a Raspberry Pi if you want."

---

### Closing (2:50–3:00)

**Visual:** GitHub repo README + `engram-rs` GitHub stars + links.

**Narration:**
> "Perseus Memory Agent: persistent memory for AI agents. Elastic for the cloud. Engram-rs for self-hosted. One API. Full code on GitHub — MIT licensed. Built for the Google Cloud Rapid Agent Hackathon 2026."

**On-screen:**
- github.com/tcconnally/perseus-rapid-agent
- github.com/tcconnally/engram-rs
- Google Cloud Rapid Agent Hackathon — Elastic Track
