"""
LangGraph Workflow Definition

Defines the main debt review workflow as a LangGraph StateGraph.
"""

from langgraph.graph import StateGraph, END
from typing import Literal
import logging

from app.agents.state import WorkflowState, WorkflowStage, calculate_progress
from app.agents.nodes import (
    init_node,
    fact_check_node,
    analysis_node,
    report_node,
    validation_node,
    error_handler_node,
    progress_sync_node
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

    # Stage progression
    stage_order = [
        WorkflowStage.INIT,
        WorkflowStage.FACT_CHECK,
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

    Workflow structure:
    ```
    [init] -> [fact_check] -> [analysis] -> [report] -> [validation]
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

    After each node, progress is synced to database.
    """
    # Create the graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("init", init_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("report", report_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("next_creditor", next_creditor_node)
    workflow.add_node("complete", complete_node)
    workflow.add_node("error_handler", error_handler_node)
    workflow.add_node("progress_sync", progress_sync_node)

    # Define edges (linear flow within a creditor)
    workflow.add_edge("init", "progress_sync")
    workflow.add_edge("progress_sync", "fact_check")
    workflow.add_edge("fact_check", "progress_sync")

    # After fact_check sync, continue to analysis
    workflow.add_conditional_edges(
        "progress_sync",
        lambda s: "analysis" if s["current_stage"] == WorkflowStage.FACT_CHECK else
                  "report" if s["current_stage"] == WorkflowStage.ANALYSIS else
                  "validation" if s["current_stage"] == WorkflowStage.REPORT else
                  "route_validation" if s["current_stage"] == WorkflowStage.VALIDATION else
                  "continue",
        {
            "analysis": "analysis",
            "report": "report",
            "validation": "validation",
            "route_validation": "validation",  # Will be routed after
            "continue": "fact_check"  # Default continue
        }
    )

    workflow.add_edge("analysis", "progress_sync")
    workflow.add_edge("report", "progress_sync")
    workflow.add_edge("validation", "progress_sync")

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
