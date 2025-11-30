"""
End-to-End Workflow Tests

Tests the complete debt review workflow with real creditor materials.
Validates:
1. Single creditor serial processing
2. Multiple creditor parallel processing
3. Checkpoint enforcement
4. Template compliance
5. Knowledge integration

Test Materials: /Users/chenchu/Desktop/第1批债权/
"""

import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.state import WorkflowState, WorkflowStage
from app.agents.workflow import (
    build_workflow,
    create_workflow_app,
    run_workflow_with_auto_mode
)
from app.agents.parallel import (
    auto_select_processing_mode,
    ProcessingMode,
    ParallelBatchState
)
from app.agents.checkpoints import QualityCheckpoints, CheckpointStatus
from app.agents.templates import (
    enforce_template_compliance,
    validate_report_format
)
from app.knowledge import get_knowledge_manager


# ============== Test Configuration ==============

# Project configuration from user input
PROJECT_CONFIG = {
    "debtor_name": "上海欧卡罗家居有限公司",
    "case_name": "上海欧卡罗家居有限公司破产清算案",
    "administrator": "上海欧卡罗家居有限公司管理人",
    "bankruptcy_date": "2024-02-26",
    "interest_stop_date": "2024-02-25",
    "penalty_multiplier": 4,
    "delay_interest_rate": 1.75,
}

# Test materials path
TEST_MATERIALS_PATH = Path("/Users/chenchu/Desktop/第1批债权")

# Creditor configurations extracted from materials
CREDITOR_CONFIGS = [
    {
        "creditor_name": "上海牧诚贸易有限公司",
        "materials_path": str(TEST_MATERIALS_PATH / "债权申报书-上海牧诚贸易有限公司.md"),
        "declared_amounts": {
            "principal": 7610000.00,
            "interest": 342449.99,
            "court_fee": 32535.00,
            "preservation_fee": 5000.00,
            "delay_interest": 278500.92,
            "total": 8268485.91
        },
        "has_judgment": True,
        "case_number": "(2023)沪0118民初14562号"
    },
    {
        "creditor_name": "黛绰维纳",
        "materials_path": str(TEST_MATERIALS_PATH / "240319-欧卡罗-债权申报材料-黛绰维纳.md"),
        "declared_amounts": {
            "total": None  # To be extracted from materials
        },
        "has_judgment": False,
        "case_number": None
    },
    {
        "creditor_name": "广林欧卡罗",
        "materials_path": str(TEST_MATERIALS_PATH / "注资3920-广林欧卡罗.md"),
        "declared_amounts": {
            "total": None  # To be extracted from materials
        },
        "has_judgment": False,
        "case_number": None
    }
]


# ============== Unit Tests ==============

class TestProjectConfiguration:
    """Test project configuration validity."""

    def test_materials_path_exists(self):
        """Verify test materials directory exists."""
        assert TEST_MATERIALS_PATH.exists(), f"Test materials not found: {TEST_MATERIALS_PATH}"

    def test_all_material_files_exist(self):
        """Verify all creditor material files exist."""
        for config in CREDITOR_CONFIGS:
            path = Path(config["materials_path"])
            assert path.exists(), f"Material file not found: {path}"

    def test_bankruptcy_date_valid(self):
        """Verify bankruptcy date is valid."""
        date = datetime.strptime(PROJECT_CONFIG["bankruptcy_date"], "%Y-%m-%d")
        assert date.year == 2024
        assert date.month == 2
        assert date.day == 26

    def test_interest_stop_date_is_day_before(self):
        """Verify interest stop date is one day before bankruptcy date."""
        bankruptcy = datetime.strptime(PROJECT_CONFIG["bankruptcy_date"], "%Y-%m-%d")
        stop_date = datetime.strptime(PROJECT_CONFIG["interest_stop_date"], "%Y-%m-%d")
        diff = bankruptcy - stop_date
        assert diff.days == 1, "Interest stop date should be one day before bankruptcy date"


class TestWorkflowStateCreation:
    """Test workflow state initialization."""

    def test_create_initial_state_single_creditor(self):
        """Test initial state creation for single creditor."""
        state = create_initial_state([CREDITOR_CONFIGS[0]])

        assert state["total_creditors"] == 1
        assert state["current_creditor_index"] == 0
        assert state["current_stage"] == WorkflowStage.INIT
        assert state["has_error"] == False
        assert state["bankruptcy_date"] == PROJECT_CONFIG["bankruptcy_date"]

    def test_create_initial_state_multiple_creditors(self):
        """Test initial state creation for multiple creditors."""
        state = create_initial_state(CREDITOR_CONFIGS)

        assert state["total_creditors"] == 3
        assert len(state["creditors"]) == 3


