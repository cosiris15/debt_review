"""
FastAPI Routes

API endpoints for the debt review system.
Implements async task submission + polling pattern.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.schemas import (
    ProjectCreate, ProjectResponse,
    CreditorCreate, CreditorResponse,
    TaskCreate, TaskResponse, TaskSubmitResponse, TaskProgress,
    InterestCalculationRequest, InterestCalculationResponse,
    TaskStatus, TaskStage
)
from app.core.database import db
from app.core.auth import get_current_user, get_optional_user, AuthenticatedUser
from app.services.task_runner import (
    submit_task, cancel_task, get_task_status, get_task_logs, TaskRunner
)
from app.tools.calculator import calculate_interest

# Create routers
projects_router = APIRouter(prefix="/projects", tags=["Projects"])
creditors_router = APIRouter(prefix="/creditors", tags=["Creditors"])
tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])
tools_router = APIRouter(prefix="/tools", tags=["Tools"])


# ============== Projects ==============

@projects_router.post("", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Create a new bankruptcy project. Requires authentication."""
    # Calculate interest stop date (bankruptcy date - 1 day)
    try:
        bankruptcy_dt = datetime.strptime(project.bankruptcy_date, "%Y-%m-%d")
        interest_stop_dt = bankruptcy_dt - timedelta(days=1)
        interest_stop_date = interest_stop_dt.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

    data = {
        "name": project.name,
        "debtor_name": project.debtor_name,
        "bankruptcy_date": project.bankruptcy_date,
        "interest_stop_date": interest_stop_date,
        "description": project.description
    }

    result = db.create_project(data)
    if not result:
        raise HTTPException(500, "Failed to create project")

    return ProjectResponse(
        id=result["id"],
        name=result["name"],
        debtor_name=result["debtor_name"],
        bankruptcy_date=result["bankruptcy_date"],
        interest_stop_date=result["interest_stop_date"],
        description=result.get("description"),
        created_at=result["created_at"],
        updated_at=result["updated_at"]
    )


@projects_router.get("", response_model=List[ProjectResponse])
async def list_projects(user: AuthenticatedUser = Depends(get_current_user)):
    """List all projects. Requires authentication."""
    projects = db.list_projects()
    return [
        ProjectResponse(
            id=p["id"],
            name=p["name"],
            debtor_name=p["debtor_name"],
            bankruptcy_date=p["bankruptcy_date"],
            interest_stop_date=p["interest_stop_date"],
            description=p.get("description"),
            created_at=p["created_at"],
            updated_at=p["updated_at"]
        )
        for p in projects
    ]


