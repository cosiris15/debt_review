# Universal Debt Calculator CLI - Complete Usage Guide

## Overview

The `universal_debt_calculator_cli.py` is a standalone command-line tool for calculating various types of debt interest with embedded LPR rate data and automatic calculation process table generation.

**Tool Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

## Key Features

- **Five calculation modes**: Simple interest, LPR floating rate, delayed performance interest, compound interest, penalty interest
- **Embedded LPR data**: 2019-2025 LPR rates built-in, regularly updated
- **Auto-generate tables**: Excel/CSV calculation process tables for audit trail
- **No dependencies**: Uses only Python standard library
- **JSON support**: Batch processing with JSON input/output
- **Precise calculations**: Handles segmented periods, payment offsets, rate changes

## Basic Syntax

```bash
python universal_debt_calculator_cli.py <mode> [options]
```

**Five Modes**:
- `simple` - Simple interest (fixed annual rate)
- `lpr` - LPR floating rate interest
- `delay` - Delayed performance interest (迟延履行期间债务利息)
- `compound` - Compound interest
- `penalty` - Penalty interest (违约金)

## Common Options

### Required Parameters (vary by mode)

```
--principal <amount>        Principal amount (required for all modes)
--start-date <YYYY-MM-DD>   Interest start date (required for all modes)
--end-date <YYYY-MM-DD>     Interest end date / stop-interest date (required for all modes)
```

### Mode-Specific Parameters

```
--rate <percentage>         Annual interest rate (for simple/compound modes)
--multiplier <number>       LPR multiplier (for lpr mode), e.g., 1.5 for LPR × 1.5
--lpr-term <1y|5y>          LPR term selection: 1y or 5y (for lpr mode)
--cycle <description>       Compounding cycle (for compound mode), e.g., "每月末", "每季度末"
```

### Output Options

```
--excel-output <filename>   Generate Excel output (.xlsx)
--csv-output <filename>     Generate CSV output (.csv)
--sheet-name <name>         Excel sheet name (default: "计算过程")
--append                    Append to existing Excel file (for multiple calculations)
--debtor <name>             Debtor name (included in output metadata)
```

### JSON Mode

```
--json-input <file>         Read parameters from JSON file
--json-output <file>        Write results to JSON file
```

## Detailed Mode Usage

### Mode 1: Simple Interest (固定利率)

**Usage**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 4.35
```

**Required Parameters**:
- `--principal`: Principal amount
- `--start-date`: Interest start date
- `--end-date`: Interest end date
- `--rate`: Annual interest rate (percentage)

**Example with Excel Output**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 500000 \
  --start-date 2023-03-15 \
  --end-date 2025-05-08 \
  --rate 6.0 \
  --excel-output "张三公司_借款利息.xlsx" \
  --debtor "张三公司"
```

**Output**:
- Console: Total interest amount
- Excel: Detailed calculation table with daily breakdown

**When to Use**:
- Loan contracts with fixed interest rate
- Contractually agreed fixed overdue interest rate
- Any fixed-rate interest calculation

### Mode 2: LPR Floating Rate Interest

**Usage**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --multiplier 1.5 \
  --lpr-term 1y
```

**Required Parameters**:
- `--principal`: Principal amount
- `--start-date`: Interest start date
- `--end-date`: Interest end date
- `--multiplier`: LPR multiplier (e.g., 1.5 for LPR × 1.5, 4.0 for 4× LPR cap)
- `--lpr-term`: LPR term - `1y` for 1-year LPR or `5y` for 5-year+ LPR

**Example - 1-Year LPR**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 200000 \
  --start-date 2023-06-01 \
  --end-date 2025-05-11 \
  --multiplier 1.5 \
  --lpr-term 1y \
  --excel-output "李四公司_逾期利息.xlsx" \
  --debtor "李四公司"
```

**Example - 5-Year LPR (Long-term debt)**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 1000000 \
  --start-date 2018-01-01 \
  --end-date 2025-05-11 \
  --multiplier 1.0 \
  --lpr-term 5y \
  --excel-output "王五公司_长期贷款利息.xlsx" \
  --debtor "王五公司"
