"""
Performance monitoring and profiling for Anna AI.

Provides real-time performance metrics, profiling tools,
and performance analytics.
"""

import time
import psutil
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
from collections import deque
from pathlib import Path


@dataclass
class PerformanceMetric:
    """Individual performance metric."""

    timestamp: str
    name: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    status: str  # success, failed, timeout


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self, max_metrics: int = 1000):
        """
        Initialize performance monitor.

        Args:
            max_metrics: Maximum metrics to store in memory
        """
        self.max_metrics = max_metrics
        self.metrics = deque(maxlen=max_metrics)
        self.locks = threading.Lock()
        self.process = psutil.Process()

    def record_metric(
        self,
        name: str,
        duration_ms: float,
        status: str = "success",
    ) -> None:
        """
        Record a performance metric.

        Args:
            name: Metric name
            duration_ms: Operation duration in milliseconds
            status: Operation status
        """
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            # Non-blocking CPU sample to avoid adding latency to profiled calls.
            cpu_percent = self.process.cpu_percent(interval=None)

            metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat() + "Z",
                name=name,
                duration_ms=duration_ms,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                status=status,
            )

            with self.locks:
                self.metrics.append(metric)

        except Exception as e:
            print(f"[ERROR] Failed to record metric: {e}")

    def get_metrics_for_name(self, name: str) -> List[PerformanceMetric]:
        """
        Get all metrics for a specific name.

        Args:
            name: Metric name

        Returns:
            List of matching metrics
        """
        with self.locks:
            return [m for m in list(self.metrics) if m.name == name]

    def get_statistics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.

        Args:
            name: Optional metric name to filter by

        Returns:
            Dictionary with statistics
        """
        with self.locks:
            metrics = (
                [m for m in list(self.metrics) if m.name == name]
                if name
                else list(self.metrics)
            )

        if not metrics:
            return {"count": 0}

        durations = [m.duration_ms for m in metrics]
        memory_values = [m.memory_mb for m in metrics]
        cpu_values = [m.cpu_percent for m in metrics]

        success_count = len([m for m in metrics if m.status == "success"])
        failed_count = len([m for m in metrics if m.status == "failed"])
        timeout_count = len([m for m in metrics if m.status == "timeout"])

        return {
            "count": len(metrics),
            "success": success_count,
            "failed": failed_count,
            "timeout": timeout_count,
            "duration_ms": {
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / len(durations),
                "total": sum(durations),
            },
            "memory_mb": {
                "min": min(memory_values),
                "max": max(memory_values),
                "avg": sum(memory_values) / len(memory_values),
            },
            "cpu_percent": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": sum(cpu_values) / len(cpu_values),
            },
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Get overall performance summary.

        Returns:
            Summary statistics
        """
        with self.locks:
            snapshot = list(self.metrics)

        if not snapshot:
                return {"status": "no metrics"}

        # Group by name from one snapshot to avoid repeated lock/filter passes.
        by_name = defaultdict(list)
        for metric in snapshot:
            by_name[metric.name].append(metric)

        summary = {}
        for name, metrics_list in by_name.items():
            durations = [m.duration_ms for m in metrics_list]
            memory_values = [m.memory_mb for m in metrics_list]
            cpu_values = [m.cpu_percent for m in metrics_list]
            success_count = len([m for m in metrics_list if m.status == "success"])
            failed_count = len([m for m in metrics_list if m.status == "failed"])
            timeout_count = len([m for m in metrics_list if m.status == "timeout"])

            summary[name] = {
                "count": len(metrics_list),
                "success": success_count,
                "failed": failed_count,
                "timeout": timeout_count,
                "duration_ms": {
                    "min": min(durations),
                    "max": max(durations),
                    "avg": sum(durations) / len(durations),
                    "total": sum(durations),
                },
                "memory_mb": {
                    "min": min(memory_values),
                    "max": max(memory_values),
                    "avg": sum(memory_values) / len(memory_values),
                },
                "cpu_percent": {
                    "min": min(cpu_values),
                    "max": max(cpu_values),
                    "avg": sum(cpu_values) / len(cpu_values),
                },
            }

        return summary

    def export_metrics(self, filepath: Path) -> bool:
        """
        Export metrics to JSON file.

        Args:
            filepath: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            import json

            filepath.parent.mkdir(parents=True, exist_ok=True)

            with self.locks:
                metrics_data = [asdict(m) for m in list(self.metrics)]

            with open(filepath, "w") as f:
                json.dump(metrics_data, f, indent=2)

            return True

        except Exception as e:
            print(f"[ERROR] Failed to export metrics: {e}")
            return False


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(
        self,
        name: str,
        monitor: Optional[PerformanceMonitor] = None,
    ):
        """
        Initialize timer.

        Args:
            name: Operation name
            monitor: Optional PerformanceMonitor instance
        """
        self.name = name
        self.monitor = monitor
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self) -> "PerformanceTimer":
        """Enter context."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and record metric."""
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000

        if exc_type is not None:
            status = "failed"
            if exc_type.__name__ == "TimeoutError":
                status = "timeout"
        else:
            status = "success"

        if self.monitor:
            self.monitor.record_metric(self.name, duration_ms, status)

    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0

        return (self.end_time - self.start_time) * 1000


