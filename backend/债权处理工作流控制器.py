#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
债权处理工作流控制器 (Debt Processing Workflow Controller) v2.0

这个脚本用于统一管理债权审查的工作流程，确保：
1. 标准化的目录结构创建
2. 规范化的文件输出路径管理
3. Agent间的协调执行
4. 质量控制和验证（v2.0新增）
5. 自动修复和批量操作（v2.0新增）

v2.0新增功能：
- Layer 2: 文件完整性验证（检测缺失Excel、文件大小异常等）
- Layer 3: 自动修复功能（生成说明TXT文件）
- Layer 4: 批量验证和修复（整批债权质量检查）
"""

import os
import sys
import json
import argparse
import configparser
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DebtProcessingController:
    """债权处理工作流控制器"""
    
    def __init__(self, project_root: str = "/root/debt_review_skills"):
        self.project_root = Path(project_root)
        self.output_root = self.project_root / "输出"
        self.config_file = self.project_root / "project_config.ini"
        
        # 加载项目配置
        self.config = self._load_project_config()
        
    def _load_project_config(self) -> configparser.ConfigParser:
        """加载项目配置文件"""
        config = configparser.ConfigParser()
        if self.config_file.exists():
            config.read(self.config_file, encoding='utf-8')
        else:
            print(f"⚠️  警告：项目配置文件不存在 {self.config_file}")
        return config
    
    def create_creditor_directory(self, batch_number: str, creditor_number: str, 
                                creditor_name: str) -> Path:
        """创建债权人标准目录结构
        
        Args:
            batch_number: 批次号（如：1）
            creditor_number: 债权人编号（如：115）
            creditor_name: 债权人名称（如：慈溪市东航建筑起重机械安装队）
            
        Returns:
            Path: 债权人基础目录路径
        """
        # 构建目录路径
        base_dir = self.output_root / f"第{batch_number}批债权" / f"{creditor_number}-{creditor_name}"
        
        # 创建标准子目录
        subdirs = ["工作底稿", "最终报告", "计算文件", "并行处理prompts"]
        
        for subdir in subdirs:
            subdir_path = base_dir / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ 创建目录: {subdir_path}")
        
        return base_dir
    
    def generate_processing_config(self, batch_number: str, creditor_number: str,
                                 creditor_name: str) -> Dict:
        """为特定债权人生成处理配置
        
        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            
        Returns:
            Dict: 处理配置信息
        """
        base_path = self.output_root / f"第{batch_number}批债权" / f"{creditor_number}-{creditor_name}"
        current_date = datetime.now().strftime("%Y%m%d")
        
        config = {
            "creditor_info": {
                "batch_number": batch_number,
                "creditor_number": creditor_number,
                "creditor_name": creditor_name,
                "processing_date": current_date
            },
            "paths": {
                "base_directory": str(base_path),
                "work_papers": str(base_path / "工作底稿"),
                "final_reports": str(base_path / "最终报告"),
                "calculation_files": str(base_path / "计算文件"),
                "parallel_prompts": str(base_path / "并行处理prompts")
            },
            "file_templates": {
                "fact_check_report": f"{creditor_name}_事实核查报告.md",
                "analysis_report": f"{creditor_name}_债权分析报告.md",
                "final_review": f"GY2025_{creditor_name}_债权审查报告_{current_date}.md",
                "file_inventory": "文件清单.md",
                # Phase 8.1: 预处理输出文件模板
                "claim_structure_overview": f"{creditor_name}_债权结构概览.md",
                "legal_relationship_diagram": f"{creditor_name}_法律关系图.md"
            },
            "project_config": {
                "bankruptcy_date": self.config.get("关键日期", "破产受理日期", fallback=""),
                "interest_stop_date": self.config.get("关键日期", "停止计息日期", fallback=""),
                "debtor_name": self.config.get("项目基本信息", "债务人名称", fallback="")
            },
            "processing_metadata": {
                "initialization": {
                    "timestamp": datetime.now().isoformat(),
                    "material_statistics": {
                        "total_files": 0,
                        "total_size_kb": 0,
                        "large_files_count": 0
                    }
                },
                "stage1_fact_checking": {
                    "completed": False,
                    "scenario": None,
                    "strategy_used": None,
                    "material_statistics": {},
                    "completion_time": None,
                    "retry_count": 0
                },
                "stage2_debt_analysis": {
                    "completed": False,
                    "completion_time": None,
                    "calculation_files_generated": False,
                    "retry_count": 0
                },
                "stage3_report_organization": {
                    "completed": False,
                    "completion_time": None,
                    "format_compliance_verified": False,
                    "retry_count": 0
                }
            }
        }

        return config
    
    def save_processing_config(self, config: Dict) -> Path:
        """保存处理配置到文件
        
        Args:
            config: 处理配置字典
            
        Returns:
            Path: 配置文件路径
        """
        base_path = Path(config["paths"]["base_directory"])
        config_file = base_path / ".processing_config.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 保存处理配置: {config_file}")
        return config_file
    
    def validate_directory_structure(self, base_path: Path) -> bool:
        """验证目录结构完整性
        
        Args:
            base_path: 债权人基础目录路径
            
        Returns:
            bool: 验证结果
        """
        required_dirs = ["工作底稿", "最终报告", "计算文件", "并行处理prompts"]
        
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            if not dir_path.exists():
                print(f"❌ 缺少目录: {dir_path}")
                return False
            elif not dir_path.is_dir():
                print(f"❌ 路径不是目录: {dir_path}")
                return False
        
        print(f"✓ 目录结构验证通过: {base_path}")
        return True
    
    def check_file_placement(self, config: Dict) -> Dict:
        """检查文件放置情况
        
        Args:
            config: 处理配置
            
        Returns:
            Dict: 检查结果
        """
        base_path = Path(config["paths"]["base_directory"])
        creditor_name = config["creditor_info"]["creditor_name"]
        
        check_results = {
            "fact_check_report": False,
            "analysis_report": False,
            "calculation_files": [],
            "final_report": False,
            "file_inventory": False
        }
        
        # 检查事实核查报告
        fact_check_path = base_path / "工作底稿" / f"{creditor_name}_事实核查报告.md"
        check_results["fact_check_report"] = fact_check_path.exists()
        
        # 检查债权分析报告
        analysis_path = base_path / "工作底稿" / f"{creditor_name}_债权分析报告.md"
        check_results["analysis_report"] = analysis_path.exists()
        
        # 检查计算文件
        calc_dir = base_path / "计算文件"
        if calc_dir.exists():
            calc_files = [f for f in calc_dir.iterdir() if f.is_file()]
            check_results["calculation_files"] = [str(f) for f in calc_files]
        
        # 检查最终报告
        current_date = datetime.now().strftime("%Y%m%d")
        final_report_path = base_path / "最终报告" / f"GY2025_{creditor_name}_债权审查报告_{current_date}.md"
        check_results["final_report"] = final_report_path.exists()
        
        # 检查文件清单
        inventory_path = base_path / "文件清单.md"
        check_results["file_inventory"] = inventory_path.exists()
        
        return check_results
    
    def initialize_creditor_processing(self, batch_number: str, creditor_number: str,
                                     creditor_name: str) -> Tuple[Path, Dict]:
        """初始化债权人处理环境
        
        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            
        Returns:
            Tuple[Path, Dict]: 基础目录路径和配置信息
        """
        print(f"\n🚀 初始化债权人处理环境")
        print(f"   批次: 第{batch_number}批")
        print(f"   编号: {creditor_number}")
        print(f"   名称: {creditor_name}")
        
        # 创建目录结构
        base_path = self.create_creditor_directory(batch_number, creditor_number, creditor_name)
        
        # 生成处理配置
        config = self.generate_processing_config(batch_number, creditor_number, creditor_name)
        
        # 保存配置文件
        self.save_processing_config(config)
        
        # 验证目录结构
        if self.validate_directory_structure(base_path):
            print(f"✅ 债权人处理环境初始化完成")
        else:
            print(f"❌ 债权人处理环境初始化失败")
            return None, None
        
        return base_path, config
    
    def print_workflow_summary(self, config: Dict):
        """打印工作流程摘要

        Args:
            config: 处理配置
        """
        print(f"\n📋 工作流程摘要")
        print(f"   基础目录: {config['paths']['base_directory']}")
        print(f"   工作底稿: {config['paths']['work_papers']}")
        print(f"   计算文件: {config['paths']['calculation_files']}")
        print(f"   最终报告: {config['paths']['final_reports']}")
        print(f"\n📝 预期文件:")
        print(f"   事实核查: {config['file_templates']['fact_check_report']}")
        print(f"   债权分析: {config['file_templates']['analysis_report']}")
        print(f"   审查意见: {config['file_templates']['final_review']}")
        print(f"   文件清单: {config['file_templates']['file_inventory']}")

    # ==================== Layer 2: 文件验证功能（v2.0新增） ====================

    def validate_preprocessing_files(self, config: Dict) -> Dict:
        """验证预处理文件完整性（Phase 8.2 - 含向后兼容）

        向后兼容：如果没有preprocessing_config字段，跳过验证

        检查项（仅当preprocessing_config存在时）：
        1. 债权结构概览文件存在性
        2. 法律关系图文件存在性（根据diagram_required判断）
        3. 文件大小验证（>500字节）

        Args:
            config: 处理配置字典

        Returns:
            {
                'status': 'pass'|'warning'|'error'|'skipped',
                'skipped': bool,
                'structure_overview': {'exists': bool, 'size': int},
                'legal_diagram': {'exists': bool, 'required': bool, 'size': int},
                'recommendations': list
            }
        """
        results = {
            'status': 'pass',
            'skipped': False,
            'structure_overview': {'exists': False, 'size': 0},
            'legal_diagram': {'exists': False, 'required': False, 'size': 0},
            'recommendations': []
        }

        # ⚠️ 向后兼容：无preprocessing_config则跳过验证
        preprocess_config = config.get('preprocessing_config')
        if not preprocess_config:
            results['status'] = 'skipped'
            results['skipped'] = True
            results['recommendations'].append(
                '旧配置文件，跳过预处理验证（向后兼容）'
            )
            return results

        base_path = Path(config["paths"]["base_directory"])
        creditor_name = config["creditor_info"]["creditor_name"]
        work_papers = base_path / "工作底稿"

        # 检查1：债权结构概览（必须存在）
        overview_file = work_papers / f"{creditor_name}_债权结构概览.md"
        if not overview_file.exists():
            results['status'] = 'error'
            results['recommendations'].append(
                f'缺少债权结构概览文件: {overview_file.name}'
            )
        else:
            results['structure_overview']['exists'] = True
            results['structure_overview']['size'] = overview_file.stat().st_size
            if results['structure_overview']['size'] < 500:
                if results['status'] != 'error':
                    results['status'] = 'warning'
                results['recommendations'].append(
                    f'债权结构概览文件过小（{results["structure_overview"]["size"]}字节），可能内容不完整'
                )

        # 检查2：法律关系图（根据preprocessing_config判断）
        diagram_required = preprocess_config.get('diagram_required', False)
        results['legal_diagram']['required'] = diagram_required

        if diagram_required:
            diagram_file = work_papers / f"{creditor_name}_法律关系图.md"
            if not diagram_file.exists():
                results['status'] = 'error'
                results['recommendations'].append(
                    f'缺少法律关系图文件: {diagram_file.name}（该债权需要生成关系图）'
                )
            else:
                results['legal_diagram']['exists'] = True
                results['legal_diagram']['size'] = diagram_file.stat().st_size

        return results

    def validate_calculation_files(self, config: Dict) -> Dict:
        """验证计算文件完整性（Layer 2检测）

        检查内容：
        1. 计算文件目录是否为空
        2. 是否存在Excel/CSV文件或TXT/MD说明文件
        3. Excel文件大小是否异常（<2KB可能损坏）
        4. 文件命名是否符合规范

        Args:
            config: 处理配置字典

        Returns:
            {
                'status': 'pass'|'warning'|'error',
                'missing_excel': bool,
                'has_explanation': bool,
                'file_size_issues': list,
                'recommendations': list
            }
        """
        calc_dir = Path(config['paths']['calculation_files'])
        creditor_name = config['creditor_info']['creditor_name']

        results = {
            'status': 'pass',
            'missing_excel': False,
            'has_explanation': False,
            'file_size_issues': [],
            'recommendations': []
        }

        # 检查目录是否存在
        if not calc_dir.exists():
            results['status'] = 'error'
            results['recommendations'].append(f'计算文件目录不存在: {calc_dir}')
            return results

        # 检查目录是否为空
        calc_files = list(calc_dir.glob('*'))
        if not calc_files:
            results['status'] = 'error'
            results['missing_excel'] = True
            results['recommendations'].append('计算文件目录为空，需要补充Excel或说明文件')
            return results

        # 检查是否有Excel文件
        excel_files = list(calc_dir.glob('*.xlsx')) + list(calc_dir.glob('*.csv'))
        txt_files = list(calc_dir.glob('*.txt'))
        md_files = list(calc_dir.glob('*.md'))

        # 区分正常说明文件和异常MD文件
        normal_explanation_files = [f for f in txt_files if '无计算项' in f.name]
        abnormal_md_files = [f for f in md_files if '计算过程' in f.name or '说明' in f.name]

        all_explanation_files = txt_files + md_files

        # 检测异常模式：有"计算过程说明.md"但没有Excel（第4批问题）
        if abnormal_md_files and not excel_files:
            results['status'] = 'error'
            results['missing_excel'] = True
            results['recommendations'].append(
                f'发现异常：有计算过程MD说明文件但缺少Excel文件（应该直接生成Excel而非MD说明）'
            )
            return results

        if not excel_files and not all_explanation_files:
            results['status'] = 'error'
            results['missing_excel'] = True
            results['recommendations'].append('未找到计算文件（.xlsx/.csv）或说明文件（.txt/.md）')
            return results

        # 检查Excel文件大小（损坏检测）
        for excel_file in excel_files:
            file_size = excel_file.stat().st_size
            if file_size < 2048:  # < 2KB
                results['status'] = 'warning'
                results['file_size_issues'].append({
                    'file': excel_file.name,
                    'size': file_size,
                    'message': f'{excel_file.name}: {file_size}字节（可能损坏）'
                })
                results['recommendations'].append(
                    f'Excel文件{excel_file.name}异常小（{file_size}字节），请检查'
                )

        # 检查是否有说明文件
        if all_explanation_files:
            results['has_explanation'] = True

        # 最终状态判断
        if results['status'] == 'pass':
            if not excel_files and all_explanation_files:
                # 只有说明文件，没有Excel - 这是合法的（无计算项情况）
                results['status'] = 'pass'
                results['recommendations'].append(
                    f'债权人{creditor_name}无计算项，已提供说明文件'
                )
            elif excel_files:
                # 有Excel文件 - 正常情况
                results['status'] = 'pass'
                results['recommendations'].append(
                    f'债权人{creditor_name}有{len(excel_files)}个Excel计算文件'
                )

        return results

    def validate_report_completeness(self, config: Dict, stage: int) -> Dict:
        """验证指定Stage的报告完整性

        Args:
            config: 处理配置
            stage: Stage编号（1=事实核查, 2=债权分析, 3=报告整理）

        Returns:
            {
                'status': 'pass'|'error',
                'missing_files': list,
                'file_sizes': dict
            }
        """
        base_path = Path(config['paths']['base_directory'])
        creditor_name = config['creditor_info']['creditor_name']

        results = {
            'status': 'pass',
            'missing_files': [],
            'file_sizes': {}
        }

        if stage == 1:
            # 验证事实核查报告
            fact_report = base_path / "工作底稿" / f"{creditor_name}_事实核查报告.md"
            if not fact_report.exists():
                results['status'] = 'error'
                results['missing_files'].append(str(fact_report))
            elif fact_report.stat().st_size < 1000:
                results['status'] = 'warning'
                results['file_sizes'][str(fact_report)] = fact_report.stat().st_size

        elif stage == 2:
            # 验证债权分析报告
            analysis_report = base_path / "工作底稿" / f"{creditor_name}_债权分析报告.md"
            if not analysis_report.exists():
                results['status'] = 'error'
                results['missing_files'].append(str(analysis_report))
            elif analysis_report.stat().st_size < 1000:
                results['status'] = 'warning'
                results['file_sizes'][str(analysis_report)] = analysis_report.stat().st_size

        elif stage == 3:
            # 验证最终报告
            current_date = datetime.now().strftime("%Y%m%d")
            final_report = base_path / "最终报告" / f"GY2025_{creditor_name}_债权审查报告_{current_date}.md"
            if not final_report.exists():
                results['status'] = 'error'
                results['missing_files'].append(str(final_report))
            else:
                # 验证格式合规性
                format_errors = self._validate_report_format(final_report)
                if format_errors:
                    results['status'] = 'error'
                    results['format_errors'] = format_errors

        return results

    def _validate_report_format(self, report_path: Path) -> List[str]:
        """验证最终报告格式合规性（私有方法）

        检查项目（CLAUDE.md要求）：
        - 不应包含Markdown标题语法（## ）
        - 不应包含bullet列表语法（- ）
        - 不应包含粗体语法（**）

        Args:
            report_path: 最终报告文件路径

        Returns:
            list: 格式错误列表
        """
        errors = []

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查Markdown标题语法
            if re.search(r'^##\s', content, re.MULTILINE):
                errors.append("最终报告包含Markdown标题语法（##），违反格式要求")

            # 检查bullet列表
            if re.search(r'^- ', content, re.MULTILINE):
                errors.append("最终报告包含bullet列表语法（-），违反格式要求")

            # 检查粗体语法
            if '**' in content:
                errors.append("最终报告包含粗体语法（**），违反格式要求")

        except Exception as e:
            errors.append(f"读取报告文件失败: {str(e)}")

        return errors

    # ==================== Layer 3: 自动修复功能（v2.0新增） ====================

    def auto_fix_missing_calculation_files(self, config: Dict,
                                          analysis_report_path: Optional[Path] = None) -> bool:
        """自动补全缺失的计算文件（Layer 3修复）

        修复策略：
        1. 如果债权分析报告存在，读取并判断原因
        2. 如果是"无计算项"情况，生成说明文件
        3. 否则，报告无法自动修复

        Args:
            config: 处理配置
            analysis_report_path: 债权分析报告路径（可选，如不提供则自动推断）

        Returns:
            bool: 是否成功修复
        """
        calc_dir = Path(config['paths']['calculation_files'])
        creditor_name = config['creditor_info']['creditor_name']

        # 检查是否需要修复
        validation_result = self.validate_calculation_files(config)
        if validation_result['status'] == 'pass':
            print(f"✓ {creditor_name}: 计算文件已存在，无需修复")
            return True

        if not validation_result['missing_excel']:
            print(f"⚠️  {creditor_name}: 问题不是缺失文件，无法自动修复")
            return False

        # 推断债权分析报告路径
        if analysis_report_path is None:
            analysis_report_path = Path(config['paths']['work_papers']) / \
                                  config['file_templates']['analysis_report']

        # 读取分析报告判断原因
        if not analysis_report_path.exists():
            print(f"⚠️  {creditor_name}: 债权分析报告不存在，无法判断原因")
            return False

        with open(analysis_report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # 判断是否为"无计算项"情况
        no_calculation_keywords = [
            '未申报利息',
            '未主张利息',
            '就低原则',
            '无需计算',
            '无利息约定',
            '无利息条款',
            '放弃利息',
            '不计算利息',
            '无计息约定'
        ]

        reason_found = None
        for keyword in no_calculation_keywords:
            if keyword in report_content:
                reason_found = keyword
                break

        if reason_found:
            # 生成说明文件
            explanation_file = calc_dir / f"{creditor_name}_无计算项说明.txt"
            self._generate_explanation_file(
                explanation_file,
                creditor_name,
                config,
                reason=f'{reason_found}（从债权分析报告中识别）'
            )
            print(f"✓ {creditor_name}: 自动生成说明文件 {explanation_file.name}")
            return True
        else:
            print(f"⚠️  {creditor_name}: 债权分析报告中未找到'无计算项'关键词，无法自动判断")
            print(f"   建议人工检查：{analysis_report_path}")
            return False

    def _generate_explanation_file(self, file_path: Path, creditor_name: str,
                                   config: Dict, reason: str):
        """生成标准化说明文件（私有辅助方法）

        Args:
            file_path: 输出文件路径
            creditor_name: 债权人名称
            config: 处理配置
            reason: 无计算项的原因
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        batch_number = config['creditor_info']['batch_number']
        creditor_number = config['creditor_info']['creditor_number']

        template = f"""债权人：{creditor_name}
债权编号：第{batch_number}批债权-{creditor_number}号
生成时间：{current_date}

===================================================================
                     无利息计算项说明
===================================================================

一、基本情况

本案无需使用计算器工具进行利息计算。

二、无计算项原因

{reason}

三、审查依据

根据债权审查"就无原则"：债权人未申报的项目，不予确认。

债权人有权自主决定是否主张利息，其放弃利息主张的意思表示应予尊重。

四、计算工具使用情况

工具路径：/root/debt_review_skills/universal_debt_calculator_cli.py

使用情况：无需使用（债权人未申报利息或适用就低原则）

五、特别说明

详细分析请参见《{creditor_name}_债权分析报告.md》相关章节。

===================================================================

说明：本文件由债权处理工作流控制器v2.0自动生成
生成时间：{current_date}
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"  生成文件: {file_path.name}")

    # ==================== Layer 4: 批量操作功能（v2.0新增） ====================

    def validate_batch_stage(self, batch_number: int, stage: int,
                            fix: bool = False) -> Dict:
        """批量验证（或修复）指定批次的指定Stage（Layer 4流程控制）

        Args:
            batch_number: 批次号
            stage: Stage编号（0=预处理, 1=事实核查, 2=债权分析, 3=报告整理）
            fix: 是否自动修复（默认只验证）

        Returns:
            {
                'total': int,      # 总债权人数
                'passed': int,     # 通过数
                'failed': int,     # 失败数
                'fixed': int,      # 修复数（fix=True时）
                'details': list    # 详细结果列表
            }
        """
        batch_dir = self.output_root / f"第{batch_number}批债权"

        if not batch_dir.exists():
            print(f"❌ 批次目录不存在: {batch_dir}")
            return {'total': 0, 'passed': 0, 'failed': 0, 'fixed': 0, 'details': []}

        # 枚举所有债权人目录
        creditor_dirs = [d for d in batch_dir.iterdir() if d.is_dir()]

        results = {
            'total': len(creditor_dirs),
            'passed': 0,
            'failed': 0,
            'fixed': 0,
            'details': []
        }

        print(f"\n📋 批量验证第{batch_number}批债权 - Stage {stage}")
        print(f"   共{len(creditor_dirs)}个债权人\n")

        for creditor_dir in creditor_dirs:
            # 解析债权人编号和名称
            dir_name = creditor_dir.name
            if '-' not in dir_name:
                print(f"⚠️  跳过非标准目录: {dir_name}")
                continue

            creditor_number, creditor_name = dir_name.split('-', 1)

            # 读取配置
            config_file = creditor_dir / '.processing_config.json'
            if not config_file.exists():
                print(f"⚠️  {dir_name}: 配置文件缺失")
                results['failed'] += 1
                results['details'].append({
                    'creditor': dir_name,
                    'status': 'error',
                    'message': '配置文件缺失'
                })
                continue

            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 执行验证
            if stage == 0:
                # Phase 8.4: 预处理阶段验证
                validation = self.validate_preprocessing_files(config)

                if validation['skipped']:
                    print(f"⏭️  {dir_name}: 跳过（旧配置，无preprocessing_config）")
                    results['passed'] += 1  # 旧配置视为通过
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'skipped',
                        'message': '旧配置文件，跳过预处理验证'
                    })
                elif validation['status'] == 'pass':
                    print(f"✅ {dir_name}: 预处理验证通过")
                    results['passed'] += 1
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'pass',
                        'message': '预处理文件完整'
                    })
                elif validation['status'] == 'warning':
                    print(f"⚠️  {dir_name}: 预处理验证警告 - {validation['recommendations']}")
                    results['passed'] += 1  # 警告也视为通过
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'warning',
                        'message': ', '.join(validation['recommendations'])
                    })
                else:
                    print(f"❌ {dir_name}: 预处理验证失败 - {validation['recommendations']}")
                    results['failed'] += 1
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'error',
                        'message': ', '.join(validation['recommendations'])
                    })

            elif stage == 2:
                validation = self.validate_calculation_files(config)

                if validation['status'] == 'pass':
                    print(f"✅ {dir_name}: 验证通过")
                    results['passed'] += 1
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'pass',
                        'message': '验证通过'
                    })
                else:
                    print(f"❌ {dir_name}: {validation['recommendations']}")
                    results['failed'] += 1

                    # 尝试自动修复
                    if fix:
                        analysis_report = Path(config['paths']['work_papers']) / \
                                        config['file_templates']['analysis_report']
                        if self.auto_fix_missing_calculation_files(config, analysis_report):
                            results['fixed'] += 1
                            results['details'].append({
                                'creditor': dir_name,
                                'status': 'fixed',
                                'message': '已自动修复'
                            })
                        else:
                            results['details'].append({
                                'creditor': dir_name,
                                'status': 'error',
                                'message': '无法自动修复'
                            })
                    else:
                        results['details'].append({
                            'creditor': dir_name,
                            'status': 'error',
                            'message': ', '.join(validation['recommendations'])
                        })

            # Stage 1和3的验证逻辑可以后续添加
            elif stage == 1:
                report_validation = self.validate_report_completeness(config, 1)
                if report_validation['status'] == 'pass':
                    print(f"✅ {dir_name}: Stage 1验证通过")
                    results['passed'] += 1
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'pass',
                        'message': '事实核查报告完整'
                    })
                else:
                    print(f"❌ {dir_name}: Stage 1验证失败")
                    results['failed'] += 1
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'error',
                        'message': '事实核查报告缺失或不完整'
                    })

            elif stage == 3:
                report_validation = self.validate_report_completeness(config, 3)
                if report_validation['status'] == 'pass':
                    print(f"✅ {dir_name}: Stage 3验证通过")
                    results['passed'] += 1
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'pass',
                        'message': '最终报告完整且格式正确'
                    })
                else:
                    print(f"❌ {dir_name}: Stage 3验证失败")
                    results['failed'] += 1
                    error_msg = '最终报告缺失或格式不符'
                    if 'format_errors' in report_validation:
                        error_msg += f": {', '.join(report_validation['format_errors'])}"
                    results['details'].append({
                        'creditor': dir_name,
                        'status': 'error',
                        'message': error_msg
                    })

        return results

    # ==================== Layer 5: 反编造验证功能（Anti-Fabrication Checking） ====================

    def run_anti_fabrication_check(self, report_path: Path, report_type: str) -> Dict:
        """对单个报告运行反编造验证

        Args:
            report_path: 报告文件路径
            report_type: 报告类型 ('fact-checking', 'debt-analysis', 'review-opinion')

        Returns:
            {
                'passed': bool,
                'violations': int,
                'severity_breakdown': {'CRITICAL': 0, 'HIGH': 0, ...},
                'report_file': str
            }
        """
        import subprocess

        if not report_path.exists():
            return {
                'passed': False,
                'error': f'报告文件不存在: {report_path}'
            }

        checker_script = self.project_root / "anti_fabrication_checker.py"
        if not checker_script.exists():
            return {
                'passed': False,
                'error': f'验证工具不存在: {checker_script}'
            }

        try:
            # Run anti-fabrication checker
            result = subprocess.run(
                ['python3', str(checker_script), str(report_path), '--report-type', report_type],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse output for statistics
            output = result.stdout
            passed = '✅ 通过' in output

            # Extract violation counts
            violations = {'total': 0, 'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

            # Parse severity counts from output
            for line in output.split('\n'):
                if '- CRITICAL (严重):' in line:
                    violations['CRITICAL'] = int(re.search(r'(\d+)', line).group(1))
                elif '- HIGH (高):' in line:
                    violations['HIGH'] = int(re.search(r'(\d+)', line).group(1))
                elif '- MEDIUM (中):' in line:
                    violations['MEDIUM'] = int(re.search(r'(\d+)', line).group(1))
                elif '- LOW (低):' in line:
                    violations['LOW'] = int(re.search(r'(\d+)', line).group(1))
                elif '总违规数:' in line:
                    violations['total'] = int(re.search(r'(\d+)', line).group(1))

            return {
                'passed': passed,
                'violations': violations['total'],
                'severity_breakdown': violations,
                'report_file': str(report_path),
                'output': output
            }

        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'error': '验证超时（>30秒）'
            }
        except Exception as e:
            return {
                'passed': False,
                'error': f'验证失败: {str(e)}'
            }

    def validate_creditor_anti_fabrication(self, config: Dict, stage: int = 3) -> Dict:
        """对单个债权人的所有报告运行反编造验证

        Args:
            config: 处理配置字典
            stage: 验证阶段 (1=事实核查, 2=债权分析, 3=全部)

        Returns:
            {
                'creditor': str,
                'stage': int,
                'reports_checked': int,
                'reports_passed': int,
                'total_violations': int,
                'details': [...]
            }
        """
        creditor_name = config['creditor_info']['creditor_name']
        base_path = Path(config['paths']['base_directory'])

        results = {
            'creditor': creditor_name,
            'stage': stage,
            'reports_checked': 0,
            'reports_passed': 0,
            'total_violations': 0,
            'details': []
        }

        # Define reports to check based on stage
        checks = []

        if stage >= 1:
            fact_check_report = base_path / "工作底稿" / f"{creditor_name}_事实核查报告.md"
            if fact_check_report.exists():
                checks.append(('fact-checking', fact_check_report, '事实核查报告'))

        if stage >= 2:
            analysis_report = base_path / "工作底稿" / f"{creditor_name}_债权分析报告.md"
            if analysis_report.exists():
                checks.append(('debt-analysis', analysis_report, '债权分析报告'))

        if stage >= 3:
            final_reports = list((base_path / "最终报告").glob("GY2025_*.md"))
            if final_reports:
                checks.append(('review-opinion', final_reports[0], '审查意见表'))

        # Run checks
        for report_type, report_path, display_name in checks:
            print(f"\n  检查 {display_name}: {report_path.name}")
            check_result = self.run_anti_fabrication_check(report_path, report_type)

            results['reports_checked'] += 1

            if 'error' in check_result:
                results['details'].append({
                    'report': display_name,
                    'status': 'error',
                    'message': check_result['error']
                })
            else:
                if check_result['passed']:
                    results['reports_passed'] += 1
                    print(f"    ✅ 通过")
                else:
                    violations = check_result['violations']
                    results['total_violations'] += violations
                    severity = check_result['severity_breakdown']
                    print(f"    ❌ 检测到 {violations} 处违规")
                    print(f"       严重: {severity['CRITICAL']}, 高: {severity['HIGH']}, "
                          f"中: {severity['MEDIUM']}, 低: {severity['LOW']}")

                results['details'].append({
                    'report': display_name,
                    'status': 'passed' if check_result['passed'] else 'failed',
                    'violations': check_result['violations'],
                    'severity': check_result['severity_breakdown']
                })

        return results

    def validate_batch_anti_fabrication(self, batch_number: int, stage: int = 3) -> Dict:
        """对整批债权运行反编造验证

        Args:
            batch_number: 批次号
            stage: 验证阶段 (1=事实核查, 2=债权分析, 3=全部)

        Returns:
            {
                'batch': int,
                'stage': int,
                'total_creditors': int,
                'creditors_passed': int,
                'total_violations': int,
                'details': [...]
            }
        """
        batch_dir = self.output_root / f"第{batch_number}批债权"

        if not batch_dir.exists():
            return {'error': f'批次目录不存在: {batch_dir}'}

        results = {
            'batch': batch_number,
            'stage': stage,
            'total_creditors': 0,
            'creditors_passed': 0,
            'total_violations': 0,
            'details': []
        }

        # Find all creditor directories
        creditor_dirs = [d for d in batch_dir.iterdir() if d.is_dir() and re.match(r'^\d+-', d.name)]

        print(f"\n🔍 批量反编造验证: 第{batch_number}批，阶段{stage}")
        print(f"找到 {len(creditor_dirs)} 个债权人目录")

        for creditor_dir in sorted(creditor_dirs):
            config_file = creditor_dir / ".processing_config.json"

            if not config_file.exists():
                print(f"\n⚠️  跳过 {creditor_dir.name} (缺少配置文件)")
                continue

            # Load config
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            creditor_name = config['creditor_info']['creditor_name']
            print(f"\n📄 检查: {creditor_name}")

            # Run anti-fabrication checks
            creditor_result = self.validate_creditor_anti_fabrication(config, stage)

            results['total_creditors'] += 1
            results['total_violations'] += creditor_result['total_violations']

            if creditor_result['reports_passed'] == creditor_result['reports_checked']:
                results['creditors_passed'] += 1

            results['details'].append({
                'creditor': creditor_name,
                'reports_checked': creditor_result['reports_checked'],
                'reports_passed': creditor_result['reports_passed'],
                'violations': creditor_result['total_violations'],
                'status': 'passed' if creditor_result['reports_passed'] == creditor_result['reports_checked'] else 'failed'
            })

        return results

def main():
    """主函数 - 命令行接口（v2.0增强版）"""
    parser = argparse.ArgumentParser(
        description='债权处理工作流控制器 v2.0 - 环境管理与质量验证工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基础初始化（原有功能）
  python 债权处理工作流控制器.py 1 115 慈溪市东航建筑起重机械安装队

  # 初始化 + 自动验证
  python 债权处理工作流控制器.py 1 115 慈溪市东航建筑起重机械安装队 --validate

  # 初始化 + 自动修复
  python 债权处理工作流控制器.py 1 115 慈溪市东航建筑起重机械安装队 --fix

  # 批量验证指定批次的Stage 2
  python 债权处理工作流控制器.py --validate-batch 1 --stage 2

  # 批量修复指定批次的Stage 2
  python 债权处理工作流控制器.py --fix-batch 1 --stage 2
        """
    )

    # 位置参数（可选，用于单个债权人操作）
    parser.add_argument('batch_number', nargs='?', help='批次号（如：1）')
    parser.add_argument('creditor_number', nargs='?', help='债权人编号（如：115）')
    parser.add_argument('creditor_name', nargs='?', help='债权人名称')

    # 选项参数（v2.0新增功能）
    parser.add_argument('--validate', action='store_true',
                       help='初始化后自动验证文件完整性')
    parser.add_argument('--fix', action='store_true',
                       help='初始化后自动验证并修复问题')
    parser.add_argument('--validate-batch', type=int, metavar='N',
                       help='批量验证指定批次（需配合--stage）')
    parser.add_argument('--fix-batch', type=int, metavar='N',
                       help='批量修复指定批次（需配合--stage）')
    parser.add_argument('--stage', type=int, choices=[1, 2, 3],
                       help='指定Stage（1=事实核查, 2=债权分析, 3=报告整理）')

    args = parser.parse_args()
    controller = DebtProcessingController()

    # 模式1：单个债权人操作
    if args.batch_number and args.creditor_number and args.creditor_name:
        base_path, config = controller.initialize_creditor_processing(
            args.batch_number, args.creditor_number, args.creditor_name
        )

        if not (base_path and config):
            sys.exit(1)

        controller.print_workflow_summary(config)

        # 选项：验证
        if args.validate or args.fix:
            print(f"\n🔍 执行文件验证...")
            validation = controller.validate_calculation_files(config)

            if validation['status'] == 'pass':
                print(f"✅ 验证通过")
                if validation['recommendations']:
                    for rec in validation['recommendations']:
                        print(f"   {rec}")
            else:
                print(f"⚠️  发现问题:")
                for rec in validation['recommendations']:
                    print(f"   - {rec}")

                # 选项：自动修复
                if args.fix:
                    print(f"\n🔧 尝试自动修复...")
                    analysis_report = Path(config['paths']['work_papers']) / config['file_templates']['analysis_report']
                    if controller.auto_fix_missing_calculation_files(config, analysis_report):
                        print(f"✅ 问题已自动修复")
                    else:
                        print(f"❌ 无法自动修复，需要人工介入")
        else:
            print(f"\n✅ 环境准备完成，可以开始债权审查流程")
            print(f"   请按照以下顺序执行Agent:")
            print(f"   1. debt-fact-checker (事实核查员)")
            print(f"   2. debt-claim-analyzer (债权分析员)")
            print(f"   3. report-organizer (报告整理员)")

    # 模式2：批量操作
    elif args.validate_batch or args.fix_batch:
        if not args.stage:
            print("错误: 批量操作需要指定--stage参数")
            sys.exit(1)

        batch = args.validate_batch or args.fix_batch
        is_fix_mode = bool(args.fix_batch)

        print(f"\n🔍 批量{'修复' if is_fix_mode else '验证'}第{batch}批债权的Stage {args.stage}...")
        results = controller.validate_batch_stage(batch, args.stage, fix=is_fix_mode)

        # 打印结果摘要
        print(f"\n📊 验证结果摘要:")
        print(f"  总计: {results['total']}个债权人")
        print(f"  通过: {results['passed']}个 ({'✅' if results['passed'] == results['total'] else '⚠️'})")
        print(f"  失败: {results['failed']}个 ({'✅' if results['failed'] == 0 else '❌'})")
        if is_fix_mode:
            print(f"  已修复: {results['fixed']}个")

        # 如果有失败项，显示详情
        if results['failed'] > 0:
            print(f"\n❌ 失败详情:")
            for detail in results['details']:
                if detail['status'] == 'error':
                    print(f"  - {detail['creditor']}: {detail['message']}")

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()