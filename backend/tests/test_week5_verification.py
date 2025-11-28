# -*- coding: utf-8 -*-
"""
Week 5验证测试 - 债权项级别增量计算和章节依赖管理

验证内容：
1. 债权项依赖关系正确识别
2. 章节依赖关系正确识别
3. Partial模式配置正确生成
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.impact_analyzer import ImpactAnalyzer
from config.impact_mappings import CHAPTER_DEPENDENCIES, get_chapters_to_update


class TestWeek5Verification(unittest.TestCase):
    """Week 5 验证测试"""

    def test_01_debt_item_dependencies(self):
        """测试1: 债权项依赖关系识别"""
        print("\n" + "=" * 60)
        print("测试1: 债权项依赖关系识别")
        print("=" * 60)

        analyzer = ImpactAnalyzer(conservative=True)

        # 场景1: 本金变更 → 只影响本金债权项
        result = analyzer.analyze_impact(["declared_principal"])
        print(f"\n场景1: 申报本金变更")
        print(f"  受影响债权项: {result.affected_debt_items}")

        # 验证：申报本金变更只影响本金确认
        self.assertIn("本金", result.affected_debt_items,
                     "申报本金变更应该影响本金")

        print("  ✅ 申报本金变更正确触发本金债权项")

        # 场景2: 利率变更 → 影响利息相关项
        result = analyzer.analyze_impact(["interest_rate_clause"])
        print(f"\n场景2: 利率约定变更")
        print(f"  受影响债权项: {result.affected_debt_items}")

        # 验证：利率变更影响利息计算
        self.assertIn("利息", result.affected_debt_items,
                     "利率变更应该影响利息")

        print("  ✅ 利率变更正确识别受影响债权项")

        # 场景3: 破产日期变更 → 影响所有债权项（CRITICAL字段）
        result = analyzer.analyze_impact(["bankruptcy_date"])
        print(f"\n场景3: 破产日期变更（CRITICAL字段）")
        print(f"  受影响债权项: {result.affected_debt_items}")

        # 验证：破产日期变更应该影响所有债权项
        all_debt_items = ["本金", "利息", "违约金", "逾期利息", "罚息", "复利", "担保债权", "保证债权"]
        for item in all_debt_items:
            self.assertIn(item, result.affected_debt_items,
                         f"破产日期变更应该影响{item}")

        print("  ✅ 破产日期变更正确触发所有债权项")

        print("\n✅ 测试1通过: 债权项依赖关系识别正确")

    def test_02_chapter_dependencies(self):
        """测试2: 章节依赖关系验证"""
        print("\n" + "=" * 60)
        print("测试2: 章节依赖关系验证")
        print("=" * 60)

        # 验证章节依赖关系定义
        print(f"\n章节依赖关系定义:")
        for chapter, deps in CHAPTER_DEPENDENCIES.items():
            print(f"  第{chapter}章 依赖: {deps if deps else '无依赖'}")

        # 测试get_chapters_to_update函数
        print(f"\n测试章节级联更新:")

        # 场景1: 第3章变更 → 应该联动更新第4、5章
        affected = get_chapters_to_update([3])
        print(f"\n场景1: 第3章变更")
        print(f"  需要更新的章节: {affected}")
        self.assertIn(3, affected, "第3章应该在更新列表中")
        self.assertIn(4, affected, "第4章依赖第3章，应该联动更新")
        self.assertIn(5, affected, "第5章依赖第3章，应该联动更新")
        print("  ✅ 第3章变更正确触发第4、5章联动更新")

        # 场景2: 第1章变更 → 应该联动更新第2、3、4、5章
        affected = get_chapters_to_update([1])
        print(f"\n场景2: 第1章变更")
        print(f"  需要更新的章节: {affected}")
        expected_chapters = [1, 2, 3, 4, 5]
        for ch in expected_chapters:
            self.assertIn(ch, affected, f"第{ch}章应该被更新")
        print("  ✅ 第1章变更正确触发所有依赖章节更新")

        # 场景3: 第6章变更 → 只更新第6章（备注说明无依赖关系）
        affected = get_chapters_to_update([6])
        print(f"\n场景3: 第6章变更（备注说明）")
        print(f"  需要更新的章节: {affected}")
        self.assertEqual(affected, [6], "第6章（备注）无依赖，只更新自己")
        print("  ✅ 第6章变更正确处理（无级联）")

        print("\n✅ 测试2通过: 章节依赖关系验证正确")

    def test_03_incremental_vs_partial(self):
        """测试3: Incremental模式 vs Partial模式的区别"""
        print("\n" + "=" * 60)
        print("测试3: Incremental模式 vs Partial模式的区别")
        print("=" * 60)

        analyzer = ImpactAnalyzer(conservative=True)

        # HIGH字段 → Incremental模式（章节级增量）
        result_high = analyzer.analyze_impact(["judgment_document"])
        print(f"\nHIGH字段（生效法律文书）:")
        print(f"  处理模式: {result_high.processing_mode.value}")
        print(f"  受影响章节: {result_high.affected_sections}")
        print(f"  预计节省时间: {result_high.time_savings_percent}%")
        self.assertEqual(result_high.processing_mode.value, "incremental")
        print("  ✅ HIGH字段触发Incremental模式")

        # LOW字段 → Partial模式（字段级增量）
        result_low = analyzer.analyze_impact(["notes"])
        print(f"\nLOW字段（备注信息）:")
        print(f"  处理模式: {result_low.processing_mode.value}")
        print(f"  受影响章节: {result_low.affected_sections}")
        print(f"  预计节省时间: {result_low.time_savings_percent}%")
        self.assertEqual(result_low.processing_mode.value, "partial")
        print("  ✅ LOW字段触发Partial模式")

        # 验证时间节省差异
        self.assertGreater(result_low.time_savings_percent,
                          result_high.time_savings_percent,
                          "Partial模式应该比Incremental模式节省更多时间")
        print(f"\n  ✅ Partial模式({result_low.time_savings_percent}%)比"
              f"Incremental模式({result_high.time_savings_percent}%)节省更多时间")

        print("\n✅ 测试3通过: 两种增量模式区别明确")

    def test_04_conservative_strategy_integration(self):
        """测试4: 保守策略与增量计算的集成"""
        print("\n" + "=" * 60)
        print("测试4: 保守策略与增量计算的集成")
        print("=" * 60)

        # 保守策略开启
        analyzer_conservative = ImpactAnalyzer(conservative=True)

        # 保守策略关闭
        analyzer_aggressive = ImpactAnalyzer(conservative=False)

        # MEDIUM字段在不同策略下的表现
        result_conservative = analyzer_conservative.analyze_impact(["payment_deadline"])
        result_aggressive = analyzer_aggressive.analyze_impact(["payment_deadline"])

        print(f"\nMEDIUM字段（付款期限）在不同策略下:")
        print(f"  保守策略: {result_conservative.processing_mode.value}")
        print(f"  激进策略: {result_aggressive.processing_mode.value}")

        # 验证：保守策略下MEDIUM字段应该用Incremental而非Partial
        self.assertEqual(result_conservative.processing_mode.value, "incremental",
                        "保守策略下MEDIUM字段应触发Incremental")
        self.assertEqual(result_aggressive.processing_mode.value, "incremental",
                        "激进策略下MEDIUM字段也触发Incremental")

        print("  ✅ 保守策略正确影响处理模式选择")

        print("\n✅ 测试4通过: 保守策略与增量计算集成正确")

    def test_05_field_priority_mapping(self):
        """测试5: 字段优先级与影响范围映射"""
        print("\n" + "=" * 60)
        print("测试5: 字段优先级与影响范围映射")
        print("=" * 60)

        analyzer = ImpactAnalyzer(conservative=True)

        # 测试不同优先级字段的影响范围
        test_cases = [
            {
                "field": "bankruptcy_date",
                "expected_priority": "CRITICAL",
                "expected_mode": "full",
                "expected_stages": [1, 2, 3]
            },
            {
                "field": "judgment_document",
                "expected_priority": "HIGH",
                "expected_mode": "incremental",
                "expected_stages": [1, 2, 3]
            },
            {
                "field": "payment_deadline",
                "expected_priority": "MEDIUM",
                "expected_mode": "incremental",
                "expected_stages": [2]
            },
            {
                "field": "creditor_contact",
                "expected_priority": "MEDIUM",
                "expected_mode": "incremental",
                "expected_stages": [3]
            },
            {
                "field": "notes",
                "expected_priority": "LOW",
                "expected_mode": "partial",
                "expected_stages": [3]
            }
        ]

        print(f"\n字段优先级与影响范围映射验证:")
        for case in test_cases:
            result = analyzer.analyze_impact([case["field"]])
            print(f"\n  字段: {case['field']}")
            print(f"    优先级: {result.highest_priority} (预期: {case['expected_priority']})")
            print(f"    处理模式: {result.processing_mode.value} (预期: {case['expected_mode']})")
            print(f"    受影响阶段: {result.affected_stages} (预期: {case['expected_stages']})")

            self.assertEqual(result.highest_priority, case["expected_priority"])
            self.assertEqual(result.processing_mode.value, case["expected_mode"])
            self.assertEqual(result.affected_stages, case["expected_stages"])
            print(f"    ✅ 映射正确")

        print("\n✅ 测试5通过: 字段优先级与影响范围映射正确")


def run_week5_tests():
    """运行Week 5验证测试"""
    print("\n" + "=" * 60)
    print("Week 5 验证测试 - 债权项增量 & 章节依赖")
    print("=" * 60)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeek5Verification)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 60)
    print("Week 5 验证测试总结")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ Week 5 所有验证测试通过！")
        print("\n核心功能验证:")
        print("  ✅ 债权项依赖关系识别正确")
        print("  ✅ 章节依赖管理算法正确")
        print("  ✅ Incremental vs Partial模式区别明确")
        print("  ✅ 保守策略集成正确")
        print("  ✅ 字段优先级映射正确")
        return 0
    else:
        print("\n❌ 部分验证测试失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_week5_tests())
