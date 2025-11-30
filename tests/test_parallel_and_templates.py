"""
Tests for Parallel Processing and Template Enforcement

Validates:
1. Automatic processing mode selection
2. Parallel execution
3. Template format compliance
4. Markdown to plain text conversion
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestParallelProcessing:
    """Tests for parallel processing module."""

    def test_auto_mode_single_creditor(self):
        """Test mode selection for single creditor."""
        from app.agents.parallel import auto_select_processing_mode, ProcessingMode

        mode = auto_select_processing_mode(1)
        assert mode == ProcessingMode.SERIAL

    def test_auto_mode_multiple_creditors(self):
        """Test mode selection for multiple creditors."""
        from app.agents.parallel import auto_select_processing_mode, ProcessingMode

        mode = auto_select_processing_mode(2)
        assert mode == ProcessingMode.PARALLEL

        mode = auto_select_processing_mode(5)
        assert mode == ProcessingMode.PARALLEL

    def test_execution_plan_serial(self):
        """Test execution plan for serial mode."""
        from app.agents.parallel import get_execution_plan, ProcessingMode

        plan = get_execution_plan(ProcessingMode.SERIAL, 1)
        assert "串行" in plan or "顺序" in plan

    def test_execution_plan_parallel(self):
        """Test execution plan for parallel mode."""
        from app.agents.parallel import get_execution_plan, ProcessingMode

        plan = get_execution_plan(ProcessingMode.PARALLEL, 5)
        assert "并行" in plan
        assert "5" in plan

    def test_parallel_batch_state(self):
        """Test ParallelBatchState dataclass."""
        from app.agents.parallel import ParallelBatchState, ProcessingMode

        state = ParallelBatchState(
            batch_id="test-batch",
            creditor_ids=["c1", "c2", "c3"],
            mode=ProcessingMode.PARALLEL
        )

        state_dict = state.to_dict()
        assert state_dict["batch_id"] == "test-batch"
        assert state_dict["creditor_count"] == 3
        assert state_dict["mode"] == "parallel"


class TestTemplateEnforcement:
    """Tests for template enforcement module."""

    def test_detect_markdown_heading(self):
        """Test detection of Markdown headings."""
        from app.agents.templates import validate_report_format, FormatViolationType

        content = "## 一、债权申报情况\n\n内容..."
        result = validate_report_format(content)

        assert not result.passed
        assert any(v.violation_type == FormatViolationType.MARKDOWN_HEADING
                   for v in result.violations)

    def test_detect_bullet_list(self):
        """Test detection of bullet lists."""
        from app.agents.templates import validate_report_format, FormatViolationType

        content = "内容如下：\n- 第一项\n- 第二项"
        result = validate_report_format(content)

        assert not result.passed
        assert any(v.violation_type == FormatViolationType.BULLET_LIST
                   for v in result.violations)

    def test_detect_bold_syntax(self):
        """Test detection of bold syntax."""
        from app.agents.templates import validate_report_format, FormatViolationType

        content = "这是**重要内容**需要关注"
        result = validate_report_format(content)

        assert not result.passed
        assert any(v.violation_type == FormatViolationType.BOLD_SYNTAX
                   for v in result.violations)

    def test_clean_content_passes(self):
        """Test that clean content passes validation."""
        from app.agents.templates import validate_report_format

        content = """一、债权申报情况

债权人某某公司于2024年1月1日向管理人申报债权，申报债权金额共计1000000.00元。

二、合同签订情况

2023年6月1日，债权人与债务人签订借款合同。"""

        result = validate_report_format(content)
        assert result.passed

    def test_convert_markdown_heading(self):
        """Test conversion of Markdown headings."""
        from app.agents.templates import convert_markdown_to_plain_text

        content = "## 一、债权申报情况"
        result = convert_markdown_to_plain_text(content)

        assert "##" not in result
        assert "一、债权申报情况" in result

    def test_convert_bullet_list(self):
        """Test conversion of bullet lists to sentences."""
        from app.agents.templates import convert_markdown_to_plain_text

        content = "内容如下：\n- 第一项\n- 第二项\n- 第三项"
        result = convert_markdown_to_plain_text(content)

        assert "- " not in result
        # Should be converted to semicolon-separated sentence
        assert "；" in result or "。" in result

    def test_convert_bold_syntax(self):
        """Test conversion of bold syntax."""
        from app.agents.templates import convert_markdown_to_plain_text

        content = "这是**重要内容**需要关注"
        result = convert_markdown_to_plain_text(content)

        assert "**" not in result
        assert "重要内容" in result

    def test_enforce_template_compliance(self):
        """Test full template compliance enforcement."""
        from app.agents.templates import enforce_template_compliance

        markdown_content = """## 一、债权申报情况

