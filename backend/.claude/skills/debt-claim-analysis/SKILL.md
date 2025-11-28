---
name: debt-claim-analysis
description: Analyze bankruptcy debt claims by breaking down amounts, calculating interest using LPR rates and legal standards, and determining statute of limitations. Produces detailed debt analysis reports with calculation process tables for precise verification.
---

# Debt Claim Analysis Skill

## Overview

Comprehensive debt claim amount analysis, interest calculation, and statute of limitations determination for bankruptcy proceedings. This skill provides systematic methodologies for analyzing claim amounts, calculating various types of interest using the universal debt calculator tool, and producing calculation audit trails.

## 📋 CRITICAL: Template Files Reference

**⚠️ MANDATORY READING - NON-NEGOTIABLE**

Before executing any debt analysis task, you **MUST** read the complete format template:

**Template Location**: `templates/debt_analysis_report_template.md`

**Why This Is Critical**:
- Defines the EXACT format structure that clients and legal teams expect
- Contains standardized amount breakdown and calculation documentation formats
- Specifies mandatory calculation command documentation requirements
- Provides complete section structure and table formats
- Ensures consistency and auditability across all debt analysis reports

**Template Contains**:
- Complete report structure (all required sections in exact order)
- Amount breakdown table formats (principal/interest/cost classification)
- Interest calculation documentation standards (full calculator commands)
- Statute analysis table structures
- Calculation file generation requirements
- Review conclusion format standards

**This is NOT optional**. The template represents established client requirements and legal professional standards. Deviating from the template format creates inconsistencies and may require report regeneration.

## When to Use This Skill

- Analyzing claim amounts and breaking down components
- Calculating interest (simple, LPR floating, delayed performance, compound)
- Determining statute of limitations for debt claims
- Producing final debt analysis reports with calculation files
- Quality control and cross-validation of debt amounts

## Prerequisites

- **Completed fact-checking report** from debt-fact-checker
- **Access to calculator tool**: `/root/debt_review_skills/universal_debt_calculator_cli.py` (MANDATORY for all calculations)
- **Bankruptcy dates verified** from `.processing_config.json`

## ⚠️ MANDATORY Pre-Work Check: Date Verification

**BEFORE starting any debt analysis work, you MUST:**

1. **Read Configuration**: Extract bankruptcy filing date from `.processing_config.json` in creditor directory
2. **Cross-Verify**: Compare with dates in fact-checking report to ensure consistency
3. **Record Confirmation**: Document the dates used at the beginning of your report
4. **Handle Inconsistencies**: If dates don't match or config is abnormal, STOP work immediately and report

**Example Output Format**:
```
✅ 破产受理日期核对完成
- 破产受理日期：2023-05-12
- 停止计息日期：2023-05-11
- 与事实核查报告一致：是
- 配置文件状态：正常
```

**Critical Importance**: Bankruptcy filing date directly determines the cutoff point for ALL interest calculations. Wrong dates will invalidate the entire analysis.

## Multi-Loan Claims (Financial Institutions)

**When to Apply**: Same creditor with ≥2 separate loans (common for banks, trusts, AMCs)

### Key Principles

1. **Per-Loan Analysis**: Each loan must be analyzed independently
2. **Per-Loan Calculations**: Interest calculated separately for each loan using calculator tool
3. **Per-Loan Lower Bound**: 就低原则 (lower bound rule) applied per loan, not on total
4. **Consolidated Summary**: All loans summarized in a single unified table

### Workflow for Multi-Loan Claims

```
Step 1: Read Claim Structure Overview
    → Identify number of loans and basic info per loan
    ↓
Step 2: Read Legal Relationship Diagram
    → Understand guarantee coverage across loans
    ↓
Step 3: Per-Loan Analysis (for each loan)
    ├─ Principal analysis
    ├─ Interest calculation (MUST use calculator)
    └─ Guarantee analysis for that loan
    ↓
Step 4: Consolidated Summary
    → Aggregate table with all loans
    ↓
Step 5: Cross-Guarantee Analysis
    → Analyze shared guarantees across loans
```

### Output Requirements

- **Report Template**: Use `templates/multi_loan_analysis_template.md`
- **Calculation Files**: One Excel file per loan OR one Excel with multiple sheets
- **Summary Table**: Must include per-loan AND aggregate totals

### Detailed Guidance

- **Analysis Guide**: See `references/financial_multi_loan_guide.md`
- **Report Template**: See `templates/multi_loan_analysis_template.md`

---

## Core Workflow (5-Step Process)

### Step 1: Receive Fact-Checking Report

**Objective**: Understand established facts and amounts

