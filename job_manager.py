"""
Simple job manager for tracking backtest progress.
In production, consider using Celery, RQ, or similar task queue.
"""
import uuid
from datetime import datetime
from typing import Dict, Optional
from enum import Enum
import threading

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Job:
    def __init__(self, job_id: str, job_type: str, params: dict):
        self.job_id = job_id
        self.job_type = job_type
        self.params = params
        self.status = JobStatus.PENDING
        self.progress = 0.0  # 0.0 to 1.0
        self.current_step = ""
        self.total_steps = 0
        self.current_step_num = 0
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class JobManager:
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create_job(self, job_type: str, params: dict) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        job = Job(job_id, job_type, params)
        with self._lock:
            self._jobs[job_id] = job
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        with self._lock:
            return self._jobs.get(job_id)

    def update_progress(self, job_id: str, progress: float, current_step: str = "", 
                       current_step_num: int = 0, total_steps: int = 0):
        """Update job progress"""
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.progress = max(0.0, min(1.0, progress))
                job.current_step = current_step
                job.current_step_num = current_step_num
                job.total_steps = total_steps
                job.updated_at = datetime.now()

    def set_status(self, job_id: str, status: JobStatus, result=None, error=None):
        """Set job status"""
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = status
                job.result = result
                job.error = error
                job.updated_at = datetime.now()
                if status == JobStatus.COMPLETED:
                    job.progress = 1.0
                elif status == JobStatus.FAILED:
                    job.progress = 0.0

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours"""
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        with self._lock:
            to_remove = [
                job_id for job_id, job in self._jobs.items()
                if job.updated_at.timestamp() < cutoff
            ]
            for job_id in to_remove:
                del self._jobs[job_id]
        return len(to_remove)

# Global job manager instance
_job_manager = None

def get_job_manager() -> JobManager:
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager



