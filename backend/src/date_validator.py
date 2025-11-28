# -*- coding: utf-8 -*-
"""
日期一致性验证器 - 确保破产日期和停止计息日期的一致性

破产日期是债权审查的生命线！任何日期错误都会导致：
- 利息计算完全错误
- 诉讼时效判断失误
- 最终审查意见无效

本模块提供强制性日期验证机制，在关键检查点自动验证日期一致性。
"""

import json
import re
import configparser
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class DateValidationResult:
    """日期验证结果"""
    is_valid: bool
    bankruptcy_date: Optional[str]
    interest_stop_date: Optional[str]
    inconsistencies: List[str]
    sources_checked: List[str]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "bankruptcy_date": self.bankruptcy_date,
            "interest_stop_date": self.interest_stop_date,
            "inconsistencies": self.inconsistencies,
            "sources_checked": self.sources_checked
        }

    def summary(self) -> str:
        """生成验证摘要"""
        if self.is_valid:
            return (
                f"✅ 日期验证通过\n"
                f"  破产受理日期: {self.bankruptcy_date}\n"
                f"  停止计息日期: {self.interest_stop_date}\n"
                f"  已验证来源: {', '.join(self.sources_checked)}"
            )
        else:
            return (
                f"❌ 日期验证失败！\n"
                f"  发现 {len(self.inconsistencies)} 处不一致：\n" +
                "\n".join(f"    - {inc}" for inc in self.inconsistencies) +
                f"\n  已检查来源: {', '.join(self.sources_checked)}"
            )


