from __future__ import annotations

import math
from marrowai.assistant import MarrowAssistant
from marrowai.memory import MemoryStore
from marrowai.planner import RuleBasedPlanner
from marrowai.tools import ManageMemoryTool, ToolRegistry
from marrowai.vector_db import EmbeddedVectorDB, SemanticEmbedder


def test_semantic_embedder_properties():
    embedder = SemanticEmbedder(dimension=256)
    vec1 = embedder.encode("Arch Linux operating system and kernel package management")
    vec2 = embedder.encode("Arch Linux pacman packages and rolling release distribution")
    vec3 = embedder.encode("Chocolate chip cookie baking recipe with butter and sugar")

    assert len(vec1) == 256
    assert len(vec2) == 256

    # Verify L2 normalization
    norm1 = math.sqrt(sum(x * x for x in vec1))
    assert abs(norm1 - 1.0) < 1e-4

    # Related sentences should have higher similarity than unrelated sentences
    sim_related = embedder.cosine_similarity(vec1, vec2)
    sim_unrelated = embedder.cosine_similarity(vec1, vec3)

    assert sim_related > 0.25
    assert sim_unrelated < 0.20
    assert sim_related > sim_unrelated


def test_embedded_vector_db_crud_and_knn(tmp_path):
    db_file = tmp_path / "test_vector.db"
    db = EmbeddedVectorDB(db_path=db_file)

    id1 = db.add("User prefers Arch Linux for development", category="preference")
    id2 = db.add("User's server runs Ubuntu 24.04 LTS", category="system")
    id3 = db.add("Database connection string uses PostgreSQL on port 5432", category="project")

    assert db.count() == 3
    assert db.count(category="preference") == 1

    # KNN Cosine Search
    results = db.search("Which Linux distribution do I like?", limit=2)
    assert len(results) >= 1
    assert results[0]["id"] == id1
    assert "Arch Linux" in results[0]["text"]
    assert results[0]["score"] > 0.2

    # Category filtered search
    sys_results = db.search("Ubuntu server", category="system")
    assert len(sys_results) == 1
    assert sys_results[0]["id"] == id2

    # Persistence verification (reopen same SQLite database file)
    db2 = EmbeddedVectorDB(db_path=db_file)
    assert db2.count() == 3
    reloaded = db2.search("PostgreSQL database port", limit=1)
    assert len(reloaded) == 1
    assert "5432" in reloaded[0]["text"]

    # Deletion
    assert db.delete(id1) is True
    assert db.count() == 2
    assert db.delete_matching("PostgreSQL") == 1
    assert db.count() == 1


def test_memory_store_automatic_fact_extraction(tmp_path):
    store = MemoryStore(path=str(tmp_path / "memory.json"))

    # Extract user identity
    facts1 = store.extract_and_store_facts("Hello! My name is Tejas and I work as a systems engineer.")
    assert any("Tejas" in f for f in facts1)
    assert any("systems engineer" in f for f in facts1)
    assert store.get("name") == "Tejas"

    # Extract user preferences
    facts2 = store.extract_and_store_facts("I prefer Arch Linux over Ubuntu for my primary workstation.")
    assert any("Arch Linux" in f for f in facts2)

    # Extract hardware specs
    facts3 = store.extract_and_store_facts("My system has 32GB RAM and my GPU is RTX 4090.")
    assert any("32GB RAM" in f or "4090" in f for f in facts3)

    # Extract direct memory instructions
    facts4 = store.extract_and_store_facts("Remember that my internal web service runs on port 8080.")
    assert any("8080" in f for f in facts4)

    # Verify semantic search in MemoryStore finds extracted facts
    matches = store.search_memories("What hardware and RAM do I have?")
    assert len(matches) > 0
    assert any("RAM" in m["text"] for m in matches)


def test_memory_store_build_context_augments_prompt(tmp_path):
    store = MemoryStore(path=str(tmp_path / "memory.json"))
    store.extract_and_store_facts("My name is Tejas.")
    store.extract_and_store_facts("I prefer Arch Linux over Ubuntu.")
    store.extract_and_store_facts("My API backend runs on port 9000.")

    context = store.build_context("Which Linux OS should we install in our VM?")
    assert "Relevant long-term memories:" in context
    assert "Arch Linux" in context


def test_manage_memory_tool(tmp_path):
    store = MemoryStore(path=str(tmp_path / "memory.json"))
    tool = ManageMemoryTool(memory_store=store)

    # Store
    res_store = tool.execute({"action": "store", "text": "User likes dark mode UI theme", "category": "preference"})
    assert res_store.status == "success"
    assert "Saved to memory" in res_store.output

    # Search
    res_search = tool.execute({"action": "search", "query": "UI theme preference"})
    assert res_search.status == "success"
    assert "dark mode" in res_search.output

    # List
    res_list = tool.execute({"action": "list"})
    assert res_list.status == "success"
    assert "dark mode" in res_list.output

    # Forget
    res_forget = tool.execute({"action": "forget", "query": "dark mode"})
    assert res_forget.status == "success"
    assert "Removed 1 memory" in res_forget.output


def test_planner_and_assistant_conversational_memory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    planner = RuleBasedPlanner()

    # Planner maps memory intents
    p1 = planner.plan("Remember that I prefer Arch Linux for high performance")
    assert p1.intent == "remember_fact"
    assert p1.steps[0].tool_name == "manage_memory"

    p2 = planner.plan("What do you remember about me?")
    assert p2.intent == "recall_memories"
    assert p2.steps[0].tool_name == "manage_memory"

    p3 = planner.plan("Search memory for Arch Linux")
    assert p3.intent == "search_memory"

    p4 = planner.plan("Forget that I use port 8080")
    assert p4.intent == "forget_memory"

    # End-to-end assistant memory execution
    assistant = MarrowAssistant(
        model_provider=__import__("marrowai.model", fromlist=["OllamaProvider"]).OllamaProvider(
            base_url="http://127.0.0.1:1"
        ),
        memory_path=str(tmp_path / "memory.json"),
    )

    # 1. User tells assistant to remember
    res1 = assistant.process("Remember that I prefer Arch Linux for all my virtual machines")
    assert res1["status"] == "success"
    assert "Arch Linux" in res1["output"]

    # 2. User asks what assistant remembers
    res2 = assistant.process("What do you remember about me?")
    assert res2["status"] == "success"
    assert "Arch Linux" in res2["output"]
