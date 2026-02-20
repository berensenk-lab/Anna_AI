# Filename: BASE/tools/installed/memory_notes/tool.py
"""
Memory & Notes Tool - Persistent memory across sessions
Anna remembers project details, preferences, todos and context.
Memory is auto-injected into thought buffer on startup so Anna
walks into each session already knowing relevant context.
"""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from BASE.handlers.base_tool import BaseTool

MAX_MEMORIES      = 500
INJECT_ON_STARTUP = True   # Inject recent memories into thought buffer at start


class MemoryStore:
    def __init__(self, path: Path):
        self.path  = path
        self._data = {"memories": [], "next_id": 1}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {"memories": [], "next_id": 1}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def add(self, content: str, topic: str = "general", tags: list = []) -> dict:
        if len(self._data["memories"]) >= MAX_MEMORIES:
            self._data["memories"].sort(key=lambda m: (m["access_count"], m["created_at"]))
            self._data["memories"].pop(0)
        memory = {
            "id":            self._data["next_id"],
            "content":       content,
            "topic":         topic.lower().strip(),
            "tags":          [t.lower().strip() for t in tags],
            "created_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_accessed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "access_count":  0
        }
        self._data["memories"].append(memory)
        self._data["next_id"] += 1
        self._save()
        return memory

    def search(self, query: str = "", topic: str = "", tag: str = "", limit: int = 10) -> list:
        results = self._data["memories"]
        if topic:
            results = [m for m in results if m["topic"] == topic.lower()]
        if tag:
            results = [m for m in results if tag.lower() in m["tags"]]
        if query:
            q = query.lower()
            results = [m for m in results if q in m["content"].lower()]
        results = sorted(results, key=lambda m: (m["access_count"], m["last_accessed"]), reverse=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ids = {m["id"] for m in results[:limit]}
        for m in self._data["memories"]:
            if m["id"] in ids:
                m["last_accessed"] = now
                m["access_count"] += 1
        self._save()
        return results[:limit]

    def forget(self, memory_id: int) -> bool:
        before = len(self._data["memories"])
        self._data["memories"] = [m for m in self._data["memories"] if m["id"] != memory_id]
        self._save()
        return len(self._data["memories"]) < before

    def forget_topic(self, topic: str) -> int:
        before = len(self._data["memories"])
        self._data["memories"] = [m for m in self._data["memories"] if m["topic"] != topic.lower()]
        removed = before - len(self._data["memories"])
        self._save()
        return removed

    def update(self, memory_id: int, content: str) -> bool:
        for m in self._data["memories"]:
            if m["id"] == memory_id:
                m["content"]       = content
                m["last_accessed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return True
        return False

    def get_all(self, limit: int = 50) -> list:
        return sorted(self._data["memories"],
                      key=lambda m: m["last_accessed"], reverse=True)[:limit]

    def get_topics(self) -> list:
        counts = {}
        for m in self._data["memories"]:
            counts[m["topic"]] = counts.get(m["topic"], 0) + 1
        return [{"topic": t, "count": c} for t, c in sorted(counts.items())]

    def stats(self) -> dict:
        mems = self._data["memories"]
        return {
            "total":  len(mems),
            "max":    MAX_MEMORIES,
            "topics": len(self.get_topics()),
            "oldest": mems[0]["created_at"] if mems else None,
            "newest": mems[-1]["created_at"] if mems else None,
        }


class MemoryNotesTool(BaseTool):

    __slots__ = ('_store',)

    @property
    def name(self) -> str:
        return "memory_notes"

    def has_context_loop(self) -> bool:
        return True

    async def initialize(self) -> bool:
        if hasattr(self._config, "project_root"):
            store_path = Path(self._config.project_root) / "BASE/tools/installed/memory_notes/memory_store.json"
        else:
            store_path = Path("BASE/tools/installed/memory_notes/memory_store.json")

        self._store = MemoryStore(store_path)
        stats = self._store.stats()

        if self._logger:
            self._logger.success(
                f"[Memory] Loaded {stats['total']} memories across {stats['topics']} topic(s) ✓"
            )
        return True

    async def cleanup(self):
        if self._logger:
            self._logger.system("[Memory] Cleaned up")

    def is_available(self) -> bool:
        return hasattr(self, "_store") and self._store is not None

    # ── Context loop — inject memory context on startup ───────────────────────

    async def context_loop(self, thought_buffer):
        if self._logger:
            self._logger.system("[Memory] Context loop started")

        if INJECT_ON_STARTUP:
            await asyncio.sleep(3)   # Let other tools initialise first
            context = self._build_context()
            if context:
                thought_buffer.add_processed_thought(
                    content=f"[MEMORY CONTEXT] Here is what I remember about you and your projects:\n\n{context}",
                    source="memory_notes"
                )
                if self._logger:
                    self._logger.system("[Memory] Injected startup context into thought buffer")

        # Keep running but no periodic work needed — memory is stored persistently
        while self._running:
            await asyncio.sleep(60)

    def _build_context(self) -> str:
        recent = self._store.get_all(limit=30)
        if not recent:
            return ""
        by_topic: dict = {}
        for m in recent:
            by_topic.setdefault(m["topic"], []).append(m["content"])
        lines = []
        for topic, contents in by_topic.items():
            lines.append(f"[{topic.upper()}]")
            for c in contents[:5]:
                lines.append(f"  - {c}")
        return "\n".join(lines)

    # ── execute ───────────────────────────────────────────────────────────────

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:

        if command == "remember":
            content = str(args[0]) if args else ""
            topic   = str(args[1]) if len(args) > 1 else "general"
            tags    = list(args[2]) if len(args) > 2 and isinstance(args[2], list) else []
            if not content:
                return self._error_result("No content provided.")
            memory = self._store.add(content, topic, tags)
            return self._success_result(
                f"Remembered: \"{content[:80]}{'...' if len(content) > 80 else ''}\"",
                metadata={"memory_id": memory["id"], "topic": memory["topic"]}
            )

        elif command == "recall":
            query = str(args[0]) if args else ""
            topic = str(args[1]) if len(args) > 1 else ""
            tag   = str(args[2]) if len(args) > 2 else ""
            limit = int(args[3]) if len(args) > 3 else 10
            results = self._store.search(query=query, topic=topic, tag=tag, limit=limit)
            return self._success_result(
                f"Found {len(results)} memory(s)." if results else "No relevant memories found.",
                metadata={"memories": results, "count": len(results)}
            )

        elif command == "forget":
            memory_id = int(args[0]) if args and str(args[0]).isdigit() else 0
            topic     = str(args[0]) if args and not str(args[0]).isdigit() else ""
            if memory_id:
                ok = self._store.forget(memory_id)
                return (
                    self._success_result(f"Memory {memory_id} forgotten.")
                    if ok else
                    self._error_result(f"Memory {memory_id} not found.")
                )
            elif topic:
                removed = self._store.forget_topic(topic)
                return self._success_result(f"Forgot {removed} memory(s) on topic '{topic}'.")
            return self._error_result("Provide memory_id or topic.")

        elif command == "update":
            memory_id   = int(args[0]) if args else 0
            new_content = str(args[1]) if len(args) > 1 else ""
            if not memory_id or not new_content:
                return self._error_result("Provide memory_id and new content.")
            ok = self._store.update(memory_id, new_content)
            return (
                self._success_result(f"Memory {memory_id} updated.")
                if ok else
                self._error_result(f"Memory {memory_id} not found.")
            )

        elif command == "list_topics":
            topics = self._store.get_topics()
            return self._success_result(
                f"{len(topics)} topic(s) in memory.",
                metadata={"topics": topics}
            )

        elif command == "get_stats":
            return self._success_result(
                "Memory stats retrieved.",
                metadata=self._store.stats()
            )

        elif command == "get_recent":
            limit   = int(args[0]) if args else 20
            recent  = self._store.get_all(limit=limit)
            return self._success_result(
                f"{len(recent)} recent memory(s).",
                metadata={"memories": recent}
            )

        elif command == "get_context":
            context = self._build_context()
            return self._success_result(
                "Context built." if context else "No memories stored yet.",
                metadata={"context": context}
            )

        else:
            return self._error_result(
                f"Unknown command: {command}",
                guidance="Commands: remember, recall, forget, update, list_topics, get_stats, get_recent, get_context"
            )
