"""
Configuration validation system for Anna AI.

Provides schema validation, environment variable checking,
and configuration integrity verification.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum


class ConfigKey(Enum):
    """Configuration keys and their specifications."""

    # Model configuration
    MODEL = ("string", "mistral", "LLM model to use")
    THINKING_MODEL = ("string", "mistral", "Model for internal thinking")
    EMBEDDING_MODEL = ("string", "nomic-embed-text", "Embedding model for memory")

    # API configuration
    OLLAMA_ENDPOINT = ("url", "http://localhost:11434", "Ollama API endpoint")
    OLLAMA_TIMEOUT = ("int", 600, "API timeout in seconds")

    # Temperature settings
    TEMPERATURE_ACTION = ("float", 0.2, "Action generation temperature (0-1)")
    TEMPERATURE_COGNITIVE = ("float", 0.6, "Cognitive processing temperature (0-1)")
    TEMPERATURE_RESPONSE = ("float", 0.9, "Response generation temperature (0-1)")

    # Memory configuration
    MAX_CONTEXT = ("int", 25, "Maximum context entries")
    MEMORY_SEARCH_RESULTS = ("int", 2, "Memory search results (1-5)")

    # Logging
    LOG_LEVEL = ("choice", "INFO", "Logging level (DEBUG/INFO/WARNING/ERROR)")
    DEBUG = ("bool", False, "Enable debug mode")

    # Audio configuration
    MICROPHONE_DEVICE = ("int", 0, "Microphone device index")
    SPEAKER_DEVICE = ("int", 0, "Speaker device index")

    # TTS configuration
    DEFAULT_TTS = ("choice", "xtts", "TTS backend (xtts/pyttsx3/gpt_sovits)")
    WHISPER_MODEL = ("choice", "base", "Whisper model size")

    # Performance
    THINKING_PACE = ("float", 0.85, "Thinking pace (lower=faster)")
    GPU_MEMORY_OPTIMIZE = ("bool", True, "Enable GPU memory optimization")

    # Deployment
    ENVIRONMENT = ("choice", "development", "Environment (development/staging/production)")


class ConfigValidator:
    """Validates configuration files and environment variables."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Run validations
        self._validate_env_file()
        self._validate_config_json()
        self._validate_environment_variables()
        self._validate_required_directories()
        self._validate_breaking_changes()

        is_valid = len(self.errors) == 0

        return is_valid, self.errors, self.warnings

    def _validate_env_file(self) -> None:
        """Validate .env file format and content."""
        env_file = self.project_root / ".env"

        if not env_file.exists():
            self.warnings.append(f".env file not found at {env_file}")
            return

        try:
            with open(env_file, "r") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Check format
                if "=" not in line:
                    self.errors.append(f".env:{line_num} Invalid format (missing '=')")
                    continue

                key, value = line.split("=", 1)

                # Validate sensitive keys
                if key in ["DISCORD_BOT_TOKEN", "TWITCH_OAUTH_TOKEN", "YOUTUBE_API_KEY"]:
                    if not value or value.isspace():
                        self.warnings.append(f".env:{line_num} {key} is not set")
                    elif len(value) < 5:
                        self.errors.append(f".env:{line_num} {key} appears to be invalid")

        except Exception as e:
            self.errors.append(f"Error reading .env file: {e}")

    def _validate_config_json(self) -> None:
        """Validate config.json format and schema."""
        config_file = self.project_root / "personality" / "config.json"

        if not config_file.exists():
            self.warnings.append(f"config.json not found at {config_file}")
            return

        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)

            # Validate required keys
            required_keys = ["bot_name", "bot_emotion"]

            for key in required_keys:
                if key not in config_data:
                    self.errors.append(f"config.json missing required key: {key}")

        except json.JSONDecodeError as e:
            self.errors.append(f"config.json JSON decode error: {e}")
        except Exception as e:
            self.errors.append(f"Error reading config.json: {e}")

    def _validate_environment_variables(self) -> None:
        """Validate environment variables."""
        required_vars = {
            "OLLAMA_ENDPOINT": "http://localhost:11434",
        }

        for var, default in required_vars.items():
            value = os.getenv(var)

            if not value:
                self.warnings.append(f"Environment variable {var} not set (using default: {default})")
            else:
                # Validate format for specific variables
                if var == "OLLAMA_ENDPOINT":
                    if not value.startswith(("http://", "https://")):
                        self.errors.append(f"{var} must be a valid URL")

    def _validate_required_directories(self) -> None:
        """Validate required directories exist."""
        required_dirs = [
            "BASE",
            "personality",
            "models",
            "logs",
        ]

        for directory in required_dirs:
            dir_path = self.project_root / directory

            if not dir_path.exists():
                self.warnings.append(f"Missing directory: {directory}")

    def _validate_breaking_changes(self) -> None:
        """Check for breaking changes in configuration."""
        # Check for removed configuration keys
        deprecated_keys = []

        for key in deprecated_keys:
            if os.getenv(key):
                self.warnings.append(
                    f"Deprecated environment variable {key} is set but no longer used"
                )

    def validate_model_names(self) -> Tuple[bool, List[str]]:
        """
        Validate that configured models are available.

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        try:
            import requests

            endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            response = requests.get(f"{endpoint}/api/tags", timeout=5)

            if response.status_code != 200:
                return False, ["Cannot connect to Ollama API"]

            available_models = [m["name"] for m in response.json().get("models", [])]

            if not available_models:
                errors.append("No models available in Ollama")
                return False, errors

        except Exception as e:
            errors.append(f"Cannot validate models: {e}")
            return False, errors

        return True, errors

    def generate_report(self) -> str:
        """
        Generate a validation report.

        Returns:
            Formatted validation report
        """
        report = "Configuration Validation Report\n"
        report += "=" * 50 + "\n\n"

        is_valid, errors, warnings = self.validate_all()

        if is_valid and not warnings:
            report += "✓ All validations passed!\n"
        elif is_valid:
            report += "✓ Configuration is valid\n\n"

        if errors:
            report += f"ERRORS ({len(errors)}):\n"
            for error in errors:
                report += f"  ✗ {error}\n"
            report += "\n"

        if warnings:
            report += f"WARNINGS ({len(warnings)}):\n"
            for warning in warnings:
                report += f"  ⚠ {warning}\n"
            report += "\n"

        return report


class ConfigSchema:
    """Defines the configuration schema."""

    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """
        Get the configuration schema.

        Returns:
            Schema definition
        """
        return {
            "model": {
                "type": "string",
                "default": "mistral",
                "description": "LLM model name",
            },
            "thinking_model": {
                "type": "string",
                "default": "mistral",
                "description": "Model for internal thinking",
            },
            "embedding_model": {
                "type": "string",
                "default": "nomic-embed-text",
                "description": "Embedding model for memory",
            },
            "ollama_endpoint": {
                "type": "url",
                "default": "http://localhost:11434",
                "description": "Ollama API endpoint",
            },
            "ollama_timeout": {
                "type": "integer",
                "default": 600,
                "min": 10,
                "max": 3600,
                "description": "API timeout in seconds",
            },
            "temperature": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "float",
                        "default": 0.2,
                        "min": 0.0,
                        "max": 1.0,
                    },
                    "cognitive": {
                        "type": "float",
                        "default": 0.6,
                        "min": 0.0,
                        "max": 1.0,
                    },
                    "response": {
                        "type": "float",
                        "default": 0.9,
                        "min": 0.0,
                        "max": 1.0,
                    },
                },
            },
            "memory": {
                "type": "object",
                "properties": {
                    "max_context": {
                        "type": "integer",
                        "default": 25,
                        "min": 5,
                        "max": 100,
                    },
                    "search_results": {
                        "type": "integer",
                        "default": 2,
                        "min": 1,
                        "max": 5,
                    },
                },
            },
            "logging": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "default": "INFO",
                        "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    },
                    "debug": {
                        "type": "boolean",
                        "default": False,
                    },
                },
            },
        }

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, errors)
        """
        schema = ConfigSchema.get_schema()
        errors = []

        for key, spec in schema.items():
            if key not in config:
                continue

            value = config[key]

            # Type validation
            if spec.get("type") == "integer":
                if not isinstance(value, int):
                    errors.append(f"{key} must be an integer")
                elif "min" in spec and value < spec["min"]:
                    errors.append(f"{key} must be >= {spec['min']}")
                elif "max" in spec and value > spec["max"]:
                    errors.append(f"{key} must be <= {spec['max']}")

            elif spec.get("type") == "float":
                if not isinstance(value, (int, float)):
                    errors.append(f"{key} must be a float")
                elif "min" in spec and value < spec["min"]:
                    errors.append(f"{key} must be >= {spec['min']}")
                elif "max" in spec and value > spec["max"]:
                    errors.append(f"{key} must be <= {spec['max']}")

            elif spec.get("type") == "string":
                if not isinstance(value, str):
                    errors.append(f"{key} must be a string")

            elif spec.get("type") == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"{key} must be a boolean")

            # Enum validation
            if "enum" in spec:
                if value not in spec["enum"]:
                    errors.append(f"{key} must be one of {spec['enum']}")

        return len(errors) == 0, errors
