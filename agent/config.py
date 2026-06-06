"""Agent configuration — single source of truth.

Switch backends by changing MEMORY_BACKEND:
  - "elastic" → Elastic Agent Builder MCP (cloud)
  - "engram"  → Engram-rs (self-hosted)

Everything else in the agent is backend-agnostic.
"""

import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for the Perseus Memory Agent."""

    # Memory backend selection: "elastic" or "engram"
    memory_backend: str = field(
        default_factory=lambda: os.getenv("MEMORY_BACKEND", "elastic")
    )

    # Google Cloud / Vertex AI Agent Builder
    gcp_project_id: str = field(
        default_factory=lambda: os.getenv("GCP_PROJECT_ID", "")
    )
    gcp_region: str = field(
        default_factory=lambda: os.getenv("GCP_REGION", "us-central1")
    )

    # Elastic Cloud
    elastic_cloud_id: str = field(
        default_factory=lambda: os.getenv("ELASTIC_CLOUD_ID", "")
    )
    elastic_api_key: str = field(
        default_factory=lambda: os.getenv("ELASTIC_API_KEY", "")
    )
    elastic_memory_index: str = field(
        default_factory=lambda: os.getenv("ELASTIC_MEMORY_INDEX", "perseus-agent-memory")
    )

    # Engram-rs
    engram_bin: str = field(
        default_factory=lambda: os.getenv("ENGRAM_BIN", "engram")
    )
    engram_db_path: str = field(
        default_factory=lambda: os.getenv(
            "ENGRAM_DB_PATH",
            os.path.expanduser("~/.hermes/mnemosyne/data/mnemosyne.db"),
        )
    )

    # Agent behavior
    max_context_tokens: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONTEXT_TOKENS", "32000"))
    )
    recall_count: int = field(
        default_factory=lambda: int(os.getenv("RECALL_COUNT", "10"))
    )
    auto_reflect: bool = field(
        default_factory=lambda: os.getenv("AUTO_REFLECT", "true").lower() == "true"
    )

    def validate(self) -> list[str]:
        """Validate configuration. Returns list of issues (empty = valid)."""
        issues = []

        if self.memory_backend not in ("elastic", "engram"):
            issues.append(f"Invalid MEMORY_BACKEND: {self.memory_backend}")

        if self.memory_backend == "elastic":
            if not self.elastic_cloud_id:
                issues.append("ELASTIC_CLOUD_ID is required for elastic backend")
            if not self.elastic_api_key:
                issues.append("ELASTIC_API_KEY is required for elastic backend")

        if self.memory_backend == "engram":
            # Engram-rs can work without explicit config if binary is in PATH
            pass

        return issues
