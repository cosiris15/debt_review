# Workflow Initialization Guide

## Purpose

Comprehensive guide for environment initialization procedures, configuration management, and troubleshooting initialization issues.

## Initialization Overview

Environment initialization is **MANDATORY** before processing each creditor. It establishes standard directory structure, configuration files, and bankruptcy date context for all subsequent agent work.

## Part 1: Pre-Initialization Requirements

### System Requirements Check

Before initialization, verify:
```
□ Python 3.x installed and accessible
□ 债权处理工作流控制器.py script exists
□ project_config.ini exists and contains bankruptcy dates
□ 输出/ directory exists with write permissions
□ Sufficient disk space for outputs
```

### Project Configuration Verification

**File**: `project_config.ini` (at project root)

**Required Sections**:
```ini
[项目基本信息]
债务人名称 = [公司名称]
项目代码 = [代码如GY2025]

[关键日期]
破产受理日期 = YYYY-MM-DD
停止计息日期 = YYYY-MM-DD  # Must be 破产受理日期 - 1 day
```

**Verification Steps**:
1. Read `project_config.ini`
2. Verify bankruptcy date format (YYYY-MM-DD)
3. Verify interest stop date = bankruptcy date - 1
4. Verify debtor name matches project context

**If project_config.ini missing or invalid**:
- STOP: Cannot proceed with any creditor processing
- Create/correct project_config.ini first
- Verify dates with authoritative source (court documents)

## Part 2: Running the Initialization Script

### Command Syntax

```bash
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

**Parameters**:
- `<批次号>`: Batch number (e.g., 1, 2, 3)
- `<债权人编号>`: Creditor number (e.g., 115, 116)
- `<债权人名称>`: Full creditor name (e.g., 慈溪市东航建筑起重机械安装队)

**Example**:
```bash
python 债权处理工作流控制器.py 1 115 慈溪市东航建筑起重机械安装队
```

### Expected Output

Successful initialization displays:
```
🚀 初始化债权人处理环境
   批次: 第1批
   编号: 115
   名称: 慈溪市东航建筑起重机械安装队

✓ 创建目录: /root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队/工作底稿
✓ 创建目录: /root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队/最终报告
✓ 创建目录: /root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队/计算文件
✓ 保存处理配置: [path]/.processing_config.json
✓ 目录结构验证通过: [base_path]
✅ 债权人处理环境初始化完成

📋 工作流程摘要
   基础目录: [path]
   工作底稿: [path]/工作底稿
   计算文件: [path]/计算文件
   最终报告: [path]/最终报告

📝 预期文件:
   事实核查: {债权人名称}_事实核查报告.md
   债权分析: {债权人名称}_债权分析报告.md
   审查意见: GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md
   文件清单: 文件清单.md

✅ 环境准备完成，可以开始债权审查流程
   请按照以下顺序执行Agent:
   1. debt-fact-checker (事实核查员)
   2. debt-claim-analyzer (债权分析员)
   3. report-organizer (报告整理员)