class MemoryProfiler:
    """Track memory usage over time."""

    def __init__(self, sample_interval: float = 1.0):
        """
        Initialize memory profiler.

        Args:
            sample_interval: Sampling interval in seconds
        """
        self.sample_interval = sample_interval
        self.samples: List[Dict[str, Any]] = []
        self.process = psutil.Process()
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start memory profiling."""
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._sample_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop memory profiling."""
        self.is_running = False

        if self.thread:
            self.thread.join(timeout=5)

    def _sample_loop(self) -> None:
        """Memory sampling loop."""
        while self.is_running:
            try:
                memory_info = self.process.memory_info()
                self.samples.append(
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "rss_mb": memory_info.rss / 1024 / 1024,
                        "vms_mb": memory_info.vms / 1024 / 1024,
                    }
                )

                time.sleep(self.sample_interval)

            except Exception as e:
                print(f"[ERROR] Memory sampling error: {e}")

    def get_peak_memory(self) -> float:
        """Get peak memory usage in MB."""
        if not self.samples:
            return 0.0

        return max(s["rss_mb"] for s in self.samples)

    def get_average_memory(self) -> float:
        """Get average memory usage in MB."""
        if not self.samples:
            return 0.0

        return sum(s["rss_mb"] for s in self.samples) / len(self.samples)

    def get_memory_trend(self) -> Dict[str, Any]:
        """Get memory trend data."""
        if not self.samples:
            return {"status": "no samples"}

        return {
            "samples": len(self.samples),
            "peak_mb": self.get_peak_memory(),
            "average_mb": self.get_average_memory(),
            "current_mb": self.samples[-1]["rss_mb"] if self.samples else 0.0,
        }


class CPUProfiler:
    """Track CPU usage over time."""

    def __init__(self, sample_interval: float = 1.0):
        """
        Initialize CPU profiler.

        Args:
            sample_interval: Sampling interval in seconds
        """
        self.sample_interval = sample_interval
        self.samples: List[Dict[str, Any]] = []
        self.process = psutil.Process()
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start CPU profiling."""
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._sample_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop CPU profiling."""
        self.is_running = False

        if self.thread:
            self.thread.join(timeout=5)

    def _sample_loop(self) -> None:
        """CPU sampling loop."""
        while self.is_running:
            try:
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.samples.append(
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "cpu_percent": cpu_percent,
                    }
                )

                time.sleep(self.sample_interval)

            except Exception as e:
                print(f"[ERROR] CPU sampling error: {e}")

    def get_peak_cpu(self) -> float:
        """Get peak CPU usage."""
        if not self.samples:
            return 0.0

        return max(s["cpu_percent"] for s in self.samples)

    def get_average_cpu(self) -> float:
        """Get average CPU usage."""
        if not self.samples:
            return 0.0

        return sum(s["cpu_percent"] for s in self.samples) / len(self.samples)

    def get_cpu_trend(self) -> Dict[str, Any]:
        """Get CPU trend data."""
        if not self.samples:
            return {"status": "no samples"}

        return {
            "samples": len(self.samples),
            "peak_percent": self.get_peak_cpu(),
            "average_percent": self.get_average_cpu(),
            "current_percent": self.samples[-1]["cpu_percent"] if self.samples else 0.0,
        }
