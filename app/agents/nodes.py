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
from pathlib import Path
import logging
import re
import json

from app.agents.state import WorkflowState, WorkflowStage, CreditorState, calculate_progress
from app.core.database import db
from app.agents.llm import (
    get_llm,
    create_fact_check_prompt,
    create_fact_check_prompt_async,
    create_analysis_prompt,
    create_analysis_prompt_async,
    create_report_prompt,
    create_report_prompt_async,
    create_legal_diagram_prompt_async,
    should_generate_legal_diagram
)
from app.agents.material_reader import read_materials
from app.tools.calculator import calculate_interest, export_to_excel
from app.core.config import settings
from app.agents.checkpoints import run_checkpoint, CheckpointStatus
from app.agents.templates import (
    enforce_template_compliance,
    validate_report_format,
    get_template_enforcer
)

logger = logging.getLogger(__name__)


def extract_calculation_requests(analysis_text: str, bankruptcy_date: str) -> List[Dict[str, Any]]:
    """
    Extract calculation parameters from analysis report.

    The LLM is prompted to output calculation requests in specific formats:
    - 【利息计算】本金: XXX, 起始日: YYYY-MM-DD, 类型: lpr/simple/delay
    - 【份额计算】总额: XXX, 份额: XX%, 描述: XXX
    - 【确认金额】金额: XXX, 来源: XXX, 描述: XXX
    - 【最高额检查】计算总额: XXX, 最高额: XXX, 描述: XXX

    Returns list of calculation parameters for the calculator tool.
    """
    calculations = []

    # ===== 1. 原有利息计算模式 =====
    # Format: 【利息计算】本金: 100000, 起始日: 2023-01-01, 类型: lpr, 倍数: 1.5
    interest_pattern = r'【利息计算】本金:\s*([\d,.]+)(?:元)?,?\s*起始日:\s*(\d{4}-\d{2}-\d{2}),?\s*类型:\s*(\w+)(?:,?\s*倍数:\s*([\d.]+))?(?:,?\s*利率:\s*([\d.]+)%?)?'

    for match in re.finditer(interest_pattern, analysis_text):
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
            logger.warning(f"Failed to parse interest calculation: {e}")
            continue

    # ===== 2. 份额比例计算模式（银团贷款）=====
    # Format: 【份额计算】总额: 247674737.97, 份额: 13.95%, 描述: 判决确认银团总利息
    share_pattern = r'【份额计算】总额:\s*([\d,.]+)(?:元)?,?\s*份额:\s*([\d.]+)%?,?\s*(?:描述:\s*(.+?))?(?:\n|$)'

    for match in re.finditer(share_pattern, analysis_text):
        total_amount_str = match.group(1).replace(',', '').replace('，', '')
        share_ratio_str = match.group(2)
        description = match.group(3).strip() if match.group(3) else ""

        try:
            total_amount = float(total_amount_str)
            share_ratio = float(share_ratio_str)

            calc_params = {
                "calculation_type": "share_ratio",
                "total_amount": total_amount,
                "share_ratio": share_ratio,
                "description": description
            }
            calculations.append(calc_params)
            logger.info(f"Extracted share_ratio calculation: {total_amount} × {share_ratio}%")

        except ValueError as e:
            logger.warning(f"Failed to parse share ratio calculation: {e}")
            continue

    # ===== 3. 判决确认金额模式 =====
    # Format: 【确认金额】金额: 247674737.97, 来源: (2018)鄂72民初1270号, 描述: 截至2018年5月15日的利息
    confirmed_pattern = r'【确认金额】金额:\s*([\d,.]+)(?:元)?,?\s*(?:来源:\s*(.+?),?\s*)?(?:描述:\s*(.+?))?(?:\n|$)'

    for match in re.finditer(confirmed_pattern, analysis_text):
        amount_str = match.group(1).replace(',', '').replace('，', '')
        source = match.group(2).strip() if match.group(2) else ""
        description = match.group(3).strip() if match.group(3) else ""

        try:
            confirmed_amount = float(amount_str)

            calc_params = {
                "calculation_type": "confirmed",
                "confirmed_amount": confirmed_amount,
                "source": source,
                "description": description
            }
            calculations.append(calc_params)
            logger.info(f"Extracted confirmed amount: {confirmed_amount} from {source}")

        except ValueError as e:
            logger.warning(f"Failed to parse confirmed amount: {e}")
            continue

    # ===== 4. 最高额限额封顶检查模式 =====
    # Format: 【最高额检查】计算总额: 153321209.81, 最高额: 150000000, 描述: 最高额保证1.5亿元
    max_limit_pattern = r'【最高额检查】计算总额:\s*([\d,.]+)(?:元)?,?\s*最高额:\s*([\d,.]+)(?:元)?,?\s*(?:描述:\s*(.+?))?(?:\n|$)'

    for match in re.finditer(max_limit_pattern, analysis_text):
        calculated_total_str = match.group(1).replace(',', '').replace('，', '')
        max_limit_str = match.group(2).replace(',', '').replace('，', '')
        description = match.group(3).strip() if match.group(3) else ""

        try:
            calculated_total = float(calculated_total_str)
            max_limit = float(max_limit_str)

            calc_params = {
                "calculation_type": "max_limit",
                "calculated_total": calculated_total,
                "max_limit": max_limit,
                "description": description
            }
            calculations.append(calc_params)
            logger.info(f"Extracted max_limit check: {calculated_total} vs limit {max_limit}")

        except ValueError as e:
            logger.warning(f"Failed to parse max limit check: {e}")
            continue

    return calculations


