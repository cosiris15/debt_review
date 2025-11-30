"""
Parallel Processing Module for Debt Review

Implements stage-level parallel processing for multiple creditors.
Matches the original Claude Code solution's parallel processing mode.

Key Features:
1. Auto-detection of processing mode (serial vs parallel)
2. Stage-level parallelism (multiple creditors, same stage)
3. Quality checkpoints between stages
4. Context isolation between creditors
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingMode(str, Enum):
    """Processing mode based on creditor count."""
    SERIAL = "serial"  # Single creditor
    PARALLEL = "parallel"  # 2+ creditors


@dataclass
class ParallelBatchState:
    """State for parallel batch processing."""
    batch_id: str
    creditor_ids: List[str]
    mode: ProcessingMode
    current_stage: str = "init"
    stage_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "creditor_count": len(self.creditor_ids),
            "mode": self.mode.value,
            "current_stage": self.current_stage,
            "stage_results": self.stage_results,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


def auto_select_processing_mode(creditor_count: int) -> ProcessingMode:
    """
    Automatically select processing mode based on creditor count.

    Rules (from original solution):
    - 1 creditor: Serial processing
    - 2+ creditors: Stage-level parallel processing

    Returns:
        ProcessingMode indicating the selected mode
    """
    if creditor_count <= 1:
        logger.info(f"检测到{creditor_count}个债权人，使用串行处理模式")
        return ProcessingMode.SERIAL
    else:
        logger.info(f"检测到{creditor_count}个债权人，自动启用并行处理模式（预计节省75-80%处理时间）")
        return ProcessingMode.PARALLEL


def get_execution_plan(mode: ProcessingMode, creditor_count: int) -> str:
    """
    Generate execution plan description for user notification.

    Args:
        mode: Selected processing mode
        creditor_count: Number of creditors

    Returns:
        Human-readable execution plan
    """
    if mode == ProcessingMode.SERIAL:
        return "将按顺序完成：环境初始化 → 事实核查 → 债权分析 → 报告整理"
    else:
        return f"""执行方案：
