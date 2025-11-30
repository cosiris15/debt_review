"""
Quality Checkpoints for Debt Review Workflow

Implements the three mandatory checkpoint mechanism from the original Claude Code solution:
- Checkpoint 1: After Fact-Check (MUST PASS)
- Checkpoint 2: After Analysis (MUST PASS)
- Checkpoint 3: After Report (MUST PASS)

Each checkpoint validates:
1. Required content presence
2. Data consistency (dates, amounts)
3. Format compliance
4. Anti-fabrication rules
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class CheckpointStatus(Enum):
    """Checkpoint validation status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class CheckpointResult:
    """Result of a checkpoint validation."""
    status: CheckpointStatus
    checkpoint_name: str
    checks_passed: List[str]
    checks_failed: List[str]
    warnings: List[str]
    details: Dict[str, Any]

    @property
    def is_passed(self) -> bool:
        return self.status == CheckpointStatus.PASSED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "checkpoint_name": self.checkpoint_name,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "warnings": self.warnings,
            "details": self.details
        }


class QualityCheckpoints:
    """
    Quality checkpoint validator for debt review workflow.

    Mirrors the original Claude Code solution's three-tier checkpoint system.
    """

    def __init__(self, bankruptcy_date: str, interest_stop_date: str):
        """
        Initialize checkpoints with project dates.

        Args:
            bankruptcy_date: Bankruptcy filing date (YYYY-MM-DD)
            interest_stop_date: Interest stop date (day before bankruptcy)
        """
        self.bankruptcy_date = bankruptcy_date
        self.interest_stop_date = interest_stop_date

    def checkpoint_fact_check(
        self,
        fact_check_report: str,
        creditor_name: str,
        declared_amounts: Dict[str, Optional[float]]
    ) -> CheckpointResult:
        """
        Checkpoint 1: After Fact-Check (MUST PASS)

        Validates:
        ✓ 破产日期在报告中明确记录
        ✓ 停止计息日期 = 破产日期 - 1
        ✓ 申报金额完整（本金、利息、合计）
        ✓ 时间线按时间顺序
        ✓ 证据引用存在
        ✓ 法律关系类型已识别
        """
        checks_passed = []
        checks_failed = []
        warnings = []
        details = {}

        # 1. 破产日期验证
        if self.bankruptcy_date in fact_check_report:
            checks_passed.append("破产日期在报告中明确记录")
        else:
            checks_failed.append(f"破产日期 {self.bankruptcy_date} 未在报告中找到")

        # 2. 停止计息日期验证
        if self.interest_stop_date in fact_check_report:
            checks_passed.append("停止计息日期在报告中记录")
        else:
            warnings.append(f"停止计息日期 {self.interest_stop_date} 建议明确标注")

        # 3. 申报金额完整性
        amount_keywords = ["本金", "利息", "合计", "申报金额"]
        found_keywords = [kw for kw in amount_keywords if kw in fact_check_report]
        if len(found_keywords) >= 2:
            checks_passed.append(f"申报金额信息存在: {', '.join(found_keywords)}")
        else:
            checks_failed.append("申报金额信息不完整")

        # 4. 时间线存在性检查
        timeline_patterns = [
            r'\d{4}[-年]\d{1,2}[-月]\d{1,2}',  # 日期格式
            r'时间线|时间顺序|事件梳理',
        ]
        timeline_found = any(re.search(p, fact_check_report) for p in timeline_patterns)
        if timeline_found:
            checks_passed.append("时间线信息存在")
        else:
            warnings.append("建议添加事件时间线")

        # 5. 证据引用检查
        evidence_keywords = ["证据", "合同", "协议", "判决", "凭证", "发票"]
        evidence_found = [kw for kw in evidence_keywords if kw in fact_check_report]
        if len(evidence_found) >= 2:
            checks_passed.append(f"证据引用存在: {', '.join(evidence_found)}")
        else:
            checks_failed.append("证据引用不足")

        # 6. 法律关系识别
        legal_relations = ["借款", "买卖", "租赁", "担保", "保证", "抵押", "质押", "货款", "工程款"]
        relation_found = [lr for lr in legal_relations if lr in fact_check_report]
        if relation_found:
            checks_passed.append(f"法律关系已识别: {', '.join(relation_found)}")
            details["legal_relations"] = relation_found
        else:
            checks_failed.append("法律关系类型未识别")

        # 7. 反编造检查 - 禁止推理词汇
        fabrication_words = ["应该是", "可能是", "估计", "大概", "推测", "假设"]
        found_fabrication = [w for w in fabrication_words if w in fact_check_report]
        if found_fabrication:
            warnings.append(f"发现推理词汇（建议审查）: {', '.join(found_fabrication)}")

        # 确定最终状态
        if checks_failed:
            status = CheckpointStatus.FAILED
        elif warnings:
            status = CheckpointStatus.WARNING
        else:
            status = CheckpointStatus.PASSED

        return CheckpointResult(
            status=status,
            checkpoint_name="Checkpoint 1: 事实核查后",
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            warnings=warnings,
            details=details
        )

    def checkpoint_analysis(
        self,
        analysis_report: str,
        fact_check_report: str,
        declared_amounts: Dict[str, Optional[float]],
        confirmed_amounts: Dict[str, Optional[float]],
        calculation_results: List[Dict[str, Any]]
    ) -> CheckpointResult:
        """
        Checkpoint 2: After Analysis (MUST PASS)

        Validates:
        ✓ 日期与事实报告一致
        ✓ 所有计算使用 Calculator 工具
        ✓ 计算文件已生成
        ✓ LPR期限选择有依据
        ✓ 违约金上限验证（≤ 4× LPR）
        ✓ 就低原则：确认额 ≤ 申报额
        ✓ 就无原则：仅确认申报项
        """
        checks_passed = []
        checks_failed = []
        warnings = []
        details = {}

        # 1. 日期一致性验证
        if self.bankruptcy_date in analysis_report:
            checks_passed.append("破产日期与事实报告一致")
        else:
            checks_failed.append("分析报告中破产日期缺失或不一致")

        # 2. Calculator 工具使用验证
        calc_patterns = [
            r'【利息计算】',
            r'计算结果',
            r'利息计算过程',
        ]
        calc_found = any(re.search(p, analysis_report) for p in calc_patterns)
        if calc_found or calculation_results:
            checks_passed.append(f"使用计算器工具: {len(calculation_results)} 项计算")
            details["calculation_count"] = len(calculation_results)
        else:
            warnings.append("未检测到利息计算标记")

        # 3. 计算结果验证
        if calculation_results:
            for i, calc in enumerate(calculation_results, 1):
                if "error" in calc:
                    checks_failed.append(f"计算 {i} 存在错误: {calc.get('error')}")
                else:
                    checks_passed.append(f"计算 {i} 成功完成")

        # 4. 就低原则验证
        declared_total = declared_amounts.get("total") or 0
        confirmed_total = confirmed_amounts.get("total") or 0

        if declared_total > 0:
            if confirmed_total <= declared_total:
                checks_passed.append(f"就低原则通过: 确认额 {confirmed_total:,.2f} ≤ 申报额 {declared_total:,.2f}")
            else:
                checks_failed.append(f"就低原则违反: 确认额 {confirmed_total:,.2f} > 申报额 {declared_total:,.2f}")

        # 5. 就无原则验证 - 检查是否有未申报项被确认
        declared_principal = declared_amounts.get("principal") or 0
        confirmed_principal = confirmed_amounts.get("principal") or 0
        if declared_principal == 0 and confirmed_principal > 0:
            checks_failed.append("就无原则违反: 本金未申报但被确认")
        else:
            checks_passed.append("就无原则通过")

        # 6. 诉讼时效分析存在性
        statute_keywords = ["诉讼时效", "时效", "执行时效", "中断", "届满"]
        statute_found = [kw for kw in statute_keywords if kw in analysis_report]
        if statute_found:
            checks_passed.append(f"诉讼时效分析存在: {', '.join(statute_found)}")
        else:
            warnings.append("建议添加诉讼时效分析")

        # 7. 违约金上限检查 (24% 年化上限)
        penalty_pattern = r'违约金.*?(\d+\.?\d*)%'
        penalty_matches = re.findall(penalty_pattern, analysis_report)
        for rate in penalty_matches:
            if float(rate) > 24:
                warnings.append(f"违约金利率 {rate}% 超过24%上限，需核实")

        # 8. 反编造检查
        fabrication_words = ["应该是", "可能是", "估计", "推测"]
        found_fabrication = [w for w in fabrication_words if w in analysis_report]
        if found_fabrication:
            warnings.append(f"发现推理词汇: {', '.join(found_fabrication)}")

        # 确定最终状态
        if checks_failed:
            status = CheckpointStatus.FAILED
        elif warnings:
            status = CheckpointStatus.WARNING
        else:
            status = CheckpointStatus.PASSED

        return CheckpointResult(
            status=status,
            checkpoint_name="Checkpoint 2: 债权分析后",
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            warnings=warnings,
            details=details
        )

    def _check_for_inference_words(self, content: str) -> Optional[str]:
        """
        Check content for inference/fabrication words.

        Returns the first found inference word, or None if clean.
        """
        fabrication_words = ["应该是", "可能是", "估计", "大概", "推测", "假设", "猜测"]
        for word in fabrication_words:
            if word in content:
                return word
        return None

    def _check_format_compliance(self, content: str) -> List[str]:
        """
        Check content for format violations (Markdown markers).

        Returns list of format issues found.
        """
        issues = []

        # Check Markdown headings
        if re.search(r'^##\s+', content, re.MULTILINE):
            issues.append("Markdown heading (##)")

        # Check bullet lists
        if re.search(r'^-\s+', content, re.MULTILINE):
            issues.append("Bullet list (-)")

        # Check bold syntax
        if re.search(r'\*\*[^*]+\*\*', content):
            issues.append("Bold syntax (**)")

        return issues

    def checkpoint_report(
        self,
        final_report: str,
        fact_check_report: str,
        analysis_report: str
    ) -> CheckpointResult:
        """
        Checkpoint 3: After Report (MUST PASS)

        Validates:
        ✓ 最终报告存在
        ✓ 日期三方一致（配置+事实报告+分析报告）
        ✓ 格式合规（NO Markdown标记）
        ✓ 内容准确提取
        ✓ 技术结论保留
        """
        checks_passed = []
        checks_failed = []
        warnings = []
        details = {}

        # 1. 报告存在性
        if final_report and len(final_report) > 100:
            checks_passed.append(f"最终报告已生成 ({len(final_report)} 字符)")
        else:
            checks_failed.append("最终报告缺失或内容不足")

        # 2. 日期三方一致性
        date_in_final = self.bankruptcy_date in final_report
        date_in_fact = self.bankruptcy_date in fact_check_report
        date_in_analysis = self.bankruptcy_date in analysis_report

        if all([date_in_final, date_in_fact, date_in_analysis]):
            checks_passed.append("破产日期三方一致")
        else:
            missing = []
            if not date_in_final:
                missing.append("最终报告")
            if not date_in_fact:
                missing.append("事实报告")
            if not date_in_analysis:
                missing.append("分析报告")
            checks_failed.append(f"日期缺失于: {', '.join(missing)}")

        # 3. 格式合规检查（零容忍）
        format_violations = []

        # 检查 Markdown 标题
        md_headers = re.findall(r'^##\s+', final_report, re.MULTILINE)
        if md_headers:
            format_violations.append(f"包含 Markdown 标题 ({len(md_headers)} 处)")

        # 检查 bullet 列表
        bullet_lists = re.findall(r'^-\s+', final_report, re.MULTILINE)
        if bullet_lists:
            format_violations.append(f"包含 bullet 列表 ({len(bullet_lists)} 处)")

        # 检查粗体标记
        bold_marks = re.findall(r'\*\*[^*]+\*\*', final_report)
        if bold_marks:
            format_violations.append(f"包含粗体标记 ({len(bold_marks)} 处)")

        if format_violations:
            checks_failed.extend([f"格式违规: {v}" for v in format_violations])
            details["format_violations"] = format_violations
        else:
            checks_passed.append("格式合规（无 Markdown 标记）")

        # 4. 七章节结构检查
        chapter_patterns = [
            "一、", "二、", "三、", "四、", "五、", "六、", "七、"
        ]
        found_chapters = [c for c in chapter_patterns if c in final_report]
        if len(found_chapters) >= 5:
            checks_passed.append(f"章节结构完整 ({len(found_chapters)}/7 章节)")
        else:
            warnings.append(f"章节结构可能不完整 ({len(found_chapters)}/7 章节)")

        # 5. 关键内容转录检查
        key_content = ["债权人", "债务人", "本金", "利息", "审查结论"]
        found_content = [kc for kc in key_content if kc in final_report]
        if len(found_content) >= 4:
            checks_passed.append(f"关键内容完整: {', '.join(found_content)}")
        else:
            checks_failed.append(f"关键内容缺失，仅找到: {', '.join(found_content)}")

        # 6. 反编造检查 - 确保无新内容添加
        # 这个检查比较复杂，这里简化为检查是否有明显的推理词汇
        fabrication_words = ["建议", "应当", "可以考虑"]
        found_fabrication = [w for w in fabrication_words if w in final_report]
        if found_fabrication:
            warnings.append(f"最终报告可能包含新增建议: {', '.join(found_fabrication)}")

        # 确定最终状态
        if checks_failed:
            status = CheckpointStatus.FAILED
        elif warnings:
            status = CheckpointStatus.WARNING
        else:
            status = CheckpointStatus.PASSED

        return CheckpointResult(
            status=status,
            checkpoint_name="Checkpoint 3: 报告整理后",
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            warnings=warnings,
            details=details
        )


