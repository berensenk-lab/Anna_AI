# Filename: BASE/tools/installed/log_watcher/tool.py
"""
Log Watcher Tool - Real-time log file monitoring
Watches .log files for errors, crashes, spam, and fast growth.
Alerts injected into thought buffer so Anna speaks them proactively.
"""
import os
import re
import asyncio
import time
from typing import List, Dict, Any
from collections import defaultdict, deque
from datetime import datetime
from BASE.handlers.base_tool import BaseTool

SEARCH_ROOT = "C:/Users/beren"
SKIP_DIRS   = {"anaconda3", "node_modules", "__pycache__", ".git", "venv", "AppData"}
ERROR_KEYWORDS = [
    "error", "exception", "traceback", "fatal", "critical",
    "failed", "failure", "crash", "killed", "segfault", "out of memory"
]
CRASH_PATTERNS = [
    r"exit\s*code\s*[1-9]\d*",
    r"returncode\s*[1-9]\d*",
    r"killed\s+by\s+signal",
    r"core\s+dumped",
]
SPAM_THRESHOLD   = 20
GROWTH_THRESHOLD = 10    # MB per minute
POLL_INTERVAL    = 5     # seconds
MAX_BUFFER       = 300   # lines per file


class WatchedFile:
    def __init__(self, path: str, label: str = ""):
        self.path        = path
        self.label       = label or os.path.basename(path)
        self.last_pos    = 0
        self.last_size   = 0
        self.line_buffer = deque(maxlen=MAX_BUFFER)
        self.line_counts = defaultdict(list)
        self.size_history= deque(maxlen=12)
        self.error_count = 0
        self.added_at    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "path":        self.path,
            "label":       self.label,
            "size_kb":     round(self.last_size / 1024, 1),
            "error_count": self.error_count,
            "lines":       len(self.line_buffer),
            "added_at":    self.added_at,
        }


