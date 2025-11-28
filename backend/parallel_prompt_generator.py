#!/usr/bin/env python3
"""
Parallel Prompt Generator for Debt Review System

This tool automatically generates self-contained prompts for parallel processing
of multiple creditors in the debt review system.

Usage:
    python parallel_prompt_generator.py --stage 1 --batch 1 --creditors 115,118,124,134,140
    python parallel_prompt_generator.py --stage 2 --batch 1 --creditors 115,118
    python parallel_prompt_generator.py --stage 3 --batch 1 --creditors 115

Version: 1.0
Created: 2025-10-26
"""

import os
import sys
import argparse
import json
import configparser
from pathlib import Path
from datetime import datetime, timedelta

# Base directory for the project
BASE_DIR = Path("/root/debt_review_skills")
PROJECT_CONFIG_FILE = BASE_DIR / "project_config.ini"
OUTPUT_BASE_DIR = BASE_DIR / "输出"
INPUT_BASE_DIR = BASE_DIR / "输入"
TEMPLATE_DIR = BASE_DIR / "parallel_prompt_templates"


def load_project_config():
    """Load project configuration from project_config.ini"""
    if not PROJECT_CONFIG_FILE.exists():
        print(f"❌ Error: Project config file not found: {PROJECT_CONFIG_FILE}")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(PROJECT_CONFIG_FILE, encoding='utf-8')

    # Extract key dates
    bankruptcy_date_str = config['关键日期']['破产受理日期']  # YYYY-MM-DD
    interest_stop_date_str = config['关键日期']['停止计息日期']  # YYYY-MM-DD
    debtor_name = config['项目基本信息']['债务人名称']

    return {
        'bankruptcy_date': bankruptcy_date_str,
        'interest_stop_date': interest_stop_date_str,
        'debtor_name': debtor_name
    }


def load_creditor_config(batch, creditor_number, creditor_name):
    """Load .processing_config.json for a specific creditor"""
    config_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / ".processing_config.json"

    if not config_path.exists():
        print(f"❌ Error: Config file not found for creditor {creditor_number}: {config_path}")
        print(f"   Please initialize environment first:")
        print(f"   python 债权处理工作流控制器.py {batch} {creditor_number} {creditor_name}")
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_creditor_name_from_input(batch, creditor_number):
    """Extract creditor name from input material filename"""
    input_dir = INPUT_BASE_DIR / f"第{batch}批债权"

    # Find files matching the pattern: {number}.{name}.md
    for file in input_dir.glob(f"{creditor_number}.*.md"):
        # Extract name: "115.慈溪市东航建筑起重机械安装队.md" -> "慈溪市东航建筑起重机械安装队"
        parts = file.stem.split('.', 1)
        if len(parts) == 2:
            return parts[1]

    return None


def format_date_chinese(date_str):
    """Convert YYYY-MM-DD to YYYY年MM月DD日"""
    parts = date_str.split('-')
    return f"{parts[0]}年{parts[1]}月{parts[2]}日"