**Actions**:
1. Read《事实核查报告》in full
2. Verify bankruptcy dates match configuration file
3. Identify declared amounts vs. proven amounts from evidence
4. Note legal relationship types and number of independent relationships
5. Review evidence hierarchy analysis

**Key Validation**:
- Ensure fact-checker verified dates correctly
- Confirm all major evidence types are covered
- Identify settlement documents or confirmations (highest hierarchy)

### Step 2: Amount Breakdown Analysis

**Objective**: Systematically decompose claim amounts into independent items

**Core Principle**: "Itemized Breakdown" + "Substance Over Form"
- Break down umbrella terms like "principal" and "interest" into smallest units
- Each amount item must have specific legal basis and calculation logic

**Standard Breakdown Structure**:

```
债权总额
├── 本金类项目 (Principal Items)
│   ├── XX合同项下的第N期货款
│   ├── XX项目的进度款
│   └── 质保金
│
├── 孳息/违约类项目 (Ancillary Items)
│   ├── 借贷类合同利息
│   ├── 普通合同逾期利息（含违约金）
│   └── 迟延履行期间债务利息
│
└── 费用类项目 (Cost/Expense Items)
    ├── 律师费
    ├── 案件受理费
    └── 保全费
```

**⚠️ Critical Rules**:

1. **Principal Items**: Breakdown by specific contract, phase, or legal document
   - Sales/Supply: "XX合同项下的第N期货款", "订单号XXX对应的货款"
   - Service/Construction: "XX项目的进度款", "质保金"
   - Loan: "XX借款合同项下的本金"
   - Legal Documents: "（案号）判决书确认的应返还款项"

2. **Interest/Penalty Items**: Each unique calculation logic = one item
   - Loan interest: Contractual obligation to pay interest
   - Overdue interest: Interest for late payment on ordinary contracts
   - Delayed performance interest: Double interest for judgment debts
   - **⚠️ Important**: Penalties (违约金) should be classified as "interest", NOT "other"

3. **Cost Items**: Recoverable expenses for claim realization
   - Attorney fees, court fees, preservation fees (if awarded by judgment)

**Detailed breakdown methods**: See `references/amount_and_interest_guide.md` § Amount Breakdown

### Step 3: Interest Calculation

**Objective**: Calculate precise interest amounts using calculator tool

**🚨 MANDATORY RULE**: MUST use `universal_debt_calculator_cli.py`, NEVER manual calculations

**Calculator Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**Five Interest Calculation Types**:

#### Type 1: Loan Contract Interest (固定利率)
**Usage**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 4.35
```

#### Type 2: LPR Floating Rate Interest
**Usage**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --multiplier 1.5 \
  --lpr-term 1y  # or 5y
```

**⚠️ LPR Term Selection Rules** (CRITICAL):

**Mandatory Period Assessment**:
1. Calculate total debt period: From interest start date to bankruptcy filing date - 1 day
2. Record period clearly: Start date, end date, total days/years
3. Period classification:
   - Total period ≤ 5 years: Prioritize 1-year LPR
   - Total period > 5 years: **MUST seriously consider 5-year+ LPR**

**1-Year LPR Scenarios**:
- Short-term debts: Performance period ≤ 5 years
- Short-term loans: Loan term ≤ 5 years
- General overdue interest: Default to 1-year LPR if no term specified
- Ordinary commercial debts: Sales, service contracts

**5-Year+ LPR Scenarios**:
- Long-term loans: Loan term > 5 years (e.g., mortgage, major project financing)
- Long-term debts: Performance period > 5 years
- Contract explicit provision: Contract specifies 5-year LPR
- Construction long-term arrears: If unpaid period > 5 years
- Judicial determination: Court explicitly applies 5-year LPR
- **⚠️ Important**: When creditor declares fixed rate BUT debt period > 5 years, MUST review whether 5-year+ LPR floating rate should apply

#### Type 3: Delayed Performance Interest (迟延履行期间债务利息)
**Usage**:
```bash
python universal_debt_calculator_cli.py delay \
  --principal 100000 \
  --start-date 2024-06-01 \
  --end-date 2024-12-31
```

**⚠️ Prerequisites for Delayed Performance Interest**:

1. **MUST be judgment debt**: Only applies to amounts confirmed by effective legal documents
2. **MUST verify performance period expired**:
   - Determine performance deadline from judgment/mediation
   - Relative deadline: Effective date + performance period
     * First-instance no appeal: Effective 15 days after delivery
     * Second-instance (including affirmation): **Effective on second-instance judgment date, NOT first-instance**
   - Specific deadline: Use date specified in legal document
   - No deadline specified: Use effective date as deadline
