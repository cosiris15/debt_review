"""
Template Enforcement Module for Debt Review

Implements mandatory template application and format validation.
Matches the original Claude Code solution's template enforcement standards.

Key Features:
1. Report template validation (NO Markdown in final reports)
2. Format conversion from Markdown to pure text
3. Placeholder replacement validation
4. Template compliance checking
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class FormatViolationType(str, Enum):
    """Types of format violations."""
    MARKDOWN_HEADING = "markdown_heading"  # ## or ###
    BULLET_LIST = "bullet_list"  # - or *
    BOLD_SYNTAX = "bold_syntax"  # **text**
    ITALIC_SYNTAX = "italic_syntax"  # *text* or _text_
    TABLE_SYNTAX = "table_syntax"  # | --- |
    CODE_BLOCK = "code_block"  # ``` or `
    UNREPLACED_PLACEHOLDER = "unreplaced_placeholder"  # [占位符]


@dataclass
class FormatViolation:
    """Represents a format violation."""
    violation_type: FormatViolationType
    line_number: int
    content: str
    suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.violation_type.value,
            "line": self.line_number,
            "content": self.content[:100],
            "suggestion": self.suggestion
        }


@dataclass
class TemplateValidationResult:
    """Result of template validation."""
    passed: bool
    violations: List[FormatViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
            "warnings": self.warnings
        }


# Patterns for detecting format violations
FORMAT_PATTERNS = {
    FormatViolationType.MARKDOWN_HEADING: r'^#{1,6}\s',
    FormatViolationType.BULLET_LIST: r'^[\s]*[-*•○]\s',
    FormatViolationType.BOLD_SYNTAX: r'\*\*[^*]+\*\*',
    FormatViolationType.ITALIC_SYNTAX: r'(?<!\*)\*[^*]+\*(?!\*)|_[^_]+_',
    FormatViolationType.TABLE_SYNTAX: r'\|[\s-]+\|',
    FormatViolationType.CODE_BLOCK: r'```|`[^`]+`',
    FormatViolationType.UNREPLACED_PLACEHOLDER: r'\[(?:年月日|金额|债权人名称|合同编号|利率|期限|日期|编号)\]'
}

# Acceptable placeholder patterns (these are intentional)
ACCEPTABLE_PLACEHOLDERS = [
    r'\[债权人未填写\]',
    r'\[证据未记载\]',
    r'\[无法确定\]',
    r'\[待补充\]',
    r'\[合同未约定\]',
    r'\[合同未载明\]',
    r'\[技术报告未[^\]]+\]',
    r'\[需[^\]]+\]'
]


def validate_report_format(content: str) -> TemplateValidationResult:
    """
    Validate report format against template standards.

    The final report must be pure text format - NO Markdown syntax allowed.

    Args:
        content: Report content to validate

    Returns:
        TemplateValidationResult with violations if any
    """
    violations = []
    warnings = []

    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Check each violation pattern
        for violation_type, pattern in FORMAT_PATTERNS.items():
            if re.search(pattern, line):
                # For placeholders, check if it's an acceptable one
                if violation_type == FormatViolationType.UNREPLACED_PLACEHOLDER:
                    # Skip if it's an acceptable placeholder
                    is_acceptable = any(
                        re.search(ap, line) for ap in ACCEPTABLE_PLACEHOLDERS
                    )
                    if is_acceptable:
                        continue

                violation = FormatViolation(
                    violation_type=violation_type,
                    line_number=line_num,
                    content=line.strip(),
                    suggestion=get_fix_suggestion(violation_type, line)
                )
                violations.append(violation)

    # Additional checks
    # Check for missing chapter structure
    chapter_pattern = r'^[一二三四五六七八九十]、'
    has_chapters = any(re.match(chapter_pattern, line) for line in lines)
    if not has_chapters:
        warnings.append("报告缺少标准章节结构（一、二、三...）")

    # Check for proper paragraph structure
    empty_line_count = sum(1 for line in lines if not line.strip())
    if empty_line_count < 3:
        warnings.append("段落之间可能缺少空行分隔")

    return TemplateValidationResult(
        passed=len(violations) == 0,
        violations=violations,
        warnings=warnings
    )


def get_fix_suggestion(violation_type: FormatViolationType, line: str) -> str:
    """
    Get suggestion for fixing a format violation.

    Args:
        violation_type: Type of violation
        line: The violating line

    Returns:
        Suggestion string for fixing
    """
    suggestions = {
        FormatViolationType.MARKDOWN_HEADING:
            "将 '## 标题' 改为纯文本 '一、标题' 或直接 '标题'",
        FormatViolationType.BULLET_LIST:
            "将列表项 '- 内容' 改为完整句子叙述",
        FormatViolationType.BOLD_SYNTAX:
            "删除 **加粗标记**，使用纯文本",
        FormatViolationType.ITALIC_SYNTAX:
            "删除 *斜体标记*，使用纯文本",
        FormatViolationType.TABLE_SYNTAX:
            "将表格转换为自然语言段落描述",
        FormatViolationType.CODE_BLOCK:
            "删除代码块标记，直接使用文本",
        FormatViolationType.UNREPLACED_PLACEHOLDER:
            "替换占位符为实际内容，或使用标准缺失标记如[债权人未填写]"
    }
    return suggestions.get(violation_type, "请修正格式问题")


def convert_markdown_to_plain_text(content: str) -> str:
    """
    Convert Markdown formatted text to plain text.

    This function performs the format conversion required by the original solution.

    Args:
        content: Markdown formatted content

    Returns:
        Plain text content suitable for final report
    """
    result = content

    # Remove Markdown headings
    # ## 一、标题 -> 一、标题
    result = re.sub(r'^#{1,6}\s*', '', result, flags=re.MULTILINE)

    # Convert bullet lists to sentences
    # - 项目1 -> 项目1。
    lines = result.split('\n')
    converted_lines = []
    bullet_items = []

    for line in lines:
        bullet_match = re.match(r'^[\s]*[-*•○]\s*(.+)$', line)
        if bullet_match:
            bullet_items.append(bullet_match.group(1).strip())
        else:
            if bullet_items:
                # Combine bullet items into a sentence
                combined = '；'.join(bullet_items) + '。'
                converted_lines.append(combined)
                bullet_items = []
            converted_lines.append(line)

    # Handle remaining bullet items
    if bullet_items:
        combined = '；'.join(bullet_items) + '。'
        converted_lines.append(combined)

    result = '\n'.join(converted_lines)

    # Remove bold syntax (handle edge cases)
    result = re.sub(r'\*\*([^*]+)\*\*', r'\1', result)
    # Handle incomplete bold markers
    result = re.sub(r'\*\*([^*]+)$', r'\1', result, flags=re.MULTILINE)
    result = re.sub(r'^([^*]+)\*\*', r'\1', result, flags=re.MULTILINE)

    # Remove italic syntax
    result = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', result)
    result = re.sub(r'_([^_]+)_', r'\1', result)

    # Remove inline code
    result = re.sub(r'`([^`]+)`', r'\1', result)

    # Remove code blocks
    result = re.sub(r'```[\w]*\n', '', result)
    result = re.sub(r'```', '', result)

    # Clean up multiple newlines
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def validate_placeholder_replacement(
    content: str,
    required_fields: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate that all required placeholders have been replaced.

    Args:
        content: Report content
        required_fields: Optional list of required field names

    Returns:
        Tuple of (all_replaced, list of unreplaced placeholders)
    """
    # Default required fields for debt review reports
    if required_fields is None:
        required_fields = [
            "债权人名称",
            "申报债权总额",
            "债权性质",
            "确认金额"
        ]

    unreplaced = []

    # Find all bracket patterns that look like placeholders
    placeholder_pattern = r'\[([^\]]+)\]'
    matches = re.findall(placeholder_pattern, content)

    for match in matches:
        # Check if it's an unreplaced required field
        if any(field in match for field in required_fields):
            # Check if it's not an acceptable missing marker
            is_acceptable = any(
                re.search(ap, f'[{match}]') for ap in ACCEPTABLE_PLACEHOLDERS
            )
            if not is_acceptable:
                unreplaced.append(match)

    return len(unreplaced) == 0, unreplaced


