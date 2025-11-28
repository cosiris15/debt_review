# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this debt review system. This is an agentic system implementing **Skills Architecture** for processing and reviewing debt claim files according to established SOPs and standards.

## System Architecture: Claude Code Skills

This project uses **Claude Code Skills** - a modular knowledge architecture where specialized skills are automatically discovered and invoked when relevant to the task at hand.

### Five Core Skills

1. **debt-fact-checking**: First-stage workflow for extracting and verifying factual information from creditor materials
2. **debt-claim-analysis**: Second-stage workflow for amount analysis, interest calculations, and statute determinations
3. **report-organization**: Third-stage workflow for consolidating reports into standardized client deliverables
4. **debt-review-foundations**: Shared foundational knowledge (legal standards, calculation formulas, terminology)
5. **debt-review-legal-standards**: Advanced legal reference for complex cases (ultra vires guarantees, factoring, construction priority, individual repayment, set-off rights, etc.) - only used for specialized scenarios

**Note**: Workflow orchestration (environment initialization, agent coordination, quality checkpoints, exception handling) is implemented as mandatory control logic in this file, not as an optional skill. This ensures 100% reliable execution without dependency on skill activation.

**Skills Location**: `.claude/skills/` directory

**Automatic Discovery**: Skills are automatically loaded when their descriptions match the current task context

## ⚠️ CRITICAL: Permissions Configuration for Continuous Operation

**This project requires FULL pre-authorization to enable uninterrupted operation.**

### Design Principle: Zero-Interruption Workflow

The three-agent collaborative system is designed for **continuous autonomous operation**:
1. User issues a command
2. Main controller coordinates all sub-agents
3. Complete processing from raw materials to final deliverables
4. **NO permission prompts should interrupt the workflow**

### Current Configuration

**File**: `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

**Meaning**: Full authorization for all Bash commands without individual permission requests.

### What This Enables

**Automatic Operations**:
- Environment initialization (`python 债权处理工作流控制器.py`)
- Interest calculations (`python universal_debt_calculator_cli.py`)
- File operations (mkdir, mv, cp, rm, etc.)
- Text processing (grep, sed, awk, etc.)
- Document generation and organization
- Quality verification and validation

**No Interruptions**: All three agents can perform their tasks autonomously without waiting for user approval at each step.

### Why Full Authorization

**Complex Multi-Step Workflows**: Each creditor processing involves dozens of file operations, script executions, and validations across three agents. Listing individual permissions would:
- Risk missing commands → workflow interruption
- High maintenance cost → update permissions for each feature
- Defeat the purpose of autonomous operation

**Safety**:
- All operations limited to project directory (`/root/debt_review_skills/`)
- Output files strictly organized in `输出/` directory
- No system-level operations required
- Full audit trail via command logging

**For detailed permission documentation**, see: `PERMISSIONS_CONFIGURATION.md`

## ⚠️ CRITICAL: Project Configuration & Date Verification

**ALWAYS read `project_config.ini` FIRST before processing any debt claims!**

This file contains project-specific information like bankruptcy filing dates that MUST be loaded. All date calculations and project-specific processing depend on these configurations.

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

**Remember**: A single date error can invalidate months of work and mislead client decisions!

## Three-Agent Collaborative System

The system uses three specialized agents working in strict sequence:

### Agent 1: debt-fact-checker (事实核查员)
**Purpose**: Extract and verify basic facts from debt claim materials
**Skill**: Primarily references **debt-fact-checking** skill
**Output**: 《事实核查报告》to `工作底稿/` directory
**Key Responsibilities**:
- Declaration information organization
- Basic factual relationship establishment
- Evidence classification and timeline creation
- Batch processing for super-long materials (>100 pages)

### Agent 2: debt-claim-analyzer (债权分析员)
**Purpose**: Perform comprehensive amount analysis and calculations
**Skill**: Primarily references **debt-claim-analysis** skill
**Outputs**:
- 《债权分析报告》to `工作底稿/`
- Calculation process files to `计算文件/`

**Key Responsibilities**:
- Amount decomposition and analysis
- Interest calculations (MANDATORY: use universal_debt_calculator_cli.py)
- Statute of limitations determination
- Quality control and error prevention

### Agent 3: report-organizer (报告整理员)
**Purpose**: Consolidate reports into standardized client deliverables
**Skill**: Primarily references **report-organization** skill
**Outputs**:
- 审查意见表 to `最终报告/`
- 文件清单.md to base directory

**Key Responsibilities**:
- Report consolidation from two technical reports
- Client template application
- File naming and organization standardization
- Final quality verification

## Mandatory Workflow Controller

### ⚠️ Automatic Environment Initialization (TRANSPARENT TO USER)

**🔑 Critical: Initialization happens automatically - user does NOT need to mention it**

**Before processing EACH creditor**, you MUST:

**Step 1: Auto-Detect**
```bash
# Check if already initialized
ls 输出/第X批债权/[编号]-[债权人名称]/.processing_config.json
```

**Step 2: Auto-Initialize (if needed)**
```bash
# Only execute if .processing_config.json NOT found
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
# Example: python 债权处理工作流控制器.py 1 115 慈溪市东航建筑起重机械安装队
```

**What Auto-Initialization Does**:
- Creates standard directory structure (`工作底稿/`, `最终报告/`, `计算文件/`, `并行处理prompts/`)
- Generates `.processing_config.json` with bankruptcy dates and paths
- Sets up file naming templates
- Verifies environment readiness

**Verification After Auto-Init**:
```
□ Standard directories created
□ .processing_config.json exists with bankruptcy dates
□ Configuration accessible to all agents
```

**User Experience**:
- ✅ User says: "Please process creditor 115"
- ✅ System auto-detects and auto-initializes (if needed)
- ✅ System proceeds to three-agent workflow
- ❌ User does NOT need to say: "Please initialize first"

**❌ If auto-initialization fails**: Report error and request manual intervention

### Step 0.5: Processing Mode Auto-Selection (MANDATORY CHECKPOINT)

**Execute IMMEDIATELY after environment initialization, BEFORE starting any agent work**

**Automatic Decision Protocol**:

```python
# Step 1: Identify all creditors to be processed
creditors = list_creditors_in_batch(batch_number)
creditor_count = len(creditors)

