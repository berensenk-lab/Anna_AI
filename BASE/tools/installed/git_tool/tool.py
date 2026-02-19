"""
Git Tool - Version control operations for Anna AI
Supports: status, diff, branch, commit, log, stash, fetch, pull, push, remote

This tool provides Git integration similar to Claude Code's built-in Git support.
"""
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from BASE.handlers.base_tool import BaseTool


class GitTool(BaseTool):
    """
    Git integration tool for Anna AI

    Provides version control operations including:
    - Repository status
    - File differences
    - Branch management
    - Commit creation
    - Commit history
    - Remote operations
    """

    def __init__(self, config, controls, logger=None):
        super().__init__(config, controls, logger)
        self.default_repo_path = None

    @property
    def name(self) -> str:
        return "git"

    async def initialize(self) -> bool:
        """Initialize git tool"""
        # Try to find default repo path (project root)
        self.default_repo_path = self._config.get('PROJECT_ROOT', '.')

        if self._logger:
            self._logger.system(f"[Git] Initialized with default path: {self.default_repo_path}")

        return True

    async def cleanup(self):
        """Cleanup git tool"""
        if self._logger:
            self._logger.system("[Git] Cleaned up")

    def is_available(self) -> bool:
        """Check if git is available"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """
        Execute git command

        Commands:
        - status: Get repository status
        - diff: Get file differences
        - branch: List/create/switch branches
        - commit: Create a commit
        - log: Get commit history
        - stash: Stash changes
        - fetch: Fetch from remote
        - pull: Pull from remote
        - push: Push to remote
        - remote: Manage remotes

        Args:
            command: Command name
            args: Command arguments [repo_path, ...options]

        Returns:
            Standardized result dict
        """
        if self._logger:
            self._logger.tool(f"[Git] Command: '{command}', args: {args}")

        # Get repo path (first arg or default)
        repo_path = str(args[0]) if args else self.default_repo_path
        extra_args = args[1:] if len(args) > 1 else []

        # Validate repo path
        if not await self._is_git_repo(repo_path):
            return self._error_result(
                f"Not a git repository: {repo_path}",
                guidance="Provide a valid git repository path"
            )

        # Execute command
        if command == 'status':
            return await self._git_status(repo_path)

        elif command == 'diff':
            return await self._git_diff(repo_path, extra_args)

        elif command == 'branch':
            return await self._git_branch(repo_path, extra_args)

        elif command == 'commit':
            return await self._git_commit(repo_path, extra_args)

        elif command == 'log':
            return await self._git_log(repo_path, extra_args)

        elif command == 'stash':
            return await self._git_stash(repo_path, extra_args)

        elif command == 'fetch':
            return await self._git_fetch(repo_path, extra_args)

        elif command == 'pull':
            return await self._git_pull(repo_path, extra_args)

        elif command == 'push':
            return await self._git_push(repo_path, extra_args)

        elif command == 'remote':
            return await self._git_remote(repo_path, extra_args)

        elif command == 'add':
            return await self._git_add(repo_path, extra_args)

        elif command in ['', 'help']:
            return self._list_commands()

        return self._error_result(
            f"Unknown command: {command}",
            guidance="Available commands: status, diff, branch, commit, log, stash, fetch, pull, push, remote, add"
        )

    def _list_commands(self) -> Dict[str, Any]:
        """List available commands"""
        commands = """
**Available Git Commands:**

| Command | Description |
|---------|-------------|
| `status` | Show working tree status |
| `diff` | Show changes |
| `branch` | List/create/switch branches |
| `commit` | Create a new commit |
| `log` | Show commit history |
| `stash` | Stash changes |
| `add` | Stage files |
| `fetch` | Fetch from remote |
| `pull` | Pull from remote |
| `push` | Push to remote |
| `remote` | Manage remotes |