3. **MUST be declared by creditor**: Follow "就无原则" - don't calculate if not declared

**Interest start date**: Day after performance deadline expires

**Fixed rate**: Daily rate of 0.0175% (万分之1.75)

#### Type 4: Compound Interest
**Usage**:
```bash
python universal_debt_calculator_cli.py compound \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 4.35 \
  --cycle "每月末"
```

#### Type 5: Payment Offset Handling

When debtor made payments during the debt period:

**Strategy**: Segmented calculation + offset processing

1. **Split periods** by payment dates
2. **Calculate separately**:
   - Pre-payment period: Use original principal
   - Post-payment period: Use remaining principal after offset
3. **Apply offset order**:
   - General debts: Costs → Interest → Principal (per Civil Code Article 561)
   - Judgment debts: Judgment amounts → Delayed performance interest
4. **Sum results**: Total interest = Sum of segments minus offset portions

**Detailed calculator usage**: See `references/calculator_usage_guide.md`

**Interest calculation formulas and parameters**: See `references/amount_and_interest_guide.md` § Interest Calculation

### 🔴 CRITICAL: Calculator Parameter Selection Decision Tree

**⚠️ MANDATORY - Execute BEFORE every calculation**

This decision tree prevents calculation errors by ensuring correct parameter selection based on rate type and scenario context.

#### Step 1: Identify Rate Expression Type

Extract rate description from legal documents/contracts and identify keywords:

**Daily Rate Keywords** (日利率):
- "日利率" (daily rate)
- "每日按...计算" (calculate daily at...)
- "按日息..." (daily interest at...)
- "日息万分之..." (daily interest at X per ten thousand)
- "每日万分之..." (daily X per ten thousand)

**Annual Rate Keywords** (年利率):
- "年利率" (annual rate)
- "年息" (annual interest)
- "按年利率...%" (at annual rate of...)
- "LPR" (ALWAYS annual rate)

#### Step 2: Apply Parameter Selection Rules

**IF identified as "Daily Rate":**
```
→ Use parameter: --daily-rate <percentage>
→ Example 1:
  Legal document: "日利率万分之一"
  → --daily-rate 0.01

→ Example 2:
  Legal document: "每日按千分之二计算"
  → --daily-rate 0.2

⚠️ DO NOT convert to annual rate
⚠️ DO NOT use --rate parameter
⚠️ DO NOT specify --base-days (not applicable for daily rates)
```

**ELIF identified as "Annual Rate":**
```
→ Determine scenario type first:

  IF Scenario = Judicial Ruling (判决/调解/仲裁确认):
      → Use: --rate <annual_rate> --base-days 365
      → Rationale: Civil calculations use calendar year (365/366 days)
      → Example:
        Judgment: "年利率6%"
        → --rate 6 --base-days 365

  ELIF Scenario = Financial Contract (银行贷款/融资租赁):
      → Check if contract specifies base days

      IF contract explicitly states "按360天计算":
          → --rate <annual_rate> --base-days 360

      ELIF contract explicitly states "按365天计算":
          → --rate <annual_rate> --base-days 365

      ELSE (no explicit specification):
          → Default: --rate <annual_rate> --base-days 360
          → Note: Financial industry convention (30 days per month)

  ELIF Scenario = Contract Penalty/Overdue Interest:
      → Default: --rate <annual_rate> --base-days 365
      → Rationale: Civil/commercial contracts use civil calculation rules
```

**ELIF identified as "LPR":**
```
→ Use lpr mode:
→ --multiplier <multiplier> --lpr-term <1y|5y>
```

#### Step 3: Scenario Type Identification Standards

**Judicial Ruling Scenario** - Identification markers:
- ✓ Judgment/mediation/arbitration document exists
- ✓ Rate determined by court/arbitration tribunal
- ✓ Fact-checking report classifies debt as "Legal Document Confirmed Type"

**Financial Contract Scenario** - Identification markers:
- ✓ Main contract is loan/financing/leasing contract
- ✓ Creditor is bank, financial institution, financing company
- ✓ Rate clause appears in contract body

**Contract Breach Scenario** - Identification markers:
- ✓ Main contract is sales/construction/service contract
- ✓ Rate clause is penalty/overdue payment interest clause
- ✓ Commercial transaction between non-financial entities

#### Step 4: Parameter Validation Checklist

Before executing command, verify:

- [ ] If source text is "daily rate", confirmed using --daily-rate parameter
- [ ] If source text is "annual rate" + judicial scenario, confirmed using --base-days 365
- [ ] If source text is "annual rate" + financial scenario, confirmed base-days matches contract
- [ ] Confirmed rate value correctly converted (e.g., 万分之一 = 0.01, NOT 1)
- [ ] Confirmed date parameters format as YYYY-MM-DD

