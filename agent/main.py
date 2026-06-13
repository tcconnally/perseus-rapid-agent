"""Perseus Memory Agent — main agent loop.

A Gemini-powered agent with persistent memory that compounds knowledge
across sessions. Runs inside Google Cloud Agent Builder (with Elastic MCP)
or standalone with Engram-rs.

Core behavior:
  1. On session start: recall relevant context from memory
  2. During conversation: store facts, decisions, and lessons
  3. On session end: reflect on new knowledge, compound insights

Usage:
  # With Elastic (cloud) — via Google Cloud Agent Builder MCP:
  MEMORY_BACKEND=elastic python -m agent.main

  # With Engram-rs (self-hosted):
  MEMORY_BACKEND=engram python -m agent.main
"""

import asyncio
import sys
from datetime import datetime, timezone

from agent.config import AgentConfig
from agent.memory import ElasticMemoryBackend, EngramMemoryBackend, MemoryEntry
from agent.tools import DecisionLogTool, KnowledgeGraphTool, ProjectContextTool


class PerseusMemoryAgent:
    """The agent that never forgets.

    Wraps Gemini's reasoning with persistent memory via Elastic or Engram-rs.
    Designed to run inside Google Cloud Agent Builder as a tooled agent.
    """

    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self._validate_config()

        # Select backend based on config
        if self.config.memory_backend == "engram":
            self.memory = EngramMemoryBackend()
        else:
            self.memory = ElasticMemoryBackend()

        # Initialize tools
        self.project_context = ProjectContextTool(self.memory)
        self.decision_log = DecisionLogTool(self.memory)
        self.knowledge_graph = KnowledgeGraphTool(self.memory)

        self.session_id = None
        self.current_project = None

    def _validate_config(self):
        issues = self.config.validate()
        if issues:
            print("Configuration issues:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            if any("required" in i.lower() for i in issues):
                raise ValueError(
                    "Missing required configuration. "
                    "Copy .env.example to .env and fill in your credentials."
                )

    async def start_session(self, project: str) -> dict:
        """Begin a new agent session.

        Loads all relevant context from memory so the agent starts informed,
        not amnesiac.
        """
        self.session_id = f"session-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.current_project = project

        # Recall what we know about this project
        context = await self.project_context.get_project_context(project)
        decisions = await self.decision_log.list_decisions(project)
        knowledge = await self.knowledge_graph.summarize_knowledge(project)

        # If this is session 3+ with auto_reflect, look for patterns
        insights = None
        if self.config.auto_reflect:
            insights = await self.knowledge_graph.find_patterns(project)

        session_context = {
            "session_id": self.session_id,
            "project": project,
            "context": context,
            "past_decisions": decisions,
            "knowledge_summary": knowledge,
            "insights": insights,
            "memory_backend": self.config.memory_backend,
        }

        print(f"\n{'='*60}")
        print(f"Perseus Memory Agent — Session Started")
        print(f"  Session: {self.session_id}")
        print(f"  Project: {project}")
        print(f"  Backend: {self.config.memory_backend}")
        print(f"  Context loaded: {context['total_facts']} facts")
        print(f"  Past decisions: {len(decisions)}")
        print(f"  Knowledge: {knowledge['knowledge']}")
        print(f"{'='*60}\n")

        return session_context

    async def process_message(self, message: str) -> dict:
        """Process a user message with full memory context.

        In Agent Builder, this is called by Gemini after it retrieves
        relevant memories via the MCP tools.
        """
        # Recall memories relevant to the message
        relevant = await self.memory.recall(
            query=message,
            project=self.current_project,
            limit=self.config.recall_count,
        )

        # Check past decisions that might apply
        related_decisions = await self.decision_log.recall_decisions(
            query=message,
            project=self.current_project,
        )

        return {
            "message": message,
            "relevant_memories": [
                {"content": r.entry.content, "score": r.score, "method": r.search_method}
                for r in relevant
            ],
            "related_decisions": related_decisions,
            "context_loaded": len(relevant) > 0,
        }

    async def learn(self, fact: str, category: str = "fact", tags: list[str] = None) -> str:
        """Store a new fact, preference, or lesson in memory."""
        entry = MemoryEntry(
            content=fact,
            category=category,
            project=self.current_project,
            tags=tags or [],
            source_session=self.session_id,
        )
        return await self.memory.remember(entry)

    async def end_session(self) -> dict:
        """End the session. Reflect on new knowledge and compound insights."""
        # Log what we learned this session
        summary_entry = MemoryEntry(
            content=f"Session {self.session_id} completed for project {self.current_project}",
            category="fact",
            project=self.current_project,
            tags=["session-summary"],
            source_session=self.session_id,
        )
        await self.memory.remember(summary_entry)

        # Auto-reflect to find patterns across sessions
        insights = None
        if self.config.auto_reflect:
            insights = await self.knowledge_graph.find_patterns(self.current_project)

        session_summary = {
            "session_id": self.session_id,
            "project": self.current_project,
            "insights": insights,
            "backend": self.config.memory_backend,
        }

        print(f"\n{'='*60}")
        print(f"Session ended: {self.session_id}")
        print(f"Memory backend: {self.config.memory_backend}")
        if insights:
            print(f"Insights found: {len(insights.get('insights', []))}")
        print(f"{'='*60}\n")

        return session_summary


async def demo_elastic_session():
    """Demonstrate the agent with Elastic backend (hackathon default)."""
    config = AgentConfig()
    config.memory_backend = "elastic"

    agent = PerseusMemoryAgent(config)

    # Session 1: Developer introduces their project
    await agent.start_session("hermes-agent")

    print("--- Session 1: Developer introduces their project ---")
    await agent.project_context.set_project_context(
        project="hermes-agent",
        stack={
            "language": "Python 3.12",
            "framework": "FastAPI",
            "database": "PostgreSQL + pgvector",
            "ai": "Claude API + Gemini",
        },
        conventions=[
            "Use type hints everywhere",
            "async/await for all I/O",
            "pytest with async support for testing",
            "Black for formatting, 100 char line length",
        ],
        architecture="Microservices with Redis message bus between agent orchestrator and tool executors",
    )

    await agent.learn(
        "Hermes Agent uses Pydantic v2 for all data models",
        category="fact",
        tags=["data", "validation"],
    )

    await agent.decision_log.log_decision(
        project="hermes-agent",
        decision="Use pgvector instead of Pinecone for vector storage",
        rationale="Keeps everything in one database, reduces operational complexity",
        alternatives=["Pinecone", "Weaviate", "Qdrant"],
        context="Self-hosted deployment, no external service dependencies wanted",
        tags=["infrastructure", "vector-db"],
    )

    await agent.end_session()

    # Session 2: Agent recalls context without being reminded
    print("\n--- Session 2 (next day): Agent recalls context ---")
    await agent.start_session("hermes-agent")
    context = await agent.process_message(
        "I need to add a new API endpoint. What database are we using?"
    )

    print("Agent recalls from memory:")
    for mem in context["relevant_memories"]:
        print(f"  [{mem['score']:.2f}] {mem['content']}")

    print("\nRelated past decisions:")
    for dec in context["related_decisions"]:
        print(f"  {dec['metadata'].get('decision', dec['content'][:80])}")

    # Semantic recall beat: this query shares no keywords with the stored
    # decision ("pgvector instead of Pinecone for vector storage") — on a
    # deployment with ELSER it matches semantically; on plain keyword
    # search it demonstrates the graceful-degradation path.
    semantic_hits = await agent.memory.recall(
        query="how do we handle embeddings?",
        project="hermes-agent",
        limit=3,
    )
    print('\nSemantic recall — "how do we handle embeddings?":')
    if semantic_hits:
        for r in semantic_hits:
            print(f"  [{r.score:.2f}] ({r.search_method}) {r.entry.content}")
    else:
        print("  (no semantic match — index is keyword-only on this deployment)")

    await agent.end_session()

    # Session 3: Agent compounds knowledge, spots patterns
    print("\n--- Session 3: Agent compounds knowledge ---")
    await agent.start_session("hermes-agent")
    await agent.learn(
        "Performance testing revealed pgvector index needs maintenance weekly",
        category="lesson",
        tags=["performance", "postgres", "ops"],
    )
    await agent.learn(
        "Async session management caused connection pool exhaustion at 500 concurrent users",
        category="lesson",
        tags=["performance", "async", "connection-pool"],
    )

    patterns = await agent.knowledge_graph.find_patterns("hermes-agent")
    print("Agent identifies patterns:")
    for insight in patterns.get("insights", []):
        print(f"  💡 {insight.get('summary', insight)}")

    await agent.end_session()


async def demo_engram_session():
    """Demonstrate the same agent with Engram-rs (self-hosted).

    Same API, different backend. Zero code changes.
    """
    config = AgentConfig()
    config.memory_backend = "engram"
    config.auto_reflect = False  # reflect requires engram >= 0.2.0

    agent = PerseusMemoryAgent(config)

    await agent.start_session("perseus")

    print("--- Engram-rs Session ---")
    await agent.learn(
        "Perseus uses AGENTS.md files for persistent project context",
        category="fact",
        tags=["architecture", "context"],
    )

    await agent.learn(
        "Engram-rs is the long-term memory backend for Perseus — SQLite-backed, MIT licensed",
        category="fact",
        tags=["memory", "engram-rs"],
    )

    results = await agent.memory.recall(query="memory backend", project="perseus")
    print("Recall results:")
    for r in results:
        print(f"  [{r.score:.2f}] {r.entry.content}")

    await agent.end_session()


async def main():
    """Entry point. Run demos for both backends."""
    import os

    backend = os.getenv("MEMORY_BACKEND", "elastic")

    print("=" * 60)
    print("  Perseus Memory Agent")
    print(f"  Backend: {backend}")
    print("  Google Cloud Rapid Agent Hackathon 2026")
    print("=" * 60)

    # Health check
    config = AgentConfig()
    agent = PerseusMemoryAgent(config)
    health = await agent.memory.health_check()
    print(f"\nMemory backend health: {health['status']}")
    print(f"  Type: {health['backend']}")

    if backend == "engram":
        await demo_engram_session()
    else:
        await demo_elastic_session()

    print("\n✅ Demo complete. See demo/demo_script.md for the 3-minute video script.")


if __name__ == "__main__":
    asyncio.run(main())