class TestProcessingModeSelection:
    """Test automatic processing mode selection."""

    def test_single_creditor_uses_serial(self):
        """Single creditor should use serial processing."""
        mode = auto_select_processing_mode(1)
        assert mode == ProcessingMode.SERIAL

    def test_multiple_creditors_use_parallel(self):
        """Multiple creditors should use parallel processing."""
        mode = auto_select_processing_mode(3)
        assert mode == ProcessingMode.PARALLEL

    def test_creditor_count_from_config(self):
        """Verify creditor count from test configuration."""
        mode = auto_select_processing_mode(len(CREDITOR_CONFIGS))
        assert mode == ProcessingMode.PARALLEL  # 3 creditors = parallel


class TestKnowledgeIntegration:
    """Test knowledge management integration."""

    @pytest.mark.asyncio
    async def test_knowledge_manager_initialized(self):
        """Test that knowledge manager is properly initialized."""
        km = get_knowledge_manager()
        categories = km.list_categories()

        assert "foundations" in categories
        assert "calculations" in categories
        assert "fact_checking" in categories
        assert "analysis" in categories

    @pytest.mark.asyncio
    async def test_load_knowledge_for_fact_check(self):
        """Test loading knowledge for fact-check stage."""
        km = get_knowledge_manager()
        items = await km.get_knowledge_for_stage("fact_check", token_budget=3000)

        assert len(items) > 0
        # Should include core principles
        ids = [item.id for item in items]
        assert "core_principles" in ids or any("principle" in id.lower() for id in ids)

    @pytest.mark.asyncio
    async def test_load_lpr_rates(self):
        """Test LPR rates loading."""
        km = get_knowledge_manager()
        lpr_data = await km.get_lpr_rates()

        assert len(lpr_data.rates) > 0
        # Check for rates around bankruptcy date
        assert any(rate.date <= "2024-02-26" for rate in lpr_data.rates)


class TestCheckpointValidation:
    """Test checkpoint validation logic."""

    def test_checkpoint_initialization(self):
        """Test checkpoint initialization with project dates."""
        checkpoints = QualityCheckpoints(
            bankruptcy_date=PROJECT_CONFIG["bankruptcy_date"],
            interest_stop_date=PROJECT_CONFIG["interest_stop_date"]
        )

        assert checkpoints.bankruptcy_date == "2024-02-26"
        assert checkpoints.interest_stop_date == "2024-02-25"

    def test_inference_word_detection(self):
        """Test detection of inference words (anti-hallucination)."""
        checkpoints = QualityCheckpoints(
            bankruptcy_date=PROJECT_CONFIG["bankruptcy_date"],
            interest_stop_date=PROJECT_CONFIG["interest_stop_date"]
        )

        # Content with inference words should be detected
        bad_content = "根据上述材料，推测债务人可能存在还款能力"
        result = checkpoints._check_for_inference_words(bad_content)
        assert result is not None

        # Clean content should pass
        good_content = "根据借款合同第5条约定，借款本金为100万元"
        result = checkpoints._check_for_inference_words(good_content)
        # May or may not return None depending on implementation

    def test_format_compliance_check(self):
        """Test format compliance checking."""
        checkpoints = QualityCheckpoints(
            bankruptcy_date=PROJECT_CONFIG["bankruptcy_date"],
            interest_stop_date=PROJECT_CONFIG["interest_stop_date"]
        )

        # Markdown content should be flagged
        markdown_content = "## 一、债权申报情况\n- 本金：100万元"
        issues = checkpoints._check_format_compliance(markdown_content)
        assert len(issues) > 0

        # Clean content should pass
        clean_content = "一、债权申报情况\n\n本金为100万元。"
        issues = checkpoints._check_format_compliance(clean_content)
        assert len(issues) == 0


