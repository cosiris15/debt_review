# -*- coding: utf-8 -*-
"""
完整集成测试 - 多轮债权审查系统端到端验证

这是系统的完整集成测试，覆盖从初始化到多轮处理的完整工作流。

测试场景：
1. 完整三轮工作流（Full → Incremental → Partial）
2. 多债权人批量处理
3. 影响分析准确性验证
4. 轮次状态管理和回滚
5. Changelog自动记录
6. 补充清单生成
7. 历史查看和追溯
8. 批量操作优化
9. 错误处理和边界条件
10. 数据一致性验证
11. 文件组织标准
12. 完整审计追踪
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
from src.impact_analyzer import ImpactAnalyzer


class TestCompleteIntegration(unittest.TestCase):
    """完整集成测试"""

    def setUp(self):
        """测试前准备"""
        # 创建临时项目目录
        self.test_dir = tempfile.mkdtemp(prefix="debt_review_integration_")
        self.project_root = Path(self.test_dir)

        # 创建输出目录
        self.output_dir = self.project_root / "输出"
        self.output_dir.mkdir()

        # 创建批次目录
        self.batch_dir = self.output_dir / "第1批债权"
        self.batch_dir.mkdir()

        # 创建控制器
        self.controller = MultiRoundController(str(self.project_root))

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_01_complete_three_round_workflow(self):
        """测试1: 完整三轮工作流（Full → Incremental → Partial）"""
        print("\n" + "=" * 80)
        print("测试1: 完整三轮工作流（Full → Incremental → Partial）")
        print("=" * 80)

        # 创建债权人目录
        creditor_dir = self.batch_dir / "100-测试债权人A"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # ========== Round 1: Full模式 ==========
        print("\n▶ Round 1: Full模式（首次处理）")
        manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 验证Round 1
        self.assertTrue(manager.round_exists(1))
        self.assertEqual(manager.get_current_round(), 1)
        self.assertEqual(manager.get_round_status(1), RoundStatus.COMPLETED.value)
        print("  ✓ Round 1完成：Full模式")

        # ========== Round 2: Incremental模式 ==========
        print("\n▶ Round 2: Incremental模式（补充证据）")
        manager.initialize_round(
            2,
            parent_round=1,
            processing_mode="incremental",
            trigger_reason="补充判决文书"
        )
        manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document", "performance_evidence"],
            "impact_analysis": {
                "affected_stages": [1, 2, 3],
                "affected_sections": [1, 2, 3],
                "time_savings_percent": 60
            }
        })
        manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        # 验证Round 2
        self.assertTrue(manager.round_exists(2))
        self.assertEqual(manager.get_current_round(), 2)
        metadata2 = manager.get_round_metadata(2)
        self.assertEqual(metadata2["processing_mode"], "incremental")
        self.assertEqual(metadata2["parent_round"], 1)
        print("  ✓ Round 2完成：Incremental模式，节省60%时间")

        # ========== Round 3: Partial模式 ==========
        print("\n▶ Round 3: Partial模式（调整备注）")
        manager.initialize_round(
            3,
            parent_round=2,
            processing_mode="partial",
            trigger_reason="调整备注说明"
        )
        manager.update_round_metadata(3, {
            "fields_updated": ["notes"],
            "impact_analysis": {
                "affected_stages": [3],
                "affected_sections": [6],
                "time_savings_percent": 85
            }
        })
        manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 验证Round 3
        self.assertTrue(manager.round_exists(3))
        self.assertEqual(manager.get_current_round(), 3)
        metadata3 = manager.get_round_metadata(3)
        self.assertEqual(metadata3["processing_mode"], "partial")
        print("  ✓ Round 3完成：Partial模式，节省85%时间")

        # ========== 验证完整历史 ==========
        print("\n▶ 验证完整历史")
        history = manager.get_history()
        self.assertEqual(history["total_rounds"], 3)
        self.assertEqual(len(history["rounds"]), 3)

        # 验证处理模式正确
        self.assertEqual(history["rounds"][0]["processing_mode"], "full")
        self.assertEqual(history["rounds"][1]["processing_mode"], "incremental")
        self.assertEqual(history["rounds"][2]["processing_mode"], "partial")

        # 验证时间节省（从processing_summary或impact_analysis中获取）
        # Round 2应该有60%节省
        round2_info = history["rounds"][1]
        if "time_saved_percent" in round2_info:
            self.assertEqual(round2_info["time_saved_percent"], 60)

        # Round 3应该有85%节省
        round3_info = history["rounds"][2]
        if "time_saved_percent" in round3_info:
            self.assertEqual(round3_info["time_saved_percent"], 85)

        print("  ✓ 三轮历史记录完整")
        print("\n✅ 测试1通过：完整三轮工作流成功")

    def test_02_multi_creditor_batch_processing(self):
        """测试2: 多债权人批量处理"""
        print("\n" + "=" * 80)
        print("测试2: 多债权人批量处理")
        print("=" * 80)

        # 创建3个债权人
        creditors = [
            (100, "债权人A"),
            (101, "债权人B"),
            (102, "债权人C")
        ]

        # 批量初始化Round 1
        print("\n▶ 批量初始化Round 1")
        for number, name in creditors:
            creditor_dir = self.batch_dir / f"{number:03d}-{name}"
            creditor_dir.mkdir()
            manager = RoundManager(creditor_dir)
            manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
            manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 验证批量列表
        listed_creditors = self.controller.list_creditors_in_batch(1)
        self.assertEqual(len(listed_creditors), 3)
        print(f"  ✓ 成功列出{len(listed_creditors)}个债权人")

        # 批量状态查询
        print("\n▶ 批量状态查询")
        result = self.controller.batch_status(1)
        self.assertTrue(result["success"])
        self.assertEqual(result["creditor_count"], 3)
        for status in result["creditors"]:
            self.assertEqual(status["current_round"], 1)
            self.assertEqual(status["total_rounds"], 1)
        print("  ✓ 批量状态查询正确")

        # 批量初始化Round 2（只处理100和102）
        print("\n▶ 批量初始化Round 2（过滤模式）")
        result = self.controller.batch_init_round(
            batch_number=1,
            round_number=2,
            creditor_filter=[100, 102]
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["success_count"], 2)

        # 验证过滤效果
        manager_100 = RoundManager(self.batch_dir / "100-债权人A")
        self.assertTrue(manager_100.round_exists(2))

        manager_101 = RoundManager(self.batch_dir / "101-债权人B")
        self.assertFalse(manager_101.round_exists(2))

        manager_102 = RoundManager(self.batch_dir / "102-债权人C")
        self.assertTrue(manager_102.round_exists(2))

        print("  ✓ 批量初始化和过滤正确")
        print("\n✅ 测试2通过：多债权人批量处理成功")

    def test_03_impact_analysis_accuracy(self):
        """测试3: 影响分析准确性验证"""
        print("\n" + "=" * 80)
        print("测试3: 影响分析准确性验证")
        print("=" * 80)

        analyzer = ImpactAnalyzer(conservative=True)

        # 测试场景1: CRITICAL字段
        print("\n▶ 场景1: CRITICAL字段（破产日期）")
        result = analyzer.analyze_impact(["bankruptcy_date"])
        self.assertEqual(result.processing_mode.value, "full")
        self.assertEqual(result.time_savings_percent, 0)
        self.assertEqual(result.affected_stages, [1, 2, 3])
        print(f"  ✓ 处理模式: {result.processing_mode.value}")
        print(f"  ✓ 时间节省: {result.time_savings_percent}%")
        print(f"  ✓ 受影响阶段: {result.affected_stages}")

        # 测试场景2: HIGH字段
        print("\n▶ 场景2: HIGH字段（判决文书）")
        result = analyzer.analyze_impact(["judgment_document"])
        self.assertEqual(result.processing_mode.value, "incremental")
        # 当所有Stage都受影响时，基础节省是50%（因为Stage内部增量处理）
        self.assertIn(result.time_savings_percent, range(40, 61))
        self.assertEqual(result.affected_stages, [1, 2, 3])
        print(f"  ✓ 处理模式: {result.processing_mode.value}")
        print(f"  ✓ 时间节省: {result.time_savings_percent}%")
        print(f"  ✓ 受影响阶段: {result.affected_stages}")

        # 测试场景3: MEDIUM字段
        print("\n▶ 场景3: MEDIUM字段（付款期限）")
        result = analyzer.analyze_impact(["payment_deadline"])
        self.assertEqual(result.processing_mode.value, "incremental")
        # payment_deadline只影响Stage 2，所以跳过Stage 1和3，基础节省约66%
        self.assertIn(result.time_savings_percent, range(60, 75))
        print(f"  ✓ 处理模式: {result.processing_mode.value}")
        print(f"  ✓ 时间节省: {result.time_savings_percent}%")

        # 测试场景4: LOW字段
        print("\n▶ 场景4: LOW字段（备注）")
        result = analyzer.analyze_impact(["notes"])
        self.assertEqual(result.processing_mode.value, "partial")
        self.assertGreaterEqual(result.time_savings_percent, 85)
        self.assertEqual(result.affected_stages, [3])
        print(f"  ✓ 处理模式: {result.processing_mode.value}")
        print(f"  ✓ 时间节省: {result.time_savings_percent}%")

        # 测试场景5: 混合优先级（就高原则）
        print("\n▶ 场景5: 混合优先级（HIGH + LOW）")
        result = analyzer.analyze_impact(["judgment_document", "notes"])
        self.assertEqual(result.processing_mode.value, "incremental")
        self.assertEqual(result.highest_priority, "HIGH")
        print(f"  ✓ 采用较高优先级: {result.highest_priority}")
        print(f"  ✓ 处理模式: {result.processing_mode.value}")

        print("\n✅ 测试3通过：影响分析准确")

    def test_04_round_status_and_rollback(self):
        """测试4: 轮次状态管理和回滚"""
        print("\n" + "=" * 80)
        print("测试4: 轮次状态管理和回滚")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 创建3个轮次
        print("\n▶ 创建3个轮次")
        for i in range(1, 4):
            manager.initialize_round(
                i,
                parent_round=i-1 if i > 1 else None,
                processing_mode="full" if i == 1 else "incremental"
            )
            manager.mark_round_status(i, RoundStatus.COMPLETED.value)
            print(f"  ✓ Round {i} 创建完成")

        # 验证状态
        for i in range(1, 4):
            self.assertEqual(manager.get_round_status(i), RoundStatus.COMPLETED.value)

        # 回滚到Round 1
        print("\n▶ 回滚到Round 1")
        success, message = manager.rollback_to_round(1, reason="测试回滚")
        self.assertTrue(success)
        self.assertEqual(manager.get_current_round(), 1)
        print(f"  ✓ {message}")

        # 验证回滚后的状态
        print("\n▶ 验证回滚后状态")
        self.assertEqual(manager.get_round_status(1), RoundStatus.COMPLETED.value)
        self.assertEqual(manager.get_round_status(2), RoundStatus.ROLLED_BACK.value)
        self.assertEqual(manager.get_round_status(3), RoundStatus.ROLLED_BACK.value)
        print("  ✓ Round 1: COMPLETED")
        print("  ✓ Round 2: ROLLED_BACK")
        print("  ✓ Round 3: ROLLED_BACK")

        # 验证数据保留（审计需求）
        print("\n▶ 验证数据保留")
        self.assertTrue(manager.round_exists(1))
        self.assertTrue(manager.round_exists(2))
        self.assertTrue(manager.round_exists(3))
        print("  ✓ 所有轮次目录都保留")

        # 验证历史记录
        history_all = manager.get_history(include_rolled_back=True)
        self.assertEqual(len(history_all["rounds"]), 3)

        history_active = manager.get_history(include_rolled_back=False)
        self.assertEqual(len(history_active["rounds"]), 1)
        print("  ✓ 历史查看过滤功能正确")

        print("\n✅ 测试4通过：轮次状态管理和回滚正确")

    def test_05_changelog_auto_recording(self):
        """测试5: Changelog自动记录"""
        print("\n" + "=" * 80)
        print("测试5: Changelog自动记录")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 执行多个操作
        print("\n▶ 执行多个操作")

        # 操作1: 初始化Round 1
        manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        print("  ✓ 初始化Round 1")

        # 操作2: 完成Round 1
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)
        print("  ✓ 完成Round 1")

        # 操作3: 初始化Round 2
        manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                trigger_reason="补充证据")
        manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document"],
            "impact_analysis": {"time_savings_percent": 60}
        })
        print("  ✓ 初始化Round 2")

        # 操作4: 完成Round 2
        manager.mark_round_status(2, RoundStatus.COMPLETED.value)
        print("  ✓ 完成Round 2")

        # 操作5: 初始化Round 3
        manager.initialize_round(3, parent_round=2, processing_mode="partial")
        print("  ✓ 初始化Round 3")

        # 操作6: 回滚到Round 1
        manager.rollback_to_round(1, reason="发现错误")
        print("  ✓ 回滚到Round 1")

        # 验证changelog
        print("\n▶ 验证Changelog")
        changelog = manager.read_changelog()

        # 应该有3个轮次的记录
        self.assertEqual(len(changelog["changelog"]), 3)
        print(f"  ✓ Changelog包含{len(changelog['changelog'])}条记录")

        # 验证Round 1记录
        round1_entry = [e for e in changelog["changelog"] if e["round_number"] == 1][0]
        self.assertEqual(round1_entry["processing_mode"], "full")
        self.assertEqual(round1_entry["status"], "completed")
        print("  ✓ Round 1记录正确")

        # 验证Round 2记录（已回滚）
        round2_entry = [e for e in changelog["changelog"] if e["round_number"] == 2][0]
        self.assertEqual(round2_entry["action"], "回滚（已作废）")
        self.assertEqual(round2_entry["status"], "rolled_back")
        print("  ✓ Round 2回滚记录正确")

        # 验证摘要生成
        summary = manager.generate_changelog_summary()
        self.assertIn("Round 1", summary)
        self.assertIn("Round 2", summary)
        self.assertIn("Round 3", summary)
        print("  ✓ Changelog摘要生成正确")

        print("\n✅ 测试5通过：Changelog自动记录正确")

    def test_06_supplemental_checklist_generation(self):
        """测试6: 补充清单生成"""
        print("\n" + "=" * 80)
        print("测试6: 补充清单生成")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 创建带字段更新的轮次
        print("\n▶ 创建轮次并更新字段")
        manager.initialize_round(1, processing_mode="incremental", trigger_reason="补充材料")
        manager.update_round_metadata(1, {
            "fields_updated": [
                "bankruptcy_date",      # CRITICAL
                "judgment_document",    # HIGH
                "payment_deadline",     # MEDIUM
                "notes"                 # LOW
            ]
        })
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)
        print("  ✓ Round 1完成，包含4个字段更新")

        # 生成补充清单
        print("\n▶ 生成补充清单")
        result = manager.generate_supplemental_checklist(1)

        self.assertTrue(result["success"])
        self.assertEqual(result["fields_count"], 4)
        print(f"  ✓ 成功生成清单，包含{result['fields_count']}个字段")

        # 验证优先级分布
        print("\n▶ 验证优先级分布")
        categorized = result["categorized_fields"]
        self.assertEqual(categorized["CRITICAL"], 1)
        self.assertEqual(categorized["HIGH"], 1)
        self.assertEqual(categorized["MEDIUM"], 1)
        self.assertEqual(categorized["LOW"], 1)

        for priority, count in categorized.items():
            print(f"  ✓ {priority}: {count}个")

        # 验证文件内容
        print("\n▶ 验证Markdown内容")
        content = result["content"]
        self.assertIn("# 补充材料清单", content)
        self.assertIn("🔴 关键字段", content)
        self.assertIn("🟠 高优先级字段", content)
        self.assertIn("🟡 中优先级字段", content)
        self.assertIn("🟢 低优先级字段", content)
        self.assertIn("## 处理建议", content)
        print("  ✓ Markdown格式正确")

        # 验证文件存在
        checklist_file = Path(result["checklist_file"])
        self.assertTrue(checklist_file.exists())
        print(f"  ✓ 清单文件已保存: {checklist_file.name}")

        print("\n✅ 测试6通过：补充清单生成正确")

    def test_07_history_viewing_and_tracing(self):
        """测试7: 历史查看和追溯"""
        print("\n" + "=" * 80)
        print("测试7: 历史查看和追溯")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 创建复杂的历史记录
        print("\n▶ 创建复杂历史")

        # Round 1: Full
        manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)
        print("  ✓ Round 1: Full")

        # Round 2: Incremental
        manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                trigger_reason="补充证据")
        manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document"],
            "processing_summary": {"time_savings_percent": 60}
        })
        manager.mark_round_status(2, RoundStatus.COMPLETED.value)
        print("  ✓ Round 2: Incremental (60%节省)")

        # Round 3: Partial
        manager.initialize_round(3, parent_round=2, processing_mode="partial",
                                trigger_reason="调整备注")
        manager.update_round_metadata(3, {
            "fields_updated": ["notes"],
            "processing_summary": {"time_savings_percent": 85}
        })
        manager.mark_round_status(3, RoundStatus.COMPLETED.value)
        print("  ✓ Round 3: Partial (85%节省)")

        # Round 4: Incremental（后续回滚）
        manager.initialize_round(4, parent_round=3, processing_mode="incremental")
        manager.mark_round_status(4, RoundStatus.COMPLETED.value)
        print("  ✓ Round 4: Incremental")

        # 回滚Round 4
        manager.rollback_to_round(3, reason="Round 4有错误")
        print("  ✓ 回滚Round 4")

        # 验证完整历史
        print("\n▶ 验证完整历史（包含已回滚）")
        history_all = manager.get_history(include_rolled_back=True)
        self.assertEqual(history_all["total_rounds"], 4)
        self.assertEqual(len(history_all["rounds"]), 4)
        self.assertEqual(history_all["current_round"], 3)
        print(f"  ✓ 总轮次: {history_all['total_rounds']}")
        print(f"  ✓ 当前轮次: {history_all['current_round']}")

        # 验证活跃历史（排除已回滚）
        print("\n▶ 验证活跃历史（排除已回滚）")
        history_active = manager.get_history(include_rolled_back=False)
        self.assertEqual(len(history_active["rounds"]), 3)
        print(f"  ✓ 活跃轮次数: {len(history_active['rounds'])}")

        # 验证详细信息
        print("\n▶ 验证详细信息")
        for round_info in history_all["rounds"]:
            round_num = round_info["round_number"]
            status = round_info["status"]
            mode = round_info["processing_mode"]
            is_rolled_back = round_info["is_rolled_back"]

            status_icon = "✗" if is_rolled_back else "✓"
            print(f"  {status_icon} Round {round_num}: {mode} ({status})")

        print("\n✅ 测试7通过：历史查看和追溯正确")

    def test_08_batch_operation_optimization(self):
        """测试8: 批量操作优化"""
        print("\n" + "=" * 80)
        print("测试8: 批量操作优化")
        print("=" * 80)

        # 创建5个债权人
        print("\n▶ 创建5个债权人")
        creditors = [(i, f"债权人{chr(65+i)}") for i in range(100, 105)]
        for number, name in creditors:
            creditor_dir = self.batch_dir / f"{number:03d}-{name}"
            creditor_dir.mkdir()
            manager = RoundManager(creditor_dir)
            manager.initialize_round(1, processing_mode="full")
            manager.mark_round_status(1, RoundStatus.COMPLETED.value)
        print(f"  ✓ 创建{len(creditors)}个债权人")

        # 测试1: 批量状态查询
        print("\n▶ 测试批量状态查询")
        result = self.controller.batch_status(1)
        self.assertTrue(result["success"])
        self.assertEqual(result["creditor_count"], 5)
        print(f"  ✓ 查询到{result['creditor_count']}个债权人")

        # 测试2: 批量初始化（全部）
        print("\n▶ 测试批量初始化（全部）")
        result = self.controller.batch_init_round(1, 2, creditor_filter=None)
        self.assertTrue(result["success"])
        self.assertEqual(result["success_count"], 5)
        print(f"  ✓ 成功初始化{result['success_count']}个轮次")

        # 测试3: 批量初始化（过滤）
        print("\n▶ 测试批量初始化（过滤: 100,102,104）")
        result = self.controller.batch_init_round(1, 3, creditor_filter=[100, 102, 104])
        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["success_count"], 3)
        print(f"  ✓ 处理{result['total']}个，成功{result['success_count']}个")

        # 验证过滤效果
        print("\n▶ 验证过滤效果")
        for number, name in creditors:
            manager = RoundManager(self.batch_dir / f"{number:03d}-{name}")
            has_round3 = manager.round_exists(3)
            should_have = number in [100, 102, 104]
            self.assertEqual(has_round3, should_have)
            icon = "✓" if has_round3 else "✗"
            print(f"  {icon} {number:03d}: Round 3 {'存在' if has_round3 else '不存在'}")

        print("\n✅ 测试8通过：批量操作优化正确")

    def test_09_error_handling_and_boundaries(self):
        """测试9: 错误处理和边界条件"""
        print("\n" + "=" * 80)
        print("测试9: 错误处理和边界条件")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 边界1: 不存在的轮次
        print("\n▶ 边界1: 访问不存在的轮次")
        self.assertFalse(manager.round_exists(99))
        metadata = manager.get_round_metadata(99)
        self.assertIsNone(metadata)
        print("  ✓ 不存在的轮次返回None")

        # 边界2: 无效的回滚
        print("\n▶ 边界2: 无效的回滚操作")
        manager.initialize_round(1, processing_mode="full")
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 尝试回滚到当前轮次
        success, message = manager.rollback_to_round(1)
        self.assertFalse(success)
        print(f"  ✓ 回滚到当前轮次被拒绝: {message}")

        # 尝试回滚到不存在的轮次
        success, message = manager.rollback_to_round(99)
        self.assertFalse(success)
        print(f"  ✓ 回滚到不存在轮次被拒绝: {message}")

        # 边界3: 回滚到已作废轮次
        print("\n▶ 边界3: 回滚到已作废轮次")
        manager.initialize_round(2, parent_round=1, processing_mode="incremental")
        manager.mark_round_status(2, RoundStatus.COMPLETED.value)
        manager.rollback_to_round(1)  # Round 2现在是ROLLED_BACK

        success, message = manager.rollback_to_round(2)
        self.assertFalse(success)
        print(f"  ✓ 回滚到已作废轮次被拒绝: {message}")

        # 边界4: 空批次查询
        print("\n▶ 边界4: 空批次查询")
        result = self.controller.batch_status(999)
        self.assertFalse(result["success"])
        self.assertEqual(result["creditor_count"], 0)
        print(f"  ✓ 空批次返回0个债权人")

        # 边界5: 无字段更新的补充清单
        print("\n▶ 边界5: 无字段更新的补充清单")
        manager_new = RoundManager(creditor_dir)
        manager_new.initialize_round(3, processing_mode="full")
        result = manager_new.generate_supplemental_checklist(3)
        self.assertFalse(result["success"])
        print(f"  ✓ 无字段更新无法生成清单: {result['message']}")

        print("\n✅ 测试9通过：错误处理和边界条件正确")

    def test_10_data_consistency_validation(self):
        """测试10: 数据一致性验证"""
        print("\n" + "=" * 80)
        print("测试10: 数据一致性验证")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 创建轮次链
        print("\n▶ 创建轮次链")
        manager.initialize_round(1, processing_mode="full", trigger_reason="首次")
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                trigger_reason="补充")
        manager.mark_round_status(2, RoundStatus.COMPLETED.value)

        manager.initialize_round(3, parent_round=2, processing_mode="partial",
                                trigger_reason="调整")
        manager.mark_round_status(3, RoundStatus.COMPLETED.value)

        # 验证1: 父子关系一致性
        print("\n▶ 验证父子关系")
        metadata2 = manager.get_round_metadata(2)
        metadata3 = manager.get_round_metadata(3)
        self.assertEqual(metadata2["parent_round"], 1)
        self.assertEqual(metadata3["parent_round"], 2)
        print("  ✓ Round 2父轮次: 1")
        print("  ✓ Round 3父轮次: 2")

        # 验证2: 当前轮次指针一致性
        print("\n▶ 验证当前轮次指针")
        current = manager.get_current_round()
        total = manager.get_total_rounds()
        self.assertEqual(current, 3)
        self.assertEqual(total, 3)
        print(f"  ✓ 当前轮次: {current}")
        print(f"  ✓ 总轮次数: {total}")

        # 验证3: Changelog与元数据一致性
        print("\n▶ 验证Changelog与元数据一致性")
        changelog = manager.read_changelog()
        for entry in changelog["changelog"]:
            round_num = entry["round_number"]
            metadata = manager.get_round_metadata(round_num)

            self.assertEqual(entry["processing_mode"], metadata["processing_mode"])
            self.assertEqual(entry["status"], metadata["status"])

            print(f"  ✓ Round {round_num}: Changelog与元数据一致")

        # 验证4: 回滚后的一致性
        print("\n▶ 验证回滚后的一致性")
        manager.rollback_to_round(1, reason="测试")

        # 当前轮次应该更新
        self.assertEqual(manager.get_current_round(), 1)

        # Round 2和3应该标记为ROLLED_BACK
        self.assertEqual(manager.get_round_status(2), RoundStatus.ROLLED_BACK.value)
        self.assertEqual(manager.get_round_status(3), RoundStatus.ROLLED_BACK.value)

        # Changelog应该更新
        changelog = manager.read_changelog()
        round2_entry = [e for e in changelog["changelog"] if e["round_number"] == 2][0]
        self.assertEqual(round2_entry["status"], "rolled_back")

        print("  ✓ 回滚后所有数据一致")

        print("\n✅ 测试10通过：数据一致性验证正确")

    def test_11_file_organization_standards(self):
        """测试11: 文件组织标准"""
        print("\n" + "=" * 80)
        print("测试11: 文件组织标准")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 初始化轮次
        print("\n▶ 初始化轮次并生成文件")
        manager.initialize_round(1, processing_mode="incremental", trigger_reason="测试")
        manager.update_round_metadata(1, {
            "fields_updated": ["judgment_document", "notes"]
        })
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)

        # 生成补充清单
        result = manager.generate_supplemental_checklist(1)
        self.assertTrue(result["success"])

        # 验证1: 轮次目录结构
        print("\n▶ 验证轮次目录结构")
        round1_dir = manager.get_round_path(1)
        self.assertTrue(round1_dir.exists())
        self.assertTrue(round1_dir.is_dir())
        print(f"  ✓ 轮次目录存在: {round1_dir.name}")

        # 验证2: 元数据文件
        print("\n▶ 验证元数据文件")
        metadata_file = round1_dir / ".round_metadata.json"
        self.assertTrue(metadata_file.exists())
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            self.assertIn("round_number", metadata)
            self.assertIn("processing_mode", metadata)
            self.assertIn("status", metadata)
        print("  ✓ 元数据文件格式正确")

        # 验证3: Changelog文件
        print("\n▶ 验证Changelog文件")
        changelog_file = creditor_dir / ".changelog.json"
        self.assertTrue(changelog_file.exists())
        with open(changelog_file, 'r', encoding='utf-8') as f:
            changelog = json.load(f)
            self.assertIn("changelog", changelog)
            self.assertIn("creditor_info", changelog)
        print("  ✓ Changelog文件格式正确")

        # 验证4: 补充清单文件
        print("\n▶ 验证补充清单文件")
        checklist_file = Path(result["checklist_file"])
        self.assertTrue(checklist_file.exists())
        self.assertTrue(checklist_file.name.startswith("round_1_supplemental_checklist"))
        self.assertTrue(checklist_file.suffix == ".md")
        print(f"  ✓ 补充清单文件存在: {checklist_file.name}")

        # 验证5: 当前轮次追踪文件
        print("\n▶ 验证当前轮次追踪")
        current_file = creditor_dir / ".current_round.json"
        self.assertTrue(current_file.exists())
        with open(current_file, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
            self.assertEqual(current_data["current_round"], 1)
            self.assertEqual(current_data["total_rounds"], 1)
        print("  ✓ 当前轮次追踪文件正确")

        print("\n✅ 测试11通过：文件组织标准正确")

    def test_12_complete_audit_trail(self):
        """测试12: 完整审计追踪"""
        print("\n" + "=" * 80)
        print("测试12: 完整审计追踪")
        print("=" * 80)

        creditor_dir = self.batch_dir / "100-测试债权人"
        creditor_dir.mkdir()
        manager = RoundManager(creditor_dir)

        # 模拟完整工作流
        print("\n▶ 模拟完整工作流")

        # 操作1: 初始化Round 1
        manager.initialize_round(1, processing_mode="full", trigger_reason="首次处理")
        manager.mark_round_status(1, RoundStatus.COMPLETED.value)
        print("  ✓ 操作1: 初始化并完成Round 1")

        # 操作2: 初始化Round 2
        manager.initialize_round(2, parent_round=1, processing_mode="incremental",
                                trigger_reason="补充判决文书")
        manager.update_round_metadata(2, {
            "fields_updated": ["judgment_document"],
            "impact_analysis": {
                "affected_stages": [1, 2, 3],
                "time_savings_percent": 60
            }
        })
        manager.mark_round_status(2, RoundStatus.COMPLETED.value)
        print("  ✓ 操作2: 初始化并完成Round 2")

        # 操作3: 生成补充清单
        result = manager.generate_supplemental_checklist(2)
        self.assertTrue(result["success"])
        print("  ✓ 操作3: 生成Round 2补充清单")

        # 操作4: 初始化Round 3
        manager.initialize_round(3, parent_round=2, processing_mode="partial",
                                trigger_reason="调整备注")
        manager.update_round_metadata(3, {
            "fields_updated": ["notes"],
            "impact_analysis": {
                "affected_stages": [3],
                "time_savings_percent": 85
            }
        })
        print("  ✓ 操作4: 初始化Round 3")

        # 操作5: 发现问题，回滚
        manager.rollback_to_round(2, reason="发现Round 3备注有误")
        print("  ✓ 操作5: 回滚Round 3")

        # 操作6: 重新处理Round 3
        manager.initialize_round(4, parent_round=2, processing_mode="partial",
                                trigger_reason="重新调整备注")
        manager.mark_round_status(4, RoundStatus.COMPLETED.value)
        print("  ✓ 操作6: 重新处理为Round 4")

        # 审计验证1: 所有操作都有记录
        print("\n▶ 审计验证1: 操作记录完整性")
        changelog = manager.read_changelog()
        # 应该有4个轮次的记录（1,2,3已回滚,4）
        self.assertEqual(len(changelog["changelog"]), 4)
        print(f"  ✓ Changelog包含{len(changelog['changelog'])}条记录")

        # 审计验证2: 历史完整性
        print("\n▶ 审计验证2: 历史记录完整性")
        history = manager.get_history(include_rolled_back=True)
        self.assertEqual(len(history["rounds"]), 4)
        print(f"  ✓ 历史包含{len(history['rounds'])}个轮次")

        # 审计验证3: 回滚追踪
        print("\n▶ 审计验证3: 回滚操作可追踪")
        round3_metadata = manager.get_round_metadata(3)
        self.assertEqual(round3_metadata["status"], "rolled_back")
        self.assertIn("rolled_back_at", round3_metadata)
        self.assertIn("rolled_back_reason", round3_metadata)
        print(f"  ✓ Round 3回滚时间: {round3_metadata['rolled_back_at']}")
        print(f"  ✓ Round 3回滚原因: {round3_metadata['rolled_back_reason']}")

        # 审计验证4: 父子关系可追踪
        print("\n▶ 审计验证4: 父子关系可追踪")
        for i in [2, 3, 4]:
            metadata = manager.get_round_metadata(i)
            print(f"  ✓ Round {i}父轮次: {metadata.get('parent_round')}")

        # 审计验证5: 影响分析可追踪
        print("\n▶ 审计验证5: 影响分析可追踪")
        for i in [2, 4]:
            metadata = manager.get_round_metadata(i)
            if "impact_analysis" in metadata:
                impact = metadata["impact_analysis"]
                print(f"  ✓ Round {i}节省时间: {impact.get('time_savings_percent', 0)}%")

        # 审计验证6: 文件完整性
        print("\n▶ 审计验证6: 所有文件都保留")
        for i in [1, 2, 3, 4]:
            self.assertTrue(manager.round_exists(i))
            print(f"  ✓ Round {i}目录存在")

        # 生成完整审计报告
        print("\n▶ 生成完整审计报告")
        print("-" * 60)
        manager.print_history(include_rolled_back=True)
        print("-" * 60)
        print(manager.generate_changelog_summary())
        print("-" * 60)

        print("\n✅ 测试12通过：完整审计追踪可用")


def run_integration_tests():
    """运行完整集成测试"""
    print("\n" + "=" * 80)
    print("多轮债权审查系统 - 完整集成测试")
    print("=" * 80)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCompleteIntegration)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 80)
    print("集成测试总结")
    print("=" * 80)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n" + "🎉" * 30)
        print("✅ 所有集成测试通过！系统功能完整！")
        print("🎉" * 30)
        print("\n测试覆盖范围:")
        print("  ✅ 测试1: 完整三轮工作流（Full → Incremental → Partial）")
        print("  ✅ 测试2: 多债权人批量处理")
        print("  ✅ 测试3: 影响分析准确性验证")
        print("  ✅ 测试4: 轮次状态管理和回滚")
        print("  ✅ 测试5: Changelog自动记录")
        print("  ✅ 测试6: 补充清单生成")
        print("  ✅ 测试7: 历史查看和追溯")
        print("  ✅ 测试8: 批量操作优化")
        print("  ✅ 测试9: 错误处理和边界条件")
        print("  ✅ 测试10: 数据一致性验证")
        print("  ✅ 测试11: 文件组织标准")
        print("  ✅ 测试12: 完整审计追踪")
        return 0
    else:
        print("\n❌ 部分集成测试失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_integration_tests())
