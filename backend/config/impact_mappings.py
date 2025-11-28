# -*- coding: utf-8 -*-
"""
影响分析映射表

定义每个字段变更时的具体影响范围，用于增量处理决策。

影响范围包括：
- stages: 受影响的处理阶段 (1=事实核查, 2=债权分析, 3=报告整理)
- debt_items: 受影响的债权项目类型
- report_sections: 受影响的报告章节编号
"""

from typing import Dict, List, Any

# ========== 债权项目类型定义 ==========
DEBT_ITEM_TYPES: List[str] = [
    "本金",
    "利息",
    "违约金",
    "逾期利息",
    "罚息",
    "复利",
    "担保债权",
    "保证债权",
    "ALL"  # 通配符：表示所有债权项
]

# ========== 报告章节定义 ==========
REPORT_SECTIONS: Dict[Any, str] = {
    1: "债权人基本信息",
    2: "债权申报情况",
    3: "事实查明与证据认定",
    4: "债权金额确认意见",
    5: "综合审查意见",
    6: "备注说明",
    "ALL": "所有章节"
}

# ========== 章节依赖关系 ==========
# 定义章节之间的依赖关系：如果前置章节变更，依赖它的后续章节也需要更新
CHAPTER_DEPENDENCIES: Dict[int, List[int]] = {
    1: [],  # 债权人基本信息，无依赖
    2: [1],  # 债权申报情况，依赖第1章
    3: [1, 2],  # 事实查明，依赖第1、2章
    4: [2, 3],  # 债权金额确认，依赖第2、3章
    5: [1, 2, 3, 4],  # 综合审查意见，依赖所有前章
    6: []  # 备注说明，无依赖
}

# ========== 影响分析映射表 ==========

IMPACT_MAPPINGS: Dict[str, Dict[str, Any]] = {
    # ========== CRITICAL字段影响映射 ==========

    "bankruptcy_date": {
        "stages": [1, 2, 3],
        "debt_items": ["ALL"],
        "report_sections": ["ALL"],
        "reason": "破产日期变更影响所有日期计算和时间节点，必须完整重审"
    },

    "interest_stop_date": {
        "stages": [2, 3],
        "debt_items": ["利息", "违约金", "逾期利息", "罚息", "复利"],
        "report_sections": [2, 3, 4, 5],
        "reason": "停止计息日变更影响所有利息类计算结果"
    },

    "legal_relationship_type": {
        "stages": [1, 2, 3],
        "debt_items": ["ALL"],
        "report_sections": ["ALL"],
        "reason": "法律关系变更影响适用法律标准、举证责任和整体分析框架"
    },

    "debt_nature": {
        "stages": [1, 3],
        "debt_items": ["ALL"],
        "report_sections": [1, 2, 3, 5],
        "reason": "债权性质变更影响清偿顺位和分组认定"
    },

    "statute_of_limitations_status": {
        "stages": [2, 3],
        "debt_items": ["ALL"],
        "report_sections": [3, 4, 5],
        "reason": "诉讼时效状态变更影响债权可获清偿性和最终确认意见"
    },

    # ========== HIGH字段影响映射 ==========

    "judgment_document": {
        "stages": [1, 2, 3],
        "debt_items": ["ALL"],
        "report_sections": [2, 3, 4, 5],
        "reason": "生效法律文书是最高证据等级，影响所有事实认定和金额确认"
    },

    "performance_evidence": {
        "stages": [1, 2, 3],
        "debt_items": ["本金", "利息", "违约金"],
        "report_sections": [2, 3, 4],
        "reason": "履行证据补充影响金额确认和事实认定，特别是本金和利息基数"
    },

    "guarantee_type": {
        "stages": [1, 3],
        "debt_items": ["担保债权", "保证债权"],
        "report_sections": [2, 3, 4, 5],
        "reason": "担保方式变更影响债权性质认定、清偿顺位和优先受偿权分析"
    },

    "collateral_value": {
        "stages": [1, 3],
        "debt_items": ["担保债权"],
        "report_sections": [3, 4, 5],
        "reason": "担保物价值变更影响清偿可能性评估和优先受偿范围"
    },

    "interest_rate_clause": {
        "stages": [2, 3],
        "debt_items": ["利息", "复利", "逾期利息"],
        "report_sections": [3, 4],
        "reason": "利率约定变更需重新计算利息"
    },

    "penalty_clause": {
        "stages": [2, 3],
        "debt_items": ["违约金", "罚息"],
        "report_sections": [3, 4],
        "reason": "违约金约定变更需重新计算违约金并重新应用30%上限规则"
    },

    # ========== MEDIUM字段影响映射 ==========

    "contract_signing_date": {
        "stages": [2],
        "debt_items": [],  # 不直接影响具体债权项
        "report_sections": [3],
        "reason": "合同日期影响诉讼时效起算点，需重新分析时效问题"
    },

    "payment_deadline": {
        "stages": [2],
        "debt_items": ["利息", "逾期利息"],
        "report_sections": [3, 4],
        "reason": "付款期限影响利息起算日，需重新计算利息"
    },

    "declared_principal": {
        "stages": [2],
        "debt_items": ["本金"],
        "report_sections": [2, 4],
        "reason": "申报本金变更影响就低原则适用，需重新确认本金金额"
    },

    "declared_interest": {
        "stages": [2],
        "debt_items": ["利息"],
        "report_sections": [2, 4],
        "reason": "申报利息变更影响就低原则适用，需重新确认利息金额"
    },

    "creditor_contact": {
        "stages": [3],
        "debt_items": [],
        "report_sections": [1],
        "reason": "联系方式变更仅影响报告抬头，不影响法律认定"
    },

    # ========== LOW字段影响映射 ==========

    "project_description": {
        "stages": [3],
        "debt_items": [],
        "report_sections": [1],
        "reason": "项目描述变更仅影响报告背景章节"
    },

    "notes": {
        "stages": [3],
        "debt_items": [],
        "report_sections": [6],
        "reason": "备注变更仅影响报告备注章节"
    },

    "processing_date": {
        "stages": [],
        "debt_items": [],
        "report_sections": [],
        "reason": "自动生成字段，不影响任何内容"
    }
}

