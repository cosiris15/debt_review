# Interest Calculation Standards
# 利息计算详细标准

## Purpose

This reference provides comprehensive standards for interest calculation in bankruptcy claims, including calculation principles, methods, base determination, period determination, and rate application. Interest calculation is one of the most technically complex areas in debt review.

## Part 1: Interest Review Principles / 利息审查原则

### Principle 1: No Proactive Calculation (不主动计算)

**Rule**: Administrator **does not proactively calculate interest** for creditors who did not declare interest.

**Reasoning**: Whether to claim interest is creditor's choice; administrator's duty is review, not advocacy.

### Principle 2: Require Explicit Amount (要求明确金额)

**Rule**: If creditor declares interest but does not provide explicit amount, administrator shall:
1. Request creditor provide interest amount + calculation method + calculation process
2. Explain: Providing explicit amount = deemed declaration of interest; refusing to provide = deemed non-declaration

**Result**:
- Creditor provides amount → Proceed to review
- Creditor refuses → Treat as no interest declared

### Principle 3: Take Lower Amount (就低原则)

**Rule**: Compare administrator's calculated amount with creditor's declared amount; confirm **the lower amount**.

**Application**: This "take lower" principle applies to **same-nature interest as a whole** (e.g., total of interest + penalty + other fees of same nature), not item-by-item comparison.

**Example**:
- Creditor declares: Overdue interest 50,000 + penalty 30,000 = Total 80,000
- Administrator calculates: Overdue interest 45,000 + penalty 35,000 = Total 80,000
- Result: Both total to 80,000 → Confirm 80,000 (not 45,000 + 30,000 = 75,000)

**Special Note**: Delayed performance double-portion interest is **separately compared** (not mixed with other interest types)

### Principle 4: Payment Allocation (清偿顺序)

**Civil Code Article 561**: Insufficient payment allocated per:
1. **Costs** for realizing claim
2. **Interest**
3. **Principal**

**Application**: For partial payments by debtor:
- If agreed/specified: Per agreement
- If not agreed: Deduct per above order
- **Do not preferentially deduct delayed performance double-portion interest**

**Effect on Calculation**: Partial payment reduces principal → affects interest calculation base for subsequent periods

---

## Part 2: Interest Calculation Method / 利息计算方法

### 2.1 General Formula

```
Interest = Principal (Base) × Days (Period) × Daily Rate
```

Where:
- **Principal**: Calculation base (see Part 3)
- **Days**: Calculation period (see Part 4)
- **Daily Rate**: Annual rate ÷ 360 (or 365, see below)

### 2.2 Annual Rate to Daily Rate Conversion

#### Method 1: 360-Day Year (Recommended)

```
Daily Rate = Annual Rate / 360
```

**Example**:
- Annual rate: 4.35%
- Daily rate: 4.35% / 360 = 0.01208%

**Rationale**: Banking practice standard; simplifies calculation

#### Method 2: 365-Day Year (Also Acceptable)

```
Daily Rate = Annual Rate / 365
```

**Example**:
- Annual rate: 4.35%
- Daily rate: 4.35% / 365 = 0.01192%

**Administrator Stance**:
- If creditor calculates per 365-day year: Accept
- If creditor calculates per 360-day year: Accept
- **Unless contract/judgment specifies, do not impose one method over the other**

**Comparison Rule**: If creditor uses 365-day calculation, administrator may use 360-day for comparison; confirm the lower result.

### 2.3 Alternative Calculation Method

**Formula**:
```
Interest = Years × Annual Rate × Principal + Remaining Days × Daily Rate × Principal
```

**Example**:
- Principal: 100,000
- Period: 2 years 50 days
- Annual rate: 5%
- Interest = 2 × 5% × 100,000 + 50 × (5%/360) × 100,000
- Interest = 10,000 + 694.44 = 10,694.44

**Administrator Stance**: Accept this method; also reasonable and commonly used

### 2.4 Multiple Calculation Periods (Segmented Calculation)

**Situation**: Interest base changes due to partial payment during period

**Method**: Calculate in segments with different bases

**Example**:
- Initial principal: 500,000
- Period 1: 2020-01-01 to 2021-06-30 (545 days)
- Payment on 2021-07-01: 100,000
- Period 2: 2021-07-01 to 2024-05-08 (remaining period)
- Rate: 5% annual

**Calculation**:
- Period 1 interest: 500,000 × 545 × (5%/360) = 37,847.22
- Period 2 interest: 400,000 × [days] × (5%/360) = [amount]
- Total interest: Period 1 + Period 2

