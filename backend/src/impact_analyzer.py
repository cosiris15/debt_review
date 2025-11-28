# -*- coding: utf-8 -*-
"""
影响分析器 - 多轮交互系统的核心决策引擎

分析字段变更的影响范围，智能决定处理模式（Full/Incremental/Partial），
并实施保守策略确保准确性。
"""

import sys
from pathlib import Path
from typing import List, Set, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.field_priorities import (
    FIELD_PRIORITIES,
    get_field_priority,
    get_highest_priority,
    is_critical_field
)
from config.impact_mappings import (
    IMPACT_MAPPINGS,
    DEBT_ITEM_TYPES,
    REPORT_SECTIONS,
    CHAPTER_DEPENDENCIES,
    get_combined_impact,
    get_chapters_to_update
)


class ProcessingMode(Enum):
    """处理模式枚举"""
    FULL = "full"
    INCREMENTAL = "incremental"
    PARTIAL = "partial"


@dataclass
class ImpactAnalysisResult:
    """影响分析结果数据类"""
    processing_mode: ProcessingMode
    affected_stages: List[int]
    affected_debt_items: List[str]
    affected_sections: List[int]
    fields_updated: List[str]
    highest_priority: str
    time_savings_percent: int
    reasoning: str
    user_confirm_required: bool
    unknown_fields: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于JSON序列化）"""
        result = asdict(self)
        result['processing_mode'] = self.processing_mode.value
        return result

    def summary(self) -> str:
        """生成用户友好的摘要"""
        lines = [
            "=" * 60,
            "🔍 影响分析结果",
            "=" * 60,
            f"变更字段: {', '.join(self.fields_updated)}",
            f"最高优先级: {self.highest_priority}",
            f"建议处理模式: {self.processing_mode.value}",
            f"受影响阶段: Stage {', '.join(map(str, self.affected_stages))}",
        ]

        if self.affected_debt_items:
            lines.append(f"受影响债权项: {', '.join(self.affected_debt_items[:5])}")
            if len(self.affected_debt_items) > 5:
                lines.append(f"               (共{len(self.affected_debt_items)}项)")

        if self.affected_sections:
            lines.append(f"受影响章节: 第{', '.join(map(str, self.affected_sections))}章")

        lines.append(f"预计节省时间: {self.time_savings_percent}%")
        lines.append(f"原因: {self.reasoning}")

        if self.unknown_fields:
            lines.append(f"⚠️  未知字段: {', '.join(self.unknown_fields)}")

        if self.user_confirm_required:
            lines.append(f"\n⚠️  需要用户确认后才能继续处理")
        else:
            lines.append(f"\n✓ 无需确认，将自动执行")

        lines.append("=" * 60)

        return "\n".join(lines)


class ImpactAnalyzer:
    """影响范围分析器 - 实施保守策略"""

    def __init__(self, conservative: bool = True):
        """初始化影响分析器

        Args:
            conservative: 是否使用保守策略（默认True）
        """
        self.conservative = conservative
        self.field_priorities = FIELD_PRIORITIES
        self.impact_mappings = IMPACT_MAPPINGS

    def analyze_impact(self, fields_updated: List[str]) -> ImpactAnalysisResult:
        """分析字段变更的影响范围（核心方法）

        Args:
            fields_updated: 变更的字段列表

        Returns:
            ImpactAnalysisResult: 完整的影响分析结果
        """
        if not fields_updated:
            return ImpactAnalysisResult(
                processing_mode=ProcessingMode.PARTIAL,
                affected_stages=[],
                affected_debt_items=[],
                affected_sections=[],
                fields_updated=[],
                highest_priority="LOW",
                time_savings_percent=100,
                reasoning="无字段变更",
                user_confirm_required=False,
                unknown_fields=[]
            )

        # 1. 识别未知字段（保守策略关键）
        unknown_fields = self._identify_unknown_fields(fields_updated)

        # 2. 确定最高优先级
        highest_priority = get_highest_priority(fields_updated)

        # 3. 如果有未知字段，保守处理为CRITICAL
        if unknown_fields and self.conservative:
            print(f"⚠️  检测到未知字段: {', '.join(unknown_fields)}")
            print(f"⚠️  保守策略：将触发完整重审（Full模式）")
            highest_priority = "CRITICAL"

        # 4. 根据优先级确定处理模式
        processing_mode, user_confirm_required, reasoning = \
            self._determine_processing_mode(highest_priority, unknown_fields)

        # 5. 计算影响范围
        combined = get_combined_impact(fields_updated)
        affected_stages = combined['affected_stages']
        affected_debt_items = combined['affected_debt_items']
        affected_sections = combined['affected_sections']

        # 6. 应用章节依赖管理
        if affected_sections and processing_mode != ProcessingMode.FULL:
            affected_sections = get_chapters_to_update(affected_sections)

        # 7. 计算预计节省时间
        time_savings = self._calculate_time_savings(
            processing_mode,
            affected_stages,
            len(fields_updated)
        )

        return ImpactAnalysisResult(
            processing_mode=processing_mode,
            affected_stages=affected_stages,
            affected_debt_items=affected_debt_items,
            affected_sections=affected_sections,
            fields_updated=fields_updated,
            highest_priority=highest_priority,
            time_savings_percent=time_savings,
            reasoning=reasoning,
            user_confirm_required=user_confirm_required,
            unknown_fields=unknown_fields
        )

    def _identify_unknown_fields(self, fields: List[str]) -> List[str]:
        """识别未知字段（未在FIELD_PRIORITIES中定义的字段）

        Args:
            fields: 字段列表

        Returns:
            List[str]: 未知字段列表
        """
        unknown = []
        for field in fields:
            if get_field_priority(field) is None:
                unknown.append(field)
        return unknown

    def _determine_processing_mode(
        self,
        highest_priority: str,
        unknown_fields: List[str]
    ) -> tuple:
        """确定处理模式（实施保守策略）

        Args:
            highest_priority: 最高优先级
            unknown_fields: 未知字段列表

        Returns:
            tuple: (processing_mode, user_confirm_required, reasoning)
        """
        # 保守策略：未知字段或CRITICAL字段 → Full模式，无需确认
        if unknown_fields or highest_priority == "CRITICAL":
            if unknown_fields:
                reasoning = (
                    f"检测到未知字段 {', '.join(unknown_fields)}，"
                    f"保守策略触发完整重审以确保准确性"
                )
            else:
                reasoning = "检测到CRITICAL字段变更，必须完整重审以确保准确性"

            return ProcessingMode.FULL, False, reasoning

        # HIGH字段 → Incremental模式，需要用户确认
        elif highest_priority == "HIGH":
            reasoning = (
                "检测到HIGH字段变更（如补充证据、担保方式变更），"
                "建议增量处理以节省时间"
            )
            return ProcessingMode.INCREMENTAL, True, reasoning

        # MEDIUM字段 → Incremental模式（保守策略：不用Partial），需要确认
        elif highest_priority == "MEDIUM":
            if self.conservative:
                reasoning = (
                    "检测到MEDIUM字段变更，保守策略建议增量处理"
                )
                return ProcessingMode.INCREMENTAL, True, reasoning
            else:
                reasoning = "检测到MEDIUM字段变更，建议增量处理"
                return ProcessingMode.INCREMENTAL, True, reasoning

        # LOW字段 → Partial模式，需要确认
        else:  # LOW or None
            reasoning = "检测到LOW字段变更，仅需局部更新"
            return ProcessingMode.PARTIAL, True, reasoning

    def _calculate_time_savings(
        self,
        processing_mode: ProcessingMode,
        affected_stages: List[int],
        field_count: int
    ) -> int:
        """计算预计节省时间百分比

        Args:
            processing_mode: 处理模式
            affected_stages: 受影响的Stage列表
            field_count: 变更字段数量

        Returns:
            int: 节省时间百分比 (0-100)
        """
        if processing_mode == ProcessingMode.FULL:
            return 0

        elif processing_mode == ProcessingMode.INCREMENTAL:
            # 基于受影响的Stage数量计算
            total_stages = 3
            skipped_stages = total_stages - len(affected_stages)

            # 基础节省 = (跳过的Stage / 总Stage) * 100
            base_savings = (skipped_stages / total_stages) * 100

            # 即使没有跳过Stage，Stage内部的增量处理也能节省时间
            if base_savings == 0:
                # 如果所有Stage都受影响，但是增量处理每个Stage
                # 预计节省40-60%
                base_savings = 50

            # 根据字段数量微调（字段越多，节省越少）
            if field_count > 5:
                adjustment = -10
            elif field_count > 3:
                adjustment = -5
            else:
                adjustment = 0

            savings = max(40, min(75, int(base_savings + adjustment)))
            return savings

        else:  # Partial
            # Partial模式节省85%+
            return 85

    def generate_detailed_analysis(
        self,
        fields_updated: List[str]
    ) -> Dict[str, Any]:
        """生成详细的影响分析报告（供开发调试和用户查看）

        Args:
            fields_updated: 变更字段列表

        Returns:
            Dict: 详细分析报告
        """
        analysis = self.analyze_impact(fields_updated)

        # 为每个字段生成详细信息
        field_details = []
        for field in fields_updated:
            priority = get_field_priority(field)
            impact = IMPACT_MAPPINGS.get(field)

            detail = {
                "field_name": field,
                "priority": priority if priority else "UNKNOWN",
                "is_known": priority is not None
            }

            if impact:
                detail["impact"] = {
                    "stages": impact.get("stages", []),
                    "debt_items": impact.get("debt_items", []),
                    "report_sections": impact.get("report_sections", []),
                    "reason": impact.get("reason", "")
                }
            else:
                detail["impact"] = None

            field_details.append(detail)

        return {
            "summary": analysis.to_dict(),
            "field_details": field_details,
            "recommendations": self._generate_recommendations(analysis)
        }

    def _generate_recommendations(
        self,
        analysis: ImpactAnalysisResult
    ) -> List[str]:
        """生成处理建议

        Args:
            analysis: 影响分析结果

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        if analysis.processing_mode == ProcessingMode.FULL:
            recommendations.append(
                "建议：完整重审所有内容，确保不遗漏任何影响"
            )
            recommendations.append(
                "预计时间：12-15分钟（与首次处理相同）"
            )

        elif analysis.processing_mode == ProcessingMode.INCREMENTAL:
            recommendations.append(
                f"建议：仅重新处理受影响的部分，预计节省{analysis.time_savings_percent}%时间"
            )
            recommendations.append(
                f"将执行Stage: {', '.join(map(str, analysis.affected_stages))}"
            )

            if analysis.affected_stages != [1, 2, 3]:
                skipped = [s for s in [1, 2, 3] if s not in analysis.affected_stages]
                recommendations.append(
                    f"将跳过Stage: {', '.join(map(str, skipped))}（复用前轮结果）"
                )

        else:  # Partial
            recommendations.append(
                f"建议：仅更新受影响的最小单元，预计节省{analysis.time_savings_percent}%时间"
            )
            recommendations.append(
                "大部分内容将直接复用前轮结果"
            )

        if analysis.unknown_fields:
            recommendations.append(
                f"⚠️  注意：未知字段 {', '.join(analysis.unknown_fields)} 已保守处理为CRITICAL"
            )

        return recommendations

    def compare_configs(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any]
    ) -> ImpactAnalysisResult:
        """比较两个配置，识别变更字段并分析影响

        Args:
            old_config: 旧配置（前轮）
            new_config: 新配置（本轮）

        Returns:
            ImpactAnalysisResult: 影响分析结果
        """
        fields_updated = self._identify_changed_fields(old_config, new_config)
        return self.analyze_impact(fields_updated)

    def _identify_changed_fields(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any]
    ) -> List[str]:
        """识别变更的字段

        Args:
            old_config: 旧配置
            new_config: 新配置

        Returns:
            List[str]: 变更字段列表
        """
        changed = []

        # 获取所有字段（新旧配置的并集）
        all_keys = set(old_config.keys()) | set(new_config.keys())

        for key in all_keys:
            old_value = old_config.get(key)
            new_value = new_config.get(key)

            # 比较值是否变更
            if old_value != new_value:
                changed.append(key)

        return changed


