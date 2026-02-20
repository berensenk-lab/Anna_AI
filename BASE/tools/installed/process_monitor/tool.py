# Filename: BASE/tools/installed/process_monitor/tool.py
"""
Process Monitor Tool - System process monitoring and management
Lists processes, finds resource hogs, identifies port owners,
watches for crashes, and handles termination with confirmation.
"""
import asyncio
import time
import threading
from typing import List, Dict, Any
from datetime import datetime
from BASE.handlers.base_tool import BaseTool

try:
    import psutil
except ImportError:
    psutil = None

CPU_HOG_THRESHOLD = 50    # %
RAM_HOG_THRESHOLD = 500   # MB
WATCH_INTERVAL    = 30    # seconds

PROTECTED = {
    "system", "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "lsass.exe", "services.exe", "svchost.exe", "explorer.exe", "python.exe"
}


class ProcessMonitorTool(BaseTool):

    __slots__ = (
        '_watched_procs', '_watch_lock', '_pending_kill',
        '_thought_buffer_ref'
    )

    @property
    def name(self) -> str:
        return "process_monitor"

    def has_context_loop(self) -> bool:
        return True

    async def initialize(self) -> bool:
        if psutil is None:
            if self._logger:
                self._logger.warning("[ProcessMonitor] psutil not installed.")
            return False
        self._watched_procs    = {}   # name -> {"label": str, "last_seen": float}
        self._watch_lock       = asyncio.Lock()
        self._pending_kill     = {}
        self._thought_buffer_ref = None
        if self._logger:
            self._logger.success("[ProcessMonitor] Ready ✓")
        return True

    async def cleanup(self):
        async with self._watch_lock:
            self._watched_procs.clear()
        if self._logger:
            self._logger.system("[ProcessMonitor] Cleaned up")

    def is_available(self) -> bool:
        return psutil is not None

    # ── Context loop — watch for crashed processes ────────────────────────────

    async def context_loop(self, thought_buffer):
        self._thought_buffer_ref = thought_buffer
        if self._logger:
            self._logger.system("[ProcessMonitor] Context loop started")

        while self._running:
            try:
                async with self._watch_lock:
                    watched = dict(self._watched_procs)

                for name, info in watched.items():
                    running = self._is_running(name)
                    if running:
                        async with self._watch_lock:
                            if name in self._watched_procs:
                                self._watched_procs[name]["last_seen"] = time.time()
                    else:
                        last_seen = info.get("last_seen", 0)
                        if last_seen > 0:
                            label = info.get("label", name)
                            msg   = f"[ALERT] Process stopped: '{label}' is no longer running."
                            thought_buffer.add_processed_thought(content=msg, source="process_monitor")
                            if self._logger:
                                self._logger.warning(f"[ProcessMonitor] {msg}")
                            async with self._watch_lock:
                                if name in self._watched_procs:
                                    self._watched_procs[name]["last_seen"] = 0

                await asyncio.sleep(WATCH_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._logger:
                    self._logger.error(f"[ProcessMonitor] Context loop error: {e}")
                await asyncio.sleep(WATCH_INTERVAL)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _is_running(self, name: str) -> bool:
        name_lower = name.lower()
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower() == name_lower:
                    return True
            except Exception:
                continue
        return False

    def _proc_info(self, proc) -> dict:
        try:
            mem_mb = proc.memory_info().rss / 1e6
            return {
                "pid":    proc.pid,
                "name":   proc.name(),
                "cpu":    proc.cpu_percent(),
                "ram_mb": round(mem_mb, 1),
                "status": proc.status()
            }
        except Exception:
            return {}

    # ── execute ───────────────────────────────────────────────────────────────

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:

        if command == "list_processes":
            sort_by = str(args[0]) if args else "cpu"
            limit   = int(args[1]) if len(args) > 1 else 20
            procs   = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
                try:
                    mem_mb = proc.info["memory_info"].rss / 1e6 if proc.info["memory_info"] else 0
                    procs.append({"pid": proc.info["pid"], "name": proc.info["name"],
                                  "cpu": proc.info["cpu_percent"], "ram_mb": round(mem_mb, 1),
                                  "status": proc.info["status"]})
                except Exception:
                    continue
            key = "cpu" if sort_by == "cpu" else "ram_mb"
            procs.sort(key=lambda x: x.get(key, 0), reverse=True)
            return self._success_result(
                f"Top {limit} processes by {sort_by}.",
                metadata={"processes": procs[:limit], "total": len(procs)}
            )

        elif command == "find_hogs":
            hogs_cpu, hogs_ram = [], []
            psutil.cpu_percent(interval=None)
            time.sleep(1)
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                try:
                    cpu    = proc.cpu_percent(interval=None)
                    mem_mb = proc.info["memory_info"].rss / 1e6 if proc.info["memory_info"] else 0
                    if cpu > CPU_HOG_THRESHOLD:
                        hogs_cpu.append({"pid": proc.pid, "name": proc.name(), "cpu": cpu})
                    if mem_mb > RAM_HOG_THRESHOLD:
                        hogs_ram.append({"pid": proc.pid, "name": proc.name(), "ram_mb": round(mem_mb, 1)})
                except Exception:
                    continue
            summary = "No resource hogs detected."
            if hogs_cpu or hogs_ram:
                parts = []
                if hogs_cpu: parts.append(f"{len(hogs_cpu)} high-CPU process(es)")
                if hogs_ram: parts.append(f"{len(hogs_ram)} high-RAM process(es)")
                summary = f"Resource hogs found: {', '.join(parts)}."
            return self._success_result(summary, metadata={"cpu_hogs": hogs_cpu, "ram_hogs": hogs_ram})

        elif command == "find_by_port":
            port = int(args[0]) if args else 0
            if not port:
                return self._error_result("No port provided.")
            try:
                for conn in psutil.net_connections(kind="inet"):
                    if conn.laddr and conn.laddr.port == port and conn.pid:
                        proc = psutil.Process(conn.pid)
                        return self._success_result(
                            f"Port {port} is used by '{proc.name()}' (PID {conn.pid})",
                            metadata={"port": port, "pid": conn.pid, "name": proc.name(), "status": conn.status}
                        )
                return self._success_result(f"No process found on port {port}.")
            except Exception as e:
                return self._error_result(str(e))

        elif command == "find_by_name":
            query = str(args[0]).lower() if args else ""
            if not query:
                return self._error_result("No name provided.")
            matches = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
                try:
                    if query in proc.info["name"].lower():
                        mem_mb = proc.info["memory_info"].rss / 1e6 if proc.info["memory_info"] else 0
                        matches.append({"pid": proc.info["pid"], "name": proc.info["name"],
                                        "cpu": proc.info["cpu_percent"], "ram_mb": round(mem_mb, 1),
                                        "status": proc.info["status"]})
                except Exception:
                    continue
            return self._success_result(
                f"{len(matches)} process(es) matching '{query}'.",
                metadata={"matches": matches}
            )

        elif command == "propose_kill":
            pid  = int(args[0]) if args and str(args[0]).isdigit() else 0
            name = str(args[0]) if args and not str(args[0]).isdigit() else (str(args[1]) if len(args) > 1 else "")
            targets = []
            if pid:
                try:
                    proc = psutil.Process(pid)
                    targets = [{"pid": pid, "name": proc.name()}]
                except Exception:
                    return self._error_result(f"No process with PID {pid}.")
            elif name:
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        if name.lower() in proc.info["name"].lower():
                            targets.append({"pid": proc.info["pid"], "name": proc.info["name"]})
                    except Exception:
                        continue
                if not targets:
                    return self._error_result(f"No process found matching '{name}'.")
            else:
                return self._error_result("Provide a PID or process name.")

            protected = [t for t in targets if t["name"].lower() in PROTECTED]
            if protected:
                return self._error_result(f"Cannot kill protected process(es): {[p['name'] for p in protected]}")

            self._pending_kill = {"targets": targets}
            names = ", ".join(f"{t['name']} (PID {t['pid']})" for t in targets)
            return self._success_result(
                f"Ready to kill: {names}. Say 'confirm kill' to proceed or 'cancel kill' to abort.",
                metadata={"targets": targets, "awaiting_confirmation": True}
            )

        elif command == "confirm_kill":
            if not self._pending_kill:
                return self._error_result("No pending kill to confirm.")
            targets = self._pending_kill.get("targets", [])
            results = []
            for t in targets:
                try:
                    proc = psutil.Process(t["pid"])
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                        results.append({"pid": t["pid"], "name": t["name"], "status": "terminated"})
                    except psutil.TimeoutExpired:
                        proc.kill()
                        results.append({"pid": t["pid"], "name": t["name"], "status": "force-killed"})
                except psutil.NoSuchProcess:
                    results.append({"pid": t["pid"], "name": t["name"], "status": "already gone"})
                except Exception as e:
                    results.append({"pid": t["pid"], "name": t["name"], "status": f"failed: {e}"})
            self._pending_kill = {}
            return self._success_result("Kill complete.", metadata={"results": results})

        elif command == "cancel_kill":
            self._pending_kill = {}
            return self._success_result("Kill cancelled.")

        elif command == "watch_process":
            proc_name = str(args[0]) if args else ""
            label     = str(args[1]) if len(args) > 1 else proc_name
            if not proc_name:
                return self._error_result("No process name provided.")
            running = self._is_running(proc_name)
            async with self._watch_lock:
                self._watched_procs[proc_name.lower()] = {
                    "label":     label,
                    "last_seen": time.time() if running else 0,
                    "added_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            return self._success_result(
                f"Now watching '{label}'. Will alert if it stops.",
                metadata={"currently_running": running}
            )

        elif command == "unwatch_process":
            proc_name = str(args[0]).lower() if args else ""
            async with self._watch_lock:
                removed = self._watched_procs.pop(proc_name, None)
            return (
                self._success_result(f"Stopped watching '{proc_name}'.")
                if removed else
                self._error_result(f"Not watching '{proc_name}'.")
            )

        elif command == "list_watched":
            async with self._watch_lock:
                watched = dict(self._watched_procs)
            result = [
                {"name": name, "label": info["label"],
                 "running": self._is_running(name), "added_at": info["added_at"]}
                for name, info in watched.items()
            ]
            return self._success_result(f"Watching {len(result)} process(es).", metadata={"processes": result})

        elif command == "system_overview":
            cpu  = psutil.cpu_percent(interval=1)
            mem  = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")
            net  = psutil.net_io_counters()
            top  = []
            for proc in sorted(psutil.process_iter(["pid", "name", "cpu_percent"]),
                                key=lambda p: p.info.get("cpu_percent", 0) or 0, reverse=True)[:5]:
                try:
                    top.append({"name": proc.info["name"], "cpu": proc.info["cpu_percent"]})
                except Exception:
                    continue
            return self._success_result(
                f"CPU {cpu:.0f}%, RAM {mem.percent:.0f}%, Disk {disk.percent:.0f}%",
                metadata={
                    "cpu_percent": cpu, "ram_percent": mem.percent,
                    "ram_used_gb": round(mem.used / 1e9, 1), "ram_total_gb": round(mem.total / 1e9, 1),
                    "disk_percent": disk.percent, "disk_free_gb": round(disk.free / 1e9, 1),
                    "net_sent_mb": round(net.bytes_sent / 1e6, 1), "net_recv_mb": round(net.bytes_recv / 1e6, 1),
                    "top_cpu": top
                }
            )

        else:
            return self._error_result(
                f"Unknown command: {command}",
                guidance="Commands: list_processes, find_hogs, find_by_port, find_by_name, propose_kill, confirm_kill, cancel_kill, watch_process, unwatch_process, list_watched, system_overview"
            )
