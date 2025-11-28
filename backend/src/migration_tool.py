# -*- coding: utf-8 -*-
"""
向后兼容的自动迁移工具

将旧格式的债权人目录自动迁移到轮次隔离结构（round_1/），确保向后兼容性。

旧格式：
  输出/第X批债权/[编号]-[债权人名称]/
  ├── .processing_config.json
  ├── 工作底稿/
  ├── 计算文件/
  ├── 最终报告/
  └── 并行处理prompts/

新格式（迁移后）：
  输出/第X批债权/[编号]-[债权人名称]/
  ├── .processing_config.json
  ├── .current_round.json  ← 新增
  └── round_1/  ← 新增
      ├── .round_metadata.json  ← 新增
      ├── 工作底稿/  ← 从旧位置移动
      ├── 计算文件/  ← 从旧位置移动
      ├── 最终报告/  ← 从旧位置移动
      └── 并行处理prompts/  ← 从旧位置移动
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class MigrationTool:
    """债权人目录迁移工具"""

    def __init__(self, project_root: str = "/root/debt_review_skills"):
        """初始化迁移工具

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "输出"

    def is_old_format(self, creditor_path: Path) -> bool:
        """判断债权人目录是否是旧格式

        Args:
            creditor_path: 债权人目录路径

        Returns:
            bool: 是否是旧格式
        """
        # 检查是否已经是新格式（存在round_1/）
        if (creditor_path / "round_1").exists():
            return False

        # 检查是否是有效的旧格式（存在工作底稿/）
        if (creditor_path / "工作底稿").exists():
            return True

        return False

    def is_already_migrated(self, creditor_path: Path) -> bool:
        """判断债权人目录是否已迁移

        Args:
            creditor_path: 债权人目录路径

        Returns:
            bool: 是否已迁移
        """
        return (creditor_path / "round_1").exists() and \
               (creditor_path / ".current_round.json").exists()

    def migrate_single_creditor(self, creditor_path: Path,
                               dry_run: bool = False) -> Tuple[bool, str]:
        """迁移单个债权人目录

        Args:
            creditor_path: 债权人目录路径
            dry_run: 是否为演练模式（不实际移动文件）

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        creditor_name = creditor_path.name

        # 检查是否需要迁移
        if not self.is_old_format(creditor_path):
            if self.is_already_migrated(creditor_path):
                return True, f"{creditor_name}: 已经是新格式，无需迁移"
            else:
                return False, f"{creditor_name}: 不是有效的债权人目录"

        if dry_run:
            print(f"[DRY RUN] 将迁移 {creditor_name} 到round_1/结构")
            return True, f"{creditor_name}: 演练模式（未实际执行）"

        try:
            # 创建round_1/目录结构
            round_1_dir = creditor_path / "round_1"
            round_1_dir.mkdir(parents=True, exist_ok=True)

            # 移动现有目录到round_1/
            subdirs_to_move = ["工作底稿", "最终报告", "计算文件", "并行处理prompts"]
            moved_dirs = []

            for subdir_name in subdirs_to_move:
                old_path = creditor_path / subdir_name
                if old_path.exists():
                    new_path = round_1_dir / subdir_name
                    shutil.move(str(old_path), str(new_path))
                    moved_dirs.append(subdir_name)

            # 生成轮次元数据
            round_metadata = {
                "round_number": 1,
                "created_at": datetime.now().isoformat(),
                "status": "completed",
                "processing_mode": "full",
                "parent_round": None,
                "migrated_from_legacy": True,
                "migration_time": datetime.now().isoformat(),
                "migration_note": "自动从旧格式迁移"
            }

            metadata_file = round_1_dir / ".round_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(round_metadata, f, ensure_ascii=False, indent=2)

            # 生成当前轮次指针
            # 尝试从round_1/最终报告/中找到最新报告
            final_reports_dir = round_1_dir / "最终报告"
            latest_report = None
            if final_reports_dir.exists():
                report_files = list(final_reports_dir.glob("GY2025_*.md"))
                if report_files:
                    # 按修改时间排序，取最新的
                    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                    latest_report = f"round_1/最终报告/{latest_report.name}"

            current_round = {
                "current_round": 1,
                "total_rounds": 1,
                "latest_report_path": latest_report,
                "last_updated": datetime.now().isoformat()
            }

            current_round_file = creditor_path / ".current_round.json"
            with open(current_round_file, 'w', encoding='utf-8') as f:
                json.dump(current_round, f, ensure_ascii=False, indent=2)

            message = f"{creditor_name}: 迁移成功（移动了{len(moved_dirs)}个目录）"
            return True, message

        except Exception as e:
            message = f"{creditor_name}: 迁移失败 - {str(e)}"
            return False, message

    def migrate_batch(self, batch_number: int, dry_run: bool = False) -> Dict:
        """批量迁移整个批次的债权人

        Args:
            batch_number: 批次号
            dry_run: 是否为演练模式

        Returns:
            Dict: 迁移结果统计
        """
        batch_dir = self.output_dir / f"第{batch_number}批债权"

        if not batch_dir.exists():
            return {
                "success": False,
                "message": f"批次目录不存在: {batch_dir}",
                "results": []
            }

        # 扫描所有债权人目录
        creditor_dirs = [d for d in batch_dir.iterdir()
                        if d.is_dir() and d.name.startswith(f"{batch_number}")]

        if not creditor_dirs:
            creditor_dirs = [d for d in batch_dir.iterdir() if d.is_dir()]

        results = []
        success_count = 0
        skip_count = 0
        fail_count = 0

        print(f"\n{'='*60}")
        print(f"开始迁移第{batch_number}批债权（共{len(creditor_dirs)}个债权人）")
        if dry_run:
            print("⚠️  演练模式：不会实际移动文件")
        print(f"{'='*60}\n")

        for creditor_dir in creditor_dirs:
            success, message = self.migrate_single_creditor(creditor_dir, dry_run)
            results.append({
                "creditor": creditor_dir.name,
                "success": success,
                "message": message
            })

            # 统计
            if "无需迁移" in message or "已经是新格式" in message:
                skip_count += 1
                print(f"✓ {message}")
            elif success:
                success_count += 1
                print(f"✓ {message}")
            else:
                fail_count += 1
                print(f"✗ {message}")

        # 生成摘要
        summary = {
            "batch_number": batch_number,
            "total_creditors": len(creditor_dirs),
            "success_count": success_count,
            "skip_count": skip_count,
            "fail_count": fail_count,
            "dry_run": dry_run,
            "results": results
        }

        # 打印摘要
        print(f"\n{'='*60}")
        print("迁移摘要")
        print(f"{'='*60}")
        print(f"  总计: {summary['total_creditors']}个债权人")
        print(f"  成功迁移: {success_count}个")
        print(f"  无需迁移: {skip_count}个")
        print(f"  失败: {fail_count}个")

        if dry_run:
            print(f"\n⚠️  这是演练模式，未实际执行迁移")
            print(f"   如要执行实际迁移，请移除 --dry-run 参数")

        return summary

    def migrate_all(self, dry_run: bool = False) -> Dict:
        """迁移所有批次的债权人

        Args:
            dry_run: 是否为演练模式

        Returns:
            Dict: 迁移结果统计
        """
        if not self.output_dir.exists():
            return {
                "success": False,
                "message": f"输出目录不存在: {self.output_dir}",
                "batches": []
            }

        # 扫描所有批次目录
        batch_dirs = [d for d in self.output_dir.iterdir()
                     if d.is_dir() and d.name.startswith("第") and d.name.endswith("批债权")]

        if not batch_dirs:
            return {
                "success": True,
                "message": "未找到批次目录",
                "batches": []
            }

        # 提取批次号并排序
        batch_numbers = []
        for batch_dir in batch_dirs:
            try:
                # 从"第X批债权"中提取X
                batch_num = int(batch_dir.name.replace("第", "").replace("批债权", ""))
                batch_numbers.append(batch_num)
            except:
                continue

        batch_numbers.sort()

        # 逐批次迁移
        batch_results = []
        total_success = 0
        total_skip = 0
        total_fail = 0

        for batch_num in batch_numbers:
            print(f"\n{'#'*60}")
            print(f"# 处理批次 {batch_num}")
            print(f"{'#'*60}")

            batch_summary = self.migrate_batch(batch_num, dry_run)
            batch_results.append(batch_summary)

            total_success += batch_summary['success_count']
            total_skip += batch_summary['skip_count']
            total_fail += batch_summary['fail_count']

        # 总摘要
        print(f"\n\n{'='*60}")
        print("总体迁移摘要")
        print(f"{'='*60}")
        print(f"  处理批次: {len(batch_numbers)}个")
        print(f"  总债权人: {total_success + total_skip + total_fail}个")
        print(f"  成功迁移: {total_success}个")
        print(f"  无需迁移: {total_skip}个")
        print(f"  失败: {total_fail}个")

        return {
            "success": True,
            "batches_processed": len(batch_numbers),
            "total_creditors": total_success + total_skip + total_fail,
            "total_success": total_success,
            "total_skip": total_skip,
            "total_fail": total_fail,
            "dry_run": dry_run,
            "batches": batch_results
        }

    def rollback_migration(self, creditor_path: Path) -> Tuple[bool, str]:
        """回滚迁移（将round_1/内容移回原位置）

        Args:
            creditor_path: 债权人目录路径

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        creditor_name = creditor_path.name

        # 检查是否是迁移后的格式
        round_1_dir = creditor_path / "round_1"
        if not round_1_dir.exists():
            return False, f"{creditor_name}: 不是新格式，无需回滚"

        # 检查是否是迁移产生的（有migrated_from_legacy标记）
        metadata_file = round_1_dir / ".round_metadata.json"
        if not metadata_file.exists():
            return False, f"{creditor_name}: 缺少元数据，不确定是否可回滚"

        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        if not metadata.get("migrated_from_legacy"):
            return False, f"{creditor_name}: 不是迁移产生的格式，不建议回滚"

        try:
            # 移动round_1/内容回原位置
            subdirs = ["工作底稿", "最终报告", "计算文件", "并行处理prompts"]
            moved_dirs = []

            for subdir_name in subdirs:
                old_path = round_1_dir / subdir_name
                if old_path.exists():
                    new_path = creditor_path / subdir_name
                    # 如果目标已存在，先删除
                    if new_path.exists():
                        shutil.rmtree(new_path)
                    shutil.move(str(old_path), str(new_path))
                    moved_dirs.append(subdir_name)

            # 删除round_1/目录
            shutil.rmtree(round_1_dir)

            # 删除.current_round.json
            current_round_file = creditor_path / ".current_round.json"
            if current_round_file.exists():
                current_round_file.unlink()

            message = f"{creditor_name}: 回滚成功（恢复了{len(moved_dirs)}个目录）"
            return True, message

        except Exception as e:
            message = f"{creditor_name}: 回滚失败 - {str(e)}"
            return False, message


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="债权人目录格式迁移工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 演练模式（不实际执行）
  python migration_tool.py --batch 1 --dry-run

  # 迁移第1批债权
  python migration_tool.py --batch 1

  # 迁移所有批次
  python migration_tool.py --all

  # 回滚迁移
  python migration_tool.py --rollback --creditor "输出/第1批债权/115-债权人名称"
        """
    )

    parser.add_argument("--batch", type=int, help="迁移指定批次号")
    parser.add_argument("--all", action="store_true", help="迁移所有批次")
    parser.add_argument("--creditor", type=str, help="迁移或回滚单个债权人（提供完整路径）")
    parser.add_argument("--rollback", action="store_true", help="回滚迁移")
    parser.add_argument("--dry-run", action="store_true", help="演练模式（不实际执行）")
    parser.add_argument("--project-root", type=str,
                       default="/root/debt_review_skills",
                       help="项目根目录")

    args = parser.parse_args()

    # 创建迁移工具实例
    tool = MigrationTool(args.project_root)

    # 执行操作
    if args.rollback:
        if not args.creditor:
            print("错误: --rollback 需要指定 --creditor 参数")
            return 1

        creditor_path = Path(args.creditor)
        if not creditor_path.is_absolute():
            creditor_path = tool.project_root / creditor_path

        success, message = tool.rollback_migration(creditor_path)
        print(message)
        return 0 if success else 1

    elif args.creditor:
        creditor_path = Path(args.creditor)
        if not creditor_path.is_absolute():
            creditor_path = tool.project_root / creditor_path

        success, message = tool.migrate_single_creditor(creditor_path, args.dry_run)
        print(message)
        return 0 if success else 1

    elif args.batch:
        summary = tool.migrate_batch(args.batch, args.dry_run)
        return 0 if summary['fail_count'] == 0 else 1

    elif args.all:
        summary = tool.migrate_all(args.dry_run)
        return 0 if summary['total_fail'] == 0 else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
