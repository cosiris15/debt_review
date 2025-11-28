# -*- coding: utf-8 -*-
"""
多轮工作流控制器 - 债权审查系统v3.0核心控制器

集成影响分析器、轮次管理器和现有v2.0控制器，提供完整的多轮交互能力。

设计原则：
- 向后兼容：保持v2.0功能不变
- 组合优于继承：组合使用现有模块
- 保守策略：不确定时倾向Full模式
- 用户友好：清晰的确认机制和进度展示
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.impact_analyzer import ImpactAnalyzer, ImpactAnalysisResult, ProcessingMode
from src.round_manager import RoundManager
from src.migration_tool import MigrationTool
from src.date_validator import DateValidator


class MultiRoundController:
    """多轮工作流控制器 v3.0

    提供完整的多轮交互能力，包括：
    - 轮次初始化和管理
    - 影响分析和处理模式决策
    - Full/Incremental/Partial模式执行
    - 回滚和历史查看
    """

    def __init__(self, project_root: str = "/root/debt_review_skills"):
        """初始化多轮控制器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.output_root = self.project_root / "输出"

        # 组合使用各个模块
        self.impact_analyzer = ImpactAnalyzer(conservative=True)
        self.migration_tool = MigrationTool(project_root)
        self.date_validator = DateValidator(project_root)

    def get_creditor_path(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str
    ) -> Path:
        """获取债权人基础目录路径

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称

        Returns:
            Path: 债权人基础目录
        """
        return self.output_root / f"第{batch_number}批债权" / f"{creditor_number}-{creditor_name}"

    def ensure_round_structure(
        self,
        creditor_path: Path
    ) -> Tuple[bool, str]:
        """确保债权人目录是轮次结构（如果不是则自动迁移）

        Args:
            creditor_path: 债权人目录路径

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 检查是否已经是轮次结构
        if (creditor_path / "round_1").exists():
            return True, "已经是轮次结构"

        # 检查是否是旧格式
        if not (creditor_path / "工作底稿").exists():
            return False, "不是有效的债权人目录"

        # 自动迁移
        print(f"检测到旧格式，正在自动迁移到轮次结构...")
        success, message = self.migration_tool.migrate_single_creditor(
            creditor_path,
            dry_run=False
        )

        return success, message

    def init_round(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        round_number: Optional[int] = None,
        supplemental_file: Optional[str] = None
    ) -> Dict:
        """初始化新轮次

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            round_number: 轮次号（如果为None则自动确定）
            supplemental_file: 补充材料配置文件路径

        Returns:
            Dict: 初始化结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)

        # 确保目录存在
        if not creditor_path.exists():
            return {
                "success": False,
                "message": f"债权人目录不存在: {creditor_path}"
            }

        # 确保是轮次结构
        success, message = self.ensure_round_structure(creditor_path)
        if not success:
            return {"success": False, "message": message}

        # 创建RoundManager实例
        round_manager = RoundManager(creditor_path)

        # 确定轮次号
        if round_number is None:
            current_round = round_manager.get_current_round()
            round_number = current_round + 1

        # 确定处理模式和触发原因
        processing_mode = "full"
        trigger_reason = "用户手动初始化"
        parent_round = round_number - 1 if round_number > 1 else None

        # 如果提供了补充文件，分析影响
        impact_result = None
        if supplemental_file and round_number > 1:
            impact_result = self._analyze_supplemental_impact(
                creditor_path,
                supplemental_file
            )
            if impact_result:
                processing_mode = impact_result.processing_mode.value
                trigger_reason = "补充材料"

        # 初始化轮次
        try:
            metadata = round_manager.initialize_round(
                round_number=round_number,
                parent_round=parent_round,
                processing_mode=processing_mode,
                trigger_reason=trigger_reason
            )

            # 如果有影响分析结果，保存到元数据中
            if impact_result:
                round_manager.update_round_metadata(round_number, {
                    "impact_analysis": impact_result.to_dict()
                })

            return {
                "success": True,
                "message": f"轮次 {round_number} 初始化成功",
                "round_number": round_number,
                "processing_mode": processing_mode,
                "metadata": metadata,
                "impact_analysis": impact_result.to_dict() if impact_result else None
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"初始化失败: {str(e)}"
            }

    def analyze_impact(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        supplemental_file: str
    ) -> Dict:
        """分析补充材料的影响

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            supplemental_file: 补充材料配置文件路径

        Returns:
            Dict: 影响分析结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)

        if not creditor_path.exists():
            return {
                "success": False,
                "message": f"债权人目录不存在: {creditor_path}"
            }

        # 确保是轮次结构
        success, message = self.ensure_round_structure(creditor_path)
        if not success:
            return {"success": False, "message": message}

        # 执行影响分析
        impact_result = self._analyze_supplemental_impact(
            creditor_path,
            supplemental_file
        )

        if impact_result is None:
            return {
                "success": False,
                "message": "影响分析失败"
            }

        return {
            "success": True,
            "impact_analysis": impact_result.to_dict(),
            "summary": impact_result.summary(),
            "recommendations": self.impact_analyzer._generate_recommendations(impact_result)
        }

    def _analyze_supplemental_impact(
        self,
        creditor_path: Path,
        supplemental_file: str
    ) -> Optional[ImpactAnalysisResult]:
        """分析补充材料影响（内部方法）

        Args:
            creditor_path: 债权人基础目录
            supplemental_file: 补充材料配置文件路径

        Returns:
            ImpactAnalysisResult: 影响分析结果，失败返回None
        """
        try:
            # 读取补充材料配置
            supplemental_path = Path(supplemental_file)
            if not supplemental_path.is_absolute():
                supplemental_path = creditor_path / supplemental_path

            if not supplemental_path.exists():
                print(f"⚠️  补充材料文件不存在: {supplemental_path}")
                return None

            with open(supplemental_path, 'r', encoding='utf-8') as f:
                supplemental_data = json.load(f)

            # 读取前轮配置
            round_manager = RoundManager(creditor_path)
            current_round = round_manager.get_current_round()

            if current_round == 0:
                print(f"⚠️  当前没有有效轮次，无法分析影响")
                return None

            previous_config_file = creditor_path / f"round_{current_round}" / ".processing_config.json"

            previous_config = {}
            if previous_config_file.exists():
                with open(previous_config_file, 'r', encoding='utf-8') as f:
                    previous_config = json.load(f)

            # 执行影响分析
            impact_result = self.impact_analyzer.compare_configs(
                previous_config,
                supplemental_data
            )

            return impact_result

        except Exception as e:
            print(f"影响分析失败: {e}")
            return None

    def process_round_full(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        round_number: int
    ) -> Dict:
        """处理指定轮次（Full模式）

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            round_number: 轮次号

        Returns:
            Dict: 处理结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        # 验证轮次存在
        if not round_manager.round_exists(round_number):
            return {
                "success": False,
                "message": f"轮次 {round_number} 不存在"
            }

        print(f"\n{'='*60}")
        print(f"开始处理 Round {round_number}（Full模式）")
        print(f"债权人: {creditor_name}")
        print(f"{'='*60}\n")

        # 🔒 检查点 0: 日期一致性强制验证
        print(f"[0/3] 检查点 0: 日期一致性验证")
        try:
            self.date_validator.enforce_validation(
                creditor_path,
                round_number,
                stage_name=f"Round {round_number} 处理"
            )
        except ValueError as e:
            return {
                "success": False,
                "message": str(e),
                "round_number": round_number,
                "error_type": "date_validation_failed"
            }

        # 标记状态为处理中
        round_manager.mark_round_status(round_number, "processing")

        try:
            # 获取轮次路径
            round_path = round_manager.get_round_path(round_number)

            # 生成处理配置（传递给Agent）
            processing_config = self._generate_round_processing_config(
                creditor_path,
                round_number,
                ProcessingMode.FULL
            )

            # 保存配置到round目录
            config_file = round_path / ".processing_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(processing_config, f, ensure_ascii=False, indent=2)

            # Stage 1: 事实核查
            print(f"[1/3] Stage 1: 事实核查")
            stage1_result = self._execute_stage1_full(
                creditor_path,
                round_number,
                processing_config
            )

            if not stage1_result["success"]:
                raise Exception(f"Stage 1失败: {stage1_result['message']}")

            # Stage 2: 债权分析
            print(f"\n[2/3] Stage 2: 债权分析")
            stage2_result = self._execute_stage2_full(
                creditor_path,
                round_number,
                processing_config
            )

            if not stage2_result["success"]:
                raise Exception(f"Stage 2失败: {stage2_result['message']}")

            # Stage 3: 报告整理
            print(f"\n[3/3] Stage 3: 报告整理")
            stage3_result = self._execute_stage3_full(
                creditor_path,
                round_number,
                processing_config
            )

            if not stage3_result["success"]:
                raise Exception(f"Stage 3失败: {stage3_result['message']}")

            # 更新轮次元数据
            round_manager.update_round_metadata(round_number, {
                "status": "completed",
                "processing_summary": {
                    "stages_executed": [1, 2, 3],
                    "stages_skipped": [],
                    "time_saved_percent": 0,
                    "completed_at": datetime.now().isoformat()
                },
                "agent_execution": {
                    "stage1": stage1_result,
                    "stage2": stage2_result,
                    "stage3": stage3_result
                }
            })

            print(f"\n{'='*60}")
            print(f"✅ Round {round_number} 处理完成！")
            print(f"{'='*60}\n")

            return {
                "success": True,
                "message": f"Round {round_number} 处理完成",
                "round_number": round_number,
                "processing_mode": "full",
                "stages_executed": [1, 2, 3]
            }

        except Exception as e:
            # 标记失败
            round_manager.mark_round_status(round_number, "failed")

            return {
                "success": False,
                "message": f"处理失败: {str(e)}",
                "round_number": round_number
            }

    def process_round_incremental(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        round_number: int,
        impact_result: ImpactAnalysisResult
    ) -> Dict:
        """处理指定轮次（Incremental模式）

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            round_number: 轮次号
            impact_result: 影响分析结果

        Returns:
            Dict: 处理结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        # 验证轮次存在
        if not round_manager.round_exists(round_number):
            return {
                "success": False,
                "message": f"轮次 {round_number} 不存在"
            }

        print(f"\n{'='*60}")
        print(f"开始处理 Round {round_number}（Incremental模式）")
        print(f"债权人: {creditor_name}")
        print(f"受影响章节: 第{', '.join(map(str, impact_result.affected_sections))}章")
        print(f"受影响债权项: {', '.join(impact_result.affected_debt_items[:5])}")
        if len(impact_result.affected_debt_items) > 5:
            print(f"              (共{len(impact_result.affected_debt_items)}项)")
        print(f"预计节省时间: {impact_result.time_savings_percent}%")
        print(f"{'='*60}\n")

        # 🔒 检查点 0: 日期一致性强制验证
        print(f"[0/3] 检查点 0: 日期一致性验证")
        try:
            self.date_validator.enforce_validation(
                creditor_path,
                round_number,
                stage_name=f"Round {round_number} 增量处理"
            )
        except ValueError as e:
            return {
                "success": False,
                "message": str(e),
                "round_number": round_number,
                "error_type": "date_validation_failed"
            }

        # 标记状态为处理中
        round_manager.mark_round_status(round_number, "processing")

        try:
            # 获取轮次路径
            round_path = round_manager.get_round_path(round_number)

            # 生成处理配置（包含影响分析信息）
            processing_config = self._generate_round_processing_config(
                creditor_path,
                round_number,
                ProcessingMode.INCREMENTAL,
                impact_result
            )

            # 保存配置到round目录
            config_file = round_path / ".processing_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(processing_config, f, ensure_ascii=False, indent=2)

            # 确定需要执行的阶段
            stages_to_execute = impact_result.affected_stages
            stages_skipped = [s for s in [1, 2, 3] if s not in stages_to_execute]

            # Stage 1: 事实核查（如果受影响）
            stage1_result = {"success": True, "skipped": True}
            if 1 in stages_to_execute:
                print(f"[1/3] Stage 1: 事实核查（增量模式）")
                stage1_result = self._execute_stage1_incremental(
                    creditor_path,
                    round_number,
                    processing_config
                )

                if not stage1_result["success"]:
                    raise Exception(f"Stage 1失败: {stage1_result['message']}")
            else:
                print(f"[1/3] Stage 1: 事实核查（跳过 - 未受影响）")

            # Stage 2: 债权分析（如果受影响）
            stage2_result = {"success": True, "skipped": True}
            if 2 in stages_to_execute:
                print(f"\n[2/3] Stage 2: 债权分析（增量模式）")
                stage2_result = self._execute_stage2_incremental(
                    creditor_path,
                    round_number,
                    processing_config
                )

                if not stage2_result["success"]:
                    raise Exception(f"Stage 2失败: {stage2_result['message']}")
            else:
                print(f"\n[2/3] Stage 2: 债权分析（跳过 - 未受影响）")

            # Stage 3: 报告整理（如果受影响）
            stage3_result = {"success": True, "skipped": True}
            if 3 in stages_to_execute:
                print(f"\n[3/3] Stage 3: 报告整理（增量模式）")
                stage3_result = self._execute_stage3_incremental(
                    creditor_path,
                    round_number,
                    processing_config
                )

                if not stage3_result["success"]:
                    raise Exception(f"Stage 3失败: {stage3_result['message']}")
            else:
                print(f"\n[3/3] Stage 3: 报告整理（跳过 - 未受影响）")

            # 更新轮次元数据
            round_manager.update_round_metadata(round_number, {
                "status": "completed",
                "processing_summary": {
                    "stages_executed": stages_to_execute,
                    "stages_skipped": stages_skipped,
                    "time_saved_percent": impact_result.time_savings_percent,
                    "completed_at": datetime.now().isoformat()
                },
                "agent_execution": {
                    "stage1": stage1_result,
                    "stage2": stage2_result,
                    "stage3": stage3_result
                },
                "impact_analysis": impact_result.to_dict()
            })

            print(f"\n{'='*60}")
            print(f"✅ Round {round_number} 处理完成！")
            print(f"节省时间: {impact_result.time_savings_percent}%")
            print(f"{'='*60}\n")

            return {
                "success": True,
                "message": f"Round {round_number} 处理完成（增量模式）",
                "round_number": round_number,
                "processing_mode": "incremental",
                "stages_executed": stages_to_execute,
                "stages_skipped": stages_skipped,
                "time_savings_percent": impact_result.time_savings_percent
            }

        except Exception as e:
            # 标记失败
            round_manager.mark_round_status(round_number, "failed")

            return {
                "success": False,
                "message": f"处理失败: {str(e)}",
                "round_number": round_number
            }

    def _generate_round_processing_config(
        self,
        creditor_path: Path,
        round_number: int,
        processing_mode: ProcessingMode,
        impact_result: Optional[ImpactAnalysisResult] = None
    ) -> Dict:
        """生成轮次处理配置（传递给Agent）

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            processing_mode: 处理模式
            impact_result: 影响分析结果（Incremental/Partial模式需要）

        Returns:
            Dict: 处理配置
        """
        round_manager = RoundManager(creditor_path)
        round_path = round_manager.get_round_path(round_number)
        parent_round = round_number - 1 if round_number > 1 else None

        # 读取项目配置（破产日期等）
        project_config_file = self.project_root / "project_config.ini"
        bankruptcy_date = "2024-12-31"  # 默认值
        interest_stop_date = "2024-12-30"

        if project_config_file.exists():
            import configparser
            config = configparser.ConfigParser()
            config.read(project_config_file, encoding='utf-8')
            if 'project' in config:
                bankruptcy_date = config['project'].get('bankruptcy_date', bankruptcy_date)
                interest_stop_date = config['project'].get('interest_stop_date', interest_stop_date)

        config = {
            "round_info": {
                "round_number": round_number,
                "processing_mode": processing_mode.value,
                "is_first_round": round_number == 1,
                "parent_round": parent_round
            },
            "paths": {
                "base_directory": str(creditor_path),
                "round_directory": str(round_path),
                "input_materials": str(round_path / "输入材料"),
                "work_papers": str(round_path / "工作底稿"),
                "final_reports": str(round_path / "最终报告"),
                "calculation_files": str(round_path / "计算文件")
            },
            "bankruptcy_info": {
                "bankruptcy_date": bankruptcy_date,
                "interest_stop_date": interest_stop_date
            },
            "processing_date": datetime.now().strftime("%Y%m%d")
        }

        # 如果是Incremental或Partial模式，添加增量处理信息
        if processing_mode in [ProcessingMode.INCREMENTAL, ProcessingMode.PARTIAL] and impact_result:
            # 添加前轮信息
            if parent_round:
                parent_round_path = round_manager.get_round_path(parent_round)
                config["previous_round"] = {
                    "round_number": parent_round,
                    "round_directory": str(parent_round_path),
                    "work_papers": str(parent_round_path / "工作底稿"),
                    "final_reports": str(parent_round_path / "最终报告"),
                    "calculation_files": str(parent_round_path / "计算文件")
                }

            # 添加影响分析结果
            config["impact_analysis"] = {
                "fields_updated": impact_result.fields_updated,
                "affected_stages": impact_result.affected_stages,
                "affected_sections": impact_result.affected_sections,
                "affected_debt_items": impact_result.affected_debt_items,
                "highest_priority": impact_result.highest_priority,
                "reasoning": impact_result.reasoning
            }

        return config

    def _execute_stage1_full(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 1（Full模式）- 准备Agent调用配置

        此方法准备debt-fact-checker Agent所需的所有配置和上下文。
        实际的Agent调用需要在Claude Code CLI层面通过Task工具完成。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 1: 事实核查")

        round_path = Path(config["paths"]["round_directory"])
        input_dir = round_path / "输入材料"
        work_dir = round_path / "工作底稿"

        # 检查输入材料是否存在
        if not input_dir.exists() or not any(input_dir.iterdir()):
            print(f"  └─ ⚠️  警告: 输入材料目录为空")

        # 准备Agent调用配置
        agent_config = {
            "subagent_type": "debt-fact-checker",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "task_description": f"事实核查 - Round {round_number}",
            "expected_output": work_dir / f"事实核查报告_round{round_number}.md"
        }

        print(f"  ├─ 输入材料: {input_dir}")
        print(f"  ├─ 输出目录: {work_dir}")
        print(f"  ├─ 破产日期: {config['bankruptcy_info']['bankruptcy_date']}")
        print(f"  └─ ✅ Stage 1 配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 1配置已准备，等待Agent调用",
            "stage": 1
        }

    def _execute_stage2_full(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 2（Full模式）- 准备Agent调用配置

        此方法准备debt-claim-analyzer Agent所需的所有配置和上下文。
        实际的Agent调用需要在Claude Code CLI层面通过Task工具完成。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 2: 债权分析")

        round_path = Path(config["paths"]["round_directory"])
        work_dir = round_path / "工作底稿"
        calc_dir = round_path / "计算文件"

        # 检查前置条件：事实核查报告必须存在
        fact_report = work_dir / f"事实核查报告_round{round_number}.md"
        if not fact_report.exists():
            # 查找任何事实核查报告
            fact_reports = list(work_dir.glob("*事实核查*.md"))
            if not fact_reports:
                print(f"  └─ ❌ 错误: 事实核查报告不存在")
                return {
                    "success": False,
                    "message": "前置条件未满足：事实核查报告不存在"
                }

        # 准备Agent调用配置
        agent_config = {
            "subagent_type": "debt-claim-analyzer",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "task_description": f"债权分析 - Round {round_number}",
            "expected_outputs": {
                "analysis_report": work_dir / f"债权分析报告_round{round_number}.md",
                "calculation_files": calc_dir
            }
        }

        print(f"  ├─ 输入: 事实核查报告")
        print(f"  ├─ 输出目录: {work_dir}, {calc_dir}")
        print(f"  ├─ 停止计息日: {config['bankruptcy_info']['interest_stop_date']}")
        print(f"  └─ ✅ Stage 2 配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 2配置已准备，等待Agent调用",
            "stage": 2
        }

    def _execute_stage3_full(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 3（Full模式）- 准备Agent调用配置

        此方法准备report-organizer Agent所需的所有配置和上下文。
        实际的Agent调用需要在Claude Code CLI层面通过Task工具完成。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 3: 报告整理")

        round_path = Path(config["paths"]["round_directory"])
        work_dir = round_path / "工作底稿"
        final_dir = round_path / "最终报告"

        # 检查前置条件：两个技术报告必须存在
        required_reports = [
            work_dir / f"事实核查报告_round{round_number}.md",
            work_dir / f"债权分析报告_round{round_number}.md"
        ]

        missing_reports = []
        for report in required_reports:
            if not report.exists():
                # 尝试查找任何相关报告
                pattern = report.name.split("_round")[0]
                found = list(work_dir.glob(f"{pattern}*.md"))
                if not found:
                    missing_reports.append(report.name)

        if missing_reports:
            print(f"  └─ ❌ 错误: 缺少报告 {', '.join(missing_reports)}")
            return {
                "success": False,
                "message": f"前置条件未满足：缺少 {', '.join(missing_reports)}"
            }

        # 准备Agent调用配置
        agent_config = {
            "subagent_type": "report-organizer",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "task_description": f"报告整理 - Round {round_number}",
            "expected_outputs": {
                "final_report": final_dir / f"GY2025_审查报告_round{round_number}_{config['processing_date']}.md",
                "file_inventory": creditor_path / "文件清单.md"
            }
        }

        print(f"  ├─ 输入: 事实核查报告 + 债权分析报告")
        print(f"  ├─ 输出目录: {final_dir}")
        print(f"  └─ ✅ Stage 3 配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 3配置已准备，等待Agent调用",
            "stage": 3
        }

    def process_round_partial(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        round_number: int,
        impact_result: ImpactAnalysisResult
    ) -> Dict:
        """处理指定轮次（Partial模式）

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            round_number: 轮次号
            impact_result: 影响分析结果

        Returns:
            Dict: 处理结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        # 验证轮次存在
        if not round_manager.round_exists(round_number):
            return {
                "success": False,
                "message": f"轮次 {round_number} 不存在"
            }

        print(f"\n{'='*60}")
        print(f"开始处理 Round {round_number}（Partial模式）")
        print(f"债权人: {creditor_name}")
        print(f"变更字段: {', '.join(impact_result.fields_updated)}")
        print(f"字段级更新 - 最小单元处理")
        print(f"预计节省时间: {impact_result.time_savings_percent}%")
        print(f"{'='*60}\n")

        # 🔒 检查点 0: 日期一致性强制验证
        print(f"[0/3] 检查点 0: 日期一致性验证")
        try:
            self.date_validator.enforce_validation(
                creditor_path,
                round_number,
                stage_name=f"Round {round_number} Partial处理"
            )
        except ValueError as e:
            return {
                "success": False,
                "message": str(e),
                "round_number": round_number,
                "error_type": "date_validation_failed"
            }

        # 标记状态为处理中
        round_manager.mark_round_status(round_number, "processing")

        try:
            # 获取轮次路径
            round_path = round_manager.get_round_path(round_number)

            # 生成处理配置（包含影响分析信息）
            processing_config = self._generate_round_processing_config(
                creditor_path,
                round_number,
                ProcessingMode.PARTIAL,
                impact_result
            )

            # 保存配置到round目录
            config_file = round_path / ".processing_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(processing_config, f, ensure_ascii=False, indent=2)

            # 确定需要执行的阶段（Partial模式通常需要更新所有Stage以保持一致性）
            stages_to_execute = impact_result.affected_stages
            stages_skipped = [s for s in [1, 2, 3] if s not in stages_to_execute]

            # Stage 1: 事实核查（字段级更新）
            stage1_result = {"success": True, "skipped": True}
            if 1 in stages_to_execute:
                print(f"[1/3] Stage 1: 事实核查（字段级更新）")
                stage1_result = self._execute_stage1_partial(
                    creditor_path,
                    round_number,
                    processing_config
                )

                if not stage1_result["success"]:
                    raise Exception(f"Stage 1失败: {stage1_result['message']}")
            else:
                print(f"[1/3] Stage 1: 事实核查（跳过 - 未受影响）")

            # Stage 2: 债权分析（字段级更新）
            stage2_result = {"success": True, "skipped": True}
            if 2 in stages_to_execute:
                print(f"\n[2/3] Stage 2: 债权分析（字段级更新）")
                stage2_result = self._execute_stage2_partial(
                    creditor_path,
                    round_number,
                    processing_config
                )

                if not stage2_result["success"]:
                    raise Exception(f"Stage 2失败: {stage2_result['message']}")
            else:
                print(f"\n[2/3] Stage 2: 债权分析（跳过 - 未受影响）")

            # Stage 3: 报告整理（字段级更新）
            stage3_result = {"success": True, "skipped": True}
            if 3 in stages_to_execute:
                print(f"\n[3/3] Stage 3: 报告整理（字段级更新）")
                stage3_result = self._execute_stage3_partial(
                    creditor_path,
                    round_number,
                    processing_config
                )

                if not stage3_result["success"]:
                    raise Exception(f"Stage 3失败: {stage3_result['message']}")
            else:
                print(f"\n[3/3] Stage 3: 报告整理（跳过 - 未受影响）")

            # 更新轮次元数据
            round_manager.update_round_metadata(round_number, {
                "status": "completed",
                "processing_summary": {
                    "stages_executed": stages_to_execute,
                    "stages_skipped": stages_skipped,
                    "time_saved_percent": impact_result.time_savings_percent,
                    "completed_at": datetime.now().isoformat()
                },
                "agent_execution": {
                    "stage1": stage1_result,
                    "stage2": stage2_result,
                    "stage3": stage3_result
                },
                "impact_analysis": impact_result.to_dict()
            })

            print(f"\n{'='*60}")
            print(f"✅ Round {round_number} 处理完成！")
            print(f"节省时间: {impact_result.time_savings_percent}%")
            print(f"{'='*60}\n")

            return {
                "success": True,
                "message": f"Round {round_number} 处理完成（Partial模式）",
                "round_number": round_number,
                "processing_mode": "partial",
                "stages_executed": stages_to_execute,
                "stages_skipped": stages_skipped,
                "time_savings_percent": impact_result.time_savings_percent
            }

        except Exception as e:
            # 标记失败
            round_manager.mark_round_status(round_number, "failed")

            return {
                "success": False,
                "message": f"处理失败: {str(e)}",
                "round_number": round_number
            }

    def _execute_stage1_incremental(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 1（Incremental模式）- 准备Agent调用配置

        此方法准备debt-fact-checker Agent所需的增量处理配置。
        Agent将根据affected_sections信息继承未受影响章节，重新核查受影响章节。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置（包含影响分析信息）

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 1: 事实核查（增量模式）")

        round_path = Path(config["paths"]["round_directory"])
        input_dir = round_path / "输入材料"
        work_dir = round_path / "工作底稿"

        # 检查前轮报告是否存在
        if "previous_round" not in config:
            print(f"  └─ ⚠️  警告: 未找到前轮信息，将回退到Full模式")
            return self._execute_stage1_full(creditor_path, round_number, config)

        previous_work_dir = Path(config["previous_round"]["work_papers"])
        previous_reports = list(previous_work_dir.glob("*事实核查*.md"))

        if not previous_reports:
            print(f"  └─ ⚠️  警告: 前轮事实核查报告不存在，将回退到Full模式")
            return self._execute_stage1_full(creditor_path, round_number, config)

        # 准备Agent调用配置（增量模式）
        agent_config = {
            "subagent_type": "debt-fact-checker",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "previous_round": config["previous_round"],
            "incremental_info": {
                "processing_mode": "incremental",
                "affected_sections": config["impact_analysis"]["affected_sections"],
                "fields_updated": config["impact_analysis"]["fields_updated"],
                "previous_report": str(previous_reports[0])
            },
            "task_description": f"事实核查（增量模式）- Round {round_number}",
            "expected_output": work_dir / f"事实核查报告_round{round_number}.md"
        }

        print(f"  ├─ 前轮报告: {previous_reports[0].name}")
        print(f"  ├─ 受影响章节: 第{', '.join(map(str, config['impact_analysis']['affected_sections']))}章")
        print(f"  ├─ 输入材料: {input_dir}")
        print(f"  ├─ 输出目录: {work_dir}")
        print(f"  └─ ✅ Stage 1 增量配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 1增量配置已准备，等待Agent调用",
            "stage": 1,
            "mode": "incremental"
        }

    def _execute_stage2_incremental(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 2（Incremental模式）- 准备Agent调用配置

        此方法准备debt-claim-analyzer Agent所需的增量处理配置。
        Agent将根据affected_debt_items信息继承未受影响债权项，重新分析受影响债权项。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置（包含影响分析信息）

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 2: 债权分析（增量模式）")

        round_path = Path(config["paths"]["round_directory"])
        work_dir = round_path / "工作底稿"
        calc_dir = round_path / "计算文件"

        # 检查前置条件：事实核查报告必须存在
        fact_report = work_dir / f"事实核查报告_round{round_number}.md"
        if not fact_report.exists():
            fact_reports = list(work_dir.glob("*事实核查*.md"))
            if not fact_reports:
                print(f"  └─ ❌ 错误: 事实核查报告不存在")
                return {
                    "success": False,
                    "message": "前置条件未满足：事实核查报告不存在"
                }

        # 检查前轮报告是否存在
        if "previous_round" not in config:
            print(f"  └─ ⚠️  警告: 未找到前轮信息，将回退到Full模式")
            return self._execute_stage2_full(creditor_path, round_number, config)

        previous_work_dir = Path(config["previous_round"]["work_papers"])
        previous_calc_dir = Path(config["previous_round"]["calculation_files"])

        previous_analysis_reports = list(previous_work_dir.glob("*债权分析*.md"))

        if not previous_analysis_reports:
            print(f"  └─ ⚠️  警告: 前轮债权分析报告不存在，将回退到Full模式")
            return self._execute_stage2_full(creditor_path, round_number, config)

        # 准备Agent调用配置（增量模式）
        agent_config = {
            "subagent_type": "debt-claim-analyzer",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "previous_round": config["previous_round"],
            "incremental_info": {
                "processing_mode": "incremental",
                "affected_debt_items": config["impact_analysis"]["affected_debt_items"],
                "fields_updated": config["impact_analysis"]["fields_updated"],
                "previous_analysis_report": str(previous_analysis_reports[0]),
                "previous_calculation_directory": str(previous_calc_dir)
            },
            "task_description": f"债权分析（增量模式）- Round {round_number}",
            "expected_outputs": {
                "analysis_report": work_dir / f"债权分析报告_round{round_number}.md",
                "calculation_files": calc_dir
            }
        }

        print(f"  ├─ 前轮分析报告: {previous_analysis_reports[0].name}")
        print(f"  ├─ 受影响债权项: {', '.join(config['impact_analysis']['affected_debt_items'][:5])}")
        if len(config['impact_analysis']['affected_debt_items']) > 5:
            print(f"  │               (共{len(config['impact_analysis']['affected_debt_items'])}项)")
        print(f"  ├─ 输出目录: {work_dir}, {calc_dir}")
        print(f"  └─ ✅ Stage 2 增量配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 2增量配置已准备，等待Agent调用",
            "stage": 2,
            "mode": "incremental"
        }

    def _execute_stage3_incremental(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 3（Incremental模式）- 准备Agent调用配置

        此方法准备report-organizer Agent所需的增量处理配置。
        Agent将根据affected_sections信息继承未受影响章节，重新整理受影响章节。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置（包含影响分析信息）

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 3: 报告整理（增量模式）")

        round_path = Path(config["paths"]["round_directory"])
        work_dir = round_path / "工作底稿"
        final_dir = round_path / "最终报告"

        # 检查前置条件：两个技术报告必须存在
        required_reports = [
            work_dir / f"事实核查报告_round{round_number}.md",
            work_dir / f"债权分析报告_round{round_number}.md"
        ]

        missing_reports = []
        for report in required_reports:
            if not report.exists():
                pattern = report.name.split("_round")[0]
                found = list(work_dir.glob(f"{pattern}*.md"))
                if not found:
                    missing_reports.append(report.name)

        if missing_reports:
            print(f"  └─ ❌ 错误: 缺少报告 {', '.join(missing_reports)}")
            return {
                "success": False,
                "message": f"前置条件未满足：缺少 {', '.join(missing_reports)}"
            }

        # 检查前轮报告是否存在
        if "previous_round" not in config:
            print(f"  └─ ⚠️  警告: 未找到前轮信息，将回退到Full模式")
            return self._execute_stage3_full(creditor_path, round_number, config)

        previous_final_dir = Path(config["previous_round"]["final_reports"])
        previous_final_reports = list(previous_final_dir.glob("GY2025_*.md"))

        if not previous_final_reports:
            print(f"  └─ ⚠️  警告: 前轮最终报告不存在，将回退到Full模式")
            return self._execute_stage3_full(creditor_path, round_number, config)

        # 准备Agent调用配置（增量模式）
        agent_config = {
            "subagent_type": "report-organizer",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "previous_round": config["previous_round"],
            "incremental_info": {
                "processing_mode": "incremental",
                "affected_sections": config["impact_analysis"]["affected_sections"],
                "fields_updated": config["impact_analysis"]["fields_updated"],
                "previous_final_report": str(previous_final_reports[0])
            },
            "task_description": f"报告整理（增量模式）- Round {round_number}",
            "expected_outputs": {
                "final_report": final_dir / f"GY2025_审查报告_round{round_number}_{config['processing_date']}.md",
                "file_inventory": creditor_path / "文件清单.md"
            }
        }

        print(f"  ├─ 前轮最终报告: {previous_final_reports[0].name}")
        print(f"  ├─ 受影响章节: 第{', '.join(map(str, config['impact_analysis']['affected_sections']))}章")
        print(f"  ├─ 输出目录: {final_dir}")
        print(f"  └─ ✅ Stage 3 增量配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 3增量配置已准备，等待Agent调用",
            "stage": 3,
            "mode": "incremental"
        }

    def _execute_stage1_partial(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 1（Partial模式）- 准备Agent调用配置

        此方法准备debt-fact-checker Agent所需的字段级更新配置。
        Agent将根据fields_updated信息进行最小单元更新。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置（包含影响分析信息）

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 1: 事实核查（字段级更新）")

        round_path = Path(config["paths"]["round_directory"])
        input_dir = round_path / "输入材料"
        work_dir = round_path / "工作底稿"

        # 检查前轮报告是否存在
        if "previous_round" not in config:
            print(f"  └─ ⚠️  警告: 未找到前轮信息，将回退到Full模式")
            return self._execute_stage1_full(creditor_path, round_number, config)

        previous_work_dir = Path(config["previous_round"]["work_papers"])
        previous_reports = list(previous_work_dir.glob("*事实核查*.md"))

        if not previous_reports:
            print(f"  └─ ⚠️  警告: 前轮事实核查报告不存在，将回退到Full模式")
            return self._execute_stage1_full(creditor_path, round_number, config)

        # 准备Agent调用配置（Partial模式）
        agent_config = {
            "subagent_type": "debt-fact-checker",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "previous_round": config["previous_round"],
            "incremental_info": {
                "processing_mode": "partial",
                "fields_updated": config["impact_analysis"]["fields_updated"],
                "affected_sections": config["impact_analysis"]["affected_sections"],
                "previous_report": str(previous_reports[0])
            },
            "task_description": f"事实核查（字段级更新）- Round {round_number}",
            "expected_output": work_dir / f"事实核查报告_round{round_number}.md"
        }

        print(f"  ├─ 前轮报告: {previous_reports[0].name}")
        print(f"  ├─ 变更字段: {', '.join(config['impact_analysis']['fields_updated'])}")
        print(f"  ├─ 处理方式: 字段级最小更新")
        print(f"  ├─ 输出目录: {work_dir}")
        print(f"  └─ ✅ Stage 1 Partial配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 1 Partial配置已准备，等待Agent调用",
            "stage": 1,
            "mode": "partial"
        }

    def _execute_stage2_partial(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 2（Partial模式）- 准备Agent调用配置

        此方法准备debt-claim-analyzer Agent所需的字段级更新配置。
        Agent将根据fields_updated信息进行最小单元更新。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置（包含影响分析信息）

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 2: 债权分析（字段级更新）")

        round_path = Path(config["paths"]["round_directory"])
        work_dir = round_path / "工作底稿"
        calc_dir = round_path / "计算文件"

        # 检查前置条件：事实核查报告必须存在
        fact_report = work_dir / f"事实核查报告_round{round_number}.md"
        if not fact_report.exists():
            fact_reports = list(work_dir.glob("*事实核查*.md"))
            if not fact_reports:
                print(f"  └─ ❌ 错误: 事实核查报告不存在")
                return {
                    "success": False,
                    "message": "前置条件未满足：事实核查报告不存在"
                }

        # 检查前轮报告是否存在
        if "previous_round" not in config:
            print(f"  └─ ⚠️  警告: 未找到前轮信息，将回退到Full模式")
            return self._execute_stage2_full(creditor_path, round_number, config)

        previous_work_dir = Path(config["previous_round"]["work_papers"])
        previous_calc_dir = Path(config["previous_round"]["calculation_files"])

        previous_analysis_reports = list(previous_work_dir.glob("*债权分析*.md"))

        if not previous_analysis_reports:
            print(f"  └─ ⚠️  警告: 前轮债权分析报告不存在，将回退到Full模式")
            return self._execute_stage2_full(creditor_path, round_number, config)

        # 准备Agent调用配置（Partial模式）
        agent_config = {
            "subagent_type": "debt-claim-analyzer",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "previous_round": config["previous_round"],
            "incremental_info": {
                "processing_mode": "partial",
                "fields_updated": config["impact_analysis"]["fields_updated"],
                "affected_debt_items": config["impact_analysis"]["affected_debt_items"],
                "previous_analysis_report": str(previous_analysis_reports[0]),
                "previous_calculation_directory": str(previous_calc_dir)
            },
            "task_description": f"债权分析（字段级更新）- Round {round_number}",
            "expected_outputs": {
                "analysis_report": work_dir / f"债权分析报告_round{round_number}.md",
                "calculation_files": calc_dir
            }
        }

        print(f"  ├─ 前轮分析报告: {previous_analysis_reports[0].name}")
        print(f"  ├─ 变更字段: {', '.join(config['impact_analysis']['fields_updated'])}")
        print(f"  ├─ 处理方式: 字段级最小更新")
        print(f"  ├─ 输出目录: {work_dir}, {calc_dir}")
        print(f"  └─ ✅ Stage 2 Partial配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 2 Partial配置已准备，等待Agent调用",
            "stage": 2,
            "mode": "partial"
        }

    def _execute_stage3_partial(
        self,
        creditor_path: Path,
        round_number: int,
        config: Dict
    ) -> Dict:
        """执行Stage 3（Partial模式）- 准备Agent调用配置

        此方法准备report-organizer Agent所需的字段级更新配置。
        Agent将根据fields_updated信息进行最小单元更新。

        Args:
            creditor_path: 债权人基础目录
            round_number: 轮次号
            config: 处理配置（包含影响分析信息）

        Returns:
            Dict: 执行结果，包含agent_call_required标志和配置
        """
        print(f"  ├─ 准备Stage 3: 报告整理（字段级更新）")

        round_path = Path(config["paths"]["round_directory"])
        work_dir = round_path / "工作底稿"
        final_dir = round_path / "最终报告"

        # 检查前置条件：两个技术报告必须存在
        required_reports = [
            work_dir / f"事实核查报告_round{round_number}.md",
            work_dir / f"债权分析报告_round{round_number}.md"
        ]

        missing_reports = []
        for report in required_reports:
            if not report.exists():
                pattern = report.name.split("_round")[0]
                found = list(work_dir.glob(f"{pattern}*.md"))
                if not found:
                    missing_reports.append(report.name)

        if missing_reports:
            print(f"  └─ ❌ 错误: 缺少报告 {', '.join(missing_reports)}")
            return {
                "success": False,
                "message": f"前置条件未满足：缺少 {', '.join(missing_reports)}"
            }

        # 检查前轮报告是否存在
        if "previous_round" not in config:
            print(f"  └─ ⚠️  警告: 未找到前轮信息，将回退到Full模式")
            return self._execute_stage3_full(creditor_path, round_number, config)

        previous_final_dir = Path(config["previous_round"]["final_reports"])
        previous_final_reports = list(previous_final_dir.glob("GY2025_*.md"))

        if not previous_final_reports:
            print(f"  └─ ⚠️  警告: 前轮最终报告不存在，将回退到Full模式")
            return self._execute_stage3_full(creditor_path, round_number, config)

        # 准备Agent调用配置（Partial模式）
        agent_config = {
            "subagent_type": "report-organizer",
            "round_info": config["round_info"],
            "paths": config["paths"],
            "bankruptcy_info": config["bankruptcy_info"],
            "previous_round": config["previous_round"],
            "incremental_info": {
                "processing_mode": "partial",
                "fields_updated": config["impact_analysis"]["fields_updated"],
                "affected_sections": config["impact_analysis"]["affected_sections"],
                "previous_final_report": str(previous_final_reports[0])
            },
            "task_description": f"报告整理（字段级更新）- Round {round_number}",
            "expected_outputs": {
                "final_report": final_dir / f"GY2025_审查报告_round{round_number}_{config['processing_date']}.md",
                "file_inventory": creditor_path / "文件清单.md"
            }
        }

        print(f"  ├─ 前轮最终报告: {previous_final_reports[0].name}")
        print(f"  ├─ 变更字段: {', '.join(config['impact_analysis']['fields_updated'])}")
        print(f"  ├─ 处理方式: 字段级最小更新")
        print(f"  ├─ 输出目录: {final_dir}")
        print(f"  └─ ✅ Stage 3 Partial配置准备完成")

        return {
            "success": True,
            "agent_call_required": True,
            "agent_config": agent_config,
            "message": "Stage 3 Partial配置已准备，等待Agent调用",
            "stage": 3,
            "mode": "partial"
        }

    def rollback_to_round(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        target_round: int,
        reason: str = ""
    ) -> Dict:
        """回滚到指定轮次

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            target_round: 目标轮次号
            reason: 回滚原因

        Returns:
            Dict: 回滚结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        success, message = round_manager.rollback_to_round(target_round, reason)

        result = {
            "success": success,
            "message": message,
            "current_round": round_manager.get_current_round() if success else None
        }

        # 如果成功，显示回滚后的历史
        if success:
            print("\n回滚成功！当前轮次历史：")
            round_manager.print_history(include_rolled_back=True)

        return result

    def show_history(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        include_rolled_back: bool = True
    ) -> Dict:
        """显示轮次历史

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            include_rolled_back: 是否包含已回滚的轮次

        Returns:
            Dict: 历史信息
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        # 使用增强的历史查看功能
        history = round_manager.get_history(include_rolled_back)

        # 打印格式化历史（用于命令行）
        round_manager.print_history(include_rolled_back)

        return {
            "success": True,
            **history
        }

    def show_changelog(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str
    ) -> Dict:
        """显示变更日志

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称

        Returns:
            Dict: Changelog信息
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        # 读取changelog
        changelog = round_manager.read_changelog()

        # 打印格式化的changelog
        print("\n" + round_manager.generate_changelog_summary())

        return {
            "success": True,
            "changelog": changelog
        }

    def generate_checklist(
        self,
        batch_number: int,
        creditor_number: int,
        creditor_name: str,
        round_number: int
    ) -> Dict:
        """生成补充材料清单

        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            round_number: 轮次号

        Returns:
            Dict: 清单生成结果
        """
        creditor_path = self.get_creditor_path(batch_number, creditor_number, creditor_name)
        round_manager = RoundManager(creditor_path)

        # 生成补充清单
        result = round_manager.generate_supplemental_checklist(round_number)

        if result["success"]:
            print(f"\n✅ 补充材料清单已生成:")
            print(f"  文件位置: {result['checklist_file']}")
            print(f"  字段数量: {result['fields_count']}")
            print(f"  优先级分布:")
            for priority, count in result["categorized_fields"].items():
                print(f"    {priority}: {count}个")
        else:
            print(f"\n❌ 生成失败: {result['message']}")

        return result

    # ========== 批量处理优化功能 ==========

    def list_creditors_in_batch(self, batch_number: int) -> List[Tuple[int, str]]:
        """列出批次中的所有债权人

        Args:
            batch_number: 批次号

        Returns:
            List[Tuple[int, str]]: [(债权人编号, 债权人名称), ...]
        """
        batch_dir = self.output_root / f"第{batch_number}批债权"
        if not batch_dir.exists():
            return []

        creditors = []
        # 扫描格式: {编号}-{债权人名称}
        for creditor_dir in sorted(batch_dir.iterdir()):
            if not creditor_dir.is_dir():
                continue

            dir_name = creditor_dir.name
            if '-' not in dir_name:
                continue

            try:
                number_str, name = dir_name.split('-', 1)
                number = int(number_str)
                creditors.append((number, name))
            except (ValueError, IndexError):
                continue

        return creditors

    def batch_status(self, batch_number: int) -> Dict:
        """查询批次内所有债权人的状态

        Args:
            batch_number: 批次号

        Returns:
            Dict: 批次状态信息
        """
        creditors = self.list_creditors_in_batch(batch_number)

        if not creditors:
            return {
                "success": False,
                "message": f"第{batch_number}批债权目录为空或不存在",
                "batch_number": batch_number,
                "creditor_count": 0,
                "creditors": []
            }

        creditor_statuses = []
        for number, name in creditors:
            creditor_path = self.get_creditor_path(batch_number, number, name)
            round_manager = RoundManager(creditor_path)

            current_round = round_manager.get_current_round()
            total_rounds = round_manager.get_total_rounds()

            status_info = {
                "number": number,
                "name": name,
                "current_round": current_round,
                "total_rounds": total_rounds,
                "rounds": []
            }

            # 获取每个轮次的状态
            for round_num in range(1, total_rounds + 1):
                if round_manager.round_exists(round_num):
                    metadata = round_manager.get_round_metadata(round_num)
                    if metadata:
                        status_info["rounds"].append({
                            "round_number": round_num,
                            "status": metadata.get("status", "unknown"),
                            "processing_mode": metadata.get("processing_mode", "unknown")
                        })

            creditor_statuses.append(status_info)

        # 打印格式化的批次状态
        print("\n" + "=" * 80)
        print(f"第{batch_number}批债权状态")
        print("=" * 80)
        print(f"债权人数量: {len(creditors)}")
        print("-" * 80)

        for status in creditor_statuses:
            print(f"\n{status['number']:03d}-{status['name']}")
            print(f"  当前轮次: Round {status['current_round']}")
            print(f"  总轮次数: {status['total_rounds']}")
            if status['rounds']:
                print(f"  轮次详情:")
                for r in status['rounds']:
                    marker = "← 当前" if r['round_number'] == status['current_round'] else ""
                    print(f"    Round {r['round_number']}: {r['status']} ({r['processing_mode']}) {marker}")

        print("\n" + "=" * 80)

        return {
            "success": True,
            "batch_number": batch_number,
            "creditor_count": len(creditors),
            "creditors": creditor_statuses
        }

    def batch_init_round(
        self,
        batch_number: int,
        round_number: int,
        creditor_filter: Optional[List[int]] = None
    ) -> Dict:
        """批量初始化新轮次

        Args:
            batch_number: 批次号
            round_number: 轮次号
            creditor_filter: 债权人编号过滤列表（如果为None则处理所有）

        Returns:
            Dict: 批量初始化结果
        """
        creditors = self.list_creditors_in_batch(batch_number)

        if not creditors:
            return {
                "success": False,
                "message": f"第{batch_number}批债权目录为空或不存在"
            }

        # 应用过滤
        if creditor_filter:
            creditors = [(n, name) for n, name in creditors if n in creditor_filter]

        print("\n" + "=" * 80)
        print(f"批量初始化 Round {round_number} - 第{batch_number}批债权")
        print("=" * 80)
        print(f"处理债权人数: {len(creditors)}")
        print("-" * 80)

        results = []
        success_count = 0
        failed_count = 0

        for number, name in creditors:
            print(f"\n处理: {number:03d}-{name}")
            try:
                result = self.init_round(batch_number, number, name, round_number)
                results.append({
                    "creditor_number": number,
                    "creditor_name": name,
                    **result
                })
                if result["success"]:
                    success_count += 1
                    print(f"  ✅ 初始化成功")
                else:
                    failed_count += 1
                    print(f"  ❌ 初始化失败: {result.get('message', '')}")
            except Exception as e:
                failed_count += 1
                results.append({
                    "creditor_number": number,
                    "creditor_name": name,
                    "success": False,
                    "message": str(e)
                })
                print(f"  ❌ 初始化异常: {e}")

        print("\n" + "=" * 80)
        print(f"批量初始化完成")
        print(f"  成功: {success_count}")
        print(f"  失败: {failed_count}")
        print("=" * 80)

        return {
            "success": failed_count == 0,
            "batch_number": batch_number,
            "round_number": round_number,
            "total": len(creditors),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }

    def batch_analyze_impact(
        self,
        batch_number: int,
        supplemental_dir: str,
        creditor_filter: Optional[List[int]] = None
    ) -> Dict:
        """批量分析补充材料影响

        Args:
            batch_number: 批次号
            supplemental_dir: 补充材料目录（包含各债权人的材料文件）
            creditor_filter: 债权人编号过滤列表

        Returns:
            Dict: 批量分析结果

        补充材料文件命名规范:
            {supplemental_dir}/{编号}-{债权人名称}_supplemental.json
        """
        creditors = self.list_creditors_in_batch(batch_number)

        if not creditors:
            return {
                "success": False,
                "message": f"第{batch_number}批债权目录为空或不存在"
            }

        # 应用过滤
        if creditor_filter:
            creditors = [(n, name) for n, name in creditors if n in creditor_filter]

        supplemental_path = Path(supplemental_dir)
        if not supplemental_path.exists():
            return {
                "success": False,
                "message": f"补充材料目录不存在: {supplemental_dir}"
            }

        print("\n" + "=" * 80)
        print(f"批量影响分析 - 第{batch_number}批债权")
        print("=" * 80)
        print(f"处理债权人数: {len(creditors)}")
        print(f"补充材料目录: {supplemental_dir}")
        print("-" * 80)

        results = []
        success_count = 0
        failed_count = 0

        for number, name in creditors:
            # 查找补充材料文件
            material_file = supplemental_path / f"{number:03d}-{name}_supplemental.json"

            if not material_file.exists():
                print(f"\n{number:03d}-{name}: ⚠️  未找到补充材料文件，跳过")
                continue

            print(f"\n处理: {number:03d}-{name}")
            try:
                result = self.analyze_impact(batch_number, number, name, str(material_file))
                results.append({
                    "creditor_number": number,
                    "creditor_name": name,
                    **result
                })
                if result["success"]:
                    success_count += 1
                    impact = result["impact_analysis"]
                    print(f"  ✅ 分析完成")
                    print(f"     处理模式: {impact['processing_mode']}")
                    print(f"     节省时间: {impact['time_savings_percent']}%")
                else:
                    failed_count += 1
                    print(f"  ❌ 分析失败: {result.get('message', '')}")
            except Exception as e:
                failed_count += 1
                results.append({
                    "creditor_number": number,
                    "creditor_name": name,
                    "success": False,
                    "message": str(e)
                })
                print(f"  ❌ 分析异常: {e}")

        print("\n" + "=" * 80)
        print(f"批量影响分析完成")
        print(f"  成功: {success_count}")
        print(f"  失败: {failed_count}")
        print("=" * 80)

        return {
            "success": failed_count == 0,
            "batch_number": batch_number,
            "total": len(creditors),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }


def cli_main():
    """命令行接口主函数"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="多轮债权处理工作流控制器 v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 1. 分析补充材料的影响
  python multi_round_controller.py analyze \\
      --batch 1 --number 115 --name "债权人名称" \\
      --supplemental supplemental_materials.json

  # 2. 初始化新轮次
  python multi_round_controller.py init-round \\
      --batch 1 --number 115 --name "债权人名称" \\
      --round 2

  # 3. 处理轮次（Full模式）- 准备Agent调用配置
  python multi_round_controller.py process-round \\
      --batch 1 --number 115 --name "债权人名称" \\
      --round 2 --mode full

  # 4. 显示轮次历史
  python multi_round_controller.py show-history \\
      --batch 1 --number 115 --name "债权人名称"

  # 5. 回滚到指定轮次
  python multi_round_controller.py rollback \\
      --batch 1 --number 115 --name "债权人名称" \\
      --target-round 1

  # 6. 运行测试
  python multi_round_controller.py test
        """
    )

    parser.add_argument("--project-root", type=str,
                       default="/root/debt_review_skills",
                       help="项目根目录")

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析补充材料的影响")
    analyze_parser.add_argument("--batch", type=int, required=True, help="批次号")
    analyze_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    analyze_parser.add_argument("--name", type=str, required=True, help="债权人名称")
    analyze_parser.add_argument("--supplemental", type=str, required=True,
                               help="补充材料配置文件路径")

    # init-round命令
    init_parser = subparsers.add_parser("init-round", help="初始化新轮次")
    init_parser.add_argument("--batch", type=int, required=True, help="批次号")
    init_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    init_parser.add_argument("--name", type=str, required=True, help="债权人名称")
    init_parser.add_argument("--round", type=int, required=True, help="轮次号")

    # process-round命令
    process_parser = subparsers.add_parser("process-round", help="处理轮次")
    process_parser.add_argument("--batch", type=int, required=True, help="批次号")
    process_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    process_parser.add_argument("--name", type=str, required=True, help="债权人名称")
    process_parser.add_argument("--round", type=int, required=True, help="轮次号")
    process_parser.add_argument("--mode", type=str, default="full",
                               choices=["full", "incremental", "partial"],
                               help="处理模式")

    # show-history命令
    history_parser = subparsers.add_parser("show-history", help="显示轮次历史")
    history_parser.add_argument("--batch", type=int, required=True, help="批次号")
    history_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    history_parser.add_argument("--name", type=str, required=True, help="债权人名称")

    # show-changelog命令
    changelog_parser = subparsers.add_parser("show-changelog", help="显示变更日志")
    changelog_parser.add_argument("--batch", type=int, required=True, help="批次号")
    changelog_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    changelog_parser.add_argument("--name", type=str, required=True, help="债权人名称")

    # generate-checklist命令
    checklist_parser = subparsers.add_parser("generate-checklist", help="生成补充材料清单")
    checklist_parser.add_argument("--batch", type=int, required=True, help="批次号")
    checklist_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    checklist_parser.add_argument("--name", type=str, required=True, help="债权人名称")
    checklist_parser.add_argument("--round", type=int, required=True, help="轮次号")

    # rollback命令
    rollback_parser = subparsers.add_parser("rollback", help="回滚到指定轮次")
    rollback_parser.add_argument("--batch", type=int, required=True, help="批次号")
    rollback_parser.add_argument("--number", type=int, required=True, help="债权人编号")
    rollback_parser.add_argument("--name", type=str, required=True, help="债权人名称")
    rollback_parser.add_argument("--target-round", type=int, required=True, help="目标轮次号")
    rollback_parser.add_argument("--reason", type=str, default="", help="回滚原因（可选）")

    # batch-status命令
    batch_status_parser = subparsers.add_parser("batch-status", help="查询批次状态")
    batch_status_parser.add_argument("--batch", type=int, required=True, help="批次号")

    # batch-init命令
    batch_init_parser = subparsers.add_parser("batch-init", help="批量初始化轮次")
    batch_init_parser.add_argument("--batch", type=int, required=True, help="批次号")
    batch_init_parser.add_argument("--round", type=int, required=True, help="轮次号")
    batch_init_parser.add_argument("--filter", type=str, help="债权人编号过滤（逗号分隔，如: 100,101,102）")

    # batch-analyze命令
    batch_analyze_parser = subparsers.add_parser("batch-analyze", help="批量影响分析")
    batch_analyze_parser.add_argument("--batch", type=int, required=True, help="批次号")
    batch_analyze_parser.add_argument("--supplemental-dir", type=str, required=True,
                                      help="补充材料目录")
    batch_analyze_parser.add_argument("--filter", type=str, help="债权人编号过滤（逗号分隔）")

    # test命令
    subparsers.add_parser("test", help="运行测试")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    controller = MultiRoundController(args.project_root)

    try:
        if args.command == "analyze":
            result = controller.analyze_impact(
                args.batch, args.number, args.name, args.supplemental
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "init-round":
            result = controller.init_round(
                args.batch, args.number, args.name, args.round
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "process-round":
            # 确定处理模式
            if args.mode == "full":
                result = controller.process_round_full(
                    args.batch, args.number, args.name, args.round
                )
            elif args.mode == "incremental":
                # Incremental模式需要先读取轮次元数据获取影响分析结果
                creditor_path = controller.get_creditor_path(args.batch, args.number, args.name)
                round_manager = RoundManager(creditor_path)

                if not round_manager.round_exists(args.round):
                    print(json.dumps({"success": False, "message": f"轮次 {args.round} 不存在"},
                                   ensure_ascii=False, indent=2))
                    return 1

                # 读取轮次元数据
                metadata = round_manager.get_round_metadata(args.round)

                if not metadata or "impact_analysis" not in metadata:
                    print(json.dumps({"success": False,
                                    "message": "轮次元数据缺失影响分析信息，请先运行init-round或analyze命令"},
                                   ensure_ascii=False, indent=2))
                    return 1

                # 从元数据重建ImpactAnalysisResult
                from src.impact_analyzer import ImpactAnalysisResult, ProcessingMode
                impact_data = metadata["impact_analysis"]
                impact_result = ImpactAnalysisResult(
                    processing_mode=ProcessingMode(impact_data["processing_mode"]),
                    affected_stages=impact_data["affected_stages"],
                    affected_debt_items=impact_data["affected_debt_items"],
                    affected_sections=impact_data["affected_sections"],
                    fields_updated=impact_data["fields_updated"],
                    highest_priority=impact_data["highest_priority"],
                    time_savings_percent=impact_data["time_savings_percent"],
                    reasoning=impact_data["reasoning"],
                    user_confirm_required=impact_data.get("user_confirm_required", False),
                    unknown_fields=impact_data.get("unknown_fields", [])
                )

                result = controller.process_round_incremental(
                    args.batch, args.number, args.name, args.round, impact_result
                )
            elif args.mode == "partial":
                # Partial模式需要先读取轮次元数据获取影响分析结果
                creditor_path = controller.get_creditor_path(args.batch, args.number, args.name)
                round_manager = RoundManager(creditor_path)

                if not round_manager.round_exists(args.round):
                    print(json.dumps({"success": False, "message": f"轮次 {args.round} 不存在"},
                                   ensure_ascii=False, indent=2))
                    return 1

                # 读取轮次元数据
                metadata = round_manager.get_round_metadata(args.round)

                if not metadata or "impact_analysis" not in metadata:
                    print(json.dumps({"success": False,
                                    "message": "轮次元数据缺失影响分析信息，请先运行init-round或analyze命令"},
                                   ensure_ascii=False, indent=2))
                    return 1

                # 从元数据重建ImpactAnalysisResult
                from src.impact_analyzer import ImpactAnalysisResult, ProcessingMode
                impact_data = metadata["impact_analysis"]
                impact_result = ImpactAnalysisResult(
                    processing_mode=ProcessingMode(impact_data["processing_mode"]),
                    affected_stages=impact_data["affected_stages"],
                    affected_debt_items=impact_data["affected_debt_items"],
                    affected_sections=impact_data["affected_sections"],
                    fields_updated=impact_data["fields_updated"],
                    highest_priority=impact_data["highest_priority"],
                    time_savings_percent=impact_data["time_savings_percent"],
                    reasoning=impact_data["reasoning"],
                    user_confirm_required=impact_data.get("user_confirm_required", False),
                    unknown_fields=impact_data.get("unknown_fields", [])
                )

                result = controller.process_round_partial(
                    args.batch, args.number, args.name, args.round, impact_result
                )
            else:
                result = {"success": False, "message": f"未知的处理模式: {args.mode}"}

            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "show-history":
            result = controller.show_history(
                args.batch, args.number, args.name
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "show-changelog":
            result = controller.show_changelog(
                args.batch, args.number, args.name
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "generate-checklist":
            result = controller.generate_checklist(
                args.batch, args.number, args.name, args.round
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "rollback":
            result = controller.rollback_to_round(
                args.batch, args.number, args.name, args.target_round,
                reason=getattr(args, 'reason', '')
            )
            # print_history already called in rollback_to_round if successful
            # print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["success"] else 1

        elif args.command == "batch-status":
            result = controller.batch_status(args.batch)
            # batch_status内部已打印格式化输出
            return 0 if result["success"] else 1

        elif args.command == "batch-init":
            # 解析filter参数
            creditor_filter = None
            if hasattr(args, 'filter') and args.filter:
                try:
                    creditor_filter = [int(x.strip()) for x in args.filter.split(',')]
                except ValueError:
                    print("❌ filter参数格式错误，应为逗号分隔的数字，如: 100,101,102")
                    return 1

            result = controller.batch_init_round(
                args.batch, args.round, creditor_filter
            )
            # batch_init_round内部已打印格式化输出
            return 0 if result["success"] else 1

        elif args.command == "batch-analyze":
            # 解析filter参数
            creditor_filter = None
            if hasattr(args, 'filter') and args.filter:
                try:
                    creditor_filter = [int(x.strip()) for x in args.filter.split(',')]
                except ValueError:
                    print("❌ filter参数格式错误，应为逗号分隔的数字，如: 100,101,102")
                    return 1

            result = controller.batch_analyze_impact(
                args.batch, args.supplemental_dir, creditor_filter
            )
            # batch_analyze_impact内部已打印格式化输出
            return 0 if result["success"] else 1

        elif args.command == "test":
            return run_tests()

    except Exception as e:
        print(f"❌ 执行失败: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def run_tests():
    """运行测试"""
    import tempfile

    print("=" * 60)
    print("多轮工作流控制器测试")
    print("=" * 60)

    # 创建临时项目目录
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        output_dir = project_root / "输出" / "第1批债权" / "100-测试债权人"
        output_dir.mkdir(parents=True)

        # 创建旧格式目录
        (output_dir / "工作底稿").mkdir()
        (output_dir / "最终报告").mkdir()
        (output_dir / "计算文件").mkdir()

        controller = MultiRoundController(str(project_root))

        # 测试1: 确保轮次结构（自动迁移）
        print("\n测试1: 确保轮次结构（自动迁移）")
        print("-" * 60)
        success, message = controller.ensure_round_structure(output_dir)
        print(f"结果: {message}")

        # 测试2: 初始化Round 2
        print("\n测试2: 初始化Round 2")
        print("-" * 60)
        result = controller.init_round(
            batch_number=1,
            creditor_number=100,
            creditor_name="测试债权人",
            round_number=2
        )
        print(f"结果: {result['message']}")

        # 测试3: 显示历史
        print("\n测试3: 显示历史")
        print("-" * 60)
        history = controller.show_history(1, 100, "测试债权人")
        print(f"当前轮次: {history['current_round']}")
        print(f"总轮次数: {history['total_rounds']}")

        # 测试4: 回滚
        print("\n测试4: 回滚到Round 1")
        print("-" * 60)
        result = controller.rollback_to_round(1, 100, "测试债权人", 1)
        print(f"结果: {result['message']}")

    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
