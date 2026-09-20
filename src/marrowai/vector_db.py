from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import struct
import time
import uuid
from typing import Any

EMBEDDING_DIM = 256

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've",
    "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
    "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
    "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
}


class SemanticEmbedder:
    """Zero-dependency, offline semantic feature embedder producing 256-d normalized vectors."""

    def __init__(self, dimension: int = EMBEDDING_DIM) -> None:
        self.dimension = dimension

    def encode(self, text: str) -> list[float]:
        """Encodes text into a normalized 256-dimensional semantic dense vector."""
        vec = [0.0] * self.dimension
        if not text or not text.strip():
            return vec

        raw = text.lower().strip()
        # Clean punctuation for tokenization
        tokens = [t.strip(".,!?;:()[]\"'{}-_") for t in raw.split()]
        tokens = [t for t in tokens if t]

        features: list[tuple[str, float]] = []

        # 1. Word token features
        for t in tokens:
            if t in STOP_WORDS:
                features.append((f"w:{t}", 0.2))
            else:
                features.append((f"w:{t}", 8.0))
                if len(t) >= 4:
                    features.append((f"stem:{t[:4]}", 4.0))

            # 2. Subword character n-grams (4-grams for stem/morphology capture)
            if len(t) >= 4 and t not in STOP_WORDS:
                for i in range(len(t) - 3):
                    ngram = t[i : i + 4]
                    features.append((f"sub:{ngram}", 0.5))

        # 3. Bigram phrase features
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 not in STOP_WORDS or w2 not in STOP_WORDS:
                features.append((f"bi:{w1}_{w2}", 4.0))

        # 4. Hash projection into dense dimension
        for feat, weight in features:
            h_val = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
            idx = h_val % self.dimension
            sign = 1.0 if (h_val >> 8) & 1 else -1.0
            vec[idx] += sign * weight

        # 5. L2 Normalize vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            vec = [x / norm for x in vec]

        return vec

    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calculates cosine similarity between two normalized vectors."""
        if len(v1) != len(v2) or not v1:
            return 0.0
        return max(-1.0, min(1.0, sum(a * b for a, b in zip(v1, v2))))


class EmbeddedVectorDB:
    """Embedded SQLite vector database for long-term semantic memory."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            db_dir = Path(".marrowai")
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "vector_memory.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.embedder = SemanticEmbedder(dimension=EMBEDDING_DIM)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
            conn.commit()

    def add(
        self,
        text: str,
        category: str = "general",
        metadata: dict[str, Any] | None = None,
        memory_id: str | None = None,
    ) -> str:
        """Embeds and inserts a new memory record into the database."""
        text = text.strip()
        if not text:
            raise ValueError("Memory text cannot be empty.")

        mid = memory_id or str(uuid.uuid4())
        meta = metadata or {}
        now = time.time()

        vector = self.embedder.encode(text)
        blob = struct.pack(f"{len(vector)}f", *vector)
        meta_json = json.dumps(meta)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories (id, text, category, embedding, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (mid, text, category, blob, meta_json, now, now),
            )
            conn.commit()

        return mid

    def search(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.0,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Performs KNN cosine similarity search over stored memory vectors."""
        query = query.strip()
        if not query:
            return []

        q_vec = self.embedder.encode(query)

        with self._get_connection() as conn:
            if category:
                cursor = conn.execute(
                    "SELECT id, text, category, embedding, metadata, created_at FROM memories WHERE category = ?",
                    (category,),
                )
            else:
                cursor = conn.execute("SELECT id, text, category, embedding, metadata, created_at FROM memories")

            results: list[dict[str, Any]] = []
            for row in cursor:
                blob = row["embedding"]
                dim = len(blob) // 4
                if dim != EMBEDDING_DIM:
                    continue
                v = list(struct.unpack(f"{dim}f", blob))
                score = self.embedder.cosine_similarity(q_vec, v)
                if score >= min_score:
                    meta = json.loads(row["metadata"]) if row["metadata"] else {}
                    results.append(
                        {
                            "id": row["id"],
                            "text": row["text"],
                            "category": row["category"],
                            "score": round(score, 4),
                            "metadata": meta,
                            "created_at": row["created_at"],
                        }
                    )

        # Sort descending by similarity score
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]

    def get_all(self, category: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Returns stored memory records."""
        with self._get_connection() as conn:
            if category:
                cursor = conn.execute(
                    "SELECT id, text, category, metadata, created_at FROM memories WHERE category = ? ORDER BY created_at DESC LIMIT ?",
                    (category, limit),
                )
            else:
                cursor = conn.execute(
                    "SELECT id, text, category, metadata, created_at FROM memories ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                )

            records = []
            for row in cursor:
                meta = json.loads(row["metadata"]) if row["metadata"] else {}
                records.append(
                    {
                        "id": row["id"],
                        "text": row["text"],
                        "category": row["category"],
                        "metadata": meta,
                        "created_at": row["created_at"],
                    }
                )
            return records

    def delete(self, memory_id: str) -> bool:
        """Deletes a memory record by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def delete_matching(self, keyword: str) -> int:
        """Deletes memories containing the given text keyword."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE text LIKE ?", (f"%{keyword}%",))
            conn.commit()
            return cursor.rowcount

    def count(self, category: str | None = None) -> int:
        """Returns the total number of memories stored."""
        with self._get_connection() as conn:
            if category:
                cursor = conn.execute("SELECT COUNT(*) FROM memories WHERE category = ?", (category,))
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM memories")
            return cursor.fetchone()[0]

    def clear(self) -> None:
        """Clears all records in the vector database."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM memories")
            conn.commit()
