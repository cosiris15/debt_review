"""
LangGraph Node Implementations

Each node represents a stage in the debt review workflow.
Nodes are responsible for:
1. Executing their specific task
2. Updating state
3. Syncing progress to database
"""

from typing import Dict, Any
from datetime import datetime
import logging

from app.agents.state import WorkflowState, WorkflowStage, CreditorState, calculate_progress
from app.core.database import db
from app.agents.llm import get_llm, create_fact_check_prompt, create_analysis_prompt, create_report_prompt

logger = logging.getLogger(__name__)


async def init_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Initialize processing for the current creditor.

    Creates directory structure and prepares for fact-checking.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Initializing creditor: {creditor['creditor_name']}")

    try:
        # Create output directory structure
        base_path = f"outputs/batch_{creditor['batch_number']}/{creditor['creditor_number']}-{creditor['creditor_name']}"

        # Update creditor paths
        creditor["output_path"] = base_path
        creditor["work_papers_path"] = f"{base_path}/工作底稿"
        creditor["calculation_files_path"] = f"{base_path}/计算文件"
        creditor["final_reports_path"] = f"{base_path}/最终报告"
        creditor["stage_completed"]["init"] = True
        creditor["current_stage"] = WorkflowStage.FACT_CHECK

        # Update state
        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.FACT_CHECK
        state["status_message"] = f"Initialized {creditor['creditor_name']}, starting fact-check..."

        # Log to database
        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Initialized creditor: {creditor['creditor_name']}",
            level="info",
            stage="init",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"Initialized creditor {creditor['creditor_name']}"],
            "progress_percent": calculate_progress(state)
        }

    except Exception as e:
        logger.error(f"Init failed: {e}")
        return {
            **state,
            "has_error": True,
            "error_message": f"Initialization failed: {str(e)}",
            "logs": [f"ERROR: Init failed - {str(e)}"]
        }


async def fact_check_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Execute fact-checking for the current creditor.

    Calls LLM to analyze materials and generate fact-check report.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Fact-checking: {creditor['creditor_name']}")

    try:
        # Get LLM
        llm = get_llm()

        # Create prompt with creditor context
        prompt = create_fact_check_prompt(
            creditor_name=creditor["creditor_name"],
            materials_path=creditor["materials_path"],
            bankruptcy_date=state["bankruptcy_date"],
            debtor_name=state["debtor_name"]
        )

        # Call LLM
        response = await llm.ainvoke(prompt)
        fact_check_report = response.content

        # Update creditor state
        creditor["fact_check_report"] = fact_check_report
        creditor["stage_completed"]["fact_check"] = True
        creditor["current_stage"] = WorkflowStage.ANALYSIS

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.ANALYSIS
        state["status_message"] = f"Fact-check complete for {creditor['creditor_name']}, starting analysis..."

        # Save report to database
        await db.create_report({
            "creditor_id": creditor["creditor_id"],
            "task_id": state["task_id"],
            "report_type": "fact_check",
            "file_name": f"{creditor['creditor_name']}_事实核查报告.md",
            "file_path": f"{creditor['work_papers_path']}/{creditor['creditor_name']}_事实核查报告.md",
            "content_preview": fact_check_report[:500] if fact_check_report else None
        })

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Fact-check completed for {creditor['creditor_name']}",
            level="info",
            stage="fact_check",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"Fact-check completed for {creditor['creditor_name']}"],
            "progress_percent": calculate_progress(state)
        }

    except Exception as e:
        logger.error(f"Fact-check failed: {e}")
        creditor["errors"].append(f"Fact-check error: {str(e)}")
        state["creditors"][current_idx] = creditor

        return {
            **state,
            "has_error": True,
            "error_message": f"Fact-check failed: {str(e)}",
            "logs": [f"ERROR: Fact-check failed - {str(e)}"]
        }


async def analysis_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Execute debt analysis for the current creditor.

    Analyzes amounts, calculates interest, determines confirmation status.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Analyzing: {creditor['creditor_name']}")

    try:
        llm = get_llm()

        # Create analysis prompt with fact-check report
        prompt = create_analysis_prompt(
            creditor_name=creditor["creditor_name"],
            fact_check_report=creditor["fact_check_report"],
            bankruptcy_date=state["bankruptcy_date"],
            interest_stop_date=state["interest_stop_date"],
            declared_amounts={
                "principal": creditor.get("declared_principal"),
                "interest": creditor.get("declared_interest"),
                "total": creditor.get("declared_total")
            }
        )

        response = await llm.ainvoke(prompt)
        analysis_report = response.content

        # TODO: Parse analysis report to extract confirmed amounts
        # For now, using declared amounts as placeholder
        creditor["analysis_report"] = analysis_report
        creditor["confirmed_principal"] = creditor.get("declared_principal")
        creditor["confirmed_interest"] = creditor.get("declared_interest")
        creditor["confirmed_total"] = creditor.get("declared_total")
        creditor["stage_completed"]["analysis"] = True
        creditor["current_stage"] = WorkflowStage.REPORT

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.REPORT
        state["status_message"] = f"Analysis complete for {creditor['creditor_name']}, generating report..."

        # Save report
        await db.create_report({
            "creditor_id": creditor["creditor_id"],
            "task_id": state["task_id"],
            "report_type": "analysis",
            "file_name": f"{creditor['creditor_name']}_债权分析报告.md",
            "file_path": f"{creditor['work_papers_path']}/{creditor['creditor_name']}_债权分析报告.md",
            "content_preview": analysis_report[:500] if analysis_report else None
        })

        # Update creditor in database with confirmed amounts
        await db.update_creditor(creditor["creditor_id"], {
            "confirmed_principal": creditor["confirmed_principal"],
            "confirmed_interest": creditor["confirmed_interest"],
            "confirmed_total": creditor["confirmed_total"],
            "current_stage": "report"
        })

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Analysis completed for {creditor['creditor_name']}",
            level="info",
            stage="analysis",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"Analysis completed for {creditor['creditor_name']}"],
            "progress_percent": calculate_progress(state)
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        creditor["errors"].append(f"Analysis error: {str(e)}")
        state["creditors"][current_idx] = creditor

        return {
            **state,
            "has_error": True,
            "error_message": f"Analysis failed: {str(e)}",
            "logs": [f"ERROR: Analysis failed - {str(e)}"]
        }


