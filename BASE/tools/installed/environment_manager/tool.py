# Filename: BASE/tools/installed/environment_manager/tool.py
"""
Environment Manager Tool - Python environment management
Discovers conda and venv environments, compares them, checks health,
and suggests the right environment for each project.
"""
import os
import json
import subprocess
from typing import List, Dict, Any
from BASE.handlers.base_tool import BaseTool

SEARCH_ROOT = "C:/Users/beren"
CONDA_BASE  = os.path.join(SEARCH_ROOT, "anaconda3")
SKIP_DIRS   = {"node_modules", "__pycache__", ".git", "AppData"}


class EnvironmentManagerTool(BaseTool):

    @property
    def name(self) -> str:
        return "environment_manager"

    def has_context_loop(self) -> bool:
        return False

    async def initialize(self) -> bool:
        if self._logger:
            self._logger.success("[EnvironmentManager] Ready ✓")
        return True

    async def cleanup(self):
        if self._logger:
            self._logger.system("[EnvironmentManager] Cleaned up")

    def is_available(self) -> bool:
        return True

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_conda_envs(self) -> list:
        conda_exe = os.path.join(CONDA_BASE, "Scripts", "conda.exe")
        if not os.path.exists(conda_exe):
            conda_exe = "conda"
        try:
            result = subprocess.run([conda_exe, "env", "list", "--json"],
                                    capture_output=True, text=True, timeout=30)
            data   = json.loads(result.stdout)
            envs   = []
            for path in data.get("envs", []):
                name       = os.path.basename(path)
                python_exe = os.path.join(path, "python.exe")
                if not os.path.exists(python_exe):
                    python_exe = os.path.join(path, "Scripts", "python.exe")
                envs.append({
                    "name":       "base" if name == "anaconda3" else name,
                    "path":       path,
                    "type":       "conda",
                    "python_exe": python_exe if os.path.exists(python_exe) else ""
                })
            return envs
        except Exception:
            return []

    def _find_venvs(self) -> list:
        venvs = []
        for dirpath, dirnames, filenames in os.walk(SEARCH_ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            if "pyvenv.cfg" in filenames:
                python_exe = os.path.join(dirpath, "Scripts", "python.exe")
                venvs.append({
                    "name":       os.path.basename(dirpath),
                    "path":       dirpath,
                    "type":       "venv",
                    "python_exe": python_exe if os.path.exists(python_exe) else ""
                })
                dirnames.clear()
        return venvs

    def _get_packages(self, python_exe: str) -> list:
        if not python_exe or not os.path.exists(python_exe):
            return []
        try:
            result = subprocess.run([python_exe, "-m", "pip", "list", "--format", "json"],
                                    capture_output=True, text=True, timeout=30)
            return json.loads(result.stdout)
        except Exception:
            return []

    def _pip_check(self, python_exe: str) -> str:
        if not python_exe or not os.path.exists(python_exe):
            return ""
        try:
            result = subprocess.run([python_exe, "-m", "pip", "check"],
                                    capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception:
            return ""

    # ── execute ───────────────────────────────────────────────────────────────

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:

        if command == "list_environments":
            conda = self._get_conda_envs()
            venvs = self._find_venvs()
            all_envs = conda + venvs
            return self._success_result(
                f"{len(all_envs)} environment(s) found ({len(conda)} conda, {len(venvs)} venv).",
                metadata={"environments": [{"name": e["name"], "type": e["type"], "path": e["path"],
                                            "has_python": bool(e["python_exe"])} for e in all_envs]}
            )

        elif command == "get_packages":
            env_name = str(args[0]) if args else ""
            all_envs = self._get_conda_envs() + self._find_venvs()
            env = next((e for e in all_envs if e["name"] == env_name), None)
            if not env:
                return self._error_result(f"Environment '{env_name}' not found.")
            pkgs = self._get_packages(env["python_exe"])
            return self._success_result(
                f"{len(pkgs)} packages in '{env_name}'.",
                metadata={"packages": pkgs, "count": len(pkgs)}
            )

        elif command == "compare_environments":
            name_a = str(args[0]) if args else ""
            name_b = str(args[1]) if len(args) > 1 else ""
            all_envs = self._get_conda_envs() + self._find_venvs()
            env_a = next((e for e in all_envs if e["name"] == name_a), None)
            env_b = next((e for e in all_envs if e["name"] == name_b), None)
            if not env_a:
                return self._error_result(f"Environment '{name_a}' not found.")
            if not env_b:
                return self._error_result(f"Environment '{name_b}' not found.")
            pkgs_a = {p["name"].lower(): p["version"] for p in self._get_packages(env_a["python_exe"])}
            pkgs_b = {p["name"].lower(): p["version"] for p in self._get_packages(env_b["python_exe"])}
            only_a   = {k: v for k, v in pkgs_a.items() if k not in pkgs_b}
            only_b   = {k: v for k, v in pkgs_b.items() if k not in pkgs_a}
            diff_ver = {k: {"in_a": pkgs_a[k], "in_b": pkgs_b[k]}
                        for k in pkgs_a if k in pkgs_b and pkgs_a[k] != pkgs_b[k]}
            return self._success_result(
                f"{len(only_a)} only in {name_a}, {len(only_b)} only in {name_b}, {len(diff_ver)} at different versions.",
                metadata={"only_in_a": only_a, "only_in_b": only_b, "version_differences": diff_ver}
            )

        elif command == "check_health":
            env_name = str(args[0]) if args else ""
            all_envs = self._get_conda_envs() + self._find_venvs()
            env = next((e for e in all_envs if e["name"] == env_name), None)
            if not env:
                return self._error_result(f"Environment '{env_name}' not found.")
            issues = self._pip_check(env["python_exe"])
            healthy = not issues or "No broken requirements" in issues
            return self._success_result(
                "Environment is healthy." if healthy else f"Issues found: {issues[:300]}",
                metadata={"healthy": healthy, "issues": issues}
            )

        elif command == "check_project_environment":
            project_path = str(args[0]) if args else ""
            if not os.path.exists(project_path):
                return self._error_result(f"Path not found: {project_path}")
            detected = []
            for venv_name in ["venv", ".venv", "env", ".env"]:
                venv_path = os.path.join(project_path, venv_name)
                if os.path.exists(os.path.join(venv_path, "Scripts", "activate")):
                    detected.append({"type": "venv", "path": venv_path, "name": venv_name})
            has_req = os.path.exists(os.path.join(project_path, "requirements.txt"))
            has_yml = os.path.exists(os.path.join(project_path, "environment.yml"))
            return self._success_result(
                f"{len(detected)} local environment(s) detected." if detected else "No local virtual environment detected.",
                metadata={"detected": detected, "has_requirements_txt": has_req, "has_environment_yml": has_yml}
            )

        elif command == "find_duplicates":
            all_envs = (self._get_conda_envs() + self._find_venvs())[:8]
            pkg_map  = {}
            for env in all_envs:
                if not env.get("python_exe") or not os.path.exists(env["python_exe"]):
                    continue
                for pkg in self._get_packages(env["python_exe"]):
                    name = pkg["name"].lower()
                    pkg_map.setdefault(name, {})[env["name"]] = pkg["version"]
            duplicates = {name: versions for name, versions in pkg_map.items()
                          if len(set(versions.values())) > 1}
            return self._success_result(
                f"{len(duplicates)} package(s) at different versions across environments.",
                metadata={"duplicates": duplicates, "environments_checked": len(all_envs)}
            )

        else:
            return self._error_result(
                f"Unknown command: {command}",
                guidance="Commands: list_environments, get_packages, compare_environments, check_health, check_project_environment, find_duplicates"
            )