```

## Part 3: Directory Structure Created

### Standard Structure

```
输出/第X批债权/[编号]-[债权人名称]/
├── .processing_config.json          # Processing configuration
├── 工作底稿/                         # Working papers directory
├── 最终报告/                         # Final reports directory
└── 计算文件/                         # Calculation files directory
```

**Directory Purposes**:
- **工作底稿/** (Working Papers): Technical reports for internal use
  - `{债权人名称}_事实核查报告.md`
  - `{债权人名称}_债权分析报告.md`
- **最终报告/** (Final Reports): Client deliverables
  - `GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md`
- **计算文件/** (Calculation Files): Audit trail
  - `{债权人名称}_{计算类型}.xlsx`
  - `{债权人名称}_{计算类型}.csv`
  - `{债权人名称}_无计算项说明.txt` (if no calculations)

### Directory Permissions

All directories created with:
- Read/write/execute for owner
- Group and other permissions as per system defaults
- Verified accessible before agent execution

## Part 4: Configuration File (.processing_config.json)

### File Location

`.processing_config.json` is placed at creditor base directory:
```
输出/第X批债权/[编号]-[债权人名称]/.processing_config.json
```

### File Structure

```json
{
  "creditor_info": {
    "batch_number": "1",
    "creditor_number": "115",
    "creditor_name": "慈溪市东航建筑起重机械安装队",
    "processing_date": "20251023"
  },
  "paths": {
    "base_directory": "/root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队",
    "work_papers": "/root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队/工作底稿",
    "final_reports": "/root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队/最终报告",
    "calculation_files": "/root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队/计算文件"
  },
  "file_templates": {
    "fact_check_report": "慈溪市东航建筑起重机械安装队_事实核查报告.md",
    "analysis_report": "慈溪市东航建筑起重机械安装队_债权分析报告.md",
    "final_review": "GY2025_慈溪市东航建筑起重机械安装队_债权审查报告_20251023.md",
    "file_inventory": "文件清单.md"
  },
  "project_config": {
    "bankruptcy_date": "2025-05-12",
    "interest_stop_date": "2025-05-11",
    "debtor_name": "浙江某某集团有限公司"
  }
}
```

### Critical Configuration Fields

**creditor_info**: Identifies the specific creditor and batch
**paths**: Absolute paths to all output directories (NEVER use relative paths)
**file_templates**: Expected filenames for all agent outputs
**project_config**: **LIFELINE-LEVEL CRITICAL** - bankruptcy dates determine all calculations

### Configuration Usage by Agents

**debt-fact-checker**:
- Reads `project_config.bankruptcy_date` for fact timeline context
- Uses `paths.work_papers` for output location
- Uses `file_templates.fact_check_report` for filename

**debt-claim-analyzer**:
- Reads `project_config.bankruptcy_date` and `interest_stop_date` for calculations
- Uses `paths.work_papers` for report output
- Uses `paths.calculation_files` for calculation files
- Uses `file_templates.analysis_report` for filename

**report-organizer**:
- Reads all fields for cross-verification
- Uses `paths.final_reports` for deliverable output
- Uses `file_templates.final_review` and `file_templates.file_inventory` for filenames

## Part 5: Post-Initialization Verification

### Verification Checklist

**Run after initialization before calling any agent:**

```
□ Directory Structure:
  □ Base directory exists: 输出/第X批债权/[编号]-[债权人名称]/
  □ 工作底稿/ subdirectory exists
  □ 最终报告/ subdirectory exists
  □ 计算文件/ subdirectory exists

□ Configuration File:
  □ .processing_config.json exists in base directory
  □ File is valid JSON (no syntax errors)
  □ All required sections present: creditor_info, paths, file_templates, project_config

□ Bankruptcy Dates:
  □ bankruptcy_date present and format YYYY-MM-DD
  □ interest_stop_date = bankruptcy_date - 1 day
  □ Dates match project_config.ini

□ Path Accessibility:
  □ All paths in config are absolute (not relative)
  □ All directories are writable
  □ No permission errors

□ File Templates:
  □ Filenames follow naming conventions
  □ Creditor name correctly embedded in filenames
```

### Verification Commands

**Check directory structure**:
```bash
ls -la 输出/第X批债权/[编号]-[债权人名称]/
```

**Verify configuration file**:
```bash
cat 输出/第X批债权/[编号]-[债权人名称]/.processing_config.json
```

**Validate JSON syntax**:
```bash
python -m json.tool 输出/第X批债权/[编号]-[债权人名称]/.processing_config.json
```

## Part 6: Troubleshooting Initialization Issues

### Issue 1: Script Not Found

**Symptom**: `python: can't open file '债权处理工作流控制器.py'`

**Cause**: Script not in current directory or incorrect path

**Resolution**:
1. Verify current directory: `pwd`
2. Check script location: `ls -la | grep 债权处理工作流控制器.py`
3. Change to correct directory or use full path
4. Re-run initialization command

### Issue 2: Permission Denied

**Symptom**: `PermissionError: [Errno 13] Permission denied: '输出/...'`

**Cause**: Insufficient permissions to create directories

**Resolution**:
1. Check output directory permissions: `ls -la 输出/`
2. Verify user has write access
3. If needed, adjust permissions: `chmod u+w 输出/`
4. Re-run initialization

### Issue 3: project_config.ini Not Found

**Symptom**: `⚠️  警告：项目配置文件不存在 [path]/project_config.ini`

**Cause**: Project configuration file missing

