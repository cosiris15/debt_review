# Other Matters Review Standards
# 其他事项审查标准

## Purpose

Comprehensive standards for miscellaneous but important issues: individual repayment, invalid repayment, set-off rights, retrieval rights, taxes and social insurance, pending contracts, VAT invoicing.

---

## Part 1: Individual Repayment and Invalid Repayment / 个别清偿与无效清偿

### 1.1 Individual Repayment (个别清偿)

**Definition**: Debtor repays **individual creditors** in preference to others during **critical period**

**Critical Period**: **6 months before bankruptcy filing**

**Legal Basis**: Bankruptcy Law Article 32

**Effect**: May be **voidable** (administrator can avoid and recover payment)

### 1.2 Voidability Conditions

**Bankruptcy Law Article 32**: Within 6 months before bankruptcy filing, if debtor:
- Is **already insolvent**, AND
- Makes **individual repayment** to certain creditors

→ Administrator **may void** the repayment

**Exception (Article 32 exceptions)**:
- Debtor's normal business operations payments
- Debt secured by property (secured creditor payments)
- Within 1-month period of debt maturity

### 1.3 Detailed Exceptions (Bankruptcy Interpretation II Articles 14-16)

**Cannot be Voided** (safe individual repayments):

**(1) Payments for Debtor's Continued Business** (Article 14):
- Payments necessary for maintaining normal operations
- Examples: Employee wages (to retain staff), critical supplier payments (to maintain supply), utility bills

**(2) Payments of Debts Due Within 1 Month** (Article 14):
- If debt matured within 1 month before payment made
- Example: Debt due Nov 1; paid Nov 15; bankruptcy filed Jan 15 (within 6 months) → Not voidable (debt was due <1 month before payment)

**(3) New Consideration Payments** (Article 15):
- Debtor pays and **simultaneously receives equivalent new value**
- Example: Pay 100,000 for new inventory worth 100,000 → Not voidable

**(4) Secured Debt Payments** (Article 16):
- Payment to secured creditor **within secured property value**
- Example: Mortgage debt 500,000; property worth 800,000; debtor pays 500,000 → Not voidable

**Administrator Burden**: If seeking to void, must prove:
- Payment was within 6 months
- Debtor was insolvent at time
- Payment does not qualify for exceptions

### 1.4 Invalid Repayment (无效清偿)

**Definition**: Repayments made **after bankruptcy filing**

**Rule**: **Automatically invalid** per Bankruptcy Law

**Effect**: Administrator **must recover** invalid payments

**No Exceptions**: All post-filing repayments to individual creditors are invalid (except common benefit debts, secured creditor from secured property with court approval)

### 1.5 Administrator Actions

**Upon Discovering Individual/Invalid Repayment**:

```
Step 1: Identify payment date and bankruptcy filing date
Step 2: Determine category:
        ├─ After filing → Invalid repayment (automatically recoverable)
        └─ Before filing (but within 6 months) → Individual repayment (check exceptions)

Step 3: If individual repayment (pre-filing within 6 months):
        - Check if exception applies (normal operations, <1 month due, new value, secured)
        - If no exception: Assess if debtor was insolvent
        - Decide whether to pursue avoidance

Step 4: If pursuing recovery:
        - Demand return from recipient creditor
        - If refused: Initiate avoidance litigation

Step 5: Document and report internally (group communication)
```

---

## Part 2: Set-Off Rights / 抵销权

### 2.1 Definition and Legal Basis

**Set-Off (抵销)**: Mutual debts between debtor and creditor cancel each other out

**Bankruptcy Law Article 40**: Creditors may exercise set-off rights for mutual debts existing before bankruptcy filing

**Benefit**: Creditor achieves 100% recovery on its debt to debtor (which offsets its debt from debtor)

### 2.2 Conditions for Valid Set-Off

**Requirements**:
1. **Mutual debts**: Debtor owes creditor AND creditor owes debtor
2. **Both debts matured before bankruptcy filing** (or deemed matured per Article 46)
3. **Set-off not prohibited** (see prohibited scenarios below)

