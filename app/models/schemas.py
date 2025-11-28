"""
Pydantic Schemas for API Request/Response

These schemas define the data structures used in API communication.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============== Enums ==============

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"           # Waiting to start
    RUNNING = "running"           # Currently executing
    COMPLETED = "completed"       # Successfully finished
    FAILED = "failed"             # Failed with error
    CANCELLED = "cancelled"       # Cancelled by user


class TaskStage(str, Enum):
    """Workflow stage for debt review."""
    INIT = "init"                 # Environment initialization
    FACT_CHECK = "fact_check"     # Stage 1: Fact checking
    ANALYSIS = "analysis"         # Stage 2: Debt analysis
    REPORT = "report"             # Stage 3: Report organization
    VALIDATION = "validation"     # Quality validation
    COMPLETE = "complete"         # All stages done


class CreditorStatus(str, Enum):
    """Processing status for a creditor."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ============== Project Schemas ==============

class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., description="Project name")
    debtor_name: str = Field(..., description="Debtor company name")
    bankruptcy_date: str = Field(..., description="Bankruptcy filing date (YYYY-MM-DD)")
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str
    name: str
    debtor_name: str
    bankruptcy_date: str
    interest_stop_date: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    total_creditors: int = 0
    completed_creditors: int = 0


# ============== Creditor Schemas ==============

class CreditorCreate(BaseModel):
    """Schema for creating/adding a creditor."""
    project_id: str
    batch_number: int = Field(..., ge=1, description="Batch number")
    creditor_number: int = Field(..., ge=1, description="Creditor number within batch")
    creditor_name: str = Field(..., description="Creditor name")
    declared_amount: Optional[float] = None
    materials_path: Optional[str] = None


class CreditorResponse(BaseModel):
    """Schema for creditor response."""
    id: str
    project_id: str
    batch_number: int
    creditor_number: int
    creditor_name: str
    declared_amount: Optional[float]
    confirmed_amount: Optional[float]
    status: CreditorStatus
    current_stage: Optional[TaskStage]
    materials_path: Optional[str]
    output_path: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============== Task Schemas ==============

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    project_id: str
    creditor_ids: List[str] = Field(..., description="List of creditor IDs to process")
    processing_mode: str = Field(default="auto", description="auto, serial, or parallel")


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    project_id: str
    status: TaskStatus
    current_stage: TaskStage
    progress_percent: int = Field(ge=0, le=100)
    creditors_total: int
    creditors_completed: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime


class TaskProgress(BaseModel):
    """Schema for task progress updates."""
    task_id: str
    status: TaskStatus
    current_stage: TaskStage
    progress_percent: int
    current_creditor: Optional[str]
    stage_details: Optional[Dict[str, Any]]
    logs: List[str] = []


class TaskSubmitResponse(BaseModel):
    """Response when a task is submitted."""
    task_id: str
    message: str = "Task submitted successfully"
    status: TaskStatus = TaskStatus.PENDING


# ============== Calculation Schemas ==============

class InterestCalculationRequest(BaseModel):
    """Request for interest calculation."""
    calculation_type: str = Field(..., description="simple, lpr, delay, compound, penalty")
    principal: float = Field(..., gt=0)
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    rate: Optional[float] = Field(None, description="Annual rate in percent")
    multiplier: Optional[float] = Field(1.0, description="LPR multiplier")
    lpr_term: Optional[str] = Field("1y", description="1y or 5y")


class InterestCalculationResponse(BaseModel):
    """Response from interest calculation."""
    principal: float
    interest: float
    total: float
    days: int
    rate_used: float
    calculation_details: Dict[str, Any]


# ============== Report Schemas ==============

class ReportResponse(BaseModel):
    """Schema for generated report."""
    creditor_id: str
    creditor_name: str
    report_type: str  # fact_check, analysis, final
    file_path: str
    generated_at: datetime


class FileListResponse(BaseModel):
    """Schema for file listing."""
    creditor_id: str
    files: List[Dict[str, str]]  # [{name, path, type, size}]
