# -*- coding: utf-8 -*-
"""
字段优先级分类系统

定义债权审查系统中所有配置字段的优先级，用于影响分析和处理模式决策。

优先级定义：
- CRITICAL: 变更触发完整重审（Full模式），0%节省时间
- HIGH: 变更触发增量处理（Incremental模式），60-75%节省时间
- MEDIUM: 变更触发增量处理（Incremental模式），70-80%节省时间
- LOW: 变更触发局部更新（Partial模式），85%+节省时间
"""

from typing import Dict, Any

# ========== CRITICAL字段（5个）==========
# 触发条件：完整重审（Full模式）
# 典型场景：首轮处理、关键信息变更

CRITICAL_FIELDS: Dict[str, Dict[str, Any]] = {
    "bankruptcy_date": {
        "display_name": "破产受理日期",
        "reason": "决定所有法律期限和利息计算终点，影响所有时间节点",
        "impact_description": "影响所有Stage和所有债权项",
        "example": "2024-12-31",
        "validation": {
            "type": "date",
            "format": "YYYY-MM-DD",
            "required": True
        }
    },

    "interest_stop_date": {
        "display_name": "停止计息日期",
        "reason": "直接影响所有利息计算结果，必须等于破产受理日期前一日",
        "impact_description": "影响Stage 2和所有利息类计算",
        "example": "2024-12-30",
        "validation": {
            "type": "date",
            "format": "YYYY-MM-DD",
            "required": True,
            "relationship": "bankruptcy_date - 1 day"
        }
    },

    "legal_relationship_type": {
        "display_name": "法律关系类型",
        "reason": "决定适用法律标准、举证责任和法律关系认定",
        "impact_description": "影响所有Stage和法律分析框架",
        "example": "买卖合同关系|借款合同关系|建设工程施工合同关系|承揽合同关系",
        "validation": {
            "type": "enum",
            "options": [
                "买卖合同关系",
                "借款合同关系",
                "建设工程施工合同关系",
                "承揽合同关系",
                "租赁合同关系",
                "服务合同关系",
                "其他"
            ],
            "required": True
        }
    },

    "debt_nature": {
        "display_name": "债权性质",
        "reason": "决定劣后顺位、清偿优先级和分组",
        "impact_description": "影响Stage 1和Stage 3，涉及清偿顺序认定",
        "example": "普通债权|担保债权|职工债权|税收债权",
        "validation": {
            "type": "enum",
            "options": [
                "担保债权",
                "职工债权",
                "税收债权",
                "普通债权",
                "劣后债权"
            ],
            "required": True
        }
    },

    "statute_of_limitations_status": {
        "display_name": "诉讼时效状态",
        "reason": "决定债权是否可获清偿，影响最终确认意见",
        "impact_description": "影响Stage 2和Stage 3，涉及诉讼时效分析",
        "example": "未过时效|已过时效但有中断|已过时效",
        "validation": {
            "type": "enum",
            "options": [
                "未过时效",
                "已过时效但有中断",
                "已过时效但有延长",
                "已过时效"
            ],
            "required": True
        }
    }
}

# ========== HIGH字段（6个）==========
# 触发条件：增量处理（Incremental模式）
# 典型场景：补充证据材料、担保方式变更