def generate_stage1_prompt(batch, creditor_number, creditor_name, project_config):
    """Generate Stage 1 (Fact-Checking) prompt"""

    # Load creditor config
    creditor_config = load_creditor_config(batch, creditor_number, creditor_name)
    if not creditor_config:
        return None

    # Extract processing date from config
    processing_date = creditor_config['creditor_info']['processing_date']

    # Build absolute paths
    config_file_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / ".processing_config.json"
    input_material_path = INPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}.{creditor_name}.md"
    output_work_papers_dir = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "工作底稿"

    # Verify input material exists
    if not input_material_path.exists():
        print(f"⚠️  Warning: Input material not found: {input_material_path}")

    prompt = f"""# 债权人{creditor_name} - 事实核查并行处理任务

## ⚠️ 重要说明：并行处理模式

你正在**并行处理模式**下工作。本次任务**仅处理债权人 {creditor_name}**，不要处理任何其他债权人。

**关键要求**:
- 所有信息都在本 prompt 中提供，不要依赖任何外部上下文或假设
- 使用绝对路径，不要猜测路径或使用相对路径
- 严格执行三重验证机制（启动验证 → 文件操作验证 → 完成验证）
- 仅处理本 prompt 中明确指定的债权人

---

## 第一部分：债权人身份标识

**批次号**: {batch}
**债权人编号**: {creditor_number}
**债权人名称**: {creditor_name}
**处理日期**: {processing_date}

**身份验证要求**:
1. 在开始工作前，读取配置文件验证上述信息
2. 如配置文件中的信息与上述不一致，**立即停止**并报告错误，不继续执行
3. 在报告中明确记录债权人身份（名称、编号、批次）

---

## 第二部分：配置文件路径

**配置文件路径（绝对路径，必须使用）**:
```
{config_file_path}
```

**使用要求**:
1. **必须**读取此配置文件获取路径和文件名模板
2. 读取后验证 `creditor_info` 部分与第一部分的标识完全一致:
   - `batch_number` == "{batch}"
   - `creditor_number` == "{creditor_number}"
   - `creditor_name` == "{creditor_name}"
3. 如不一致，**立即停止**并报告: "配置验证失败: prompt 指定 {creditor_name}，配置显示 [配置中的名称]"
4. 使用配置中的 `paths` 进行所有文件操作
5. 使用配置中的 `file_templates.fact_check_report` 作为输出文件名

---

## 第三部分：输入材料路径

**材料文件路径（绝对路径）**:
```
{input_material_path}
```

**读取要求**:
1. **必须**读取此路径的材料文件，不得读取其他债权人的材料
2. 读取前验证路径包含正确的批次号和债权人标识
3. 读取后验证文件内容对应正确的债权人（检查文件开头的债权人名称）
4. 如文件不存在或路径错误，立即报告错误，不要猜测其他路径

---

## 第四部分：输出目录路径

**工作底稿目录（绝对路径）**:
```
{output_work_papers_dir}
```

**输出文件名**（从配置文件读取）:
```
{creditor_name}_事实核查报告.md
```

**输出要求**:
1. 事实核查报告**必须**保存到上述工作底稿目录
2. 文件名使用配置文件中的 `file_templates.fact_check_report`
3. 写入前验证目录路径包含 "{creditor_number}-{creditor_name}"
4. 写入后验证文件已成功保存: 使用 `ls` 命令确认文件存在

---

## 第五部分：关键参数

**破产受理日期**: {project_config['bankruptcy_date']}（格式: YYYY-MM-DD）
**停止计息日期**: {project_config['interest_stop_date']}（格式: YYYY-MM-DD）
**债务人名称**: {project_config['debtor_name']}

**日期验证要求**:
1. 与配置文件中的 `project_config.bankruptcy_date` 交叉验证
2. 如发现任何不一致，**立即停止**并报告错误
3. 在输出报告中使用中文日期格式: YYYY年MM月DD日
   - 示例: {format_date_chinese(project_config['bankruptcy_date'])}
4. 在报告中明确记录这些日期

---

## 第六部分：任务指令

请按照 debt-fact-checker agent 的标准工作流程执行事实核查，生成完整的《事实核查报告》。

**完整任务要求**: 参考 `.claude/agents/debt-fact-checker.md` 和 `debt-fact-checking` skill。

---

## 第七部分：防污染检查清单

### 启动前验证
- [ ] 读取配置文件并验证债权人信息一致
- [ ] 输入材料路径包含正确的债权人标识

### 完成后自我验证
- [ ] 报告中的债权人名称 == "{creditor_name}"
- [ ] 报告中的债权人编号 == "{creditor_number}"
- [ ] 报告中的破产受理日期 == "{format_date_chinese(project_config['bankruptcy_date'])}"
- [ ] 报告内容对应该债权人的输入材料
- [ ] 文件已保存到正确的目录
- [ ] 仅处理了 prompt 指定的债权人 {creditor_name}

如以上任何一项不满足，请立即停止并报告问题。

---

**债权人**: {creditor_name}（编号 {creditor_number}）
**阶段**: 1 - 事实核查
**模式**: 并行处理
"""

    return prompt


