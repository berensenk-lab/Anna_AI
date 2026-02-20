# Filename: BASE/tools/installed/dependency_auditor/tool.py
"""
Dependency Auditor Tool - Python and Node.js dependency auditing
Checks for outdated packages, vulnerabilities, version conflicts,
and missing/unused imports across all projects.
"""
import os
import re
import json
import subprocess
import urllib.request
from typing import List, Dict, Any
from collections import defaultdict
from BASE.handlers.base_tool import BaseTool

SEARCH_ROOT = "C:/Users/beren"
SKIP_DIRS   = {"anaconda3", "node_modules", "__pycache__", ".git", "venv", "AppData", ".conda"}
MAX_PROJECTS = 40


class DependencyAuditorTool(BaseTool):

    @property
    def name(self) -> str:
        return "dependency_auditor"

    def has_context_loop(self) -> bool:
        return False

    async def initialize(self) -> bool:
        if self._logger:
            self._logger.success("[DependencyAuditor] Ready ✓")
        return True

    async def cleanup(self):
        if self._logger:
            self._logger.system("[DependencyAuditor] Cleaned up")

    def is_available(self) -> bool:
        return True

    # ── Discovery ─────────────────────────────────────────────────────────────

    def _discover_projects(self) -> list:
        projects = []
        for dirpath, dirnames, filenames in os.walk(SEARCH_ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            dep_files = []
            for fn in ("requirements.txt", "setup.py", "pyproject.toml"):
                if fn in filenames:
                    dep_files.append(os.path.join(dirpath, fn))
            if "package.json" in filenames and "node_modules" not in dirpath:
                dep_files.append(os.path.join(dirpath, "package.json"))
            if dep_files:
                has_py  = any(f.endswith((".txt", ".toml", "setup.py")) for f in dep_files)
                has_npm = any(f.endswith("package.json") for f in dep_files)
                projects.append({
                    "name":      os.path.basename(dirpath),
                    "path":      dirpath,
                    "dep_files": dep_files,
                    "type":      ("python+node" if has_py and has_npm else "node" if has_npm else "python")
                })
                if len(projects) >= MAX_PROJECTS:
                    break
        return projects

    def _parse_requirements(self, path: str) -> list:
        packages = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = re.split(r";|#", line.strip())[0].strip()
                    if not line or line.startswith("-"):
                        continue
                    m = re.match(r"^([A-Za-z0-9_.\-]+)\s*([><=!~^,\s\d.*]*)?", line)
                    if m and m.group(1):
                        packages.append({"name": m.group(1).strip(), "spec": (m.group(2) or "").strip()})
        except Exception:
            pass
        return packages

    def _get_latest_pypi_version(self, name: str) -> str:
        try:
            with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=5) as r:
                return json.loads(r.read())["info"]["version"]
        except Exception:
            return ""

    # ── execute ───────────────────────────────────────────────────────────────

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:

        if command == "list_projects":
            projects = self._discover_projects()
            return self._success_result(
                f"{len(projects)} project(s) found.",
                metadata={"projects": [{"name": p["name"], "path": p["path"], "type": p["type"]} for p in projects]}
            )

        elif command == "check_outdated":
            project_path = str(args[0]) if args else ""
            check_all    = bool(args[1]) if len(args) > 1 else not project_path
            projects = self._discover_projects() if check_all else [{"path": project_path, "name": os.path.basename(project_path), "dep_files": [os.path.join(project_path, "requirements.txt")]}]
            outdated = []
            for proj in [p for p in projects if "python" in p.get("type", "python")]:
                for req_file in [f for f in proj.get("dep_files", []) if f.endswith(".txt")]:
                    if not os.path.exists(req_file):
                        continue
                    for pkg in self._parse_requirements(req_file)[:20]:
                        latest = self._get_latest_pypi_version(pkg["name"])
                        if not latest:
                            continue
                        pinned_m = re.search(r"==\s*([\d.]+)", pkg["spec"])
                        pinned   = pinned_m.group(1) if pinned_m else ""
                        if pinned and pinned != latest:
                            outdated.append({"project": proj["name"], "package": pkg["name"], "pinned": pinned, "latest": latest})
            return self._success_result(
                f"{len(outdated)} outdated package(s) found." if outdated else "All packages appear up to date.",
                metadata={"outdated": outdated}
            )

        elif command == "check_vulnerabilities":
            project_path = str(args[0]) if args else ""
            try:
                req = os.path.join(project_path, "requirements.txt") if project_path else ""
                cmd = (["pip-audit", "-r", req, "--format", "json"] if req and os.path.exists(req)
                       else ["pip-audit", "--format", "json"])
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                data   = json.loads(result.stdout)
                vulns  = []
                for dep in data.get("dependencies", []):
                    for v in dep.get("vulns", []):
                        vulns.append({"package": dep.get("name"), "version": dep.get("version"),
                                      "vuln_id": v.get("id"), "description": v.get("description", "")[:150]})
                return self._success_result(
                    f"{len(vulns)} vulnerability(s) found." if vulns else "No known vulnerabilities found.",
                    metadata={"vulnerabilities": vulns}
                )
            except FileNotFoundError:
                return self._error_result("pip-audit not found.", guidance="Run: pip install pip-audit")
            except Exception as e:
                return self._error_result(str(e))

        elif command == "check_conflicts":
            projects  = self._discover_projects()
            pkg_map   = defaultdict(dict)
            for proj in projects:
                for req_file in [f for f in proj.get("dep_files", []) if f.endswith(".txt")]:
                    for pkg in self._parse_requirements(req_file):
                        m = re.search(r"==\s*([\d.]+)", pkg["spec"])
                        if m:
                            pkg_map[pkg["name"].lower()][proj["name"]] = m.group(1)
            conflicts = [
                {"package": name, "versions": versions}
                for name, versions in pkg_map.items()
                if len(set(versions.values())) > 1
            ]
            return self._success_result(
                f"{len(conflicts)} version conflict(s) found." if conflicts else "No version conflicts found.",
                metadata={"conflicts": conflicts}
            )

        elif command == "check_missing":
            project_path = str(args[0]) if args else ""
            if not os.path.exists(project_path):
                return self._error_result(f"Path not found: {project_path}")
            imported = set()
            for dirpath, dirnames, filenames in os.walk(project_path):
                dirnames[:] = [d for d in dirnames if d not in {"__pycache__", "venv"}]
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    try:
                        with open(os.path.join(dirpath, fn), "r", encoding="utf-8", errors="ignore") as f:
                            for m in re.finditer(r"^(?:import|from)\s+([A-Za-z0-9_]+)", f.read(), re.MULTILINE):
                                imported.add(m.group(1).lower())
                    except Exception:
                        continue
            req_file = os.path.join(project_path, "requirements.txt")
            declared = set()
            if os.path.exists(req_file):
                for pkg in self._parse_requirements(req_file):
                    declared.add(pkg["name"].lower().replace("-", "_"))
            stdlib = {"os","sys","re","json","time","datetime","threading","subprocess",
                      "collections","pathlib","io","math","random","typing","abc","copy",
                      "functools","itertools","logging","unittest","argparse","hashlib",
                      "base64","urllib","http","socket","enum","dataclasses","contextlib"}
            third_party = imported - stdlib
            return self._success_result(
                f"{len(third_party - declared)} possibly missing, {len(declared - third_party)} possibly unused.",
                metadata={"possibly_missing": sorted(third_party - declared),
                           "possibly_unused":  sorted(declared - third_party)}
            )

        elif command == "audit_npm":
            project_path = str(args[0]) if args else ""
            paths = ([project_path] if project_path else
                     [p["path"] for p in self._discover_projects() if "node" in p.get("type", "")])
            results = []
            for path in paths:
                if not os.path.exists(os.path.join(path, "package.json")):
                    continue
                try:
                    r = subprocess.run(["npm", "audit", "--json"], cwd=path, capture_output=True, text=True, timeout=60)
                    data  = json.loads(r.stdout)
                    vulns = data.get("metadata", {}).get("vulnerabilities", {})
                    total = sum(vulns.values()) if isinstance(vulns, dict) else 0
                    results.append({"project": os.path.basename(path), "vulnerabilities": vulns, "total": total})
                except Exception as e:
                    results.append({"project": os.path.basename(path), "error": str(e)})
            return self._success_result(f"npm audit complete for {len(results)} project(s).", metadata={"results": results})

        elif command == "full_audit":
            project_path = str(args[0]) if args else ""
            results = {}
            results["outdated"]        = (await self.execute("check_outdated", [project_path] if project_path else []))["metadata"]
            results["vulnerabilities"] = (await self.execute("check_vulnerabilities", [project_path] if project_path else []))["metadata"]
            results["conflicts"]       = (await self.execute("check_conflicts", []))["metadata"]
            issues = []
            if results["outdated"].get("outdated"):
                issues.append(f"{len(results['outdated']['outdated'])} outdated package(s)")
            if results["vulnerabilities"].get("vulnerabilities"):
                issues.append(f"{len(results['vulnerabilities']['vulnerabilities'])} vulnerability(s)")
            if results["conflicts"].get("conflicts"):
                issues.append(f"{len(results['conflicts']['conflicts'])} version conflict(s)")
            summary = f"Audit complete: {', '.join(issues)}." if issues else "Audit complete: all clear."
            return self._success_result(summary, metadata=results)

        else:
            return self._error_result(
                f"Unknown command: {command}",
                guidance="Commands: list_projects, check_outdated, check_vulnerabilities, check_conflicts, check_missing, audit_npm, full_audit"
            )