```

**Output**:
- Automatically segments calculation by LPR rate change dates
- Shows applicable LPR rate for each period
- Calculates interest for each segment
- Provides total interest amount

**When to Use**:
- Contracts specifying LPR-based interest
- Overdue interest when no fixed rate specified (default to 1y LPR)
- Long-term debts > 5 years (consider 5y LPR)
- Penalty caps (use multiplier 4.0 to calculate 4× LPR limit)

**⚠️ LPR Term Selection**:
- **≤ 5 years**: Use `--lpr-term 1y`
- **> 5 years**: Strongly consider `--lpr-term 5y`
- See `amount_and_interest_guide.md` for detailed selection rules

### Mode 3: Delayed Performance Interest (迟延履行期间债务利息)

**Usage**:
```bash
python universal_debt_calculator_cli.py delay \
  --principal 100000 \
  --start-date 2024-06-01 \
  --end-date 2024-12-31
```

**Required Parameters**:
- `--principal`: Amount in delayed performance (迟延履行的款项)
- `--start-date`: Interest start date (day after performance deadline expires)
- `--end-date`: Interest end date (usually bankruptcy filing date - 1 day)

**Note**: Rate is fixed at daily 0.0175% (万分之1.75), no `--rate` parameter needed.

**Example**:
```bash
python universal_debt_calculator_cli.py delay \
  --principal 120000 \
  --start-date 2025-03-21 \
  --end-date 2025-05-07 \
  --excel-output "上海金桥信息_迟延履行利息.xlsx" \
  --debtor "上海金桥信息股份有限公司"
```

**Output**:
- Daily calculation at fixed rate 0.0175%
- Total days in delayed performance
- Total delayed performance interest

**When to Use**:
- ONLY for judgment/mediation/arbitration debts
- ONLY when performance deadline has expired
- ONLY when creditor declared this item (就无原则)

**⚠️ Prerequisites**:
1. Must be judgment debt (effective legal document)
2. Performance deadline must have expired
3. Creditor must have declared this interest

### Mode 4: Compound Interest

**Usage**:
```bash
python universal_debt_calculator_cli.py compound \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 4.35 \
  --cycle "每月末"
```

**Required Parameters**:
- `--principal`: Initial principal amount
- `--start-date`: Interest start date
- `--end-date`: Interest end date
- `--rate`: Annual interest rate (percentage)
- `--cycle`: Compounding cycle description (e.g., "每月末", "每季度末", "每年末")

**Example - Monthly Compounding**:
```bash
python universal_debt_calculator_cli.py compound \
  --principal 500000 \
  --start-date 2023-01-01 \
  --end-date 2025-05-11 \
  --rate 5.5 \
  --cycle "每月末" \
  --excel-output "赵六公司_复利计算.xlsx" \
  --debtor "赵六公司"
```

**Output**:
- Shows compounding at each cycle point
- Displays principal growth after each compounding
- Total compound interest amount

**When to Use**:
- Contract explicitly provides for compound interest
- Interest-on-interest calculations
- Rare in ordinary commercial debts

**⚠️ Legal Requirement**: Compound interest must have explicit contractual basis.

### Mode 5: Penalty Interest

**Usage**: Similar to `simple` or `lpr` mode, but specifically for penalty calculations.

```bash
python universal_debt_calculator_cli.py penalty \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 24.0
```

**When to Use**:
- Calculating contractual penalties (违约金)
- Verifying penalties against 4× LPR cap

**⚠️ Important**: Always check penalty against 4× LPR legal maximum.

## Advanced Usage

### 🔴 Multiple Calculations for Same Creditor (2025-11-04 Updated Standard)

**Use Case**: Same creditor has multiple interest items (e.g., loan interest + delayed performance interest).

**🚨 MANDATORY FILE CONSOLIDATION RULE**:

```
Decision Tree:

IF 计算项数量 == 1:
    → File: {债权人名称}_{计算类型}.xlsx
    → Single sheet
    → No --append needed
    → Example: "张三公司_借款利息计算.xlsx"

ELIF 计算项数量 >= 2:
    → File: {债权人名称}_计算过程.xlsx  (UNIFIED NAMING)
    → Multiple sheets (one per calculation)
    → First calculation: NO --append
    → Subsequent calculations: MUST use --append
    → Example: "张三公司_计算过程.xlsx" (contains multiple sheets)
