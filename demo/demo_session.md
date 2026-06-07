# Demo Session Transcript

Example interaction showing the agent remembering across sessions.

---

## Session 1: Introducing the Project

**Developer:**
> I'm working on hermes-agent. It's a Python 3.12 async project using FastAPI for the REST layer, PostgreSQL with pgvector for vector storage, and the Claude API for LLM calls. We run on Docker with docker-compose.

**Perseus Memory Agent:**
> Got it! I've stored your project context in memory:
> - **Stack:** Python 3.12, FastAPI, PostgreSQL + pgvector, Claude API, Docker
> - **Category:** fact × 5 entries
> 
> I'll remember this for future sessions. Anything else I should know about how you work?

**Developer:**
> Yeah — we use Black for formatting (100 chars), mypy strict mode, and pytest with pytest-asyncio. All I/O must be async. And we chose pgvector over Pinecone because we want everything self-hosted.

**Perseus Memory Agent:**
> Stored:
> - 3 coding conventions (formatting, type checking, testing)
> - 1 I/O rule (async only)
> - Decision logged: pgvector over Pinecone (rationale: self-hosted, single-DB simplicity)
> 
> I've noted the alternatives you considered (Pinecone, Weaviate, Qdrant) for future reference.

**Developer:**
> Oh right — the deployment model is microservices. Agent orchestrator communicates with tool executors via Redis pub/sub. Each tool is a separate container.

**Perseus Memory Agent:**
> Architecture noted: microservices with Redis message bus. Stored as fact with tag "architecture".

---

## Session 2: Next Day — Agent Remembers

**Developer:**
> Hey — I need to add a new API endpoint for user preferences. What DB are we using again?

**Perseus Memory Agent:**
> *(recalls from memory — no re-explanation needed)*
> 
> You're using **PostgreSQL with pgvector** for vector storage. You chose this over Pinecone on our first session to keep everything self-hosted and reduce operational complexity.
> 
> For the user preferences endpoint — since we use FastAPI with async/await, you'll want to add it under the existing user router. Would you like me to draft the endpoint following your conventions (Pydantic v2 models, async handler, pytest-asyncio test)?

**Developer:**
> Whoa, you remember all that?

**Perseus Memory Agent:**
> That's the point! I currently hold **47 facts**, **12 decisions**, and **8 conventions** about hermes-agent across our sessions. I load this context at the start of every session so you never have to repeat yourself.

---

## Session 3: Knowledge Compounding

**Developer:**
> We're getting connection pool exhaustion at ~500 concurrent users. Ideas?

**Perseus Memory Agent:**
> *(cross-references memories)*
> 
> I've noticed a pattern. In the past 3 sessions, you've logged these related issues:
> 1. **Session 1:** "async session management needs tuning for high concurrency"
> 2. **Session 2:** "pgvector index maintenance should be weekly, not daily"
> 3. **Now:** Connection pool exhaustion at 500 users
> 
> **Insight:** These all point to database connection management under load. Based on your previous decisions:
> - You're using asyncpg with a pool size of 20
> - FastAPI's default connection pooling might not scale for your workload
> 
> **Recommendation:** Consider implementing a connection pool monitor (you mentioned wanting self-hosted solutions — I'd suggest adding a pgBouncer sidecar to your docker-compose, which aligns with your "single-DB, self-hosted" philosophy from June 3rd).

**Developer:**
> That's... actually really helpful. You connected dots I hadn't.

**Perseus Memory Agent:**
> That's the compounding effect. Every session I learn more about your codebase, your preferences, and your problems. The longer we work together, the more useful I become.
