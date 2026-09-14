from __future__ import annotations

from marrowai.memory import MemoryStore


def test_memory_store_can_remember_and_fetch_value(tmp_path):
    store = MemoryStore(path=str(tmp_path / "memory.json"))
    store.remember("name", "marrowai")

    assert store.get("name") == "marrowai"


def test_memory_store_tracks_history_and_context(tmp_path):
    store = MemoryStore(path=str(tmp_path / "memory.json"))
    store.add_event("user", "hello")
    store.add_event("assistant", "hello there")

    context = store.build_context("next task")
    assert "hello" in context
    assert "next task" in context