**Usage Examples:**
```
{"tool": "git.status", "args": ["/path/to/repo"]}
{"tool": "git.diff", "args": ["/path/to/repo", "--staged"]}
{"tool": "git.branch", "args": ["/path/to/repo", "-a"]}
{"tool": "git.commit", "args": ["/path/to/repo", "Your commit message"]}
{"tool": "git.log", "args": ["/path/to/repo", "-10"]}
```
"""
        return self._success_result(
            commands,
            metadata={"command_count": 11}
        )

    async def _is_git_repo(self, path: str) -> bool:
        """Check if path is a git repository"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _run_git(self, args: List[str], cwd: str) -> Dict[str, Any]:
        """Run git command and return result"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            else:
                return {
                    'success': False,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }

    async def _git_status(self, repo_path: str) -> Dict[str, Any]:
        """Get git status"""
        result = await self._run_git(['status', '--porcelain'], repo_path)

        if not result['success']:
            return self._error_result(
                f"Git status failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        output = result['stdout'].strip()

        if not output:
            return self._success_result(
                "✅ Working tree is clean (no changes)",
                metadata={'repo': repo_path, 'clean': True}
            )

        # Parse status output
        lines = output.split('\n')
        staged = []
        modified = []
        untracked = []
        deleted = []

        for line in lines:
            if len(line) < 2:
                continue

            status = line[:2]
            filepath = line[3:]

            if status[0] != ' ':
                staged.append(f"{status[0]}: {filepath}")
            if status[1] == 'M':
                modified.append(filepath)
            elif status[1] == 'D':
                deleted.append(filepath)
            elif status == '??':
                untracked.append(filepath)

        # Format output
        output_lines = ["**Git Status**", ""]

        if staged:
            output_lines.append("📦 **Staged Changes:**")
            for s in staged:
                output_lines.append(f"  - {s}")
            output_lines.append("")

        if modified:
            output_lines.append("✏️ **Modified Files:**")
            for m in modified:
                output_lines.append(f"  - {m}")
            output_lines.append("")

        if deleted:
            output_lines.append("❌ **Deleted Files:**")
            for d in deleted:
                output_lines.append(f"  - {d}")
            output_lines.append("")

        if untracked:
            output_lines.append("❓ **Untracked Files:**")
            for u in untracked:
                output_lines.append(f"  - {u}")
            output_lines.append("")

        output_lines.append(f"**Total changes:** {len(lines)} file(s)")

        if self._logger:
            self._logger.success(f"[Git] Status: {len(lines)} changes")

        return self._success_result(
            '\n'.join(output_lines),
            metadata={
                'repo': repo_path,
                'staged': len(staged),
                'modified': len(modified),
                'deleted': len(deleted),
                'untracked': len(untracked)
            }
        )

    async def _git_diff(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Get git diff"""
        args = ['diff', '--color=never']
        args.extend(extra_args)

        result = await self._run_git(args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git diff failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        output = result['stdout'].strip()

        if not output:
            return self._success_result(
                "✅ No differences found",
                metadata={'repo': repo_path, 'has_diff': False}
            )

        # Truncate if too long
        if len(output) > 10000:
            output = output[:10000] + "\n\n... (truncated)"

        if self._logger:
            self._logger.success(f"[Git] Diff retrieved: {len(output)} chars")

        return self._success_result(
            f"**Git Diff**\n\n{output}",
            metadata={'repo': repo_path, 'has_diff': True}
        )

    async def _git_branch(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Handle branch operations"""
        if not extra_args:
            # List branches
            result = await self._run_git(['branch', '-a'], repo_path)
        elif extra_args[0] == '-c' and len(extra_args) > 2:
            # Create branch: git branch -c <name> <start-point>
            result = await self._run_git(['branch', '-c', extra_args[1], extra_args[2] if len(extra_args) > 2 else 'HEAD'], repo_path)
        elif extra_args[0] == '-d' and len(extra_args) > 1:
            # Delete branch: git branch -d <name>
            result = await self._run_git(['branch', '-d'] + extra_args[1:], repo_path)
        elif extra_args[0] == '-D' and len(extra_args) > 1:
            # Force delete: git branch -D <name>
            result = await self._run_git(['branch', '-D'] + extra_args[1:], repo_path)
        elif extra_args[0] == 'checkout' or extra_args[0] == 'switch':
            # Checkout/switch branch
            cmd = 'checkout' if extra_args[0] == 'checkout' else 'switch'
            result = await self._run_git([cmd] + extra_args[1:], repo_path)
        elif extra_args[0] == '-m' and len(extra_args) > 1:
            # Rename branch: git branch -m <old> <new>
            result = await self._run_git(['branch', '-m', extra_args[1], extra_args[2] if len(extra_args) > 2 else ''], repo_path)
        else:
            # Just list with extra args
            result = await self._run_git(['branch'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git branch failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        output = result['stdout'].strip()

        # Get current branch
        current = await self._run_git(['branch', '--show-current'], repo_path)
        current_branch = current['stdout'].strip() if current['success'] else 'unknown'

        if self._logger:
            self._logger.success(f"[Git] Branch operation completed")

        return self._success_result(
            f"**Git Branch**\n\nCurrent: `{current_branch}`\n\n{output}",
            metadata={'repo': repo_path, 'current': current_branch}
        )

    async def _git_commit(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Create a git commit"""
        if not extra_args:
            return self._error_result(
                "No commit message provided",
                guidance='Usage: {"tool": "git.commit", "args": ["/repo", "Your commit message"]}'
            )

        commit_message = ' '.join(extra_args)

        # Check if there are staged changes
        status = await self._run_git(['status', '--porcelain'], repo_path)
        has_staged = any(line.startswith(('M', 'A', 'D', 'R', 'C')) for line in status['stdout'].split('\n') if line)

        if not has_staged:
            return self._error_result(
                "No staged changes to commit",
                guidance='Stage files first with: {"tool": "git.add", "args": ["/repo", "."]}'
            )

        result = await self._run_git(['commit', '-m', commit_message], repo_path)

        if not result['success']:
            return self._error_result(
                f"Git commit failed: {result['stderr']}",
                metadata={'repo': repo_path, 'message': commit_message}
            )

        # Get commit info
        commit_hash = await self._run_git(['rev-parse', 'HEAD'], repo_path)
        short_hash = commit_hash['stdout'][:8] if commit_hash['success'] else 'unknown'

        if self._logger:
            self._logger.success(f"[Git] Commit created: {short_hash}")

        return self._success_result(
            f"✅ **Commit Created**\n\nHash: `{short_hash}`\nMessage: {commit_message}",
            metadata={
                'repo': repo_path,
                'hash': short_hash,
                'message': commit_message
            }
        )

    async def _git_log(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Get git log"""
        # Default to 10 commits
        if not extra_args:
            extra_args = ['-10']

        # Check if first arg is a number
        try:
            count = int(extra_args[0])
            extra_args = [f'-{count}']
        except ValueError:
            pass

        result = await self._run_git(['log', '--oneline', '--decorate'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git log failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        output = result['stdout'].strip()

        if not output:
            return self._success_result(
                "No commits found",
                metadata={'repo': repo_path, 'count': 0}
            )

        commits = output.split('\n')

        if self._logger:
            self._logger.success(f"[Git] Log: {len(commits)} commits")

        return self._success_result(
            f"**Git Log ({len(commits)} commits)**\n\n{output}",
            metadata={'repo': repo_path, 'count': len(commits)}
        )

    async def _git_stash(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Handle stash operations"""
        if not extra_args:
            # Default: stash changes
            result = await self._run_git(['stash'], repo_path)
        elif extra_args[0] == 'pop':
            result = await self._run_git(['stash', 'pop'], repo_path)
        elif extra_args[0] == 'list':
            result = await self._run_git(['stash', 'list'], repo_path)
        elif extra_args[0] == 'drop':
            result = await self._run_git(['stash', 'drop'] + extra_args[1:], repo_path)
        elif extra_args[0] == 'show':
            result = await self._run_git(['stash', 'show'] + extra_args[1:], repo_path)
        else:
            result = await self._run_git(['stash'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git stash failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        if self._logger:
            self._logger.success(f"[Git] Stash operation completed")

        return self._success_result(
            f"✅ **Stash Operation Complete**\n\n{result['stdout'].strip()}",
            metadata={'repo': repo_path}
        )

    async def _git_add(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Stage files"""
        if not extra_args:
            return self._error_result(
                "No files to stage",
                guidance='Usage: {"tool": "git.add", "args": ["/repo", "."]} or {"tool": "git.add", "args": ["/repo", "file.txt"]}'
            )

        result = await self._run_git(['add'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git add failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        files = ', '.join(extra_args)

        if self._logger:
            self._logger.success(f"[Git] Staged: {files}")

        return self._success_result(
            f"✅ **Files Staged**\n\nStaged: {files}",
            metadata={'repo': repo_path, 'files': files}
        )

    async def _git_fetch(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Fetch from remote"""
        result = await self._run_git(['fetch'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git fetch failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        if self._logger:
            self._logger.success(f"[Git] Fetch completed")

        return self._success_result(
            f"✅ **Fetch Complete**\n\n{result['stdout'].strip() or 'Successfully fetched from remote'}",
            metadata={'repo': repo_path}
        )

    async def _git_pull(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Pull from remote"""
        result = await self._run_git(['pull'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git pull failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        if self._logger:
            self._logger.success(f"[Git] Pull completed")

        return self._success_result(
            f"✅ **Pull Complete**\n\n{result['stdout'].strip()}",
            metadata={'repo': repo_path}
        )

    async def _git_push(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Push to remote"""
        result = await self._run_git(['push'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git push failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        if self._logger:
            self._logger.success(f"[Git] Push completed")

        return self._success_result(
            f"✅ **Push Complete**\n\n{result['stdout'].strip()}",
            metadata={'repo': repo_path}
        )

    async def _git_remote(self, repo_path: str, extra_args: List[str]) -> Dict[str, Any]:
        """Handle remote operations"""
        if not extra_args or extra_args[0] == '-v':
            # List remotes
            result = await self._run_git(['remote', '-v'], repo_path)
        elif extra_args[0] == 'add' and len(extra_args) > 1:
            # Add remote: git remote add <name> <url>
            result = await self._run_git(['remote', 'add', extra_args[1], extra_args[2] if len(extra_args) > 2 else ''], repo_path)
        elif extra_args[0] == 'remove':
            result = await self._run_git(['remote', 'remove'] + extra_args[1:], repo_path)
        elif extra_args[0] == 'rename':
            result = await self._run_git(['remote', 'rename'] + extra_args[1:], repo_path)
        elif extra_args[0] == 'get-url':
            result = await self._run_git(['remote', 'get-url'] + extra_args[1:], repo_path)
        else:
            result = await self._run_git(['remote'] + extra_args, repo_path)

        if not result['success']:
            return self._error_result(
                f"Git remote failed: {result['stderr']}",
                metadata={'repo': repo_path}
            )

        output = result['stdout'].strip()

        if not output:
            output = "No remotes configured"

        if self._logger:
            self._logger.success(f"[Git] Remote operation completed")

        return self._success_result(
            f"**Git Remotes**\n\n{output}",
            metadata={'repo': repo_path}
        )