#### Error Case Warnings

**❌ Error Example 1 (Jiangsu Jiangyan Shipbuilding Case - ACTUAL ERROR)**:
```
Legal document: "日利率万分之一"
Wrong approach: --rate 3.65 --base-days 360
Problems:
  (1) Converted daily rate to annual rate
  (2) Used financial base days (360) for civil calculation
  (3) Result error: 1.39% deviation (3,115 yuan excess)

Correct approach: --daily-rate 0.01
```

**❌ Error Example 2**:
```
Judgment: "年利率6%"
Wrong approach: --rate 6 (missing base-days)
Problem: Defaults to 360 days, judicial calculations should use 365 days

Correct approach: --rate 6 --base-days 365
```

**✓ Correct Example 1**:
```
Judgment: "以本金100万元为基数，按日利率万分之二计算"
Correct: --daily-rate 0.02 --principal 1000000 ...
```

**✓ Correct Example 2**:
```
Mediation: "按年利率4.35%计算利息"
Correct: --rate 4.35 --base-days 365 --principal ...
```

**✓ Correct Example 3**:
```
Loan contract: "年利率LPR+50BP，按360天计算"
Correct: --rate <LPR+0.5> --base-days 360 --principal ...
```

#### Critical Reminders

**Key Principle**: "法律文书怎么写，就怎么算" (Calculate exactly as legal document states)

- 🔴 Daily rate → Use --daily-rate (direct calculation, no conversion)
- 🔴 Annual rate + judicial → Use --base-days 365 (calendar year)
- 🔴 Annual rate + financial → Check contract, default 360 (financial convention)
- 🔴 When in doubt → Explicitly specify all parameters, never rely on defaults

### 🔴 CRITICAL: Post-Calculation Self-Check List

**⚠️ MANDATORY - Execute AFTER generating each Excel file**

This checklist prevents calculation errors by validating parameters and results immediately after generation.

#### Self-Check Item 1: Base Days Rationality Verification

**Execution Method**:
Read first 20 rows of generated Excel file, locate "基准天数" (base days) field

**Judgment Rules**:

```
IF found "基准天数: 360":
    IF source document states "日利率" (daily rate):
        → ⚠️ WARNING: Daily rate calculation should NOT show base days
        → Suggestion: Check if should use --daily-rate parameter

    ELIF scenario type is "Judicial Ruling":
        → ⚠️ WARNING: Judicial calculations should use 365-day base
        → Suggestion: Check if should use --base-days 365

    ELIF scenario type is "Contract Penalty":
        → ⚠️ WARNING: Penalty calculations typically use 365 days
        → Suggestion: Verify if contract explicitly specifies 360-day base

IF found "基准天数: 365":
    IF scenario type is "Financial Contract":
        → ⚠️ NOTE: Verify if contract specifies 365 days
        → (Financial contracts typically use 360 days, but need confirmation)
```

#### Self-Check Item 2: Calculation Formula Consistency Verification

**Check content**:
- [ ] Excel displayed formula matches legal document expression
- [ ] If legal document states "日利率", formula should be "本金 × 天数 × 日利率"
- [ ] If legal document states "年利率", formula should be "本金 × (天数/基准) × 年利率"

#### Self-Check Item 3: Rate Value Accuracy Verification

**Common Errors**:
```
❌ 万分之一 → 1 (WRONG)
✓ 万分之一 → 0.01 (CORRECT)

❌ 千分之二 → 2 (WRONG)
✓ 千分之二 → 0.2 (CORRECT)
```

**Verification Method**:
Check Excel rate field value is reasonable (typically < 10)

#### Self-Check Item 4: Calculation Result Reasonableness Verification

**Empirical Rules**:
- Annual rate 6%, 1 year interest → Should be ~6% of principal
- Daily rate 0.01% (万分之一), 1 year interest → Should be ~3.65% of principal
- If result significantly deviates from expectation → Review parameter settings

#### Self-Check Failure Response Procedure

```
1. STOP work immediately, record identified issues
2. Re-examine legal document rate expression
3. Re-execute parameter selection decision tree
4. Regenerate calculation command and execute
5. Execute self-check list again
6. Only proceed with subsequent work after ALL self-checks pass
```

#### Self-Check Documentation Template