HIGH_FIELDS: Dict[str, Dict[str, Any]] = {
    "judgment_document": {
        "display_name": "生效法律文书",
        "reason": "最高证据等级，影响所有事实认定和金额确认",
        "impact_description": "影响所有Stage，特别是证据效力和金额依据",
        "example": {
            "document_type": "民事判决书",
            "case_number": "（2024）沪01民初123号",
            "judgment_date": "2024-06-15",
            "judgment_amount": {
                "principal": "100万元",
                "interest": "5万元"
            }
        },
        "validation": {
            "type": "object",
            "required": False,
            "note": "如有生效法律文书，必须提供案号和判决日期"
        }
    },

    "performance_evidence": {
        "display_name": "履行证据",
        "reason": "影响金额确认和事实认定，特别是本金和实际履行情况",
        "impact_description": "影响Stage 1和Stage 2，涉及本金和利息计算基数",
        "example": ["银行流水", "发票", "送货签收单", "对账单", "收款收据"],
        "validation": {
            "type": "list",
            "required": False,
            "note": "补充证据时需详细列出证据类型"
        }
    },

    "guarantee_type": {
        "display_name": "担保方式",
        "reason": "影响债权性质认定、清偿顺位和优先受偿权",
        "impact_description": "影响Stage 1和Stage 3，涉及担保债权认定",
        "example": "抵押担保|保证担保|质押担保|留置担保|无担保",
        "validation": {
            "type": "enum",
            "options": [
                "抵押担保",
                "保证担保",
                "质押担保",
                "留置担保",
                "定金担保",
                "无担保"
            ],
            "required": False
        }
    },

    "collateral_value": {
        "display_name": "担保物价值",
        "reason": "影响债权清偿可能性评估和优先受偿范围",
        "impact_description": "影响Stage 1和Stage 3，涉及清偿分析",
        "example": {
            "appraised_value": "500万元",
            "appraisal_date": "2024-10-15",
            "appraiser": "XX评估公司"
        },
        "validation": {
            "type": "object",
            "required": False,
            "note": "如有担保物，建议提供评估价值"
        }
    },

    "interest_rate_clause": {
        "display_name": "利率约定",
        "reason": "直接影响利息计算，包括利率类型、利率值和计算方式",
        "impact_description": "影响Stage 2和Stage 3，涉及利息计算",
        "example": {
            "rate_type": "固定利率",
            "annual_rate": "6%",
            "calculation_method": "单利"
        },
        "validation": {
            "type": "object",
            "required": False,
            "note": "未约定利率时按LPR处理"
        }
    },

    "penalty_clause": {
        "display_name": "违约金约定",
        "reason": "影响违约金计算和上限适用（30%本金上限）",
        "impact_description": "影响Stage 2和Stage 3，涉及违约金认定",
        "example": {
            "penalty_type": "固定金额|按日计算|按比例计算",
            "penalty_rate": "每日千分之一",
            "penalty_cap": "本金的30%"
        },
        "validation": {
            "type": "object",
            "required": False,
            "note": "违约金需注意30%本金上限"
        }
    }
}

# ========== MEDIUM字段（5个）==========
# 触发条件：增量处理（Incremental模式）
# 典型场景：金额调整、日期调整

MEDIUM_FIELDS: Dict[str, Dict[str, Any]] = {
    "contract_signing_date": {
        "display_name": "合同签订日期",
        "reason": "影响诉讼时效起算点和合同履行期限",
        "impact_description": "影响Stage 2，涉及诉讼时效分析",
        "example": "2023-06-15",
        "validation": {
            "type": "date",
            "format": "YYYY-MM-DD",
            "required": False
        }
    },

    "payment_deadline": {
        "display_name": "付款期限",
        "reason": "影响利息起算日和违约责任认定",
        "impact_description": "影响Stage 2，涉及利息起算点",
        "example": "2023-12-31",
        "validation": {
            "type": "date",
            "format": "YYYY-MM-DD",
            "required": False
        }
    },

    "declared_principal": {
        "display_name": "申报本金",
        "reason": "影响就低原则适用，是确认金额的上限",
        "impact_description": "影响Stage 2，涉及本金确认",
        "example": "100万元",
        "validation": {
            "type": "amount",
            "required": True,
            "note": "确认金额不应超过申报金额（就低原则）"
        }
    },

    "declared_interest": {
        "display_name": "申报利息",
        "reason": "影响就低原则适用，是确认利息的上限",
        "impact_description": "影响Stage 2，涉及利息确认",
        "example": "5万元",
        "validation": {
            "type": "amount",
            "required": False,
            "note": "确认利息不应超过申报利息（就低原则）"
        }
    },

    "creditor_contact": {
        "display_name": "债权人联系方式",
        "reason": "影响报告抬头和送达信息，不影响法律认定",
        "impact_description": "影响Stage 3，仅涉及报告格式",
        "example": {
            "contact_person": "张三",
            "phone": "13812345678",
            "email": "zhangsan@example.com",
            "address": "上海市XX区XX路XX号"
        },
        "validation": {
            "type": "object",
            "required": False
        }
    }
}

# ========== LOW字段（3个）==========
# 触发条件：局部更新（Partial模式）
# 典型场景：格式调整、微小修改

LOW_FIELDS: Dict[str, Dict[str, Any]] = {
    "project_description": {
        "display_name": "项目描述",
        "reason": "仅影响报告背景描述，不影响法律认定",
        "impact_description": "影响Stage 3，仅涉及报告第1章",
        "example": "建材供应纠纷",
        "validation": {
            "type": "string",
            "required": False
        }
    },

    "notes": {
        "display_name": "备注信息",
        "reason": "不影响法律认定，仅作为附加说明",
        "impact_description": "影响Stage 3，仅涉及报告备注章节",
        "example": "需补充证据|已协商还款计划",
        "validation": {
            "type": "string",
            "required": False
        }
    },

    "processing_date": {
        "display_name": "处理日期",
        "reason": "自动生成字段，仅用于记录",
        "impact_description": "无影响",
        "example": "20251112",
        "validation": {
            "type": "date",
            "format": "YYYYMMDD",
            "auto_generated": True
        }
    }
}

