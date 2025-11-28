---
name: debt-workflow-orchestration
description: Main controller workflow for orchestrating three-agent debt review system. Handles environment initialization, agent coordination, sequential processing, quality control checkpoints, and exception management. Essential for coordinating debt-fact-checker, debt-claim-analyzer, and report-organizer agents.
---

# Debt Workflow Orchestration Skill

## Overview

This skill defines the main controller responsibilities for orchestrating the three-agent debt review system. It ensures proper environment initialization, sequential agent execution, quality control, and standardized output management.

## When to Use This Skill

- Starting debt claim processing workflow
- Coordinating three specialized agents (fact-checker, analyzer, organizer)
- Managing batch processing of multiple creditors
- Ensuring quality control and standardization
- Handling workflow exceptions and errors

## Core Responsibilities

As the main controller, you must:

1. **Environment Initialization** (MANDATORY): Prepare processing environment for each creditor
2. **Agent Coordination**: Execute agents in strict sequence (fact-checker → analyzer → organizer)
3. **Quality Monitoring**: Verify each agent's output meets standards
4. **Process Control**: Ensure sequential processing, never parallel batch processing
5. **Exception Management**: Handle errors and edge cases appropriately

## Part 1: Automatic Environment Initialization

### ⚠️ MANDATORY Pre-Processing Step (AUTOMATIC)

**🔑 Key Principle: Environment initialization is AUTOMATIC and TRANSPARENT to user**

User only needs to say: "Please process creditor X"
System automatically handles initialization without user intervention.

### Automatic Initialization Logic

**Step 1: Auto-Detect Environment Status**

Before processing any creditor, automatically check:
```bash
# Check if configuration file exists
File path: 输出/第<批次>批债权/<编号>-<债权人名称>/.processing_config.json
```

**Step 2: Auto-Initialize (if needed)**

```
IF .processing_config.json NOT found:
  → Automatically execute: python 债权处理工作流控制器.py <批次> <编号> <名称>
  → Inform user: "Initializing processing environment..."
  → Verify initialization completed successfully

ELSE:
  → Skip initialization
  → Proceed directly to agent execution
```

**Step 3: Verify Initialization**

After auto-initialization, confirm:
```
□ Standard directories created:
  - 工作底稿/ (working papers)
  - 最终报告/ (final reports)
  - 计算文件/ (calculation files)
□ .processing_config.json exists and is valid
□ Configuration contains bankruptcy dates from project_config.ini
□ Directory paths are accessible
```

### What Initialization Creates

The workflow controller automatically creates:
- **Standard directory structure** (`工作底稿/`, `最终报告/`, `计算文件/`)
- **Processing configuration** (`.processing_config.json`)
- **File naming templates** (for all output files)
- **Bankruptcy date configuration** (loaded from `project_config.ini`)

### User Experience

✅ **What user says**: "Please process 第1批债权第115号债权人"

✅ **What system does**:
1. Auto-detect: Check if environment initialized
2. Auto-initialize: Run script if needed (transparent to user)
3. Execute: Start three-agent workflow
4. Output: Save results to standard directories

❌ **What user does NOT need to say**: "Please initialize environment first"

**Principle**: Initialization is a system implementation detail, not a user concern

### Configuration File Contents

The `.processing_config.json` contains:
- **creditor_info**: Batch number, creditor number, name, processing date
- **paths**: Base directory, work papers, final reports, calculation files
- **file_templates**: Standard filenames for all outputs
- **project_config**: Bankruptcy date, interest stop date, debtor name

## Part 2: Sequential Workflow Execution

### Mandatory Processing Sequence

**⚠️ CRITICAL**: Process ONE claim at a time through complete workflow

```
✅ CORRECT (Serial Processing):
Claim 1: Initialize → Fact Check → Analyze → Organize → Complete ✓
Claim 2: Initialize → Fact Check → Analyze → Organize → Complete ✓
Claim 3: Initialize → Fact Check → Analyze → Organize → Complete ✓

❌ WRONG (Batch Processing):
Claims 1,2,3: All Initialize → All Fact Check → All Analyze → All Organize
```

**Rationale**: Each claim requires complete independent review to ensure quality and traceability.