def apply_template_structure(
    content: str,
    template_type: str = "single_creditor"
) -> str:
    """
    Apply standard template structure to content.

    Ensures the content follows the required chapter structure.

    Args:
        content: Raw content to structure
        template_type: "single_creditor" or "multi_creditor"

    Returns:
        Structured content
    """
    # Standard chapter structure for single creditor
    single_chapters = [
        "一、债权申报情况",
        "二、合同签订情况",
        "三、合同履行情况",
        "四、担保情况",
        "五、涉诉情况",
        "六、债务人核查情况",
        "七、管理人审查结论"
    ]

    # Multi-creditor chapters
    multi_chapters = [
        "一、债权申报情况",
        "二、债权形成情况",
        "三、债务人核查情况",
        "四、债权初步审查意见"
    ]

    chapters = single_chapters if template_type == "single_creditor" else multi_chapters

    # Check if content already has proper structure
    has_structure = any(
        chapter in content for chapter in chapters
    )

    if has_structure:
        # Content already structured, just clean format
        return convert_markdown_to_plain_text(content)

    # Log warning if restructuring needed
    logger.warning("Report content lacks standard chapter structure")
    return convert_markdown_to_plain_text(content)


def enforce_template_compliance(content: str) -> Tuple[str, TemplateValidationResult]:
    """
    Enforce template compliance on report content.

    This is the main entry point for template enforcement.

    Args:
        content: Report content

    Returns:
        Tuple of (compliant content, validation result)
    """
    # Step 1: Convert to plain text
    converted = convert_markdown_to_plain_text(content)

    # Step 2: Apply template structure
    structured = apply_template_structure(converted)

    # Step 3: Validate the result
    validation = validate_report_format(structured)

    if not validation.passed:
        logger.warning(
            f"Template compliance failed with {len(validation.violations)} violations"
        )
        # Try additional cleanup for remaining violations
        for violation in validation.violations:
            if violation.violation_type == FormatViolationType.MARKDOWN_HEADING:
                structured = re.sub(r'^#{1,6}\s*', '', structured, flags=re.MULTILINE)
            elif violation.violation_type == FormatViolationType.BOLD_SYNTAX:
                structured = re.sub(r'\*\*([^*]+)\*\*', r'\1', structured)

        # Re-validate after additional cleanup
        validation = validate_report_format(structured)

    return structured, validation


