#!/usr/bin/env python3
"""
Anna AI CLI Launcher
====================
Standalone CLI entry point for Anna AI agent.
Provides command-line interaction similar to Claude Code.

Usage:
    python anna_cli.py                    # Interactive mode
    python anna_cli.py "your message"      # Single command
    python anna_cli.py --help             # Show help
    python anna_cli.py --check            # System health check
    python anna_cli.py --no-color         # Disable colors

Inspired by Claude Code's CLI experience.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# ANSI color codes
class Colors:
    """Terminal color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @classmethod
    def disable(cls):
        """Disable all colors"""
        cls.RESET = cls.BOLD = cls.RED = cls.GREEN = cls.YELLOW = ""
        cls.BLUE = cls.MAGENTA = cls.CYAN = cls.GRAY = ""


class AnnaCLI:
    """Anna AI Command Line Interface"""

    def __init__(self, no_color: bool = False, verbose: bool = False):
        self.no_color = no_color
        self.verbose = verbose
        self.running = True

        if no_color:
            Colors.disable()

        # Import core components
        self.ai_core = None
        self.config = None
        self.logger = None

    def print_banner(self):
        """Print startup banner"""
        print(f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   {Colors.BOLD}Anna AI - CLI Interface{Colors.RESET}{Colors.CYAN}                              ║
║   {Colors.GRAY}Your AI Agent Companion{Colors.RESET}{Colors.CYAN}                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.GRAY}Type your message or 'help' for commands{Colors.RESET}
Type 'exit' or 'quit' to end the session
""")

    async def initialize(self) -> bool:
        """Initialize Anna AI core"""
        try:
            # Load environment
            from dotenv import load_dotenv
            env_file = PROJECT_ROOT / ".env"
            if env_file.exists():
                load_dotenv(env_file)

            # Import core
            from BASE.core.config import Config
            from BASE.core.logger import Logger, MessageType
            from BASE.core.core_initializer import CoreInitializer

            print(f"{Colors.GRAY}[INFO] Initializing Anna AI...{Colors.RESET}")

            self.config = Config()
            self.logger = Logger(self.config)

            print(f"{Colors.GRAY}[INFO] Loading AI core...{Colors.RESET}")

            core_initializer = CoreInitializer(self.config, self.logger)
            self.ai_core = core_initializer.initialize()

            if not self.ai_core:
                print(f"{Colors.RED}[ERROR] Failed to initialize AI core{Colors.RESET}")
                return False

            print(f"{Colors.GREEN}[OK] Anna AI ready!{Colors.RESET}\n")
            return True

        except Exception as e:
            print(f"{Colors.RED}[ERROR] Initialization failed: {e}{Colors.RESET}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def print_help(self):
        """Print help message"""
        print(f"""
{Colors.BOLD}Anna AI CLI Commands:{Colors.RESET}

{Colors.CYAN}General:{Colors.RESET}
  help, ?         - Show this help message
  exit, quit, q   - Exit the CLI
  clear, cls      - Clear screen

{Colors.CYAN}Tools:{Colors.RESET}
  tools           - List available tools
  enable <tool>   - Enable a tool
  disable <tool>  - Disable a tool

{Colors.CYAN}Git Integration:{Colors.RESET}
  git status      - Show git status
  git log         - Show recent commits
  git branch      - List branches

{Colors.CYAN}System:{Colors.RESET}
  check           - Run system health check
  restart         - Restart AI core
  verbose         - Toggle verbose mode
  version, ver    - Show version info