**Record in report**:
```markdown
**自检结果** (Self-Check Results):
- 基准天数合理性 (Base Days Rationality): ✓ 通过 / ⚠️ 警告 / ❌ 失败
- 计算公式一致性 (Formula Consistency): ✓ 通过 / ❌ 失败
- 利率数值正确性 (Rate Value Accuracy): ✓ 通过 / ❌ 失败
- 计算结果合理性 (Result Reasonableness): ✓ 通过 / ❌ 失败

**如有警告/失败** (If warnings/failures):
- 问题描述 (Issue Description): <specific issue>
- 处理措施 (Corrective Action): <what was done>
- 重新计算结果 (Recalculation Result): <new result>
```

### Step 4: Statute of Limitations Determination

**Objective**: Determine if claims are time-barred

**Statute Period Determination**:

**Step 1: Determine Start Date**
- Contract debts: Day after contractual performance deadline
- Tort debts: When creditor knew/should have known of damage
- Judgment debts: Day after judgment performance deadline
- No deadline specified: When creditor could first claim

**Step 2: Determine Applicable Period (2 years or 3 years)**

**Standard Process**:
1. Calculate "old law expiration date": Start date + 2 years
2. Apply transition rule:
   - If "old law expiration date" < October 1, 2017 → Apply **2-year** period
   - If "old law expiration date" ≥ October 1, 2017 → Apply **3-year** period

**Example**:
```
Scenario 1:
- Start date: June 1, 2015
- Old law expiration: June 1, 2015 + 2 years = June 1, 2017
- June 1, 2017 < October 1, 2017
- Result: Apply 2-year period

Scenario 2:
- Start date: January 1, 2016
- Old law expiration: January 1, 2016 + 2 years = January 1, 2018
- January 1, 2018 ≥ October 1, 2017
- Result: Apply 3-year period (from January 1, 2016)
```

**Step 3: Review Interruption Events**

**Interruption Types**:

1. **Creditor Active Collection**:
   - Written demand letters with delivery proof
   - Electronic evidence (WeChat, email) with identity confirmation
   - Public notice (only if debtor whereabouts unknown, in provincial+ media)

2. **Debtor Acknowledgment** (MOST POWERFUL):
   - **⚠️ Critical**: Debtor signing/stamping confirmation documents
   - Forms: Reconciliation statements, debt confirmation letters, IOUs, promise letters
   - **⚠️ Mandatory Time Review**:
     * MUST record specific date (not just "before 2025 filing")
     * MUST have evidence supporting the date
     * MUST recalculate period from interruption date
     * MUST compare recalculated expiration with filing date
   - **Partial payment** (before bankruptcy filing) also constitutes acknowledgment

3. **Judicial/Quasi-Judicial Actions**:
   - Lawsuit filing, arbitration application

**Step 4: Review Suspension Events**

**Suspension Conditions**: In last 6 months of statute period, force majeure or obstacles prevent claim

**Calculation**: From suspension end date + 6 months = new expiration date

**Step 5: Compare Final Expiration with Filing Date**

- Expiration date > Filing date → **NOT time-barred**
- Expiration date < Filing date → **Time-barred** (mark as【暂缓确认】)

**Detailed statute analysis methods**: See `references/statute_limitations_guide.md`

### Step 5: Quality Control and Report Generation

**Objective**: Validate results and produce final report + calculation files

**Quality Control Steps**:

1. **Cross-validate amounts**:
   - Compare declared vs. proven amounts
   - Verify each item has evidence support
   - Apply "就低原则": If calculation > declaration, use declaration amount
   - Apply "就无原则": If not declared by creditor, don't include

2. **Verify calculations**:
   - Confirm all interest calculations used calculator tool
   - Check calculation process tables generated
   - Verify dates consistent (bankruptcy dates)
   - Cross-check against fact-checking report

3. **Check report structure**:
   - Independent debt relationships correctly identified
   - All amount items properly categorized
   - Interest parameters complete and accurate
   - Statute of limitations analysis thorough

**Output Requirements**:

1. **《债权分析报告》** in `工作底稿/`:
   - Complete amount breakdown
   - Interest calculation parameters
   - Statute of limitations analysis
   - Final confirmation amounts

