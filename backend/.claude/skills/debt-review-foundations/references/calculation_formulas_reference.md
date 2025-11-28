# Calculation Formulas Reference

## Purpose

This document provides comprehensive calculation formulas, rate data, and computational methods for all types of debt interest calculations in bankruptcy proceedings.

## Part 1: Calculator Tool Overview

### Mandatory Tool Usage

**⚠️ CRITICAL**: ALL calculations MUST use `/root/debt_review_skills/universal_debt_calculator_cli.py`

**NO manual calculations permitted**

**Rationale**:
- Ensures accuracy and consistency
- Auto-generates audit trail (Excel/CSV)
- Embedded LPR rate data (2019-2025)
- Handles complex segmentation automatically

### Five Calculation Modes

| Mode | Use For | Key Parameters |
|------|---------|----------------|
| `simple` | Fixed rate interest | --rate (annual %) |
| `lpr` | LPR floating rate | --multiplier, --lpr-term (1y/5y) |
| `delay` | Delayed performance interest | (rate is fixed 0.0175% daily) |
| `compound` | Compound interest | --rate, --cycle |
| `penalty` | Penalty interest | --rate or --multiplier |

## Part 2: Simple Interest Calculation

### Formula

```
Total Interest = Principal × Annual Rate × (Days / Base Days)
```

**Where**:
- Principal = Amount bearing interest
- Annual Rate = Fixed annual percentage rate (e.g., 4.35% = 0.0435)
- Days = Number of days in interest period
- Base Days = 360 or 365 (per contract specification)

### Calculator Command

```bash
python universal_debt_calculator_cli.py simple \
  --principal <amount> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD> \
  --rate <percentage>
```

**Example**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 4.35
```

### When to Use

- Loan contracts with fixed interest rate
- Contract overdue interest with fixed rate specified
- Any fixed-rate interest calculation

### Parameters

- **Principal**: Must match evidence (contract, judgment)
- **Start Date**: Loan disbursement date OR day after payment deadline
- **End Date**: ≤ Bankruptcy filing date - 1 day
- **Rate**: Contractual annual rate (as percentage, e.g., 4.35 not 0.0435)

## Part 3: LPR Floating Rate Calculation

### Formula

```
For each LPR rate period:
  Period Interest = Principal × (LPR × Multiplier) × (Days / Base Days)

Total Interest = Sum of all period interests
```

**Where**:
- LPR = Loan Prime Rate for the applicable period
- Multiplier = Contract multiplier (e.g., 1.5 for "LPR × 1.5")
- Calculator automatically segments by LPR rate change dates

### Calculator Command

```bash
python universal_debt_calculator_cli.py lpr \
  --principal <amount> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD> \
  --multiplier <number> \
  --lpr-term <1y|5y>
```

**Example - 1-Year LPR**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 200000 \
  --start-date 2023-06-01 \
  --end-date 2025-05-11 \
  --multiplier 1.5 \
  --lpr-term 1y
```

**Example - 5-Year LPR**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 1000000 \
  --start-date 2018-01-01 \
  --end-date 2025-05-11 \
  --multiplier 1.0 \
  --lpr-term 5y
