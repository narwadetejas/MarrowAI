from __future__ import annotations

import datetime
import json
from pathlib import Path
import re
import time
from typing import Any

from .vector_db import EmbeddedVectorDB


class MemoryStore:
    """Long-term memory store combining JSON state, daily episodic context, and SQLite vector DB."""

    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or ".marrowai/memory.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

        # Colocated daily context directory
        self.daily_context_dir = self.path.parent / "daily_context"
        self.daily_context_dir.mkdir(parents=True, exist_ok=True)

        # Database path colocated with memory path
        db_name = f"{self.path.stem}_vector.db" if path else "vector_memory.db"
        self.db_path = self.path.parent / db_name
        self.vector_db = EmbeddedVectorDB(db_path=self.db_path)

    def _load(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {}

    def _save(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    def remember(self, key: str, value: Any) -> None:
        """Stores a key-value in JSON profile state and indexes it into the vector database."""
        data = self._load()
        data[key] = value
        self._save(data)

        # Also index in vector database for semantic recall
        fact_text = f"User profile: {key} is {value}"
        self.vector_db.add(
            text=fact_text,
            category="profile",
            metadata={"key": key, "value": str(value)},
        )

    def get(self, key: str, default: Any = None) -> Any:
        return self._load().get(key, default)

    def remember_fact(self, text: str, category: str = "general", metadata: dict[str, Any] | None = None) -> str:
        """Explicitly stores an arbitrary semantic memory in the vector database."""
        return self.vector_db.add(text=text, category=category, metadata=metadata or {})

    def search_memories(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.15,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Performs semantic similarity search across stored memories."""
        return self.vector_db.search(query=query, limit=limit, min_score=min_score, category=category)

    def get_all_memories(self, category: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Returns all stored memories in chronological order."""
        return self.vector_db.get_all(category=category, limit=limit)

    def forget(self, keyword: str) -> int:
        """Deletes memories containing the given keyword."""
        return self.vector_db.delete_matching(keyword)

    def count_memories(self, category: str | None = None) -> int:
        """Returns the total number of memories stored."""
        return self.vector_db.count(category=category)

    # ---------------------------------------------------------
    # Daily Context & Episodic Journal Tracking
    # ---------------------------------------------------------

    def get_today_str(self) -> str:
        """Returns today's date string (YYYY-MM-DD)."""
        return datetime.date.today().isoformat()

    def record_daily_turn(
        self,
        role: str,
        message: str,
        details: dict[str, Any] | None = None,
        date_str: str | None = None,
    ) -> None:
        """Records an interaction turn in today's persistent daily context journal."""
        today = date_str or self.get_today_str()
        file_path = self.daily_context_dir / f"{today}.json"

        day_data: dict[str, Any] = {"date": today, "turns": []}
        if file_path.exists():
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        day_data = loaded
            except Exception:
                pass

        turns = day_data.setdefault("turns", [])
        entry = {
            "turn_id": len(turns) + 1,
            "timestamp": time.time(),
            "time_str": time.strftime("%H:%M:%S", time.localtime()),
            "role": role,
            "message": message,
        }
        if details:
            entry["details"] = details

        turns.append(entry)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(day_data, f, indent=2)

        # Keep session history in memory.json for backward compatibility
        self.add_event(role, message)

        # Index turn into vector DB for cross-day semantic retrieval
        if len(message.strip()) > 10:
            self.vector_db.add(
                text=f"[{today} {role}] {message}",
                category="daily_context",
                metadata={"date": today, "role": role},
            )

    def get_daily_context(self, date_str: str | None = None) -> dict[str, Any]:
        """Loads and returns the structured context for the given date (default today)."""
        today = date_str or self.get_today_str()
        file_path = self.daily_context_dir / f"{today}.json"
        if file_path.exists():
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {"date": today, "turns": []}

    def review_day_context(self, date_str: str | None = None, max_turns: int = 50) -> str:
        """Returns a comprehensive, formatted review string of that day's dialogue and actions."""
        context = self.get_daily_context(date_str)
        today = context.get("date", self.get_today_str())
        turns = context.get("turns", [])
        if not turns:
            return f"Daily Context ({today}): No previous interactions recorded for this date."

        lines = [f"Daily Context Review for {today} ({len(turns)} total turns):"]
        for item in turns[-max_turns:]:
            t_str = item.get("time_str", "")
            r = item.get("role", "user").capitalize()
            msg = item.get("message", "").strip()
            # Collapse multi-line messages for compact context
            collapsed_msg = " ".join(msg.splitlines())
            if len(collapsed_msg) > 160:
                collapsed_msg = collapsed_msg[:160] + "..."
            lines.append(f"- [{t_str}] {r}: {collapsed_msg}")

            if item.get("details"):
                d = item["details"]
                if "intent" in d:
                    lines.append(f"    (Intent: {d['intent']})")
                if "status" in d:
                    lines.append(f"    (Status: {d['status']})")

        return "\n".join(lines)

    def list_available_days(self) -> list[str]:
        """Returns all recorded dates in chronological order."""
        if not self.daily_context_dir.exists():
            return []
        return sorted([f.stem for f in self.daily_context_dir.glob("*.json")])

    def add_event(self, role: str, message: str) -> None:
        """Records a conversation event in session history."""
        data = self._load()
        history = data.setdefault("history", [])
        history.append({"role": role, "message": message, "timestamp": time.time()})
        if len(history) > 100:
            history = history[-100:]
        data["history"] = history
        self._save(data)

    def extract_and_store_facts(self, user_input: str, assistant_output: str | None = None) -> list[str]:
        """Automatically extracts facts, preferences, identity, and system specs from conversation."""
        extracted: list[tuple[str, str, dict[str, Any]]] = []
        text = user_input.strip()
        lowered = text.lower()

        # 1. Name & Identity
        name_match = re.search(r"\bmy name is\s+([a-zA-Z0-9_\-]+(?:\s+[a-zA-Z0-9_\-]+)?)", text, re.IGNORECASE)
        if name_match:
            raw_name = name_match.group(1).strip(".,;!?")
            parts = raw_name.split()
            if len(parts) > 1 and parts[1].lower() in {"and", "who", "from", "the", "a", "i"}:
                name = parts[0]
            else:
                name = raw_name
            fact = f"User's name is {name}"
            extracted.append((fact, "identity", {"name": name}))
            self.remember("name", name)

        role_match = re.search(r"\bi (?:am|work as) an?\s+([a-zA-Z0-9_\-]+(?:\s+[a-zA-Z0-9_\-]+)?)", text, re.IGNORECASE)
        if role_match:
            role = role_match.group(1).strip(".,;!?")
            if not any(w in role.lower() for w in ["sure", "ready", "here", "waiting", "not", "a"]):
                fact = f"User role or profession is {role}"
                extracted.append((fact, "identity", {"role": role}))
                self.remember("role", role)

        # 2. Preferences
        pref_over_match = re.search(r"\bi prefer ([a-zA-Z0-9_\- ]+) over ([a-zA-Z0-9_\- ]+)", text, re.IGNORECASE)
        if pref_over_match:
            p1 = pref_over_match.group(1).strip()
            p2 = pref_over_match.group(2).strip(".,;!?")
            fact = f"User prefers {p1} over {p2}"
            extracted.append((fact, "preference", {"preference": p1, "alternative": p2}))
        else:
            pref_match = re.search(r"\bi prefer ([a-zA-Z0-9_\- ]+)", text, re.IGNORECASE)
            if pref_match:
                pref = pref_match.group(1).strip(".,;!?")
                fact = f"User preference: prefers {pref}"
                extracted.append((fact, "preference", {"preference": pref}))

        fav_match = re.search(r"\bmy favorite ([a-zA-Z0-9_\- ]+) is ([a-zA-Z0-9_\- ]+)", text, re.IGNORECASE)
        if fav_match:
            item = fav_match.group(1).strip()
            val = fav_match.group(2).strip(".,;!?")
            fact = f"User favorite {item} is {val}"
            extracted.append((fact, "preference", {"item": item, "value": val}))

        like_match = re.search(r"\bi (?:like|love) ([a-zA-Z0-9_\- ]+)", text, re.IGNORECASE)
        if like_match and not any(w in like_match.group(1).lower() for w in ["to", "you", "that", "this"]):
            liked = like_match.group(1).strip(".,;!?")
            fact = f"User likes {liked}"
            extracted.append((fact, "preference", {"likes": liked}))

        dislike_match = re.search(r"\bi (?:dislike|hate|don't like) ([a-zA-Z0-9_\- ]+)", text, re.IGNORECASE)
        if dislike_match:
            disliked = dislike_match.group(1).strip(".,;!?")
            fact = f"User dislikes {disliked}"
            extracted.append((fact, "preference", {"dislikes": disliked}))

        # 3. Direct Memory Instructions
        instruct_match = re.search(r"\b(?:remember that|remember|note that|keep in mind that) (.+)", text, re.IGNORECASE)
        if instruct_match:
            raw_fact = instruct_match.group(1).strip(".,;!?")
            fact = f"User instruction: {raw_fact}"
            extracted.append((fact, "instruction", {"raw": raw_fact}))

        # 4. System Specs & Hardware
        if any(w in lowered for w in ["my gpu is", "my graphics card is", "i have a gpu"]):
            extracted.append((f"User hardware info: {text}", "system", {"raw": text}))
        if any(w in lowered for w in ["my distro is", "my os is", "i use arch", "i use ubuntu", "i use debian"]):
            extracted.append((f"User operating system: {text}", "system", {"raw": text}))
        if re.search(r"\bi have \d+\s*(?:gb|tb)\s*ram", lowered):
            extracted.append((f"User memory capacity: {text}", "system", {"raw": text}))

        # 5. Project & Workflow
        if any(w in lowered for w in ["port is", "running on port", "my project is", "backend is"]):
            extracted.append((f"User project detail: {text}", "project", {"raw": text}))

        stored_facts: list[str] = []
        for fact_text, cat, meta in extracted:
            self.vector_db.add(text=fact_text, category=cat, metadata=meta)
            stored_facts.append(fact_text)

        # If user input contains a substantial conversational turn, index it
        if len(text) > 20 and not text.startswith(("/", "$", "run")):
            self.vector_db.add(
                text=f"User said: {text}",
                category="conversation",
                metadata={"role": "user", "input": text},
            )

        return stored_facts

    def build_context(self, user_input: str) -> str:
        """Constructs an augmented context prompt reviewing today's full context, profile, and semantic memories."""
        data = self._load()
        profile = data.get("profile", {})
        parts: list[str] = []

        # 1. User Profile & Preferences
        if profile:
            parts.append(f"User profile: {json.dumps(profile, sort_keys=True)}")

        # 2. Comprehensive Review of Today's Context
        today_review = self.review_day_context(max_turns=30)
        parts.append(today_review)

        # 3. Fallback: Recent Interaction History from memory.json if no daily turns
        if "No previous interactions" in today_review:
            history = data.get("history", [])
            recent = history[-6:]
            if recent:
                recent_lines = ["Recent interaction:"]
                for item in recent:
                    recent_lines.append(f"- {item['role']}: {item['message']}")
                parts.append("\n".join(recent_lines))

        # 4. Semantic Long-Term Memory Retrieval via Vector DB
        if user_input.strip():
            similar = self.vector_db.search(query=user_input, limit=4, min_score=0.18)
            if similar:
                mem_lines = ["Relevant long-term memories:"]
                for mem in similar:
                    cat = mem.get("category", "general")
                    score = mem.get("score", 0.0)
                    mem_lines.append(f"- [{cat} | score: {score:.2f}] {mem['text']}")
                parts.append("\n".join(mem_lines))

        # 5. Current Request
        if user_input:
            parts.append(f"Current request: {user_input}")

        return "\n\n".join(parts)

    def set_profile(self, profile: dict[str, Any]) -> None:
        """Updates profile and indexes fields into the vector database."""
        data = self._load()
        data["profile"] = profile
        self._save(data)

        for k, v in profile.items():
            self.vector_db.add(
                text=f"User profile fact: {k} is {v}",
                category="profile",
                metadata={"key": k, "value": str(v)},
            )