def main():
    """命令行测试入口"""
    print("=" * 60)
    print("影响分析器测试")
    print("=" * 60)

    analyzer = ImpactAnalyzer(conservative=True)

    # 测试场景1: CRITICAL字段变更
    print("\n测试1: CRITICAL字段变更（破产日期）")
    print("-" * 60)
    result = analyzer.analyze_impact(["bankruptcy_date"])
    print(result.summary())

    # 测试场景2: HIGH字段变更（补充证据）
    print("\n\n测试2: HIGH字段变更（补充证据）")
    print("-" * 60)
    result = analyzer.analyze_impact(["judgment_document", "performance_evidence"])
    print(result.summary())

    # 测试场景3: MEDIUM字段变更（金额调整）
    print("\n\n测试3: MEDIUM字段变更（金额调整）")
    print("-" * 60)
    result = analyzer.analyze_impact(["declared_principal"])
    print(result.summary())

    # 测试场景4: LOW字段变更（联系方式）
    print("\n\n测试4: LOW字段变更（联系方式）")
    print("-" * 60)
    result = analyzer.analyze_impact(["creditor_contact"])
    print(result.summary())

    # 测试场景5: 未知字段（保守策略）
    print("\n\n测试5: 未知字段（保守策略）")
    print("-" * 60)
    result = analyzer.analyze_impact(["unknown_field_123"])
    print(result.summary())

    # 测试场景6: 混合优先级字段
    print("\n\n测试6: 混合优先级字段")
    print("-" * 60)
    result = analyzer.analyze_impact([
        "judgment_document",  # HIGH
        "declared_principal",  # MEDIUM
        "notes"  # LOW
    ])
    print(result.summary())

    # 测试场景7: 配置比较
    print("\n\n测试7: 配置比较")
    print("-" * 60)
    old_config = {
        "bankruptcy_date": "2024-12-31",
        "judgment_document": None,
        "declared_principal": "100万元"
    }
    new_config = {
        "bankruptcy_date": "2024-12-31",  # 不变
        "judgment_document": {  # 新增
            "case_number": "（2024）沪01民初123号"
        },
        "declared_principal": "95万元"  # 变更
    }
    result = analyzer.compare_configs(old_config, new_config)
    print(result.summary())

    # 测试场景8: 详细分析
    print("\n\n测试8: 详细分析报告")
    print("-" * 60)
    detailed = analyzer.generate_detailed_analysis(["judgment_document", "declared_principal"])
    print(f"\n变更字段详情:")
    for field_detail in detailed['field_details']:
        print(f"\n  字段: {field_detail['field_name']}")
        print(f"  优先级: {field_detail['priority']}")
        if field_detail.get('impact'):
            print(f"  受影响Stage: {field_detail['impact']['stages']}")
            print(f"  原因: {field_detail['impact']['reason']}")

    print(f"\n处理建议:")
    for rec in detailed['recommendations']:
        print(f"  - {rec}")


if __name__ == "__main__":
    main()