class DateValidator:
    """日期一致性验证器"""

    def __init__(self, project_root: str = "/root/debt_review_skills"):
        """初始化验证器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)

    def validate_dates(
        self,
        creditor_path: Path,
        round_number: Optional[int] = None,
        check_previous_rounds: bool = True
    ) -> DateValidationResult:
        """验证日期一致性（核心方法）

        Args:
            creditor_path: 债权人目录
            round_number: 轮次号（如果为None则验证最新轮次）
            check_previous_rounds: 是否检查前轮次的日期一致性

        Returns:
            DateValidationResult: 验证结果
        """
        sources_checked = []
        dates_found = {}  # {source_name: (bankruptcy_date, interest_stop_date)}
        inconsistencies = []

        # 1. 读取项目配置（权威来源）
        project_dates = self._read_project_config()
        if project_dates:
            sources_checked.append("project_config.ini")
            dates_found["project_config.ini"] = project_dates

        # 2. 读取轮次配置
        if round_number is None:
            # 查找最新轮次
            round_dirs = sorted(creditor_path.glob("round_*"))
            if round_dirs:
                round_number = int(round_dirs[-1].name.split("_")[1])

        if round_number:
            round_config_dates = self._read_round_config(creditor_path, round_number)
            if round_config_dates:
                sources_checked.append(f"round_{round_number}/.processing_config.json")
                dates_found[f"round_{round_number}_config"] = round_config_dates

            # 3. 读取轮次报告中的日期
            round_report_dates = self._read_round_reports(creditor_path, round_number)
            if round_report_dates:
                sources_checked.extend([
                    f"round_{round_number}/工作底稿/事实核查报告",
                    f"round_{round_number}/工作底稿/债权分析报告"
                ])
                for report_name, dates in round_report_dates.items():
                    dates_found[f"round_{round_number}_{report_name}"] = dates

        # 4. 检查前轮次日期（可选）
        if check_previous_rounds and round_number and round_number > 1:
            for prev_round in range(1, round_number):
                prev_config_dates = self._read_round_config(creditor_path, prev_round)
                if prev_config_dates:
                    sources_checked.append(f"round_{prev_round}/.processing_config.json")
                    dates_found[f"round_{prev_round}_config"] = prev_config_dates

        # 5. 分析一致性
        if not dates_found:
            return DateValidationResult(
                is_valid=False,
                bankruptcy_date=None,
                interest_stop_date=None,
                inconsistencies=["未找到任何日期信息"],
                sources_checked=sources_checked
            )

        # 确定权威日期（优先级：project_config > round_config）
        authoritative_dates = None
        if "project_config.ini" in dates_found:
            authoritative_dates = dates_found["project_config.ini"]
        elif f"round_{round_number}_config" in dates_found:
            authoritative_dates = dates_found[f"round_{round_number}_config"]
        else:
            # 使用第一个找到的日期
            authoritative_dates = list(dates_found.values())[0]

        bankruptcy_date_ref, interest_stop_date_ref = authoritative_dates

        # 6. 检查所有来源的一致性
        for source, (bankruptcy_date, interest_stop_date) in dates_found.items():
            if bankruptcy_date and bankruptcy_date != bankruptcy_date_ref:
                inconsistencies.append(
                    f"{source}: 破产受理日期 {bankruptcy_date} != 权威日期 {bankruptcy_date_ref}"
                )

            if interest_stop_date and interest_stop_date != interest_stop_date_ref:
                inconsistencies.append(
                    f"{source}: 停止计息日期 {interest_stop_date} != 权威日期 {interest_stop_date_ref}"
                )

        # 7. 验证日期关系（停止计息日 = 破产日 - 1天）
        if bankruptcy_date_ref and interest_stop_date_ref:
            try:
                bankruptcy_dt = datetime.strptime(bankruptcy_date_ref, "%Y-%m-%d")
                interest_stop_dt = datetime.strptime(interest_stop_date_ref, "%Y-%m-%d")
                expected_interest_stop_dt = bankruptcy_dt - timedelta(days=1)

                if interest_stop_dt != expected_interest_stop_dt:
                    inconsistencies.append(
                        f"停止计息日期 {interest_stop_date_ref} 应为破产日前一天 "
                        f"({expected_interest_stop_dt.strftime('%Y-%m-%d')})"
                    )
            except ValueError as e:
                inconsistencies.append(f"日期格式错误: {e}")

        is_valid = len(inconsistencies) == 0

        return DateValidationResult(
            is_valid=is_valid,
            bankruptcy_date=bankruptcy_date_ref,
            interest_stop_date=interest_stop_date_ref,
            inconsistencies=inconsistencies,
            sources_checked=sources_checked
        )

    def _read_project_config(self) -> Optional[Tuple[str, str]]:
        """读取项目配置文件中的日期

        Returns:
            Optional[Tuple[str, str]]: (bankruptcy_date, interest_stop_date) 或 None
        """
        config_file = self.project_root / "project_config.ini"

        if not config_file.exists():
            return None

        try:
            config = configparser.ConfigParser()
            config.read(config_file, encoding='utf-8')

            if 'project' not in config:
                return None

            bankruptcy_date = config['project'].get('bankruptcy_date')
            interest_stop_date = config['project'].get('interest_stop_date')

            if bankruptcy_date and interest_stop_date:
                return (bankruptcy_date, interest_stop_date)

        except Exception as e:
            print(f"⚠️  读取project_config.ini失败: {e}")

        return None

    def _read_round_config(
        self,
        creditor_path: Path,
        round_number: int
    ) -> Optional[Tuple[str, str]]:
        """读取轮次配置文件中的日期

        Args:
            creditor_path: 债权人目录
            round_number: 轮次号

        Returns:
            Optional[Tuple[str, str]]: (bankruptcy_date, interest_stop_date) 或 None
        """
        config_file = creditor_path / f"round_{round_number}" / ".processing_config.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if "bankruptcy_info" in config:
                bankruptcy_date = config["bankruptcy_info"].get("bankruptcy_date")
                interest_stop_date = config["bankruptcy_info"].get("interest_stop_date")

                if bankruptcy_date and interest_stop_date:
                    return (bankruptcy_date, interest_stop_date)

        except Exception as e:
            print(f"⚠️  读取round_{round_number}配置失败: {e}")

        return None

    def _read_round_reports(
        self,
        creditor_path: Path,
        round_number: int
    ) -> Dict[str, Tuple[str, str]]:
        """读取轮次报告中的日期（事实核查报告、债权分析报告）

        Args:
            creditor_path: 债权人目录
            round_number: 轮次号

        Returns:
            Dict[str, Tuple[str, str]]: {报告名称: (bankruptcy_date, interest_stop_date)}
        """
        work_dir = creditor_path / f"round_{round_number}" / "工作底稿"

        if not work_dir.exists():
            return {}

        results = {}

        # 检查事实核查报告
        fact_reports = list(work_dir.glob("*事实核查*.md"))
        for report in fact_reports:
            dates = self._extract_dates_from_report(report)
            if dates:
                results["fact_report"] = dates
                break

        # 检查债权分析报告
        analysis_reports = list(work_dir.glob("*债权分析*.md"))
        for report in analysis_reports:
            dates = self._extract_dates_from_report(report)
            if dates:
                results["analysis_report"] = dates
                break

        return results

    def _extract_dates_from_report(self, report_path: Path) -> Optional[Tuple[str, str]]:
        """从报告文件中提取日期

        Args:
            report_path: 报告文件路径

        Returns:
            Optional[Tuple[str, str]]: (bankruptcy_date, interest_stop_date) 或 None
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 正则表达式匹配日期模式
            bankruptcy_pattern = r"破产.*?受理.*?日期?[:：]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?)"
            interest_stop_pattern = r"停止.*?计息.*?日期?[:：]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?)"

            bankruptcy_match = re.search(bankruptcy_pattern, content)
            interest_stop_match = re.search(interest_stop_pattern, content)

            if bankruptcy_match and interest_stop_match:
                bankruptcy_date = bankruptcy_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')
                interest_stop_date = interest_stop_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')

                return (bankruptcy_date, interest_stop_date)

        except Exception as e:
            print(f"⚠️  提取{report_path.name}日期失败: {e}")

        return None

    def enforce_validation(
        self,
        creditor_path: Path,
        round_number: Optional[int] = None,
        stage_name: str = "处理"
    ) -> bool:
        """强制性日期验证（验证失败则抛出异常）

        Args:
            creditor_path: 债权人目录
            round_number: 轮次号
            stage_name: 阶段名称（用于错误消息）

        Returns:
            bool: 验证通过返回True

        Raises:
            ValueError: 日期验证失败
        """
        result = self.validate_dates(creditor_path, round_number)

        if not result.is_valid:
            error_msg = (
                f"\n{'='*60}\n"
                f"❌ 日期验证失败！{stage_name}终止！\n"
                f"{'='*60}\n"
                f"{result.summary()}\n"
                f"{'='*60}\n"
                f"⚠️  破产日期是债权审查的生命线！\n"
                f"⚠️  任何日期错误都会导致利息计算完全错误！\n"
                f"⚠️  请立即修正日期不一致问题后再继续！\n"
                f"{'='*60}\n"
            )
            raise ValueError(error_msg)

        print(result.summary())
        return True


