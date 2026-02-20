# BASE/tools/installed/docker/tool.py
"""
Docker Tool - Container monitoring and management
Converted from anna_docker_plugin.py to BaseTool architecture
"""

import os
import asyncio
import threading
import time
from typing import Any, Dict, List, Optional

from BASE.handlers.base_tool import BaseTool

try:
    import docker
except ImportError:
    docker = None


class DockerTool(BaseTool):
    """Docker container monitoring and management"""
    
    def __init__(self, config, controls, logger=None):
        super().__init__(config, controls, logger)
        self.tool_name = "docker"
        
        # Configuration
        self.monitor_interval = 30  # seconds between health checks
        self.log_lines = 50
        
        # Monitor state
        self._monitor = None
        self._monitor_thread = None
        self._last_states = {}
    
    
    @property
    def name(self) -> str:
        return self.tool_name

    async def initialize(self) -> bool:
        return True

    async def cleanup(self):
        pass

    def is_available(self) -> bool:
        return self._running

    async def start(self, thought_buffer=None, event_loop=None):
        """Initialize the Docker tool"""
        self._thought_buffer = thought_buffer
        self._event_loop = event_loop
        
        # Verify Docker is available
        if docker is None:
            if self._logger:
                self._logger.warning("[Docker] docker package not installed - tool disabled")
            self.is_available = False
            return
        
        try:
            client = docker.from_env()
            client.ping()
            if self._logger:
                self._logger.success("[Docker] Docker Desktop is running ✓")
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[Docker] Cannot connect to Docker: {e}")
            self.is_available = False
            return
        
        # Start background monitor
        self._start_monitor()
        self.is_available = True
    
    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """Execute Docker commands"""
        
        if command == "list_containers":
            all_containers = args[0] if args else False
            return await self._list_containers(all_containers)
        
        elif command == "get_container_logs":
            container_name = args[0] if args else ""
            lines = int(args[1]) if len(args) > 1 else self.log_lines
            return await self._get_container_logs(container_name, lines)
        
        elif command == "get_container_health":
            container_name = args[0] if args else ""
            return await self._get_container_health(container_name)
        
        elif command == "restart_container":
            container_name = args[0] if args else ""
            return await self._restart_container(container_name)
        
        else:
            return {"success": False, "content": f"Unknown command: {command}"}
    
    async def end(self):
        """Cleanup"""
        self._stop_monitor()
        self.is_available = False
    
    # ─────────────────────────────────────────────
    # IMPLEMENTATION
    # ─────────────────────────────────────────────
    
    def _get_client(self) -> Optional[Any]:
        """Get Docker client or return None"""
        if docker is None:
            return None
        
        try:
            client = docker.from_env()
            client.ping()
            return client
        except Exception:
            return None
    
    async def _list_containers(self, all_containers: bool = False) -> Dict[str, Any]:
        """List Docker containers"""
        client = self._get_client()
        if not client:
            return {
                "success": False,
                "content": "Cannot connect to Docker. Is Docker Desktop running?"
            }
        
        try:
            containers = client.containers.list(all=all_containers)
            result = []
            
            for c in containers:
                result.append({
                    "name": c.name,
                    "id": c.short_id,
                    "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                    "status": c.status,
                    "health": c.attrs.get("State", {}).get("Health", {}).get("Status", "none"),
                    "ports": list(c.ports.keys()) if c.ports else []
                })
            
            content = (
                f"**Docker Containers** ({len(result)} total)\n\n"
                + "\n".join(
                    f"- {c['name']:30} {c['status']:15} {c['image']}"
                    for c in result
                )
            )
            
            return {
                "success": True,
                "content": content,
                "container_count": len(result),
                "containers": result
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error listing containers: {str(e)}"}
    
    async def _get_container_logs(self, container_name: str, lines: int = None) -> Dict[str, Any]:
        """Get container logs"""
        if not container_name:
            return {"success": False, "content": "No container name provided"}
        
        if lines is None:
            lines = self.log_lines
        
        client = self._get_client()
        if not client:
            return {
                "success": False,
                "content": "Cannot connect to Docker. Is Docker Desktop running?"
            }
        
        try:
            container = client.containers.get(container_name)
        except Exception:
            return {"success": False, "content": f"Container '{container_name}' not found"}
        
        try:
            logs = container.logs(tail=lines, timestamps=True).decode("utf-8", errors="ignore")
            preview = logs[:1000] + "..." if len(logs) > 1000 else logs
            
            return {
                "success": True,
                "content": f"**Logs for {container_name}** (last {lines} lines)\n\n```\n{preview}\n```",
                "container": container_name,
                "status": container.status,
                "full_logs": logs
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error reading logs: {str(e)}"}
    
    async def _get_container_health(self, container_name: str) -> Dict[str, Any]:
        """Get container health details"""
        if not container_name:
            return {"success": False, "content": "No container name provided"}
        
        client = self._get_client()
        if not client:
            return {
                "success": False,
                "content": "Cannot connect to Docker. Is Docker Desktop running?"
            }
        
        try:
            container = client.containers.get(container_name)
        except Exception:
            return {"success": False, "content": f"Container '{container_name}' not found"}
        
        try:
            attrs = container.attrs
            state = attrs.get("State", {})
            health = state.get("Health", {})
            
            # Resource usage (non-streaming)
            try:
                stats = container.stats(stream=False)
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                           stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                              stats["precpu_stats"]["system_cpu_usage"]
                num_cpus = stats["cpu_stats"].get("online_cpus", 1)
                cpu_percent = (cpu_delta / system_delta) * num_cpus * 100 if system_delta > 0 else 0
                
                mem_usage = stats["memory_stats"].get("usage", 0)
                mem_limit = stats["memory_stats"].get("limit", 1)
                mem_percent = (mem_usage / mem_limit) * 100
            except:
                cpu_percent = mem_percent = mem_usage = None
            
            # Last health check
            health_log = health.get("Log", [])
            last_check = {}
            if health_log:
                last = health_log[-1]
                last_check = {
                    "exit_code": last.get("ExitCode"),
                    "output": last.get("Output", "").strip()[:200]
                }
            
            content = (
                f"**Container Health: {container_name}**\n\n"
                f"Status: {container.status}\n"
                f"Health: {health.get('Status', 'none')}\n"
                f"Running: {state.get('Running', False)}\n"
            )
            
            if cpu_percent is not None:
                content += f"CPU: {cpu_percent:.1f}%\n"
                content += f"RAM: {mem_percent:.1f}% ({mem_usage / 1e6:.1f}MB)\n"
            
            if last_check:
                content += f"\nLast health check: Exit code {last_check['exit_code']}\n"
                if last_check['output']:
                    content += f"Output: {last_check['output']}\n"
            
            return {
                "success": True,
                "content": content,
                "container": container_name,
                "status": container.status,
                "health": health.get("Status", "none"),
                "running": state.get("Running", False),
                "cpu_percent": round(cpu_percent, 2) if cpu_percent is not None else None,
                "ram_percent": round(mem_percent, 2) if mem_percent is not None else None
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error getting health: {str(e)}"}
    
    async def _restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a Docker container"""
        if not container_name:
            return {"success": False, "content": "No container name provided"}
        
        client = self._get_client()
        if not client:
            return {
                "success": False,
                "content": "Cannot connect to Docker. Is Docker Desktop running?"
            }
        
        try:
            container = client.containers.get(container_name)
        except Exception:
            return {"success": False, "content": f"Container '{container_name}' not found"}
        
        try:
            previous_status = container.status
            container.restart()
            container.reload()
            
            return {
                "success": True,
                "content": f"✅ Restarted '{container_name}': {previous_status} → {container.status}",
                "container": container_name,
                "previous_status": previous_status,
                "new_status": container.status
            }
        
        except Exception as e:
            return {"success": False, "content": f"Error restarting container: {str(e)}"}
    
    # ─────────────────────────────────────────────
    # BACKGROUND MONITOR
    # ─────────────────────────────────────────────
    
    def _start_monitor(self):
        """Start background container monitoring"""
        if self._monitor_thread is not None:
            return
        
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        if self._logger:
            self._logger.system("[Docker] Background monitor started")
    
    def _stop_monitor(self):
        """Stop background monitoring"""
        self._monitor_thread = None
        self._last_states.clear()
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitor_thread is not None:
            try:
                client = self._get_client()
                if not client:
                    time.sleep(self.monitor_interval)
                    continue
                
                containers = client.containers.list(all=True)
                
                for c in containers:
                    name = c.name
                    current_status = c.status
                    health = c.attrs.get("State", {}).get("Health", {}).get("Status", "none")
                    
                    previous = self._last_states.get(name)
                    
                    # Detect state transitions
                    if previous is not None and previous != current_status:
                        if current_status in ("exited", "dead", "removing"):
                            message = f"⚠️ Container '{name}' went DOWN ({previous} → {current_status})"
                            if self._logger:
                                self._logger.warning(f"[Docker Monitor] {message}")
                            
                            if self._thought_buffer:
                                self._thought_buffer.add_processed_thought(
                                    content=message,
                                    source="docker_alert"
                                )
                        
                        elif current_status == "running" and previous in ("exited", "dead"):
                            message = f"✅ Container '{name}' is back UP"
                            if self._logger:
                                self._logger.success(f"[Docker Monitor] {message}")
                    
                    # Check health
                    prev_health = self._last_states.get(f"{name}_health")
                    if health == "unhealthy" and prev_health != "unhealthy":
                        message = f"⚠️ Container '{name}' health check FAILED"
                        if self._logger:
                            self._logger.error(f"[Docker Monitor] {message}")
                        
                        if self._thought_buffer:
                            self._thought_buffer.add_processed_thought(
                                content=message,
                                source="docker_alert"
                            )
                    
                    self._last_states[name] = current_status
                    self._last_states[f"{name}_health"] = health
                
            except Exception as e:
                if self._logger:
                    self._logger.error(f"[Docker Monitor] Error: {e}")
            
            time.sleep(self.monitor_interval)