**Critical**: Payment date is both:
- End date for previous segment (calculate to day before payment)
- Start date for next segment (with reduced base)

---

## Part 3: Calculation Base Determination / 计息基数确定

### 3.1 General Rule

**Calculation base = Principal**

**"Principal" defined**:
- Loan contracts: Loan principal amount
- Sales contracts: Unpaid purchase price
- Service contracts: Unpaid service fees
- Lease contracts: Unpaid rent
- Judgment debts: Principal amount per judgment

### 3.2 Partial Payment Effect

**Rule**: Partial payment reduces principal → reduces calculation base for subsequent period

**Method**: Segmented calculation (see 2.4 above)

**Payment Allocation**:
- Per agreement: Follow agreement
- No agreement: Allocate per Civil Code Article 561 (costs → interest → principal)
- If payment made after some interest accrued: Typically allocated to interest first, then principal

**Example**:
- Principal: 1,000,000
- Interest accrued through 2021-12-31: 50,000
- Payment on 2022-01-01: 80,000
- Allocation: 50,000 to interest (fully paid) + 30,000 to principal
- New principal for Period 2: 1,000,000 - 30,000 = 970,000

### 3.3 Compound Base (Capitalized Interest)

**Question**: Can accrued interest be added to principal for calculating subsequent interest (compound interest)?

**General Rule**: **NO**, unless explicitly agreed in contract or specified in judgment

**Contract Law** (pre-Civil Code) Article 205: Interest cannot be compounded unless agreed

**Civil Code**: Maintains this rule (no default compounding)

**Exception**: If contract explicitly states "unpaid interest shall be added to principal for compounding" → Follow contract

**Bank Practice**: Loan contracts often include compound interest clauses; review contract language carefully

---

## Part 4: Calculation Period Determination / 计息期间确定

### 4.1 Determine Start Date (起息日)

**General Rule**: Per contract agreement or law

**Common Scenarios**:

**(1) Contract Specifies Start Date**:
- "Interest accrues from actual disbursement date"
- "Interest accrues from payment due date"
- Follow contract specification

**(2) Loan Contract Without Specification**:
- Starts from actual loan disbursement date

**(3) Overdue Interest** (逾期利息):
- Starts from day after payment deadline expires
- Example: Deadline 2020-12-31 → Start 2021-01-01

**(4) Judgment Interest**:
- Typically starts from: Date specified in judgment
- Or: Date when judgment performance period expires

### 4.2 Determine End Date (止息日)

**Bankruptcy Context Rule**: **Day before bankruptcy filing date**

**Legal Basis**: Bankruptcy Law Article 46 - "Interest stops accruing from bankruptcy filing date"

**Example**:
- Bankruptcy filing date: 2024-05-09
- Interest calculates to: 2024-05-08

**Exception**: Secured claims may receive interest from secured property proceeds (if sufficient value remains after principal)

### 4.3 Day Count Calculation

```
Days = End Date - Start Date + 1
```

**Inclusive Counting**: Include start date, include end date

**Example**:
- Start: 2020-01-01
- End: 2020-01-10
- Days: 10 days (1st through 10th)

### 4.4 Partial Payment Effect on Period

**Rule**: Partial payment creates new period with new base (see 2.4 and 3.2)

**Payment Date Treatment**:
- **Previous period ends**: Day before payment date (calculate interest through day before)
- **New period starts**: Payment date (with reduced base, calculate from this day)

**Rationale**: Payment takes effect on payment date, so interest should be calculated on reduced base starting that day

---

## Part 5: Interest Rate Determination / 计息利率确定

### 5.1 Hierarchy of Rate Sources

**Priority Order**:
1. **Contract agreement** (if present and legal)
2. **Judgment determination** (for litigation-based claims)
3. **Legal/regulatory specification** (e.g., delayed performance interest)
4. **Applicable default rule** (e.g., LPR for loans without agreed rate)

### 5.2 Contracted Rate

**Rule**: If contract specifies rate, calculate per contract

**Validity Check**:
- Private lending: Must not exceed legal cap (see Part 6 below)
- Financial institution loans: Generally enforceable as agreed
- Sales/service contracts: Overdue interest/penalty must not exceed caps

**Administrator Duty**: If contract specifies rate, use it unless:
- Exceeds legal cap (then reduce to cap)
- Judgment has determined different rate (then use judgment rate)

### 5.3 Applicable Benchmark Rate (Bank Peer Loan Rate / LPR)