@projects_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get a project by ID. Requires authentication."""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # Count creditors
    creditors = db.list_creditors(project_id)
    completed = sum(1 for c in creditors if c.get("status") == "completed")

    return ProjectResponse(
        id=project["id"],
        name=project["name"],
        debtor_name=project["debtor_name"],
        bankruptcy_date=project["bankruptcy_date"],
        interest_stop_date=project["interest_stop_date"],
        description=project.get("description"),
        created_at=project["created_at"],
        updated_at=project["updated_at"],
        total_creditors=len(creditors),
        completed_creditors=completed
    )


# ============== Creditors ==============

@creditors_router.post("", response_model=CreditorResponse)
async def create_creditor(
    creditor: CreditorCreate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Add a creditor to a project. Requires authentication."""
    # Verify project exists
    project = db.get_project(creditor.project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    data = {
        "project_id": creditor.project_id,
        "batch_number": creditor.batch_number,
        "creditor_number": creditor.creditor_number,
        "creditor_name": creditor.creditor_name,
        "declared_total": creditor.declared_amount,
        "materials_path": creditor.materials_path,
        "status": "not_started"
    }

    result = db.create_creditor(data)
    if not result:
        raise HTTPException(500, "Failed to create creditor")

    return CreditorResponse(
        id=result["id"],
        project_id=result["project_id"],
        batch_number=result["batch_number"],
        creditor_number=result["creditor_number"],
        creditor_name=result["creditor_name"],
        declared_amount=result.get("declared_total"),
        confirmed_amount=result.get("confirmed_total"),
        status=result["status"],
        current_stage=result.get("current_stage"),
        materials_path=result.get("materials_path"),
        output_path=result.get("output_path"),
        created_at=result["created_at"],
        updated_at=result["updated_at"]
    )


@creditors_router.get("/project/{project_id}", response_model=List[CreditorResponse])
async def list_creditors(
    project_id: str,
    batch_number: Optional[int] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """List creditors for a project. Requires authentication."""
    creditors = db.list_creditors(project_id, batch_number)
    return [
        CreditorResponse(
            id=c["id"],
            project_id=c["project_id"],
            batch_number=c["batch_number"],
            creditor_number=c["creditor_number"],
            creditor_name=c["creditor_name"],
            declared_amount=c.get("declared_total"),
            confirmed_amount=c.get("confirmed_total"),
            status=c["status"],
            current_stage=c.get("current_stage"),
            materials_path=c.get("materials_path"),
            output_path=c.get("output_path"),
            created_at=c["created_at"],
            updated_at=c["updated_at"]
        )
        for c in creditors
    ]


@creditors_router.get("/{creditor_id}", response_model=CreditorResponse)
async def get_creditor(
    creditor_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get a creditor by ID. Requires authentication."""
    creditor = db.get_creditor(creditor_id)
    if not creditor:
        raise HTTPException(404, "Creditor not found")

    return CreditorResponse(
        id=creditor["id"],
        project_id=creditor["project_id"],
        batch_number=creditor["batch_number"],
        creditor_number=creditor["creditor_number"],
        creditor_name=creditor["creditor_name"],
        declared_amount=creditor.get("declared_total"),
        confirmed_amount=creditor.get("confirmed_total"),
        status=creditor["status"],
        current_stage=creditor.get("current_stage"),
        materials_path=creditor.get("materials_path"),
        output_path=creditor.get("output_path"),
        created_at=creditor["created_at"],
        updated_at=creditor["updated_at"]
    )


# ============== Tasks ==============

@tasks_router.post("", response_model=TaskSubmitResponse)
async def submit_review_task(
    task: TaskCreate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Submit a debt review task for background processing. Requires authentication.

    Returns immediately with task ID. Poll /tasks/{task_id}/status for progress.
    """
    try:
        task_id = await submit_task(
            project_id=task.project_id,
            creditor_ids=task.creditor_ids,
            processing_mode=task.processing_mode
        )

        return TaskSubmitResponse(
            task_id=task_id,
            message=f"Task submitted for {len(task.creditor_ids)} creditors",
            status=TaskStatus.PENDING
        )

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to submit task: {str(e)}")


@tasks_router.get("/{task_id}/status", response_model=TaskProgress)
async def get_task_progress(
    task_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Get current task progress. Requires authentication.

    Frontend polls this endpoint to track progress.
    """
    status = get_task_status(task_id)
    if not status:
        raise HTTPException(404, "Task not found")

    # Get recent logs
    logs = get_task_logs(task_id, limit=10)
    log_messages = [log["message"] for log in logs]

    return TaskProgress(
        task_id=task_id,
        status=status["status"],
        current_stage=status["current_stage"],
        progress_percent=status["progress_percent"],
        current_creditor=status.get("current_creditor"),
        stage_details={
            "creditors_total": status.get("creditors_total"),
            "creditors_completed": status.get("creditors_completed")
        },
        logs=log_messages
    )


@tasks_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get full task details. Requires authentication."""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    return TaskResponse(
        id=task["id"],
        project_id=task["project_id"],
        status=task["status"],
        current_stage=task["current_stage"],
        progress_percent=task.get("progress_percent", 0),
        creditors_total=task.get("creditors_total", 0),
        creditors_completed=task.get("creditors_completed", 0),
        started_at=task.get("started_at"),
        completed_at=task.get("completed_at"),
        error_message=task.get("error_message"),
        created_at=task["created_at"]
    )


@tasks_router.post("/{task_id}/cancel")
async def cancel_review_task(
    task_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Cancel a running task. Requires authentication."""
    success = await cancel_task(task_id)
    if not success:
        raise HTTPException(400, "Task not running or already completed")

    return {"message": "Task cancellation requested", "task_id": task_id}


@tasks_router.get("/{task_id}/logs")
async def get_task_log_entries(
    task_id: str,
    limit: int = 100,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get detailed logs for a task. Requires authentication."""
    logs = get_task_logs(task_id, limit=limit)
    return {"task_id": task_id, "logs": logs}


@tasks_router.get("/project/{project_id}", response_model=List[TaskResponse])
async def list_project_tasks(
    project_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """List all tasks for a project. Requires authentication."""
    tasks = db.list_tasks(project_id=project_id)
    return [
        TaskResponse(
            id=t["id"],
            project_id=t["project_id"],
            status=t["status"],
            current_stage=t["current_stage"],
            progress_percent=t.get("progress_percent", 0),
            creditors_total=t.get("creditors_total", 0),
            creditors_completed=t.get("creditors_completed", 0),
            started_at=t.get("started_at"),
            completed_at=t.get("completed_at"),
            error_message=t.get("error_message"),
            created_at=t["created_at"]
        )
        for t in tasks
    ]


# ============== Tools ==============

@tools_router.post("/calculate-interest", response_model=InterestCalculationResponse)
async def calculate_interest_endpoint(request: InterestCalculationRequest):
    """
    Calculate interest for a debt.

    Supports: simple, lpr, delay, compound, penalty
    """
    result = calculate_interest(
        calculation_type=request.calculation_type,
        principal=request.principal,
        start_date=request.start_date,
        end_date=request.end_date,
        rate=request.rate,
        multiplier=request.multiplier,
        lpr_term=request.lpr_term
    )

    if "error" in result:
        raise HTTPException(400, result["error"])

    return InterestCalculationResponse(
        principal=result["principal"],
        interest=result["interest"],
        total=result["total"],
        days=result.get("days", result.get("total_days", 0)),
        rate_used=result.get("annual_rate", result.get("effective_rate", 0)),
        calculation_details=result
    )
