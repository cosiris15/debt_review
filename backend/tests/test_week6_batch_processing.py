# -*- coding: utf-8 -*-
"""
Week 6验证测试 - 批量处理优化

验证内容：
1. 批量状态查询
2. 批量初始化轮次
3. 批量影响分析
4. 债权人过滤功能
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.multi_round_controller import MultiRoundController
from src.round_manager import RoundManager


class TestWeek6BatchProcessing(unittest.TestCase):
    """Week 6 批量处理优化验证测试"""

    def setUp(self):
        """测试前准备"""
        # 创建临时项目目录
        self.test_dir = tempfile.mkdtemp(prefix="debt_review_test_batch_")
        self.project_root = Path(self.test_dir)

        # 创建测试批次目录
        self.batch_dir = self.project_root / "输出" / "第1批债权"
        self.batch_dir.mkdir(parents=True)

        # 创建3个测试债权人目录
        self.creditors = [
            (100, "债权人A"),
            (101, "债权人B"),
            (102, "债权人C")
        ]

        for number, name in self.creditors:
            creditor_dir = self.batch_dir / f"{number:03d}-{name}"
            creditor_dir.mkdir()

            # 初始化Round 1
            manager = RoundManager(creditor_dir)
            manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
            manager.mark_round_status(1, "completed")

        self.controller = MultiRoundController(str(self.project_root))

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_01_list_creditors(self):
        """测试1: 列出批次中的债权人"""
        print("\n" + "=" * 60)
        print("测试1: 列出批次中的债权人")
        print("=" * 60)

        creditors = self.controller.list_creditors_in_batch(1)

        print(f"\n第1批债权人列表:")
        for number, name in creditors:
            print(f"  {number:03d}-{name}")

        self.assertEqual(len(creditors), 3)
        self.assertEqual(creditors[0], (100, "债权人A"))
        self.assertEqual(creditors[1], (101, "债权人B"))
        self.assertEqual(creditors[2], (102, "债权人C"))

        print("  ✅ 债权人列表获取正确")

    def test_02_batch_status(self):
        """测试2: 批量状态查询"""
        print("\n" + "=" * 60)
        print("测试2: 批量状态查询")
        print("=" * 60)

        result = self.controller.batch_status(1)

        self.assertTrue(result["success"])
        self.assertEqual(result["batch_number"], 1)
        self.assertEqual(result["creditor_count"], 3)

        # 验证每个债权人的状态
        creditor_statuses = result["creditors"]
        self.assertEqual(len(creditor_statuses), 3)

        for status in creditor_statuses:
            self.assertEqual(status["current_round"], 1)
            self.assertEqual(status["total_rounds"], 1)
            self.assertEqual(len(status["rounds"]), 1)
            self.assertEqual(status["rounds"][0]["status"], "completed")

        print("  ✅ 批量状态查询正确")

    def test_03_batch_init_round(self):
        """测试3: 批量初始化轮次"""
        print("\n" + "=" * 60)
        print("测试3: 批量初始化轮次")
        print("=" * 60)

        # 批量初始化Round 2（所有债权人）
        result = self.controller.batch_init_round(
            batch_number=1,
            round_number=2,
            creditor_filter=None
        )

        print(f"\n批量初始化结果:")
        print(f"  成功数: {result['success_count']}")
        print(f"  失败数: {result['failed_count']}")

        self.assertTrue(result["success"])
        self.assertEqual(result["success_count"], 3)
        self.assertEqual(result["failed_count"], 0)

        # 验证每个债权人的Round 2都被创建
        for number, name in self.creditors:
            creditor_dir = self.batch_dir / f"{number:03d}-{name}"
            manager = RoundManager(creditor_dir)
            self.assertTrue(manager.round_exists(2))
            self.assertEqual(manager.get_current_round(), 2)

        print("  ✅ 批量初始化成功")

    def test_04_batch_init_with_filter(self):
        """测试4: 批量初始化（带过滤）"""
        print("\n" + "=" * 60)
        print("测试4: 批量初始化（带过滤）")
        print("=" * 60)

        # 只初始化100和102两个债权人的Round 3
        result = self.controller.batch_init_round(
            batch_number=1,
            round_number=3,
            creditor_filter=[100, 102]  # 跳过101
        )

        print(f"\n批量初始化结果（过滤模式）:")
        print(f"  处理数: {result['total']}")
        print(f"  成功数: {result['success_count']}")

        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 2)  # 只处理2个
        self.assertEqual(result["success_count"], 2)

        # 验证：100和102有Round 3，101没有
        manager_100 = RoundManager(self.batch_dir / "100-债权人A")
        self.assertTrue(manager_100.round_exists(3))

        manager_101 = RoundManager(self.batch_dir / "101-债权人B")
        self.assertFalse(manager_101.round_exists(3))

        manager_102 = RoundManager(self.batch_dir / "102-债权人C")
        self.assertTrue(manager_102.round_exists(3))

        print("  ✅ 过滤功能正确")

    def test_05_batch_analyze_impact(self):
        """测试5: 批量影响分析"""
        print("\n" + "=" * 60)
        print("测试5: 批量影响分析")
        print("=" * 60)

        # 准备补充材料目录
        supplemental_dir = self.project_root / "补充材料"
        supplemental_dir.mkdir()

        # 为100和102创建补充材料文件
        for number in [100, 102]:
            name = "债权人A" if number == 100 else "债权人C"
            material_file = supplemental_dir / f"{number:03d}-{name}_supplemental.json"

            material_data = {
                "judgment_document": "新的判决文书"  # HIGH字段
            }
            with open(material_file, 'w', encoding='utf-8') as f:
                json.dump(material_data, f, ensure_ascii=False, indent=2)

        # 批量分析（没有过滤，101会被跳过因为没有材料文件）
        result = self.controller.batch_analyze_impact(
            batch_number=1,
            supplemental_dir=str(supplemental_dir),
            creditor_filter=None
        )

        print(f"\n批量影响分析结果:")
        print(f"  成功数: {result['success_count']}")

        # 应该成功分析2个（100和102有材料文件）
        self.assertEqual(result["success_count"], 2)

        # 验证分析结果被保存
        for result_item in result["results"]:
            if result_item["success"]:
                impact = result_item["impact_analysis"]
                self.assertIn("processing_mode", impact)
                self.assertIn("time_savings_percent", impact)

        print("  ✅ 批量影响分析成功")

    def test_06_batch_empty_batch(self):
        """测试6: 空批次处理"""
        print("\n" + "=" * 60)
        print("测试6: 空批次处理")
        print("=" * 60)

        # 查询不存在的批次
        result = self.controller.batch_status(999)

        print(f"\n空批次查询结果:")
        print(f"  成功: {result['success']}")
        print(f"  消息: {result['message']}")

        self.assertFalse(result["success"])
        self.assertEqual(result["creditor_count"], 0)

        print("  ✅ 空批次处理正确")


def run_week6_batch_tests():
    """运行Week 6批量处理验证测试"""
    print("\n" + "=" * 60)
    print("Week 6 验证测试 - 批量处理优化")
    print("=" * 60)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeek6BatchProcessing)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 60)
    print("Week 6 批量处理验证测试总结")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ Week 6 批量处理所有验证测试通过！")
        print("\n核心功能验证:")
        print("  ✅ 批量债权人列表")
        print("  ✅ 批量状态查询")
        print("  ✅ 批量初始化轮次")
        print("  ✅ 债权人过滤功能")
        print("  ✅ 批量影响分析")
        print("  ✅ 空批次处理")
        return 0
    else:
        print("\n❌ 部分验证测试失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_week6_batch_tests())
