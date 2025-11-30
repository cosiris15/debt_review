"""
LangGraph Workflow Definition

Defines the main debt review workflow as a LangGraph StateGraph.

Supports:
1. Serial processing (single creditor)
2. Stage-level parallel processing (multiple creditors)

The processing mode is automatically selected based on creditor count.
"""

from langgraph.graph import StateGraph, END
from typing import Literal, Dict, Any, List
import logging
import asyncio

from app.agents.state import WorkflowState, WorkflowStage, InputState, calculate_progress, create_initial_state
from app.agents.nodes import (
    init_node,
    fact_check_node,
    legal_diagram_node,
    analysis_node,
    report_node,
    validation_node,
    error_handler_node,
    progress_sync_node
)
from app.agents.parallel import (
    auto_select_processing_mode,
    get_execution_plan,
    ProcessingMode,
    run_parallel_batch
)

logger = logging.getLogger(__name__)


def should_continue(state: WorkflowState) -> Literal["continue", "error", "complete"]:
    """Determine if workflow should continue, handle error, or complete."""
    if state["has_error"]:
        return "error"

    if state["completed_creditors"] >= state["total_creditors"]:
        return "complete"

    return "continue"


def get_next_stage(state: WorkflowState) -> str:
    """
    Determine the next stage based on current state.

    Returns the name of the next node to execute.
    """
    current_stage = state["current_stage"]

    # Stage progression (including legal_diagram stage)
    stage_order = [
        WorkflowStage.INIT,
        WorkflowStage.FACT_CHECK,
        WorkflowStage.LEGAL_DIAGRAM,
        WorkflowStage.ANALYSIS,
        WorkflowStage.REPORT,
        WorkflowStage.VALIDATION,
        WorkflowStage.COMPLETE
    ]

    try:
        current_index = stage_order.index(current_stage)
        next_stage = stage_order[current_index + 1]

        # Map stage to node name
        stage_to_node = {
            WorkflowStage.INIT: "init",
            WorkflowStage.FACT_CHECK: "fact_check",
            WorkflowStage.LEGAL_DIAGRAM: "legal_diagram",
            WorkflowStage.ANALYSIS: "analysis",
            WorkflowStage.REPORT: "report",
            WorkflowStage.VALIDATION: "validation",
            WorkflowStage.COMPLETE: "complete"
        }

        return stage_to_node.get(next_stage, "complete")

    except (ValueError, IndexError):
        return "complete"


def route_after_validation(state: WorkflowState) -> Literal["next_creditor", "complete", "error"]:
    """
    Route after validation stage.

    Decides whether to process next creditor or complete workflow.
    """
    if state["has_error"]:
        return "error"

    # Check if current creditor is done
    current_idx = state["current_creditor_index"]
    if current_idx < len(state["creditors"]) - 1:
        # More creditors to process
        return "next_creditor"
    else:
        # All creditors done
        return "complete"


def next_creditor_node(state: WorkflowState) -> WorkflowState:
    """
    Move to the next creditor in the list.

    Resets stage to INIT for the new creditor.
    """
    new_index = state["current_creditor_index"] + 1
    new_completed = state["completed_creditors"] + 1

    return {
        **state,
        "current_creditor_index": new_index,
        "completed_creditors": new_completed,
        "current_stage": WorkflowStage.INIT,
        "progress_percent": calculate_progress(state),
        "status_message": f"Moving to creditor {new_index + 1}/{state['total_creditors']}",
        "logs": [f"Completed creditor {new_index}, moving to next"]
    }


def complete_node(state: WorkflowState) -> WorkflowState:
    """
    Mark workflow as complete.
    """
    from datetime import datetime

    return {
        **state,
        "current_stage": WorkflowStage.COMPLETE,
        "completed_creditors": state["total_creditors"],
        "progress_percent": 100,
        "status_message": "Workflow completed successfully",
        "completed_at": datetime.utcnow().isoformat(),
        "logs": ["Workflow completed successfully"]
    }