def generate_stage2_prompt(batch, creditor_number, creditor_name, project_config):
    """Generate Stage 2 (Debt Analysis) prompt"""

    creditor_config = load_creditor_config(batch, creditor_number, creditor_name)
    if not creditor_config:
        return None

    processing_date = creditor_config['creditor_info']['processing_date']

    # Paths
    config_file_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / ".processing_config.json"
    fact_check_report_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "工作底稿" / f"{creditor_name}_事实核查报告.md"
    output_work_papers_dir = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "工作底稿"
    output_calculation_dir = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "计算文件"

    # Verify fact-check report exists
    if not fact_check_report_path.exists():
        print(f"❌ Error: Fact-check report not found: {fact_check_report_path}")
        print(f"   Stage 1 must be completed before Stage 2.")
        return None

    prompt = f"""# 债权人{creditor_name} - 债权分析并行处理任务

## ⚠️ 重要说明：并行处理模式

你正在**并行处理模式**下工作。本次任务**仅处理债权人 {creditor_name}**，不要处理任何其他债权人。

**关键要求**:
- **必须**读取该债权人的事实核查报告作为分析依据
- **必须**使用 calculator 工具进行所有利息计算
- 仅处理本 prompt 中明确指定的债权人

---

## 第一部分：债权人身份标识

**批次号**: {batch}
**债权人编号**: {creditor_number}
**债权人名称**: {creditor_name}
**处理日期**: {processing_date}

---

## 第二部分：配置文件路径

**配置文件路径**:
```
{config_file_path}
```

---

## 第三部分：前置报告路径（关键依赖）

**事实核查报告路径（绝对路径）**:
```
{fact_check_report_path}
```

**读取要求（防污染关键）**:
1. **必须**读取此报告作为分析依据，不得使用其他债权人的报告
2. 读取后验证报告中的债权人信息:
   - 报告中的债权人名称 == "{creditor_name}"
   - 报告中的债权人编号 == "{creditor_number}"
3. 验证报告中的破产日期与本 prompt 一致
4. 如验证失败，**立即停止**并报告错误

---

## 第四部分：输出目录路径

**工作底稿目录**:
```
{output_work_papers_dir}
```

**计算文件目录**:
```
{output_calculation_dir}
```

**输出文件**:
1. 债权分析报告: `{creditor_name}_债权分析报告.md`（保存到工作底稿目录）
2. 计算文件: `{creditor_name}_[计算类型].xlsx` 或 `.csv`（保存到计算文件目录）

---

## 第五部分：关键参数

**破产受理日期**: {project_config['bankruptcy_date']}
**停止计息日期**: {project_config['interest_stop_date']}
**债务人名称**: {project_config['debtor_name']}

**日期交叉验证要求**:
1. 与事实核查报告中的日期一致
2. 如发现不一致，**立即停止**并报告详细的不一致信息
3. 所有利息计算必须使用 {project_config['interest_stop_date']} 作为截止日期

---

## 第六部分：任务指令

请按照 debt-claim-analyzer agent 的标准工作流程执行债权分析。

**关键提醒**:
- **必须使用 calculator 工具**: `/root/debt_review_skills/universal_debt_calculator_cli.py`
- 应用就低原则和就无原则
- 记录完整的计算命令

**完整任务要求**: 参考 `.claude/agents/debt-claim-analyzer.md` 和 `debt-claim-analysis` skill。

---

## 第七部分：防污染检查清单

### 启动前验证
- [ ] 事实核查报告存在且债权人信息正确
- [ ] 日期在 prompt、配置、事实核查报告中一致

### 完成后自我验证
- [ ] 分析报告中的债权人信息正确
- [ ] 所有计算使用了 calculator 工具
- [ ] 计算文件已保存到正确目录
- [ ] 仅处理了 prompt 指定的债权人

---

**债权人**: {creditor_name}（编号 {creditor_number}）
**阶段**: 2 - 债权分析
**模式**: 并行处理
"""

    return prompt