2. **Calculation Process Tables** in `计算文件/` (MANDATORY):

   **🔴 CRITICAL: Multi-Calculation Consolidation Standard (2025-11-04更新)**

   **AUTOMATIC FILE CONSOLIDATION RULE**:

   ```
   IF 计算项数量 == 1 (单一计算项):
       → 文件名: {债权人名称}_{计算类型}.xlsx
       → 单sheet，直接生成
       → 示例: "江苏姜堰船舶_逾期付款违约金计算.xlsx"

   ELIF 计算项数量 >= 2 (多个计算项):
       → 文件名: {债权人名称}_计算过程.xlsx（统一命名）
       → 多sheets，每个计算项一个sheet
       → 使用--append参数整合到同一文件
   ```

   **Multi-Sheet Consolidation Implementation**:

   **First Calculation (创建文件)**:
   ```bash
   python universal_debt_calculator_cli.py simple \
     --principal 500000 \
     --start-date 2024-01-01 \
     --end-date 2025-05-08 \
     --rate 4.35 \
     --excel-output "{债权人名称}_计算过程.xlsx" \
     --sheet-name "本金利息" \
     --debtor "{债权人全称}"
   # 注意：第一次调用 NO --append 参数
   ```

   **Subsequent Calculations (追加sheets)**:
   ```bash
   python universal_debt_calculator_cli.py simple \
     --principal 500000 \
     --start-date 2024-06-01 \
     --end-date 2025-05-08 \
     --rate 24 \
     --excel-output "{债权人名称}_计算过程.xlsx" \
     --sheet-name "违约金" \
     --debtor "{债权人全称}" \
     --append  # ⚠️ 关键：追加到同一文件

   python universal_debt_calculator_cli.py delay \
     --principal 500000 \
     --start-date 2025-01-01 \
     --end-date 2025-05-07 \
     --excel-output "{债权人名称}_计算过程.xlsx" \
     --sheet-name "迟延履行利息" \
     --debtor "{债权人全称}" \
     --append  # ⚠️ 关键：追加到同一文件
   ```

   **Final Result**: 1个Excel文件包含3个sheets（本金利息、违约金、迟延履行利息）

   **Sheet Naming Standards**:
   - 本金利息、借款利息、逾期利息 (各类利息计算)
   - 违约金 (违约金计算)
   - 迟延履行利息 (迟延履行期间债务利息)
   - 使用简洁描述性名称，方便律师审阅时快速定位

   **File Consolidation Verification**:
   - [ ] 多计算项场景（≥2项）仅生成1个Excel文件
   - [ ] Excel文件包含的sheet数量 = 计算项数量
   - [ ] 第一项计算命令未使用--append
   - [ ] 后续计算命令全部使用--append
   - [ ] 文件命名为 `{债权人名称}_计算过程.xlsx`

   **❌ PROHIBITED Multi-File Pattern (旧模式)**:
   ```
   ❌ 江苏姜堰船舶_逾期付款违约金计算.xlsx (独立文件)
   ❌ 江苏姜堰船舶_迟延履行加倍利息计算.xlsx (独立文件)

   问题：多个独立文件，律师需要打开多个Excel审阅，不便利
   ```

   **✅ REQUIRED Multi-Sheet Pattern (新标准)**:
   ```
   ✅ 江苏姜堰船舶_计算过程.xlsx
      ├─ Sheet 1: 逾期付款违约金
      └─ Sheet 2: 迟延履行利息

   优势：所有计算集中在1个文件，审阅便利
   ```

   **"No calculation" scenario (ONLY if)**:
   - Creditor declared ZERO interest/penalty items, AND
   - All amounts are fixed (no calculations needed), AND
   - Create `{债权人名称}_无计算项说明.txt` with clear explanation

   ⚠️ **PROHIBITED** (异常模式):
   - ❌ Creating `计算过程说明.md` files as substitutes when calculations exist
   - ❌ Using TXT/MD files to "explain" calculations instead of generating Excel
   - ❌ Recording calculator commands but not executing with --excel-output
   - ❌ Generating multiple independent Excel files for multi-calculation scenarios (NEW)

3. **File Inventory**: List all generated files

**Template**: See `templates/debt_analysis_report_template.md`

**QC checklist**: See `references/quality_control_guide.md`

## Critical Tools

### Universal Debt Calculator CLI

**Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**Key Features**:
- Embedded LPR rate data (2019-2025, updated regularly)
- Automatic calculation process table generation (Excel/CSV)
- Five interest calculation modes: simple, LPR, delay, compound, penalty
- JSON input/output support
- No external dependencies (Python standard library only)

**Basic Syntax**:
```bash
python universal_debt_calculator_cli.py <mode> [options]

Modes:
  simple    - Simple interest (fixed rate)
  lpr       - LPR floating rate interest
  delay     - Delayed performance interest
  compound  - Compound interest
  penalty   - Penalty interest

Common Options:
  --principal <amount>        - Principal amount
  --start-date <YYYY-MM-DD>   - Interest start date
  --end-date <YYYY-MM-DD>     - Interest end date (stop-interest date)
  --rate <percentage>         - Annual rate (for simple/compound)
  --multiplier <number>       - LPR multiplier (for LPR mode)
  --lpr-term <1y|5y>          - LPR term selection
  --json-input <file>         - JSON input file
  --json-output <file>        - JSON output file
```