class TemplateEnforcer:
    """
    Class-based template enforcer for integration with workflow nodes.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize template enforcer.

        Args:
            strict_mode: If True, reject non-compliant reports
        """
        self.strict_mode = strict_mode

    def process_report(
        self,
        content: str,
        creditor_name: str
    ) -> Dict[str, Any]:
        """
        Process a report through template enforcement.

        Args:
            content: Report content
            creditor_name: Creditor name for logging

        Returns:
            Dict with processed content and validation results
        """
        logger.info(f"Processing report for template compliance: {creditor_name}")

        # Enforce compliance
        compliant_content, validation = enforce_template_compliance(content)

        result = {
            "creditor_name": creditor_name,
            "original_length": len(content),
            "processed_length": len(compliant_content),
            "validation": validation.to_dict(),
            "compliant": validation.passed
        }

        if validation.passed:
            result["content"] = compliant_content
            logger.info(f"Report passed template validation: {creditor_name}")
        else:
            if self.strict_mode:
                logger.error(
                    f"Report failed template validation: {creditor_name} "
                    f"({len(validation.violations)} violations)"
                )
                result["content"] = compliant_content  # Return best effort
                result["requires_manual_review"] = True
            else:
                result["content"] = compliant_content
                logger.warning(
                    f"Report has format warnings: {creditor_name} "
                    f"({len(validation.violations)} violations)"
                )

        return result

    def batch_process(
        self,
        reports: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple reports in batch.

        Args:
            reports: List of dicts with 'content' and 'creditor_name' keys

        Returns:
            List of processed results
        """
        results = []
        for report in reports:
            result = self.process_report(
                content=report.get("content", ""),
                creditor_name=report.get("creditor_name", "Unknown")
            )
            results.append(result)

        # Log batch summary
        passed = sum(1 for r in results if r.get("compliant"))
        logger.info(f"Batch template processing: {passed}/{len(results)} passed")

        return results


# Singleton instance
_template_enforcer = None


def get_template_enforcer(strict_mode: bool = True) -> TemplateEnforcer:
    """Get or create template enforcer instance."""
    global _template_enforcer
    if _template_enforcer is None:
        _template_enforcer = TemplateEnforcer(strict_mode=strict_mode)
    return _template_enforcer