{Colors.GRAY}You can also ask questions naturally!{Colors.RESET}
""")

    async def handle_command(self, user_input: str) -> bool:
        """Handle special CLI commands"""
        cmd = user_input.strip().lower()

        # Exit commands
        if cmd in ('exit', 'quit', 'q'):
            print(f"{Colors.YELLOW}Goodbye!{Colors.RESET}")
            self.running = False
            return True

        # Help
        if cmd in ('help', '?'):
            self.print_help()
            return True

        # Clear screen
        if cmd in ('clear', 'cls'):
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()
            return True

        # List tools
        if cmd == 'tools':
            await self.list_tools()
            return True

        # System check
        if cmd == 'check':
            self.run_health_check()
            return True

        # Version
        if cmd in ('version', 'ver'):
            print(f"{Colors.CYAN}Anna AI CLI v1.0.0{Colors.RESET}")
            return True

        # Toggle verbose
        if cmd == 'verbose':
            self.verbose = not self.verbose
            status = "enabled" if self.verbose else "disabled"
            print(f"{Colors.GREEN}Verbose mode {status}{Colors.RESET}")
            return True

        # Git shortcuts
        if cmd.startswith('git '):
            await self.handle_git_command(cmd[4:])
            return True

        # Not a special command - process as AI message
        return False

    async def list_tools(self):
        """List available tools"""
        if not self.ai_core or not hasattr(self.ai_core, 'tool_manager'):
            print(f"{Colors.RED}Tool manager not available{Colors.RESET}")
            return

        try:
            tool_manager = self.ai_core.tool_manager
            enabled = tool_manager.get_enabled_tool_names()
            all_meta = tool_manager.get_all_tool_metadata()

            print(f"\n{Colors.BOLD}Available Tools:{Colors.RESET}")

            for tool_name in sorted(all_meta.keys()):
                meta = all_meta[tool_name]
                status = f"{Colors.GREEN}✓ enabled{Colors.RESET}" if tool_name in enabled else f"{Colors.GRAY}disabled{Colors.RESET}"
                desc = meta.get('tool_description', 'No description')[:50]
                print(f"  {Colors.CYAN}{tool_name}{Colors.RESET} - {desc} [{status}]")

            print()
        except Exception as e:
            print(f"{Colors.RED}Error listing tools: {e}{Colors.RESET}")

    async def handle_git_command(self, git_cmd: str):
        """Handle git shortcut commands"""
        if not self.ai_core or not hasattr(self.ai_core, 'tool_manager'):
            print(f"{Colors.RED}Tool manager not available{Colors.RESET}")
            return

        # Parse git command
        parts = git_cmd.strip().split()
        if not parts:
            print(f"{Colors.YELLOW}Usage: git <status|log|branch|diff>{Colors.RESET}")
            return

        subcmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Build tool call
        tool_call = f"git.{subcmd}"

        print(f"{Colors.GRAY}[Executing] git {subcmd}...{Colors.RESET}")

        # This would need proper thought buffer integration
        # For now, just show the command structure
        print(f"\n{Colors.CYAN}Git {subcmd} command prepared{Colors.RESET}")
        print(f"Tool: {tool_call}")
        print(f"Args: {args}")
        print(f"\n{Colors.GRAY}Note: Full execution requires thought buffer integration{Colors.RESET}\n")

    def run_health_check(self):
        """Run system health check"""
        print(f"\n{Colors.BOLD}Running Health Check...{Colors.RESET}\n")

        checks = [
            ("Python Version", sys.version_info >= (3, 11)),
            ("Project Structure", (PROJECT_ROOT / "BASE").exists()),
            (".env File", (PROJECT_ROOT / ".env").exists()),
        ]

        for name, result in checks:
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"  {status} {name}")

        print()

    async def chat(self, message: str) -> str:
        """Send message to AI and get response"""
        if not self.ai_core:
            return "AI core not initialized"

        try:
            # Process message through AI core
            self.ai_core.process_user_message(message)

            # In a proper implementation, this would wait for response
            # For now, return a placeholder
            return "Processing..."

        except Exception as e:
            return f"Error: {str(e)}"

    async def run_interactive(self):
        """Run interactive CLI loop"""
        self.print_banner()

        # Initialize AI
        if not await self.initialize():
            return 1

        # Main loop
        while self.running:
            try:
                user_input = input(f"{Colors.CYAN}You:{Colors.RESET} ").strip()

                if not user_input:
                    continue

                # Check for special commands first
                is_handled = await self.handle_command(user_input)

                if not is_handled and self.running:
                    # Process as AI message
                    print(f"{Colors.GRAY}Anna: ...{Colors.RESET}")
                    response = await self.chat(user_input)
                    print(f"{Colors.GREEN}Anna:{Colors.RESET} {response}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Interrupted. Type 'exit' to quit.{Colors.RESET}")
            except EOFError:
                break

        return 0

    async def run_single(self, message: str) -> int:
        """Run single command"""
        if not await self.initialize():
            return 1

        response = await self.chat(message)
        print(f"\n{Colors.GREEN}Anna:{Colors.RESET} {response}")

        return 0


async def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Anna AI - CLI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python anna_cli.py                    # Start interactive mode
  python anna_cli.py "Hello"           # Single command
  python anna_cli.py --check           # Health check
  python anna_cli.py --no-color        # No colors
  python anna_cli.py -v "your message" # Verbose mode
        """
    )

    parser.add_argument(
        'message',
        nargs='?',
        help='Message to send to Anna AI'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Run health check and exit'
    )

    args = parser.parse_args()

    cli = AnnaCLI(no_color=args.no_color, verbose=args.verbose)

    if args.check:
        cli.run_health_check()
        return 0

    if args.message:
        return await cli.run_single(args.message)

    return await cli.run_interactive()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
