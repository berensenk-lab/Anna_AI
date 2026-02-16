#!/usr/bin/env python3
"""
Anna AI - Main Application Entry Point

This module serves as the single entry point for the Anna AI agentic system.
It orchestrates initialization, configuration loading, and system startup.

Usage:
    python main.py                 # Start with GUI
    python main.py --no-gui        # CLI only
    python main.py --check         # Verify system health
    python main.py --help          # Show usage
"""

import argparse
import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from BASE.core.logger import Logger, MessageType
from BASE.core.config import Config
from BASE.core.core_initializer import CoreInitializer


class AnnaAIApp:
    """Main application class for Anna AI system."""

    def __init__(self, gui_enabled: bool = True, verbose: bool = False):
        """
        Initialize the Anna AI application.

        Args:
            gui_enabled: Whether to start the GUI interface
            verbose: Enable verbose logging
        """
        self.gui_enabled = gui_enabled
        self.verbose = verbose
        self.logger: Optional[Logger] = None
        self.config: Optional[Config] = None
        self.ai_core = None
        self.gui = None

    def setup_environment(self) -> bool:
        """
        Set up environment variables and paths.

        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Load .env file
            from dotenv import load_dotenv
            env_file = PROJECT_ROOT / ".env"
            if env_file.exists():
                load_dotenv(env_file)
            else:
                print(f"[WARNING] .env file not found at {env_file}")
                print("         Using default environment settings")

            # Create required directories
            required_dirs = [
                PROJECT_ROOT / "logs",
                PROJECT_ROOT / "personality" / "memory",
                PROJECT_ROOT / "personality" / "base_memory",
                PROJECT_ROOT / "models",
            ]

            for directory in required_dirs:
                directory.mkdir(parents=True, exist_ok=True)

            return True

        except Exception as e:
            print(f"[ERROR] Failed to setup environment: {e}")
            traceback.print_exc()
            return False

    def initialize_core(self) -> bool:
        """
        Initialize the core AI system.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            print("[INFO] Initializing configuration...")
            self.config = Config()

            print("[INFO] Initializing logger...")
            self.logger = Logger(self.config)
            if self.verbose:
                self.config.LOG_LEVEL = "DEBUG"

            self.logger.log(
                "Application started",
                MessageType.SYSTEM,
                extra_info={"version": "1.0.0", "mode": "GUI" if self.gui_enabled else "CLI"}
            )

            print("[INFO] Initializing AI core...")
            core_initializer = CoreInitializer(self.config, self.logger)
            self.ai_core = core_initializer.initialize()

            if not self.ai_core:
                self.logger.log(
                    "Failed to initialize AI core",
                    MessageType.ERROR
                )
                return False

            self.logger.log(
                "AI core initialized successfully",
                MessageType.SYSTEM
            )
            return True

        except Exception as e:
            if self.logger:
                self.logger.log(
                    f"Core initialization failed: {e}",
                    MessageType.ERROR
                )
            else:
                print(f"[ERROR] Core initialization failed: {e}")
            traceback.print_exc()
            return False

    def check_system_health(self) -> bool:
        """
        Perform system health checks.

        Returns:
            True if all checks pass, False otherwise
        """
        print("\n[*] Running system health checks...\n")

        checks = {
            "Python Version": self._check_python_version,
            "Project Structure": self._check_project_structure,
            "Dependencies": self._check_dependencies,
            "Environment Variables": self._check_environment_variables,
            "Ollama Connection": self._check_ollama_connection,
        }

        passed = 0
        failed = 0

        for check_name, check_func in checks.items():
            try:
                result = check_func()
                status = "PASS" if result else "FAIL"
                print(f"  [{status}] {check_name}")
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  [ERROR] {check_name}: {e}")
                failed += 1

        print(f"\n[*] Health Check Summary: {passed} passed, {failed} failed\n")
        return failed == 0

    @staticmethod
    def _check_python_version() -> bool:
        """Check Python version compatibility."""
        return sys.version_info >= (3, 11)

    @staticmethod
    def _check_project_structure() -> bool:
        """Check that required project directories exist."""
        required = [
            PROJECT_ROOT / "BASE",
            PROJECT_ROOT / "personality",
            PROJECT_ROOT / "models",
        ]
        return all(d.exists() for d in required)

    @staticmethod
    def _check_dependencies() -> bool:
        """Check that critical dependencies are installed."""
        critical_packages = [
            "numpy",
            "PIL",
            "discord",
            "requests",
            "pygame",
            "dotenv",
        ]
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        return True

    @staticmethod
    def _check_environment_variables() -> bool:
        """Check that required environment variables are set or have defaults."""
        required_vars = {
            "OLLAMA_ENDPOINT": "http://localhost:11434",
        }
        for var, default in required_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
        return True

    @staticmethod
    def _check_ollama_connection() -> bool:
        """Check connection to Ollama API."""
        try:
            import requests
            endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            response = requests.get(
                f"{endpoint}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            # Ollama not running - this is expected if not started yet
            return False  # Don't fail health check for this, it's optional

    def run_gui(self) -> bool:
        """
        Start the GUI interface.

        Returns:
            True if GUI ran successfully, False otherwise
        """
        try:
            if not self.ai_core:
                print("[ERROR] AI core not initialized")
                return False

            print("[INFO] Initializing GUI...")
            import tkinter as tk
            from BASE.interface.gui_interface import OllamaGUI
            
            root = tk.Tk()
            self.gui = OllamaGUI(root)
            self.gui.setup_chat_with_history()
            root.protocol("WM_DELETE_WINDOW", self.gui.on_closing)

            self.logger.log(
                "GUI interface initialized",
                MessageType.SYSTEM
            )

            print("[INFO] Starting GUI event loop...")
            root.mainloop()
            return True

        except Exception as e:
            if self.logger:
                self.logger.log(
                    f"GUI failed: {e}",
                    MessageType.ERROR
                )
            else:
                print(f"[ERROR] GUI failed: {e}")
            traceback.print_exc()
            return False

    def run_cli(self) -> bool:
        """
        Start CLI mode for headless operation.

        Returns:
            True if CLI ran successfully, False otherwise
        """
        try:
            if not self.ai_core:
                print("[ERROR] AI core not initialized")
                return False

            print("[INFO] Starting CLI mode (type 'exit' to quit)...\n")

            while True:
                try:
                    user_input = input("You: ").strip()

                    if user_input.lower() in ("exit", "quit", "bye"):
                        print("[INFO] Shutting down...")
                        break

                    if not user_input:
                        continue

                    # Process message through AI core
                    self.ai_core.process_user_message(user_input)

                    # In CLI mode, just wait for cognitive loop to process
                    # The response will be logged/printed via the logger

                except KeyboardInterrupt:
                    print("\n[INFO] Interrupted by user")
                    break
                except Exception as e:
                    print(f"[ERROR] {e}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.log(
                    f"CLI failed: {e}",
                    MessageType.ERROR
                )
            else:
                print(f"[ERROR] CLI failed: {e}")
            traceback.print_exc()
            return False

    def shutdown(self) -> None:
        """Clean shutdown of all components."""
        print("\n[INFO] Initiating shutdown sequence...")

        try:
            if self.gui and hasattr(self.gui, 'on_closing'):
                try:
                    self.gui.on_closing()
                except Exception:
                    pass  # Already shutting down

            if self.ai_core and hasattr(self.ai_core, 'shutdown'):
                try:
                    self.ai_core.shutdown()
                except Exception:
                    pass  # Already shutting down

            if self.logger:
                self.logger.log(
                    "Application shutdown",
                    MessageType.SYSTEM
                )

            print("[INFO] Shutdown complete")

        except Exception as e:
            print(f"[ERROR] Error during shutdown: {e}")
            traceback.print_exc()

    def run(self) -> int:
        """
        Run the Anna AI application.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Setup environment
            if not self.setup_environment():
                return 1

            # Initialize core components
            if not self.initialize_core():
                return 1

            # Start appropriate interface
            if self.gui_enabled:
                success = self.run_gui()
            else:
                success = self.run_cli()

            return 0 if success else 1

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user")
            return 0
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            traceback.print_exc()
            return 1
        finally:
            self.shutdown()


def main() -> int:
    """
    Main entry point for Anna AI application.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Anna AI - Agentic AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with GUI
  python main.py --no-gui          # Start CLI only
  python main.py --check           # System health check
  python main.py -v --check        # Verbose health check
        """
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run in CLI mode without GUI"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Run system health checks and exit"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Anna AI 1.0.0"
    )

    args = parser.parse_args()

    # Create app instance
    app = AnnaAIApp(
        gui_enabled=not args.no_gui,
        verbose=args.verbose
    )

    # Run health checks if requested
    if args.check:
        return 0 if app.check_system_health() else 1

    # Otherwise run the app
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
