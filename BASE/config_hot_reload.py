"""
Configuration hot reload system for Anna AI.

Allows configuration changes without server restart.
Includes configuration versioning and change notification.
"""

import os
import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ConfigChange:
    """Record of a configuration change."""

    timestamp: str
    key: str
    old_value: Any
    new_value: Any
    changed_by: str = "api"


class ConfigHotReloader:
    """Manages hot reloading of configuration."""

    def __init__(self, config_file: Path):
        """
        Initialize hot reloader.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.config_version = 1
        self.change_history: List[ConfigChange] = []
        self.callbacks: List[Callable] = []
        self.lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_mtime = 0

        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            self.config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        with self.lock:
            return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        with self.lock:
            return dict(self.config)

    def set(self, key: str, value: Any, changed_by: str = "api") -> bool:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: New value
            changed_by: Who made the change

        Returns:
            True if changed, False if value is same
        """
        with self.lock:
            old_value = self.config.get(key)

            # Only record change if value is different
            if old_value == value:
                return False

            self.config[key] = value
            self.config_version += 1

            # Record change
            change = ConfigChange(
                timestamp=datetime.utcnow().isoformat() + "Z",
                key=key,
                old_value=old_value,
                new_value=value,
                changed_by=changed_by,
            )
            self.change_history.append(change)

            # Trigger callbacks
            self._trigger_callbacks(key, value, old_value)

            # Save to file
            self._save_config()

            return True

    def set_multiple(self, updates: Dict[str, Any], changed_by: str = "api") -> Dict[str, bool]:
        """
        Set multiple configuration values.

        Args:
            updates: Dictionary of key-value pairs
            changed_by: Who made the changes

        Returns:
            Dictionary of which keys were changed
        """
        results = {}
        for key, value in updates.items():
            results[key] = self.set(key, value, changed_by)

        return results

    def register_callback(self, callback: Callable) -> None:
        """
        Register callback for configuration changes.

        Callback signature: callback(key: str, new_value: Any, old_value: Any)

        Args:
            callback: Callback function
        """
        with self.lock:
            if callback not in self.callbacks:
                self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable) -> None:
        """
        Unregister callback.

        Args:
            callback: Callback function to remove
        """
        with self.lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)

    def _trigger_callbacks(
        self,
        key: str,
        new_value: Any,
        old_value: Any,
    ) -> None:
        """Trigger all registered callbacks."""
        for callback in self.callbacks:
            try:
                callback(key, new_value, old_value)
            except Exception as e:
                print(f"[ERROR] Callback error: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")

    def start_monitoring(self, check_interval: float = 5.0) -> None:
        """
        Start monitoring configuration file for changes.

        Args:
            check_interval: How often to check for changes (seconds)
        """
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(check_interval,),
            daemon=True,
        )
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring configuration file."""
        self.monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self, check_interval: float) -> None:
        """Monitor loop for file changes."""
        while self.monitoring:
            try:
                if self.config_file.exists():
                    current_mtime = os.path.getmtime(self.config_file)

                    if current_mtime > self.last_mtime:
                        self.last_mtime = current_mtime
                        self._handle_file_change()

                time.sleep(check_interval)

            except Exception as e:
                print(f"[ERROR] Monitor loop error: {e}")
                time.sleep(check_interval)

    def _handle_file_change(self) -> None:
        """Handle configuration file changes."""
        try:
            with open(self.config_file, "r") as f:
                new_config = json.load(f)

            with self.lock:
                # Detect changes
                for key, new_value in new_config.items():
                    old_value = self.config.get(key)

                    if old_value != new_value:
                        self.config[key] = new_value
                        self._trigger_callbacks(key, new_value, old_value)

                self.config_version += 1

        except Exception as e:
            print(f"[ERROR] Failed to handle file change: {e}")

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get change history.

        Args:
            limit: Maximum number of changes to return

        Returns:
            List of changes
        """
        with self.lock:
            history = [asdict(change) for change in self.change_history]

            if limit:
                return history[-limit:]

            return history

    def get_version(self) -> int:
        """Get current configuration version."""
        with self.lock:
            return self.config_version

    def rollback_to_version(self, version: int) -> bool:
        """
        Rollback to a specific configuration version.

        Args:
            version: Version to rollback to

        Returns:
            True if rollback successful, False otherwise
        """
        if version < 1 or version >= self.config_version:
            return False

        # For now, this is a placeholder
        # Full implementation would require storing versions
        print(f"[INFO] Rollback to version {version} not yet implemented")
        return False

    def validate(self) -> Dict[str, Any]:
        """
        Validate current configuration.

        Returns:
            Validation result with errors and warnings
        """
        from BASE.config_validator import ConfigSchema

        schema = ConfigSchema.get_schema()
        is_valid, errors = ConfigSchema.validate_config(self.config)

        return {
            "valid": is_valid,
            "errors": errors,
            "version": self.config_version,
        }

    def export(self, filepath: Path) -> bool:
        """
        Export configuration to file.

        Args:
            filepath: File to export to

        Returns:
            True if export successful, False otherwise
        """
        try:
            with self.lock:
                with open(filepath, "w") as f:
                    json.dump(
                        {
                            "version": self.config_version,
                            "config": self.config,
                            "exported_at": datetime.utcnow().isoformat() + "Z",
                        },
                        f,
                        indent=2,
                    )

            return True

        except Exception as e:
            print(f"[ERROR] Export failed: {e}")
            return False

    def import_config(self, filepath: Path) -> bool:
        """
        Import configuration from file.

        Args:
            filepath: File to import from

        Returns:
            True if import successful, False otherwise
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            if "config" in data:
                imported_config = data["config"]
            else:
                imported_config = data

            with self.lock:
                for key, value in imported_config.items():
                    old_value = self.config.get(key)
                    self.config[key] = value
                    self._trigger_callbacks(key, value, old_value)

                self.config_version += 1

            self._save_config()
            return True

        except Exception as e:
            print(f"[ERROR] Import failed: {e}")
            return False


class ConfigurationManager:
    """Centralized configuration management with hot reload."""

    _instance: Optional["ConfigurationManager"] = None

    def __new__(cls) -> "ConfigurationManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        """Initialize configuration manager."""
        if self._initialized:
            return

        project_root = Path(__file__).parent.parent
        self.config_file = project_root / "personality" / "config.json"

        self.reloader = ConfigHotReloader(self.config_file)
        self.reloader.start_monitoring(check_interval=2.0)

        self._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.reloader.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """Set configuration value."""
        return self.reloader.set(key, value, changed_by="api")

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self.reloader.get_all()

    def register_change_listener(self, callback: Callable) -> None:
        """Register listener for configuration changes."""
        self.reloader.register_callback(callback)

    def get_change_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent changes."""
        return self.reloader.get_history(limit)

    def get_version(self) -> int:
        """Get current version."""
        return self.reloader.get_version()

    def validate(self) -> Dict[str, Any]:
        """Validate configuration."""
        return self.reloader.validate()

    def export(self, filepath: Path) -> bool:
        """Export configuration."""
        return self.reloader.export(filepath)

    def shutdown(self) -> None:
        """Shutdown configuration manager."""
        self.reloader.stop_monitoring()