### 2.3 Prohibited Set-Offs (Article 40)

**Cannot Set Off If**:

**(1) Creditor's Debt to Debtor Arose After Bankruptcy Filing**:
- Creditor incurs obligation to debtor post-filing → Cannot use to offset pre-filing claim

**(2) Creditor Knew Debtor Insolvent and Provided Credit**:
- Creditor provided goods/services knowing debtor was insolvent (within 1 year before filing)
- Purpose: Prevent creditors from intentionally creating set-off opportunities

**(3) Negative Debts Resulting from Debtor's Legal Obligations**:
- Example: Debt owed by debtor due to debtor's illegal act

### 2.4 Additional Prohibited Set-Offs (Bankruptcy Interpretation II Articles 44-46)

**Article 44 - Affiliate Transactions**:
- Debtor's affiliate (controlling shareholder, subsidiary, etc.) owes debt to debtor
- Affiliate acquires claim against debtor after bankruptcy filing
- Affiliate cannot set off (prohibit strategic offsetting by insiders)

**Article 45 - Manipulated Set-Offs**:
- Debtor, knowing insolvency, increases obligations to creditor to create set-off opportunity
- Administrator may prohibit such set-offs

**Article 46 - Differing Debt Natures**:
- Not explicitly in law, but some courts prohibit offsetting debts of different natures (e.g., money vs. goods)
- Administrator discretion to allow or disallow

### 2.5 Set-Off Procedure

**Creditor Must Assert**: Set-off is **not automatic**; creditor must explicitly declare set-off right

**Process**:
1. Creditor declares both: (a) Claim against debtor, (b) Debt owed to debtor, (c) Intent to set off
2. Administrator reviews conditions (mutual, matured, not prohibited)
3. If valid: Confirm debt as **set-off** (creditor's claim and debtor's claim to creditor both reduced/eliminated)
4. Net debt (if any) is confirmed

**Example**:
- Creditor's claim against debtor: 100,000
- Creditor's debt to debtor: 40,000
- Set-off: 40,000
- Net confirmation: Creditor has 60,000 claim (ordinary or per classification)

### 2.6 Administrator Duty

**Internal Reporting**: All set-off assertions should be reported internally for coordination between asset and liability teams

**Asset Team Verification**: Verify debtor's claim to creditor actually exists and amount correct

---

## Part 3: Retrieval Rights / 取回权

### 3.1 Definition

**Retrieval Right (取回权)**: Owner of property in debtor's possession may retrieve its property

**Legal Basis**: Bankruptcy Law Article 38

**Typical Scenarios**:
- Goods sold to debtor but ownership not transferred (retention of title)
- Consignment goods
- Bailment goods
- Leased property (lessor retrieves)

### 3.2 Conditions

**Requirements**:
1. Property physically in debtor's possession but **not owned by debtor**
2. Claimant proves **ownership** (or retention of title per contract)
3. Property identifiable and still existing

### 3.3 Administrator Review

**Review Steps**:

```
Step 1: Verify current status of property (location, condition, identifiability)
Step 2: Review claimant's ownership proof:
        - Title documents (real property deed, vehicle registration)
        - Contracts with retention of title clauses (sales, consignment, lease)
        - Proof property not passed to debtor
Step 3: Check for competing claims (e.g., security interest, other claimant)
Step 4: If valid: Approve retrieval
        If invalid/disputed: Deny; require litigation
```

**Documentation**: Claimant should provide:
- Ownership证明
- Contract showing basis for property being in debtor's possession
- Identification of specific property (serial numbers, location)

### 3.4 Internal Reporting

**All Retrieval Right Assertions**: Report internally (coordination with asset team)

**Asset Team**: Verify property exists and not needed for ongoing operations (if reorganization)

---

## Part 4: Taxes and Social Insurance / 税款与社保债权

### 4.1 Tax Claims

**Scope**: Taxes owed to tax authorities

**Components**:
1. **Tax Principal** (税款本金)
2. **Late Payment Interest** (缓税利息, if applicable)
3. **Late Fees** (滞纳金)
4. **Fines and Penalties** (罚款、罚金)