**Situation**: Contract does not specify rate, but creditor declares interest

**Rule**: Calculate per "bank peer loan rate" or "LPR" (Loan Prime Rate) applicable during the period

#### Historical Rate System in China

**Pre-2019-08-20**: People's Bank of China (PBOC) Benchmark Lending Rate
- 6-month: Different rate
- 1-year: Different rate
- 1-5 years: Different rate
- 5+ years: Different rate

**2019-08-20 onward**: LPR (Loan Prime Rate) system
- 1-year LPR
- 5-year+ LPR
- Published monthly by National Interbank Funding Center

**Segmented Application**:
- For interest period spanning 2019-08-20: Apply benchmark rate before 08-20; apply LPR after 08-20

### 5.4 LPR Term Selection

**Question**: For a 10-year loan, use 1-year LPR or 5-year+ LPR?

**Rule**: **Depends on original loan term**

- Original term ≤ 5 years: Use 1-year LPR
- Original term > 5 years: Use 5-year+ LPR

**Rationale**: Match LPR term to original financing term, not remaining term

**If Unclear**: Default to 1-year LPR (more common, more conservative)

### 5.5 Segmented Rate Application

**Principle**: Interest rate may change during calculation period; apply segmented rates for accuracy

**Method**:
1. Divide calculation period by rate change dates
2. Apply each applicable rate to its respective sub-period
3. Sum all sub-period interest amounts

**Example**:
- Principal: 500,000
- Period: 2018-01-01 to 2024-05-08
- Before 2019-08-20: PBOC 1-year rate 4.35%
- After 2019-08-20: LPR 1-year (assume 3.85% average)

**Calculation**:
- Period 1 (2018-01-01 to 2019-08-19): 500,000 × 566 days × 4.35% / 360
- Period 2 (2019-08-20 to 2024-05-08): 500,000 × [days] × 3.85% / 360
- Total interest: Period 1 + Period 2

---

## Part 6: Rate Caps and Limitations / 利率上限

### 6.1 Private Lending Rate Cap

See `05_private_lending_standards.md` for comprehensive treatment. Key points:

**Pre-2020-08-20**: 24% annual cap for confirmed claims (36% absolute cap)

**Post-2020-08-20**: LPR 1-year × 4 cap

**Segmented Claims**: Apply different caps to different time periods

### 6.2 Financial Institution Claims

See `04_financial_institution_standards.md`. Key point:

**Supreme Court Guidance**: Total of interest + compound interest + penalty + fees should not significantly exceed 24% annually (even post-2020 reform)

**Exception**: If effective judgment already confirms higher rate, no need to reduce

### 6.3 Non-Lending Contract Overdue Interest

**Sales, Services, Lease, etc.**: Overdue interest + penalty + fees must comply with caps

**Civil Code Article 646**: For paid contracts without legal basis, may refer to sales contract rules → Overdue payment penalty per LPR 1-year × 1.3

**Administrator Discretion**: If creditor does not actively claim per above standard, administrator is not required to proactively calculate

---

## Part 7: Compound Interest and Penalty Interest / 复利与罚息

### 7.1 Compound Interest (复利)

#### Definition

**Compound Interest**: Interest calculated on unpaid interest (interest on interest)

#### Legality

**General Rule**: **Not permitted unless agreed**

**Exception**: Express contractual agreement

#### Financial Institution Special Rules

See `04_financial_institution_standards.md`:
- Financial institutions may compound interest per People's Bank regulations
- Two types: (1) During loan term - on unpaid interest at loan rate; (2) After overdue/misappropriation - on unpaid interest at penalty rate

#### Private Lending

**Not Permitted**: Compound interest on compound interest

**Original Compound Clause**: If contract agreed compound interest, the first-level compounding may be honored; but compounding of that compound interest is not

### 7.2 Penalty Interest (罚息)

#### Financial Institution Penalty Interest

**Legal Basis**: PBOC "RMB Interest Rate Management Rules" and related notices

**Two Types**:

**(1) Overdue Penalty**:
- Scenario: Borrower fails to repay principal by due date
- Base: Unpaid principal
- Rate: Loan rate × 1.3 to 1.5 (30%-50% markup)

**(2) Misappropriation Penalty**:
- Scenario: Borrower uses loan for unauthorized purposes
- Base: Loan principal
- Rate: Loan rate × 1.5 to 1.8 (50%-80% markup)

**Cannot Stack**: If both overdue and misappropriation, apply higher penalty only (misappropriation), not both

