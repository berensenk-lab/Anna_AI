"""
Message Queue System for Anna AI - Phase 3

Provides:
- Job queue management
- Worker process management
- Async task processing
- Job scheduling
- Retry logic
- Job status tracking
"""

import os
import logging
import json
import time
from typing import Any, Dict, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid

import redis
from rq import Queue, Worker, Job, Retry
from rq.job import JobStatus
from rq_scheduler import ScheduledJobQueue

logger = logging.getLogger(__name__)


class JobPriority(str, Enum):
    """Job priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QueueConfig:
    """Queue configuration."""

    def __init__(self):
        """Initialize queue configuration from environment."""
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.queue_names = {
            JobPriority.CRITICAL: "critical",
            JobPriority.HIGH: "high",
            JobPriority.MEDIUM: "default",
            JobPriority.LOW: "low",
        }
        self.job_timeout = int(os.getenv("JOB_TIMEOUT", "300"))
        self.result_ttl = int(os.getenv("RESULT_TTL", "3600"))
        self.failure_ttl = int(os.getenv("FAILURE_TTL", "86400"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "5"))

    def validate(self) -> bool:
        """Validate queue configuration."""
        if not self.redis_url:
            logger.error("REDIS_URL not set")
            return False

        return True


class QueueManager:
    """Manage message queues and jobs."""

    _instance: Optional["QueueManager"] = None

    def __new__(cls) -> "QueueManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        """Initialize queue manager."""
        if self._initialized:
            return

        self.config = QueueConfig()

        if not self.config.validate():
            raise ValueError("Invalid queue configuration")

        # Connect to Redis
        self.redis_conn = redis.from_url(self.config.redis_url, decode_responses=True)

        # Verify Redis connection
        try:
            self.redis_conn.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

        # Create queues
        self.queues = {
            priority: Queue(
                name=queue_name,
                connection=self.redis_conn,
                default_timeout=self.config.job_timeout,
            )
            for priority, queue_name in self.config.queue_names.items()
        }

        # Scheduled job queue
        self.scheduler = ScheduledJobQueue(connection=self.redis_conn)

        # Job tracking
        self.job_callbacks: Dict[str, List[Callable]] = {}

        logger.info("Queue manager initialized")

        self._initialized = True

    def enqueue_job(
        self,
        func: Callable,
        priority: JobPriority = JobPriority.MEDIUM,
        *args,
        **kwargs,
    ) -> Job:
        """
        Enqueue a job.

        Args:
            func: Function to execute
            priority: Job priority
            *args: Function positional arguments
            **kwargs: Function keyword arguments

        Returns:
            Job object
        """
        queue = self.queues[priority]

        retry_config = Retry(
            max=self.config.max_retries,
            interval=self.config.retry_delay,
        )

        job = queue.enqueue(
            func,
            *args,
            job_timeout=self.config.job_timeout,
            result_ttl=self.config.result_ttl,
            failure_ttl=self.config.failure_ttl,
            retry=retry_config,
            **kwargs,
        )

        logger.info(f"Job enqueued: {job.id} (priority: {priority})")
        return job

    def schedule_job(
        self,
        func: Callable,
        scheduled_time: datetime,
        *args,
        **kwargs,
    ) -> Job:
        """
        Schedule a job for later execution.

        Args:
            func: Function to execute
            scheduled_time: When to execute
            *args: Function positional arguments
            **kwargs: Function keyword arguments

        Returns:
            Job object
        """
        job = self.scheduler.schedule(
            scheduled_time=scheduled_time,
            func=func,
            args=args,
            kwargs=kwargs,
            timeout=self.config.job_timeout,
        )

        logger.info(f"Job scheduled: {job.id} for {scheduled_time}")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job object or None if not found
        """
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            return job
        except Exception as e:
            logger.warning(f"Job not found: {job_id}")
            return None

    def get_job_status(self, job_id: str) -> Optional[str]:
        """
        Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job status or None if not found
        """
        job = self.get_job(job_id)

        if not job:
            return None

        return job.get_status()

    def get_job_result(self, job_id: str) -> Any:
        """
        Get job result.

        Args:
            job_id: Job ID

        Returns:
            Job result or None
        """
        job = self.get_job(job_id)

        if not job:
            return None

        if job.is_finished:
            return job.result
        elif job.is_failed:
            return {"error": job.exc_info}
        else:
            return {"status": job.get_status()}

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled, False otherwise
        """
        try:
            job = self.get_job(job_id)

            if job:
                job.cancel()
                logger.info(f"Job cancelled: {job_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to cancel job: {e}")
            return False

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.

        Returns:
            Queue statistics
        """
        stats = {}

        for priority, queue in self.queues.items():
            stats[priority.value] = {
                "queued": len(queue),
                "started": len(queue.started_job_registry),
                "finished": len(queue.finished_job_registry),
                "failed": len(queue.failed_job_registry),
                "scheduled": len(queue.scheduled_job_registry),
            }

        return stats

    def get_failed_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently failed jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of failed job info
        """
        failed_jobs = []

        for queue in self.queues.values():
            for job_id in queue.failed_job_registry.get_job_ids()[:limit]:
                job = self.get_job(job_id)

                if job:
                    failed_jobs.append({
                        "id": job.id,
                        "name": job.func_name,
                        "status": job.get_status(),
                        "exception": job.exc_info,
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                    })

        return failed_jobs

    def health_check(self) -> bool:
        """
        Check queue system health.

        Returns:
            True if healthy, False otherwise
        """
        try:
            self.redis_conn.ping()
            return True
        except Exception as e:
            logger.error(f"Queue health check failed: {e}")
            return False

    def clear_all_queues(self) -> int:
        """
        Clear all queues (for testing/cleanup).

        Returns:
            Number of jobs cleared
        """
        total = 0

        for queue in self.queues.values():
            total += len(queue)
            queue.empty()

        logger.warning(f"Cleared {total} jobs from all queues")
        return total

    def start_workers(self, num_workers: int = 1, queues: Optional[List[str]] = None) -> List[Worker]:
        """
        Start worker processes.

        Args:
            num_workers: Number of workers to start
            queues: Queue names to process (default: all)

        Returns:
            List of worker objects
        """
        if queues is None:
            queues = list(self.config.queue_names.values())

        workers = []

        for i in range(num_workers):
            worker = Worker(
                queues,
                connection=self.redis_conn,
                name=f"worker-{i}-{uuid.uuid4()}",
                job_monitoring_interval=30,
            )

            workers.append(worker)
            logger.info(f"Worker started: {worker.name}")

        return workers

    def get_workers(self) -> List[Dict[str, Any]]:
        """
        Get information about active workers.

        Returns:
            List of worker info
        """
        workers_info = []

        for worker in Worker.all(connection=self.redis_conn):
            workers_info.append({
                "name": worker.name,
                "state": worker.get_state(),
                "current_job": worker.get_current_job().id if worker.get_current_job() else None,
                "birth_date": worker.birth_date.isoformat() if worker.birth_date else None,
                "successful_jobs": worker.successful_job_count,
                "failed_jobs": worker.failed_job_count,
            })

        return workers_info


# Convenience functions
def enqueue(
    func: Callable,
    priority: JobPriority = JobPriority.MEDIUM,
    *args,
    **kwargs,
) -> Job:
    """Enqueue a job."""
    manager = QueueManager()
    return manager.enqueue_job(func, priority, *args, **kwargs)


def schedule(
    func: Callable,
    scheduled_time: datetime,
    *args,
    **kwargs,
) -> Job:
    """Schedule a job."""
    manager = QueueManager()
    return manager.schedule_job(func, scheduled_time, *args, **kwargs)


def get_job_status(job_id: str) -> Optional[str]:
    """Get job status."""
    manager = QueueManager()
    return manager.get_job_status(job_id)


def get_job_result(job_id: str) -> Any:
    """Get job result."""
    manager = QueueManager()
    return manager.get_job_result(job_id)


def queue_stats() -> Dict[str, Any]:
    """Get queue statistics."""
    manager = QueueManager()
    return manager.get_queue_stats()


def start_workers(num_workers: int = 1) -> List[Worker]:
    """Start worker processes."""
    manager = QueueManager()
    return manager.start_workers(num_workers)
