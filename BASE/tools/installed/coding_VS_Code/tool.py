# Filename: BASE/tools/installed/coding_VS_Code/tool.py
"""
Cursor Coding Tool - Simplified Architecture
Single master class with start() and end() lifecycle
Integrates with Cursor/VS Code extension via HTTP REST API
"""
import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from BASE.handlers.base_tool import BaseTool

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CodingTool(BaseTool):
    """
    Cursor integration for AI-powered code editing
    Communicates with editor extension via HTTP REST API
    """

    @property
    def name(self) -> str:
        return "coding"

    @staticmethod
    def _normalize_url(url: Optional[str]) -> Optional[str]:
        """Normalize and validate server URL values."""
        if not url:
            return None
        normalized = str(url).strip().rstrip('/')
        if not normalized:
            return None
        if not normalized.startswith(("http://", "https://")):
            normalized = f"http://{normalized}"
        return normalized

    def _set_server_url(self, url: str):
        """Set server URL and refresh endpoint paths."""
        self.server_url = url.rstrip('/')
        self.edit_endpoint = f"{self.server_url}/edit"
        self.file_endpoint = f"{self.server_url}/file"
        self.files_endpoint = f"{self.server_url}/files"

    def _build_candidate_urls(self, configured_urls: List[str]) -> List[str]:
        """Build ordered probe list for bridge auto-discovery."""
        candidates = []
        seen = set()

        def add(url: Optional[str]):
            normalized = self._normalize_url(url)
            if normalized and normalized not in seen:
                candidates.append(normalized)
                seen.add(normalized)

        # Prefer explicit config first, then common local bridge ports.
        for url in configured_urls:
            add(url)

        for port in (3000, 1337, 13331, 13333, 13344, 55000):
            add(f"http://127.0.0.1:{port}")

        return candidates

    def _probe_server_url(self, base_url: str) -> bool:
        """Check whether a given base URL exposes the expected /files endpoint."""
        try:
            response = requests.get(
                f"{base_url}/files",
                timeout=0.5,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            payload = response.json()
            return isinstance(payload, dict) and (
                'success' in payload or 'files' in payload or 'activeFile' in payload
            )
        except requests.exceptions.RequestException as e:
            self._last_availability_error = f"{base_url}/files -> {e}"
            return False
        except ValueError:
            self._last_availability_error = f"{base_url}/files -> non-JSON response"
            return False

    def _probe_for_server(self) -> bool:
        """Probe configured and fallback URLs, switching to the first reachable endpoint."""
        current_url = self._normalize_url(getattr(self, "server_url", None))
        if current_url and self._probe_server_url(current_url):
            return True

        for url in getattr(self, "_candidate_urls", []):
            if current_url and url == current_url:
                continue
            if self._probe_server_url(url):
                previous = current_url or "unset"
                self._set_server_url(url)
                if self._logger and previous != url:
                    self._logger.system(
                        f"[Coding] Auto-discovered bridge: {url} (previous: {previous})"
                    )
                return True

        return False

    async def initialize(self) -> bool:
        """
        Initialize coding system

        Returns:
            True if initialization successful (always returns True for graceful degradation)
        """
        # Server configuration
        self.editor_name = getattr(self._config, 'coding_editor_name', 'Cursor')
        configured_cursor_url = getattr(self._config, 'cursor_server_url', None)
        configured_vscode_url = getattr(self._config, 'vscode_server_url', 'http://localhost:3000')
        configured_urls = [configured_cursor_url, configured_vscode_url]
        self._candidate_urls = self._build_candidate_urls(configured_urls)
        self._set_server_url(self._candidate_urls[0] if self._candidate_urls else "http://localhost:3000")
        self.timeout = (
            getattr(self._config, 'cursor_timeout', None)
            or getattr(self._config, 'vscode_timeout', 30)
        )

        # Cache
        self._cached_files = None
        self._cache_time = 0
        self._availability_cache = None
        self._availability_checked_at = 0.0
        self._availability_ttl = 3.0
        self._last_availability_error = None

        # Check initial bridge connection
        available = self.is_bridge_available()

        if self._logger:
            if available:
                status = self._get_status_info()
                self._logger.system(
                    f"[Coding] {self.editor_name} extension ready: "
                    f"{status.get('open_files', 0)} files open, "
                    f"active: {status.get('active_file', 'none')}"
                )
            else:
                self._logger.warning(
                    f"[Coding] {self.editor_name} extension not available (server: {self.server_url})"
                )

        # Always return True for graceful degradation
        return True

    async def cleanup(self):
        """Cleanup coding resources"""
        self._cached_files = None

        if self._logger:
            self._logger.system("[Coding] Cleanup complete")

    def is_available(self) -> bool:
        """
        ToolManager-level availability.

        Important:
        - ToolManager gates execute() on is_available().
        - Bridge connectivity is handled separately in is_bridge_available()
          so commands like coding.status can still execute while offline.
        """
        return bool(getattr(self, "_running", False) and REQUESTS_AVAILABLE)

    def is_bridge_available(self, force_check: bool = False) -> bool:
        """
        Check if editor extension server is available
        Returns:
            True when the editor extension server is reachable
        """
        if not self.is_available():
            return False

        now = time.monotonic()
        if (
            not force_check and
            self._availability_cache is not None and
            (now - self._availability_checked_at) < self._availability_ttl
        ):
            return self._availability_cache

        self._availability_cache = self._probe_for_server()

        self._availability_checked_at = now
        return bool(self._availability_cache)

    def get_status(self) -> Dict[str, Any]:
        """
        Get editor extension status

        Returns:
            Status dictionary with connection info
        """
        return self._get_status_info()

    def _get_status_info(self) -> Dict[str, Any]:
        """Internal method to get status info"""
        status = {
            'tool_ready': self.is_available(),
            'available': self.is_bridge_available(),
            'requests_available': REQUESTS_AVAILABLE,
            'server_url': self.server_url,
            'candidate_urls': self._candidate_urls,
            'open_files': 0,
            'active_file': None,
            'last_error': self._last_availability_error
        }

        if status['available']:
            try:
                files_result = self._get_open_files()
                if files_result.get('success'):
                    status['open_files'] = len(files_result.get('files', []))
                    status['active_file'] = files_result.get('activeFile')
            except:
                pass

        return status

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """
        Execute coding command

        Commands:
        - edit: [instruction, optional_file_path, optional_selection]
        - fetch: [file_path, optional_start_line, optional_end_line]
        - verify: [file_path, optional_expected_changes]
        - files: [] - List open files
        - status: [] - Check connection

        Args:
            command: Command name
            args: Command arguments as defined in information.json

        Returns:
            Standardized result dict
        """
        if self._logger:
            self._logger.tool(f"[Coding] Command: '{command}', args: {args}")

        # Always allow status checks, even when extension is offline
        if command == 'status':
            return await self._handle_status()

        # Check availability
        if not self.is_bridge_available():
            return self._error_result(
                f'{self.editor_name} extension not available',
                metadata={
                    'server_url': self.server_url,
                    'requests_available': REQUESTS_AVAILABLE,
                    'last_error': self._last_availability_error
                },
                guidance=(
                    f'Open {self.editor_name} and start the extension HTTP server on '
                    f'{self.server_url}, then retry.'
                )
            )

        # Handle empty command (default to edit if instruction provided)
        if not command:
            if not args:
                return self._error_result(
                    'No command or arguments provided',
                    guidance='Use coding.edit, coding.fetch, coding.files, coding.verify, or coding.status'
                )
            command = 'edit'

        try:
            # Route to appropriate handler
            if command == 'edit':
                return await self._handle_edit(args)
            elif command == 'fetch':
                return await self._handle_fetch(args)
            elif command == 'verify':
                return await self._handle_verify(args)
            elif command == 'files':
                return await self._handle_files()
            else:
                return self._error_result(
                    f'Unknown command: {command}',
                    guidance='Available commands: edit, fetch, verify, files, status'
                )

        except Exception as e:
            if self._logger:
                self._logger.error(f"[Coding] Command error: {e}")
            import traceback
            traceback.print_exc()

            return self._error_result(
                f'Command execution failed: {str(e)}',
                metadata={'error': str(e)},
                guidance=f'Check {self.editor_name} extension and network connection'
            )

    async def _handle_edit(self, args: List[Any]) -> Dict[str, Any]:
        """Handle edit command: coding.edit with [instruction, optional_file, optional_selection]"""
        if not args:
            return self._error_result(
                'No instruction provided',
                guidance='Provide coding instruction: {"tool": "coding.edit", "args": ["add error handling"]}'
            )

        instruction = str(args[0])
        file_path = str(args[1]) if len(args) > 1 else None

        # Extract selection if provided (args[2] should be dict)
        selection = args[2] if len(args) > 2 and isinstance(args[2], dict) else None

        # Send edit instruction
        result = self._send_edit_instruction(instruction, file_path, selection)

        if result.get('success'):
            if self._logger:
                self._logger.success(f"[Coding] Edit instruction sent: {instruction[:50]}...")

            # Format the response
            message = result.get('message', f'Edit instruction sent to {self.editor_name}')

            return self._success_result(
                f'[OK] {message}',
                metadata={
                    'instruction': instruction,
                    'file': file_path,
                    'has_selection': selection is not None,
                    'result': result.get('result', {})
                }
            )
        else:
            error = result.get('error', 'Unknown error')
            if self._logger:
                self._logger.error(f"[Coding] Edit failed: {error}")

            return self._error_result(
                f'Edit failed: {error}',
                metadata={'error': error},
                guidance=f'Check {self.editor_name} extension status and file accessibility'
            )

    async def _handle_fetch(self, args: List[Any]) -> Dict[str, Any]:
        """Handle fetch command: coding.fetch with [file_path, optional_start, optional_end]"""
        if not args:
            return self._error_result(
                'No file path provided',
                guidance='Provide file path: {"tool": "coding.fetch", "args": ["main.py"]}'
            )

        file_path = str(args[0])

        # Add error handling for int conversion
        start_line = None
        end_line = None

        if len(args) > 1:
            try:
                start_line = int(args[1])
            except (ValueError, TypeError) as e:
                return self._error_result(
                    f'Invalid start_line value: {args[1]}',
                    metadata={'error': str(e)},
                    guidance='start_line must be an integer'
                )

        if len(args) > 2:
            try:
                end_line = int(args[2])
            except (ValueError, TypeError) as e:
                return self._error_result(
                    f'Invalid end_line value: {args[2]}',
                    metadata={'error': str(e)},
                    guidance='end_line must be an integer'
                )

        # Fetch file content
        result = self._fetch_file_content(file_path, start_line, end_line)

        if result.get('success'):
            content = result.get('content', '')
            line_count = result.get('lineCount', 0)
            is_open = result.get('isOpen', False)

            if self._logger:
                self._logger.success(
                    f"[Coding] Fetched {file_path}: {line_count} lines"
                )

            # Truncate content for display if too long
            content_preview = content[:500] + '...' if len(content) > 500 else content

            return self._success_result(
                f'File: {file_path}\nLines: {line_count}\nOpen: {is_open}\n\n{content_preview}',
                metadata={
                    'file': file_path,
                    'line_count': line_count,
                    'is_open': is_open,
                    'full_content': content,
                    'start_line': start_line,
                    'end_line': end_line
                }
            )
        else:
            error = result.get('error', 'Unknown error')
            if self._logger:
                self._logger.error(f"[Coding] Fetch failed: {error}")

            return self._error_result(
                f'Failed to fetch file: {error}',
                metadata={'file': file_path, 'error': error},
                guidance=f'Check file path and {self.editor_name} extension'
            )

    async def _handle_verify(self, args: List[Any]) -> Dict[str, Any]:
        """Handle verify command: coding.verify with [file_path, optional_expected_changes]"""
        if not args:
            return self._error_result(
                'No file path provided',
                guidance='Provide file path to verify'
            )

        file_path = str(args[0])
        expected_changes = str(args[1]) if len(args) > 1 else None

        # Fetch file content
        result = self._fetch_file_content(file_path)

        if not result.get('success'):
            return self._error_result(
                f'Failed to verify: {result.get("error")}',
                metadata={'file': file_path},
                guidance='Could not access file for verification'
            )

        # Check for expected changes
        verification = {
            'file': file_path,
            'line_count': result.get('lineCount', 0),
            'is_open': result.get('isOpen', False)
        }

        if expected_changes and result.get('content'):
            changes_found = expected_changes in result['content']
            verification['changes_found'] = changes_found

            status = "[OK] verified" if changes_found else "[NOT FOUND]"
            content = f'Verification {status}: "{expected_changes}" in {file_path}'
        else:
            content = f'File verified: {file_path} ({verification["line_count"]} lines)'

        if self._logger:
            self._logger.success(f"[Coding] Verified {file_path}")

        return self._success_result(
            content,
            metadata=verification
        )

    async def _handle_files(self) -> Dict[str, Any]:
        """Handle files command: coding.files with no args"""
        result = self._get_open_files()

        if not result.get('success'):
            return self._error_result(
                f'Failed to get files: {result.get("error")}',
                guidance=f'Check {self.editor_name} extension connection'
            )

        files = result.get('files', [])
        active_file = result.get('activeFile')

        if not files:
            return self._success_result(
                f'No files open in {self.editor_name}',
                metadata={'count': 0}
            )

        # Build file list
        lines = [f"Open files ({len(files)}):"]

        for i, file_info in enumerate(files):
            file_name = file_info.get('fileName', 'Unknown')
            file_path = file_info.get('filePath', '')
            is_active = file_path == active_file
            marker = "> " if is_active else "  "

            lines.append(f"{marker}{i+1}. {file_name}")
            if is_active:
                lines.append(f"     (Active)")

        if self._logger:
            self._logger.success(f"[Coding] Retrieved {len(files)} open files")

        return self._success_result(
            '\n'.join(lines),
            metadata={
                'count': len(files),
                'files': files,
                'active_file': active_file
            }
        )

    async def _handle_status(self) -> Dict[str, Any]:
        """Handle status command: coding.status with no args"""
        status = self._get_status_info()

        lines = [
            f"{self.editor_name} Extension Status:",
            f"  Available: {status['available']}",
            f"  Server: {status['server_url']}",
            f"  Open files: {status['open_files']}",
        ]

        if status['active_file']:
            lines.append(f"  Active file: {status['active_file']}")

        if self._logger:
            self._logger.system("[Coding] Status check complete")

        return self._success_result(
            '\n'.join(lines),
            metadata=status
        )

    # === Internal Helper Methods ===

    def _get_open_files(self) -> Dict[str, Any]:
        """Get open files from editor extension"""
        try:
            response = requests.get(
                self.files_endpoint,
                timeout=5,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'files': []
            }

    def _fetch_file_content(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fetch file content from editor extension"""
        try:
            params = {'path': str(Path(file_path).resolve())}

            if start_line is not None:
                params['startLine'] = str(start_line)
            if end_line is not None:
                params['endLine'] = str(end_line)

            response = requests.get(
                self.file_endpoint,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _send_edit_instruction(
        self,
        prompt: str,
        file_path: Optional[str] = None,
        selection: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send edit instruction to editor extension"""
        if not prompt or not prompt.strip():
            return {
                'success': False,
                'error': 'Empty prompt provided'
            }

        payload = {'prompt': prompt}

        if file_path:
            payload['file'] = str(Path(file_path).resolve())

        if selection:
            import json
            payload['selection'] = json.dumps(selection)

        try:
            response = requests.post(
                self.edit_endpoint,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'Request timed out after {self.timeout} seconds'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': f'Could not connect to {self.editor_name} extension'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