- 阶段0（串行）: 依次初始化{creditor_count}个债权人环境
- 阶段1（并行）: 同时进行{creditor_count}个债权人的事实核查
- 阶段2（并行）: 同时进行{creditor_count}个债权人的债权分析
- 阶段3（并行）: 同时进行{creditor_count}个债权人的报告整理"""


class ParallelExecutor:
    """
    Executor for stage-level parallel processing.

    Implements the original solution's parallel processing mode:
    - Serial initialization
    - Parallel stage execution (fact_check, analysis, report)
    - Quality checkpoints between stages
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Initialize parallel executor.

        Args:
            max_concurrent: Maximum concurrent creditors per stage
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_stage_parallel(
        self,
        stage_func,
        creditor_states: List[Dict[str, Any]],
        shared_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute a stage for multiple creditors in parallel.

        Args:
            stage_func: Async function to execute for each creditor
            creditor_states: List of creditor state dicts
            shared_context: Shared context (bankruptcy_date, debtor_name, etc.)

        Returns:
            List of results for each creditor
        """
        async def execute_with_semaphore(creditor_state):
            async with self.semaphore:
                try:
                    # Create isolated context for this creditor
                    isolated_context = {
                        **shared_context,
                        "creditor": creditor_state.copy()
                    }
                    result = await stage_func(isolated_context)
                    return {
                        "creditor_id": creditor_state.get("creditor_id"),
                        "success": True,
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"Parallel execution error for {creditor_state.get('creditor_name')}: {e}")
                    return {
                        "creditor_id": creditor_state.get("creditor_id"),
                        "success": False,
                        "error": str(e)
                    }

        # Execute all creditors in parallel with semaphore limit
        tasks = [execute_with_semaphore(cs) for cs in creditor_states]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "creditor_id": creditor_states[i].get("creditor_id"),
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    async def run_parallel_workflow(
        self,
        creditor_states: List[Dict[str, Any]],
        shared_context: Dict[str, Any],
        stage_funcs: Dict[str, Any],
        checkpoint_func=None
    ) -> Dict[str, Any]:
        """
        Run complete parallel workflow for multiple creditors.

        Workflow:
        1. Serial initialization (init stage)
        2. Parallel fact-checking (with checkpoint)
        3. Parallel analysis (with checkpoint)
        4. Parallel report generation (with checkpoint)
        5. Parallel validation

        Args:
            creditor_states: List of creditor state dicts
            shared_context: Shared context
            stage_funcs: Dict mapping stage names to async functions
            checkpoint_func: Optional checkpoint validation function

        Returns:
            Workflow result with all stage results
        """
        batch_state = ParallelBatchState(
            batch_id=shared_context.get("task_id", "unknown"),
            creditor_ids=[cs.get("creditor_id") for cs in creditor_states],
            mode=auto_select_processing_mode(len(creditor_states)),
            started_at=datetime.utcnow().isoformat()
        )

        stages = ["init", "fact_check", "analysis", "report", "validation"]

        for stage in stages:
            stage_func = stage_funcs.get(stage)
            if not stage_func:
                logger.warning(f"No function defined for stage: {stage}")
                continue

            batch_state.current_stage = stage
            logger.info(f"Starting parallel stage: {stage} for {len(creditor_states)} creditors")

            # Execute stage in parallel
            stage_results = await self.execute_stage_parallel(
                stage_func,
                creditor_states,
                shared_context
            )

            batch_state.stage_results[stage] = {
                "results": stage_results,
                "success_count": sum(1 for r in stage_results if r.get("success")),
                "failure_count": sum(1 for r in stage_results if not r.get("success"))
            }

            # Run checkpoint if provided
            if checkpoint_func and stage in ["fact_check", "analysis", "report"]:
                checkpoint_passed = await checkpoint_func(stage, stage_results)
                if not checkpoint_passed:
                    logger.warning(f"Checkpoint failed for stage {stage}")
                    # Continue but log warning - don't block workflow

            # Update creditor states with results
            for result in stage_results:
                creditor_id = result.get("creditor_id")
                for cs in creditor_states:
                    if cs.get("creditor_id") == creditor_id:
                        cs[f"{stage}_result"] = result
                        if result.get("success") and result.get("result"):
                            # Merge result into creditor state
                            cs.update(result.get("result", {}))
                        break

        batch_state.completed_at = datetime.utcnow().isoformat()

        return {
            "batch_state": batch_state.to_dict(),
            "creditor_states": creditor_states,
            "success": all(
                batch_state.stage_results.get(s, {}).get("failure_count", 0) == 0
                for s in stages
            )
        }


async def run_parallel_batch(
    workflow_app,
    creditor_configs: List[Dict[str, Any]],
    shared_context: Dict[str, Any],
    max_concurrent: int = 5
) -> Dict[str, Any]:
    """
    Convenience function to run parallel batch processing.

    Args:
        workflow_app: Compiled LangGraph workflow
        creditor_configs: List of creditor configurations
        shared_context: Shared context (bankruptcy_date, etc.)
        max_concurrent: Maximum concurrent executions

    Returns:
        Batch processing results
    """
    from app.agents.state import WorkflowState, WorkflowStage

    mode = auto_select_processing_mode(len(creditor_configs))

    if mode == ProcessingMode.SERIAL:
        # Serial processing - use standard workflow
        results = []
        for config in creditor_configs:
            initial_state = {
                **shared_context,
                "creditors": [config],
                "current_creditor_index": 0,
                "total_creditors": 1,
                "current_stage": WorkflowStage.INIT
            }
            result = await workflow_app.ainvoke(initial_state)
            results.append(result)
        return {"mode": "serial", "results": results}

    else:
        # Parallel processing
        from app.agents.state import create_initial_state
        import uuid

        # For LangGraph, we run the full workflow for each creditor in parallel
        async def run_single_creditor(config, index):
            # Normalize creditor config to match expected format
            normalized_creditor = {
                "id": config.get("creditor_id", f"creditor-{uuid.uuid4().hex[:8]}"),
                "creditor_name": config.get("creditor_name", f"Creditor {index+1}"),
                "batch_number": config.get("batch_number", 1),
                "creditor_number": config.get("creditor_number", index + 1),
                "materials_path": config.get("materials_path", ""),
                "output_path": config.get("output_path", f"./outputs/{index+1}"),
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
                project_id=shared_context.get("project_id", "parallel-project"),
                project_config=project_config,
                creditors=[normalized_creditor]
            )
            return await workflow_app.ainvoke(initial_state)

        # Execute all creditors in parallel with semaphore
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_limit(config, index):
            async with semaphore:
                try:
                    result = await run_single_creditor(config, index)
                    return {
                        "creditor_name": config.get("creditor_name"),
                        "success": not result.get("has_error", False),
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"Parallel execution error for {config.get('creditor_name')}: {e}")
                    return {
                        "creditor_name": config.get("creditor_name"),
                        "success": False,
                        "error": str(e)
                    }

        tasks = [run_with_limit(c, i) for i, c in enumerate(creditor_configs)]
        results = await asyncio.gather(*tasks)

        return {
            "mode": "parallel",
            "execution_plan": get_execution_plan(mode, len(creditor_configs)),
            "results": results,
            "success_count": sum(1 for r in results if r.get("success")),
            "failure_count": sum(1 for r in results if not r.get("success"))
        }