#### Private Lending Penalty Interest

**Civil Code Article 646 Application**:
- For paid contracts lacking legal basis, may refer to sales contract rules
- Overdue payment penalty: Per LPR 1-year × 1.3

**Administrator Stance**: Does not proactively calculate; if creditor claims, may calculate per above standard

---

## Part 8: Special Calculation Situations / 特殊计算情形

### 8.1 Interest-Only Payment Claims

**Situation**: Creditor only claims interest, not principal (perhaps principal already paid or settled)

**Calculation**: Calculate per methods above, with claimed interest amount as the debt

**Base for Delayed Performance**: If judgment determines interest debt, the interest amount itself becomes the base for delayed performance interest

### 8.2 Multiple Interest Types Simultaneously

**Situation**: Contract specifies multiple interest types (e.g., normal interest + overdue interest + penalty)

**Administrator Review**:
1. Calculate each type per its own rules
2. Sum all types
3. Check total against legal cap (especially for private lending)
4. If total exceeds cap: Reduce proportionally or per contract priority

### 8.3 Interest on Interest Prohibition Except Where Agreed

**Civil Code**: Interest on unpaid interest is not permitted unless:
- Contract explicitly agrees to compounding, OR
- Creditor demands payment and debtor agrees to add unpaid interest to principal, OR
- Effective legal instrument determines compounding

**Default Rule**: Simple interest only

---

## Part 9: Documentation Requirements / 计算文件要求

### 9.1 Calculation Process Documentation

**Mandatory Requirement**: All interest calculations must be documented with:
1. Calculation base (principal amount)
2. Calculation period (start date, end date, days)
3. Interest rate used (and legal basis)
4. Formula and arithmetic
5. Segmented calculations (if applicable)

**Tool Requirement**: Use `universal_debt_calculator_cli.py` for all calculations (per system requirements)

**Output Format**: Generate Excel or CSV showing calculation process

### 9.2 Rate Change Documentation

**For Segmented Rate Calculations**:
- List each period with its applicable rate
- Cite source for each rate (e.g., "PBOC benchmark 1-year rate effective 2018-01-01: 4.35%")
- Show sub-calculation for each period
- Sum total interest

**LPR Documentation**:
- Cite specific month's LPR (e.g., "LPR 1-year for June 2024: 3.70%")
- Source: National Interbank Funding Center published rates

---

## Part 10: Administrator's Practical Checklist / 管理人实务核查清单

For each interest calculation review:

```
□ Has creditor explicitly declared interest?
□ Has creditor provided calculation amount, method, and process?
□ Is the calculation base correct (principal)?
□ Has partial payment been accounted for (segmented calculation)?
□ Is the start date correct per contract/judgment/law?
□ Is the end date correct (day before bankruptcy filing)?
□ Is the day count correct (inclusive)?
□ Is the interest rate correct and legally compliant?
□ Have rate changes been applied (segmented rates)?
□ Does total interest + penalty + fees exceed legal cap?
□ Is compound interest applied only if agreed?
□ Has calculation been performed using universal debt calculator tool?
□ Has calculation process been documented in Excel/CSV?
□ Has comparison been made with creditor's declared amount?
□ Has lower amount been selected for confirmation?
```

---

## Summary / 总结

Interest calculation is technically demanding but follows systematic principles:

**Core Principles**:
1. No proactive calculation
2. Require explicit amounts
3. Take lower amount (administrator vs. creditor)
4. Payment allocation per Civil Code Article 561

**Calculation Method**:
- Formula: Base × Days × Daily Rate
- Daily rate: Annual / 360 (or 365)
- Segmented calculation for partial payments or rate changes

**Critical Determinations**:
- **Base**: Principal (reduced by partial payments)
- **Period**: Start date (per contract/judgment) to day before bankruptcy filing
- **Rate**: Contract > judgment > legal specification > applicable benchmark/LPR

**Special Rules**:
- Compound interest: Not permitted unless agreed
- Penalty interest: Per PBOC rules (financial) or Civil Code 646 (private)
- Rate caps: Private lending has strict caps; financial institutions subject to reasonableness review

**Must Use**: `universal_debt_calculator_cli.py` tool for all calculations; document process in Excel/CSV

**Cross-References**:
- Private lending rate caps: `05_private_lending_standards.md`
- Financial institution rules: `04_financial_institution_standards.md`
- Delayed performance interest: `02_litigation_claims_standards.md`
- Calculator tool usage: `debt-claim-analysis` Skill
