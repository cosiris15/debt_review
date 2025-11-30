"""
Supabase Database Client

Provides async database operations for the application.
"""

from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import re
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(str(value)))


def _async_wrap(result):
    """Wrap a synchronous result as an awaitable coroutine."""
    async def _awaitable():
        return result
    return _awaitable()


class Database:
    """Supabase database wrapper with typed operations."""

    _client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client."""
        if cls._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("Supabase credentials not configured")
            cls._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        return cls._client

    # ============== Projects ==============

    @classmethod
    def create_project(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project."""
        client = cls.get_client()
        result = client.table("projects").insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_project(cls, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        client = cls.get_client()
        result = client.table("projects").select("*").eq("id", project_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    def list_projects(cls) -> List[Dict[str, Any]]:
        """List all projects."""
        client = cls.get_client()
        result = client.table("projects").select("*").order("created_at", desc=True).execute()
        return result.data or []

    @classmethod
    def update_project(cls, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project."""
        client = cls.get_client()
        result = client.table("projects").update(data).eq("id", project_id).execute()
        return result.data[0] if result.data else None

    # ============== Creditors ==============

    @classmethod
    def create_creditor(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new creditor."""
        client = cls.get_client()
        result = client.table("creditors").insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_creditor(cls, creditor_id: str) -> Optional[Dict[str, Any]]:
        """Get creditor by ID."""
        client = cls.get_client()
        result = client.table("creditors").select("*").eq("id", creditor_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    def list_creditors(cls, project_id: str, batch_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """List creditors for a project."""
        client = cls.get_client()
        query = client.table("creditors").select("*").eq("project_id", project_id)
        if batch_number:
            query = query.eq("batch_number", batch_number)
        result = query.order("batch_number").order("creditor_number").execute()
        return result.data or []

    @classmethod
    async def update_creditor(cls, creditor_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a creditor."""
        if not is_valid_uuid(creditor_id):
            logger.debug(f"Skipping update_creditor for non-UUID creditor_id: {creditor_id}")
            return {"id": creditor_id, **data}
        client = cls.get_client()
        result = client.table("creditors").update(data).eq("id", creditor_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    async def update_creditor_status(
        cls,
        creditor_id: str,
        status: str,
        stage: Optional[str] = None,
        amounts: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Update creditor processing status."""
        if not is_valid_uuid(creditor_id):
            logger.debug(f"Skipping update_creditor_status for non-UUID creditor_id: {creditor_id}")
            return {"id": creditor_id, "status": status}
        data = {"status": status}
        if stage:
            data["current_stage"] = stage
        if amounts:
            data.update(amounts)
        return await cls.update_creditor(creditor_id, data)

    # ============== Tasks ==============

    @classmethod
    def create_task(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        client = cls.get_client()
        result = client.table("tasks").insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_task(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        client = cls.get_client()
        result = client.table("tasks").select("*").eq("id", task_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    def list_tasks(cls, project_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks with optional filters."""
        client = cls.get_client()
        query = client.table("tasks").select("*")
        if project_id:
            query = query.eq("project_id", project_id)
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).execute()
        return result.data or []

    @classmethod
    def update_task(cls, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        client = cls.get_client()
        result = client.table("tasks").update(data).eq("id", task_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    async def update_task_progress(
        cls,
        task_id: str,
        status: str,
        stage: str,
        progress: int,
        current_creditor_id: Optional[str] = None,
        current_creditor_name: Optional[str] = None,
        creditors_completed: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task progress (called frequently during execution).

        If task_id is not a valid UUID, skips database update (test mode).
        """
        # Skip database update for non-UUID task IDs (test mode)
        if not is_valid_uuid(task_id):
            logger.debug(f"Skipping DB update for non-UUID task_id: {task_id}")
            return {
                "id": task_id,
                "status": status,
                "current_stage": stage,
                "progress_percent": progress
            }

        data = {
            "status": status,
            "current_stage": stage,
            "progress_percent": progress
        }
        if current_creditor_id:
            data["current_creditor_id"] = current_creditor_id
        if current_creditor_name:
            data["current_creditor_name"] = current_creditor_name
        if creditors_completed is not None:
            data["creditors_completed"] = creditors_completed
        if error_message:
            data["error_message"] = error_message
        return cls.update_task(task_id, data)

    @classmethod
    async def start_task(cls, task_id: str) -> Dict[str, Any]:
        """Mark task as started."""
        if not is_valid_uuid(task_id):
            logger.debug(f"Skipping start_task for non-UUID task_id: {task_id}")
            return {"id": task_id, "status": "running"}
        return cls.update_task(task_id, {
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        })

    @classmethod
    async def complete_task(cls, task_id: str, success: bool, error_message: Optional[str] = None) -> Dict[str, Any]:
        """Mark task as completed or failed."""
        if not is_valid_uuid(task_id):
            logger.debug(f"Skipping complete_task for non-UUID task_id: {task_id}")
            return {"id": task_id, "status": "completed" if success else "failed"}
        data = {
            "status": "completed" if success else "failed",
            "progress_percent": 100 if success else None,
            "completed_at": datetime.utcnow().isoformat()
        }
        if error_message:
            data["error_message"] = error_message
        return cls.update_task(task_id, data)

    # ============== Task Logs ==============

    @classmethod
    async def add_task_log(
        cls,
        task_id: str,
        message: str,
        level: str = "info",
        stage: Optional[str] = None,
        creditor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a log entry for a task.

        If task_id is not a valid UUID, logs to console only (test mode).
        """
        # Skip database write for non-UUID task IDs (test mode)
        if not is_valid_uuid(task_id):
            logger.info(f"[{level.upper()}] {message}")
            return {"task_id": task_id, "message": message, "level": level}

        client = cls.get_client()
        data = {
            "task_id": task_id,
            "message": message,
            "level": level
        }
        if stage:
            data["stage"] = stage
        if creditor_id:
            data["creditor_id"] = creditor_id
        if details:
            data["details"] = details
        result = client.table("task_logs").insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_task_logs(cls, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for a task."""
        client = cls.get_client()
        result = (
            client.table("task_logs")
            .select("*")
            .eq("task_id", task_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    # ============== Reports ==============

    @classmethod
    async def create_report(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a report record.

        If creditor_id is not a valid UUID, skips database write (test mode).
        """
        creditor_id = data.get("creditor_id", "")
        if not is_valid_uuid(creditor_id):
            logger.debug(f"Skipping create_report for non-UUID creditor_id: {creditor_id}")
            return {"id": "test-report", **data}
        client = cls.get_client()
        result = client.table("reports").insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_report(cls, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report by ID."""
        client = cls.get_client()
        result = client.table("reports").select("*").eq("id", report_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    def list_reports(cls, creditor_id: str) -> List[Dict[str, Any]]:
        """List reports for a creditor."""
        client = cls.get_client()
        result = (
            client.table("reports")
            .select("*")
            .eq("creditor_id", creditor_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    # ============== Calculations ==============

    @classmethod
    async def save_calculation(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a calculation record.

        If creditor_id is not a valid UUID, skips database write (test mode).
        """
        creditor_id = data.get("creditor_id", "")
        if not is_valid_uuid(creditor_id):
            logger.debug(f"Skipping save_calculation for non-UUID creditor_id: {creditor_id}")
            return {"id": "test-calc", **data}
        client = cls.get_client()
        result = client.table("calculations").insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def list_calculations(cls, creditor_id: str) -> List[Dict[str, Any]]:
        """List calculations for a creditor."""
        client = cls.get_client()
        result = (
            client.table("calculations")
            .select("*")
            .eq("creditor_id", creditor_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []


# Convenience alias
db = Database