### Three-Stage Execution

#### Stage 1: Fact-Checking (debt-fact-checker)
**Goal**: Extract and verify basic facts from debt claim materials

**Agent Invocation**:
```
Call: debt-fact-checker agent
Input: Raw debt claim materials from 输入/第X批债权/
Output: 事实核查报告.md to 工作底稿/
```

**Verification Before Proceeding**:
```
□ 事实核查报告.md exists in 工作底稿/
□ Report contains complete fact-finding information
□ Bankruptcy dates verified and recorded
□ Evidence timeline created
□ No critical information missing
```

#### Stage 2: Debt Analysis (debt-claim-analyzer)
**Goal**: Analyze amounts, calculate interest, determine statute of limitations

**Agent Invocation**:
```
Call: debt-claim-analyzer agent
Input: 事实核查报告.md from 工作底稿/
Output:
  - 债权分析报告.md to 工作底稿/
  - Calculation files to 计算文件/ (Excel/CSV or TXT explanation)
```

**Verification Before Proceeding**:
```
□ 债权分析报告.md exists in 工作底稿/
□ Report contains complete analysis and calculations
□ Calculator tool used for ALL calculations
□ Calculation process files generated in 计算文件/
□ Bankruptcy dates cross-verified with fact report
□ No calculation errors detected
```

#### Stage 3: Report Organization (report-organizer)
**Goal**: Consolidate technical reports into standardized review opinion form

**Agent Invocation**:
```
Call: report-organizer agent
Input: Both technical reports from 工作底稿/
Output:
  - 审查意见表.md to 最终报告/
  - 文件清单.md to base directory
```

**Verification on Completion**:
```
□ 审查意见表.md exists in 最终报告/
□ Report follows client template format
□ Content accuracy preserved (no modifications)
□ File naming complies with standards
□ 文件清单.md generated with complete inventory
□ All dates consistent across three reports
```

## Part 3: Quality Control Checkpoints

### Checkpoint 1: After Fact-Checker

**Date Verification (MANDATORY)**:
```
□ Bankruptcy date verified from .processing_config.json
□ Interest stop date correctly recorded (bankruptcy date - 1)
□ Dates explicitly documented in report
```

**Content Quality**:
```
□ Declaration information complete and accurate
□ Basic debt relationships clearly identified
□ Timeline chronologically ordered
□ Evidence vs. declaration materials distinguished
□ All facts cite specific evidence sources
□ No unauthorized simplification or summarization
```

### Checkpoint 2: After Debt Analyzer

**Date Verification (MANDATORY)**:
```
□ Bankruptcy date re-verified from .processing_config.json
□ Cross-verified with fact-checker report (dates match)
□ All calculations use correct interest stop date
□ Statute analysis uses correct reference dates
```

**Calculation Quality**:
```
□ Calculator tool used for ALL interest calculations
□ Calculation commands documented in report
□ Excel/CSV process files generated
□ LPR term selection reviewed (1y vs 5y+)
□ Penalty caps verified (4× LPR maximum)
□ 就低原则 applied where calculation > declaration
□ 就无原则 applied (only declared items included)
```

**File Completeness**:
```
□ Debt analysis report in 工作底稿/
□ Calculation files in 计算文件/
□ All files properly named
```

### Checkpoint 3: After Report Organizer

**Date Verification (MANDATORY)**:
```
□ Bankruptcy dates consistent across all three reports
□ Final report contains correct dates
□ No date discrepancies in client deliverable
```

**Report Quality**:
```
□ Content extracted accurately from technical reports
□ Template format correctly applied
□ Professional language maintained
□ No information loss during consolidation
```

**File Organization**:
```
□ Final report in 最终报告/
□ File naming follows standard (GY2025_[债权人]_债权审查报告_[YYYYMMDD].md)
□ 文件清单.md complete and accurate
□ Directory structure complies with standards
```

## Part 4: Batch Processing Standards

### Multiple Creditors Processing

**Rule**: Process creditors serially, one complete workflow at a time