def _convert_input_to_workflow_state(input_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert minimal InputState to full WorkflowState.

    This is called when the workflow receives InputState (from API/Studio)
    instead of a full WorkflowState.

    InputState has: debtor_name, bankruptcy_date, creditors, [optional: task_id, project_id, interest_stop_date]
    WorkflowState needs: all tracking fields with defaults
    """
    import uuid
    from datetime import datetime as dt

    # Generate IDs if not provided
    task_id = input_state.get("task_id") or f"task-{uuid.uuid4().hex[:8]}"
    project_id = input_state.get("project_id") or "default-project"

    # Get dates
    bankruptcy_date = input_state.get("bankruptcy_date", "")
    interest_stop_date = input_state.get("interest_stop_date") or bankruptcy_date
    debtor_name = input_state.get("debtor_name", "")

    # Convert creditor inputs to full CreditorState format
    creditor_states = []
    for i, c in enumerate(input_state.get("creditors", [])):
        creditor_states.append({
            "creditor_id": c.get("creditor_id") or f"creditor-{uuid.uuid4().hex[:8]}",
            "creditor_name": c.get("creditor_name", f"Creditor {i+1}"),
            "batch_number": c.get("batch_number", 1),
            "creditor_number": c.get("creditor_number", i + 1),
            "materials_path": c.get("materials_path", ""),
            "output_path": c.get("output_path", f"./outputs/{i+1}"),
            "work_papers_path": "",
            "calculation_files_path": "",
            "final_reports_path": "",
            "declared_principal": c.get("declared_principal"),
            "declared_interest": c.get("declared_interest"),
            "declared_total": c.get("declared_total"),
            "confirmed_principal": None,
            "confirmed_interest": None,
            "confirmed_total": None,
            "current_stage": WorkflowStage.INIT,
            "stage_completed": {
                "init": False,
                "fact_check": False,
                "legal_diagram": False,
                "analysis": False,
                "report": False,
                "validation": False
            },
            "fact_check_report": None,
            "legal_diagram": None,
            "should_generate_diagram": False,
            "analysis_report": None,
            "final_report": None,
            "calculations": [],
            "errors": []
        })

    # Build full WorkflowState
    return {
        "task_id": task_id,
        "project_id": project_id,
        "project_config": {
            "bankruptcy_date": bankruptcy_date,
            "interest_stop_date": interest_stop_date,
            "debtor_name": debtor_name,
        },
        "bankruptcy_date": bankruptcy_date,
        "interest_stop_date": interest_stop_date,
        "debtor_name": debtor_name,
        "creditors": creditor_states,
        "total_creditors": len(creditor_states),
        "completed_creditors": 0,
        "current_creditor_index": 0,
        "current_stage": WorkflowStage.INIT,
        "processing_mode": "parallel" if len(creditor_states) >= 2 else "serial",
        "progress_percent": 0,
        "status_message": "Initializing workflow...",
        "messages": [],
        "logs": [f"Workflow initialized with {len(creditor_states)} creditors"],
        "has_error": False,
        "error_message": None,
        "started_at": dt.utcnow().isoformat(),
        "completed_at": None
    }


async def init_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Initialize processing for the current creditor.

    Creates directory structure and prepares for fact-checking.

    This node also handles the InputState -> WorkflowState conversion
    when the workflow is started via API with minimal input.
    """
    # Check if this is a minimal InputState (missing internal tracking fields)
    if "current_creditor_index" not in state:
        logger.info("Detected InputState input, converting to WorkflowState...")
        state = _convert_input_to_workflow_state(state)

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
    Uses dynamic knowledge loading for enhanced prompts.

    CRITICAL: This node first reads the actual material content from file system,
    then passes it to the LLM as part of the prompt. Without this, the LLM
    would only see the file path and would fabricate data.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Fact-checking: {creditor['creditor_name']}")

    # Check if dynamic knowledge loading is enabled
    use_dynamic_knowledge = getattr(settings, 'USE_DYNAMIC_KNOWLEDGE', True)

    try:
        # ===== CRITICAL: Read material content from file system =====
        materials_path = creditor.get("materials_path", "")
        materials_content = ""
        materials_meta = {}

        if materials_path:
            logger.info(f"Reading materials from: {materials_path}")
            materials_content, materials_meta = await read_materials(materials_path)

            if materials_content:
                logger.info(f"Materials loaded successfully: {materials_meta.get('file_name', 'directory')}, "
                           f"size={materials_meta.get('file_size', materials_meta.get('total_size', 0))} chars, "
                           f"estimated_tokens={materials_meta.get('estimated_tokens', 0):.0f}")
            else:
                logger.warning(f"Failed to read materials: {materials_meta.get('error', 'Unknown error')}")
                # Log warning but continue - LLM will work with limited info
                await db.add_task_log(
                    task_id=state["task_id"],
                    message=f"Warning: Could not read materials for {creditor['creditor_name']}: {materials_meta.get('error')}",
                    level="warning",
                    stage="fact_check",
                    creditor_id=creditor["creditor_id"]
                )
        else:
            logger.warning(f"No materials_path provided for {creditor['creditor_name']}")
        # ===== End of material reading =====

        # Get LLM
        llm = get_llm()

        # Create prompt with creditor context AND material content
        if use_dynamic_knowledge:
            prompt = await create_fact_check_prompt_async(
                creditor_name=creditor["creditor_name"],
                materials_path=creditor["materials_path"],
                bankruptcy_date=state["bankruptcy_date"],
                debtor_name=state["debtor_name"],
                materials_content=materials_content,  # Pass actual content!
                use_dynamic_knowledge=True
            )
        else:
            # For legacy sync version, still need to pass materials_content somehow
            # But the sync version doesn't support it, so use async anyway
            prompt = await create_fact_check_prompt_async(
                creditor_name=creditor["creditor_name"],
                materials_path=creditor["materials_path"],
                bankruptcy_date=state["bankruptcy_date"],
                debtor_name=state["debtor_name"],
                materials_content=materials_content,
                use_dynamic_knowledge=False
            )

        # Call LLM
        response = await llm.ainvoke(prompt)
        fact_check_report = response.content

        # Update creditor state
        creditor["fact_check_report"] = fact_check_report
        creditor["stage_completed"]["fact_check"] = True

        # Determine if legal diagram should be generated
        should_generate = should_generate_legal_diagram(fact_check_report)
        creditor["should_generate_diagram"] = should_generate
        logger.info(f"Legal diagram generation needed: {should_generate}")

        creditor["current_stage"] = WorkflowStage.LEGAL_DIAGRAM

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.LEGAL_DIAGRAM
        state["status_message"] = f"Fact-check complete for {creditor['creditor_name']}, checking legal diagram..."

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

        # ===== Checkpoint 1: After Fact-Check (MUST PASS) =====
        checkpoint_result = run_checkpoint("fact_check", state, creditor)
        logger.info(f"Checkpoint 1 result: {checkpoint_result.status.value}")

        if checkpoint_result.status == CheckpointStatus.FAILED:
            creditor["errors"].extend(checkpoint_result.checks_failed)
            await db.add_task_log(
                task_id=state["task_id"],
                message=f"Checkpoint 1 FAILED: {', '.join(checkpoint_result.checks_failed)}",
                level="warning",
                stage="fact_check",
                creditor_id=creditor["creditor_id"],
                details=checkpoint_result.to_dict()
            )
        elif checkpoint_result.warnings:
            await db.add_task_log(
                task_id=state["task_id"],
                message=f"Checkpoint 1 WARNINGS: {', '.join(checkpoint_result.warnings)}",
                level="warning",
                stage="fact_check",
                creditor_id=creditor["creditor_id"]
            )

        return {
            **state,
            "logs": [f"Fact-check completed for {creditor['creditor_name']} (Checkpoint: {checkpoint_result.status.value})"],
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


async def legal_diagram_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate legal relationship diagram for the current creditor.

    This node is executed after fact_check and before analysis.
    It generates a Mermaid diagram visualizing:
    - Parties involved (creditor, debtor, guarantors)
    - Collateral relationships
    - Contract relationships
    - Debt assignment chain (if applicable)

    Generation conditions (any one triggers diagram generation):
    - ≥1 guarantor/保证人
    - ≥1 collateral (抵押/质押)
    - ≥2 debt claims (多笔债权)
    - Debt assignment exists (债权转让)

    Output: {债权人名称}_法律关系图.md in 工作底稿 directory
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Legal diagram stage: {creditor['creditor_name']}")

    try:
        # Check if diagram generation is needed
        should_generate = creditor.get("should_generate_diagram", False)

        if not should_generate:
            logger.info(f"Skipping legal diagram for {creditor['creditor_name']} - not needed")
            # Update stage and proceed to analysis
            creditor["stage_completed"]["legal_diagram"] = True
            creditor["current_stage"] = WorkflowStage.ANALYSIS
            creditor["legal_diagram"] = None

            state["creditors"][current_idx] = creditor
            state["current_stage"] = WorkflowStage.ANALYSIS
            state["status_message"] = f"Legal diagram skipped for {creditor['creditor_name']}, proceeding to analysis..."

            await db.add_task_log(
                task_id=state["task_id"],
                message=f"Legal diagram skipped for {creditor['creditor_name']} (simple case)",
                level="info",
                stage="legal_diagram",
                creditor_id=creditor["creditor_id"]
            )

            return {
                **state,
                "logs": [f"Legal diagram skipped for {creditor['creditor_name']}"],
                "progress_percent": calculate_progress(state)
            }

        # Generate legal diagram
        logger.info(f"Generating legal diagram for {creditor['creditor_name']}")

        llm = get_llm()

        # Create prompt for legal diagram generation
        prompt = await create_legal_diagram_prompt_async(
            creditor_name=creditor["creditor_name"],
            fact_check_report=creditor.get("fact_check_report", ""),
            bankruptcy_date=state["bankruptcy_date"],
            debtor_name=state["debtor_name"]
        )

        # Call LLM
        response = await llm.ainvoke(prompt)
        legal_diagram = response.content

        # Update creditor state
        creditor["legal_diagram"] = legal_diagram
        creditor["stage_completed"]["legal_diagram"] = True
        creditor["current_stage"] = WorkflowStage.ANALYSIS

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.ANALYSIS
        state["status_message"] = f"Legal diagram generated for {creditor['creditor_name']}, proceeding to analysis..."

        # Save legal diagram to file
        import asyncio

        output_path = Path(creditor.get("output_path", "./outputs"))

        def write_legal_diagram():
            work_papers_dir = output_path / "工作底稿"
            work_papers_dir.mkdir(parents=True, exist_ok=True)

            diagram_file = work_papers_dir / f"{creditor['creditor_name']}_法律关系图.md"
            diagram_file.write_text(legal_diagram, encoding="utf-8")
            logger.info(f"Saved legal diagram: {diagram_file}")
            return diagram_file

        diagram_file = await asyncio.to_thread(write_legal_diagram)

        # Save to database
        await db.create_report({
            "creditor_id": creditor["creditor_id"],
            "task_id": state["task_id"],
            "report_type": "legal_diagram",
            "file_name": f"{creditor['creditor_name']}_法律关系图.md",
            "file_path": str(diagram_file),
            "content_preview": legal_diagram[:500] if legal_diagram else None
        })

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Legal diagram generated for {creditor['creditor_name']}",
            level="info",
            stage="legal_diagram",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"Legal diagram generated for {creditor['creditor_name']}"],
            "progress_percent": calculate_progress(state)
        }

    except Exception as e:
        logger.error(f"Legal diagram generation failed: {e}")
        # Don't fail the entire workflow for diagram generation
        # Just log the error and proceed to analysis
        creditor["errors"].append(f"Legal diagram error: {str(e)}")
        creditor["stage_completed"]["legal_diagram"] = True
        creditor["current_stage"] = WorkflowStage.ANALYSIS
        creditor["legal_diagram"] = None

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.ANALYSIS

        await db.add_task_log(
            task_id=state["task_id"],
            message=f"Legal diagram generation failed for {creditor['creditor_name']}: {str(e)}",
            level="warning",
            stage="legal_diagram",
            creditor_id=creditor["creditor_id"]
        )

        return {
            **state,
            "logs": [f"WARNING: Legal diagram failed for {creditor['creditor_name']}, proceeding to analysis"],
            "progress_percent": calculate_progress(state)
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
    Uses dynamic knowledge loading for enhanced prompts with legal standards.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Analyzing: {creditor['creditor_name']}")

    # Check if dynamic knowledge loading is enabled
    use_dynamic_knowledge = getattr(settings, 'USE_DYNAMIC_KNOWLEDGE', True)

    try:
        llm = get_llm()

        # Create analysis prompt with fact-check report (using async version for dynamic knowledge)
        if use_dynamic_knowledge:
            prompt = await create_analysis_prompt_async(
                creditor_name=creditor["creditor_name"],
                fact_check_report=creditor["fact_check_report"],
                bankruptcy_date=state["bankruptcy_date"],
                interest_stop_date=state["interest_stop_date"],
                declared_amounts={
                    "principal": creditor.get("declared_principal"),
                    "interest": creditor.get("declared_interest"),
                    "total": creditor.get("declared_total")
                },
                use_dynamic_knowledge=True
            )
        else:
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

        # Categorize calculation results by type
        lpr_interest_total = 0.0  # 普通利息（LPR、simple等）
        delay_interest_total = 0.0  # 迟延履行利息

        for result in calculation_results:
            calc_type = result.get("calculation_type", "")
            interest = result.get("interest", 0)
            if calc_type == "delay":
                delay_interest_total += interest
            else:
                lpr_interest_total += interest

        # Append calculation results to analysis report with detailed breakdown
        if calculation_results:
            calc_summary = "\n\n=== 利息计算结果（由系统自动计算）===\n"
            for i, result in enumerate(calculation_results, 1):
                calc_type = result.get("calculation_type", "unknown")
                type_label = {
                    "lpr": "LPR浮动利率",
                    "simple": "固定利率",
                    "delay": "迟延履行利息",
                    "penalty": "罚息"
                }.get(calc_type, calc_type)

                calc_summary += f"\n计算{i} ({type_label}):\n"
                calc_summary += f"  本金: {result.get('principal', 0):,.2f}元\n"
                calc_summary += f"  利息: {result.get('interest', 0):,.2f}元\n"
                calc_summary += f"  合计: {result.get('total', 0):,.2f}元\n"
                calc_summary += f"  计算天数: {result.get('days', result.get('total_days', 0))}天\n"

                # 对于迟延履行利息，显示日利率
                if calc_type == "delay":
                    calc_summary += f"  日利率: {result.get('daily_rate', '万分之1.75')}\n"
                    calc_summary += f"  法律依据: {result.get('legal_basis', '《民事诉讼法》第260条')}\n"

            calc_summary += f"\n--- 汇总 ---\n"
            calc_summary += f"普通利息合计: {lpr_interest_total:,.2f}元\n"
            calc_summary += f"迟延履行利息合计: {delay_interest_total:,.2f}元\n"
            analysis_report += calc_summary

        # ===== Apply 就低原则 with proper categorization =====
        declared_principal = creditor.get("declared_principal") or 0
        declared_interest = creditor.get("declared_interest") or 0  # 普通利息申报金额
        declared_total = creditor.get("declared_total") or 0

        # 确认本金（通常直接采用申报金额，除非有证据不支持）
        confirmed_principal = declared_principal

        # 确认普通利息 - 就低原则
        if declared_interest:
            confirmed_lpr_interest = min(lpr_interest_total, declared_interest)
        else:
            confirmed_lpr_interest = lpr_interest_total

        # 迟延履行利息 - 需要单独处理
        # 从申报材料中提取迟延履行利息申报金额（这里需要从creditor信息或分析报告中提取）
        # 暂时使用delay计算结果，在最终报告中会通过LLM判断应用就低原则
        confirmed_delay_interest = delay_interest_total

        # 总利息 = 普通利息 + 迟延履行利息
        confirmed_interest = confirmed_lpr_interest
        confirmed_total = confirmed_principal + confirmed_lpr_interest + confirmed_delay_interest

        # Apply final 就低原则 on total
        if declared_total and confirmed_total > declared_total:
            confirmed_total = declared_total

        # Store categorized results for later use
        creditor["calculated_lpr_interest"] = lpr_interest_total
        creditor["calculated_delay_interest"] = delay_interest_total
        creditor["confirmed_lpr_interest"] = confirmed_lpr_interest
        creditor["confirmed_delay_interest"] = confirmed_delay_interest

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

        # ===== Checkpoint 2: After Analysis (MUST PASS) =====
        checkpoint_result = run_checkpoint("analysis", state, creditor)
        logger.info(f"Checkpoint 2 result: {checkpoint_result.status.value}")

        if checkpoint_result.status == CheckpointStatus.FAILED:
            creditor["errors"].extend(checkpoint_result.checks_failed)
            await db.add_task_log(
                task_id=state["task_id"],
                message=f"Checkpoint 2 FAILED: {', '.join(checkpoint_result.checks_failed)}",
                level="warning",
                stage="analysis",
                creditor_id=creditor["creditor_id"],
                details=checkpoint_result.to_dict()
            )
        elif checkpoint_result.warnings:
            await db.add_task_log(
                task_id=state["task_id"],
                message=f"Checkpoint 2 WARNINGS: {', '.join(checkpoint_result.warnings)}",
                level="warning",
                stage="analysis",
                creditor_id=creditor["creditor_id"]
            )

        return {
            **state,
            "logs": [f"Analysis completed for {creditor['creditor_name']} (Checkpoint: {checkpoint_result.status.value})"],
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
    Uses dynamic knowledge loading for report formatting standards.
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Generating report: {creditor['creditor_name']}")

    # Check if dynamic knowledge loading is enabled
    use_dynamic_knowledge = getattr(settings, 'USE_DYNAMIC_KNOWLEDGE', True)

    try:
        llm = get_llm()

        # Create report prompt (using async version for dynamic knowledge)
        if use_dynamic_knowledge:
            prompt = await create_report_prompt_async(
                creditor_name=creditor["creditor_name"],
                fact_check_report=creditor["fact_check_report"],
                analysis_report=creditor["analysis_report"],
                debtor_name=state["debtor_name"],
                bankruptcy_date=state["bankruptcy_date"],
                use_dynamic_knowledge=True
            )
        else:
            prompt = create_report_prompt(
                creditor_name=creditor["creditor_name"],
                fact_check_report=creditor["fact_check_report"],
                analysis_report=creditor["analysis_report"],
                debtor_name=state["debtor_name"],
                bankruptcy_date=state["bankruptcy_date"]
            )

        response = await llm.ainvoke(prompt)
        raw_report = response.content

        # ===== TEMPLATE ENFORCEMENT (MANDATORY) =====
        # Apply template compliance - convert Markdown to pure text format
        # This matches the original solution's zero-tolerance format requirements
        compliant_report, validation_result = enforce_template_compliance(raw_report)

        if not validation_result.passed:
            logger.warning(
                f"Report format conversion applied for {creditor['creditor_name']}: "
                f"{len(validation_result.violations)} violations fixed"
            )
            await db.add_task_log(
                task_id=state["task_id"],
                message=f"Template enforcement: {len(validation_result.violations)} format violations auto-fixed",
                level="info",
                stage="report",
                creditor_id=creditor["creditor_id"],
                details=validation_result.to_dict()
            )

        # Use compliant report (format converted)
        final_report = compliant_report

        creditor["final_report"] = final_report
        creditor["template_validation"] = validation_result.to_dict()
        creditor["stage_completed"]["report"] = True
        creditor["current_stage"] = WorkflowStage.VALIDATION

        state["creditors"][current_idx] = creditor
        state["current_stage"] = WorkflowStage.VALIDATION
        state["status_message"] = f"Report generated for {creditor['creditor_name']}, validating..."

        # Save final report (now in compliant format)
        report_date = datetime.now().strftime("%Y%m%d")

        # ===== Write files to disk (using asyncio.to_thread for non-blocking) =====
        import asyncio

        output_path = Path(creditor.get("output_path", "./outputs"))

        def write_files():
            """
            Synchronous file writing wrapped for async execution.

            Directory structure matches original solution:
            outputs/batch_X/N-债权人名称/
            ├── 工作底稿/
            │   ├── XX_事实核查报告.md
            │   └── XX_债权分析报告.md
            ├── 最终报告/
            │   └── GY2025_XX_债权审查报告_日期.md
            └── 计算文件/
                └── XX_利息计算结果.json
            """
            # Create subdirectory structure
            work_papers_dir = output_path / "工作底稿"
            final_reports_dir = output_path / "最终报告"
            calculation_dir = output_path / "计算文件"

            work_papers_dir.mkdir(parents=True, exist_ok=True)
            final_reports_dir.mkdir(parents=True, exist_ok=True)
            calculation_dir.mkdir(parents=True, exist_ok=True)

            # Write fact-check report (工作底稿)
            fact_check_file = work_papers_dir / f"{creditor['creditor_name']}_事实核查报告.md"
            fact_check_file.write_text(creditor.get("fact_check_report", ""), encoding="utf-8")
            logger.info(f"Saved fact-check report: {fact_check_file}")

            # Write analysis report (工作底稿)
            analysis_file = work_papers_dir / f"{creditor['creditor_name']}_债权分析报告.md"
            analysis_file.write_text(creditor.get("analysis_report", ""), encoding="utf-8")
            logger.info(f"Saved analysis report: {analysis_file}")

            # Write final report (最终报告)
            final_file = final_reports_dir / f"GY2025_{creditor['creditor_name']}_债权审查报告_{report_date}.md"
            final_file.write_text(final_report, encoding="utf-8")
            logger.info(f"Saved final report: {final_file}")

            # Write calculation results (计算文件)
            if creditor.get("calculation_results"):
                # Save JSON file
                calc_file = calculation_dir / f"{creditor['creditor_name']}_利息计算结果.json"
                calc_file.write_text(json.dumps(creditor["calculation_results"], ensure_ascii=False, indent=2), encoding="utf-8")
                logger.info(f"Saved calculation results (JSON): {calc_file}")

                # Save Excel file with detailed calculation breakdown
                excel_file = calculation_dir / f"{creditor['creditor_name']}_利息计算明细.xlsx"
                claimed_amounts = {
                    "利息损失": creditor.get("declared_interest"),
                    "迟延履行利息": creditor.get("declared_delay_interest")
                }
                # Filter out None values
                claimed_amounts = {k: v for k, v in claimed_amounts.items() if v is not None}

                try:
                    export_to_excel(
                        results=creditor["calculation_results"],
                        creditor_name=creditor['creditor_name'],
                        output_path=str(excel_file),
                        claimed_amounts=claimed_amounts if claimed_amounts else None
                    )
                    logger.info(f"Saved calculation results (Excel): {excel_file}")
                except Exception as e:
                    logger.warning(f"Failed to export Excel file: {e}")

            return final_file

        # Execute file writing in a thread pool to avoid blocking
        final_file = await asyncio.to_thread(write_files)

        # Save to database
        await db.create_report({
            "creditor_id": creditor["creditor_id"],
            "task_id": state["task_id"],
            "report_type": "final",
            "file_name": f"GY2025_{creditor['creditor_name']}_债权审查报告_{report_date}.txt",
            "file_path": str(final_file),
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

    Uses Checkpoint 3 from the original solution:
    - Format compliance (NO Markdown markers)
    - Date consistency (three-way)
    - Content completeness
    - Template compliance
    """
    current_idx = state["current_creditor_index"]
    creditor = state["creditors"][current_idx]

    logger.info(f"Validating: {creditor['creditor_name']}")

    try:
        # ===== Checkpoint 3: After Report (MUST PASS) =====
        checkpoint_result = run_checkpoint("report", state, creditor)
        logger.info(f"Checkpoint 3 result: {checkpoint_result.status.value}")

        validation_errors = checkpoint_result.checks_failed.copy()
        validation_warnings = checkpoint_result.warnings.copy()

        if validation_errors:
            creditor["errors"].extend(validation_errors)
            logger.warning(f"Checkpoint 3 FAILED for {creditor['creditor_name']}: {validation_errors}")

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
            message=f"Checkpoint 3 {checkpoint_result.status.value}: {len(checkpoint_result.checks_passed)} passed, {len(validation_errors)} failed, {len(validation_warnings)} warnings",
            level="warning" if validation_errors or validation_warnings else "info",
            stage="validation",
            creditor_id=creditor["creditor_id"],
            details=checkpoint_result.to_dict()
        )

        return {
            **state,
            "logs": [f"Validation completed for {creditor['creditor_name']} (Checkpoint: {checkpoint_result.status.value})"],
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