# Step 2: Apply automatic decision rule
if creditor_count == 1:
    mode = "Serial Processing"
    notify_user(f"检测到1个债权人，使用串行处理模式")
    execution_plan = "Process creditor 1: Init → Stage 1 → Stage 2 → Stage 3"

elif creditor_count >= 2:
    mode = "Stage-Level Parallel Processing"
    notify_user(f"检测到{creditor_count}个债权人，自动启用并行处理模式（预计节省75-80%处理时间）")
    execution_plan = """
    Initialization: Serial (creditors 1-{N})
    Stage 1: Parallel fact-checking (all {N} creditors simultaneously)
    Stage 2: Parallel debt analysis (all {N} creditors simultaneously)
    Stage 3: Parallel report organization (all {N} creditors simultaneously)
    """

# Step 3: Announce execution plan to user
print(f"执行方案: {execution_plan}")
```

**User Notification Examples**:

Single creditor:
```
检测到1个债权人，使用串行处理模式。
将按顺序完成：环境初始化 → 事实核查 → 债权分析 → 报告整理
```

Multiple creditors:
```
检测到6个债权人，自动启用并行处理模式（预计节省75-80%处理时间）。
执行方案：
- 阶段0（串行）: 依次初始化6个债权人环境
- 阶段1（并行）: 同时进行6个债权人的事实核查
- 阶段2（并行）: 同时进行6个债权人的债权分析
- 阶段3（并行）: 同时进行6个债权人的报告整理
```

**Checkpoint Verification**:
```
□ Creditor count verified
□ Processing mode selected automatically (not manually)
□ User notified of selected mode and rationale
□ Execution plan announced
□ Ready to proceed with selected mode
```

### Processing Flow: Automatic Mode Selection

**⚠️ CRITICAL: Processing mode is automatically determined - you do NOT manually choose**

#### Automatic Decision Logic (MANDATORY)

**Step 1: Count creditors to process**
```python
creditor_count = len(creditors_in_batch)
```

**Step 2: Apply decision rule**
```
IF creditor_count == 1:
    → Use Serial Processing Mode
    → Notify user: "检测到1个债权人，使用串行处理模式"
ELSE IF creditor_count >= 2:
    → Use Stage-Level Parallel Processing Mode
    → Notify user: "检测到{N}个债权人，自动启用并行处理模式（预计节省75-80%处理时间）"
```

**Step 3: Execute selected mode**

#### Mode 1: Serial Processing (Auto-selected for single creditor)

Process ONE creditor through complete three-stage workflow:

```
Creditor 1: Initialize → Fact-Check → Analyze → Organize → Complete ✓
```

**Efficiency**: Standard processing time
**Use case**: Single creditor in batch

#### Mode 2: Stage-Level Parallel Processing (Auto-selected for 2+ creditors)

Process multiple creditors **within the same stage**, but keep stages sequential:

```
✅ AUTOMATIC PARALLEL EXECUTION:
Stage 0 (Serial): Initialize creditors 1, 2, 3, 4, 5
         ↓
Stage 1 (Parallel): Fact-check creditors 1, 2, 3, 4, 5 simultaneously
         ↓ Quality Checkpoint
Stage 2 (Parallel): Analyze creditors 1, 2, 3, 4, 5 simultaneously
         ↓ Quality Checkpoint
Stage 3 (Parallel): Organize creditors 1, 2, 3, 4, 5 simultaneously
         ↓ Final Verification
