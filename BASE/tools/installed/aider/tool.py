# BASE/tools/installed/aider/tool.py
"""
Aider Tool - AI Code Assistant Integration
Converted from anna_aider_plugin.py to BaseTool architecture
"""

import os
import asyncio
import subprocess
from typing import Any, Dict, List, Optional

from BASE.handlers.base_tool import BaseTool


class AiderTool(BaseTool):
    """Aider AI Code Assistant for software development"""
    
    def __init__(self, config, controls, logger=None):
        super().__init__(config, controls, logger)
        self.tool_name = "aider"
        
        # Configuration
        self.search_root = "C:/Users/beren"
        self.aider_history = os.path.join(self.search_root, ".aider.chat.history.md")
        self.aider_model = os.getenv("AIDER_MODEL", "ollama/qwen2.5-coder:7b")
        self.aider_cmd = "aider"
        
        # Pending command state (awaiting user confirmation)
        self._pending_command: Dict[str, Any] = {}
    
    
    @property
    def name(self) -> str:
        return self.tool_name

    async def initialize(self) -> bool:
        return True

    async def cleanup(self):
        pass

    def is_available(self) -> bool:
        return self._running

    async def start(self, thought_buffer, event_loop):
        """Initialize the Aider tool"""
        self._thought_buffer = thought_buffer
        self._event_loop = event_loop
        
        # Verify Aider is installed
        try:
            result = await self._run_command([self.aider_cmd, "--version"], timeout=5)
            if result["success"]:
                version_line = result.get("stdout", "").split('\n')[0]
                if self._logger:
                    self._logger.success(f"[Aider] Found: {version_line}")
            else:
                if self._logger:
                    self._logger.warning(f"[Aider] Not found - install with: pip install aider-chat")
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[Aider] Could not verify installation: {e}")
        
        self.is_available = True
    
    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """Execute Aider commands"""
        
        if command == "propose_fix":
            file_path = args[0] if args else ""
            issue_desc = args[1] if len(args) > 1 else ""
            return await self._propose_fix(file_path, issue_desc)
        
        elif command == "propose_feature":
            file_paths = args[0] if args else []
            feature_desc = args[1] if len(args) > 1 else ""
            return await self._propose_feature(file_paths, feature_desc)
        
        elif command == "propose_fix_from_scan":
            scan_results = args[0] if args else {}
            return await self._propose_fix_from_scan(scan_results)
        
        elif command == "confirm_and_run":
            return await self._confirm_and_run()
        
        elif command == "cancel_pending":
            return await self._cancel_pending()
        
        elif command == "view_aider_history":
            lines = int(args[0]) if args else 100
            return await self._view_aider_history(lines)
        
        elif command == "get_pending_command":
            return await self._get_pending_command()
        
        else:
            return {"success": False, "content": f"Unknown command: {command}"}
    
    async def end(self):
        """Cleanup"""
        self._pending_command.clear()
        self.is_available = False
    
    # ─────────────────────────────────────────────
    # IMPLEMENTATION
    # ─────────────────────────────────────────────
    
    async def _propose_fix(self, file_path: str, issue_description: str) -> Dict[str, Any]:
        """Propose an Aider fix command"""
        if not file_path:
            return {"success": False, "content": "No file path provided"}
        
        file_path = os.path.normpath(file_path)
        
        if not os.path.exists(file_path):
            return {"success": False, "content": f"File not found: {file_path}"}
        
        cmd = [
            self.aider_cmd,
            "--model", self.aider_model,
            "--yes-always",
            "--no-auto-commits",
            file_path,
            "--message", issue_description
        ]
        
        command_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
        
        self._pending_command = {
            "type": "fix",
            "file": file_path,
            "description": issue_description,
            "command": cmd,
            "command_str": command_str,
            "cwd": os.path.dirname(file_path)
        }
        
        content = (
            f"**Proposed Aider Fix**\n\n"
            f"File: `{os.path.basename(file_path)}`\n"
            f"Issue: {issue_description}\n\n"
            f"Command:\n```\n{command_str}\n```\n\n"
            f"📝 Type **confirm** to run, or **cancel** to skip."
        )
        
        return {
            "success": True,
            "content": content,
            "status": "awaiting_confirmation",
            "pending": True
        }
    
    async def _propose_feature(self, file_paths: List[str], feature_description: str) -> Dict[str, Any]:
        """Propose an Aider feature implementation"""
        if not file_paths:
            return {"success": False, "content": "No files provided"}
        
        # Normalize paths and verify they exist
        normalized = []
        for p in file_paths:
            p = os.path.normpath(p)
            if not os.path.exists(p):
                return {"success": False, "content": f"File not found: {p}"}
            normalized.append(p)
        
        cmd = [
            self.aider_cmd,
            "--model", self.aider_model,
            "--yes-always",
            "--no-auto-commits",
            *normalized,
            "--message", feature_description
        ]
        
        command_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
        
        self._pending_command = {
            "type": "feature",
            "files": normalized,
            "description": feature_description,
            "command": cmd,
            "command_str": command_str,
            "cwd": os.path.dirname(normalized[0]) if normalized else self.search_root
        }
        
        files_display = "\n".join(f"- `{os.path.basename(f)}`" for f in normalized)
        
        content = (
            f"**Proposed Aider Feature**\n\n"
            f"Feature: {feature_description}\n\n"
            f"Files:\n{files_display}\n\n"
            f"Command:\n```\n{command_str}\n```\n\n"
            f"📝 Type **confirm** to run, or **cancel** to skip."
        )
        
        return {
            "success": True,
            "content": content,
            "status": "awaiting_confirmation",
            "pending": True
        }
    
    async def _propose_fix_from_scan(self, scan_results: Dict) -> Dict[str, Any]:
        """Propose fix from scan_code results"""
        if "error" in scan_results:
            return {"success": False, "content": f"Scan error: {scan_results['error']}"}
        
        path = scan_results.get("path")
        issues = scan_results.get("issues", [])
        
        if not path:
            return {"success": False, "content": "Scan results missing file path"}
        
        if not issues:
            return {"success": True, "content": "No issues found in scan — nothing to fix!"}
        
        # Build issue summary
        issue_lines = []
        for issue in issues[:10]:
            line_num = issue.get("line", "?")
            severity = issue.get("severity", "info")
            message = issue.get("message", "Unknown issue")
            issue_lines.append(f"Line {line_num} [{severity}]: {message}")
        
        issue_summary = "\n".join(issue_lines)
        description = f"Please fix these code issues:\n{issue_summary}"
        
        return await self._propose_fix(path, description)
    
    async def _confirm_and_run(self) -> Dict[str, Any]:
        """Run the pending Aider command"""
        if not self._pending_command:
            return {"success": False, "content": "No pending Aider command to confirm"}
        
        cmd = self._pending_command.get("command")
        cwd = self._pending_command.get("cwd", self.search_root)
        cmd_str = self._pending_command.get("command_str", "")
        
        try:
            if self._logger:
                self._logger.tool(f"[Aider] Executing: {cmd_str}")
            
            result = await self._run_command(cmd, cwd=cwd, timeout=300)
            
            self._pending_command.clear()
            
            if result["success"]:
                stdout = result.get("stdout", "")
                preview = stdout[:500] + "..." if len(stdout) > 500 else stdout
                
                content = (
                    f"✅ **Aider completed successfully**\n\n"
                    f"Output:\n```\n{preview}\n```"
                )
                
                return {
                    "success": True,
                    "content": content,
                    "return_code": result.get("return_code", 0)
                }
            else:
                stderr = result.get("stderr", "Unknown error")
                content = (
                    f"⚠️ **Aider exited with error**\n\n"
                    f"Error:\n```\n{stderr[:500]}\n```"
                )
                
                return {
                    "success": False,
                    "content": content,
                    "return_code": result.get("return_code", 1)
                }
        
        except asyncio.TimeoutError:
            self._pending_command.clear()
            return {
                "success": False,
                "content": "❌ Aider timed out after 5 minutes"
            }
        except Exception as e:
            self._pending_command.clear()
            return {
                "success": False,
                "content": f"❌ Error running Aider: {str(e)}"
            }
    
    async def _cancel_pending(self) -> Dict[str, Any]:
        """Cancel the pending command"""
        if not self._pending_command:
            return {"success": True, "content": "No pending command to cancel"}
        
        desc = self._pending_command.get("description", "command")
        self._pending_command.clear()
        
        return {
            "success": True,
            "content": f"Cancelled: {desc}"
        }
    
    async def _view_aider_history(self, lines: int = 100) -> Dict[str, Any]:
        """View Aider chat history"""
        if not os.path.exists(self.aider_history):
            return {
                "success": False,
                "content": f"History not found: {self.aider_history}"
            }
        
        try:
            with open(self.aider_history, "r", encoding="utf-8", errors="ignore") as f:
                content = f.readlines()
            
            recent = "".join(content[-lines:])
            preview = recent[:1000] + "..." if len(recent) > 1000 else recent
            
            return {
                "success": True,
                "content": f"**Recent Aider History** ({len(content)} total lines)\n\n```\n{preview}\n```",
                "total_lines": len(content),
                "showing_lines": min(lines, len(content))
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error reading history: {str(e)}"}
    
    async def _get_pending_command(self) -> Dict[str, Any]:
        """Get the current pending command"""
        if not self._pending_command:
            return {
                "success": True,
                "content": "No pending Aider command",
                "pending": False
            }
        
        cmd_type = self._pending_command.get("type", "unknown")
        description = self._pending_command.get("description", "")
        command_str = self._pending_command.get("command_str", "")
        
        content = (
            f"**Pending {cmd_type.capitalize()} Command**\n\n"
            f"Description: {description}\n\n"
            f"Command:\n```\n{command_str}\n```"
        )
        
        return {
            "success": True,
            "content": content,
            "pending": True,
            "type": cmd_type
        }
    
    # ─────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────
    
    async def _run_command(
        self,
        cmd: List[str],
        cwd: str = None,
        timeout: float = 30
    ) -> Dict[str, Any]:
        """Run a shell command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.search_root
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore"),
                "return_code": process.returncode
            }
        
        except FileNotFoundError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command not found: {cmd[0]}",
                "return_code": 127
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "return_code": 124
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": 1
            }