**Example** (3 creditors in batch):
```
1. Initialize creditor 1 environment
2. Run creditor 1 through: fact-check → analyze → organize
3. Verify creditor 1 outputs complete
4. Initialize creditor 2 environment
5. Run creditor 2 through: fact-check → analyze → organize
6. Verify creditor 2 outputs complete
7. Initialize creditor 3 environment
8. Run creditor 3 through: fact-check → analyze → organize
9. Verify creditor 3 outputs complete
```

### Output Independence

**Principle**: Each creditor gets independent, complete reports

**Requirements**:
- Each creditor has separate directory (第X批债权/[编号]-[债权人名称]/)
- Each creditor has three independent reports
- No cross-creditor consolidation or summary
- Each report must be usable standalone

## Part 5: Exception Handling

### Common Exception Scenarios

#### 1. Environment Not Initialized
**Symptom**: `.processing_config.json` missing or directories incomplete

**Action**:
```
1. STOP all agent work immediately
2. Run 债权处理工作流控制器.py for this creditor
3. Verify initialization successful
4. Resume from beginning of workflow
```

#### 2. Date Inconsistencies Detected
**Symptom**: Different bankruptcy dates in config vs. reports

**Action**:
```
1. STOP all work immediately
2. Identify authoritative source (project_config.ini)
3. Correct .processing_config.json if needed
4. Re-run affected agents with correct dates
5. DO NOT deliver reports with date errors
```

#### 3. Missing Input Materials
**Symptom**: Debt claim materials incomplete or missing

**Action**:
```
1. Document missing items specifically
2. Process available materials (do NOT guess or fabricate)
3. Mark report with "材料不完整" note
4. List specific missing evidence in report
```

#### 4. Calculator Tool Error
**Symptom**: universal_debt_calculator_cli.py fails or returns error

**Action**:
```
1. Verify command syntax correct
2. Check input parameters (dates, amounts, rates)
3. Retry with corrected parameters
4. If persistent error: Document issue in report
5. DO NOT use manual calculations as substitute
```

#### 5. Agent Output File Missing
**Symptom**: Expected report file not found in designated directory

**Action**:
```
1. Verify file naming matches template exactly
2. Check file saved in correct subdirectory
3. If file truly missing: Re-run the agent
4. DO NOT proceed to next stage without previous output
```

#### 6. Super-Long Materials (>100 pages or >50 evidence items)
**Symptom**: Materials exceed system processing capacity

**Action**:
```
1. Notify fact-checker agent of long material scenario
2. Agent should apply batch processing mechanism:
   - Batch 1: Core contracts and direct performance evidence
   - Batch 2: High-volume performance records (invoices, bank records)
   - Batch 3: Legal documents and summary materials
3. Agent consolidates batches into single unified report
4. Final report shows no traces of batching
```

### Error Escalation

**When to stop and report**: Date errors unresolvable from sources; fundamental evidence contradictions; persistent tool failures; work standards conflicts

**Error Documentation**: Issue description; resolution steps; sources consulted; recommended resolution

## Part 6: File and Directory Standards

### Standard Directory Structure

```
输出/第X批债权/[编号]-[债权人名称]/
├── .processing_config.json          # Processing configuration (auto-generated)
├── 工作底稿/                         # Working papers (internal)
│   ├── {债权人名称}_事实核查报告.md
│   └── {债权人名称}_债权分析报告.md
├── 最终报告/                         # Final reports (client deliverable)
│   └── GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md
├── 计算文件/                         # Calculation process files (audit trail)
│   ├── {债权人名称}_{计算类型}.xlsx
│   ├── {债权人名称}_{计算类型}.csv
│   └── {债权人名称}_无计算项说明.txt (if no calculations)
└── 文件清单.md                       # File inventory
```

### File Naming Standards

**Fact-checking report**: `{债权人名称}_事实核查报告.md`
**Debt analysis report**: `{债权人名称}_债权分析报告.md`
**Final review opinion**: `GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md`
**Calculation files**: `{债权人名称}_{计算类型}.xlsx`
**File inventory**: `文件清单.md`

### Path Management Rules

**MANDATORY Rules**:
1. Never use relative paths - always absolute paths
2. Always verify directory exists before writing files
3. Use paths from `.processing_config.json["paths"]`
4. Never scatter files outside standard directories