```

**Rationale**:
- Single file with multiple sheets improves lawyer review efficiency
- All calculations consolidated in one location
- Prevents scattered Excel files
- Aligns with professional audit trail standards

**✅ CORRECT Implementation (Multi-Calculation Scenario)**:

```bash
# Scenario: Creditor has 3 calculation items
# - Loan interest
# - Penalty
# - Delayed performance interest

# Step 1: First calculation - CREATE file (NO --append)
python universal_debt_calculator_cli.py simple \
  --principal 500000 \
  --start-date 2024-01-01 \
  --end-date 2025-05-08 \
  --rate 4.35 \
  --excel-output "张三公司_计算过程.xlsx" \
  --sheet-name "借款利息" \
  --debtor "张三公司"
# Note: First call does NOT use --append

# Step 2: Second calculation - APPEND to same file
python universal_debt_calculator_cli.py simple \
  --principal 500000 \
  --start-date 2024-06-01 \
  --end-date 2025-05-08 \
  --rate 24 \
  --excel-output "张三公司_计算过程.xlsx" \
  --sheet-name "违约金" \
  --debtor "张三公司" \
  --append
# ⚠️ Critical: Use --append to add new sheet to existing file

# Step 3: Third calculation - APPEND to same file
python universal_debt_calculator_cli.py delay \
  --principal 500000 \
  --start-date 2025-01-01 \
  --end-date 2025-05-07 \
  --excel-output "张三公司_计算过程.xlsx" \
  --sheet-name "迟延履行利息" \
  --debtor "张三公司" \
  --append
# ⚠️ Critical: Use --append for all subsequent calculations
```

**Result**:
- **Single file**: `张三公司_计算过程.xlsx`
- **Three sheets**: "借款利息", "违约金", "迟延履行利息"
- **Lawyer experience**: Open one file, review all calculations across sheets

**❌ PROHIBITED Pattern (Old approach - multiple files)**:

```bash
# ❌ DO NOT DO THIS:
python ... --excel-output "张三公司_借款利息计算.xlsx" ...
python ... --excel-output "张三公司_违约金计算.xlsx" ...
python ... --excel-output "张三公司_迟延履行利息计算.xlsx" ...

# Problem: Creates 3 separate files
# Lawyer must open 3 Excel files to review all calculations
# Inconvenient and increases risk of missing files
```

**Verification Checklist**:
- [ ] Multi-calculation scenario (≥2 items) generates exactly 1 Excel file
- [ ] File named as `{债权人}_计算过程.xlsx`
- [ ] First calculation command does NOT include --append
- [ ] All subsequent calculations include --append
- [ ] Excel file contains correct number of sheets matching calculation items
- [ ] Sheet names are descriptive (借款利息, 违约金, 迟延履行利息, etc.)

### Segmented Calculation with Payment Offsets

**Use Case**: Debtor made payments during debt period, requiring segmented calculation.

**Approach**: Calculate each segment separately, then sum results minus offsets.

**Example**:
```
Debt: 100,000 principal, overdue interest from 2023-01-01
Payment 1: 2023-06-15, paid 20,000
Payment 2: 2023-10-20, paid 15,000
End: 2025-05-11

Offset order (general debt): Costs → Interest → Principal
```

**Calculation Steps**:

1. Calculate Segment 1 (2023-01-01 to 2023-06-15):
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2023-01-01 \
  --end-date 2023-06-15 \
  --multiplier 1.5 \
  --lpr-term 1y \
  --excel-output "某公司_逾期利息.xlsx" \
  --sheet-name "期间1" \
  --debtor "某公司"
```

2. Apply offset (assume no costs, 20,000 offsets interest first, remainder to principal):
   - Segment 1 interest: X yuan (from calculation)
   - If X < 20,000: All interest paid, (20,000 - X) reduces principal
   - New principal: 100,000 - (20,000 - X)

3. Calculate Segment 2 (2023-06-15 to 2023-10-20) with new principal:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal <new_principal> \
  --start-date 2023-06-15 \
  --end-date 2023-10-20 \
  --multiplier 1.5 \
  --lpr-term 1y \
  --excel-output "某公司_逾期利息.xlsx" \
  --sheet-name "期间2" \
  --append \
  --debtor "某公司"
