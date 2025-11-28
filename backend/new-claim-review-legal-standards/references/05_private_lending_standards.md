# Private Lending Claims Review Standards
# 民间借贷债权审查标准

## Purpose

This reference provides comprehensive standards for reviewing private lending claims, focusing on the strict interest rate caps, prohibited practices (advance deduction, disguised interest), and application of the Private Lending Judicial Interpretation in bankruptcy context.

## Part 1: Scope and Definition / 适用范围

### 1.1 What is Private Lending

**Private Lending Judicial Interpretation (民间借贷司法解释)** defines private lending as:
> Financing activities between natural persons, legal persons, and unincorporated organizations, **excluding financial institutions as lenders**

**Key Characteristic**: Lender is **not a licensed financial institution**

### 1.2 Entities Covered

**Lenders**:
- Natural persons (individuals)
- Companies (non-financial)
- Partnerships, sole proprietorships
- Other organizations

**Borrowers**: Any natural person or organization

### 1.3 Exclusions - NOT Private Lending

**Excluded** (Do NOT apply Private Lending Interpretation):
1. **Financial institutions as lenders** (banks, licensed financial companies) → Use financial institution rules (`04_financial_institution_standards.md`)
2. **Commercial sales/services with payment terms** → Trade credit, not lending
3. **Bonds, debentures** → Securities law applies

**Special Case - Entrusted Loans**:
- Company A lends to Company B **through bank as intermediary** (bank handles disbursement and collection but is not lender)
- This **IS** private lending (lender is Company A, not bank)
- Applies Private Lending Interpretation

---

## Part 2: Documentation Review / 证据材料审查

### 2.1 Required Evidence

**Creditor (lender) must provide**:
1. **Loan Agreement or Contract**
2. **Loan Vouchers** (借据, IOUs, receipts, notes)
3. **Disbursement Proof**: Bank transfer records, payment receipts
4. **Guarantee Contracts** (if secured)
5. **Other evidence** of lending relationship

### 2.2 Critical Review: Actual Disbursement

**Principle**: Contract alone is insufficient; must prove **actual loan disbursement**

**Administrator Duty**: Verify through:
- Bank transfer records (most reliable)
- Cash receipts (if credible, with supporting evidence)
- Borrower's acknowledgment in writing

**Common Issue**: Contract signed but money never actually lent → No debt

**Burden**: Creditor must prove disbursement; if cannot prove, do not confirm principal

---

## Part 3: Calculation Base - Advance Deduction Prohibition / 计息基数 - 砍头息禁止

### 3.1 Advance Deduction ("Cutting Head Interest" / 砍头息)

**Definition**: Interest is deducted from principal **before** disbursement

**Private Lending Interpretation Rule**: Interest may not be deducted in advance from principal. If deducted, **actual disbursed amount** is the principal for all purposes (repayment and interest calculation).

### 3.2 Identification of Advance Deduction

**典型情形**:

**(1) Direct Deduction from Transfer**:
- Contract states: Loan 100,000 yuan at 10% annual interest
- But bank transfer shows only 90,000 yuan to borrower
- 10,000 deducted upfront
- **Result**: Principal is **90,000** (actual disbursed), not 100,000