def cli_main():
    """命令行接口"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="日期一致性验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 验证指定债权人的日期一致性
  python date_validator.py \\
      --creditor-path 输出/第1批债权/115-债权人名称

  # 验证指定轮次
  python date_validator.py \\
      --creditor-path 输出/第1批债权/115-债权人名称 \\
      --round 2

  # 强制验证模式（验证失败返回非零退出码）
  python date_validator.py \\
      --creditor-path 输出/第1批债权/115-债权人名称 \\
      --enforce
        """
    )

    parser.add_argument("--project-root", type=str,
                       default="/root/debt_review_skills",
                       help="项目根目录")
    parser.add_argument("--creditor-path", type=str, required=True,
                       help="债权人目录路径")
    parser.add_argument("--round", type=int,
                       help="轮次号（不指定则验证最新轮次）")
    parser.add_argument("--enforce", action="store_true",
                       help="强制验证模式（失败时抛出异常）")

    args = parser.parse_args()

    validator = DateValidator(args.project_root)
    creditor_path = Path(args.creditor_path)

    if not creditor_path.exists():
        print(f"❌ 债权人目录不存在: {creditor_path}")
        return 1

    try:
        if args.enforce:
            validator.enforce_validation(creditor_path, args.round)
            print("\n✅ 强制验证通过！")
            return 0
        else:
            result = validator.validate_dates(creditor_path, args.round)
            print(f"\n{result.summary()}")
            return 0 if result.is_valid else 1

    except ValueError as e:
        print(str(e))
        return 1
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(cli_main())
