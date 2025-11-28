"""
LangGraph State Definitions

Defines the state structure that flows through the debt review workflow.
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated
from datetime import datetime
from enum import Enum
import operator


class WorkflowStage(str, Enum):
    """Stages in the debt review workflow."""
    INIT = "init"
    FACT_CHECK = "fact_check"
    ANALYSIS = "analysis"
    REPORT = "report"
    VALIDATION = "validation"
    COMPLETE = "complete"
    ERROR = "error"


class CreditorState(TypedDict):
    """State for a single creditor being processed."""
    creditor_id: str
    creditor_name: str
    batch_number: int
    creditor_number: int

    # Paths
    materials_path: str
    output_path: str
    work_papers_path: str
    calculation_files_path: str
    final_reports_path: str

    # Declared amounts (from creditor)
    declared_principal: Optional[float]
    declared_interest: Optional[float]
    declared_total: Optional[float]

    # Confirmed amounts (our analysis)
    confirmed_principal: Optional[float]
    confirmed_interest: Optional[float]
    confirmed_total: Optional[float]

    # Processing state
    current_stage: WorkflowStage
    stage_completed: Dict[str, bool]  # {stage_name: completed}

    # Generated content
    fact_check_report: Optional[str]  # Markdown content
    analysis_report: Optional[str]
    final_report: Optional[str]

    # Calculation results
    calculations: List[Dict[str, Any]]

    # Errors
    errors: List[str]


class WorkflowState(TypedDict):
    """
    Main workflow state that flows through the LangGraph.

    This state is persisted and updated as the workflow progresses.
    The frontend polls the database to get the current state.
    """

    # Task identification
    task_id: str
    project_id: str

    # Project config (loaded at start)
    project_config: Dict[str, Any]
    bankruptcy_date: str
    interest_stop_date: str
    debtor_name: str

    # Creditors to process
    creditors: List[CreditorState]
    total_creditors: int
    completed_creditors: int
    current_creditor_index: int

    # Overall workflow state
    current_stage: WorkflowStage
    processing_mode: str  # "serial" or "parallel"

    # Progress tracking (for frontend polling)
    progress_percent: int
    status_message: str

    # Accumulated messages (for chat-like display)
    # Using Annotated with operator.add to accumulate messages
    messages: Annotated[List[Dict[str, Any]], operator.add]

    # Logs (for debugging)
    logs: Annotated[List[str], operator.add]

    # Error handling
    has_error: bool
    error_message: Optional[str]

    # Timing
    started_at: Optional[str]
    completed_at: Optional[str]


def create_initial_state(
    task_id: str,
    project_id: str,
    project_config: Dict[str, Any],
    creditors: List[Dict[str, Any]]
) -> WorkflowState:
    """
    Create initial workflow state from task and project data.

    Args:
        task_id: Task ID from database
        project_id: Project ID
        project_config: Project configuration including dates
        creditors: List of creditor data from database

    Returns:
        Initial WorkflowState
    """
    # Convert creditor data to CreditorState
    creditor_states = []
    for c in creditors:
        creditor_states.append(CreditorState(
            creditor_id=c["id"],
            creditor_name=c["creditor_name"],
            batch_number=c["batch_number"],
            creditor_number=c["creditor_number"],
            materials_path=c.get("materials_path", ""),
            output_path=c.get("output_path", ""),
            work_papers_path="",  # Will be set during init
            calculation_files_path="",
            final_reports_path="",
            declared_principal=c.get("declared_principal"),
            declared_interest=c.get("declared_interest"),
            declared_total=c.get("declared_total"),
            confirmed_principal=None,
            confirmed_interest=None,
            confirmed_total=None,
            current_stage=WorkflowStage.INIT,
            stage_completed={
                "init": False,
                "fact_check": False,
                "analysis": False,
                "report": False,
                "validation": False
            },
            fact_check_report=None,
            analysis_report=None,
            final_report=None,
            calculations=[],
            errors=[]
        ))

    # Determine processing mode
    processing_mode = "parallel" if len(creditor_states) >= 2 else "serial"

    return WorkflowState(
        task_id=task_id,
        project_id=project_id,
        project_config=project_config,
        bankruptcy_date=project_config.get("bankruptcy_date", ""),
        interest_stop_date=project_config.get("interest_stop_date", ""),
        debtor_name=project_config.get("debtor_name", ""),
        creditors=creditor_states,
        total_creditors=len(creditor_states),
        completed_creditors=0,
        current_creditor_index=0,
        current_stage=WorkflowStage.INIT,
        processing_mode=processing_mode,
        progress_percent=0,
        status_message="Initializing workflow...",
        messages=[],
        logs=[f"Workflow initialized with {len(creditor_states)} creditors"],
        has_error=False,
        error_message=None,
        started_at=datetime.utcnow().isoformat(),
        completed_at=None
    )


def calculate_progress(state: WorkflowState) -> int:
    """
    Calculate overall progress percentage.

    Progress is calculated as:
    - Each creditor is 100 / total_creditors
    - Each stage within a creditor is 1/5 of that creditor's portion
    """
    if state["total_creditors"] == 0:
        return 0

    creditor_weight = 100 / state["total_creditors"]
    stage_weight = creditor_weight / 5  # 5 stages per creditor

    total_progress = 0

    for i, creditor in enumerate(state["creditors"]):
        if i < state["completed_creditors"]:
            # Fully completed creditors
            total_progress += creditor_weight
        elif i == state["current_creditor_index"]:
            # Current creditor - count completed stages
            stages_done = sum(1 for v in creditor["stage_completed"].values() if v)
            total_progress += stages_done * stage_weight

    return min(int(total_progress), 100)
