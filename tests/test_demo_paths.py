"""Smoke tests for the demo paths and the memory backends.

The MemoryEntry id regression (TypeError on construction without id)
crashed both demos in session 1 — these tests exist so that class of
bug can't ship again. No Elastic deployment or engram binary required.
"""

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.config import AgentConfig  # noqa: E402
from agent.memory.backend import (  # noqa: E402
    MemoryBackend,
    MemoryBackendError,
    MemoryEntry,
    MemorySearchResult,
)


# ── MemoryEntry construction (the demo-crash regression) ────────────────────


def test_memory_entry_constructs_without_id():
    entry = MemoryEntry(content="x", category="fact", project="p")
    assert entry.id == ""


def test_memory_entry_tools_style_construction():
    # Exactly how agent/tools/*.py construct entries.
    entry = MemoryEntry(
        content="Architecture: microservices",
        category="fact",
        project="demo",
        tags=["architecture"],
    )
    assert entry.confidence == 1.0
    assert entry.tags == ["architecture"]


# ── Config validation ────────────────────────────────────────────────────────


def test_config_validation_catches_missing_elastic_creds(monkeypatch):
    monkeypatch.delenv("ELASTIC_CLOUD_ID", raising=False)
    monkeypatch.delenv("ELASTIC_API_KEY", raising=False)
    monkeypatch.setenv("MEMORY_BACKEND", "elastic")
    issues = AgentConfig().validate()
    assert any("ELASTIC_CLOUD_ID" in i for i in issues)
    assert any("ELASTIC_API_KEY" in i for i in issues)


def test_config_validation_rejects_unknown_backend(monkeypatch):
    monkeypatch.setenv("MEMORY_BACKEND", "carrier-pigeon")
    assert any("Invalid MEMORY_BACKEND" in i for i in AgentConfig().validate())


# ── Elastic backend (fake client — no deployment needed) ────────────────────


class FakeIndices:
    def __init__(self, exists=True, semantic=True):
        self._exists = exists
        self._semantic = semantic

    def exists(self, index):
        return self._exists

    def get_mapping(self, index):
        props = {"content": {"type": "text"}}
        if self._semantic:
            props["content_semantic"] = {"type": "semantic_text"}
        return {index: {"mappings": {"properties": props}}}

    def create(self, index, mappings):
        self._exists = True


class FakeES:
    def __init__(self, search_response=None, fail=False):
        self.indices = FakeIndices()
        self.indexed = []
        self.deleted = []
        self._search_response = search_response or {"hits": {"hits": []}}
        self._fail = fail

    def ping(self):
        return not self._fail

    def index(self, index, id, document, refresh=None):
        if self._fail:
            raise ConnectionError("boom")
        self.indexed.append((index, id, document))

    def search(self, index, **kwargs):
        if self._fail:
            raise ConnectionError("boom")
        return self._search_response

    def delete(self, index, id, refresh=None):
        self.deleted.append(id)


@pytest.fixture
def elastic_backend(monkeypatch):
    monkeypatch.setenv("ELASTIC_CLOUD_ID", "deployment:abc123")
    monkeypatch.setenv("ELASTIC_API_KEY", "key")
    from agent.memory.elastic_memory import ElasticMemoryBackend

    backend = ElasticMemoryBackend()
    backend._es = FakeES()
    return backend


def test_elastic_requires_credentials(monkeypatch):
    monkeypatch.delenv("ELASTIC_CLOUD_ID", raising=False)
    monkeypatch.delenv("ELASTIC_API_KEY", raising=False)
    from agent.memory.elastic_memory import ElasticMemoryBackend

    with pytest.raises(ValueError, match="ELASTIC_CLOUD_ID"):
        ElasticMemoryBackend()


def test_elastic_remember_actually_indexes(elastic_backend):
    entry = MemoryEntry(content="we use pgvector", category="fact", project="p")
    entry_id = asyncio.run(elastic_backend.remember(entry))

    assert entry_id.startswith("mem-")
    assert len(elastic_backend._es.indexed) == 1
    index, doc_id, doc = elastic_backend._es.indexed[0]
    assert doc_id == entry_id
    assert doc["content"] == "we use pgvector"
    assert doc["created_at"]  # timestamps set


def test_elastic_recall_maps_hits(elastic_backend):
    elastic_backend._es._search_response = {
        "hits": {
            "hits": [
                {
                    "_id": "mem-1",
                    "_score": 2.5,
                    "_source": {
                        "id": "mem-1",
                        "content": "pgvector for vector search",
                        "category": "decision",
                        "project": "p",
                        "confidence": 0.9,
                        "created_at": "2026-06-12T00:00:00+00:00",
                    },
                }
            ]
        }
    }
    results = asyncio.run(elastic_backend.recall("embeddings", project="p"))
    assert len(results) == 1
    assert results[0].entry.content == "pgvector for vector search"
    assert results[0].score == 2.5
    assert results[0].search_method in ("hybrid", "keyword")


def test_elastic_recall_empty_is_empty_not_error(elastic_backend):
    assert asyncio.run(elastic_backend.recall("nothing")) == []


def test_elastic_backend_failure_raises_not_empty(elastic_backend):
    elastic_backend._es._fail = True
    elastic_backend._semantic = True  # skip index bootstrap
    with pytest.raises(MemoryBackendError):
        asyncio.run(elastic_backend.recall("anything"))
    with pytest.raises(MemoryBackendError):
        asyncio.run(
            elastic_backend.remember(
                MemoryEntry(content="x", category="fact", project="p")
            )
        )


def test_elastic_health_check_never_raises(elastic_backend):
    elastic_backend._es._fail = True
    health = asyncio.run(elastic_backend.health_check())
    assert health["status"] == "error"
    assert "error" in health


# ── Engram demo path (real direct-SQLite backend, tmp database) ─────────────


def test_engram_demo_session_runs_end_to_end(monkeypatch, tmp_path):
    import agent.main as main_mod

    monkeypatch.setenv("ENGRAM_DB_PATH", str(tmp_path / "engram-demo.db"))
    # The demo prints; we only assert it completes without raising —
    # this is the exact path that crashed with TypeError before the
    # MemoryEntry id fix. The backend is the real one: stdlib sqlite3
    # against engram's facts schema, no binary required.
    asyncio.run(main_mod.demo_engram_session())


def test_engram_backend_roundtrip(monkeypatch, tmp_path):
    from agent.memory.engram_memory import EngramMemoryBackend

    monkeypatch.setenv("ENGRAM_DB_PATH", str(tmp_path / "engram-test.db"))
    backend = EngramMemoryBackend()

    eid = asyncio.run(backend.remember(MemoryEntry(
        content="pgvector handles vector search",
        category="fact", project="demo", tags=["vector-db"],
        confidence=0.9,
    )))
    results = asyncio.run(backend.recall("pgvector", project="demo"))
    assert len(results) == 1
    assert results[0].entry.id == eid
    assert results[0].entry.tags == ["vector-db"]

    assert asyncio.run(backend.forget(eid)) is True
    assert asyncio.run(backend.recall("pgvector", project="demo")) == []