def generate_stage3_prompt(batch, creditor_number, creditor_name, project_config):
    """Generate Stage 3 (Report Organization) prompt"""

    creditor_config = load_creditor_config(batch, creditor_number, creditor_name)
    if not creditor_config:
        return None

    processing_date = creditor_config['creditor_info']['processing_date']

    # Paths
    config_file_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / ".processing_config.json"
    fact_check_report_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "工作底稿" / f"{creditor_name}_事实核查报告.md"
    debt_analysis_report_path = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "工作底稿" / f"{creditor_name}_债权分析报告.md"
    output_final_reports_dir = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}" / "最终报告"
    base_dir = OUTPUT_BASE_DIR / f"第{batch}批债权" / f"{creditor_number}-{creditor_name}"

    # Verify both reports exist
    if not fact_check_report_path.exists():
        print(f"❌ Error: Fact-check report not found: {fact_check_report_path}")
        return None
    if not debt_analysis_report_path.exists():
        print(f"❌ Error: Debt analysis report not found: {debt_analysis_report_path}")
        return None

    prompt = f"""# 债权人{creditor_name} - 报告整理并行处理任务

## ⚠️ 重要说明：并行处理模式

你正在**并行处理模式**下工作。本次任务**仅处理债权人 {creditor_name}**。

**关键要求**:
- **必须**读取该债权人的两个技术报告（事实核查、债权分析）
- **不修改**技术报告的任何结论或金额

---

## 第一部分：债权人身份标识

**批次号**: {batch}
**债权人编号**: {creditor_number}
**债权人名称**: {creditor_name}
**处理日期**: {processing_date}

---

## 第二部分：配置文件路径

**配置文件路径**:
```
{config_file_path}
```

---

## 第三部分：前置报告路径（关键依赖）

### 3.1 事实核查报告

**报告路径**:
```
{fact_check_report_path}
```

### 3.2 债权分析报告

**报告路径**:
```
{debt_analysis_report_path}
```

### 3.3 两个报告的交叉验证（防污染关键）

**关键验证**:
- [ ] 两个报告的债权人名称完全一致
- [ ] 两个报告的破产受理日期完全一致
- [ ] 两个报告的申报金额一致

如不一致: **立即停止**

---

## 第四部分：输出目录路径

**最终报告目录**:
```
{output_final_reports_dir}
```

**债权人根目录**（文件清单保存位置）:
```
{base_dir}
```

**输出文件**:
1. 审查意见表: `GY2025_{creditor_name}_债权审查报告_{processing_date}.md`
2. 文件清单: `文件清单.md`

---

## 第五部分：关键参数

**破产受理日期**: {project_config['bankruptcy_date']}
**停止计息日期**: {project_config['interest_stop_date']}
**债务人名称**: {project_config['debtor_name']}

---

## 第六部分：任务指令

请按照 report-organizer agent 的标准工作流程执行报告整理。

**关键原则**:
- 内容保真（不修改技术报告的结论和金额）
- 模板忠实（遵循GY2025七章节格式）

**完整任务要求**: 参考 `.claude/agents/report-organizer.md` 和 `report-organization` skill。

---

## 第七部分：防污染检查清单

### 启动前验证
- [ ] 两个技术报告都存在
- [ ] 两个报告的债权人信息一致
- [ ] 两个报告的日期一致

### 完成后自我验证
- [ ] 审查意见表包含正确的债权人信息
- [ ] 金额与债权分析报告完全一致（未修改）
- [ ] 文件清单仅列出本债权人的文件

---

**债权人**: {creditor_name}（编号 {creditor_number}）
**阶段**: 3 - 报告整理
**模式**: 并行处理
"""

    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="Generate parallel processing prompts for debt review system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Stage 1 prompts for 5 creditors
  python parallel_prompt_generator.py --stage 1 --batch 1 --creditors 115,118,124,134,140

  # Generate Stage 2 prompts for 2 creditors
  python parallel_prompt_generator.py --stage 2 --batch 1 --creditors 115,118

  # Generate all stages for one creditor
  python parallel_prompt_generator.py --stage all --batch 1 --creditors 115
        """
    )

    parser.add_argument('--stage', type=str, required=True,
                       choices=['1', '2', '3', 'all'],
                       help='Processing stage: 1 (fact-check), 2 (analysis), 3 (organize), or all')
    parser.add_argument('--batch', type=int, required=True,
                       help='Batch number (e.g., 1 for 第1批债权)')
    parser.add_argument('--creditors', type=str, required=True,
                       help='Comma-separated creditor numbers (e.g., "115,118,124")')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for generated prompts (default: current directory)')

    args = parser.parse_args()

    # Parse creditor numbers
    try:
        creditor_numbers = [int(num.strip()) for num in args.creditors.split(',')]
    except ValueError:
        print("❌ Error: Invalid creditor numbers format. Use comma-separated integers.")
        sys.exit(1)

    # Load project config
    print("📖 Loading project configuration...")
    project_config = load_project_config()
    print(f"   Bankruptcy date: {project_config['bankruptcy_date']}")
    print(f"   Interest stop date: {project_config['interest_stop_date']}")
    print(f"   Debtor: {project_config['debtor_name']}")
    print()

    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Default: use each creditor's parallel_prompts directory
        # (will be handled per-creditor in the save logic)
        output_dir = None

    # Get creditor names
    print("🔍 Identifying creditors...")
    creditors = []
    for num in creditor_numbers:
        name = get_creditor_name_from_input(args.batch, num)
        if not name:
            print(f"❌ Error: Could not find creditor name for number {num} in batch {args.batch}")
            print(f"   Expected input file: 输入/第{args.batch}批债权/{num}.[名称].md")
            sys.exit(1)
        creditors.append((num, name))
        print(f"   ✅ Creditor {num}: {name}")
    print()

    # Generate prompts
    stages = ['1', '2', '3'] if args.stage == 'all' else [args.stage]

    for stage in stages:
        print(f"🚀 Generating Stage {stage} prompts...")

        generator_func = {
            '1': generate_stage1_prompt,
            '2': generate_stage2_prompt,
            '3': generate_stage3_prompt
        }[stage]

        for num, name in creditors:
            prompt = generator_func(args.batch, num, name, project_config)

            if prompt is None:
                print(f"   ❌ Failed to generate prompt for creditor {num}")
                continue

            # Determine output location
            if output_dir is None:
                # Default: save to creditor's parallel_prompts directory
                creditor_config = load_creditor_config(args.batch, num, name)
                if creditor_config and 'paths' in creditor_config and 'parallel_prompts' in creditor_config['paths']:
                    prompt_dir = Path(creditor_config['paths']['parallel_prompts'])
                else:
                    # Fallback if config doesn't have the path yet (for backward compatibility)
                    prompt_dir = OUTPUT_BASE_DIR / f"第{args.batch}批债权" / f"{num}-{name}" / "并行处理prompts"
                prompt_dir.mkdir(parents=True, exist_ok=True)
                output_file = prompt_dir / f"stage{stage}_creditor{num}_{name}_prompt.txt"
            else:
                # User-specified output directory
                output_file = output_dir / f"stage{stage}_creditor{num}_{name}_prompt.txt"

            # Save prompt to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(prompt)

            print(f"   ✅ Generated: {output_file}")

        print()

    print("✅ All prompts generated successfully!")
    if output_dir:
        print(f"📂 Output directory: {output_dir.absolute()}")
    else:
        print(f"📂 Prompts saved to each creditor's 并行处理prompts/ subdirectory")
    print()
    print("Next steps:")
    print("1. Review the generated prompts")
    print("2. Copy each prompt into a Task call in Claude Code")
    print("3. Launch all Tasks in a single message for parallel execution")


if __name__ == '__main__':
    main()