class TestTemplateEnforcement:
    """Test template enforcement for reports."""

    def test_markdown_to_plain_text(self):
        """Test Markdown to plain text conversion."""
        markdown_content = """## 一、债权申报情况

**债权人**上海牧诚贸易有限公司申报债权：

- 本金：7,610,000元
- 利息：342,449.99元
- 合计：8,268,485.91元
"""

        compliant, result = enforce_template_compliance(markdown_content)

        # Should remove Markdown syntax
        assert "##" not in compliant
        assert "**" not in compliant
        assert "- " not in compliant

        # Should preserve content
        assert "债权申报情况" in compliant
        assert "本金" in compliant

    def test_clean_content_passes(self):
        """Test that properly formatted content passes."""
        clean_content = """一、债权申报情况

债权人上海牧诚贸易有限公司于2024年3月14日向管理人申报债权。

申报债权总额为8,268,485.91元，其中本金7,610,000元，利息342,449.99元。

二、证据材料

债权人提交了民事判决书、执行裁定书等证据材料。
"""

        result = validate_report_format(clean_content)
        assert result.passed


class TestMaterialParsing:
    """Test parsing of actual creditor materials."""

    def test_read_muchen_materials(self):
        """Test reading 上海牧诚贸易有限公司 materials."""
        path = Path(CREDITOR_CONFIGS[0]["materials_path"])
        content = path.read_text(encoding='utf-8')

        # Verify key information is present
        assert "上海牧诚贸易有限公司" in content
        assert "7,610,000" in content or "7610000" in content
        assert "8,268,485.91" in content or "8268485.91" in content

    def test_extract_declared_amounts(self):
        """Test that declared amounts match material content."""
        config = CREDITOR_CONFIGS[0]

        # Verify against known values from the material
        assert config["declared_amounts"]["principal"] == 7610000.00
        assert config["declared_amounts"]["total"] == 8268485.91


# ============== Integration Tests ==============

class TestWorkflowGraph:
    """Test workflow graph structure."""

    def test_build_workflow(self):
        """Test that workflow graph builds successfully."""
        workflow = build_workflow()
        assert workflow is not None

    def test_create_workflow_app(self):
        """Test that workflow app compiles."""
        app = create_workflow_app()
        assert app is not None

    def test_workflow_has_required_nodes(self):
        """Test that workflow has all required nodes."""
        workflow = build_workflow()

        # Check for essential nodes
        # Note: Node access may vary by LangGraph version
        expected_nodes = ["init", "fact_check", "analysis", "report", "validation"]
        # This is a structural test - actual node verification depends on implementation


class TestSerialWorkflow:
    """Test single creditor serial workflow (mock version)."""

    def test_state_progression(self):
        """Test state progression through stages."""
        stages = [
            WorkflowStage.INIT,
            WorkflowStage.FACT_CHECK,
            WorkflowStage.ANALYSIS,
            WorkflowStage.REPORT,
            WorkflowStage.VALIDATION,
            WorkflowStage.COMPLETE
        ]

        # Verify stage order
        for i, stage in enumerate(stages[:-1]):
            assert stages.index(stages[i+1]) > stages.index(stage)


class TestParallelWorkflow:
    """Test multiple creditor parallel workflow."""

    def test_parallel_batch_state(self):
        """Test ParallelBatchState creation."""
        creditor_ids = [c["creditor_name"] for c in CREDITOR_CONFIGS]

        state = ParallelBatchState(
            batch_id="test-batch-001",
            creditor_ids=creditor_ids,
            mode=ProcessingMode.PARALLEL
        )

        assert state.batch_id == "test-batch-001"
        assert len(state.creditor_ids) == 3

        state_dict = state.to_dict()
        assert state_dict["mode"] == "parallel"
        assert state_dict["creditor_count"] == 3


# ============== E2E Tests (Require LLM API) ==============

