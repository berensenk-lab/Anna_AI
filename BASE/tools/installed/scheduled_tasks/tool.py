# Filename: BASE/tools/installed/scheduled_tasks/tool.py
"""
Scheduled Tasks Tool - Background task scheduler
Runs tasks on a schedule and injects results into thought buffer.
Schedules persist in scheduled_tasks_config.json across restarts.
"""
import os
import json
import asyncio
import psutil
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from BASE.handlers.base_tool import BaseTool

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    HAS_APSCHEDULER = True
except ImportError:
    HAS_APSCHEDULER = False

CONFIG_PATH = "BASE/tools/installed/scheduled_tasks/scheduler_config.json"

DEFAULT_TASKS = [
    {
        "id":       "daily_health",
        "name":     "Daily System Health Report",
        "task_type":"builtin",
        "task_fn":  "system_health_report",
        "schedule": "cron",
        "hour":     9, "minute": 0,
        "enabled":  True,
    },
    {
        "id":       "morning_repos",
        "name":     "Morning Repo Scan",
        "task_type":"builtin",
        "task_fn":  "repo_scan",
        "schedule": "cron",
        "hour":     9, "minute": 15,
        "enabled":  True,
    },
    {
        "id":       "hourly_logs",
        "name":     "Hourly Log Summary",
        "task_type":"builtin",
        "task_fn":  "log_summary",
        "schedule": "interval",
        "hours":    1,
        "enabled":  True,
    },
]