**Classification**:

**(1) Tax Principal + Late Payment Interest (if applicable)**:
- **Priority**: Bankruptcy Law Article 113(2) - **Second priority** (after employee claims, before ordinary)

**(2) Late Fees (滞纳金)**:
- **Nature**: Determined as **ordinary claim** per Bankruptcy Law Interpretation II
- **Not** second priority

**(3) Fines and Penalties (罚款、罚金)**:
- **Nature**: **Subordinated claim** (劣后债权)
- Lower priority than ordinary claims

### 4.2 Social Insurance Claims

**Scope**: Social insurance contributions owed

**Types**:
- Pension insurance (excluding employee individual accounts - those are employee claims per Article 113(1))
- Medical insurance (excluding employee individual accounts)
- Unemployment insurance
- Work injury insurance
- Maternity insurance

**Classification**:

**(1) Insurance Contributions (Employer Portion)**:
- **Priority**: Article 113(2) - **Second priority**

**(2) Late Fees on Insurance**:
- **Nature**: **Ordinary claim**

**Administrator Review**: Verify amounts with social insurance authorities; request statements

---

## Part 5: Pending Contracts / 待履行合同

### 5.1 Definition

**Pending Contract (待履行合同)**: Contract where **both parties have not fully performed** at time of bankruptcy filing

**Bankruptcy Law Article 18**: Administrator may choose to **continue performance** or **terminate** pending contracts

### 5.2 Debt Treatment - Bifurcation

**Rule**: Debts from pending contracts are **bifurcated** by bankruptcy filing date

**(1) Pre-Filing Portion**:
- **Classification**: Bankruptcy claims (列入债权表)
- **Priority**: Per contract nature (ordinary, secured, etc.)

**(2) Post-Filing Portion** (if administrator elects to continue):
- **Classification**: **Common benefit debts** (共益债务, Article 42)
- **Priority**: Paid before all bankruptcy claims

**Example**:
- Supply contract: Monthly delivery, monthly payment
- Bankruptcy filed May 9
- Jan-Apr deliveries unpaid: Pre-filing → Bankruptcy claims (列入债权表)
- May-Dec deliveries (after May 9, if administrator continues contract): Post-filing → Common benefit debts (not in债权表)

### 5.3 Termination Damages

**If Administrator Terminates Contract** (Article 18):
- Counterparty suffers loss from termination
- Counterparty may declare **damages claim**
- Damages = **Expectation damages** (lost profits, reliance losses)
- **Classification**: Ordinary bankruptcy claim

**Administrator Review**: Determine damages per contract law; may require evidence of actual losses

**Note**: Termination is administrator's discretion; if standardized for reporting, follow latest court-agreed standard

---

## Part 6: VAT Invoicing and Tax Rate Changes / 增值税开票与税率调整

### 6.1 Invoicing as Contract Obligation

**Rule**: Issuing VAT invoice is **incidental obligation** of sales contract, not **precondition** for payment obligation

**Effect**: Even if seller has not issued invoice, buyer's payment obligation exists

**In Bankruptcy**: Creditor (seller) may declare debt including VAT, **regardless of whether invoice issued**

**Exception**: If contract explicitly made payment conditional on invoicing, then payment obligation contingent

### 6.2 Creditor Declaration of VAT

**Rule**: Creditor may declare debt **including VAT** as part of claim

**Rationale**: VAT is part of transaction price; debtor owes full amount including VAT

**Classification**: Same as underlying debt (if underlying debt is ordinary, VAT portion is also ordinary)

### 6.3 Inclusive vs. Exclusive of Tax

**Contract Silent on Whether Price Includes Tax**:
- **Presumption**: Price **includes tax** (含税价)
- Creditor cannot add VAT on top

**Contract Specifies Tax-Exclusive Price**:
- Creditor may declare: Price + VAT

**Example**:
- Contract: "Payment 100,000 yuan" (silent) → Assume 100,000 includes VAT
- Contract: "Payment 100,000 yuan plus VAT" → Creditor may declare 100,000 + applicable VAT (e.g., 13,000 @ 13% rate) = 113,000

