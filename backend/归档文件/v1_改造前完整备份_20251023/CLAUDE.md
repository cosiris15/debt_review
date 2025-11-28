# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. You are an agentic system to process and review debt claim files with certain SOP and scripts.

## ⚠️ CRITICAL: Project Configuration & Date Verification
**ALWAYS read `project_config.ini` FIRST before processing any debt claims!**
This file contains project-specific information like bankruptcy filing dates that MUST be loaded.
All date calculations and project-specific processing depend on these configurations.

### 🚨 MANDATORY DATE VERIFICATION PROTOCOL
**破产受理日期是债权审查的生命线！**

#### For ALL Agents - No Exceptions:
1. **Before Starting Work**: MUST verify bankruptcy date from `.processing_config.json`
2. **Cross-Verification**: Compare with previous agent reports (if applicable)
3. **Record in Report**: Explicitly document the dates used in all outputs
4. **Stop on Inconsistency**: Halt work immediately if any date discrepancy is found

#### Critical Importance:
- **Bankruptcy Date (破产受理日期)**: Determines all legal deadlines and interest calculations
- **Interest Stop Date (停止计息日期)**: Must be bankruptcy date minus 1 day
- **Wrong Dates = Invalid Results**: Any error renders the entire debt analysis useless

#### Verification Commands:
```bash
# Verify environment includes correct dates
python 环境初始化检查器.py <batch> <number> <name>
```

**Remember**: A single date error can invalidate months of work and mislead client decisions!

## Commands

### Initialize Debt Processing Environment (MANDATORY)
```bash
# MUST run before processing each creditor
python 债权处理工作流控制器.py <batch_number> <creditor_number> <creditor_name>
# Example:
python 债权处理工作流控制器.py 1 115 慈溪市东航建筑起重机械安装队
```

### Check Environment Status (Optional)
```bash
# Check if environment is properly initialized
python 环境初始化检查器.py <batch_number> <creditor_number> <creditor_name>
# Example:
python 环境初始化检查器.py 1 115 慈溪市东航建筑起重机械安装队

# Or check by path:
python 环境初始化检查器.py /root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队
```

### Run the Debt Interest Calculator
```bash
# Basic simple interest calculation
python universal_debt_calculator_cli.py simple --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --rate 4.35

# LPR floating rate calculation
python universal_debt_calculator_cli.py lpr --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --multiplier 1.5

# Delayed performance double interest calculation
python universal_debt_calculator_cli.py delay --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31

# Compound interest calculation
python universal_debt_calculator_cli.py compound --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --rate 4.35 --cycle "每月末"

# JSON input/output mode
python universal_debt_calculator_cli.py simple --json-input input.json --json-output result.json
```

## Architecture Overview

This is a **Multi-Agent Debt Review System** (多智能体债权审查系统) designed for systematic debt claim analysis in bankruptcy proceedings. The system uses a three-agent collaborative approach:

### Core Components

0. **Project Configuration** (`project_config.ini`) - **MUST BE LOADED FIRST**
   - Contains all project-specific information (bankruptcy dates, debtor names, etc.)
   - CRITICAL: Read this file at the start of EVERY debt processing session
   - All date calculations depend on these configurations
   - Key dates: bankruptcy filing date, interest stop date

1. **Universal Debt Calculator** (`universal_debt_calculator_cli.py`)
   - Standalone CLI tool for calculating various types of debt interest
   - Supports simple interest, LPR floating rates, delayed performance interest, and compound interest
   - Includes embedded LPR rate data (2019-2025)
   - No external dependencies, uses only Python standard library
   - Generates Excel/CSV calculation process tables for audit trail

2. **Three-AI-Agent System** (三智能体系统)
   - **Fact Checker Agent** (事实核查员): Extracts and verifies debt claim information from submitted materials
   - **Debt Analyst Agent** (债权分析员): Performs amount analysis, interest calculations, statute of limitations determination, and **generates calculation process table files for each debt claim**
   - **Report Organizer Agent** (报告整理员): Consolidates technical reports into standardized 审查意见表 (review opinion forms)