Complete: All 5 creditors finished

Efficiency: ~75-80% time saving (e.g., 80min → 18min for 5 creditors)
```

**Use case**: Batch of 2+ creditors (production processing)

**Requirements for Parallel Processing**:
```
□ All creditors pre-initialized (environment ready)
□ Use completely self-contained prompts (see parallel templates)
□ Each Task includes absolute paths and full context
□ Apply strict context isolation (no cross-creditor contamination)
□ Execute batch quality checks after each stage
□ Detailed protocol: See PARALLEL_PROCESSING_PROTOCOL.md
```

#### ❌ PROHIBITED - Cross-Stage Parallelism

**NEVER** run different stages of the same creditor simultaneously:

```
❌ WRONG:
Creditor 1: Fact-check + Analyze + Organize (all at once)
Reason: Stages have dependencies - Analyze needs Fact-check output
```

**Summary**:
- ✅ **Automatic mode selection** (based on creditor count) → MANDATORY
- ✅ **Stage-internal parallelism** (multiple creditors, same stage) → AUTO-ENABLED for 2+ creditors
- ❌ **Cross-stage parallelism** (same creditor, multiple stages) → PROHIBITED
- ✅ **User notification** (mode selection announced) → REQUIRED

**For detailed parallel processing procedures**: See `PARALLEL_PROCESSING_PROTOCOL.md`, `PARALLEL_QUALITY_CHECKLIST.md`, and `parallel_prompt_templates/`

## Workflow Execution Details

### Three-Stage Execution Requirements

#### Stage 1: Fact-Checking (debt-fact-checker agent)

**Agent Invocation**:
```
Call: debt-fact-checker agent
Input: Raw materials from 输入/第X批债权/
Output: {债权人名称}_事实核查报告.md to 工作底稿/
```

**Mandatory Pre-Work Verification**:
```
□ Environment initialized (.processing_config.json exists)
□ Bankruptcy dates read from configuration
□ Raw material files accessible
□ Output directory 工作底稿/ writable
```

**Mandatory Post-Work Verification** (Checkpoint 1):
```
□ Report file exists in correct location
□ Bankruptcy dates documented in report
□ Declaration information complete
□ Evidence timeline created
□ Legal relationship identified
□ No placeholders or "TBD" items remaining
```

#### Stage 2: Debt Analysis (debt-claim-analyzer agent)

**Agent Invocation**:
```
Call: debt-claim-analyzer agent
Input: Fact-checker report from 工作底稿/
Outputs:
  - {债权人名称}_债权分析报告.md to 工作底稿/
  - Calculation files to 计算文件/
```

**Mandatory Pre-Work Verification**:
```
□ Fact-checker report exists and complete
□ Bankruptcy dates cross-verified with fact report
□ Calculator tool tested and working
□ Output directories writable
```

**Mandatory Post-Work Verification** (Checkpoint 2):
```
□ Analysis report exists in 工作底稿/
□ Calculation files exist in 计算文件/ (or explanation TXT if none)
□ Calculator tool used for ALL calculations (zero manual calculations)
□ Dates consistent with fact-checker report
□ 就低原则 applied (confirmation ≤ declaration)
□ 就无原则 applied (only declared items included)
□ LPR term selection justified for long-term debts
□ Penalty caps applied if needed
```

#### Stage 3: Report Organization (report-organizer agent)

**Agent Invocation**:
```
Call: report-organizer agent
Input: Both technical reports from 工作底稿/
Outputs:
  - GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md to 最终报告/
  - 文件清单.md to base directory
```

**Mandatory Pre-Work Verification**:
```
□ Both technical reports exist and complete
□ Dates verified across all three sources (config + 2 reports)
□ Output directory 最终报告/ writable
```

**Mandatory Post-Work Verification** (Checkpoint 3):
```
□ Final report exists in 最终报告/
□ File inventory exists in base directory
□ Dates consistent across all three reports
□ Content accurately extracted from technical reports
□ No technical conclusions modified
□ Template format applied correctly
□ File naming follows standard
```

### Critical Quality Checkpoints

**Checkpoint 0: After Pre-Processing (MUST PASS before Stage 1)**

Execution Timing: After Step 0 completion, before Step 1 starts

Pre-Processing File Verification:
```
□ Claim structure overview file exists in 工作底稿/
□ File size > 500 bytes (not empty stub)
□ Version matches preprocessing_config (simplified/comprehensive)
□ If diagram_required=true: Legal relationship diagram exists
□ If comprehensive version: Contains guarantee matrix section
```

Configuration Update Verification:
```
□ preprocessing_config field added to .processing_config.json
□ version field correctly set (simplified/comprehensive)
□ trigger_conditions accurately reflect material assessment
□ diagram_required matches actual diagram generation
□ diagram_types lists all generated diagram types
```

Failure Protocol:
```
IF checkpoint fails:
  → STOP Stage 1 (do not proceed with fact-checking)
  → Report specific missing items
  → Agent must complete pre-processing before continuing