def build_workflow() -> StateGraph:
    """
    Build the LangGraph workflow for debt review.

    Workflow structure (simplified linear):
    ```
    [init] -> [fact_check] -> [legal_diagram] -> [analysis] -> [report] -> [validation]
                                                                                 |
                                                                                 v
                                                                       [route_after_validation]
                                                                            /       \
                                                                           v         v
                                                                  [next_creditor]  [complete]
                                                                           |
                                                                           v
                                                                      [init] (loop)
    ```

    Progress sync is handled within each node.

    Note: Uses InputState for input schema so LangGraph Studio only shows
    required fields (debtor_name, bankruptcy_date, creditors) instead of
    all internal tracking fields.
    """
    # Create the graph with explicit input schema
    # This tells LangGraph Studio what fields are actually needed to start
    workflow = StateGraph(WorkflowState, input=InputState)

    # Add nodes
    workflow.add_node("init", init_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("legal_diagram", legal_diagram_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("report", report_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("next_creditor", next_creditor_node)
    workflow.add_node("complete", complete_node)
    workflow.add_node("error_handler", error_handler_node)

    # Define edges (simple linear flow within a creditor)
    # New flow: init -> fact_check -> legal_diagram -> analysis -> report -> validation
    workflow.add_edge("init", "fact_check")
    workflow.add_edge("fact_check", "legal_diagram")
    workflow.add_edge("legal_diagram", "analysis")
    workflow.add_edge("analysis", "report")
    workflow.add_edge("report", "validation")

    # After validation, route to next creditor or complete
    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "next_creditor": "next_creditor",
            "complete": "complete",
            "error": "error_handler"
        }
    )

    # Next creditor loops back to init
    workflow.add_edge("next_creditor", "init")

    # Error handler and complete go to END
    workflow.add_edge("error_handler", END)
    workflow.add_edge("complete", END)

    # Set entry point
    workflow.set_entry_point("init")

    return workflow


def create_workflow_app():
    """
    Create a compiled workflow application.

    Returns a compiled LangGraph that can be invoked.
    """
    workflow = build_workflow()
    return workflow.compile()


# Singleton workflow app
_workflow_app = None


def get_workflow_app():
    """Get or create the workflow application."""
    global _workflow_app
    if _workflow_app is None:
        _workflow_app = create_workflow_app()
    return _workflow_app


async def run_workflow_with_auto_mode(
    creditor_configs: List[Dict[str, Any]],
    shared_context: Dict[str, Any],
    max_concurrent: int = 5
) -> Dict[str, Any]:
    """
    Run workflow with automatic mode selection.

    This function implements the original solution's automatic processing mode:
    - 1 creditor: Serial processing
    - 2+ creditors: Stage-level parallel processing (75-80% time savings)

    Args:
        creditor_configs: List of creditor configurations
        shared_context: Shared context (bankruptcy_date, debtor_name, task_id, etc.)
        max_concurrent: Maximum concurrent creditors for parallel mode

    Returns:
        Workflow execution results
    """
    creditor_count = len(creditor_configs)
    mode = auto_select_processing_mode(creditor_count)
    execution_plan = get_execution_plan(mode, creditor_count)

    logger.info(f"Processing mode: {mode.value}")
    logger.info(f"Execution plan:\n{execution_plan}")

    workflow_app = get_workflow_app()

    if mode == ProcessingMode.SERIAL:
        # Serial processing - standard workflow
        from datetime import datetime, timezone
        import uuid

        all_results = []
        for i, config in enumerate(creditor_configs):
            # Normalize creditor config to match expected format
            normalized_creditor = {
                "id": config.get("creditor_id", f"creditor-{uuid.uuid4().hex[:8]}"),
                "creditor_name": config.get("creditor_name", f"Creditor {i+1}"),
                "batch_number": config.get("batch_number", 1),
                "creditor_number": config.get("creditor_number", i + 1),
                "materials_path": config.get("materials_path", ""),
                "output_path": config.get("output_path", f"./outputs/{i+1}"),
                "declared_principal": config.get("declared_amounts", {}).get("principal"),
                "declared_interest": config.get("declared_amounts", {}).get("interest"),
                "declared_total": config.get("declared_amounts", {}).get("total"),
            }

            # Build project config from shared context
            project_config = {
                "bankruptcy_date": shared_context.get("bankruptcy_date", ""),
                "interest_stop_date": shared_context.get("interest_stop_date", ""),
                "debtor_name": shared_context.get("debtor_name", ""),
            }

            # Use the proper state creation function
            initial_state = create_initial_state(
                task_id=shared_context.get("task_id", f"task-{uuid.uuid4().hex[:8]}"),
                project_id=shared_context.get("project_id", "test-project"),
                project_config=project_config,
                creditors=[normalized_creditor]
            )

            result = await workflow_app.ainvoke(initial_state)
            all_results.append({
                "creditor_name": config.get("creditor_name"),
                "success": not result.get("has_error", False),
                "result": result
            })

        return {
            "mode": "serial",
            "execution_plan": execution_plan,
            "results": all_results,
            "success_count": sum(1 for r in all_results if r.get("success")),
            "failure_count": sum(1 for r in all_results if not r.get("success"))
        }

    else:
        # Parallel processing
        return await run_parallel_batch(
            workflow_app=workflow_app,
            creditor_configs=creditor_configs,
            shared_context=shared_context,
            max_concurrent=max_concurrent
        )
