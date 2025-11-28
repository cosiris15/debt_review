"""
LangGraph Node Implementations

Each node represents a stage in the debt review workflow.
Nodes are responsible for:
1. Executing their specific task
2. Updating state
3. Syncing progress to database

The analysis node automatically invokes the calculator tool for interest calculations,
matching the original agent workflow where the LLM agent calls calculator autonomously.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re
import json

from app.agents.state import WorkflowState, WorkflowStage, CreditorState, calculate_progress
from app.core.database import db
from app.agents.llm import get_llm, create_fact_check_prompt, create_analysis_prompt, create_report_prompt
from app.tools.calculator import calculate_interest

logger = logging.getLogger(__name__)


def extract_calculation_requests(analysis_text: str, bankruptcy_date: str) -> List[Dict[str, Any]]:
    """
    Extract calculation parameters from analysis report.

    The LLM is prompted to output calculation requests in a specific format:
    【利息计算】本金: XXX, 起始日: YYYY-MM-DD, 类型: lpr/simple/delay

    Returns list of calculation parameters for the calculator tool.
    """
    calculations = []

    # Pattern to match calculation requests embedded in the analysis
    # Format: 【利息计算】本金: 100000, 起始日: 2023-01-01, 类型: lpr, 倍数: 1.5
    pattern = r'【利息计算】本金:\s*([\d,.]+)(?:元)?,?\s*起始日:\s*(\d{4}-\d{2}-\d{2}),?\s*类型:\s*(\w+)(?:,?\s*倍数:\s*([\d.]+))?(?:,?\s*利率:\s*([\d.]+)%?)?'

    for match in re.finditer(pattern, analysis_text):
        principal_str = match.group(1).replace(',', '').replace('，', '')
        start_date = match.group(2)
        calc_type = match.group(3).lower()
        multiplier = float(match.group(4)) if match.group(4) else 1.0
        rate = float(match.group(5)) if match.group(5) else None

        try:
            principal = float(principal_str)

            # Calculate interest stop date (bankruptcy_date - 1 day)
            from datetime import datetime as dt, timedelta
            end_dt = dt.strptime(bankruptcy_date, "%Y-%m-%d") - timedelta(days=1)
            end_date = end_dt.strftime("%Y-%m-%d")

            calc_params = {
                "calculation_type": calc_type,
                "principal": principal,
                "start_date": start_date,
                "end_date": end_date
            }

            if calc_type == "lpr":
                calc_params["multiplier"] = multiplier
                calc_params["lpr_term"] = "1y"  # Default to 1-year LPR
            elif calc_type in ["simple", "penalty"]:
                calc_params["rate"] = rate or 4.35  # Default rate

            calculations.append(calc_params)

        except ValueError as e:
            logger.warning(f"Failed to parse calculation: {e}")
            continue

    return calculations


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

    This node:
    1. Calls LLM to analyze the debt claim
    2. Automatically extracts and executes interest calculations
    3. Updates the analysis with calculated results
    4. Saves all calculation records to database

    The calculator tool is called AUTOMATICALLY during analysis,
    matching the original agent workflow behavior.
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

        # ==== AUTOMATIC CALCULATOR INVOCATION ====
        # Extract calculation requests from the analysis
        calculation_requests = extract_calculation_requests(
            analysis_report,
            state["bankruptcy_date"]
        )

        calculation_results = []
        total_calculated_interest = 0.0

        for calc_params in calculation_requests:
            logger.info(f"Auto-executing calculator: {calc_params}")

            # Call calculator tool automatically
            result = calculate_interest(**calc_params)

            if "error" not in result:
                calculation_results.append(result)
                total_calculated_interest += result.get("interest", 0)

                # Save calculation to database
                await db.save_calculation({
                    "creditor_id": creditor["creditor_id"],
                    "task_id": state["task_id"],
                    "calculation_type": calc_params["calculation_type"],
                    "principal": calc_params["principal"],
                    "interest": result.get("interest", 0),
                    "total": result.get("total", calc_params["principal"]),
                    "parameters": calc_params,
                    "result": result
                })

                await db.add_task_log(
                    task_id=state["task_id"],
                    message=f"Calculator executed: {calc_params['calculation_type']} for {calc_params['principal']}",
                    level="info",
                    stage="analysis",
                    creditor_id=creditor["creditor_id"],
                    details={"calculation": result}
                )
            else:
                logger.warning(f"Calculator error: {result['error']}")

        # Append calculation results to analysis report
        if calculation_results:
            calc_summary = "\n\n=== 利息计算结果（由系统自动计算）===\n"
            for i, result in enumerate(calculation_results, 1):
                calc_summary += f"\n计算{i}:\n"
                calc_summary += f"  本金: {result.get('principal', 0):,.2f}元\n"
                calc_summary += f"  利息: {result.get('interest', 0):,.2f}元\n"
                calc_summary += f"  合计: {result.get('total', 0):,.2f}元\n"
                calc_summary += f"  计算天数: {result.get('days', result.get('total_days', 0))}天\n"
            analysis_report += calc_summary

        # Determine confirmed amounts
        # Apply 就低原则: use declared amount if calculation exceeds it
        declared_principal = creditor.get("declared_principal") or 0
        declared_interest = creditor.get("declared_interest") or 0
        declared_total = creditor.get("declared_total") or 0

        confirmed_principal = declared_principal
        confirmed_interest = min(total_calculated_interest, declared_interest) if declared_interest else total_calculated_interest
        confirmed_total = confirmed_principal + confirmed_interest

        # Apply final 就低原则 on total
        if declared_total and confirmed_total > declared_total:
            confirmed_total = declared_total

        creditor["analysis_report"] = analysis_report
        creditor["confirmed_principal"] = confirmed_principal
        creditor["confirmed_interest"] = confirmed_interest
        creditor["confirmed_total"] = confirmed_total
        creditor["calculation_results"] = calculation_results
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
            "confirmed_principal": confirmed_principal,
            "confirmed_interest": confirmed_interest,
            "confirmed_total": confirmed_total,
            "current_stage": "report"
        })

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Analysis completed for {creditor['creditor_name']} ({len(calculation_results)} calculations executed)",
            level="info",
            stage="analysis",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"Analysis completed for {creditor['creditor_name']} with {len(calculation_results)} auto-calculations"],
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