```

**Batch Validation Command**:
```bash
python 债权处理工作流控制器.py --validate-batch X --stage 0
```

**Note**: For backward compatibility, creditors without `preprocessing_config` field will be skipped (not failed) in validation.

**Checkpoint 1: After Fact-Checker (MUST PASS before proceeding)**

Date Verification:
```
✓ Bankruptcy date verified from .processing_config.json
✓ Interest stop date = bankruptcy date - 1
✓ Dates explicitly documented in report
```

Content Quality:
```
✓ Declaration amounts complete and breakdown sums correctly
✓ Timeline events in chronological order
✓ Evidence citations present for all key facts
✓ Legal relationship type identified (not vague)
```

**Checkpoint 2: After Analyzer (MUST PASS before proceeding)**

Date Verification:
```
✓ Dates re-verified from .processing_config.json
✓ Cross-verified with fact-checker report (dates match)
✓ All calculations use correct interest_stop_date
```

Calculation Quality:
```
✓ Calculator tool commands documented for all calculations
✓ Calculation process files generated
✓ LPR term selection reviewed and justified
✓ Penalty caps verified and applied if needed
✓ 就低原则 applied where calculation > declaration
```

**⚠️ Execution Period Verification** (MANDATORY for judgment-based claims):
```
✓ Identified all claims based on effective legal documents
✓ For each such claim, calculated execution period (2 years from performance deadline)
✓ Reviewed creditor's execution evidence (application, acceptance notice, records)
✓ If execution period exceeded WITHOUT evidence:
  → Marked as 【不予确认】(NOT 【暂缓确认】)
  → Used correct reasoning citing Supreme Court Interpretation + Court Guidelines
  → Did NOT use prohibited phrases like "执行时效届满不消灭实体债权"
✓ Clearly distinguished execution-barred claims from statute-barred claims
```

**Critical Reminder**:
- **Execution Period Expired** → 【不予确认】(Do NOT confirm)
- **Statute of Limitations Expired** → 【暂缓确认】(Deferred confirmation)
- Different legal treatment, different confirmation marks
- For detailed guidance: See `.claude/skills/debt-claim-analysis/references/statute_limitations_guide.md` Section "⚠️ CRITICAL WARNING"

**NEW: Automated File Validation (v2.0)** ⭐

After Stage 2 completes, use the workflow controller v2.0 to automatically verify file integrity:

```bash
# For single creditor validation
python 债权处理工作流控制器.py <batch> <number> <name> --validate

# For batch validation (recommended after parallel processing)
python 债权处理工作流控制器.py --validate-batch <X> --stage 2
```

**What gets validated automatically**:
```
✓ 计算文件/ directory not empty
✓ Excel files exist OR explanation TXT exists (not both, not neither)
✓ Excel file sizes reasonable (>2KB, not corrupted)
✓ NO "计算过程说明.md" files (异常模式 - 应该是Excel而非MD)
✓ Calculation files match creditor name conventions
```

**Auto-fix capability** (if validation fails):
```bash
# Automatically generate explanation TXT for "no calculation" cases
python 债权处理工作流控制器.py --fix-batch <X> --stage 2

# Success rate: 80-95% (remaining cases need manual review)
```

**Checkpoint 3: After Organizer (MUST PASS before completion)**

Date Verification:
```
✓ Dates consistent across config + fact report + analysis report
✓ Final report contains correct dates
```

**Format Compliance Verification (CRITICAL - Zero Tolerance)**:

**MANDATORY: Execute automated format checks on final report before declaring completion**

```bash
# Get final report path
FINAL_REPORT="输出/第X批债权/[编号]-[债权人名称]/最终报告/GY2025_*.md"

# Check 1: No Markdown heading syntax
echo "Checking for prohibited Markdown headings..."
grep -n "^##" "$FINAL_REPORT"
# Expected: Empty output (no matches)
# If matches found: FAIL - Report contains Markdown headings

# Check 2: No bullet list markers
echo "Checking for prohibited bullet lists..."
grep -n "^- " "$FINAL_REPORT"
# Expected: Empty output (no matches)
# If matches found: FAIL - Report contains bullet lists

# Check 3: No bold/italic syntax
echo "Checking for prohibited bold syntax..."
grep -n "\*\*" "$FINAL_REPORT"
# Expected: Empty output (no matches)
# If matches found: FAIL - Report contains bold syntax

# All checks must return empty - otherwise STOP and regenerate report
```

**Visual Verification** (spot check):
```bash
# Display first 50 lines of final report
head -50 "$FINAL_REPORT"