class ScheduledTasksTool(BaseTool):

    __slots__ = ('_scheduler', '_config_path', '_thought_buffer', '_config_data')

    @property
    def name(self) -> str:
        return "scheduled_tasks"

    def has_context_loop(self) -> bool:
        return True

    async def initialize(self) -> bool:
        if not HAS_APSCHEDULER:
            if self._logger:
                self._logger.warning("[ScheduledTasks] APScheduler not installed — run: pip install APScheduler")
            return False

        self._thought_buffer = None
        self._config_path    = Path(self._config.project_root) / CONFIG_PATH if hasattr(self._config, 'project_root') else Path(CONFIG_PATH)
        self._config_data    = self._load_config()
        self._scheduler      = AsyncIOScheduler()
        self._scheduler.start()

        # Register all enabled tasks
        for task_id, task in self._config_data.get("tasks", {}).items():
            if task.get("enabled", True):
                self._register_task(task_id, task)

        if self._logger:
            self._logger.success(f"[ScheduledTasks] {len(self._config_data.get('tasks', {}))} task(s) loaded ✓")
        return True

    async def cleanup(self):
        if hasattr(self, '_scheduler') and self._scheduler:
            self._scheduler.shutdown(wait=False)
        if self._logger:
            self._logger.system("[ScheduledTasks] Cleaned up")

    def is_available(self) -> bool:
        return HAS_APSCHEDULER and hasattr(self, '_scheduler') and self._scheduler.running

    # ── Context loop ──────────────────────────────────────────────────────────

    async def context_loop(self, thought_buffer):
        self._thought_buffer = thought_buffer
        if self._logger:
            self._logger.system("[ScheduledTasks] Context loop started")
        while self._running:
            await asyncio.sleep(30)

    # ── Config persistence ────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        if self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        # First run — create defaults
        config = {"tasks": {t["id"]: t for t in DEFAULT_TASKS}}
        self._save_config(config)
        return config

    def _save_config(self, config: dict = None):
        data = config or self._config_data
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w") as f:
            json.dump(data, f, indent=2)

    # ── Task registration ─────────────────────────────────────────────────────

    def _register_task(self, task_id: str, task: dict) -> bool:
        try:
            try:
                self._scheduler.remove_job(task_id)
            except Exception:
                pass

            schedule = task.get("schedule", "cron")
            if schedule == "cron":
                trigger = CronTrigger(
                    hour=task.get("hour", 9),
                    minute=task.get("minute", 0),
                    day_of_week=task.get("day_of_week", "*")
                )
            else:
                trigger = IntervalTrigger(
                    hours=task.get("hours", 0),
                    minutes=task.get("minutes", 0),
                    seconds=task.get("seconds", 0)
                )

            task_fn  = task.get("task_fn", "")
            task_type= task.get("task_type", "builtin")
            task_name= task.get("name", task_id)

            if task_type == "builtin":
                fn = getattr(self, f"_task_{task_fn}", None)
                if not fn:
                    return False
                self._scheduler.add_job(fn, trigger, id=task_id, name=task_name, replace_existing=True)
            elif task_type == "custom":
                prompt = task.get("prompt", "")
                self._scheduler.add_job(
                    self._task_custom, trigger, id=task_id, name=task_name,
                    kwargs={"prompt": prompt, "task_name": task_name},
                    replace_existing=True
                )
            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"[ScheduledTasks] Failed to register {task_id}: {e}")
            return False

    # ── Built-in task functions ───────────────────────────────────────────────

    def _task_system_health_report(self):
        try:
            cpu  = psutil.cpu_percent(interval=2)
            mem  = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")
            issues = []
            if cpu > 85:        issues.append(f"CPU at {cpu:.0f}%")
            if mem.percent > 85: issues.append(f"RAM at {mem.percent:.0f}%")
            if disk.percent > 90:issues.append(f"Disk at {disk.percent:.0f}%")

            if issues:
                msg = f"[SCHEDULED] System health report: {', '.join(issues)} — attention needed."
            else:
                msg = f"[SCHEDULED] Morning system check: CPU {cpu:.0f}%, RAM {mem.percent:.0f}%, Disk {disk.percent:.0f}% — all good."

            if self._thought_buffer:
                self._thought_buffer.add_processed_thought(content=msg, source="scheduled_tasks")
        except Exception as e:
            if self._logger:
                self._logger.error(f"[ScheduledTasks] Health report failed: {e}")

    def _task_repo_scan(self):
        try:
            from git import Repo
            import os
            root   = "C:/Users/beren"
            skip   = {"anaconda3", "node_modules", "__pycache__", "venv"}
            issues = []
            for dirpath, dirnames, _ in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in skip]
                if ".git" in os.listdir(dirpath):
                    dirnames.clear()
                    try:
                        repo = Repo(dirpath)
                        if repo.is_dirty(untracked_files=True):
                            issues.append(os.path.basename(dirpath))
                    except Exception:
                        continue
            if issues:
                msg = f"[SCHEDULED] Morning repo scan: {len(issues)} repo(s) with uncommitted changes: {', '.join(issues[:3])}."
            else:
                msg = "[SCHEDULED] Morning repo scan: all git repos are clean."
            if self._thought_buffer:
                self._thought_buffer.add_processed_thought(content=msg, source="scheduled_tasks")
        except Exception as e:
            if self._logger:
                self._logger.error(f"[ScheduledTasks] Repo scan failed: {e}")

    def _task_log_summary(self):
        try:
            from BASE.tools.installed.log_watcher.tool import _global_instance
            if _global_instance:
                files  = list(_global_instance._watched.values())
                errors = sum(f.error_count for f in files)
                troubled = [f.label for f in files if f.error_count > 0]
                if troubled:
                    msg = f"[SCHEDULED] Log summary: {errors} error(s) across {', '.join(troubled[:3])}."
                else:
                    msg = f"[SCHEDULED] Log summary: {len(files)} file(s) watched — no errors."
            else:
                msg = "[SCHEDULED] Log summary: log watcher not active."
            if self._thought_buffer:
                self._thought_buffer.add_processed_thought(content=msg, source="scheduled_tasks")
        except Exception as e:
            if self._logger:
                self._logger.error(f"[ScheduledTasks] Log summary failed: {e}")

    def _task_custom(self, prompt: str = "", task_name: str = "Custom Task"):
        if self._thought_buffer:
            self._thought_buffer.add_processed_thought(
                content=f"[SCHEDULED] {task_name}: {prompt}",
                source="scheduled_tasks"
            )

    # ── execute ───────────────────────────────────────────────────────────────

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:

        if command == "list_tasks":
            jobs = {j.id: j for j in self._scheduler.get_jobs()}
            tasks = []
            for tid, task in self._config_data.get("tasks", {}).items():
                job      = jobs.get(tid)
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job and job.next_run_time else "N/A"
                tasks.append({
                    "id":       tid,
                    "name":     task.get("name", tid),
                    "enabled":  task.get("enabled", True),
                    "next_run": next_run
                })
            return self._success_result(f"{len(tasks)} task(s) scheduled.", metadata={"tasks": tasks})

        elif command == "add_task":
            name     = str(args[0]) if args else "Custom Task"
            schedule = str(args[1]) if len(args) > 1 else "cron"
            hour     = int(args[2]) if len(args) > 2 else 9
            minute   = int(args[3]) if len(args) > 3 else 0
            task_fn  = str(args[4]) if len(args) > 4 else ""
            prompt   = str(args[5]) if len(args) > 5 else ""
            task_id  = name.lower().replace(" ", "_")
            task_type= "builtin" if task_fn else "custom"
            task = {
                "name": name, "task_type": task_type, "task_fn": task_fn,
                "prompt": prompt, "schedule": schedule, "hour": hour,
                "minute": minute, "enabled": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._config_data.setdefault("tasks", {})[task_id] = task
            self._save_config()
            ok = self._register_task(task_id, task)
            return (
                self._success_result(f"Task '{name}' scheduled.")
                if ok else
                self._error_result(f"Failed to schedule '{name}'.")
            )

        elif command == "remove_task":
            task_id = str(args[0]) if args else ""
            try:
                self._scheduler.remove_job(task_id)
            except Exception:
                pass
            removed = self._config_data.get("tasks", {}).pop(task_id, None)
            self._save_config()
            return (
                self._success_result(f"Task '{task_id}' removed.")
                if removed else
                self._error_result(f"Task '{task_id}' not found.")
            )

        elif command == "run_now":
            task_id = str(args[0]) if args else ""
            task = self._config_data.get("tasks", {}).get(task_id)
            if not task:
                return self._error_result(f"Task '{task_id}' not found.")
            fn = getattr(self, f"_task_{task.get('task_fn', '')}", None)
            if fn:
                fn()
                return self._success_result(f"Task '{task_id}' executed.")
            return self._error_result(f"Cannot run task '{task_id}' manually.")

        elif command == "enable_task":
            task_id = str(args[0]) if args else ""
            enabled = bool(args[1]) if len(args) > 1 else True
            task = self._config_data.get("tasks", {}).get(task_id)
            if not task:
                return self._error_result(f"Task '{task_id}' not found.")
            task["enabled"] = enabled
            self._save_config()
            if enabled:
                self._register_task(task_id, task)
            else:
                try:
                    self._scheduler.remove_job(task_id)
                except Exception:
                    pass
            state = "enabled" if enabled else "disabled"
            return self._success_result(f"Task '{task_id}' {state}.")

        else:
            return self._error_result(
                f"Unknown command: {command}",
                guidance="Commands: list_tasks, add_task, remove_task, run_now, enable_task"
            )