**(2) Same-Day Reverse Payment**:
- Loan contract: 100,000 yuan
- Day 1: Lender transfers 100,000 to borrower
- **Same day**: Borrower transfers 10,000 back to lender (or lender's designee)
- **Result**: This is advance deduction; principal is **90,000**

**(3) Payment to Lender's Designee on Disbursement Day**:
- Lender transfers 100,000 to borrower
- Same day: Borrower pays 10,000 to person/company designated by lender
- **Result**: Advance deduction; principal is **90,000**

### 3.3 Administrator Actions

**When Advance Deduction Suspected**:
1. **Review bank records** for disbursement date and any same-day reverse transfers
2. **Inquiry**: Ask both creditor and debtor about any same-day payments
3. **Determine actual principal**: Amount actually received and kept by borrower
4. **Calculate interest on actual principal**: Not the nominal contract principal

**Example Calculation**:
- Contract principal: 200,000 yuan
- Advance deduction: 20,000 yuan
- Actual principal: 180,000 yuan
- Agreed rate: 12% annual
- Interest calculation base: **180,000**, not 200,000
- Creditor can claim: 180,000 principal + interest on 180,000

---

## Part 4: Disguised Interest / 变相利息

### 4.1 Common Forms

Lenders may charge fees under various names:
- **Service fees** (服务费)
- **Consulting fees** (咨询费)
- **Advisory fees** (顾问费)
- **Management fees** (管理费)
- **Handling fees** (手续费)
- **Investigation fees** (调查费)

### 4.2 Identification Standard

**If fees are**:
- Collected by lender or lender's designee, AND
- Not supported by actual services rendered, OR
- Unreasonably high relative to any actual services

→ **Treat as disguised interest**

### 4.3 Administrator Review Process

**Burden**: Creditor (lender) must prove fees are legitimate and supported by actual services

**Steps**:
1. **Request evidence**: Service contracts, invoices, description of services provided
2. **Assess**: Were services actually performed? Is fee amount reasonable?
3. **Inquire with debtor's personnel**: Did they receive such services?
4. **Determine**:
   - **If legitimate**: Treat as separate fee (ordinary claim unless secured)
   - **If not legitimate**: **Add to interest** amount; check total against rate caps

**Treatment Options**:
- **As advance deduction** (if collected upfront): Reduce principal by fee amount
- **As disguised interest** (if collected during term): Add to interest; count against rate caps

### 4.4 Example

- Loan: 500,000 yuan, 1-year, 15% annual interest
- "Consulting fee": 50,000 yuan to lender's affiliate
- No evidence of consulting services
- **Determination**: 50,000 is disguised interest
- Effective interest: 75,000 (15% interest) + 50,000 (disguised) = 125,000
- Effective rate: 125,000 / 500,000 = 25%
- **Comparison with cap**: Post-2020-08-20, if LPR 1-year × 4 = 15.4%, then 25% exceeds cap
- **Action**: Reduce total interest to 77,000 (15.4% of 500,000)

---

## Part 5: Interest Agreement / 对利息的约定

### 5.1 No Agreement on Interest

**Scenario**: Lending agreement does not mention interest at all

**Rule**:
- **If lender claims interest**: Do **not** confirm interest
- **Borrower only owes principal**

**Exception**: Does not apply to professional/commercial lending (those are presumed interest-bearing)

### 5.2 Agreement Unclear on Interest

**Scenario**: Agreement mentions "interest" or "pay interest" but does not specify rate or calculation method

#### (1) Between Natural Persons

**Rule**: If both lender and borrower are **natural persons** (individuals), unclear agreement = no interest

**Lender claims interest**: Do **not** confirm

#### (2) Other Parties (Not Both Natural Persons)

**Rule**: If lender or borrower is legal person/organization, unclear agreement = **interest per applicable bank lending rate**

**Calculation**: Use bank peer lending rate (pre-2019-08-20) or LPR (post-2019-08-20), segmented by period

### 5.3 "Return Principal Plus Interest Upon Maturity" (到期还本付息)

**Common Contract Language**: "Borrower shall return principal plus interest upon maturity"

**Judicial Interpretation**: This is **unclear agreement** on interest rate

**Treatment**: Per 5.2 above:
- Both natural persons: No interest
- Otherwise: Interest at applicable benchmark/LPR rate

### 5.4 Agreed Interest Rate

**If contract specifies rate** (e.g., "10% annual interest"): Calculate per agreed rate, **subject to caps** (Part 6 below)

---

## Part 6: Interest Rate Caps / 利率上限

This is the **most critical** part of private lending review.

### 6.1 Historical Evolution of Rate Caps

#### Pre-2020-08-20 (Old Rule)

**Private Lending Interpretation (2015 version)**:

**24% Annual Cap** (judicial protection line):
- Interest agreed or calculated ≤ 24% annual: Fully confirmed
- Interest 24%-36% annual: If already paid by borrower, not recovered; if not paid, not confirmed
- Interest > 36% annual: Not confirmed; if already paid, recovered (returned to borrower/estate)

**Application**:
- For agreements made before 2020-08-20
- Interest accrued before 2020-08-20 calculated per above caps

#### Post-2020-08-20 (New Rule)

**Private Lending Interpretation (2020 amendment)**:

**LPR × 4 Cap** (judicial protection line):
- Rate cap = **1-year LPR × 4** (四倍一年期LPR)
- LPR published monthly; use **the LPR applicable on contract formation date** (or litigation filing date per Supreme Court clarification)
- Interest exceeding this cap: Not confirmed

**Example** (assume LPR 1-year = 3.85%):
- Cap = 3.85% × 4 = 15.4% annual
- Agreed rate 18%: Confirm only up to 15.4%
- Excess 2.6%: Do not confirm

### 6.2 Segmented Calculation for Cross-Period Loans

**Scenario**: Loan made before 2020-08-20, extends beyond that date

**Principle**: Apply **different caps to different time periods**

**Method**:

**(1) Calculate Interest for Period Before 2020-08-20**:
- Use **24% annual cap**
- Formula: Principal × Days (through 2020-08-19) × min(Agreed Rate, 24%) / 360

**(2) Calculate Interest for Period From 2020-08-20 Onward**:
- Use **LPR × 4 cap** applicable on relevant date (contract date, or litigation date per courts)
- Formula: Principal × Days (from 2020-08-20) × min(Agreed Rate, LPR×4) / 360

**(3) Sum Both Periods**

**Critical**: Interest within each period is capped separately; cannot average across periods

### 6.3 Determining Applicable LPR for Cap

**Question**: Which LPR to use for the cap? (LPR changes monthly)

**Supreme Court Guidance** (2021 amendment understanding):
- **Primary Rule**: LPR on **contract formation date**
- **Litigation Context**: If litigated before bankruptcy, may use LPR on **litigation filing date** per court's determination
- **Bankruptcy Context**: Administrator may use:
  - LPR on contract date, OR
  - LPR on bankruptcy filing date (more conservative), OR
  - Follow litigation judgment if case was litigated

**Practical Approach**: Use LPR on contract date; if unclear, use LPR around bankruptcy filing date (ensures not over-confirming)

### 6.4 Comprehensive Cap Rule

**Critical Rule**: Regardless of how interest is calculated (standard interest, overdue interest, penalty, etc.) or what names are used, **the sum of all interest-nature payments must not exceed the cap**

**Formula**:
```
Total Confirmed Interest ≤ Principal × LPR×4 (or 24% for pre-2020-08-20 period) × Years
```

**Application**:
- Regular interest + overdue interest + penalty + fees = Must not exceed cap
- If total exceeds: Reduce to cap amount
- Allocate reduced amount among different interest types per contract priority or proportionally

### 6.5 Cap Application to Multiple Payment Names

**Common Scenario**: Contract specifies:
- Regular interest: 15%
- Overdue interest: 20%
- Penalty (liquidated damages): 10% of overdue amount

**Review**:
1. Calculate each item per contract
2. Sum all items
3. Compare sum with cap
4. If sum exceeds cap: Confirm only up to cap

**Example**:
- Principal: 100,000, term: 2 years, all overdue
- Regular interest: 15% × 2 × 100,000 = 30,000
- Overdue interest: 20% × 2 × 100,000 = 40,000
- Penalty: 10% × 100,000 = 10,000
- Total claimed: 30,000 + 40,000 + 10,000 = 80,000 (80% over 2 years = 40% annual)
- Cap (assume LPR×4 = 15.4%): 15.4% × 2 × 100,000 = 30,800
- **Confirm**: 30,800 only (not 80,000)

---

## Part 7: Overdue Interest and Penalties / 逾期利息与违约金

### 7.1 Overdue Interest When Agreed

**Rule**: If contract specifies overdue interest rate, calculate per contract, **subject to caps**

**Common Language**: "If payment overdue, bear overdue interest at [X]% annual rate"

**Calculation**:
- Base: Overdue principal
- Rate: Contract overdue rate (but not exceeding cap)
- Period: From overdue date to bankruptcy filing date -1

### 7.2 Overdue Interest When Not Agreed But Loan Rate Agreed

**Rule**: If contract agreed loan rate but did not specify separate overdue rate:

**Lender claims overdue interest**: Calculate at **loan contract rate**

**Legal Basis**: Borrower's obligation to pay interest per contract continues into overdue period

### 7.3 No Loan Rate, No Overdue Rate

**Rule**: If neither loan rate nor overdue rate agreed:

**Per Part 5**:
- Both natural persons: No interest (including overdue)
- Otherwise: Calculate at applicable benchmark/LPR rate

### 7.4 Penalties / Liquidated Damages

**Contractual Penalties**: Many contracts include penalty clause (违约金) for breach

**Private Lending Context**: Penalties for late payment **count toward interest cap**

**Rule**: Creditor may claim:
- Overdue interest, OR
- Penalty (liquidated damages), OR
- Both combined

**But**: Total (interest + penalty + fees) **cannot exceed rate cap**

**Administrator Application**:
- Calculate per creditor's claim
- Sum all amounts
- Cap at LPR×4 (or 24% for applicable period)

---

## Part 8: Repayment Allocation and Capitalization / 还款分配与结算

### 8.1 Capitalization of Interest (结息)

**"Capitalization" (结息/结算)**: Practice where accrued interest is added to principal, creating new principal amount for subsequent interest calculation

**Example**:
- Original loan: 100,000 at 10%
- After 1 year: Principal 100,000 + Interest 10,000 = 110,000
- Parties "settle": New IOU issued for 110,000 as "principal"
- Subsequently interest calculated on 110,000

**Legal Rule**: This form of **capitalization is prohibited** from creating amounts exceeding the cap

**Private Lending Interpretation**: "Regardless of how parties settle or re-document, total principal + interest at any time cannot exceed: Initial Principal × Cap Rate × Elapsed Time"

**Application**:
- Even if parties re-document 110,000 as principal
- Interest can only be calculated per cap on **original initial principal** (100,000)
- The "capitalized" 10,000 cannot generate additional interest beyond the cap

**Administrator Review**:
- Identify if capitalization occurred (successive IOUs with increasing principal)
- Calculate maximum allowable total debt: Initial Principal × LPR×4 × Years
- Confirm only up to maximum allowable amount

### 8.2 Partial Payment Allocation

**Per Civil Code Article 561**: Costs → Interest → Principal

**Effect**: Partial payment reduces future interest calculation base

**Example**:
- Loan: 200,000 at 10%
- After 1 year, debtor pays 30,000
- Accrued interest: 20,000
- Allocation: 20,000 to interest (fully paid), 10,000 to principal
- New principal: 190,000
- Year 2 interest calculated on 190,000

---

## Part 9: Special Scenarios / 特殊情形

### 9.1 Partial Payment After Rate Cap Breach

**Scenario**:
- Agreed rate 30% (exceeds cap of 15%)
- Debtor has been paying per 30% for years
- Bankruptcy filed

**Review**:
- Payments made within 24% (old rule) or LPR×4 (new rule): Valid payments, not recoverable
- Payments made exceeding cap: May be subject to recovery/offset against debt

**Practical Application**: Usually do not pursue recovery of excess payments; simply confirm remaining debt per capped rate

### 9.2 Mixed Lending and Investment

**Scenario**: Contract labeled "investment agreement" but substance is lending (fixed return, repayment obligation)

**"Substance Over Form" Principle**: Review economic substance; if substance is lending, apply lending rules and caps

**Administrator Action**:
- Analyze contract terms
- If borrower must repay fixed amount regardless of project outcome: Lending
- Apply private lending caps

### 9.3 Intra-Group Lending

**Scenario**: Lending between parent company and subsidiary, or between sister companies

**Treatment**: Still private lending (unless through licensed finance company)

**Rate Caps Apply**: Even if related parties, interest must not exceed caps

**Special Consideration**: Verify if lending complied with corporate resolutions and related-party transaction rules

---

## Part 10: Administrator's Review Checklist for Private Lending

```
□ Verified lender is NOT licensed financial institution?
□ Verified actual loan disbursement (bank records, receipts)?
□ Checked for advance deduction (same-day reverse payments)?
□ Checked for disguised interest (service fees, etc.)?
□ Determined if interest agreed (rate specified or unclear)?
□ Applied correct rate cap (24% pre-2020-08-20; LPR×4 post)?
□ Performed segmented calculation if loan crosses 2020-08-20?
□ Checked total interest + penalty + fees against cap?
□ Identified any capitalization/re-documentation of interest?
□ Calculated maximum allowable debt per cap on initial principal?
□ Accounted for partial payments (segmented calculation)?
□ Confirmed only amounts within legal caps?
```

---

## Summary / 总结

Private lending claims are subject to **strict interest rate caps** and **prohibited practices**:

**Key Rules**:
1. **Lender Identification**: Must not be licensed financial institution
2. **Advance Deduction Prohibited**: Actual disbursed amount is principal
3. **Disguised Interest**: Service fees without actual services = interest
4. **Interest Agreement**:
   - No agreement: No interest
   - Unclear agreement: Bank rate (unless both natural persons)
5. **Rate Caps**:
   - Pre-2020-08-20: 24% annual
   - Post-2020-08-20: LPR 1-year × 4
   - Segmented calculation for cross-period loans
6. **Comprehensive Cap**: Interest + penalty + fees total cannot exceed cap
7. **Capitalization Limit**: Cannot create excess debt through re-documentation

**Common Errors to Avoid**:
- ❌ Confirming interest exceeding caps
- ❌ Using nominal principal when advance deduction occurred
- ❌ Ignoring disguised interest (fees)
- ❌ Failing to apply segmented calculation for cross-2020-08-20 loans
- ❌ Allowing capitalized interest to exceed cap on original principal

**Cross-References**:
- Interest calculation methods: `03_interest_calculation_standards.md`
- Financial institution comparison: `04_financial_institution_standards.md`
- Secured private lending: `06_secured_claims_standards.md`