## Part 7: Workflow Execution Template

### Complete Single-Creditor Workflow

```
📋 WORKFLOW CHECKLIST: [债权人名称]

□ Step 0: Environment Initialization
  □ Run: python 债权处理工作流控制器.py [batch] [number] [name]
  □ Verify directories created
  □ Verify .processing_config.json exists
  □ Read and confirm bankruptcy dates

□ Step 1: Fact-Checking
  □ Call debt-fact-checker agent
  □ Input: Raw materials from 输入/第X批债权/
  □ Verify output: {债权人名称}_事实核查报告.md in 工作底稿/
  □ Quality check: Date verification, content completeness

□ Step 2: Debt Analysis
  □ Call debt-claim-analyzer agent
  □ Input: Fact-checker report from 工作底稿/
  □ Verify outputs:
    - {债权人名称}_债权分析报告.md in 工作底稿/
    - Calculation files in 计算文件/
  □ Quality check: Calculator usage, date consistency, file completeness

□ Step 3: Report Organization
  □ Call report-organizer agent
  □ Input: Both technical reports from 工作底稿/
  □ Verify outputs:
    - GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md in 最终报告/
    - 文件清单.md in base directory
  □ Quality check: Template compliance, content accuracy, file naming

✅ Workflow Complete for [债权人名称]
```

## Part 8: Quality Assurance Principles

### Zero-Tolerance Items

**These errors are NEVER acceptable**:
- ❌ Wrong bankruptcy dates in any report
- ❌ Manual calculations (not using calculator tool)
- ❌ Files in wrong directories
- ❌ Missing calculation process files
- ❌ Date inconsistencies between reports
- ❌ Starting next stage without completing previous stage

### Best Practices

**DO**:
- ✅ Initialize environment before every creditor
- ✅ Verify each checkpoint before proceeding
- ✅ Document all exceptions and resolution attempts
- ✅ Preserve complete audit trail
- ✅ Apply core principles (就低, 就无) consistently

**DO NOT**:
- ❌ Skip environment initialization
- ❌ Process multiple creditors in parallel
- ❌ Modify agent outputs during consolidation
- ❌ Guess or fabricate missing information
- ❌ Proceed with unresolved date inconsistencies

## Part 9: Key References

### For Detailed Procedures

**Workflow Initialization Reference**: See `references/workflow_initialization_guide.md`
- Detailed initialization procedures
- Configuration file structure
- Troubleshooting initialization issues

**Quality Control Reference**: See `references/quality_control_standards.md`
- Complete checkpoint checklists
- Quality verification procedures
- Common quality issues and prevention

**Exception Handling Reference**: See `references/exception_handling_guide.md`
- Comprehensive exception scenarios
- Resolution procedures
- Escalation criteria

### Related Skills

**debt-review-foundations**: Core principles, terminology, legal standards
**debt-fact-checking**: Fact-checker agent workflow and standards
**debt-claim-analysis**: Debt analyzer agent workflow and standards
**report-organization**: Report organizer agent workflow and standards

## Part 10: Stage-Level Parallel Processing

### Overview

**New Capability (v2.1)**: The system now supports **stage-level parallel processing** to dramatically improve batch processing efficiency while maintaining the same quality standards.

**Key Distinction**:
- ✅ **Stage-internal parallelism**: Process multiple creditors **within the same stage** → ALLOWED
- ❌ **Cross-stage parallelism**: Process multiple stages of the same creditor simultaneously → PROHIBITED

### When to Use Parallel Processing

**Recommended scenarios**:
- Batch of 2-5 creditors → Parallel processing in single batch
- Batch of 6-15 creditors → Split into 2-3 groups, parallel within each
- Batch of 15+ creditors → Split into multiple groups of 5-8 each

**Performance gains**:
- 5 creditors: 80 minutes (serial) → 18 minutes (parallel) = **78% faster**
- Efficiency primarily from eliminating sequential wait times

### Parallel Processing Requirements

#### Prerequisite 1: Environment Initialization

ALL creditors must be initialized **before** starting parallel processing:

