# -*- coding: utf-8 -*-
"""
Week 7验证测试 - Changelog自动生成 & 补充清单生成

验证内容：
Part A: Changelog功能
1. Changelog文件自动生成
2. 初始化轮次时自动记录
3. 状态变更时自动记录
4. 回滚操作时自动记录
5. Changelog内容完整性
6. Changelog摘要生成

Part B: 补充清单功能
7. 补充清单文件生成
8. 字段优先级分类
9. Markdown格式输出
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


class TestWeek7Changelog(unittest.TestCase):
    """Week 7 Changelog功能验证测试"""

    def setUp(self):
        """测试前准备"""
        # 创建临时债权人目录
        self.test_dir = tempfile.mkdtemp(prefix="debt_review_test_changelog_")
        self.creditor_path = Path(self.test_dir) / "test_creditor"
        self.creditor_path.mkdir(parents=True)

        self.manager = RoundManager(self.creditor_path)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_01_changelog_file_creation(self):
        """测试1: Changelog文件自动创建"""
        print("\n" + "=" * 60)
        print("测试1: Changelog文件自动创建")
        print("=" * 60)

        # 初始化Round 1
        self.manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")

        # 验证：.changelog.json文件被创建
        changelog_file = self.creditor_path / ".changelog.json"
        self.assertTrue(changelog_file.exists(), "Changelog文件应该被自动创建")

        # 读取并验证内容
        with open(changelog_file, 'r', encoding='utf-8') as f:
            changelog = json.load(f)

        self.assertIn("creditor_info", changelog)
        self.assertIn("changelog", changelog)
        self.assertEqual(len(changelog["changelog"]), 1)

        print(f"  ✅ Changelog文件已创建: {changelog_file}")
        print(f"  ✅ 记录数: {len(changelog['changelog'])}")

    def test_02_initialize_round_records(self):
        """测试2: 初始化轮次时自动记录"""
        print("\n" + "=" * 60)
        print("测试2: 初始化轮次时自动记录")
        print("=" * 60)

        # 初始化Round 1
        self.manager.initialize_round(
            1,
            processing_mode="full",
            trigger_reason="首次处理"
        )

        # 读取changelog
        changelog = self.manager.read_changelog()

        # 验证：包含Round 1的记录
        self.assertEqual(len(changelog["changelog"]), 1)

        entry = changelog["changelog"][0]
        print(f"\nRound 1记录:")
        print(f"  轮次号: {entry['round_number']}")
        print(f"  动作: {entry['action']}")
        print(f"  处理模式: {entry['processing_mode']}")
        print(f"  状态: {entry['status']}")

        self.assertEqual(entry["round_number"], 1)
        self.assertEqual(entry["action"], "初始化")
        self.assertEqual(entry["processing_mode"], "full")
        self.assertEqual(entry["trigger_reason"], "首次处理")
        self.assertEqual(entry["status"], "initialized")

        print("  ✅ Round 1初始化记录正确")

    def test_03_status_change_records(self):
        """测试3: 状态变更时自动记录"""
        print("\n" + "=" * 60)
        print("测试3: 状态变更时自动记录")
        print("=" * 60)

        # 初始化Round 1
        self.manager.initialize_round(1, processing_mode="full")

        # 变更状态为processing
        self.manager.mark_round_status(1, RoundStatus.PROCESSING.value)

        # 变更状态为completed
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 读取changelog
        changelog = self.manager.read_changelog()

        print(f"\nChangelog记录数: {len(changelog['changelog'])}")

        # 验证：包含所有状态变更（初始化 + 2次状态变更，最后一次状态更新覆盖前面的）
        # 注意：由于update_changelog会更新已有记录，最终只有1条记录
        self.assertEqual(len(changelog["changelog"]), 1)

        entry = changelog["changelog"][0]
        print(f"\n最终状态记录:")
        print(f"  动作: {entry['action']}")
        print(f"  状态: {entry['status']}")

        self.assertEqual(entry["status"], "completed")

        print("  ✅ 状态变更记录正确")

    def test_04_multiple_rounds_changelog(self):
        """测试4: 多轮次changelog记录"""
        print("\n" + "=" * 60)
        print("测试4: 多轮次changelog记录")
        print("=" * 60)

        # 创建3个轮次
        self.manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(
            2,
            parent_round=1,
            processing_mode="incremental",
            trigger_reason="补充证据"
        )
        self.manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document"],
            "impact_analysis": {
                "affected_stages": [1, 2, 3],
                "affected_sections": [1, 2, 3],
                "time_savings_percent": 60
            }
        })
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(
            3,
            parent_round=2,
            processing_mode="partial",
            trigger_reason="调整备注"
        )
        self.manager.update_round_metadata(3, {
            "fields_updated": ["notes"],
            "impact_analysis": {
                "affected_stages": [3],
                "affected_sections": [6],
                "time_savings_percent": 85
            }
        })
        self.manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 读取changelog
        changelog = self.manager.read_changelog()

        print(f"\nChangelog记录数: {len(changelog['changelog'])}")

        # 验证：包含3个轮次的记录
        self.assertEqual(len(changelog["changelog"]), 3)

        # 验证Round 2的记录
        round2_entry = [e for e in changelog["changelog"] if e["round_number"] == 2][0]
        print(f"\nRound 2记录:")
        print(f"  处理模式: {round2_entry['processing_mode']}")
        print(f"  变更字段: {round2_entry['fields_updated']}")
        print(f"  节省时间: {round2_entry.get('impact_analysis', {}).get('time_savings_percent', 0)}%")

        self.assertEqual(round2_entry["processing_mode"], "incremental")
        self.assertEqual(round2_entry["fields_updated"], ["judgment_document"])
        self.assertEqual(round2_entry["impact_analysis"]["time_savings_percent"], 60)

        # 验证Round 3的记录
        round3_entry = [e for e in changelog["changelog"] if e["round_number"] == 3][0]
        self.assertEqual(round3_entry["processing_mode"], "partial")
        self.assertEqual(round3_entry["impact_analysis"]["time_savings_percent"], 85)

        print("  ✅ 多轮次记录正确")

    def test_05_rollback_records(self):
        """测试5: 回滚操作时自动记录"""
        print("\n" + "=" * 60)
        print("测试5: 回滚操作时自动记录")
        print("=" * 60)

        # 创建3个轮次
        self.manager.initialize_round(1, processing_mode="full")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental")
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(3, parent_round=2, processing_mode="partial")
        self.manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 回滚到Round 1
        success, message = self.manager.rollback_to_round(1, reason="发现数据错误")
        self.assertTrue(success)

        # 读取changelog
        changelog = self.manager.read_changelog()

        print(f"\nChangelog记录数: {len(changelog['changelog'])}")

        # 验证：Round 2和3的状态被更新为回滚
        round2_entry = [e for e in changelog["changelog"] if e["round_number"] == 2][0]
        round3_entry = [e for e in changelog["changelog"] if e["round_number"] == 3][0]

        print(f"\nRound 2状态:")
        print(f"  动作: {round2_entry['action']}")
        print(f"  状态: {round2_entry['status']}")

        print(f"\nRound 3状态:")
        print(f"  动作: {round3_entry['action']}")
        print(f"  状态: {round3_entry['status']}")

        self.assertEqual(round2_entry["action"], "回滚（已作废）")
        self.assertEqual(round2_entry["status"], "rolled_back")
        self.assertEqual(round3_entry["action"], "回滚（已作废）")
        self.assertEqual(round3_entry["status"], "rolled_back")

        print("  ✅ 回滚操作记录正确")

    def test_06_changelog_summary(self):
        """测试6: Changelog摘要生成"""
        print("\n" + "=" * 60)
        print("测试6: Changelog摘要生成")
        print("=" * 60)

        # 创建2个轮次
        self.manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        self.manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                      trigger_reason="补充证据")
        self.manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document"],
            "impact_analysis": {
                "time_savings_percent": 60
            }
        })
        self.manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        # 生成摘要
        summary = self.manager.generate_changelog_summary()

        print(f"\nChangelog摘要:")
        print(summary)

        # 验证：摘要包含关键信息
        self.assertIn("Round 1", summary)
        self.assertIn("Round 2", summary)
        self.assertIn("首次处理", summary)
        self.assertIn("补充证据", summary)
        self.assertIn("60%", summary)

        print("\n  ✅ Changelog摘要生成正确")

    def test_07_supplemental_checklist_generation(self):
        """测试7: 补充清单文件生成"""
        print("\n" + "=" * 60)
        print("测试7: 补充清单文件生成")
        print("=" * 60)

        # 创建带有字段更新信息的轮次
        self.manager.initialize_round(
            1,
            processing_mode="incremental",
            trigger_reason="补充判决文书"
        )
        self.manager.update_round_metadata(1, {
            "fields_updated": ["judgment_document", "performance_evidence"],
            "impact_analysis": {
                "affected_stages": [1, 2, 3],
                "time_savings_percent": 60
            }
        })
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 生成补充清单
        result = self.manager.generate_supplemental_checklist(1)

        print(f"\n生成结果:")
        print(f"  成功: {result['success']}")
        print(f"  文件: {result.get('checklist_file', 'N/A')}")
        print(f"  字段数量: {result.get('fields_count', 0)}")

        self.assertTrue(result["success"])
        self.assertIn("checklist_file", result)
        self.assertEqual(result["fields_count"], 2)

        # 验证文件存在
        from pathlib import Path
        checklist_file = Path(result["checklist_file"])
        self.assertTrue(checklist_file.exists(), "补充清单文件应该被创建")

        print("  ✅ 补充清单文件成功生成")

    def test_08_checklist_priority_categorization(self):
        """测试8: 字段优先级分类"""
        print("\n" + "=" * 60)
        print("测试8: 字段优先级分类")
        print("=" * 60)

        # 创建包含不同优先级字段的轮次
        self.manager.initialize_round(1, processing_mode="incremental")
        self.manager.update_round_metadata(1, {
            "fields_updated": [
                "bankruptcy_date",  # CRITICAL
                "judgment_document",  # HIGH
                "payment_deadline",  # MEDIUM
                "notes"  # LOW
            ]
        })
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 生成补充清单
        result = self.manager.generate_supplemental_checklist(1)

        self.assertTrue(result["success"])

        # 验证优先级分布
        categorized = result["categorized_fields"]
        print(f"\n优先级分布:")
        for priority, count in categorized.items():
            print(f"  {priority}: {count}个")

        self.assertIn("CRITICAL", categorized)
        self.assertIn("HIGH", categorized)
        self.assertIn("MEDIUM", categorized)
        self.assertIn("LOW", categorized)

        self.assertEqual(categorized["CRITICAL"], 1)
        self.assertEqual(categorized["HIGH"], 1)
        self.assertEqual(categorized["MEDIUM"], 1)
        self.assertEqual(categorized["LOW"], 1)

        print("  ✅ 字段优先级分类正确")

    def test_09_checklist_markdown_format(self):
        """测试9: Markdown格式输出"""
        print("\n" + "=" * 60)
        print("测试9: Markdown格式输出")
        print("=" * 60)

        # 创建轮次并生成清单
        self.manager.initialize_round(1, processing_mode="incremental", trigger_reason="补充材料")
        self.manager.update_round_metadata(1, {
            "fields_updated": ["judgment_document", "notes"]
        })
        self.manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        result = self.manager.generate_supplemental_checklist(1)
        self.assertTrue(result["success"])

        # 验证Markdown内容
        content = result["content"]

        print(f"\nMarkdown内容验证:")

        # 检查标题
        self.assertIn("# 补充材料清单", content)
        print("  ✓ 包含主标题")

        # 检查元数据
        self.assertIn("**生成时间**:", content)
        self.assertIn("**触发原因**: 补充材料", content)
        self.assertIn("**处理模式**: incremental", content)
        print("  ✓ 包含元数据")

        # 检查优先级章节
        self.assertIn("🟠 高优先级字段", content)
        self.assertIn("🟢 低优先级字段", content)
        print("  ✓ 包含优先级章节")

        # 检查字段信息
        self.assertIn("judgment_document", content)
        self.assertIn("notes", content)
        print("  ✓ 包含字段信息")

        # 检查处理建议
        self.assertIn("## 处理建议", content)
        self.assertIn("### 下一步操作", content)
        print("  ✓ 包含处理建议")

        # 读取文件验证
        from pathlib import Path
        checklist_file = Path(result["checklist_file"])
        with open(checklist_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            self.assertEqual(content, file_content, "文件内容应与返回内容一致")

        print("  ✅ Markdown格式正确")


def run_week7_changelog_tests():
    """运行Week 7验证测试"""
    print("\n" + "=" * 60)
    print("Week 7 验证测试 - Changelog & 补充清单")
    print("=" * 60)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeek7Changelog)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 60)
    print("Week 7 验证测试总结")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ Week 7 所有验证测试通过！")
        print("\n核心功能验证:")
        print("\nPart A: Changelog功能")
        print("  ✅ Changelog文件自动创建")
        print("  ✅ 初始化轮次时自动记录")
        print("  ✅ 状态变更时自动记录")
        print("  ✅ 多轮次changelog记录")
        print("  ✅ 回滚操作时自动记录")
        print("  ✅ Changelog摘要生成")
        print("\nPart B: 补充清单功能")
        print("  ✅ 补充清单文件生成")
        print("  ✅ 字段优先级分类")
        print("  ✅ Markdown格式输出")
        return 0
    else:
        print("\n❌ 部分验证测试失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_week7_changelog_tests())
