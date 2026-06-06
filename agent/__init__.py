"""Perseus Memory Agent — persistent memory for AI agents.

Google Cloud Rapid Agent Hackathon 2026 — Elastic Partner Track.
"""

from agent.config import AgentConfig
from agent.main import PerseusMemoryAgent
from agent.memory import (
    ElasticMemoryBackend,
    EngramMemoryBackend,
    MemoryBackend,
    MemoryEntry,
    MemorySearchResult,
)

__all__ = [
    "AgentConfig",
    "PerseusMemoryAgent",
    "MemoryBackend",
    "MemoryEntry",
    "MemorySearchResult",
    "ElasticMemoryBackend",
    "EngramMemoryBackend",
]