# ========== 辅助函数 ==========

def get_impact_for_field(field_name: str) -> Dict[str, Any]:
    """获取单个字段的影响范围

    Args:
        field_name: 字段名称

    Returns:
        Dict: 影响范围字典，如果字段未知则返回None
    """
    return IMPACT_MAPPINGS.get(field_name)


def get_combined_impact(field_names: List[str]) -> Dict[str, Any]:
    """获取多个字段变更的合并影响范围

    Args:
        field_names: 字段名称列表

    Returns:
        Dict: 合并后的影响范围
    """
    combined_stages = set()
    combined_debt_items = set()
    combined_sections = set()
    unknown_fields = []

    for field in field_names:
        mapping = IMPACT_MAPPINGS.get(field)
        if mapping:
            combined_stages.update(mapping.get("stages", []))
            combined_debt_items.update(mapping.get("debt_items", []))
            combined_sections.update(mapping.get("report_sections", []))
        else:
            unknown_fields.append(field)

    # 处理通配符
    if "ALL" in combined_debt_items:
        combined_debt_items = set(DEBT_ITEM_TYPES)
        combined_debt_items.discard("ALL")

    if "ALL" in combined_sections:
        combined_sections = set([k for k in REPORT_SECTIONS.keys() if isinstance(k, int)])

    return {
        "affected_stages": sorted(combined_stages),
        "affected_debt_items": sorted(combined_debt_items),
        "affected_sections": sorted(combined_sections),
        "unknown_fields": unknown_fields
    }


def get_chapters_to_update(directly_affected: List[int]) -> List[int]:
    """获取需要更新的所有章节（含依赖章节）

    根据章节依赖关系，计算除了直接受影响的章节外，
    还有哪些依赖这些章节的后续章节也需要更新。

    Args:
        directly_affected: 直接受影响的章节编号列表

    Returns:
        List[int]: 需要更新的所有章节编号（已排序）

    Example:
        >>> get_chapters_to_update([3])  # 第3章受影响
        [3, 4, 5]  # 第3章 + 第4章（依赖3） + 第5章（依赖3、4）
    """
    to_update = set(directly_affected)

    # 递归添加依赖于受影响章节的章节
    for chapter, deps in CHAPTER_DEPENDENCIES.items():
        if any(dep in directly_affected for dep in deps):
            to_update.add(chapter)

            # 递归处理：如果这个章节被加入，需要检查是否有其他章节依赖它
            sub_affected = get_chapters_to_update([chapter])
            to_update.update(sub_affected)

    return sorted(to_update)