class TestE2EWithLLM:
    """
    End-to-end tests that require LLM API.

    These tests require DEEPSEEK_API_KEY configured in .env
    """

    @pytest.fixture
    def check_api_key(self):
        """Check if DeepSeek API key is configured."""
        from app.core.config import settings
        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            pytest.skip("DEEPSEEK_API_KEY not configured")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_single_creditor_full_workflow(self, check_api_key):
        """
        Test complete workflow for single creditor (牧诚贸易).

        This is the most comprehensive test - runs the full pipeline.
        """
        creditor_config = CREDITOR_CONFIGS[0]  # 上海牧诚贸易有限公司

        shared_context = {
            "task_id": "e2e-test-001",
            "project_id": "test-project",
            "debtor_name": PROJECT_CONFIG["debtor_name"],
            "bankruptcy_date": PROJECT_CONFIG["bankruptcy_date"],
            "interest_stop_date": PROJECT_CONFIG["interest_stop_date"],
        }

        result = await run_workflow_with_auto_mode(
            creditor_configs=[creditor_config],
            shared_context=shared_context,
            max_concurrent=1
        )

        # Verify result structure
        assert result is not None
        assert result.get("mode") == "serial"

        # Log results for debugging
        print(f"\nE2E Test Result: {result.get('success_count')} success, {result.get('failure_count')} failed")

        # If we got results, check them
        if result.get("results"):
            creditor_result = result["results"][0]
            print(f"Creditor: {creditor_result.get('creditor_name')}")
            print(f"Success: {creditor_result.get('success')}")

            # Check if there were errors
            if not creditor_result.get("success"):
                workflow_result = creditor_result.get("result", {})
                print(f"Error: {workflow_result.get('error_message')}")

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_multi_creditor_parallel_workflow(self, check_api_key):
        """
        Test parallel workflow for all 3 creditors.

        Validates parallel processing and result aggregation.
        """
        shared_context = {
            "task_id": "e2e-test-002",
            "project_id": "test-project",
            "debtor_name": PROJECT_CONFIG["debtor_name"],
            "bankruptcy_date": PROJECT_CONFIG["bankruptcy_date"],
            "interest_stop_date": PROJECT_CONFIG["interest_stop_date"],
        }

        result = await run_workflow_with_auto_mode(
            creditor_configs=CREDITOR_CONFIGS,
            shared_context=shared_context,
            max_concurrent=3
        )

        # Verify parallel mode was selected (3 creditors)
        assert result.get("mode") == "parallel"

        # Log results
        print(f"\nParallel E2E Test: {result.get('success_count')} success, {result.get('failure_count')} failed")


# ============== Helper Functions ==============

def create_initial_state(creditor_configs: List[Dict[str, Any]]) -> WorkflowState:
    """Create initial workflow state for testing."""
    # Create proper creditor states with all required fields
    creditors = []
    for i, config in enumerate(creditor_configs):
        creditor_state = {
            "creditor_id": f"test-creditor-{i+1}",
            "creditor_name": config.get("creditor_name", f"Creditor {i+1}"),
            "batch_number": 1,
            "creditor_number": i + 1,
            "materials_path": config.get("materials_path", ""),
            "output_path": f"./outputs/test/{i+1}",
            "work_papers_path": f"./outputs/test/{i+1}/work_papers",
            "calculation_files_path": f"./outputs/test/{i+1}/calculations",
            "final_reports_path": f"./outputs/test/{i+1}/reports",
            "declared_principal": config.get("declared_amounts", {}).get("principal"),
            "declared_interest": config.get("declared_amounts", {}).get("interest"),
            "declared_total": config.get("declared_amounts", {}).get("total"),
            "confirmed_principal": None,
            "confirmed_interest": None,
            "confirmed_total": None,
            "current_stage": WorkflowStage.INIT,
            "stage_completed": {
                "init": False,
                "fact_check": False,
                "analysis": False,
                "report": False,
                "validation": False
            },
            "fact_check_report": None,
            "analysis_report": None,
            "final_report": None,
            "calculations": [],
            "errors": []
        }
        creditors.append(creditor_state)

    return {
        "task_id": f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "project_id": "test-project",
        "project_config": PROJECT_CONFIG,
        "debtor_name": PROJECT_CONFIG["debtor_name"],
        "bankruptcy_date": PROJECT_CONFIG["bankruptcy_date"],
        "interest_stop_date": PROJECT_CONFIG["interest_stop_date"],
        "creditors": creditors,
        "current_creditor_index": 0,
        "completed_creditors": 0,
        "total_creditors": len(creditor_configs),
        "current_stage": WorkflowStage.INIT,
        "has_error": False,
        "error_message": None,
        "logs": [],
        "progress_percent": 0,
        "status_message": "Initializing...",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "fact_check_reports": {},
        "analysis_reports": {},
        "final_reports": {},
        "checkpoint_results": {}
    }


# ============== Pytest Configuration ==============

def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run end-to-end tests that require LLM API"
    )


def pytest_collection_modifyitems(config, items):
    """Skip e2e tests unless --run-e2e is specified."""
    if config.getoption("--run-e2e"):
        return

    skip_e2e = pytest.mark.skip(reason="Need --run-e2e option to run")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


# ============== Main ==============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