```

### LPR Term Selection (CRITICAL)

**⚠️ Mandatory Period Assessment**:

1. **Calculate total debt period**: Start date → Bankruptcy filing date - 1
2. **Record period clearly**: Note total days/years
3. **Apply selection rule**:
   - Period ≤ 5 years → Prioritize **1-year LPR** (`--lpr-term 1y`)
   - Period > 5 years → **MUST consider 5-year+ LPR** (`--lpr-term 5y`)

**Selection Guidelines**:

**Use 1-Year LPR When**:
- Short-term debts (performance period ≤ 5 years)
- Short-term loans (loan term ≤ 5 years)
- General commercial debts (sales, service contracts)
- Default choice if period not specified

**Use 5-Year+ LPR When**:
- Long-term loans (loan term > 5 years, e.g., mortgage)
- Long-term debts (performance period > 5 years)
- Contract explicitly specifies 5-year LPR
- Construction long-term arrears (unpaid > 5 years)
- Court explicitly applied 5-year LPR

**⚠️ Special Review Required**:
- When creditor declares fixed rate BUT debt period > 5 years
- MUST review whether 5-year+ LPR floating rate should apply instead

### LPR Rate Data Table (2019-2025)

#### 1-Year LPR History

| Effective Date | Rate | Effective Date | Rate |
|----------------|------|----------------|------|
| 2019-08-20 | 4.25% | 2022-05-20 | 3.70% |
| 2019-09-20 | 4.20% | 2022-08-22 | 3.65% |
| 2019-11-20 | 4.15% | 2023-06-20 | 3.55% |
| 2020-02-20 | 4.05% | 2023-08-21 | 3.45% |
| 2020-04-20 | 3.85% | 2024-07-22 | 3.35% |
| 2020-05-20 | 3.85% | 2024-10-21 | 3.10% |
| 2021-12-20 | 3.80% | 2025-01-20 | 3.00% |
| 2022-01-20 | 3.70% | (current) | 3.00% |

#### 5-Year+ LPR History

| Effective Date | Rate | Effective Date | Rate |
|----------------|------|----------------|------|
| 2019-08-20 | 4.85% | 2022-05-20 | 4.45% |
| 2019-11-20 | 4.80% | 2022-08-22 | 4.30% |
| 2020-04-20 | 4.65% | 2023-06-20 | 4.20% |
| 2020-05-20 | 4.65% | 2023-08-21 | 4.20% |
| 2021-12-20 | 4.65% | 2024-02-20 | 3.95% |
| 2022-01-20 | 4.60% | 2024-10-21 | 3.60% |
| 2022-05-15 | 4.45% | (current) | 3.60% |

**Note**: Calculator has these rates embedded; manual lookup not needed for calculations.

### When to Use

- Contracts specifying LPR-based interest
- Overdue interest when no fixed rate specified (default: 1y LPR × 1.5)
- Any floating rate tied to LPR

## Part 4: Delayed Performance Interest

### Formula

```
Delayed Performance Interest = Principal × Daily Rate × Days
```

**Where**:
- Principal = Amount in delayed performance (per judgment)
- Daily Rate = **0.0175%** (万分之1.75) - FIXED, not variable
- Days = From (performance deadline + 1 day) to interest stop date

### Calculator Command

```bash
python universal_debt_calculator_cli.py delay \
  --principal <amount> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD>
```

**Example**:
```bash
python universal_debt_calculator_cli.py delay \
  --principal 120000 \
  --start-date 2025-03-21 \
  --end-date 2025-05-07
```

**Note**: No `--rate` parameter needed (rate is fixed by law).

### Prerequisites (ALL must be met)

1. **MUST be judgment debt**: Only for amounts confirmed by effective legal documents
2. **Performance deadline MUST have expired**:
   - Determine deadline from judgment/mediation
   - Verify expiration occurred before or during bankruptcy
3. **Creditor MUST have declared**: Follow 就无原则 - don't calculate if not declared

### Interest Start Date Determination

**Critical Rule**: Start date = Day AFTER performance deadline expires

**Performance Deadline Determination**:

**Scenario 1: Specific Date Specified**
```
Judgment: "Pay by March 20, 2025"
Deadline: March 20, 2025
Interest starts: March 21, 2025
```

**Scenario 2: Relative Period (First-Instance, No Appeal)**
```
Judgment delivered: March 1, 2025
Period: "Within 15 days of effective date"
Effective date: March 1 + 15 days = March 16, 2025
Deadline: March 16 + 15 days = March 31, 2025
Interest starts: April 1, 2025
```

**Scenario 3: Second-Instance (Affirmation)**
```
First-instance delivered: January 10, 2025
Second-instance judgment: March 1, 2025 (affirms first-instance)
Period: "Within 15 days"
⚠️ CRITICAL: Effective date = March 1, 2025 (second-instance date, NOT first-instance)
Deadline: March 1 + 15 = March 16, 2025
Interest starts: March 17, 2025
```

**Scenario 4: No Deadline Specified**
```
Judgment effective: March 1, 2025
No period specified: Effective date = deadline
Interest starts: March 2, 2025
```

### Principal Base Determination

**⚠️ Common Error**: Using only principal amount

**Correct Approach**: Principal may include:
- Judgment principal amount
- + Judgment interest amount (if included in judgment debt)
- + Judgment penalty amount (if included in judgment debt)
- + Judgment costs (if included in judgment debt, BUT be cautious - see special rule)

**Example**:
```
Judgment debt breakdown:
- Contract principal: 48,000元
- Contract penalty: 2,287元
- Total judgment debt: 50,287元