def is_debt_item_affected(debt_item: str, affected_items: List[str]) -> bool:
    """判断债权项是否受影响

    Args:
        debt_item: 债权项名称
        affected_items: 受影响的债权项列表

    Returns:
        bool: 是否受影响
    """
    if "ALL" in affected_items:
        return True

    # 特殊处理：如果利息受影响，复利也受影响
    if "利息" in affected_items and debt_item in ["复利", "逾期利息"]:
        return True

    return debt_item in affected_items


def get_stage_name(stage_number: int) -> str:
    """获取Stage的名称

    Args:
        stage_number: Stage编号 (1, 2, 3)

    Returns:
        str: Stage名称
    """
    stage_names = {
        1: "事实核查 (debt-fact-checker)",
        2: "债权分析 (debt-claim-analyzer)",
        3: "报告整理 (report-organizer)"
    }
    return stage_names.get(stage_number, f"Stage {stage_number}")


def validate_impact_mappings() -> tuple:
    """验证影响映射表的完整性和一致性

    Returns:
        tuple: (is_valid: bool, errors: List[str])
    """
    errors = []

    # 验证：所有debt_items必须在DEBT_ITEM_TYPES中
    for field, mapping in IMPACT_MAPPINGS.items():
        debt_items = mapping.get("debt_items", [])
        for item in debt_items:
            if item not in DEBT_ITEM_TYPES:
                errors.append(f"字段 {field} 引用了未知的债权项: {item}")

    # 验证：所有report_sections必须在REPORT_SECTIONS中
    for field, mapping in IMPACT_MAPPINGS.items():
        sections = mapping.get("report_sections", [])
        valid_sections = list(REPORT_SECTIONS.keys())
        for section in sections:
            if section not in valid_sections:
                errors.append(f"字段 {field} 引用了未知的章节: {section}")

    # 验证：stages必须在1-3之间
    for field, mapping in IMPACT_MAPPINGS.items():
        stages = mapping.get("stages", [])
        for stage in stages:
            if stage not in [1, 2, 3]:
                errors.append(f"字段 {field} 引用了无效的Stage: {stage}")

    return len(errors) == 0, errors


if __name__ == "__main__":
    # 测试代码
    print("===== 影响分析映射表测试 =====\n")

    # 测试1: 获取单个字段影响
    print("测试1: 获取单个字段影响")
    test_fields = ["bankruptcy_date", "judgment_document", "declared_principal"]
    for field in test_fields:
        impact = get_impact_for_field(field)
        if impact:
            print(f"\n  字段: {field}")
            print(f"  受影响Stage: {impact['stages']}")
            print(f"  受影响债权项: {impact['debt_items']}")
            print(f"  受影响章节: {impact['report_sections']}")
            print(f"  原因: {impact['reason']}")

    # 测试2: 合并多个字段影响
    print("\n\n测试2: 合并多个字段影响")
    combined = get_combined_impact(["judgment_document", "declared_principal"])
    print(f"  字段: judgment_document + declared_principal")
    print(f"  受影响Stage: {combined['affected_stages']}")
    print(f"  受影响债权项: {combined['affected_debt_items']}")
    print(f"  受影响章节: {combined['affected_sections']}")

    # 测试3: 章节依赖管理
    print("\n\n测试3: 章节依赖管理")
    test_cases = [[3], [2], [1, 4]]
    for directly_affected in test_cases:
        all_affected = get_chapters_to_update(directly_affected)
        print(f"  直接受影响章节: {directly_affected}")
        print(f"  需要更新章节: {all_affected}")

    # 测试4: 验证映射表
    print("\n\n测试4: 验证映射表")
    is_valid, errors = validate_impact_mappings()
    if is_valid:
        print("  ✅ 映射表验证通过")
    else:
        print("  ❌ 映射表验证失败:")
        for error in errors:
            print(f"    - {error}")

    # 测试5: 统计
    print("\n\n测试5: 统计信息")
    print(f"  定义字段数: {len(IMPACT_MAPPINGS)}")
    print(f"  债权项类型数: {len(DEBT_ITEM_TYPES)}")
    print(f"  报告章节数: {len([k for k in REPORT_SECTIONS.keys() if isinstance(k, int)])}")