# Verify format:
□ Chapter titles appear as "一、" "二、" (NOT "## 一、")
□ Content in complete sentences (NOT bullet points)
□ No ** bold markers visible
□ Reads like formal legal document
```

**Failure Protocol**:
```
IF any format check fails:
  → STOP immediately
  → Report specific violations to user
  → Regenerate report with explicit format conversion
  → Re-run ALL format checks
  → DO NOT proceed until all checks pass
```

Report Quality:
```
✓ Content extracted accurately (no information loss)
✓ Technical conclusions preserved (no modifications)
✓ Template format correctly applied
✓ All files in correct directories
✓ File naming complies with standards
✓ Format compliance verified (grep checks passed)
```

### Common Exception Handling

**Exception 1: Environment Not Initialized**
- **Symptom**: `.processing_config.json` missing
- **Action**: STOP → Run `python 债权处理工作流控制器.py [batch] [number] [name]` → Verify → Resume from beginning

**Exception 2: Date Inconsistencies**
- **Symptom**: Different dates in config vs. reports
- **Action**: STOP → Identify authoritative source (court documents → project_config.ini) → Correct source → Re-run affected agents → NEVER deliver with date errors

**Exception 3: Incomplete Materials**
- **Symptom**: Key evidence missing
- **Action**: Document missing items specifically → Process available materials only → Mark report with "材料不完整" note → Do NOT fabricate or guess

**Exception 4: Calculator Tool Error**
- **Symptom**: Tool fails or returns errors
- **Action**: Verify command syntax → Check parameters (dates, amounts, rates) → Retry with corrections → If persistent: STOP and escalate (DO NOT use manual calculations)

**Exception 5: Missing Agent Output**
- **Symptom**: Expected report file not found
- **Action**: Search for file → Check naming → Move to correct location if misplaced → If truly missing: Re-run agent → DO NOT proceed without prerequisite outputs

**Exception 6: Super-Long Materials (>100 pages or >50 items)**
- **Symptom**: Material volume exceeds capacity
- **Action**: Activate batch processing (fact-checker) → Process in batches: (1) Core contracts, (2) Performance records, (3) Legal documents → Consolidate into single unified report

**Escalation Criteria** (STOP and report to supervisor):
- Bankruptcy date cannot be determined or fundamentally contradictory
- Evidence appears forged or fraudulent
- Calculator tool fundamentally broken
- Novel legal scenario not covered in standards
- Workflow standards contradict on critical point

### Financial Claim Processing (Banks, Trusts, AMCs)

**Special handling for financial institution claims with two key characteristics:**
1. Long files (500+ pages per document)
2. Multiple loans per creditor (e.g., bank with 3 separate loan contracts)

#### Pre-Processing Layer: Claim Structure Overview (Step 0)

**⚠️ MANDATORY for ALL debt claims - Execute BEFORE the standard 6-step workflow**

Before detailed fact-checking, generate a structured claim overview:

**Version Selection**:
```
Use COMPREHENSIVE version if ANY apply:
├─ Financial institution creditor (bank, trust, AMC, leasing, factoring)
├─ Multi-loan claims (≥2 separate loans from same creditor)
├─ Complex guarantee structure (≥3 guarantors OR mixed guarantee types)
├─ Debt transfer involved
└─ Total claim amount ≥10 million yuan

Use SIMPLIFIED version for:
└─ Simple claims (single contract, ≤2 guarantors, no transfers)
```

**Output Files**:
- `{债权人名称}_债权结构概览.md` → `工作底稿/`
- For comprehensive version: Includes per-loan matrix, guarantee coverage table, debt transfer chain

**Reference**: `debt-fact-checking/templates/claim_structure_overview_template.md`

#### Legal Relationship Diagrams (Mermaid)

**When to Generate**: For comprehensive version claims (multi-loan or complex structures)

**Three Diagram Types**:
```
1. Subject Relationship Diagram (主体关系图)
   - Shows relationships between all parties
   - Use when ≥4 parties involved

2. Contract Relationship Diagram (合同关系图)
   - Shows contract network between parties
   - Use for multi-contract scenarios

3. Debt Transfer Chain Diagram (转让链图)
   - Shows transfer sequence from original creditor
   - Use when debt transfers occurred
```

**Output File**: `{债权人名称}_法律关系图.md` → `工作底稿/`

**Standard Color Scheme**:
```
Creditor: #9f9 (green)
Debtor: #f99 (red)
Guarantor: #ff9 (yellow)
Collateral: #9cf (blue)
```

**Reference**: `debt-fact-checking/references/mermaid_diagram_generation.md`

#### Multi-Loan Analysis Workflow

**Core Principle**: Analyze each loan independently, consolidate for reporting

**Per-Loan Analysis**:
```
For each loan:
├─ Independent principal analysis
├─ Independent interest calculation (use calculator tool)
├─ Independent guarantee analysis
├─ Independent statute of limitations check
└─ Apply 就低原则 PER LOAN (not on total)
```

**Calculator Tool Usage** (one call per loan):
```bash
# Loan 1
python universal_debt_calculator_cli.py lpr --principal 5000000 --start-date 2023-01-01 --end-date 2024-05-19 --multiplier 1.0 --lpr-term 1y