### Workflow

⚠️ **STEP 0: ALWAYS load project_config.ini first!**

Follow the 智能体债权审查SOP.md!

## 📋 主控制者责任 (Your Primary Responsibilities)

**作为债权审查流程的主控制者，你必须：**

### 1. 环境初始化责任 ⚠️ MANDATORY
**在处理每个债权人之前，必须执行：**
```bash
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

**验证初始化完成：**
- 确认标准目录结构已创建
- 确认配置文件 `.processing_config.json` 存在
- 如果环境未初始化，**禁止调用任何Agent**

### 2. Agent协调责任
**严格按此顺序执行Agent：**
1. **debt-fact-checker** → 生成事实核查报告
2. **debt-claim-analyzer** → 生成债权分析报告和计算文件  
3. **report-organizer** → 生成审查意见表和文件清单

### 3. 质量监控责任
**每个Agent完成后验证：**
- 文件存在于正确目录位置
- 文件命名符合规范
- 没有文件散落在错误位置

## 🔄 标准处理流程

The system processes debt claims sequentially:
0. **Load project_config.ini** → Get bankruptcy dates and project info
1. **⚠️ YOU MUST: Initialize environment** → Run 债权处理工作流控制器.py for each creditor
2. Raw materials → Fact Checker → structured fact extraction (to `工作底稿/`)
3. Fact report → Debt Analyst → amount analysis & calculations (to `工作底稿/` and `计算文件/`)
4. Two technical reports → Report Organizer → 审查意见表 (to `最终报告/` + `文件清单.md`)
5. Final output → Standardized directory structure with all files properly organized
6. Do not write new codes to complete your task unless it is inevitable! Use your agentic ability to accomplish the task.

**Important**: 
- Each debt claim must be processed independently with its own output report
- Each debt claim must have its own calculation process table file (Excel/CSV) or explanation file (TXT if no calculations)
- Batch processing of multiple claims in parallel is explicitly prohibited

**File Path Verification Rule**:
- When using Write tool, ALWAYS first run `ls` command (or similar) to confirm the correct directory
- Never guess file paths - if unclear, follow project settings or file context (e.g., 债权处理工作流控制器.py)  
- Verify directory exists before creating files
- Use absolute paths as defined in the initialization scripts

### Key Standards Documents

- **`project_config.ini`**: Project-specific configuration (LOAD FIRST!)
- `智能体债权审查SOP.md`: Overall system workflow and collaboration rules
- `事实核查员工作标准.md`: Defines fact-checking procedures and output formats
- `债权分析员工作标准.md`: Defines debt analysis procedures and calculation methods
- `报告整理员工作标准.md`: Defines report consolidation and 审查意见表 standards
- `审查意见表模板.md`: Review opinion form template (to be customized per client)

### Data Organization

**Input/Output Separation Design:**
- `/输入/第1批债权/`, `/输入/第2批债权/`, etc.: Input directories for raw debt claim materials
- `/输出/`: Output directory for processed results (reports and calculation files)
- `事实核查报告模板.md`: Template and example for fact-checker reports
- `债权分析报告模板.md`: Template and example for debt analyst reports

**Directory Structure:**
```
/root/debt_review_solution/
├── 输入/                          # Raw debt claim materials
│   ├── 第1批债权/
│   │   ├── 115.慈溪市东航建筑起重机械安装队.md
│   │   └── ...
│   ├── 第2批债权/
│   └── 第3批债权/
│
├── 输出/                          # Processing results
│   ├── 第1批债权/
│   │   └── 115-慈溪市东航建筑起重机械安装队/
│   │       ├── 工作底稿/         # Working papers
│   │       ├── 最终报告/         # Final reports
│   │       └── 计算文件/         # Calculation files
│   └── ...
│
├── project_config.ini            # Project configuration (MUST load first)
├── 债权处理工作流控制器.py        # Workflow controller
├── 环境初始化检查器.py            # Environment checker
├── universal_debt_calculator_cli.py
└── ...
```