```bash
# Initialize all creditors first (serial)
for creditor in list; do
  python 债权处理工作流控制器.py [batch] [number] [name]
done

# Verify all .processing_config.json files exist
```

#### Prerequisite 2: Self-Contained Prompts

Each parallel Task must have a **completely self-contained prompt** containing:

```
✅ Creditor identity (batch, number, name)
✅ Configuration file path (absolute)
✅ Input material path (absolute)
✅ Output directory paths (absolute)
✅ Previous reports paths (for stages 2&3, absolute)
✅ Bankruptcy dates
✅ All task instructions

❌ NO dependencies on external context
❌ NO relative paths
❌ NO assumptions about "current creditor"
```

**Use provided templates**: `parallel_prompt_templates/stage[1-3]_*.md`

#### Prerequisite 3: Context Isolation

Apply **three-layer verification** to prevent cross-creditor contamination:

```
Layer 1 (Agent startup): Verify config matches prompt identity
Layer 2 (File operations): Verify paths contain correct creditor ID
Layer 3 (Completion): Verify output content matches creditor
```

**Detailed protocol**: See `PARALLEL_PROCESSING_PROTOCOL.md`

### Parallel Execution Workflow

#### Step 0: Batch Initialization (Serial)

```
For each creditor in batch:
  1. Run 债权处理工作流控制器.py
  2. Verify .processing_config.json created
  3. Verify directories created
Time: ~2 minutes for 5 creditors
```

#### Step 1: Parallel Fact-Checking

```
Generate 5 self-contained prompts using stage1 template
↓
In ONE message, launch 5 Task calls:
  Task 1: debt-fact-checker (Creditor 1, complete prompt)
  Task 2: debt-fact-checker (Creditor 2, complete prompt)
  Task 3: debt-fact-checker (Creditor 3, complete prompt)
  Task 4: debt-fact-checker (Creditor 4, complete prompt)
  Task 5: debt-fact-checker (Creditor 5, complete prompt)
↓
Wait for all 5 to complete (~5 minutes)
↓
Execute Quality Checkpoint 1 (see PARALLEL_QUALITY_CHECKLIST.md)
```

#### Step 2: Parallel Debt Analysis

```
Generate 5 prompts using stage2 template (include fact-check report paths)
↓
In ONE message, launch 5 Task calls (debt-claim-analyzer)
↓
Wait for all 5 to complete (~8 minutes)
↓
Execute Quality Checkpoint 2
```

#### Step 3: Parallel Report Organization

```
Generate 5 prompts using stage3 template (include both report paths)
↓
In ONE message, launch 5 Task calls (report-organizer)
↓
Wait for all 5 to complete (~3 minutes)
↓
Execute Quality Checkpoint 3
```

#### Final Verification

```
Run batch-level verification:
  □ All creditors have complete file sets
  □ No cross-creditor contamination
  □ All dates consistent
  □ All outputs in correct locations
```

**Total time**: ~18-20 minutes (vs. 80 minutes serial) for 5 creditors

### 10.3 Parallel Prompt生成与管理

#### What Are Parallel Prompts?

Parallel prompts are **self-contained task instructions** that enable independent agent execution in parallel processing mode. Each prompt includes ALL information needed for one agent to process one creditor without any external context.

**Purpose**:
- ✅ **Context isolation**: Each agent has complete information in its prompt
- ✅ **Pollution prevention**: No dependencies on "current creditor" or shared context
- ✅ **Audit trail**: Complete record of what each agent was instructed to do
- ✅ **Reproducibility**: Can recreate exact processing conditions from prompts

#### Generation Tool: parallel_prompt_generator.py

**Location**: `/root/debt_review_skills/parallel_prompt_generator.py`

**Usage**:
```bash
# Generate prompts for Stage 1 (Fact-Checking)
python parallel_prompt_generator.py --stage 1 --batch 1 --creditors 115,118,124

# Generate prompts for Stage 2 (Debt Analysis)
python parallel_prompt_generator.py --stage 2 --batch 1 --creditors 115,118

# Generate prompts for all stages
python parallel_prompt_generator.py --stage all --batch 1 --creditors 115
```