Delayed performance interest base: 50,287元 (NOT just 48,000元)
```

**Special Rule - Court Fees**:
- Generally do NOT calculate delayed performance interest on court fees
- Court fees have separate deadlines
- Even if expired, be cautious

### When to Use

- ONLY for judgment/mediation/arbitration debts
- ONLY when performance deadline has expired
- ONLY when creditor declared this interest

### Legal Basis

- Supreme Court interpretation on delayed performance interest
- Fixed rate: Daily 0.0175% (万分之1.75)
- Not affected by contract terms

## Part 5: Compound Interest Calculation

### Formula

```
For each compounding cycle:
  Cycle Interest = Current Principal × Annual Rate × (Cycle Days / Base Days)
  New Principal = Current Principal + Cycle Interest

Total Interest = Final Principal - Original Principal
```

### Calculator Command

```bash
python universal_debt_calculator_cli.py compound \
  --principal <amount> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD> \
  --rate <percentage> \
  --cycle <description>
```

**Example**:
```bash
python universal_debt_calculator_cli.py compound \
  --principal 500000 \
  --start-date 2023-01-01 \
  --end-date 2025-05-11 \
  --rate 5.5 \
  --cycle "每月末"
```

### Compounding Cycles

**Common Cycles**:
- `"每月末"` - Monthly (last day of month)
- `"每季度末"` - Quarterly
- `"每年末"` - Annually

**Contract Specification Required**: Cannot infer compound interest from general interest clause.

### Legal Requirement

**⚠️ MUST have explicit contractual basis**

- Contract must specifically provide for compound interest
- Must specify compounding cycle
- Cannot default to compound interest

### When to Use

- Rare in ordinary commercial debts
- Loan contracts explicitly providing compound interest
- Specific compounding terms in contract

## Part 6: Penalty Interest / Penalty Calculation

### Penalty Interest (as Interest Rate)

**Use**: When penalty calculated as percentage rate over time

**Formula**: Same as simple interest or LPR interest
```
Penalty = Principal × Penalty Rate × (Days / Base Days)
```

**Cap Check**: MUST verify against 4× LPR limit

### Penalty Cap Verification Process

**Step 1**: Calculate penalty per contract terms
```bash
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 24.0
```

**Step 2**: Calculate 4× LPR cap
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --multiplier 4.0 \
  --lpr-term 1y  # or 5y based on period
```

**Step 3**: Compare results
```
Contractual penalty: X元
4× LPR cap: Y元
Use: MIN(X, Y)
Then apply 就低原则 vs. declared amount
```

**Example**:
```
Contractual (24% annual): 24,000元
4× LPR cap (3.45% × 4 = 13.8%): 13,800元
Declared: 15,000元
Final confirmation: 13,800元 (4× LPR cap < declared < contractual)
```

### Fixed Amount Penalty

**When**: Contract specifies fixed penalty amount (e.g., "5,000元 penalty")

**Handling**:
- If ≤ declared amount: Confirm fixed amount
- Still check if exceeds 4× LPR calculated amount
- Apply 就低原则

## Part 7: Payment Offset Handling

### When Applicable

Debtor made payments during debt period (after claim arose, before bankruptcy filing).

### Strategy: Segmented Calculation

**Step-by-Step Process**:

1. **Identify payment dates**:
   ```
   Debt period: 2023-01-01 to 2025-05-11
   Payment 1: 2023-06-15 (20,000元)
   Payment 2: 2023-10-20 (15,000元)
   ```

2. **Split into segments**:
   ```
   Segment 1: 2023-01-01 to 2023-06-15
   Segment 2: 2023-06-15 to 2023-10-20
   Segment 3: 2023-10-20 to 2025-05-11
   ```

3. **Calculate each segment separately**:

   **Segment 1** (original principal):
   ```bash
   python universal_debt_calculator_cli.py lpr \
     --principal 100000 \
     --start-date 2023-01-01 \
     --end-date 2023-06-15 \
     --multiplier 1.5 \
     --lpr-term 1y
   ```

4. **Apply offset order**:

   **For General Debts** (Civil Code Article 561):
   ```
   Offset Order:
   1. Costs (实现债权的费用)
   2. Interest
   3. Principal
   ```

   **For Judgment Debts**:
   ```
   Offset Order:
   1. Amounts in legal document (principal, interest, costs per judgment)
   2. Delayed performance interest
   ```

5. **Calculate remaining segments with adjusted principal**:

   Assume Segment 1 interest = 5,000元:
   ```
   Payment 1: 20,000元
   Offset: 5,000元 (interest) + 15,000元 (principal)
   Remaining principal: 100,000 - 15,000 = 85,000元
   ```

   **Segment 2** (adjusted principal):
   ```bash
   python universal_debt_calculator_cli.py lpr \
     --principal 85000 \
     --start-date 2023-06-15 \
     --end-date 2023-10-20 \
     --multiplier 1.5 \
     --lpr-term 1y
   ```

6. **Continue for all segments and sum**:
   ```
   Total Interest = Segment 1 + Segment 2 + Segment 3 - (offset interest portions)
   ```

### Offset Order Application

**General Debt Example**:
```
Outstanding: 100,000 principal + 10,000 interest + 2,000 costs
Payment: 15,000元

Offset:
1. Costs: 2,000元 (fully paid)
2. Interest: 10,000元 (fully paid)
3. Principal: 3,000元 (partial)

Remaining: 97,000 principal + 0 interest + 0 costs
```

**Judgment Debt Example**:
```
Judgment amounts: 100,000 principal + 8,000 interest + 2,000 costs = 110,000
Delayed interest accrued: 3,000元
Payment: 50,000元

Offset:
1. Judgment amounts: 50,000元 (partial, applies to judgment amounts first)
2. Delayed interest: 0元 (not reached)

Remaining judgment: 60,000元
Delayed interest continues to accrue on 60,000元
```

## Part 8: Interest Rate Reference (2024-2025)

| 利率类型 | 当前参考值 | 应用场景 |
|---------|-----------|---------|
| 1年期LPR | 3.00% | 一般商事债权、≤5年债务 |
| 5年期以上LPR | 3.60% | 长期贷款、>5年债务 |
| 法定利率上限 | LPR × 4 | 民间借贷利率保护上限 |
| 迟延履行利率 | 日利率0.0175% | 固定，仅判决债权 |

**Note**: Rates change periodically. Calculator has current rates embedded.

## Part 9: Common Calculation Scenarios

### Scenario 1: Simple Overdue Interest (Fixed Rate)

**Situation**: Contract specifies fixed overdue interest rate

**Formula**: Simple interest
**Calculator Mode**: `simple`
**Parameters**: Principal, dates, contract rate

**Example**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 132216 \
  --start-date 2023-04-16 \
  --end-date 2025-05-11 \
  --rate 24.0
```

### Scenario 2: LPR-Based Overdue Interest

**Situation**: No fixed rate specified, use LPR floating rate

**Formula**: LPR × multiplier (commonly 1.5)
**Calculator Mode**: `lpr`
**Parameters**: Principal, dates, multiplier, LPR term

**Example**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 200000 \
  --start-date 2023-06-01 \
  --end-date 2025-05-11 \
  --multiplier 1.5 \
  --lpr-term 1y
```

