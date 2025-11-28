# -*- coding: utf-8 -*-
"""
Week 6验证测试 - 历史查看和回滚功能

验证内容：
1. 轮次状态管理（ACTIVE/COMPLETED/ROLLED_BACK）
2. 历史查看功能（get_history/print_history）
3. 回滚功能（rollback_to_round）
4. 回滚后数据保留（审计需求）
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.round_manager import RoundManager, RoundStatus
from src.multi_round_controller import MultiRoundController


class TestWeek6HistoryRollback(unittest.TestCase):
    """Week 6 历史查看和回滚验证测试"""

    def setUp(self):
        """测试前准备"""
        # 创建临时项目目录
        self.test_dir = tempfile.mkdtemp(prefix="debt_review_test_week6_")
        self.project_root = Path(self.test_dir)

        # 创建测试债权人目录
        self.creditor_path = self.project_root / "test_creditor"
        self.creditor_path.mkdir(parents=True)

        self.manager = RoundManager(self.creditor_path)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_01_round_status_enum(self):
        """测试1: 轮次状态枚举"""
        print("\n" + "=" * 60)
        print("测试1: 轮次状态枚举")
        print("=" * 60)

        # 验证所有状态值
        print("\n所有轮次状态:")
        for status in RoundStatus:
            print(f"  {status.name}: {status.value}")

        self.assertEqual(RoundStatus.INITIALIZED.value, "initialized")
        self.assertEqual(RoundStatus.PROCESSING.value, "processing")
        self.assertEqual(RoundStatus.COMPLETED.value, "completed")
        self.assertEqual(RoundStatus.FAILED.value, "failed")
        self.assertEqual(RoundStatus.ROLLED_BACK.value, "rolled_back")

        # 验证状态检查
        self.assertTrue(RoundStatus.is_valid_status("completed"))
        self.assertTrue(RoundStatus.is_valid_status("rolled_back"))
        self.assertFalse(RoundStatus.is_valid_status("invalid_status"))

        print("  ✅ 轮次状态枚举定义正确")

    def test_02_multi_round_history(self):
        """测试2: 多轮次历史记录"""
        print("\n" + "=" * 60)
        print("测试2: 多轮次历史记录")
        print("=" * 60)

        # 创建3个轮次
        self.manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                      trigger_reason="补充证据")
        self.manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document", "performance_evidence"],
            "processing_summary": {
                "time_savings_percent": 60,
                "stages_executed": [1, 2, 3]
            }
        })
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(3, parent_round=2, processing_mode="partial",
                                      trigger_reason="调整备注")
        self.manager.update_round_metadata(3, {
            "fields_updated": ["notes"],
            "processing_summary": {
                "time_savings_percent": 85,
                "stages_executed": [3]
            }
        })
        self.manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 获取历史
        history = self.manager.get_history(include_rolled_back=True)

        print(f"\n历史摘要:")
        print(f"  当前轮次: Round {history['current_round']}")
        print(f"  总轮次数: {history['total_rounds']}")
        print(f"  历史轮次数: {len(history['rounds'])}")

        self.assertEqual(history['current_round'], 3)
        self.assertEqual(history['total_rounds'], 3)
        self.assertEqual(len(history['rounds']), 3)

        # 验证每轮的详细信息
        round1 = history['rounds'][0]
        self.assertEqual(round1['round_number'], 1)
        self.assertEqual(round1['status'], RoundStatus.COMPLETED.value)
        self.assertEqual(round1['processing_mode'], "full")
        self.assertFalse(round1['is_current'])

        round2 = history['rounds'][1]
        self.assertEqual(round2['round_number'], 2)
        self.assertEqual(round2['fields_updated'], ["judgment_document", "performance_evidence"])
        self.assertEqual(round2['time_saved_percent'], 60)

        round3 = history['rounds'][2]
        self.assertEqual(round3['round_number'], 3)
        self.assertTrue(round3['is_current'])
        self.assertEqual(round3['time_saved_percent'], 85)

        print("  ✅ 多轮次历史记录正确")

    def test_03_rollback_preserves_data(self):
        """测试3: 回滚保留数据（不删除文件）"""
        print("\n" + "=" * 60)
        print("测试3: 回滚保留数据（不删除文件）")
        print("=" * 60)

        # 创建3个轮次
        self.manager.initialize_round(1, processing_mode="full")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental")
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(3, parent_round=2, processing_mode="partial")
        self.manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 回滚到Round 1
        success, message = self.manager.rollback_to_round(1, reason="发现Round 2有错误")

        print(f"\n回滚结果: {message}")
        self.assertTrue(success)
        self.assertEqual(self.manager.get_current_round(), 1)

        # 验证：Round 2和3的目录仍然存在（数据保留）
        self.assertTrue(self.manager.round_exists(1))
        self.assertTrue(self.manager.round_exists(2), "Round 2目录应该保留（审计需求）")
        self.assertTrue(self.manager.round_exists(3), "Round 3目录应该保留（审计需求）")

        # 验证：Round 2和3的状态被标记为ROLLED_BACK
        round2_metadata = self.manager.get_round_metadata(2)
        self.assertEqual(round2_metadata['status'], RoundStatus.ROLLED_BACK.value)
        self.assertIn('rolled_back_at', round2_metadata)
        self.assertEqual(round2_metadata['rolled_back_reason'], "发现Round 2有错误")

        round3_metadata = self.manager.get_round_metadata(3)
        self.assertEqual(round3_metadata['status'], RoundStatus.ROLLED_BACK.value)

        print("  ✅ 回滚正确保留数据（文件未删除，仅标记状态）")

    def test_04_rollback_validation(self):
        """测试4: 回滚验证逻辑"""
        print("\n" + "=" * 60)
        print("测试4: 回滚验证逻辑")
        print("=" * 60)

        # 创建2个轮次
        self.manager.initialize_round(1, processing_mode="full")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental")
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        # 测试1: 无法回滚到当前轮次或更高
        success, message = self.manager.rollback_to_round(2)
        print(f"\n测试1 - 回滚到当前轮次: {message}")
        self.assertFalse(success)

        # 测试2: 无法回滚到已作废的轮次
        success, message = self.manager.rollback_to_round(1)
        self.assertTrue(success)  # 第一次回滚成功

        # Round 2现在已作废
        success, message = self.manager.rollback_to_round(2)
        print(f"\n测试2 - 回滚到已作废轮次: {message}")
        self.assertFalse(success)

        print("  ✅ 回滚验证逻辑正确")

    def test_05_history_with_rolled_back(self):
        """测试5: 历史查看包含/排除已回滚轮次"""
        print("\n" + "=" * 60)
        print("测试5: 历史查看包含/排除已回滚轮次")
        print("=" * 60)

        # 创建3个轮次并回滚
        self.manager.initialize_round(1, processing_mode="full")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental")
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(3, parent_round=2, processing_mode="partial")
        self.manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 回滚到Round 1
        self.manager.rollback_to_round(1, reason="测试")

        # 测试：包含已回滚轮次
        history_with = self.manager.get_history(include_rolled_back=True)
        print(f"\n包含已回滚轮次: {len(history_with['rounds'])}个轮次")
        self.assertEqual(len(history_with['rounds']), 3)

        # 测试：排除已回滚轮次
        history_without = self.manager.get_history(include_rolled_back=False)
        print(f"排除已回滚轮次: {len(history_without['rounds'])}个轮次")
        self.assertEqual(len(history_without['rounds']), 1)  # 只有Round 1

        # 验证：排除模式下只有Round 1
        self.assertEqual(history_without['rounds'][0]['round_number'], 1)
        self.assertEqual(history_without['rounds'][0]['status'], RoundStatus.COMPLETED.value)

        print("  ✅ 历史查看过滤功能正确")

    def test_06_print_history_format(self):
        """测试6: 格式化历史打印"""
        print("\n" + "=" * 60)
        print("测试6: 格式化历史打印")
        print("=" * 60)

        # 创建2个轮次并回滚
        self.manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                      trigger_reason="补充证据")
        self.manager.update_round_metadata(2, {"fields_updated": ["judgment_document"]})
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        self.manager.rollback_to_round(1, reason="发现数据错误")

        print("\n格式化历史打印测试:")
        self.manager.print_history(include_rolled_back=True)

        print("\n  ✅ 格式化历史打印功能正常")


def run_week6_tests():
    """运行Week 6验证测试"""
    print("\n" + "=" * 60)
    print("Week 6 验证测试 - 历史查看 & 回滚功能")
    print("=" * 60)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeek6HistoryRollback)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 60)
    print("Week 6 验证测试总结")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ Week 6 所有验证测试通过！")
        print("\n核心功能验证:")
        print("  ✅ 轮次状态管理（ROLLED_BACK状态）")
        print("  ✅ 多轮次历史记录")
        print("  ✅ 回滚保留数据（审计需求）")
        print("  ✅ 回滚验证逻辑")
        print("  ✅ 历史查看过滤功能")
        print("  ✅ 格式化历史打印")
        return 0
    else:
        print("\n❌ 部分验证测试失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_week6_tests())
