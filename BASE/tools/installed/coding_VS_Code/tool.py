# Filename: BASE/tools/installed/coding_VS_Code/tool.py
"""
VS Code Coding Tool - Simplified Architecture
Single master class with start() and end() lifecycle
Integrates with VS Code Ollama Code Editor extension via HTTP REST API
"""
import asyncio
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
    VS Code integration for AI-powered code editing
    Communicates with VS Code extension via HTTP REST API
    """
    
    @property
    def name(self) -> str:
        return "coding"
    
    async def initialize(self) -> bool:
        """
        Initialize VS Code coding system
        
        Returns:
            True if initialization successful (always returns True for graceful degradation)
        """
        # Server configuration
        self.server_url = getattr(
            self._config,
            'vscode_server_url',
            'http://localhost:3000'
        ).rstrip('/')
        
        self.timeout = getattr(self._config, 'vscode_timeout', 30)
        
        # Endpoints
        self.edit_endpoint = f"{self.server_url}/edit"
        self.file_endpoint = f"{self.server_url}/file"
        self.files_endpoint = f"{self.server_url}/files"
        
        # Cache
        self._cached_files = None
        self._cache_time = 0
        
        # Check initial connection
        available = self.is_available()
        
        if self._logger:
            if available:
                status = self._get_status_info()
                self._logger.system(
                    f"[Coding] VS Code extension ready: "
                    f"{status.get('open_files', 0)} files open, "
                    f"active: {status.get('active_file', 'none')}"
                )
            else:
                self._logger.warning(
                    f"[Coding] VS Code extension not available (server: {self.server_url})"
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
        Check if VS Code extension server is available
        
        Returns:
            True if server is responding
        """
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.get(self.server_url, timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get VS Code extension status
        
        Returns:
            Status dictionary with connection info
        """
        return self._get_status_info()
    
    def _get_status_info(self) -> Dict[str, Any]:
        """Internal method to get status info"""
        status = {
            'available': self.is_available(),
            'requests_available': REQUESTS_AVAILABLE,
            'server_url': self.server_url,
            'open_files': 0,
            'active_file': None
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
        
        # Check availability
        if not self.is_available():
            return self._error_result(
                'VS Code extension not available',
                metadata={
                    'server_url': self.server_url,
                    'requests_available': REQUESTS_AVAILABLE
                },
                guidance='Ensure VS Code is running with Ollama Code Editor extension on localhost:3000'
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
            elif command == 'status':
                return await self._handle_status()
            elif command == 'search':
                return await self._handle_search(args)
            elif command == 'tree':
                return await self._handle_tree(args)
            elif command == 'patch':
                return await self._handle_patch(args)
            else:
                return self._error_result(
                    f'Unknown command: {command}',
                    guidance='Available commands: edit, fetch, verify, files, status, search, tree, patch'
                )
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Coding] Command error: {e}")
            import traceback
            traceback.print_exc()
            
            return self._error_result(
                f'Command execution failed: {str(e)}',
                metadata={'error': str(e)},
                guidance='Check VS Code extension and network connection'
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
            message = result.get('message', 'Edit instruction sent to VS Code')
            
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
                guidance='Check VS Code extension status and file accessibility'
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
                guidance='Check file path and VS Code extension'
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
                guidance='Check VS Code extension connection'
            )
        
        files = result.get('files', [])
        active_file = result.get('activeFile')
        
        if not files:
            return self._success_result(
                'No files open in VS Code',
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
            "VS Code Extension Status:",
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
    

    async def _handle_search(self, args):
        """
        Handle search command: coding.search with [query, optional_root, optional_mode]
        Modes: text (default), function, file
        """
        if not args:
            return self._error_result(
                'No search query provided',
                guidance='Usage: {"tool": "coding.search", "args": ["query", "project/root", "text|function|file"]}'
            )

        query = str(args[0])
        root = str(args[1]) if len(args) > 1 and args[1] else '.'
        mode = str(args[2]).lower() if len(args) > 2 and args[2] else 'text'

        try:
            results = self._search_codebase(query, root, mode)
            if not results:
                return self._success_result(
                    f'No results found for "{query}" (mode: {mode})',
                    metadata={'query': query, 'mode': mode, 'root': root, 'matches': []}
                )

            lines = [f'Search results for "{query}" (mode: {mode}, root: {root}):']
            for match in results[:30]:
                lines.append(f'  {match["file"]}:{match.get("line", "")}  {match.get("preview", "").strip()}')

            if self._logger:
                self._logger.success(f"[Coding] Search '{query}' found {len(results)} result(s)")

            return self._success_result(
                '\n'.join(lines),
                metadata={'query': query, 'mode': mode, 'root': root, 'matches': results}
            )

        except Exception as e:
            return self._error_result(
                f'Search failed: {str(e)}',
                guidance='Check that the root path exists and is accessible'
            )

    async def _handle_tree(self, args):
        """
        Handle tree command: coding.tree with [optional_root, optional_max_depth]
        Returns folder/file structure of the project.
        """
        root = str(args[0]) if args and args[0] else '.'
        max_depth = int(args[1]) if len(args) > 1 and args[1] else 3

        try:
            root_path = Path(root).resolve()
            if not root_path.exists():
                return self._error_result(
                    f'Root path does not exist: {root}',
                    guidance='Provide a valid project root directory'
                )

            lines = [str(root_path)]
            self._build_tree(root_path, lines, prefix='', depth=0, max_depth=max_depth)

            if self._logger:
                self._logger.success(f"[Coding] Tree generated for {root_path}")

            return self._success_result(
                '\n'.join(lines),
                metadata={'root': str(root_path), 'max_depth': max_depth}
            )

        except Exception as e:
            return self._error_result(
                f'Tree failed: {str(e)}',
                guidance='Check that the root path is accessible'
            )

    async def _handle_patch(self, args):
        """
        Handle patch command: coding.patch with [file_path, start_line, end_line, new_content]
        Replaces lines start_line..end_line (1-indexed, inclusive) with new_content.
        """
        if len(args) < 4:
            return self._error_result(
                'patch requires 4 args: file_path, start_line, end_line, new_content',
                guidance='Usage: {"tool": "coding.patch", "args": ["main.py", 10, 20, "replacement code"]}'
            )

        file_path_str = str(args[0])
        try:
            start_line = int(args[1])
            end_line = int(args[2])
        except (ValueError, TypeError):
            return self._error_result(
                'start_line and end_line must be integers',
                guidance='Line numbers are 1-indexed and inclusive'
            )

        new_content = str(args[3])

        try:
            file_path = Path(file_path_str).resolve()
            if not file_path.exists():
                return self._error_result(
                    f'File not found: {file_path_str}',
                    guidance='Ensure the file path is correct and relative to project root'
                )

            original_lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
            total_lines = len(original_lines)

            if start_line < 1 or end_line > total_lines or start_line > end_line:
                return self._error_result(
                    f'Invalid line range {start_line}-{end_line} for file with {total_lines} lines',
                    guidance='Use coding.fetch first to confirm line numbers'
                )

            replacement = new_content if new_content.endswith('\n') else new_content + '\n'
            patched = original_lines[:start_line - 1] + [replacement] + original_lines[end_line:]
            file_path.write_text(''.join(patched), encoding='utf-8')

            lines_replaced = end_line - start_line + 1
            summary = (
                f'Patched {file_path_str}: replaced lines {start_line}-{end_line} '
                f'({lines_replaced} line(s) replaced)'
            )

            if self._logger:
                self._logger.success(f"[Coding] {summary}")

            try:
                self._send_edit_instruction(
                    f'File {file_path_str} was patched externally at lines {start_line}-{end_line}. Reload.',
                    file_path_str
                )
            except Exception:
                pass

            return self._success_result(
                summary,
                metadata={
                    'file': file_path_str,
                    'start_line': start_line,
                    'end_line': end_line,
                    'lines_replaced': lines_replaced,
                    'new_line_count': len(patched)
                }
            )

        except Exception as e:
            return self._error_result(
                f'Patch failed: {str(e)}',
                metadata={'error': str(e)},
                guidance='Check file permissions and that line numbers are correct'
            )

    def _search_codebase(self, query, root, mode):
        """Search the codebase for query string, function name, or filename."""
        import os
        import re as _re

        root_path = Path(root).resolve()
        matches = []
        SKIP_DIRS = {'__pycache__', '.git', '.venv', 'venv', 'node_modules', '.mypy_cache', '.pytest_cache'}
        TEXT_EXTS = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
            '.md', '.txt', '.html', '.css', '.env', '.cfg', '.ini', '.toml'
        }

        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for filename in filenames:
                filepath = Path(dirpath) / filename
                rel = str(filepath.relative_to(root_path))

                if mode == 'file':
                    if query.lower() in filename.lower():
                        matches.append({'file': rel, 'line': '', 'preview': filename})
                    continue

                if filepath.suffix not in TEXT_EXTS:
                    continue

                try:
                    text = filepath.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

                if mode == 'function':
                    pattern = _re.compile(
                        rf'(def\s+{_re.escape(query)}|function\s+{_re.escape(query)}|{_re.escape(query)}\s*[=:]\s*(async\s+)?function)',
                        _re.IGNORECASE
                    )
                    for i, line in enumerate(text.splitlines(), 1):
                        if pattern.search(line):
                            matches.append({'file': rel, 'line': i, 'preview': line.strip()})
                else:  # text search
                    for i, line in enumerate(text.splitlines(), 1):
                        if query.lower() in line.lower():
                            matches.append({'file': rel, 'line': i, 'preview': line.strip()})

        return matches

    def _build_tree(self, path, lines, prefix, depth, max_depth):
        """Recursively build a tree representation of the directory."""
        import os
        SKIP_DIRS = {'__pycache__', '.git', '.venv', 'venv', 'node_modules', '.mypy_cache'}

        if depth >= max_depth:
            return

        try:
            entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        entries = [e for e in entries if not (e.is_dir() and e.name in SKIP_DIRS)]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = '└── ' if is_last else '├── '
            lines.append(f'{prefix}{connector}{entry.name}')
            if entry.is_dir():
                extension = '    ' if is_last else '│   '
                self._build_tree(entry, lines, prefix + extension, depth + 1, max_depth)

    # === Internal Helper Methods ===
    
    def _get_open_files(self) -> Dict[str, Any]:
        """Get open files from VS Code"""
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
        """Fetch file content from VS Code"""
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
        """Send edit instruction to VS Code"""
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
                'error': 'Could not connect to VS Code extension'
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