### Scenario 3: Long-Term Debt (>5 Years)

**Situation**: Debt period exceeds 5 years, must consider 5-year LPR

**Period Calculation**:
```
Start: 2018-03-01
End: 2025-05-11
Period: ~7.2 years > 5 years
```

**Selection**: Use 5-year+ LPR

**Example**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 1000000 \
  --start-date 2018-03-01 \
  --end-date 2025-05-11 \
  --multiplier 1.0 \
  --lpr-term 5y
```

### Scenario 4: Judgment with Delayed Performance Interest

**Situation**: Judgment effective, performance deadline passed

**Step 1 - Determine deadline**:
```
Mediation date: 2025-02-20 (effective immediately)
Payment deadline: 2025-03-20
Performance expired: 2025-03-20
Interest starts: 2025-03-21
```

**Step 2 - Calculate**:
```bash
python universal_debt_calculator_cli.py delay \
  --principal 120000 \
  --start-date 2025-03-21 \
  --end-date 2025-05-07
```

### Scenario 5: Penalty with Cap Verification

**Situation**: Contract penalty 24%, need to verify against cap

**Step 1 - Contractual**:
```bash
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 24.0
# Result: 24,000元
```

**Step 2 - Cap (4× 1y LPR = ~12%)**:
```bash
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --multiplier 4.0 \
  --lpr-term 1y
# Result: ~12,000元
```

**Step 3 - Compare**:
```
Contractual: 24,000元
Cap: 12,000元
Declared: 15,000元
Confirm: 12,000元 (cap < declared < contractual)
```

## Part 10: Calculation Quality Control

### Pre-Calculation Checks

```
□ Principal amount verified against evidence
□ Start date correct (loan date, overdue date, etc.)
□ End date ≤ bankruptcy filing date - 1 day
□ Rate/multiplier matches contract terms
□ LPR term selected based on period (1y vs 5y)
□ For delayed interest: Prerequisites verified (judgment + expired + declared)
```

### During Calculation

```
□ Using calculator tool (not manual calculation)
□ Command parameters correct
□ Excel/CSV output file generation enabled
□ File naming follows standards
```

### Post-Calculation Checks

```
□ Result seems reasonable (not obviously wrong)
□ Applied 就低原则 (compare with declared amount)
□ For penalties: Verified against 4× LPR cap
□ Calculation process file generated and saved
□ Command documented in report
```

### Common Calculation Errors to Avoid

**Error 1**: End date after bankruptcy filing
- ❌ Wrong: `--end-date 2025-05-13` (if bankruptcy = 2025-05-12)
- ✅ Right: `--end-date 2025-05-11` (bankruptcy - 1 day)

**Error 2**: Wrong LPR term for long debts
- ❌ Wrong: 7-year debt with `--lpr-term 1y`
- ✅ Right: 7-year debt with `--lpr-term 5y` (or documented reason for 1y)

**Error 3**: Manual calculation instead of tool
- ❌ Wrong: Calculating interest by hand
- ✅ Right: ALWAYS use calculator tool

**Error 4**: Missing cap verification for penalties
- ❌ Wrong: Confirming 24% penalty without cap check
- ✅ Right: Calculate both contractual and 4× LPR, use lesser

**Error 5**: Wrong delayed performance base
- ❌ Wrong: Using only principal (48,000) when judgment includes penalty
- ✅ Right: Using total judgment debt (50,287) as base

## Summary

**Calculation Principles**:
1. **ALWAYS use calculator tool** - No exceptions
2. **Verify dates first** - Bankruptcy date is critical
3. **Select correct mode** - Five modes for five calculation types
4. **Check LPR term** - 1y vs 5y based on debt period
5. **Verify caps** - Penalties cannot exceed 4× LPR
6. **Document process** - Generate Excel/CSV files
7. **Apply 就低原则** - Final amount ≤ declared amount

**Calculator Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**For detailed calculator usage**: See `debt-claim-analysis` skill reference guides
**For legal basis**: See `legal_standards_reference.md`
**For terminology**: See `common_terms_glossary.md`