### 6.4 Historical VAT Rate Changes

**China VAT Rate Reductions**:
- **May 1, 2018**: Rates reduced (e.g., 17% → 16%, 11% → 10%)
- **April 1, 2019**: Further reduced (16% → 13%, 10% → 9%)

**Application**:

**(1) Transaction Before Rate Reduction**:
- Creditor may declare per original higher rate OR per current lower rate
- **Administrator**: Accept whichever creditor declares (both are lawful)

**(2) Transaction After Rate Reduction**:
- Apply new lower rate

**Example**:
- Sale contract signed and performed in 2017, rate was 17%
- Creditor declares in 2024
- Creditor may declare 17% VAT or 13% VAT (creditor's choice)
- Administrator: Accept either

---

## Part 7: Pending Litigation/Arbitration Claims / 诉讼仲裁未决债权

### 7.1 Declaration Allowed

**Bankruptcy Law Article 47**: Claims in pending litigation or arbitration may be declared

**Effect**: Creditor may declare claim **provisionally**

### 7.2 Administrator Treatment

**Suspension of Final Determination**:
- Administrator **does not make final determination** of pending litigation/arbitration claims
- Administrator **provisionally notes** the claim
- Wait for litigation/arbitration to conclude

**After Judgment/Award Effective**:
- Administrator issues **final review opinion** per effective legal instrument
- Confirm amount per judgment/award

**If Litigation/Arbitration Dismissed or Creditor Loses**:
- Do not confirm claim

### 7.3 Voting Rights

**During creditors meetings**: Pending claims may have **provisional voting rights** (subject to court determination)

---

## Summary Checklist

**Individual/Invalid Repayment**:
```
□ Identified payments within 6 months before filing?
□ Identified post-filing payments?
□ Checked exceptions for individual repayment?
□ Assessed insolvency at time of payment?
□ Reported internally for potential recovery action?
```

**Set-Off Rights**:
```
□ Verified mutual debts exist?
□ Confirmed both debts matured before filing (or deemed matured)?
□ Checked prohibited scenarios (Articles 40, 44-46)?
□ Calculated net debt after set-off?
□ Coordinated with asset team?
```

**Retrieval Rights**:
```
□ Verified property in debtor's possession?
□ Reviewed claimant's ownership proof?
□ Checked property current status and identifiability?
□ Coordinated with asset team?
```

**Taxes and Social Insurance**:
```
□ Distinguished tax principal (second priority) vs. late fees (ordinary) vs. fines (subordinated)?
□ Distinguished insurance contributions (second) vs. late fees (ordinary)?
□ Verified amounts with authorities?
```

**Pending Contracts**:
```
□ Identified pre-filing portion (bankruptcy claims) vs. post-filing (common benefit)?
□ If termination: Assessed damages claim?
□ Classified correctly?
```

**VAT and Invoicing**:
```
□ Confirmed creditor may declare debt including VAT regardless of invoicing?
□ Determined if price includes tax (presumption) or excludes (explicit)?
□ Applied correct VAT rate per transaction date?
```

---

## Summary / 总结

Miscellaneous matters require careful attention to specific rules:

**Individual Repayment**: Within 6 months, voidable if insolvent + no exception

**Invalid Repayment**: Post-filing payments automatically recoverable

**Set-Off**: Allowed if mutual, matured, not prohibited; creditor must assert

**Retrieval**: Owner may retrieve property if proves ownership and property exists

**Taxes/Social Insurance**:
- Tax principal + late interest: Second priority
- Late fees: Ordinary
- Fines: Subordinated
- Insurance contributions: Second priority; late fees: Ordinary

**Pending Contracts**: Bifurcate pre/post-filing; post-filing = common benefit debts

**VAT**: Creditor may declare including VAT regardless of invoicing; presume price includes tax if silent

**Pending Litigation**: Provisionally note; finalize after judgment/award effective

**Cross-References**:
- Priority order: `debt-review-foundations` Skill
- Common benefit debts: `CLAUDE.md` (工作流执行详细说明部分)
- Secured vs. ordinary classification: Throughout all reference files