# Loan 2
python universal_debt_calculator_cli.py lpr --principal 3000000 --start-date 2023-06-01 --end-date 2024-05-19 --multiplier 1.3 --lpr-term 1y
```

**Consolidated Output Tables**:
```
| Loan# | Contract | Principal | Interest | Type | Status |
|-------|----------|-----------|----------|------|--------|
| 1 | XXXX-001 | X元 | X元 | Secured | Confirmed |
| 2 | XXXX-002 | X元 | X元 | Secured | Confirmed |
| 3 | XXXX-003 | X元 | X元 | Unsecured | Partial |
| Total | | X元 | X元 | | |
```

**Common Guarantee Analysis** (when same guarantor covers multiple loans):
```
| Guarantor | Type | Loan 1 | Loan 2 | Loan 3 | Limit |
|-----------|------|--------|--------|--------|-------|
| Zhang San | Joint | ✓ | ✓ | ✓ | Unlimited |
| Property A | Mortgage | ✓ | | | Appraised value |
```

**References**:
- `debt-claim-analysis/references/financial_multi_loan_guide.md`
- `debt-claim-analysis/templates/multi_loan_analysis_template.md`

#### Financial Claim Output Files

**Standard outputs plus financial-specific files**:

```
工作底稿/
├── {债权人名称}_债权结构概览.md      # Pre-processing output
├── {债权人名称}_法律关系图.md        # Mermaid diagrams (if applicable)
├── {债权人名称}_事实核查报告.md      # Standard fact-check report
└── {债权人名称}_债权分析报告.md      # Multi-loan format for financial claims

计算文件/
├── {债权人名称}_笔1_利息计算.xlsx    # Per-loan calculation files
├── {债权人名称}_笔2_利息计算.xlsx
└── {债权人名称}_笔3_利息计算.xlsx
```

**Quality Checklist for Financial Claims**:
```
□ Pre-processing: Claim structure overview generated
□ Per-loan: Each loan analyzed independently
□ Calculator: One calculation file per loan (or consolidated with multiple sheets)
□ Guarantee: Common guarantee coverage matrix created
□ Summary: All loans consolidated in unified table
□ 就低原则: Applied per loan, NOT on total
```

### File Management Standards

**Path Management Rules (MANDATORY)**:
```
✓ Always use absolute paths from .processing_config.json
✓ Never use relative paths or hardcoded paths
✓ Verify directory exists before writing files
✓ Verify file saved successfully after write
✓ Use exact filenames from configuration templates
```

**File Naming Standards**:
```
Fact-checking report:  {债权人名称}_事实核查报告.md
Debt analysis report:  {债权人名称}_债权分析报告.md
Final review opinion:  GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md
Calculation files:     {债权人名称}_{计算类型}.xlsx
File inventory:        文件清单.md
```

**Directory Organization (STRICT)**:
```
工作底稿/     → Technical reports (fact-checker, analyzer)
最终报告/     → Client deliverables (final review opinion)
计算文件/     → Calculation process files (Excel/CSV or explanation TXT)
并行处理prompts/ → Parallel processing task prompts (audit trail)
```

**Zero-Tolerance File Errors**:
- ❌ Files in wrong directories
- ❌ Wrong file naming
- ❌ Missing calculation process files (for calculation items)
- ❌ Files scattered outside standard structure

## Universal Debt Calculator Tool

**Tool Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**MANDATORY Usage**: ALL interest calculations MUST use this tool - ZERO manual calculations accepted

**Five Calculation Modes**:
```bash
# Simple interest
python universal_debt_calculator_cli.py simple --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --rate 4.35

# LPR floating rate
python universal_debt_calculator_cli.py lpr --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --multiplier 1.5 --lpr-term 1y

# Delayed performance interest
python universal_debt_calculator_cli.py delay --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31

# Compound interest
python universal_debt_calculator_cli.py compound --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --rate 4.35 --cycle "每月末"