class LogWatcherTool(BaseTool):

    __slots__ = ('_watched', '_watch_lock', '_pending_alerts')

    @property
    def name(self) -> str:
        return "log_watcher"

    def has_context_loop(self) -> bool:
        return True

    async def initialize(self) -> bool:
        self._watched       = {}
        self._watch_lock    = asyncio.Lock()
        self._pending_alerts= deque(maxlen=50)

        # Auto-discover log files
        found = self._discover_logs()
        for path in found:
            self._add_file_internal(path)

        if self._logger:
            self._logger.success(f"[LogWatcher] Watching {len(self._watched)} log file(s) ✓")
        return True

    async def cleanup(self):
        async with self._watch_lock:
            self._watched.clear()
        if self._logger:
            self._logger.system("[LogWatcher] Cleaned up")

    def is_available(self) -> bool:
        return True

    # ── Context loop ──────────────────────────────────────────────────────────

    async def context_loop(self, thought_buffer):
        if self._logger:
            self._logger.system("[LogWatcher] Context loop started")

        while self._running:
            try:
                async with self._watch_lock:
                    files = list(self._watched.values())

                for wf in files:
                    alerts = self._check_file(wf)
                    for alert in alerts:
                        thought_buffer.add_processed_thought(
                            content=alert,
                            source="log_watcher"
                        )
                        # Also route to notifications tool if available
                        self._try_notify(alert)

                await asyncio.sleep(POLL_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._logger:
                    self._logger.error(f"[LogWatcher] Context loop error: {e}")
                await asyncio.sleep(POLL_INTERVAL)

    def _try_notify(self, message: str):
        try:
            from BASE.tools.installed.notifications.tool import _global_instance
            if _global_instance:
                _global_instance.fire("Log Alert", message[:200], severity="warning",
                                      source="log_watcher", cooldown_key=f"log_{message[:50]}")
        except Exception:
            pass

    # ── File checking ─────────────────────────────────────────────────────────

    def _check_file(self, wf: WatchedFile) -> list:
        alerts = []
        if not os.path.exists(wf.path):
            return alerts

        current_size = os.path.getsize(wf.path)
        now = time.time()
        wf.size_history.append((now, current_size))

        # Growth check
        if len(wf.size_history) >= 2:
            oldest_time, oldest_size = wf.size_history[0]
            elapsed = (now - oldest_time) / 60
            if elapsed > 0.5:
                rate = (current_size - oldest_size) / 1e6 / elapsed
                if rate > GROWTH_THRESHOLD:
                    alerts.append(f"[LOG GROWTH] {wf.label} growing at {rate:.1f} MB/min — possible runaway logging.")

        if current_size <= wf.last_pos:
            wf.last_size = current_size
            return alerts

        # Read new lines
        try:
            with open(wf.path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(wf.last_pos)
                new_lines = f.readlines()
                wf.last_pos = f.tell()
        except Exception:
            return alerts

        wf.last_size = current_size

        for raw in new_lines:
            line = raw.rstrip()
            if not line:
                continue

            wf.line_buffer.append({"time": datetime.now().strftime("%H:%M:%S"), "text": line})
            line_lower = line.lower()

            # Error keyword check
            for kw in ERROR_KEYWORDS:
                if kw in line_lower:
                    wf.error_count += 1
                    severity = "CRITICAL" if kw in ("fatal", "critical", "crash") else "ERROR"
                    alerts.append(f"[{severity}] {wf.label}: {line[:200]}")
                    break

            # Crash pattern check
            for pattern in CRASH_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    alerts.append(f"[CRASH] {wf.label}: {line[:200]}")
                    break

            # Spam check
            key = re.sub(r"\d+", "N", line[:80])
            wf.line_counts[key].append(now)
            wf.line_counts[key] = [t for t in wf.line_counts[key] if now - t < 60]
            if len(wf.line_counts[key]) == SPAM_THRESHOLD:
                alerts.append(f"[LOG SPAM] {wf.label}: same line repeated {SPAM_THRESHOLD}x in 60s: {line[:100]}")

        return alerts

    # ── Discovery & file management ───────────────────────────────────────────

    def _discover_logs(self, max_files: int = 50) -> list:
        found = []
        for dirpath, dirnames, filenames in os.walk(SEARCH_ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fn in filenames:
                if fn.endswith(".log"):
                    found.append(os.path.join(dirpath, fn))
                    if len(found) >= max_files:
                        return found
        return found

    def _add_file_internal(self, path: str, label: str = "") -> bool:
        path = os.path.normpath(path)
        if not os.path.exists(path) or path in self._watched:
            return False
        wf = WatchedFile(path, label)
        try:
            wf.last_pos  = os.path.getsize(path)
            wf.last_size = wf.last_pos
        except Exception:
            pass
        self._watched[path] = wf
        return True

    # ── execute ───────────────────────────────────────────────────────────────

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:

        if command == "watch_file":
            path  = str(args[0]) if args else ""
            label = str(args[1]) if len(args) > 1 else ""
            if not path:
                return self._error_result("No path provided")
            async with self._watch_lock:
                ok = self._add_file_internal(path, label)
            return (
                self._success_result(f"Now watching: {path}")
                if ok else
                self._error_result(f"Could not add: {path}", guidance="Check the path exists")
            )

        elif command == "unwatch_file":
            path = os.path.normpath(str(args[0])) if args else ""
            async with self._watch_lock:
                removed = self._watched.pop(path, None)
            return (
                self._success_result(f"Stopped watching: {path}")
                if removed else
                self._error_result(f"Not watching: {path}")
            )

        elif command == "list_watched":
            async with self._watch_lock:
                files = [wf.to_dict() for wf in self._watched.values()]
            return self._success_result(
                f"Watching {len(files)} file(s).",
                metadata={"files": files}
            )

        elif command == "get_tail":
            path  = os.path.normpath(str(args[0])) if args else ""
            lines = int(args[1]) if len(args) > 1 else 50
            async with self._watch_lock:
                wf = self._watched.get(path)
            if wf:
                recent = list(wf.line_buffer)[-lines:]
            else:
                # Read directly
                if not os.path.exists(path):
                    return self._error_result(f"File not found: {path}")
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        all_lines = f.readlines()
                    recent = [{"time": "", "text": l.rstrip()} for l in all_lines[-lines:]]
                except Exception as e:
                    return self._error_result(str(e))
            content = "\n".join(e["text"] for e in recent)
            return self._success_result(content, metadata={"line_count": len(recent)})

        elif command == "search_log":
            path  = str(args[0]) if args else ""
            query = str(args[1]) if len(args) > 1 else ""
            if not path or not query:
                return self._error_result("Provide path and query")
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    all_lines = f.readlines()
                matches = [
                    {"line": i + 1, "text": l.rstrip()}
                    for i, l in enumerate(all_lines)
                    if query.lower() in l.lower()
                ]
                return self._success_result(
                    f"{len(matches)} match(es) for '{query}'",
                    metadata={"matches": matches[-100:]}
                )
            except Exception as e:
                return self._error_result(str(e))

        elif command == "discover":
            found = self._discover_logs()
            async with self._watch_lock:
                for f in found:
                    self._add_file_internal(f)
            return self._success_result(
                f"Discovered and added {len(found)} log file(s).",
                metadata={"files": found}
            )

        else:
            return self._error_result(
                f"Unknown command: {command}",
                guidance="Commands: watch_file, unwatch_file, list_watched, get_tail, search_log, discover"
            )


# Global instance reference for cross-tool access
_global_instance: LogWatcherTool = None