**What It Does**:
1. Reads `project_config.ini` for bankruptcy dates
2. Loads each creditor's `.processing_config.json`
3. Validates environment initialization status
4. Generates stage-specific prompts using templates
5. Saves prompts to each creditor's `并行处理prompts/` subdirectory

**Output Location** (default):
```
输出/第X批债权/[编号]-[债权人名称]/并行处理prompts/
├── stage1_creditor115_[name]_prompt.txt
├── stage2_creditor115_[name]_prompt.txt
└── stage3_creditor115_[name]_prompt.txt
```

**Custom Output** (optional):
```bash
# Save to custom directory (e.g., for review before execution)
python parallel_prompt_generator.py --stage 1 --batch 1 --creditors 115,118 --output /tmp/review
```

#### Prompt Contents Structure

Each generated prompt contains 7 sections:

1. **债权人身份标识**: Batch, number, name, processing date
2. **配置文件路径**: Absolute path to `.processing_config.json`
3. **输入材料路径/前置报告路径**: Absolute paths to dependencies
4. **输出目录路径**: Absolute paths for outputs
5. **关键参数**: Bankruptcy dates and debtor name
6. **任务指令**: Reference to agent definition and skill
7. **防污染检查清单**: Verification checklists

#### When to Generate Prompts

**Timing**: After environment initialization, before parallel execution

**Workflow**:
```
1. Initialize all creditors (serial)
   → python 债权处理工作流控制器.py [batch] [number] [name]

2. Generate Stage 1 prompts
   → python parallel_prompt_generator.py --stage 1 --batch X --creditors A,B,C

3. Execute Stage 1 in parallel
   → Use Task tool with 3 debt-fact-checker calls in ONE message

4. Checkpoint 1 verification

5. Generate Stage 2 prompts
   → python parallel_prompt_generator.py --stage 2 --batch X --creditors A,B,C

6. Execute Stage 2 in parallel
   → Use Task tool with 3 debt-claim-analyzer calls in ONE message

... (continue for Stage 3)
```

#### Why NOT a Separate Skill?

**Decision**: Parallel prompt generation remains a **tool function**, NOT a separate skill.

**Reasoning**:
- ❌ It's a **technical utility**, not domain knowledge
- ❌ No complex business logic or legal standards involved
- ❌ Creating a skill would be over-engineering
- ✅ Simple script with clear input/output relationship
- ✅ Documentation in workflow orchestration is sufficient

#### File Management Best Practices

**Storage Location**:
- ✅ **Recommended**: Each creditor's `并行处理prompts/` subdirectory (default)
- ⚠️ **Alternative**: Custom directory for review, then copy to creditor folders
- ❌ **Avoid**: Leaving prompts scattered in project root

**Naming Convention**:
```
stage{1|2|3}_creditor{编号}_{债权人名称}_prompt.txt
```

**Retention**:
- Keep prompts as part of audit trail
- Include in file inventory (`文件清单.md`)
- Useful for reproducing processing conditions
- Helpful for debugging if issues arise

#### Integration with File Inventory

The report-organizer agent should list prompts in the file inventory:

```markdown
## 并行处理prompts/

### 1. stage1_creditor115_慈溪市东航建筑起重机械安装队_prompt.txt
- **文件类型**: Stage 1并行处理任务指令
- **文件用途**: 事实核查阶段的完整任务描述（审计追溯）
- **主要内容**: 债权人身份、配置路径、输入材料路径、防污染检查清单

### 2. stage2_creditor115_慈溪市东航建筑起重机械安装队_prompt.txt
- **文件类型**: Stage 2并行处理任务指令
- **文件用途**: 债权分析阶段的完整任务描述（审计追溯）

### 3. stage3_creditor115_慈溪市东航建筑起重机械安装队_prompt.txt
- **文件类型**: Stage 3并行处理任务指令
- **文件用途**: 报告整理阶段的完整任务描述（审计追溯）
```

#### Troubleshooting

**Error: "Config file not found for creditor X"**
- **Cause**: Environment not initialized for this creditor
- **Solution**: Run `python 债权处理工作流控制器.py [batch] [number] [name]`

**Error: "Could not find creditor name for number X"**
- **Cause**: Input material file missing or incorrectly named
- **Solution**: Verify file exists at `输入/第X批债权/{number}.{name}.md`