**Resolution**:
1. Verify project_config.ini location
2. Create project_config.ini with required sections if missing
3. Populate with bankruptcy dates from authoritative source
4. Re-run initialization

### Issue 4: Invalid Bankruptcy Dates

**Symptom**: Empty or malformed dates in .processing_config.json

**Cause**: project_config.ini missing or has incorrect format

**Resolution**:
1. Open project_config.ini
2. Verify [关键日期] section exists
3. Check date format: YYYY-MM-DD
4. Verify interest_stop_date = bankruptcy_date - 1
5. Correct dates and re-run initialization

### Issue 5: Directory Already Exists

**Symptom**: Directories already present from previous run

**Cause**: Re-initializing same creditor

**Resolution**:
- **If processing fresh**: Delete existing directory and re-initialize
- **If continuing processing**: No re-initialization needed, proceed to agents
- **If correcting error**: Archive existing directory, then re-initialize

**Command to check existing status**:
```bash
ls -la 输出/第X批债权/[编号]-[债权人名称]/
```

### Issue 6: Chinese Character Encoding Issues

**Symptom**: Garbled Chinese characters in filenames or paths

**Cause**: Terminal or system encoding not set to UTF-8

**Resolution**:
1. Set environment encoding: `export LANG=zh_CN.UTF-8`
2. Verify Python encoding: Script uses `encoding='utf-8'`
3. Re-run initialization
4. If persistent: Check system locale settings

## Part 7: Re-Initialization Scenarios

### When to Re-Initialize

**Must re-initialize if**:
- Processing new creditor for first time
- Previous initialization failed or incomplete
- Configuration needs correction (bankruptcy dates changed)
- Directory structure was corrupted or deleted

**Do NOT re-initialize if**:
- Processing in progress (agents already working)
- Previous processing completed successfully
- Only individual agent needs re-run

### Safe Re-Initialization Process

If re-initialization needed:
1. **Archive existing work** (if any):
   ```bash
   mv 输出/第X批债权/[编号]-[债权人名称]/ 归档文件/[名称]_[日期]/
   ```
2. **Run initialization script**:
   ```bash
   python 债权处理工作流控制器.py [batch] [number] [name]
   ```
3. **Verify fresh environment** (checklist in Part 5)
4. **Resume from beginning** of agent workflow

## Part 8: Initialization Best Practices

### DO

✅ **Always initialize before first agent**: Never skip this step
✅ **Verify configuration after initialization**: Check bankruptcy dates immediately
✅ **Use consistent naming**: Match creditor names across all references
✅ **Document initialization time**: For audit trail
✅ **Keep project_config.ini updated**: Central source of truth

### DO NOT

❌ **Never skip initialization**: Even if "just testing"
❌ **Never manually create directories**: Use script for consistency
❌ **Never use relative paths**: Always absolute paths in configuration
❌ **Never guess bankruptcy dates**: Always verify from authoritative source
❌ **Never modify .processing_config.json manually**: Regenerate via script if changes needed

## Part 9: Integration with Agent Workflow

### From Initialization to Fact-Checking

**After successful initialization**:
1. Verify all checkpoints passed
2. Note bankruptcy dates from configuration
3. Prepare raw debt claim materials
4. Call **debt-fact-checker** agent with:
   - Base directory path
   - Raw materials location
   - Reference to .processing_config.json

### Configuration Flow

```
project_config.ini (master config)
         ↓
债权处理工作流控制器.py (initialization script)
         ↓
.processing_config.json (creditor-specific config)
         ↓
Agent 1: debt-fact-checker (reads config, outputs to 工作底稿/)
         ↓
Agent 2: debt-claim-analyzer (reads config, outputs to 工作底稿/ and 计算文件/)
         ↓
Agent 3: report-organizer (reads config, outputs to 最终报告/)
```

## Summary

**Initialization is the foundation** of quality debt review:
- Creates standard structure
- Establishes bankruptcy date context
- Provides configuration for all agents
- Ensures output consistency

**Key Success Factors**:
1. Always run initialization first
2. Verify bankruptcy dates immediately
3. Check all verification points
4. Never skip or shortcut the process

**Remember**: A proper initialization prevents 90% of downstream errors. Time spent on initialization verification is time saved on debugging and rework.
