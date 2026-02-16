"""
Structured JSON logging for Anna AI.

Provides JSON-formatted logs suitable for log aggregation systems
(ELK, Splunk, CloudWatch, etc.)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger


class StructuredLogFormatter(jsonlogger.JsonFormatter):
    """Custom JSON log formatter for Anna AI."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_format: str,
    ) -> None:
        """
        Add custom fields to log record.

        Args:
            log_record: Log record dictionary
            record: Python logging record
            message_format: Message format string
        """
        super().add_fields(log_record, record, message_format)

        # Add custom fields
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add thread info
        log_record["thread"] = record.thread
        log_record["thread_name"] = record.threadName

        # Add process info
        log_record["process"] = record.process

        # Remove duplicate fields added by default
        log_record.pop("asctime", None)


class StructuredLogger:
    """Structured logging manager for Anna AI."""

    def __init__(
        self,
        name: str,
        log_file: Optional[Path] = None,
        level: str = "INFO",
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            log_file: Optional log file path
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))

        # Console handler (JSON)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            StructuredLogFormatter(
                fmt='{"message": "%(message)s"}',
            )
        )
        self.logger.addHandler(console_handler)

        # File handler (JSON)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                StructuredLogFormatter(
                    fmt='{"message": "%(message)s"}',
                )
            )
            self.logger.addHandler(file_handler)

    def log(
        self,
        message: str,
        level: str = "INFO",
        **kwargs: Any,
    ) -> None:
        """
        Log a message with structured data.

        Args:
            message: Log message
            level: Log level
            **kwargs: Additional structured fields
        """
        # Build log entry
        log_entry = {
            "message": message,
            **kwargs,
        }

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_entry))

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.log(message, "INFO", **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.log(message, "WARNING", **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.log(message, "ERROR", **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.log(message, "DEBUG", **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.log(message, "CRITICAL", **kwargs)


class LogManager:
    """Central log management for Anna AI."""

    _instance: Optional["LogManager"] = None

    def __new__(cls) -> "LogManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        """Initialize log manager."""
        if self._initialized:
            return

        self.project_root = Path(__file__).parent.parent
        self.log_dir = self.project_root / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup main application logger
        self.app_logger = StructuredLogger(
            "anna_ai",
            log_file=self.log_dir / "app.json",
            level="INFO",
        )

        # Setup API server logger
        self.api_logger = StructuredLogger(
            "api_server",
            log_file=self.log_dir / "api.json",
            level="INFO",
        )

        # Setup tool execution logger
        self.tool_logger = StructuredLogger(
            "tools",
            log_file=self.log_dir / "tools.json",
            level="INFO",
        )

        # Setup memory logger
        self.memory_logger = StructuredLogger(
            "memory",
            log_file=self.log_dir / "memory.json",
            level="INFO",
        )

        # Setup error logger
        self.error_logger = StructuredLogger(
            "errors",
            log_file=self.log_dir / "errors.json",
            level="ERROR",
        )

        self._initialized = True

    def get_logger(self, name: str) -> StructuredLogger:
        """
        Get or create a logger.

        Args:
            name: Logger name

        Returns:
            StructuredLogger instance
        """
        log_file = self.log_dir / f"{name}.json"
        return StructuredLogger(
            name,
            log_file=log_file,
            level="INFO",
        )

    def log_event(
        self,
        category: str,
        message: str,
        level: str = "INFO",
        **kwargs: Any,
    ) -> None:
        """
        Log a structured event.

        Args:
            category: Event category (app, api, tool, memory, error)
            message: Event message
            level: Log level
            **kwargs: Additional fields
        """
        logger = getattr(self, f"{category}_logger", self.app_logger)
        logger.log(message, level, category=category, **kwargs)

    def log_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        **kwargs: Any,
    ) -> None:
        """
        Log API request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional fields
        """
        self.api_logger.info(
            f"API request: {method} {endpoint}",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_tool_execution(
        self,
        tool_name: str,
        command: str,
        status: str,
        duration_ms: float,
        **kwargs: Any,
    ) -> None:
        """
        Log tool execution.

        Args:
            tool_name: Name of tool
            command: Tool command
            status: Execution status (success/failed/timeout)
            duration_ms: Execution duration in milliseconds
            **kwargs: Additional fields
        """
        self.tool_logger.info(
            f"Tool execution: {tool_name}",
            tool_name=tool_name,
            command=command,
            status=status,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_memory_operation(
        self,
        operation: str,
        tier: str,
        size: int,
        duration_ms: float,
        **kwargs: Any,
    ) -> None:
        """
        Log memory operation.

        Args:
            operation: Operation type (search/store/update/delete)
            tier: Memory tier (short/medium/long/base)
            size: Number of items
            duration_ms: Operation duration in milliseconds
            **kwargs: Additional fields
        """
        self.memory_logger.info(
            f"Memory operation: {operation}",
            operation=operation,
            tier=tier,
            size=size,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_error(
        self,
        error_type: str,
        message: str,
        traceback: str,
        **kwargs: Any,
    ) -> None:
        """
        Log error.

        Args:
            error_type: Error type
            message: Error message
            traceback: Error traceback
            **kwargs: Additional fields
        """
        self.error_logger.error(
            f"Error: {error_type}",
            error_type=error_type,
            message=message,
            traceback=traceback,
            **kwargs,
        )