**Full documentation**: See `references/calculator_usage_guide.md`

## Core Application Rules

### Rule 1: 就低原则 (Lower Bound Rule)

**When**: Calculation result > Creditor's declared amount

**Action**: Use declared amount as final confirmation (就低)

**Example**: Creditor declares 10,000 interest, calculation shows 12,000 → Confirm 10,000

### Rule 2: 就无原则 (Non-Existence Rule) - 完整决策树

**核心规则**: 债权人未申报的事项,一律不予确认(即使证据显示存在)

#### 🔍 精确应用决策树

**第1步: 检查债权申报表**
```
事项已在申报表中列明?
├─ 是 → 进入第2步
└─ 否 → ❌ 停止处理,不予确认(就无原则)
         → 标注:"证据显示[X],但债权人未申报,不予确认"
```

**第2步: 检查申报颗粒度(是否拆分子项)**
```
债权人申报方式:
├─ 单一项申报(如"利息50万元")
│   → 只能确认总额50万,不能拆分子类型
│   → ❌ 禁止:"申报利息50万,我拆成本金利息30万+复利20万"
│   → ✅ 正确:"确认利息50万元(债权人未细分类型)"
│
└─ 细分申报(如"本金利息30万+复利20万")
    → 可以分别分析各子项
    → 每个子项独立应用就低原则
```

**第3步: 证据金额 vs 申报金额对比**
```
证据显示金额 vs 申报金额:
├─ 证据金额 > 申报金额
│   → 确认申报金额(就低原则)
│   → 备注:"证据显示[大额],债权人申报[小额],确认[小额]"
│
└─ 证据金额 ≤ 申报金额
    → 正常分析,以证据为准
```

#### ❌ 典型错误模式(绝对禁止)

**错误1: 代替债权人拆分申报项**
```
❌ 错误:"债权人申报'欠款100万',证据显示可拆分为(本金80万+利息20万),
         所以我确认本金80万+利息20万"
原因:债权人选择不拆分,审查员不能代为拆分

✅ 正确:"债权人申报'欠款100万',虽证据显示可拆分,但债权人未拆分申报,
         确认'普通债权100万元'(不细分类型)"
```

**错误2: 根据证据添加未申报项**
```
❌ 错误:"债权人申报'本金50万',判决书包含迟延履行利息条款,
         所以我计算并确认迟延履行利息5万"
原因:债权人未申报迟延利息,不能因证据存在就添加

✅ 正确:"债权人申报'本金50万',未申报迟延履行利息。
         确认:本金50万元。
         备注:判决书第X条包含迟延履行利息条款,但债权人未申报此项,不予确认"
```

**错误3: 根据合同约定计算未申报项**
```
❌ 错误:"债权人未申报违约金,但合同第8条约定违约金为本金10%,
         计算违约金10万元并确认"
原因:即使合同明确约定,债权人未申报就不确认

✅ 正确:"债权人未申报违约金。
         备注:合同约定违约金条款,但债权人未申报,不予确认"
```

**错误4: 用"就低原则"确认未申报项**
```
❌ 错误:"债权人未申报利息,但我算出利息30万,按就低原则确认0元"
原因:就低原则用于比较已申报项,不用于未申报项

✅ 正确:"债权人未申报利息,不予确认(就无原则),无需计算"
```

**错误5: 将申报总额拆分为未申报子项**
```
❌ 错误:"债权人申报'债权总额100万',我根据证据拆分为:
         本金80万+利息15万+违约金5万=100万"
原因:债权人只申报了总额,未声明各子项构成

✅ 正确:"债权人申报'债权总额100万',未细分构成。
         确认:普通债权100万元(不拆分子项)"
```

#### ✅ 正确处理模式

**模式1: 已申报项的正常确认**
```
债权人申报:本金100万+利息50万
证据验证:合同本金100万,利息计算结果80万
处理:
  - 本金:申报100万=证据100万 → 确认100万
  - 利息:申报50万<证据80万 → 确认50万(就低原则)
```

**模式2: 未申报项的正确处理**
```
债权人申报:本金100万
证据显示:合同约定本金100万+年利率6%+违约金条款
处理:
  - 本金:已申报 → 确认100万
  - 利息:未申报 → 不予确认,备注"合同约定利率但债权人未申报"
  - 违约金:未申报 → 不予确认,备注"合同约定违约金但债权人未申报"
```