# Penalty interest
python universal_debt_calculator_cli.py penalty --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --rate 6.0
```

**Capabilities**:
- Embedded LPR rate data (2019-2025)
- Automatic Excel/CSV process table generation
- No external dependencies required
- Complete audit trail documentation

## Quality Validation and Auto-Fix (Workflow Controller v2.0)

**Version**: Controller upgraded from v1.0 to v2.0 (2025-10-29)

The workflow controller now includes built-in validation and auto-fix capabilities to prevent calculation file generation issues.

### Validation Capabilities (Layer 2)

Controller automatically detects:
- ✓ Empty calculation file directories
- ✓ Missing Excel/CSV files or explanation TXT files
- ✓ Abnormally small Excel files (<2KB, possibly corrupted)
- ✓ Abnormal patterns (MD explanation files instead of Excel)
- ✓ Missing required reports at each stage

### Auto-Fix Capabilities (Layer 3)

Controller can automatically fix:
- ✓ Generate explanation TXT for "no calculation" cases
- ✓ Based on keywords in analysis report (未申报利息, 就低原则, etc.)
- ✓ Success rate: 80-95% (remaining cases need manual review)
- ✓ Standardized explanation file format with audit trail

### Batch Operations (Layer 4)

Process entire batch at once:

```bash
# Validate all creditors in batch X, stage 2
python 债权处理工作流控制器.py --validate-batch X --stage 2

# Auto-fix all creditors in batch X, stage 2
python 债权处理工作流控制器.py --fix-batch X --stage 2
```

**Benefits**:
- Catches calculation file issues before Stage 3
- Reduces manual intervention by 75-80%
- Ensures 100% compliance with Excel generation standards
- Provides batch-level quality metrics

### When to Use Validation

**Recommended workflow integration**:

```
Step 0: Initialize environment (auto)
Step 1: Fact-checking (Agent 1)
Step 2: Debt analysis (Agent 2)
Step 2.5: Validation checkpoint → python 债权处理工作流控制器.py --validate-batch X --stage 2
         ↓ If issues: python 债权处理工作流控制器.py --fix-batch X --stage 2
Step 3: Report organization (Agent 3)
Step 3.5: Final validation → python 债权处理工作流控制器.py --validate-batch X --stage 3
```

### Usage Examples

**Single Creditor**:
```bash
# Initialize + validate
python 债权处理工作流控制器.py 1 115 债权人名称 --validate

# Initialize + auto-fix
python 债权处理工作流控制器.py 1 115 债权人名称 --fix
```

**Batch Operations**:
```bash
# Validate entire batch
python 债权处理工作流控制器.py --validate-batch 4 --stage 2

# Expected output:
# 📊 验证结果摘要:
#   总计: 6个债权人
#   通过: 5个 (⚠️)
#   失败: 1个 (❌)
```

**For detailed controller documentation**: See `债权处理工作流控制器.py --help`

## Core Principles

### 就低原则 (Lower Bound Rule)
When calculation > creditor's declaration, use declared amount as final confirmation
**Rationale**: Respect creditor's self-limitation

### 就无原则 (Non-Existence Rule)
Items identified in evidence but NOT declared by creditor are NOT included
**Rationale**: Debt review is verification, not claim generation

### Evidence Hierarchy
1. **Highest**: Legal documents (judgments, mediations, arbitrations)
2. Bilateral confirmations (settlement statements, reconciliations)
3. Contracts and amendments
4. **Lowest**: Unilateral evidence (invoices, delivery slips)

### Substance Over Form (实质重于形式)
Focus on actual legal relationships and economic substance, not just document labels

## Directory Structure

```
/root/debt_review_skills/
├── .claude/
│   ├── agents/                      # Three agent definitions (orchestration files)
│   │   ├── debt-fact-checker.md
│   │   ├── debt-claim-analyzer.md
│   │   └── report-organizer.md
│   └── skills/                      # Five Skills (detailed knowledge)
│       ├── debt-fact-checking/
│       │   ├── SKILL.md
│       │   ├── templates/
│       │   └── references/
│       ├── debt-claim-analysis/
│       │   ├── SKILL.md
│       │   ├── templates/
│       │   └── references/
│       ├── report-organization/
│       │   ├── SKILL.md
│       │   ├── templates/
│       │   └── references/
│       ├── debt-review-foundations/
│       │   ├── SKILL.md
│       │   └── references/
│       └── debt-review-legal-standards/
│           ├── SKILL.md
│           └── references/
│
├── project_config.ini               # Project configuration (LOAD FIRST!)
├── 债权处理工作流控制器.py            # Workflow controller script
├── universal_debt_calculator_cli.py # Interest calculator tool
└── 归档文件/                         # Archived files from migration
    └── v1_改造前完整备份_20251023/   # Pre-migration backup

输出/第X批债权/[编号]-[债权人名称]/    # Processing outputs (per creditor)
├── .processing_config.json          # Creditor-specific configuration
├── 工作底稿/                         # Working papers (technical reports)
│   ├── {债权人}_事实核查报告.md
│   └── {债权人}_债权分析报告.md
├── 最终报告/                         # Final reports (client deliverables)
│   └── GY2025_{债权人}_债权审查报告_{YYYYMMDD}.md
├── 计算文件/                         # Calculation process files
│   └── {债权人}_{类型}.xlsx
└── 并行处理prompts/                  # Parallel processing task prompts (audit trail)
    ├── stage1_creditor{编号}_{债权人名称}_prompt.txt
    ├── stage2_creditor{编号}_{债权人名称}_prompt.txt
    └── stage3_creditor{编号}_{债权人名称}_prompt.txt