**Prompts saved to wrong location**
- **Cause**: Using old version before this update
- **Solution**: Re-run generator after updating controller script

---

### Quality Checkpoints for Parallel Mode

Use `PARALLEL_QUALITY_CHECKLIST.md` for comprehensive verification at each checkpoint.

**Critical checks**:
- File existence (all expected files generated)
- Creditor identity verification (no mix-ups)
- Date consistency (across all reports)
- Content independence (no cross-creditor references)

**Acceptance criteria**: ALL checks must pass before proceeding to next stage

**If failures occur**:
```
1. Identify failed creditors
2. Analyze failure cause
3. Reprocess ONLY failed creditors (individually)
4. Successful creditors remain unchanged
5. Retry checkpoint
```

### Error Isolation in Parallel Mode

**Key principle**: One creditor's failure doesn't affect others

**Example**:
```
Parallel batch results:
  Creditor 1: ✅ Success
  Creditor 2: ✅ Success
  Creditor 3: ❌ Failed (config error)
  Creditor 4: ✅ Success
  Creditor 5: ✅ Success

Action:
  - Keep results from 1, 2, 4, 5
  - Fix Creditor 3's issue
  - Reprocess only Creditor 3
  - No need to reprocess 1, 2, 4, 5
```

### Important Limitations

**DO NOT use parallel processing for**:
```
❌ Different stages of the same creditor
❌ When learning the system (stick to serial first)
❌ When materials are incomplete (high failure risk)
❌ When troubleshooting issues
```

**Parallel processing is NOT a silver bullet**:
- Requires careful prompt preparation
- Needs thorough quality checks
- More complex error handling
- Only beneficial for batches of 2+ creditors

### Rollback Plan

If parallel processing causes systemic issues:

```
1. Stop using parallel mode immediately
2. Revert to serial processing (Mode 1 in CLAUDE.md)
3. All business logic unchanged (agents/skills not modified)
4. Quality standards remain the same
5. Simply ignore parallel-related documents
```

### Reference Documents

**Core protocol**: `PARALLEL_PROCESSING_PROTOCOL.md` - Complete technical specification

**Quality checklist**: `PARALLEL_QUALITY_CHECKLIST.md` - Stage-by-stage verification procedures

**Prompt templates**:
- `parallel_prompt_templates/stage1_fact_checking_parallel_template.md`
- `parallel_prompt_templates/stage2_debt_analysis_parallel_template.md`
- `parallel_prompt_templates/stage3_report_organization_parallel_template.md`

**User guide**: `PARALLEL_PROCESSING_USER_GUIDE.md` - Practical operation manual

**SOP**: `PARALLEL_PROCESSING_SOP.md` - Standard operating procedures

---

## Summary

This workflow orchestration skill ensures:

1. **Environment Preparation**: Mandatory initialization for each creditor
2. **Flexible Execution**: Serial (safe) or stage-level parallel (efficient) processing modes
3. **Quality Control**: Mandatory checkpoints at each stage (adapted for parallel mode)
4. **Date Integrity**: Triple verification of bankruptcy dates
5. **Output Standardization**: Consistent directory structure and file naming
6. **Context Isolation**: Zero cross-creditor contamination in parallel mode
7. **Exception Management**: Clear procedures for common issues
8. **Audit Trail**: Complete traceability from input to output

**Golden Rules for Main Controller**:
- **ALWAYS initialize environment first** - No exceptions
- **NEVER skip checkpoints** - Quality over speed
- **FOR PARALLEL**: Use self-contained prompts with absolute paths (see templates)
- **FOR PARALLEL**: Verify context isolation (three-layer verification)
- **NEVER cross-stage parallelize** - Only stage-internal parallelism allowed
- **ALWAYS verify dates** - Date errors invalidate everything
- **NEVER guess or improvise** - Follow standards strictly

**For detailed agent-specific procedures**: See individual agent skills (debt-fact-checking, debt-claim-analysis, report-organization)

**For system foundations**: See debt-review-foundations skill

**For detailed workflow procedures**: See reference guides in `references/` directory
