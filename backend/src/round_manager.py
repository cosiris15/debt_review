# -*- coding: utf-8 -*-
"""
轮次管理器 - 管理多轮交互的轮次生命周期

负责轮次的初始化、元数据管理、状态跟踪等核心功能。
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class RoundStatus(Enum):
    """轮次状态枚举"""
    INITIALIZED = "initialized"  # 已初始化
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 处理失败
    ROLLED_BACK = "rolled_back"  # 已回滚（作废）

    @classmethod
    def is_valid_status(cls, status: str) -> bool:
        """检查状态值是否有效"""
        return status in [s.value for s in cls]


class RoundManager:
    """轮次管理器"""

    def __init__(self, creditor_base_path: Path):
        """初始化轮次管理器

        Args:
            creditor_base_path: 债权人基础目录路径
        """
        self.base_path = Path(creditor_base_path)
        self.current_round_file = self.base_path / ".current_round.json"

    def get_current_round(self) -> int:
        """获取当前轮次号

        Returns:
            int: 当前轮次号，如果不存在轮次结构返回0
        """
        if self.current_round_file.exists():
            with open(self.current_round_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("current_round", 0)

        # 检测是否有round_1/目录
        round_1 = self.base_path / "round_1"
        if round_1.exists():
            return 1

        return 0

    def get_total_rounds(self) -> int:
        """获取总轮次数

        Returns:
            int: 总轮次数
        """
        if self.current_round_file.exists():
            with open(self.current_round_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("total_rounds", 0)

        # 扫描所有round_N/目录
        round_dirs = list(self.base_path.glob("round_*"))
        return len(round_dirs)

    def round_exists(self, round_number: int) -> bool:
        """检查轮次是否存在

        Args:
            round_number: 轮次号

        Returns:
            bool: 是否存在
        """
        round_dir = self.base_path / f"round_{round_number}"
        return round_dir.exists()

    def get_round_path(self, round_number: int) -> Path:
        """获取轮次目录路径

        Args:
            round_number: 轮次号

        Returns:
            Path: 轮次目录路径
        """
        return self.base_path / f"round_{round_number}"

    def initialize_round(
        self,
        round_number: int,
        parent_round: Optional[int] = None,
        processing_mode: str = "full",
        trigger_reason: str = ""
    ) -> Dict:
        """初始化新轮次

        Args:
            round_number: 轮次号
            parent_round: 父轮次号（如果是补充轮）
            processing_mode: 处理模式（full, incremental, partial）
            trigger_reason: 触发原因

        Returns:
            Dict: 轮次元数据

        Raises:
            ValueError: 如果轮次已存在
        """
        round_dir = self.get_round_path(round_number)

        if round_dir.exists():
            raise ValueError(f"轮次 {round_number} 已存在: {round_dir}")

        # 创建标准子目录
        subdirs = ["输入材料", "工作底稿", "最终报告", "计算文件"]
        for subdir in subdirs:
            (round_dir / subdir).mkdir(parents=True, exist_ok=True)

        # 生成轮次元数据
        metadata = {
            "round_number": round_number,
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "processing_mode": processing_mode,
            "parent_round": parent_round,
            "trigger_reason": trigger_reason,
            "fields_updated": [],
            "processing_summary": {},
            "agent_execution": {},
            "quality_checks": {}
        }

        metadata_file = round_dir / ".round_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 更新当前轮次指针
        self._update_current_round(round_number)

        # 记录到changelog
        self.update_changelog(round_number, action="初始化")

        print(f"✓ 初始化轮次 {round_number}: {round_dir}")
        return metadata

    def get_round_metadata(self, round_number: int) -> Optional[Dict]:
        """获取轮次元数据

        Args:
            round_number: 轮次号

        Returns:
            Dict: 轮次元数据，如果不存在返回None
        """
        metadata_file = self.get_round_path(round_number) / ".round_metadata.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_round_metadata(
        self,
        round_number: int,
        updates: Dict
    ) -> bool:
        """更新轮次元数据

        Args:
            round_number: 轮次号
            updates: 要更新的字段字典

        Returns:
            bool: 是否成功
        """
        metadata = self.get_round_metadata(round_number)
        if metadata is None:
            return False

        # 合并更新
        metadata.update(updates)

        # 写回文件
        metadata_file = self.get_round_path(round_number) / ".round_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return True

    def mark_round_status(
        self,
        round_number: int,
        status: str
    ) -> bool:
        """标记轮次状态

        Args:
            round_number: 轮次号
            status: 状态（initialized, processing, completed, failed）

        Returns:
            bool: 是否成功
        """
        success = self.update_round_metadata(round_number, {"status": status})
        if success:
            # 记录状态变更到changelog
            action_map = {
                RoundStatus.INITIALIZED.value: "初始化",
                RoundStatus.PROCESSING.value: "开始处理",
                RoundStatus.COMPLETED.value: "完成",
                RoundStatus.FAILED.value: "失败",
                RoundStatus.ROLLED_BACK.value: "回滚"
            }
            action = action_map.get(status, f"状态变更: {status}")
            self.update_changelog(round_number, action=action)
        return success

    def get_round_status(self, round_number: int) -> Optional[str]:
        """获取轮次状态

        Args:
            round_number: 轮次号

        Returns:
            str: 状态，如果轮次不存在返回None
        """
        metadata = self.get_round_metadata(round_number)
        return metadata.get("status") if metadata else None

    def list_all_rounds(self) -> List[Dict]:
        """列出所有轮次的基本信息

        Returns:
            List[Dict]: 轮次信息列表
        """
        rounds = []
        current = self.get_current_round()

        for round_num in range(1, current + 1):
            if self.round_exists(round_num):
                metadata = self.get_round_metadata(round_num)
                if metadata:
                    rounds.append({
                        "round_number": round_num,
                        "created_at": metadata.get("created_at"),
                        "status": metadata.get("status"),
                        "processing_mode": metadata.get("processing_mode"),
                        "is_current": round_num == current
                    })

        return rounds

    def get_history(self, include_rolled_back: bool = True) -> Dict:
        """获取轮次历史（详细视图）

        Args:
            include_rolled_back: 是否包含已回滚的轮次

        Returns:
            Dict: 包含历史信息的字典
        """
        current = self.get_current_round()

        # 扫描所有实际存在的轮次（不依赖total_rounds）
        all_round_dirs = sorted(self.base_path.glob("round_*"))
        max_round = max([int(d.name.split("_")[1]) for d in all_round_dirs]) if all_round_dirs else 0

        history = {
            "current_round": current,
            "total_rounds": max_round,  # 实际存在的轮次数
            "rounds": []
        }

        # 扫描所有轮次（包括被回滚的）
        for round_num in range(1, max_round + 1):
            if not self.round_exists(round_num):
                continue

            metadata = self.get_round_metadata(round_num)
            if not metadata:
                continue

            status = metadata.get("status", "unknown")

            # 跳过已回滚轮次（如果不包含）
            if not include_rolled_back and status == RoundStatus.ROLLED_BACK.value:
                continue

            round_info = {
                "round_number": round_num,
                "status": status,
                "created_at": metadata.get("created_at", ""),
                "processing_mode": metadata.get("processing_mode", "unknown"),
                "parent_round": metadata.get("parent_round"),
                "trigger_reason": metadata.get("trigger_reason", ""),
                "fields_updated": metadata.get("fields_updated", []),
                "is_current": round_num == current,
                "is_rolled_back": status == RoundStatus.ROLLED_BACK.value
            }

            # 添加回滚信息（如果已回滚）
            if status == RoundStatus.ROLLED_BACK.value:
                round_info["rolled_back_at"] = metadata.get("rolled_back_at", "")
                round_info["rolled_back_reason"] = metadata.get("rolled_back_reason", "")

            # 添加处理摘要
            processing_summary = metadata.get("processing_summary", {})
            if processing_summary:
                round_info["time_saved_percent"] = processing_summary.get("time_savings_percent", 0)
                round_info["stages_executed"] = processing_summary.get("stages_executed", [])

            history["rounds"].append(round_info)

        return history

    def print_history(self, include_rolled_back: bool = True):
        """打印格式化的轮次历史

        Args:
            include_rolled_back: 是否包含已回滚的轮次
        """
        history = self.get_history(include_rolled_back)

        print("\n" + "=" * 80)
        print("轮次历史")
        print("=" * 80)
        print(f"当前轮次: Round {history['current_round']}")
        print(f"总轮次数: {history['total_rounds']}")
        print("-" * 80)

        for r in history["rounds"]:
            # 状态标记
            status_markers = []
            if r["is_current"]:
                status_markers.append("← 当前")
            if r["is_rolled_back"]:
                status_markers.append("✗ 已作废")
            status_str = " ".join(status_markers)

            print(f"\nRound {r['round_number']}: {r['status']} {status_str}")
            print(f"  处理模式: {r['processing_mode']}")
            print(f"  创建时间: {r['created_at']}")

            if r.get("parent_round"):
                print(f"  父轮次: Round {r['parent_round']}")

            if r.get("trigger_reason"):
                print(f"  触发原因: {r['trigger_reason']}")

            if r.get("fields_updated"):
                print(f"  变更字段: {', '.join(r['fields_updated'])}")

            if r.get("time_saved_percent"):
                print(f"  节省时间: {r['time_saved_percent']}%")

            # 回滚信息
            if r["is_rolled_back"]:
                print(f"  回滚时间: {r.get('rolled_back_at', '')}")
                print(f"  回滚原因: {r.get('rolled_back_reason', '')}")

        print("\n" + "=" * 80)

    def get_latest_report_path(
        self,
        round_number: Optional[int] = None
    ) -> Optional[Path]:
        """获取最新最终报告的路径

        Args:
            round_number: 轮次号，如果为None则使用当前轮次

        Returns:
            Path: 报告路径，如果不存在返回None
        """
        if round_number is None:
            round_number = self.get_current_round()

        if round_number == 0:
            return None

        final_reports_dir = self.get_round_path(round_number) / "最终报告"
        if not final_reports_dir.exists():
            return None

        # 查找GY2025_*.md文件
        report_files = list(final_reports_dir.glob("GY2025_*.md"))
        if not report_files:
            return None

        # 返回最新的（按修改时间）
        latest = max(report_files, key=lambda p: p.stat().st_mtime)
        return latest

    def rollback_to_round(self, target_round: int, reason: str = "") -> Tuple[bool, str]:
        """回滚到指定轮次（标记后续轮次为ROLLED_BACK，不删除数据）

        Args:
            target_round: 目标轮次号
            reason: 回滚原因

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        current = self.get_current_round()
        total = self.get_total_rounds()

        if target_round >= current:
            return False, f"目标轮次 {target_round} 必须小于当前轮次 {current}"

        if target_round < 1:
            return False, f"目标轮次必须 >= 1"

        if not self.round_exists(target_round):
            return False, f"目标轮次 {target_round} 不存在"

        # 检查目标轮次是否已被回滚
        target_status = self.get_round_status(target_round)
        if target_status == RoundStatus.ROLLED_BACK.value:
            return False, f"目标轮次 {target_round} 已被回滚，无法回滚到已作废的轮次"

        try:
            # 标记target_round之后的所有轮次为ROLLED_BACK
            rolled_back_rounds = []
            for round_num in range(target_round + 1, total + 1):
                if self.round_exists(round_num):
                    # 标记为ROLLED_BACK状态
                    self.update_round_metadata(round_num, {
                        "status": RoundStatus.ROLLED_BACK.value,
                        "rolled_back_at": datetime.now().isoformat(),
                        "rolled_back_reason": reason or "用户请求回滚"
                    })
                    rolled_back_rounds.append(round_num)

            # 确保目标轮次标记为COMPLETED
            self.mark_round_status(target_round, RoundStatus.COMPLETED.value)

            # 更新当前轮次指针
            self._update_current_round(target_round)

            # 记录回滚操作到changelog
            for round_num in rolled_back_rounds:
                self.update_changelog(
                    round_num,
                    action="回滚（已作废）",
                    additional_info={"rollback_reason": reason or "用户请求回滚"}
                )

            message = (
                f"回滚成功：标记 {rolled_back_rounds} 轮次为已作废（数据保留用于审计），"
                f"当前轮次: {target_round}"
            )
            return True, message

        except Exception as e:
            return False, f"回滚失败: {str(e)}"

    def _update_current_round(self, round_number: int):
        """更新当前轮次指针（内部方法）

        Args:
            round_number: 轮次号
        """
        # 查找最新报告
        latest_report = self.get_latest_report_path(round_number)
        latest_report_path = None
        if latest_report:
            # 转换为相对于base_path的路径
            latest_report_path = str(latest_report.relative_to(self.base_path))

        data = {
            "current_round": round_number,
            "total_rounds": round_number,
            "latest_report_path": latest_report_path,
            "last_updated": datetime.now().isoformat()
        }

        with open(self.current_round_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def copy_files_from_previous_round(
        self,
        current_round: int,
        subdirs: List[str]
    ) -> Dict[str, bool]:
        """从前一轮复制文件到当前轮（用于增量处理）

        Args:
            current_round: 当前轮次号
            subdirs: 要复制的子目录列表（如 ["工作底稿", "计算文件"]）

        Returns:
            Dict[str, bool]: 每个子目录的复制状态
        """
        if current_round <= 1:
            return {subdir: False for subdir in subdirs}

        previous_round = current_round - 1
        results = {}

        for subdir in subdirs:
            src_dir = self.get_round_path(previous_round) / subdir
            dst_dir = self.get_round_path(current_round) / subdir

            if not src_dir.exists():
                results[subdir] = False
                continue

            try:
                # 复制目录内容
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)

                shutil.copytree(src_dir, dst_dir)
                results[subdir] = True
            except Exception as e:
                print(f"复制 {subdir} 失败: {e}")
                results[subdir] = False

        return results

    # ========== Changelog管理功能 ==========

    def get_changelog_path(self) -> Path:
        """获取changelog文件路径

        Returns:
            Path: .changelog.json文件路径
        """
        return self.base_path / ".changelog.json"

    def read_changelog(self) -> Dict:
        """读取changelog

        Returns:
            Dict: changelog内容，如果文件不存在返回空结构
        """
        changelog_file = self.get_changelog_path()

        if not changelog_file.exists():
            return {
                "creditor_info": {},
                "changelog": []
            }

        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  读取changelog失败: {e}")
            return {
                "creditor_info": {},
                "changelog": []
            }

    def write_changelog(self, changelog_data: Dict) -> bool:
        """写入changelog

        Args:
            changelog_data: changelog数据

        Returns:
            bool: 是否成功
        """
        changelog_file = self.get_changelog_path()

        try:
            with open(changelog_file, 'w', encoding='utf-8') as f:
                json.dump(changelog_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  写入changelog失败: {e}")
            return False

    def update_changelog(
        self,
        round_number: int,
        action: str = "更新",
        additional_info: Optional[Dict] = None
    ) -> bool:
        """更新changelog（添加轮次变更记录）

        Args:
            round_number: 轮次号
            action: 操作类型（初始化、增量更新、回滚等）
            additional_info: 附加信息

        Returns:
            bool: 是否成功
        """
        # 读取现有changelog
        changelog = self.read_changelog()

        # 获取轮次元数据
        metadata = self.get_round_metadata(round_number)
        if not metadata:
            print(f"⚠️  无法获取轮次 {round_number} 的元数据")
            return False

        # 构建变更记录
        change_entry = {
            "round_number": round_number,
            "timestamp": metadata.get("created_at", datetime.now().isoformat()),
            "action": action,
            "processing_mode": metadata.get("processing_mode", "unknown"),
            "trigger_reason": metadata.get("trigger_reason", ""),
            "fields_updated": metadata.get("fields_updated", []),
            "status": metadata.get("status", "initialized")
        }

        # 添加影响分析信息（如果存在）
        if "impact_analysis" in metadata:
            impact = metadata["impact_analysis"]
            change_entry["impact_analysis"] = {
                "affected_stages": impact.get("affected_stages", []),
                "affected_sections": impact.get("affected_sections", []),
                "time_savings_percent": impact.get("time_savings_percent", 0)
            }

        # 添加附加信息
        if additional_info:
            change_entry.update(additional_info)

        # 检查是否已存在该轮次的记录
        existing_index = None
        for i, entry in enumerate(changelog["changelog"]):
            if entry["round_number"] == round_number:
                existing_index = i
                break

        if existing_index is not None:
            # 更新现有记录
            changelog["changelog"][existing_index] = change_entry
        else:
            # 添加新记录
            changelog["changelog"].append(change_entry)

        # 按轮次号排序
        changelog["changelog"].sort(key=lambda x: x["round_number"])

        # 写入文件
        return self.write_changelog(changelog)

    def generate_changelog_summary(self) -> str:
        """生成changelog摘要（人类可读）

        Returns:
            str: 格式化的changelog摘要
        """
        changelog = self.read_changelog()

        if not changelog["changelog"]:
            return "暂无变更历史"

        lines = ["变更历史摘要", "=" * 60]

        for entry in changelog["changelog"]:
            lines.append(f"\nRound {entry['round_number']}: {entry['action']}")
            lines.append(f"  时间: {entry['timestamp']}")
            lines.append(f"  处理模式: {entry['processing_mode']}")

            if entry.get("trigger_reason"):
                lines.append(f"  触发原因: {entry['trigger_reason']}")

            if entry.get("fields_updated"):
                lines.append(f"  变更字段: {', '.join(entry['fields_updated'])}")

            if entry.get("impact_analysis"):
                impact = entry["impact_analysis"]
                lines.append(f"  节省时间: {impact.get('time_savings_percent', 0)}%")

            lines.append(f"  状态: {entry['status']}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

    # ========== 补充清单生成功能 ==========

    def generate_supplemental_checklist(
        self,
        round_number: int,
        output_file: Optional[str] = None
    ) -> Dict:
        """生成补充材料清单（基于影响分析结果）

        Args:
            round_number: 轮次号
            output_file: 输出文件路径（可选，默认为当前债权人目录下）

        Returns:
            Dict: 补充清单信息
        """
        from config.field_priorities import FIELD_PRIORITIES

        # 获取轮次元数据
        metadata = self.get_round_metadata(round_number)
        if not metadata:
            return {"success": False, "message": f"轮次 {round_number} 不存在"}

        # 获取影响分析信息
        impact_analysis = metadata.get("impact_analysis", {})
        fields_updated = metadata.get("fields_updated", [])

        if not fields_updated:
            return {
                "success": False,
                "message": f"轮次 {round_number} 无字段更新信息，无法生成补充清单"
            }

        # 按优先级分类字段
        categorized_fields = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }

        # 查找每个字段的优先级和信息
        for field in fields_updated:
            # 在FIELD_PRIORITIES中查找该字段所属的优先级
            found_priority = None
            field_data = None

            for priority_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if field in FIELD_PRIORITIES[priority_level]:
                    found_priority = priority_level
                    field_data = FIELD_PRIORITIES[priority_level][field]
                    break

            # 如果没找到，默认为MEDIUM
            if found_priority is None:
                found_priority = "MEDIUM"
                field_data = {"display_name": field, "reason": ""}

            field_info = {
                "field_name": field,
                "display_name": field_data.get("display_name", field),
                "description": field_data.get("reason", ""),
                "required_materials": field_data.get("required_materials", [])
            }
            categorized_fields[found_priority].append(field_info)

        # 生成Markdown清单
        lines = [
            f"# 补充材料清单 - Round {round_number}",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**触发原因**: {metadata.get('trigger_reason', '未说明')}",
            f"**处理模式**: {metadata.get('processing_mode', 'unknown')}",
            "",
            "---",
            "",
            "## 补充材料清单概览",
            "",
            f"本轮次需要补充 **{len(fields_updated)}** 个字段的相关材料。",
            ""
        ]

        # 按优先级输出
        priority_labels = {
            "CRITICAL": "🔴 关键字段（必须补充）",
            "HIGH": "🟠 高优先级字段",
            "MEDIUM": "🟡 中优先级字段",
            "LOW": "🟢 低优先级字段"
        }

        for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            fields = categorized_fields[priority]
            if not fields:
                continue

            lines.append(f"### {priority_labels[priority]}")
            lines.append("")

            for i, field_info in enumerate(fields, 1):
                lines.append(f"#### {i}. {field_info['display_name']}")
                lines.append("")
                lines.append(f"**字段名称**: `{field_info['field_name']}`")
                lines.append("")

                if field_info['description']:
                    lines.append(f"**说明**: {field_info['description']}")
                    lines.append("")

                if field_info['required_materials']:
                    lines.append("**所需材料**:")
                    lines.append("")
                    for material in field_info['required_materials']:
                        lines.append(f"- [ ] {material}")
                    lines.append("")
                else:
                    lines.append("**所需材料**: *(未明确指定，请根据实际情况补充)*")
                    lines.append("")

                lines.append("---")
                lines.append("")

        # 添加处理建议
        lines.extend([
            "## 处理建议",
            "",
            "### 优先级说明",
            "",
            "- **🔴 关键字段**: 影响所有债权项和章节，必须优先补充",
            "- **🟠 高优先级**: 影响多个章节，建议尽快补充",
            "- **🟡 中优先级**: 影响特定章节，根据重要性补充",
            "- **🟢 低优先级**: 影响较小，可最后补充",
            "",
            "### 下一步操作",
            "",
            "1. 根据清单收集所需补充材料",
            "2. 整理材料文件放入补充材料目录",
            "3. 使用影响分析功能评估补充材料的影响范围",
            "4. 初始化新轮次进行增量处理",
            "",
            "---",
            "",
            f"*本清单由多轮债权审查系统自动生成 - Round {round_number}*"
        ])

        checklist_content = "\n".join(lines)

        # 保存到文件
        if output_file is None:
            output_file = self.base_path / f"round_{round_number}_supplemental_checklist.md"
        else:
            output_file = Path(output_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(checklist_content)

        return {
            "success": True,
            "checklist_file": str(output_file),
            "fields_count": len(fields_updated),
            "categorized_fields": {
                priority: len(fields)
                for priority, fields in categorized_fields.items()
                if fields
            },
            "content": checklist_content
        }


def main():
    """测试代码"""
    import tempfile

    print("=" * 60)
    print("轮次管理器测试")
    print("=" * 60)

    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test_creditor"
        test_path.mkdir()

        manager = RoundManager(test_path)

        # 测试1: 初始化Round 1
        print("\n测试1: 初始化Round 1")
        print("-" * 60)
        metadata = manager.initialize_round(
            round_number=1,
            processing_mode="full",
            trigger_reason="首次处理"
        )
        print(f"Round 1 元数据: {json.dumps(metadata, ensure_ascii=False, indent=2)}")

        # 测试2: 获取当前轮次
        print("\n测试2: 获取当前轮次")
        print("-" * 60)
        current = manager.get_current_round()
        print(f"当前轮次: {current}")

        # 测试3: 更新元数据
        print("\n测试3: 更新元数据")
        print("-" * 60)
        success = manager.update_round_metadata(1, {
            "status": "completed",
            "processing_summary": {
                "stages_executed": [1, 2, 3],
                "time_saved_percent": 0
            }
        })
        print(f"更新成功: {success}")
        updated_metadata = manager.get_round_metadata(1)
        print(f"更新后状态: {updated_metadata['status']}")

        # 测试4: 初始化Round 2
        print("\n测试4: 初始化Round 2")
        print("-" * 60)
        metadata2 = manager.initialize_round(
            round_number=2,
            parent_round=1,
            processing_mode="incremental",
            trigger_reason="补充证据"
        )
        print(f"Round 2 初始化成功，父轮次: {metadata2['parent_round']}")

        # 测试5: 列出所有轮次
        print("\n测试5: 列出所有轮次")
        print("-" * 60)
        all_rounds = manager.list_all_rounds()
        for r in all_rounds:
            marker = "← 当前" if r['is_current'] else ""
            print(f"  Round {r['round_number']}: {r['status']} ({r['processing_mode']}) {marker}")

        # 测试6: 回滚
        print("\n测试6: 回滚到Round 1")
        print("-" * 60)
        success, message = manager.rollback_to_round(1)
        print(f"回滚结果: {message}")
        print(f"当前轮次: {manager.get_current_round()}")


if __name__ == "__main__":
    main()
