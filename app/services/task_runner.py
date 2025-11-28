"""
Async Task Runner

Handles background execution of long-running debt review workflows.
Uses asyncio for concurrent execution and database for state persistence.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from app.core.database import db
from app.core.config import settings
from app.agents.state import create_initial_state, WorkflowState
from app.agents.workflow import get_workflow_app
from app.models.schemas import TaskStatus, TaskStage

logger = logging.getLogger(__name__)

# Thread pool for running sync operations
_executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_TASKS)

# Track running tasks
_running_tasks: Dict[str, asyncio.Task] = {}


class TaskRunner:
    """
    Manages background task execution.

    Responsibilities:
    - Start tasks in background
    - Track running tasks
    - Handle task cancellation
    - Persist state to database
    """

    @classmethod
    async def submit_task(
        cls,
        project_id: str,
        creditor_ids: List[str],
        processing_mode: str = "auto"
    ) -> str:
        """
        Submit a new task for processing.

        Creates task record in database and starts background execution.

        Args:
            project_id: Project ID
            creditor_ids: List of creditor IDs to process
            processing_mode: "auto", "serial", or "parallel"

        Returns:
            Task ID
        """
        # Get project and creditors from database
        project = db.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        creditors = []
        for cid in creditor_ids:
            creditor = db.get_creditor(cid)
            if creditor:
                creditors.append(creditor)

        if not creditors:
            raise ValueError("No valid creditors found")

        # Auto-determine processing mode
        if processing_mode == "auto":
            processing_mode = "parallel" if len(creditors) >= 2 else "serial"

        # Create task record in database
        task_data = {
            "project_id": project_id,
            "task_type": "full_review",
            "processing_mode": processing_mode,
            "status": TaskStatus.PENDING.value,
            "current_stage": TaskStage.INIT.value,
            "progress_percent": 0,
            "creditor_ids": creditor_ids,
            "creditors_total": len(creditors),
            "creditors_completed": 0,
            "config": {
                "bankruptcy_date": project.get("bankruptcy_date"),
                "interest_stop_date": project.get("interest_stop_date"),
                "debtor_name": project.get("debtor_name")
            }
        }

        task = db.create_task(task_data)
        task_id = task["id"]

        logger.info(f"Created task {task_id} for {len(creditors)} creditors")

        # Start background execution
        asyncio.create_task(cls._execute_task(task_id, project, creditors))

        return task_id

    @classmethod
    async def _execute_task(
        cls,
        task_id: str,
        project: Dict[str, Any],
        creditors: List[Dict[str, Any]]
    ):
        """
        Execute task in background.

        This is the main execution loop that runs the LangGraph workflow.
        """
        logger.info(f"Starting task execution: {task_id}")

        try:
            # Mark task as started
            db.start_task(task_id)

            # Add to running tasks
            _running_tasks[task_id] = asyncio.current_task()

            # Create initial workflow state
            project_config = {
                "bankruptcy_date": project.get("bankruptcy_date"),
                "interest_stop_date": project.get("interest_stop_date"),
                "debtor_name": project.get("debtor_name")
            }

            initial_state = create_initial_state(
                task_id=task_id,
                project_id=project["id"],
                project_config=project_config,
                creditors=creditors
            )

            # Get workflow app
            workflow = get_workflow_app()

            # Log start
            db.add_task_log(
                task_id=task_id,
                message=f"Starting workflow with {len(creditors)} creditors",
                level="info",
                stage="init"
            )

            # Execute workflow
            # Note: LangGraph's invoke is synchronous, so we run in executor
            final_state = await asyncio.get_event_loop().run_in_executor(
                _executor,
                lambda: workflow.invoke(initial_state)
            )

            # Check result
            if final_state.get("has_error"):
                db.complete_task(
                    task_id,
                    success=False,
                    error_message=final_state.get("error_message")
                )
                logger.error(f"Task {task_id} failed: {final_state.get('error_message')}")
            else:
                db.complete_task(task_id, success=True)
                logger.info(f"Task {task_id} completed successfully")

            # Log completion
            db.add_task_log(
                task_id=task_id,
                message="Workflow completed",
                level="info",
                stage="complete"
            )

        except asyncio.CancelledError:
            logger.warning(f"Task {task_id} was cancelled")
            db.update_task(task_id, {
                "status": TaskStatus.CANCELLED.value,
                "completed_at": datetime.utcnow().isoformat()
            })
            db.add_task_log(
                task_id=task_id,
                message="Task cancelled by user",
                level="warning"
            )

        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            logger.error(f"Task {task_id} error: {error_msg}\n{error_trace}")

            db.complete_task(
                task_id,
                success=False,
                error_message=error_msg
            )
            db.add_task_log(
                task_id=task_id,
                message=f"Task failed with error: {error_msg}",
                level="error",
                details={"traceback": error_trace}
            )

        finally:
            # Remove from running tasks
            _running_tasks.pop(task_id, None)

    @classmethod
    async def cancel_task(cls, task_id: str) -> bool:
        """
        Cancel a running task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled, False if not found/already done
        """
        task = _running_tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            logger.info(f"Cancelled task: {task_id}")
            return True
        return False

    @classmethod
    def get_task_status(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current task status from database.

        This is what the frontend polls to get progress updates.
        """
        task = db.get_task(task_id)
        if not task:
            return None

        return {
            "task_id": task_id,
            "status": task.get("status"),
            "current_stage": task.get("current_stage"),
            "progress_percent": task.get("progress_percent", 0),
            "creditors_total": task.get("creditors_total", 0),
            "creditors_completed": task.get("creditors_completed", 0),
            "current_creditor": task.get("current_creditor_name"),
            "started_at": task.get("started_at"),
            "completed_at": task.get("completed_at"),
            "error_message": task.get("error_message")
        }

    @classmethod
    def get_task_logs(cls, task_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent logs for a task.
        """
        return db.get_task_logs(task_id, limit=limit)

    @classmethod
    def is_task_running(cls, task_id: str) -> bool:
        """Check if a task is currently running."""
        return task_id in _running_tasks and not _running_tasks[task_id].done()

    @classmethod
    def get_running_tasks(cls) -> List[str]:
        """Get list of currently running task IDs."""
        return [
            task_id for task_id, task in _running_tasks.items()
            if not task.done()
        ]


# Convenience functions
async def submit_task(project_id: str, creditor_ids: List[str], **kwargs) -> str:
    """Submit a new task."""
    return await TaskRunner.submit_task(project_id, creditor_ids, **kwargs)


async def cancel_task(task_id: str) -> bool:
    """Cancel a running task."""
    return await TaskRunner.cancel_task(task_id)


def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status."""
    return TaskRunner.get_task_status(task_id)


def get_task_logs(task_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get task logs."""
    return TaskRunner.get_task_logs(task_id, limit)