**模式3: 单一项申报的处理**
```
债权人申报:利息50万元(未细分类型)
证据显示:可拆分为本金利息30万+复利20万
处理:
  ❌ 错误:拆分确认本金利息30万+复利20万
  ✅ 正确:确认利息50万元,备注"债权人未细分利息类型,以申报总额确认"
```

#### 📊 "就无原则"判断流程图

```
                    开始审查某项金额
                           ↓
        ┌──────────────────────────────────┐
        │ 债权人在申报表中列明了此项? │
        └──────────────────────────────────┘
                 ↙              ↘
              是                  否
              ↓                   ↓
    ┌─────────────────┐   ┌──────────────────┐
    │ 检查申报颗粒度  │   │ ❌ 不予确认     │
    │ (总额 vs 拆分)│   │ (就无原则)      │
    └─────────────────┘   │                  │
             ↓               │ 备注:证据显示XX │
   申报为总额 vs 细分?      │ 但债权人未申报   │
      ↙        ↘            └──────────────────┘
    总额       细分
     ↓          ↓
  只确认     分别分析
  总额      各子项
     ↓          ↓
   应用       应用
  就低原则   就低原则
```

#### ⚠️ 特别提示

1. **"就无原则"优先级 > "证据充分性"**
   - 即使证据100%充分证明某项存在,债权人未申报也不确认

2. **债权审查 ≠ 债权申报代理**
   - 审查员的职责是验证申报内容,不是帮债权人"补全"申报

3. **未申报项的处理方式**
   - 在审查意见中提示债权人:"XX证据显示XX项,但您未申报,如需主张请补充申报"
   - 不是直接确认未申报项

4. **申报表是唯一边界**
   - 申报表中有的 → 可以审查确认
   - 申报表中没有的 → 不予确认(无论证据多充分)

**⚠️ Important**: Don't proactively calculate delayed performance interest if creditor didn't declare it

### Rule 3: Evidence Support Rule

**Requirements**:
- Creditor-declared items without evidence support → NOT confirmed
- Evidence-proven items not declared by creditor → NOT included

### Rule 4: Court Fee Special Rule

**Important**: Do NOT calculate delayed performance interest on court fees
- Court fees have separate performance deadlines
- Need individual assessment for deadline expiration
- Even if expired, be cautious about calculating delayed interest

## Error Prevention Quick Checklist

**Before Finalizing**:
- [ ] All interest calculations use calculator tool (no manual calculations)
- [ ] Bankruptcy dates verified and consistent with fact-checking report
- [ ] Calculation process tables generated and saved to `计算文件/`
- [ ] Amounts cross-validated against fact-checking report
- [ ] LPR term selection reviewed for debts > 5 years
- [ ] Delayed performance interest prerequisites verified (judgment + expired + declared)
- [ ] Statute of limitations analysis documented with evidence
- [ ] 就低原则 and 就无原则 applied correctly
- [ ] Report follows template structure
- [ ] All files properly named and located

**Complete checklist**: See `references/quality_control_guide.md`

## Quick Reference

### Interest Rate Reference (2024)

| 利率类型 | 参考值 | 备注 |
|---------|-------|------|
| 1年期LPR | 3.45% | 一般商事债权常用 |
| 5年期以上LPR | 3.95% | 长期贷款、超5年债权 |
| 法定利率上限 | LPR × 4 | 民间借贷利率保护上限 |
| 迟延履行利率 | 日利率0.0175% | 固定，仅适用判决债权 |

### Calculation File Naming Convention

```
[债权人编号]-[债权人名称]-[类型].xlsx

Examples:
115-东航建筑-逾期利息计算表.xlsx
115-东航建筑-借款利息计算表.xlsx
115-东航建筑-迟延履行利息计算表.xlsx
```

### Amount Item Classification

```
本金类: XX合同项下的XX款项
利息类: 基于XX本金，按XX标准计算的XX利息
费用类: XX判决书判令的XX费用
```

### LPR Term Decision Tree

```
债权期限 ≤ 5年? ─Yes→ 优先考虑1年期LPR
    │
    No
    ↓
债权期限 > 5年? ─Yes→ 必须重点考虑5年期以上LPR
    │              │
    │              ├→ 合同明确约定? ─Yes→ 从其约定
    │              │
    │              └→ 未明确约定? ─Yes→ 审慎判断，考虑适用5年期
```

## 复杂案件进阶参考

如遇越权担保、保理争议、建设工程优先权、个别清偿认定、抵销权争议等复杂法律问题，可参考**debt-review-legal-standards** Skill进行深度分析。

**⚠️ 注意**: 常规债权审查（普通买卖、标准借款、常规工程款）无需使用该Skill，使用本Skill即可完成。