# ========== 完整字段优先级字典 ==========
FIELD_PRIORITIES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "CRITICAL": CRITICAL_FIELDS,
    "HIGH": HIGH_FIELDS,
    "MEDIUM": MEDIUM_FIELDS,
    "LOW": LOW_FIELDS
}

# ========== 辅助函数 ==========

def get_field_priority(field_name: str) -> str:
    """获取字段的优先级

    Args:
        field_name: 字段名称

    Returns:
        str: 优先级（CRITICAL, HIGH, MEDIUM, LOW）或None（未知字段）
    """
    for priority, fields in FIELD_PRIORITIES.items():
        if field_name in fields:
            return priority
    return None


def get_field_spec(field_name: str) -> Dict[str, Any]:
    """获取字段的完整规格

    Args:
        field_name: 字段名称

    Returns:
        Dict: 字段规格字典，如果字段未知则返回None
    """
    for priority, fields in FIELD_PRIORITIES.items():
        if field_name in fields:
            spec = fields[field_name].copy()
            spec["priority"] = priority
            return spec
    return None


def get_highest_priority(field_names: list) -> str:
    """获取字段列表中的最高优先级

    Args:
        field_names: 字段名称列表

    Returns:
        str: 最高优先级（CRITICAL, HIGH, MEDIUM, LOW）或None（无已知字段）
    """
    priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    for priority in priorities:
        priority_fields = FIELD_PRIORITIES.get(priority, {})
        if any(field in priority_fields for field in field_names):
            return priority

    return None


def is_critical_field(field_name: str) -> bool:
    """判断字段是否为CRITICAL优先级

    Args:
        field_name: 字段名称

    Returns:
        bool: 是否为CRITICAL字段
    """
    return field_name in CRITICAL_FIELDS


def is_high_field(field_name: str) -> bool:
    """判断字段是否为HIGH优先级

    Args:
        field_name: 字段名称

    Returns:
        bool: 是否为HIGH字段
    """
    return field_name in HIGH_FIELDS


def get_all_field_names() -> list:
    """获取所有已定义的字段名称

    Returns:
        list: 所有字段名称列表
    """
    all_fields = []
    for priority, fields in FIELD_PRIORITIES.items():
        all_fields.extend(fields.keys())
    return all_fields


def validate_field_value(field_name: str, value: Any) -> tuple:
    """验证字段值是否符合规格

    Args:
        field_name: 字段名称
        value: 字段值

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    spec = get_field_spec(field_name)
    if not spec:
        return True, ""  # 未知字段跳过验证

    validation = spec.get("validation", {})

    # 必填字段检查
    if validation.get("required") and value is None:
        return False, f"{spec['display_name']} 是必填字段"

    # 枚举值检查
    if validation.get("type") == "enum" and value is not None:
        options = validation.get("options", [])
        if value not in options:
            return False, f"{spec['display_name']} 的值必须是以下之一: {', '.join(options)}"

    return True, ""


if __name__ == "__main__":
    # 测试代码
    print("===== 字段优先级分类系统测试 =====\n")

    # 测试1: 获取字段优先级
    test_fields = ["bankruptcy_date", "judgment_document", "declared_principal", "notes", "unknown_field"]
    print("测试1: 获取字段优先级")
    for field in test_fields:
        priority = get_field_priority(field)
        print(f"  {field}: {priority}")

    # 测试2: 获取最高优先级
    print("\n测试2: 获取最高优先级")
    test_groups = [
        ["judgment_document", "declared_principal"],
        ["bankruptcy_date", "notes"],
        ["notes", "processing_date"],
        ["unknown_field"]
    ]
    for group in test_groups:
        highest = get_highest_priority(group)
        print(f"  {group}: {highest}")

    # 测试3: 获取字段规格
    print("\n测试3: 获取字段规格")
    spec = get_field_spec("bankruptcy_date")
    if spec:
        print(f"  字段: bankruptcy_date")
        print(f"  显示名称: {spec['display_name']}")
        print(f"  优先级: {spec['priority']}")
        print(f"  原因: {spec['reason']}")

    # 测试4: 统计
    print("\n测试4: 字段统计")
    print(f"  CRITICAL字段: {len(CRITICAL_FIELDS)}个")
    print(f"  HIGH字段: {len(HIGH_FIELDS)}个")
    print(f"  MEDIUM字段: {len(MEDIUM_FIELDS)}个")
    print(f"  LOW字段: {len(LOW_FIELDS)}个")
    print(f"  总计: {len(get_all_field_names())}个")