```

4. Repeat for remaining segments...

5. Sum all segment interests minus offset amounts = Final interest

### Rate Change Handling

**Use Case**: LPR rate changed during calculation period (automatically handled in `lpr` mode).

**Example**:
```bash
# LPR mode automatically segments by LPR rate change dates
python universal_debt_calculator_cli.py lpr \
  --principal 300000 \
  --start-date 2022-01-01 \
  --end-date 2025-05-11 \
  --multiplier 1.5 \
  --lpr-term 1y \
  --excel-output "某公司_LPR浮动利息.xlsx" \
  --debtor "某公司"
```

**Output**: Automatically shows:
- 2022-01-01 to 2022-05-19: LPR 3.70% × 1.5
- 2022-05-20 to 2022-08-21: LPR 3.65% × 1.5
- ... (all LPR rate changes)
- Total interest across all periods

## JSON Input/Output Mode

### JSON Input Format

**Use Case**: Batch processing or complex parameters.

**Input File** (`input.json`):
```json
{
  "mode": "lpr",
  "principal": 100000,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "multiplier": 1.5,
  "lpr_term": "1y",
  "debtor": "某公司"
}
```

**Command**:
```bash
python universal_debt_calculator_cli.py --json-input input.json --json-output result.json
```

**Output File** (`result.json`):
```json
{
  "total_interest": 5234.52,
  "calculation_details": [
    {
      "period": "2024-01-01 to 2024-05-19",
      "days": 140,
      "rate": "5.175%",
      "interest": 1987.67
    },
    ...
  ]
}
```

### Batch Processing Multiple Claims

**Create batch input file** (`batch.json`):
```json
[
  {
    "creditor": "公司A",
    "mode": "simple",
    "principal": 100000,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "rate": 4.35
  },
  {
    "creditor": "公司B",
    "mode": "lpr",
    "principal": 200000,
    "start_date": "2023-06-01",
    "end_date": "2024-12-31",
    "multiplier": 1.5,
    "lpr_term": "1y"
  }
]
```

**Process**: Loop through and call calculator for each item.

## Output Formats

### Console Output

**Standard output** shows:
- Calculation parameters
- Segmented period details (if applicable)
- Total interest amount
- Calculation formula

**Example**:
```
计算参数:
- 本金: 100,000.00元
- 起息日: 2024-01-01
- 止息日: 2024-12-31
- 利率: LPR 1年期 × 1.5

分段计算:
期间1: 2024-01-01 至 2024-05-19 (140天)
  适用利率: 3.45% × 1.5 = 5.175%
  期间利息: 1,987.67元

期间2: 2024-05-20 至 2024-12-31 (226天)
  适用利率: 3.35% × 1.5 = 5.025%
  期间利息: 3,115.48元

总利息: 5,103.15元
```

### Excel Output (.xlsx)

**File Structure**:
- **Sheet 1** (or named sheet): Calculation process table
  - Column A: Date
  - Column B: Days
  - Column C: Applicable rate
  - Column D: Daily interest
  - Column E: Cumulative interest
  - ...
- **Metadata rows**: Debtor name, calculation period, parameters
- **Summary row**: Total interest

**Naming Convention**:
- Single calculation: `债权人名称_计算类型.xlsx`
- Multiple calculations: `债权人名称_计算过程.xlsx` (with multiple sheets)

**Example filename**: `张三公司_逾期利息.xlsx`

### CSV Output (.csv)

**Format**: Same structure as Excel, but plain text CSV format.

**Use Case**: When Excel not available, or for importing into other tools.

## File Naming Standards

### For Calculation Files

**Pattern**: `[债权人编号]-[债权人名称]-[类型].xlsx`

**Examples**:
```
115-东航建筑-逾期利息计算表.xlsx
115-东航建筑-借款利息计算表.xlsx
115-东航建筑-迟延履行利息计算表.xlsx
```

### For No-Calculation Cases

**When**: Debt claim has NO interest calculations (only fixed amounts).

**File**: Create TXT explanation file instead.

**Pattern**: `[债权人编号]-[债权人名称]-无计算项说明.txt`

**Content Example**:
```
========================================
债权人：慈溪市东航建筑起重机械安装队
债权人编号：115
生成时间：2025-05-10
说明：本债权仅涉及固定金额确认，无需进行利息或其他金额计算。