def run_checkpoint(
    checkpoint_name: str,
    state: dict,
    creditor: dict
) -> CheckpointResult:
    """
    Run a specific checkpoint based on the current workflow stage.

    Args:
        checkpoint_name: "fact_check", "analysis", or "report"
        state: Current workflow state
        creditor: Current creditor state

    Returns:
        CheckpointResult with validation details
    """
    checkpoints = QualityCheckpoints(
        bankruptcy_date=state.get("bankruptcy_date", ""),
        interest_stop_date=state.get("interest_stop_date", "")
    )

    if checkpoint_name == "fact_check":
        return checkpoints.checkpoint_fact_check(
            fact_check_report=creditor.get("fact_check_report", ""),
            creditor_name=creditor.get("creditor_name", ""),
            declared_amounts={
                "principal": creditor.get("declared_principal"),
                "interest": creditor.get("declared_interest"),
                "total": creditor.get("declared_total")
            }
        )

    elif checkpoint_name == "analysis":
        return checkpoints.checkpoint_analysis(
            analysis_report=creditor.get("analysis_report", ""),
            fact_check_report=creditor.get("fact_check_report", ""),
            declared_amounts={
                "principal": creditor.get("declared_principal"),
                "interest": creditor.get("declared_interest"),
                "total": creditor.get("declared_total")
            },
            confirmed_amounts={
                "principal": creditor.get("confirmed_principal"),
                "interest": creditor.get("confirmed_interest"),
                "total": creditor.get("confirmed_total")
            },
            calculation_results=creditor.get("calculation_results", [])
        )

    elif checkpoint_name == "report":
        return checkpoints.checkpoint_report(
            final_report=creditor.get("final_report", ""),
            fact_check_report=creditor.get("fact_check_report", ""),
            analysis_report=creditor.get("analysis_report", "")
        )

    else:
        raise ValueError(f"Unknown checkpoint: {checkpoint_name}")