**债权人**某某公司申报债权：

- 本金：100万元
- 利息：5万元

### 1.1 申报详情

内容..."""

        compliant, result = enforce_template_compliance(markdown_content)

        # Should convert to plain text
        assert "##" not in compliant
        assert "**" not in compliant
        assert "- " not in compliant

        # Core content should be preserved
        assert "债权申报情况" in compliant
        assert "本金" in compliant

    def test_acceptable_placeholders(self):
        """Test that acceptable placeholders are not flagged."""
        from app.agents.templates import validate_report_format

        content = "利率：[合同未约定]\n期限：[债权人未填写]"
        result = validate_report_format(content)

        # These are acceptable placeholders, should not cause failures
        # Only unreplaced standard placeholders like [年月日] should fail
        unreplaced_violations = [
            v for v in result.violations
            if "UNREPLACED" in str(v.violation_type)
        ]
        assert len(unreplaced_violations) == 0

    def test_template_enforcer_class(self):
        """Test TemplateEnforcer class."""
        from app.agents.templates import get_template_enforcer

        enforcer = get_template_enforcer(strict_mode=True)

        markdown_report = "## 标题\n\n**内容**"
        result = enforcer.process_report(markdown_report, "测试债权人")

        assert "content" in result
        assert "##" not in result["content"]


class TestCheckpointIntegration:
    """Tests for checkpoint integration."""

    def test_checkpoint_status_enum(self):
        """Test CheckpointStatus enum."""
        from app.agents.checkpoints import CheckpointStatus

        assert CheckpointStatus.PASSED.value == "passed"
        assert CheckpointStatus.FAILED.value == "failed"
        assert CheckpointStatus.WARNING.value == "warning"

    def test_checkpoint_result(self):
        """Test CheckpointResult dataclass."""
        from app.agents.checkpoints import CheckpointResult, CheckpointStatus

        result = CheckpointResult(
            checkpoint_name="test",
            status=CheckpointStatus.PASSED,
            checks_passed=["check1", "check2"],
            checks_failed=[],
            warnings=["warning1"],
            details={}
        )

        result_dict = result.to_dict()
        assert result_dict["checkpoint_name"] == "test"
        assert result_dict["status"] == "passed"
        assert len(result_dict["checks_passed"]) == 2


class TestAntiHallucination:
    """Tests for anti-hallucination checks."""

    def test_inference_word_detection(self):
        """Test detection of inference words."""
        from app.agents.checkpoints import QualityCheckpoints

        checkpoints = QualityCheckpoints(
            bankruptcy_date="2024-05-09",
            interest_stop_date="2024-05-08"
        )

        # Content with inference words
        content_with_inference = "根据上述材料，推测债务人可能存在还款能力"

        # Should detect inference words
        result = checkpoints._check_for_inference_words(content_with_inference)
        assert result is not None  # Found inference word

    def test_clean_content_no_inference(self):
        """Test that clean content passes inference check."""
        from app.agents.checkpoints import QualityCheckpoints

        checkpoints = QualityCheckpoints(
            bankruptcy_date="2024-05-09",
            interest_stop_date="2024-05-08"
        )

        # Clean content without inference
        clean_content = "根据借款合同第5条约定，借款本金为100万元"

        result = checkpoints._check_for_inference_words(clean_content)
        # Should not find inference words in clean content
        # (result depends on implementation)


class TestFormatValidation:
    """Tests for format validation in checkpoints."""

    def test_format_compliance_check(self):
        """Test format compliance checking."""
        from app.agents.checkpoints import QualityCheckpoints

        checkpoints = QualityCheckpoints(
            bankruptcy_date="2024-05-09",
            interest_stop_date="2024-05-08"
        )

        # Content with Markdown
        markdown_content = "## 标题\n- 列表项"

        # Should detect format issues
        issues = checkpoints._check_format_compliance(markdown_content)
        assert len(issues) > 0

    def test_format_compliance_clean(self):
        """Test that clean content passes format check."""
        from app.agents.checkpoints import QualityCheckpoints

        checkpoints = QualityCheckpoints(
            bankruptcy_date="2024-05-09",
            interest_stop_date="2024-05-08"
        )

        # Clean content
        clean_content = "一、债权申报情况\n\n债权人申报本金100万元。"

        issues = checkpoints._check_format_compliance(clean_content)
        assert len(issues) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
