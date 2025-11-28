#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-Fabrication Checker
自动化反编造验证工具

Purpose: Automatically detect fabrication patterns, missing citations,
         and prohibited improvements in debt review reports.

Usage:
    python anti_fabrication_checker.py <report_file> [--report-type TYPE]

Report Types:
    - fact-checking (事实核查报告)
    - debt-analysis (债权分析报告)
    - review-opinion (审查意见表)

Author: Anti-Fabrication Protection System
Version: 1.0
Date: 2025-11-06
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Violation:
    """Represents a detected violation"""
    line_num: int
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category: str
    description: str
    context: str  # The actual line content
    recommendation: str


class AntiFabricationChecker:
    """Main checker class for detecting fabrication patterns"""

    def __init__(self, report_type: str = 'fact-checking'):
        self.report_type = report_type
        self.violations: List[Violation] = []

        # Define prohibited phrase patterns
        self.prohibited_phrases = {
            'CRITICAL': [
                (r'根据常理', '根据常理', '禁止用常识填补证据'),
                (r'一般[来说|认为|情况]', '一般来说/认为/情况', '禁止用一般情况假设未明事项'),
                (r'应该是|肯定是|一定是', '应该是/肯定是/一定是', '禁止推测性确定表述'),
                (r'按照惯例|行业惯例|通常情况', '按照惯例/行业惯例', '禁止用惯例替代证据'),
                (r'从逻辑[上推|推断]', '从逻辑上推断', '禁止逻辑推测填补证据'),
            ],
            'HIGH': [
                (r'可能是(?!.*[可能构成|存在.*风险])', '可能是 (非法律推理)', '推测性表述,需标注为[证据未记载]'),
                (r'似乎|看起来|大概', '似乎/看起来/大概', '模糊推测,需明确标注不确定'),
                (r'应当|应为(?!依据)', '应当/应为 (无法律依据)', '未引用法律依据的"应当"'),
                (r'毫无疑问|显而易见|不言而喻', '毫无疑问/显而易见', '过度确定表述'),
                (r'不可能不|必然', '不可能不/必然', '过度确定推理'),
            ],
            'MEDIUM': [
                (r'根据证据材料(?!第\d+页)', '根据证据材料 (无页码)', '模糊引用,需指明具体页码'),
                (r'债权人说明|债权人称|债权人提供的材料显示', '债权人说明/称/提供的材料显示', '需指明具体证据,不可笼统引用'),
                (r'据此可以认为|由此推断', '据此可以认为/由此推断', '推理性表述,需核查是否有法律依据'),
            ],
        }

        # Citation format patterns
        self.citation_patterns = {
            'required': r'（见.*第\d+页）|（见.*第\d+-\d+页）|（见.*条.*页）',
            'judgment': r'（见.*\(\d{4}\).*号.*第\d+页）',
            'contract': r'（见《.*》第\d+条.*页）',
        }

        # Gap marker patterns (acceptable)
        self.gap_markers = [
            r'\[证据未记载\]',
            r'\[债权人未填写\]',
            r'\[债权人未提供\]',
            r'\[无法确定\]',
            r'\[待补充\]',
            r'\[合同未约定\]',
            r'\[判决书未明确\]',
        ]

        # Placeholder patterns (should be replaced)
        self.placeholders = [
            r'\[债权人名称\]',
            r'\[债务人名称\]',
            r'\[年月日\]',
            r'\[金额\]',
            r'\[X\]',  # Generic placeholder
        ]

    def check_file(self, file_path: str) -> Dict:
        """Main entry point: check a report file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return {'error': f'File not found: {file_path}'}
        except Exception as e:
            return {'error': f'Error reading file: {str(e)}'}

        # Reset violations
        self.violations = []

        # Run all checks
        for line_num, line in enumerate(lines, 1):
            self._check_prohibited_phrases(line_num, line)
            self._check_citations(line_num, line)
            self._check_placeholders(line_num, line)

        # Report-type specific checks
        if self.report_type == 'review-opinion':
            self._check_format_compliance(lines)

        # Calculate statistics
        stats = self._calculate_statistics()

        return {
            'file': file_path,
            'report_type': self.report_type,
            'total_lines': len(lines),
            'violations': self.violations,
            'statistics': stats,
            'passed': len(self.violations) == 0
        }

    def _check_prohibited_phrases(self, line_num: int, line: str):
        """Check for prohibited fabrication phrases"""
        for severity, patterns in self.prohibited_phrases.items():
            for pattern, display, reason in patterns:
                if re.search(pattern, line):
                    self.violations.append(Violation(
                        line_num=line_num,
                        severity=severity,
                        category='禁止推测性表述',
                        description=f'检测到禁止短语: "{display}"',
                        context=line.strip(),
                        recommendation=reason
                    ))

    def _check_citations(self, line_num: int, line: str):
        """Check for proper evidence citations"""
        # Skip lines that are gap markers (these don't need citations)
        if any(re.search(marker, line) for marker in self.gap_markers):
            return

        # Skip lines that don't make factual claims
        if self._is_metadata_line(line) or self._is_heading_line(line):
            return

        # Check for factual statements that need citations
        factual_indicators = [
            r'\d{4}年\d{1,2}月\d{1,2}日',  # Dates
            r'人民币.*元|金额.*元',  # Amounts
            r'根据|依据(?!《)',  # "According to" without law reference
            r'合同.*约定',  # Contract terms
            r'判决.*认定',  # Judgment findings
        ]

        has_factual_claim = any(re.search(indicator, line) for indicator in factual_indicators)

        if has_factual_claim:
            # Check if line has proper citation
            has_citation = re.search(self.citation_patterns['required'], line)
            has_gap_marker = any(re.search(marker, line) for marker in self.gap_markers)

            if not has_citation and not has_gap_marker:
                # Check if it's a legal reasoning (has law citation)
                has_law_citation = re.search(r'依据《.*》第\d+条', line)
                if not has_law_citation:
                    self.violations.append(Violation(
                        line_num=line_num,
                        severity='HIGH',
                        category='缺少证据引用',
                        description='事实陈述缺少证据来源页码',
                        context=line.strip(),
                        recommendation='添加证据引用: （见XX第X页）或标注为[证据未记载]'
                    ))

    def _check_placeholders(self, line_num: int, line: str):
        """Check for unreplaced placeholders"""
        # Special handling: [债权人名称] in review-opinion template is acceptable
        # as it's a standardized format element in the final report title
        if self.report_type == 'review-opinion' and '[债权人名称]' in line and line_num <= 5:
            return  # Allow in title section

        for placeholder in self.placeholders:
            if re.search(placeholder, line):
                # Distinguish from gap markers
                if not any(re.search(marker, line) for marker in self.gap_markers):
                    self.violations.append(Violation(
                        line_num=line_num,
                        severity='CRITICAL',
                        category='未替换占位符',
                        description=f'检测到未替换的模板占位符: {placeholder}',
                        context=line.strip(),
                        recommendation='替换占位符为实际内容,或使用[证据未记载]等缺失标记'
                    ))

    def _check_format_compliance(self, lines: List[str]):
        """Check format compliance for review opinion forms (pure text format)"""
        prohibited_markdown = [
            (r'^#{1,6}\s', 'Markdown标题语法 (#)', '使用纯文本格式,如"一、"'),
            (r'^\s*[-*•○]\s', '列表符号 (-/*/•)', '转换为完整句子段落'),
            (r'\*\*.*\*\*', '加粗语法 (**)', '移除加粗标记'),
            (r'\|.*\|', '表格语法', '转换为叙述性文字'),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, markdown_type, recommendation in prohibited_markdown:
                if re.search(pattern, line):
                    self.violations.append(Violation(
                        line_num=line_num,
                        severity='CRITICAL',
                        category='格式不符合要求',
                        description=f'检测到{markdown_type}',
                        context=line.strip(),
                        recommendation=recommendation
                    ))

    def _is_metadata_line(self, line: str) -> bool:
        """Check if line is metadata (not factual content)"""
        metadata_patterns = [
            r'^#',  # Markdown heading
            r'^\s*$',  # Empty line
            r'^---',  # Separator
            r'^\*\*.*\*\*:\s*$',  # Bold label with colon
        ]
        return any(re.search(pattern, line) for pattern in metadata_patterns)

    def _is_heading_line(self, line: str) -> bool:
        """Check if line is a heading"""
        heading_patterns = [
            r'^#{1,6}\s',  # Markdown heading
            r'^[一二三四五六七八九十]+、',  # Chinese numbered heading
            r'^\d+\.\s',  # Numbered heading
        ]
        return any(re.search(pattern, line) for pattern in heading_patterns)

    def _calculate_statistics(self) -> Dict:
        """Calculate violation statistics"""
        stats = {
            'total': len(self.violations),
            'by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'by_category': {}
        }

        for v in self.violations:
            stats['by_severity'][v.severity] += 1
            if v.category not in stats['by_category']:
                stats['by_category'][v.category] = 0
            stats['by_category'][v.category] += 1

        return stats


def format_report(result: Dict) -> str:
    """Format check results into readable report"""
    if 'error' in result:
        return f"\n❌ 错误: {result['error']}\n"

    lines = []
    lines.append("=" * 80)
    lines.append("反编造验证报告 (Anti-Fabrication Verification Report)")
    lines.append("=" * 80)
    lines.append(f"\n文件: {result['file']}")
    lines.append(f"报告类型: {result['report_type']}")
    lines.append(f"总行数: {result['total_lines']}")
    lines.append("")

    stats = result['statistics']
    lines.append("验证结果摘要:")
    lines.append(f"  总违规数: {stats['total']}")
    lines.append(f"  严重级别分布:")
    lines.append(f"    - CRITICAL (严重): {stats['by_severity']['CRITICAL']}")
    lines.append(f"    - HIGH (高): {stats['by_severity']['HIGH']}")
    lines.append(f"    - MEDIUM (中): {stats['by_severity']['MEDIUM']}")
    lines.append(f"    - LOW (低): {stats['by_severity']['LOW']}")
    lines.append("")

    if result['passed']:
        lines.append("✅ 通过 - 未检测到违规")
    else:
        lines.append(f"❌ 失败 - 检测到 {stats['total']} 处违规")
        lines.append("")
        lines.append("=" * 80)
        lines.append("详细违规列表:")
        lines.append("=" * 80)

        # Group by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            severity_violations = [v for v in result['violations'] if v.severity == severity]
            if not severity_violations:
                continue

            lines.append(f"\n【{severity}】{len(severity_violations)} 处违规:")
            lines.append("-" * 80)

            for i, v in enumerate(severity_violations, 1):
                lines.append(f"\n{i}. 第 {v.line_num} 行")
                lines.append(f"   类别: {v.category}")
                lines.append(f"   描述: {v.description}")
                lines.append(f"   内容: {v.context[:100]}{'...' if len(v.context) > 100 else ''}")
                lines.append(f"   建议: {v.recommendation}")

        lines.append("")
        lines.append("=" * 80)
        lines.append("修复建议:")
        lines.append("=" * 80)

        # Category-specific recommendations
        if stats['by_category'].get('禁止推测性表述', 0) > 0:
            lines.append("\n【禁止推测性表述】:")
            lines.append("  - 移除所有\"应该是\"、\"可能是\"、\"一般来说\"等推测性短语")
            lines.append("  - 如证据不明确,使用[证据未记载]等缺失标记")
            lines.append("  - 法律推理需引用法律依据: 依据《XX法》第X条")

        if stats['by_category'].get('缺少证据引用', 0) > 0:
            lines.append("\n【缺少证据引用】:")
            lines.append("  - 每个事实陈述必须标注证据来源和页码")
            lines.append("  - 格式: （见XX第X页）或（见《XX》第X条,第X页）")
            lines.append("  - 如证据缺失,使用[证据未记载]明确标注")

        if stats['by_category'].get('未替换占位符', 0) > 0:
            lines.append("\n【未替换占位符】:")
            lines.append("  - 替换所有[年月日]、[金额]、[X]等占位符为实际内容")
            lines.append("  - 如信息缺失,使用标准缺失标记: [证据未记载]、[债权人未填写]")

        if stats['by_category'].get('格式不符合要求', 0) > 0:
            lines.append("\n【格式不符合要求】:")
            lines.append("  - 移除所有Markdown语法: ##、-、**等")
            lines.append("  - 转换为纯文本段落格式")
            lines.append("  - 章节标题使用\"一、\"、\"二、\"格式")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Anti-Fabrication Checker for Debt Review Reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check fact-checking report
  python anti_fabrication_checker.py 工作底稿/XX公司_事实核查报告.md --report-type fact-checking

  # Check debt analysis report
  python anti_fabrication_checker.py 工作底稿/XX公司_债权分析报告.md --report-type debt-analysis

  # Check review opinion form
  python anti_fabrication_checker.py 最终报告/GY2025_XX公司_债权审查报告_20251106.md --report-type review-opinion

Report Types:
  fact-checking   事实核查报告
  debt-analysis   债权分析报告
  review-opinion  审查意见表
        """
    )

    parser.add_argument('file', help='Path to report file to check')
    parser.add_argument(
        '--report-type',
        choices=['fact-checking', 'debt-analysis', 'review-opinion'],
        default='fact-checking',
        help='Type of report (default: fact-checking)'
    )
    parser.add_argument(
        '--output',
        help='Output file for report (default: stdout)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error code if violations found'
    )

    args = parser.parse_args()

    # Run checker
    checker = AntiFabricationChecker(report_type=args.report_type)
    result = checker.check_file(args.file)

    # Format report
    report = format_report(result)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"验证报告已保存至: {args.output}")
    else:
        print(report)

    # Exit code
    if args.strict and not result.get('passed', False):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