```

## Standard Workflow

### Step 0: Automatic Environment Initialization (TRANSPARENT)
**System automatically detects and initializes - user does NOT need to request this**
```bash
# Auto-executed by system if .processing_config.json not found
python 债权处理工作流控制器.py [batch] [number] [name]
```

### Step 1: Fact-Checking (Agent 1)
- **Call**: debt-fact-checker agent
- **Input**: Raw debt claim materials from `输入/第X批债权/`
- **Output**: 事实核查报告.md to `工作底稿/`
- **Checkpoint**: Verify report exists, dates verified, facts complete

### Step 2: Debt Analysis (Agent 2)
- **Call**: debt-claim-analyzer agent
- **Input**: Fact-checker report from `工作底稿/`
- **Outputs**: Analysis report to `工作底稿/`, calculation files to `计算文件/`
- **Checkpoint**: Verify reports exist, calculator used, dates consistent

### Step 3: Report Organization (Agent 3)
- **Call**: report-organizer agent
- **Input**: Both technical reports from `工作底稿/`
- **Outputs**: Review opinion to `最终报告/`, file inventory to base directory
- **Checkpoint**: Verify template applied, dates consistent, files organized

### Step 4: Quality Verification (Main Controller)
- Verify all files in correct locations
- Verify file naming standards followed
- Verify no files scattered in wrong directories
- Mark creditor processing as complete

## Quality Standards

### Zero-Tolerance Items
**These errors are NEVER acceptable**:
- ❌ Wrong bankruptcy dates in any report
- ❌ Manual calculations (not using calculator tool)
- ❌ Files in wrong directories
- ❌ Missing calculation process files
- ❌ Date inconsistencies between reports
- ❌ Starting next stage without completing previous stage

### Date Verification Protocol (ALL Agents)
```
□ Read dates from .processing_config.json
□ Verify interest_stop_date = bankruptcy_date - 1
□ Cross-verify with previous reports (if applicable)
□ Record dates explicitly in output
□ STOP if any inconsistency found
```

**Note**: For detailed workflow execution requirements, quality checkpoints, exception handling, and file management standards, see "Workflow Execution Details" section above.

## Skills Architecture Benefits

**Modularity**: Each skill focused on specific domain knowledge
**Reusability**: Shared foundations skill avoids duplication
**Maintainability**: Update knowledge in one place
**Discovery**: Skills auto-load when context matches
**Scalability**: Easy to add new skills for new scenarios

## Migration Notes

This project was migrated from traditional agent mode to Skills architecture on 2025-10-23.

**Backup**: Complete pre-migration backup in `归档文件/v1_改造前完整备份_20251023/`

**Key Changes**:
- Agent definitions simplified from 180-205 lines to 174-255 lines
- Detailed workflows moved to Skills (5 SKILL.md files + 11 reference guides)
- No functional changes - all business logic preserved
- Same three-agent workflow, same quality standards

**For migration details**: See `MIGRATION_TO_SKILLS_V2.md`

## Key Reference Documents

**For Main Controller (this file)**:
- Workflow orchestration: See "Workflow Execution Details" section in this file
- Core principles and standards: **debt-review-foundations** skill

**For Agents**:
- Each agent references its primary skill for detailed workflows
- All agents reference debt-review-foundations for shared knowledge

**For Legal Standards**: `debt-review-foundations/references/legal_standards_reference.md`
**For Calculations**: `debt-review-foundations/references/calculation_formulas_reference.md`
**For Terminology**: `debt-review-foundations/references/common_terms_glossary.md`

## Important Reminders

1. **ALWAYS initialize environment first** - Run 债权处理工作流控制器.py for each creditor
2. **NEVER skip date verification** - Verify bankruptcy dates at every stage
3. **ALWAYS use calculator tool** - Zero manual calculations accepted
4. **ALWAYS use automatic mode selection** - System automatically chooses serial/parallel based on creditor count
5. **ALWAYS apply core principles** - 就低原则, 就无原则 in every analysis
6. **NEVER modify technical conclusions** - Report organizer preserves analysis accuracy

## Getting Started

**For new project**:
1. Update `project_config.ini` with bankruptcy dates and project info
2. Prepare raw materials in `输入/第X批债权/` directory
3. For each creditor: Initialize → fact-check → analyze → organize
4. Verify outputs in standard directory structure

**For questions about workflow**: See "Workflow Execution Details" section in this file
**For questions about analysis**: Reference **debt-claim-analysis** skill
**For questions about principles**: Reference **debt-review-foundations** skill

---

**System Version**: Skills Architecture v2.0
**Migration Date**: 2025-10-23
**Architecture**: Three-agent collaborative system with five modular skills
**Quality Standard**: Professional debt review with complete audit trail