async def report_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate final report for the current creditor.

    Consolidates fact-check and analysis into final review opinion.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Generating report: {creditor['creditor_name']}")

    try:
        llm = get_llm()

        prompt = create_report_prompt(
            creditor_name=creditor["creditor_name"],
            fact_check_report=creditor["fact_check_report"],
            analysis_report=creditor["analysis_report"],
            debtor_name=state["debtor_name"],
            bankruptcy_date=state["bankruptcy_date"]
        )

        response = await llm.ainvoke(prompt)
        final_report = response.content

        creditor["final_report"] = final_report
        creditor["stage_completed"]["report"] = True
        creditor["current_stage"] = WorkflowStage.VALIDATION

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.VALIDATION
        state["status_message"] = f"Report generated for {creditor['creditor_name']}, validating..."

        # Save final report
        report_date = datetime.now().strftime("%Y%m%d")
        await db.create_report({
            "creditor_id": creditor["creditor_id"],
            "task_id": state["task_id"],
            "report_type": "final",
            "file_name": f"GY2025_{creditor['creditor_name']}_债权审查报告_{report_date}.md",
            "file_path": f"{creditor['final_reports_path']}/GY2025_{creditor['creditor_name']}_债权审查报告_{report_date}.md",
            "content_preview": final_report[:500] if final_report else None
        })

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Report generated for {creditor['creditor_name']}",
            level="info",
            stage="report",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"Report generated for {creditor['creditor_name']}"],
            "progress_percent": calculate_progress(state)
        }

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        creditor["errors"].append(f"Report error: {str(e)}")
        state["creditors"][current_idx] = creditor

        return {
            **state,
            "has_error": True,
            "error_message": f"Report generation failed: {str(e)}",
            "logs": [f"ERROR: Report generation failed - {str(e)}"]
        }


async def validation_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Validate the generated reports for the current creditor.

    Checks format compliance, date consistency, etc.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Validating: {creditor['creditor_name']}")

    try:
        # Validation checks
        validation_errors = []

        # Check report exists
        if not creditor["final_report"]:
            validation_errors.append("Final report is missing")

        # Check dates in report
        if creditor["final_report"]:
            if state["bankruptcy_date"] not in creditor["final_report"]:
                validation_errors.append("Bankruptcy date not found in report")

        # Check format (no markdown headers in final report)
        if creditor["final_report"] and "## " in creditor["final_report"]:
            validation_errors.append("Report contains markdown headers (format violation)")

        if validation_errors:
            creditor["errors"].extend(validation_errors)
            logger.warning(f"Validation warnings for {creditor['creditor_name']}: {validation_errors}")

        creditor["stage_completed"]["validation"] = True
        creditor["current_stage"] = WorkflowStage.COMPLETE

        state["creditors"][current_idx] = creditor
        state["status_message"] = f"Validation complete for {creditor['creditor_name']}"

        # Update creditor status in database
        await db.update_creditor_status(
            creditor["creditor_id"],
            status="completed",
            stage="complete"
        )

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Validation completed for {creditor['creditor_name']}. Warnings: {len(validation_errors)}",
            level="warning" if validation_errors else "info",
            stage="validation",
            creditor_id=creditor["creditor_id"],
            details={"validation_errors": validation_errors} if validation_errors else None
        )

        return {
            **state,
            "logs": [f"Validation completed for {creditor['creditor_name']}"],
            "progress_percent": calculate_progress(state)
        }

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {
            **state,
            "has_error": True,
            "error_message": f"Validation failed: {str(e)}",
            "logs": [f"ERROR: Validation failed - {str(e)}"]
        }


async def error_handler_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Handle errors in the workflow.

    Logs error and updates database.
    """
    logger.error(f"Workflow error: {state['error_message']}")

    # Update task status in database
    await db.complete_task(
        state["task_id"],
        success=False,
        error_message=state["error_message"]
    )

    await db.add_task_log(
        task_id=state["task_id"],
        message=f"Workflow failed: {state['error_message']}",
        level="error",
        stage=state["current_stage"].value
    )

    return {
        **state,
        "current_stage": WorkflowStage.ERROR,
        "completed_at": datetime.utcnow().isoformat()
    }


async def progress_sync_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Sync progress to database.

    Called after each stage to update the task progress in database.
    This allows frontend to poll and see real-time progress.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx] if current_idx < len(state["creditors"]) else None

    progress = calculate_progress(state)

    # Update task progress in database
    await db.update_task_progress(
        task_id=state["task_id"],
        status="running",
        stage=state["current_stage"].value,
        progress=progress,
        current_creditor_id=creditor["creditor_id"] if creditor else None,
        current_creditor_name=creditor["creditor_name"] if creditor else None,
        creditors_completed=state["completed_creditors"]
    )

    return {
        **state,
        "progress_percent": progress
    }
