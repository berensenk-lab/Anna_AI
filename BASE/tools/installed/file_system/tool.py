# BASE/tools/installed/file_system/tool.py
"""
FileSystem Tool - File operations and system health monitoring
Converted from anna_filesystem_plugin.py to BaseTool architecture
"""

import os
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from BASE.handlers.base_tool import BaseTool

try:
    import psutil
except ImportError:
    psutil = None


class FileSystemTool(BaseTool):
    """File system operations and system health monitoring"""
    
    def __init__(self, config, controls, logger=None):
        super().__init__(config, controls, logger)
        self.tool_name = "file_system"
        
        # Configuration
        self.search_root = "C:/Users/beren"
        self.max_file_size = 100_000  # bytes
        self.allowed_extensions = {
            ".py", ".txt", ".md", ".json", ".yaml", ".yml",
            ".toml", ".cfg", ".ini", ".html", ".js", ".ts", ".bat"
        }
    
    
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
        """Initialize the file system tool"""
        self._thought_buffer = thought_buffer
        self._event_loop = event_loop
        
        # Verify psutil is available
        if psutil is None:
            self.logger.warning("[FileSystem] psutil not installed - health monitoring disabled")
        
        self.is_available = True
        self.logger.success("[FileSystem] Tool initialized")
    
    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """Execute file system commands"""
        
        if command == "get_system_health":
            return await self._get_system_health()
        
        elif command == "read_file":
            return await self._read_file(args[0] if args else "")
        
        elif command == "list_directory":
            return await self._list_directory(args[0] if args else "")
        
        elif command == "search_files":
            query = args[0] if args else ""
            root = args[1] if len(args) > 1 else self.search_root
            extension = args[2] if len(args) > 2 else ""
            return await self._search_files(query, root, extension)
        
        elif command == "scan_code":
            return await self._scan_code(args[0] if args else "")
        
        else:
            return {"success": False, "content": f"Unknown command: {command}"}
    
    async def end(self):
        """Cleanup"""
        self.is_available = False
    
    # ─────────────────────────────────────────────
    # IMPLEMENTATION
    # ─────────────────────────────────────────────
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        if psutil is None:
            return {
                "success": False,
                "content": "psutil not installed. Install with: pip install psutil"
            }
        
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            
            warnings = []
            if mem.percent > 85:
                warnings.append(f"⚠️ High RAM usage: {mem.percent:.1f}%")
            if disk.percent > 90:
                warnings.append(f"⚠️ Low disk space: only {disk.free / 1e9:.1f} GB free")
            if psutil.cpu_percent(interval=0.5) > 90:
                warnings.append("⚠️ High CPU usage detected")
            
            health_data = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_cores": len(cpu_per_core),
                "cpu_per_core": cpu_per_core,
                "ram_used_gb": round(mem.used / 1e9, 2),
                "ram_total_gb": round(mem.total / 1e9, 2),
                "ram_percent": mem.percent,
                "disk_used_gb": round(disk.used / 1e9, 2),
                "disk_total_gb": round(disk.total / 1e9, 2),
                "disk_free_gb": round(disk.free / 1e9, 2),
                "disk_percent": disk.percent,
                "warnings": warnings if warnings else ["✅ All systems look healthy"]
            }
            
            content = (
                f"**System Health Report:**\n"
                f"CPU: {health_data['cpu_percent']}% ({health_data['cpu_cores']} cores)\n"
                f"RAM: {health_data['ram_used_gb']}GB / {health_data['ram_total_gb']}GB ({health_data['ram_percent']}%)\n"
                f"Disk: {health_data['disk_used_gb']}GB / {health_data['disk_total_gb']}GB ({health_data['disk_percent']}%)\n"
                f"Status: {health_data['warnings'][0]}"
            )
            
            return {
                "success": True,
                "content": content,
                "data": health_data
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error getting system health: {str(e)}"}
    
    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents"""
        if not path:
            return {"success": False, "content": "No file path provided"}
        
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            return {"success": False, "content": f"File not found: {path}"}
        
        if not os.path.isfile(path):
            return {"success": False, "content": f"Not a file: {path}"}
        
        ext = os.path.splitext(path)[1].lower()
        if ext not in self.allowed_extensions:
            return {"success": False, "content": f"File type '{ext}' not allowed"}
        
        size = os.path.getsize(path)
        if size > self.max_file_size:
            return {
                "success": False,
                "content": f"File too large: {size} bytes (max: {self.max_file_size})"
            }
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            preview = content[:500] + "..." if len(content) > 500 else content
            
            return {
                "success": True,
                "content": preview,
                "full_content": content,
                "file": path,
                "size_bytes": size
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error reading file: {str(e)}"}
    
    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        if not path:
            path = self.search_root
        
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            return {"success": False, "content": f"Path not found: {path}"}
        
        if not os.path.isdir(path):
            return {"success": False, "content": f"Not a directory: {path}"}
        
        try:
            items = []
            for name in sorted(os.listdir(path)):
                if name.startswith('.'):
                    continue
                
                full_path = os.path.join(path, name)
                is_dir = os.path.isdir(full_path)
                size = os.path.getsize(full_path) if os.path.isfile(full_path) else None
                
                items.append({
                    "name": name,
                    "type": "📁 dir" if is_dir else "📄 file",
                    "size_bytes": size
                })
            
            content = f"📁 {path}\n"
            content += f"Items: {len(items)}\n"
            content += "\n".join(f"  {item['type']:12} {item['name']:40}" for item in items[:20])
            
            if len(items) > 20:
                content += f"\n  ... and {len(items) - 20} more items"
            
            return {
                "success": True,
                "content": content,
                "path": path,
                "item_count": len(items),
                "items": items
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error listing directory: {str(e)}"}
    
    async def _search_files(self, query: str, root: str = None, extension: str = "") -> Dict[str, Any]:
        """Search for files containing query string"""
        if not query:
            return {"success": False, "content": "No search query provided"}
        
        if root is None:
            root = self.search_root
        
        root = os.path.normpath(root)
        extension = extension.lower()
        matches = []
        files_scanned = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                # Skip system/hidden directories
                dirnames[:] = [
                    d for d in dirnames 
                    if not d.startswith((".", "__"))
                    and d not in ("node_modules", "__pycache__", "anaconda3", ".git", "venv")
                ]
                
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    
                    if extension and ext != extension:
                        continue
                    
                    if ext not in self.allowed_extensions:
                        continue
                    
                    filepath = os.path.join(dirpath, filename)
                    
                    try:
                        size = os.path.getsize(filepath)
                        if size > self.max_file_size:
                            continue
                        
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        files_scanned += 1
                        
                        if query.lower() in content.lower():
                            lines = content.splitlines()
                            matching_lines = [
                                f"Line {i+1}: {line.strip()[:100]}"
                                for i, line in enumerate(lines)
                                if query.lower() in line.lower()
                            ][:5]
                            
                            matches.append({
                                "file": filepath,
                                "matching_lines": matching_lines,
                                "line_count": len(matching_lines)
                            })
                    
                    except Exception:
                        continue
            
            content = (
                f"**Search Results**\n"
                f"Query: '{query}'\n"
                f"Files scanned: {files_scanned}\n"
                f"Matches found: {len(matches)}\n"
            )
            
            if matches:
                content += "\n**Matching files:**\n"
                for match in matches[:10]:
                    content += f"- {match['file']} ({match['line_count']} matches)\n"
            
            return {
                "success": True,
                "content": content,
                "query": query,
                "root": root,
                "files_scanned": files_scanned,
                "match_count": len(matches),
                "matches": matches[:20]
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error searching files: {str(e)}"}
    
    async def _scan_code(self, path: str) -> Dict[str, Any]:
        """Scan Python file for code issues"""
        if not path:
            return {"success": False, "content": "No file path provided"}
        
        # First read the file
        read_result = await self._read_file(path)
        if not read_result["success"]:
            return read_result
        
        content = read_result.get("full_content", "")
        lines = content.splitlines()
        issues = []
        
        checks = [
            ("TODO", "warning", "Unresolved TODO comment"),
            ("FIXME", "warning", "FIXME marker found"),
            ("HACK", "warning", "HACK marker found"),
            ("print(", "info", "Debug print statement (consider using logging)"),
            ("except:", "warning", "Bare except clause - catches all exceptions"),
            ("eval(", "warning", "Use of eval() - potential security risk"),
            ("exec(", "warning", "Use of exec() - potential security risk"),
            ("import *", "warning", "Wildcard import - namespace pollution"),
            ("password", "warning", "Possible hardcoded credential"),
            ("secret", "warning", "Possible hardcoded secret"),
            ("api_key", "warning", "Possible hardcoded API key"),
        ]
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip comments
            if stripped.startswith("#"):
                continue
            
            for keyword, severity, message in checks:
                if keyword.lower() in line.lower():
                    issues.append({
                        "line": i + 1,
                        "severity": severity,
                        "message": message,
                        "code": stripped[:120]
                    })
        
        stats = {
            "total_lines": len(lines),
            "blank_lines": sum(1 for l in lines if not l.strip()),
            "comment_lines": sum(1 for l in lines if l.strip().startswith("#")),
            "functions": sum(1 for l in lines if l.strip().startswith("def ")),
            "classes": sum(1 for l in lines if l.strip().startswith("class ")),
        }
        
        content = (
            f"**Code Scan Report: {os.path.basename(path)}**\n"
            f"Total lines: {stats['total_lines']}\n"
            f"Functions: {stats['functions']}, Classes: {stats['classes']}\n"
            f"Issues found: {len(issues)}\n"
        )
        
        if issues:
            content += "\n**Issues:**\n"
            for issue in issues[:10]:
                content += f"- Line {issue['line']} [{issue['severity']}]: {issue['message']}\n"
        
        return {
            "success": True,
            "content": content,
            "path": path,
            "stats": stats,
            "issue_count": len(issues),
            "issues": issues
        }