确认金额明细：
- 货款本金：132,216.00元（固定金额）
- 案件受理费：2,500元（固定金额）

总计：134,716.00元
========================================
```

## Common Usage Scenarios

### Scenario 1: Simple Overdue Interest (Fixed Rate)

**Situation**: Contract specifies fixed overdue interest rate.

**Command**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 132216 \
  --start-date 2023-04-16 \
  --end-date 2025-05-11 \
  --rate 24.0 \
  --excel-output "115-东航建筑-逾期利息.xlsx" \
  --debtor "慈溪市东航建筑起重机械安装队"
```

### Scenario 2: LPR-Based Overdue Interest

**Situation**: No fixed rate specified, use 1-year LPR × 1.5.

**Command**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 200000 \
  --start-date 2023-06-01 \
  --end-date 2025-05-11 \
  --multiplier 1.5 \
  --lpr-term 1y \
  --excel-output "120-某公司-逾期利息.xlsx" \
  --debtor "某公司"
```

### Scenario 3: Long-term Debt (> 5 years) with LPR

**Situation**: Debt period exceeds 5 years, must consider 5-year LPR.

**Command**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 1000000 \
  --start-date 2018-03-01 \
  --end-date 2025-05-11 \
  --multiplier 1.0 \
  --lpr-term 5y \
  --excel-output "125-某公司-长期贷款利息.xlsx" \
  --debtor "某公司"
```

### Scenario 4: Delayed Performance Interest on Judgment

**Situation**: Judgment effective 2025-03-20, performance deadline 2025-03-20, not performed.

**Command**:
```bash
python universal_debt_calculator_cli.py delay \
  --principal 120000 \
  --start-date 2025-03-21 \
  --end-date 2025-05-07 \
  --excel-output "130-某公司-迟延履行利息.xlsx" \
  --debtor "某公司"
```

**Note**: Start date is day AFTER deadline (2025-03-21).

### Scenario 5: Penalty Cap Verification

**Situation**: Contract penalty 24%, need to verify against 4× LPR cap.

**Step 1** - Calculate contractual penalty:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 24.0 \
  --excel-output "违约金_合同约定.xlsx"
```

**Step 2** - Calculate 4× LPR cap:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --multiplier 4.0 \
  --lpr-term 1y \
  --excel-output "违约金_法定上限.xlsx"
```

**Step 3** - Compare results, use lesser amount (also apply 就低原则).

## Error Prevention

### Common Mistakes to Avoid

1. **Wrong end date**: Setting end date AFTER bankruptcy filing date
   - ❌ Wrong: `--end-date 2025-05-13` (if bankruptcy date is 2025-05-12)
   - ✅ Right: `--end-date 2025-05-11` (bankruptcy date - 1 day)

2. **Wrong LPR term for long-term debts**:
   - ❌ Wrong: Using `--lpr-term 1y` for 7-year debt period
   - ✅ Right: Using `--lpr-term 5y` and documenting rationale

3. **Calculating delayed interest without prerequisites**:
   - ❌ Wrong: Calculating for contract debt (not judgment)
   - ✅ Right: Only for judgment debts with expired deadlines

4. **Not using calculator for segmented calculations**:
   - ❌ Wrong: Manually calculating payment offset adjustments
   - ✅ Right: Using calculator for each segment with correct principal

### Verification Steps

Before finalizing:
- [ ] Verified principal amount matches evidence
- [ ] Checked start date is correct (overdue date, loan date, etc.)
- [ ] Confirmed end date ≤ bankruptcy filing date - 1 day
- [ ] Selected appropriate LPR term (1y vs 5y) based on period
- [ ] Generated Excel/CSV output for audit trail
- [ ] Verified total interest amount is reasonable
- [ ] Applied 就低原则 (compare with declared amount)

## Summary

**Golden Rules**:
1. **ALWAYS use calculator** - No manual calculations
2. **ALWAYS generate output files** - Excel/CSV for audit trail
3. **ALWAYS verify dates** - Especially end date ≤ bankruptcy date - 1
4. **ALWAYS select correct LPR term** - 1y vs 5y based on debt period
5. **ALWAYS apply 就低原则** - Final amount ≤ declared amount

**Tool Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**For detailed parameter selection rules**: See `amount_and_interest_guide.md`
