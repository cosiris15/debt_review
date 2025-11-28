# Secured Claims Review Standards
# 担保类债权审查标准

## Purpose

Comprehensive standards for reviewing secured claims, including property security (mortgage, pledge), personal security (guarantee), mixed security, and complex issues like ultra vires guarantees, disguised security, and guarantor rights in bankruptcy.

## Part 1: Secured Claim Definition and Scope

**Secured Claims**: Claims secured by specific property of debtor or third party, enjoying priority repayment from secured property.

**Types**:
1. **Mortgage** (抵押): Real property, vehicles, equipment
2. **Pledge** (质押): Movable property, rights (stocks, IP, receivables)
3. **Guarantee** (保证): Personal guarantee by third party
4. **Mixed Security**: Combination of property and personal security

---

## Part 2: Property Security Review

### 2.1 Mortgage Rights (抵押权)

**Perfection Requirement**: Registration (for real property, vehicles, etc.)

**Civil Code Article 402**: Mortgage right established upon **registration**

**Review Points**:
□ Mortgage contract executed?
□ Mortgage registration completed?
□ Registration date and expiry (if applicable)?
□ Scope of secured claims per registration?

**If Not Registered**: No mortgage right → Creditor has ordinary claim, not secured

### 2.2 Pledge Rights (质权)

**Perfection Requirement**: Delivery (for movable property) or registration (for rights pledge)

**Civil Code Article 429**: Pledge right established upon **delivery of pledged property**

**Review Points**:
□ Pledge contract executed?
□ Pledged property delivered to creditor?
□ Or registration completed (for rights pledge)?

**Common Issue**: Debtor retains possession → No valid pledge

### 2.3 Scope of Security

**Contract Determines Scope**: Review security contract language

**Typical Scope**:
- Principal
- Interest
- Liquidated damages
- Damages
- Expenses for realizing secured claim (costs, fees)

**Administrator Review**:
- If scope includes "all debts and expenses" → Broadly secured
- If scope specifies "principal and interest only" → Narrower scope; penalties and costs are ordinary claims

**🔗 For Detailed Mortgage Effectiveness Analysis**: See `11_mortgage_effectiveness_analysis.md` for comprehensive coverage of:
- Mortgage registration effectiveness (登记生效 vs 登记对抗)
- Mortgage priority order rules (一物多押顺位)
- Impact of seizure on mortgage rights (查封对抵押权的影响)
- Mortgage defects and remedies (登记瑕疵与补正)
- Special situations: Under-construction projects, property expectancy rights

---

## Part 3: Guarantor and Debtor's Guarantor in Bankruptcy

### 3.1 Legal Framework

**Bankruptcy Law Article 51**:
- Guarantor who has **already repaid** debt on debtor's behalf: May declare **reimbursement claim**
- Guarantor who has **not yet repaid**: May declare **future reimbursement claim**
- **Exception**: If creditor has already declared full debt, guarantor cannot also declare (avoid double counting)

**Civil Code Article 700**: Guarantor who repays has right to reimbursement, subrogates to creditor's rights

**Supreme Court Bankruptcy Minutes Article 31** + **Civil Code Guarantee Interpretation Article 23**: Detailed rules

### 3.2 Three Scenarios

#### Scenario A: Creditor Declared Debt + Guarantor Has Not Repaid

**Rule**: Guarantor **cannot** declare reimbursement claim

**Rationale**: Creditor holds primary claim; guarantor's right is contingent

**Process**:
- Creditor declares full debt amount
- Administrator confirms creditor's claim
- Guarantor does not declare
- Creditor receives bankruptcy distribution
- After bankruptcy distribution, creditor can still seek payment from guarantor for undistributed portion
- If guarantor pays creditor after bankruptcy, guarantor cannot seek reimbursement from reorganized/liquidated debtor

#### Scenario B: Creditor Has Not Declared (or Partial Declaration) + Guarantor Wants to Declare

**Rule**: Guarantor may declare **only if creditor authorizes or confirms will not declare**

**Administrator Action**:
1. Contact creditor: Will you declare full amount?
2. If creditor says no (in writing): Guarantor may declare
3. If creditor says yes or plans to: Guarantor cannot declare (wait for creditor)

**Best Practice**: Encourage creditor to declare full amount

#### Scenario C: Guarantor Has Fully Repaid Creditor Before Bankruptcy Filing

**Rule**: Guarantor may declare reimbursement claim **in place of creditor**

**Process**:
- Guarantor provides evidence of full repayment to creditor
- Guarantor declares reimbursement claim against debtor
- Administrator confirms guarantor's claim
- Guarantor receives distribution (up to amount paid to creditor)

**Alternative** (if creditor already declared before guarantor repaid): Guarantor may request administrator transfer distribution to guarantor (substitution)

### 3.3 Guarantor Repayment After Bankruptcy Filing

**Rule**: If guarantor pays creditor after bankruptcy case concluded:
- **Cannot seek reimbursement** from reorganized or harmony agreement-compliant debtor
- **Can seek reimbursement** from debtor only for amounts **exceeding** what creditor received from bankruptcy distribution

**Example**:
- Original debt: 1,000,000
- Creditor received 20% distribution: 200,000
- Post-bankruptcy, guarantor paid creditor: 800,000 (to make creditor whole)
- Guarantor can request creditor return: 0 (creditor entitled to full 1,000,000)
- But guarantor cannot pursue reorganized debtor for reimbursement

---

## Part 4: Guarantee Period (保证期间) - Critical Time Limit

### 4.1 Nature: Exclusion Period

**Guarantee period is NOT statute of limitations**; it is **exclusion period** (除斥期间):
- Cannot be tolled, suspended, or interrupted
- If expired, guarantee right **extinguished**
- Creditor permanently loses right to claim guarantor

### 4.2 Determination of Guarantee Period

**Civil Code Article 692**:

**(1) Parties Agreed on Period**:
- Use agreed period
- **But**: If agreed period is earlier than or concurrent with primary debt performance deadline → Deemed no agreement

**(2) No Agreement or Unclear Agreement**:
- **6 months** from primary debt performance deadline

**(3) No Primary Debt Deadline Agreed**:
- 6 months from when creditor demands payment from debtor (with reasonable grace period)

**Example**:
- Debt due: 2020-12-31
- Guarantee contract: "Guarantee period until 2021-12-31"
- Guarantee period: 2020-12-31 to 2021-12-31 (1 year, per agreement)

**Example**:
- Debt due: 2020-12-31
- Guarantee contract: Silent on period
- Guarantee period: 2020-12-31 to 2021-06-30 (6 months, default rule)

### 4.3 Transitional Rule (Old Guarantee Law vs. Civil Code)

**Pre-Civil Code Guarantee Law** (before 2021-01-01): Default guarantee period was **6 months** (if agreed unclear) or **2 years** (if not agreed)

**Supreme Court Interpretation on Civil Code Time Effectiveness Article 27**:

For guarantees formed before Civil Code (pre-2021-01-01):
- If primary debt deadline → Civil Code effective date < 2 years: Apply 2-year rule
- If primary debt deadline → Civil Code effective date < 6 months: Apply 6-month rule

**Practical Effect**: Most guarantees now under Civil Code (2021-01-01+); use 6-month default

### 4.4 When Guarantee Period Starts

**General Rule**: Day after primary debt performance deadline

**If Primary Debt Has No Deadline**: When creditor demands payment from debtor (with grace period), deadline expires, then guarantee period starts

### 4.5 Claiming Against Guarantor Within Period

**General Guarantee** (一般保证):
- Creditor must **sue debtor** (or apply for arbitration) within guarantee period
- Effect: Guarantor cannot assert "debtor property exhaustion" defense

**Joint and Several Guarantee** (连带责任保证):
- Creditor must **demand performance from guarantor** within guarantee period
- Effect: Guarantor obligated to pay

**If Not Done Within Period**: Guarantee right extinguished

### 4.6 Administrator Review - Guarantee Period Expired?

```
Step 1: Determine primary debt deadline
Step 2: Calculate guarantee period per contract (agreed) or default (6 months)
Step 3: Check if creditor took required action (sued debtor for general guarantee; demanded from guarantor for joint guarantee) within period
Step 4: If period expired without action → Do not confirm guarantor's liability
Step 5: If within period → Guarantee valid, confirm per contract
```

### 4.7 Guarantee Period vs. Statute of Limitations

**Key Distinction**:
- **Guarantee period**: Time to **assert guarantee right**
- **Statute of limitations**: After guarantor becomes liable, time to **sue guarantor**

**Sequence**:
1. Guarantee period: Creditor must act within period to make guarantor liable
2. Once guarantor liable: Statute of limitations (on reimbursement claim) begins

**Example**:
- Debt due: 2020-12-31
- Guarantee period: 6 months → expires 2021-06-30
- Creditor demanded guarantor on 2021-05-01 (within period) → Guarantor liable
- Statute of limitations on guarantor debt: Starts 2021-05-01, runs for 3 years
- Creditor must sue guarantor by 2024-05-01 (3-year statute)

---

## Part 5: Ultra Vires Guarantee (越权担保)

### 5.1 Definition

**Ultra Vires Guarantee**: Company legal representative provides guarantee **without proper corporate authorization** (no board/shareholder resolution)

**Civil Code Guarantee Interpretation Article 8**: Framework for determining validity

### 5.2 When Corporate Resolution Required

**General Rule**: Company external guarantees require corporate resolution

**Specific Requirements**:

**(1) Guarantees for Shareholders or Actual Controllers**:
- **Must** have **shareholder meeting/assembly resolution**
- **Cannot** be mere board resolution
- Interested shareholders must abstain from voting

**(2) Guarantees for Others (Non-Shareholders)**:
- Check **company articles of association**:
  - If articles require shareholder resolution: Need shareholder resolution
  - If articles assign to board: Board resolution sufficient
  - If articles silent: Board resolution sufficient (for non-listed companies)

**(3) Listed Company Special Rules**:
- More stringent requirements per articles and securities regulations

### 5.3 Exceptions - No Resolution Needed

**Civil Code Guarantee Interpretation Article 8** provides three exceptions where guarantee is valid even without resolution:

**(1) Financial Institution Issuing Letter of Guarantee or Guarantee Company Providing Guarantee**:
- Their business is providing guarantees
- Not ultra vires

**(2) Company Guarantees for Its Wholly-Owned Subsidiary**:
- Applies to non-listed companies only
- Wholly-owned: 100% ownership
- Purpose: Facilitate subsidiary business operations

**(3) Guarantee Signed/Agreed by Shareholders Holding 2/3+ of Voting Rights**:
- Direct shareholder approval (not through meeting)
- Applies to non-listed companies
- Must be shareholders with 2/3+ of **voting rights on guarantee matters**

### 5.4 Validity Determination Framework

```
Question: Was there proper corporate resolution?
│
├─ YES → Guarantee valid
│
└─ NO → Check if any exception applies (Article 8)
    │
    ├─ Exception applies → Guarantee valid
    │
    └─ No exception → Check creditor's good faith
        │
        ├─ Creditor in good faith (didn't know/shouldn't have known) → Guarantee valid (apparent authority)
        │
        └─ Creditor not in good faith (knew or should have known) → Guarantee invalid
```

### 5.5 Good Faith Creditor (Apparent Authority)

**Question**: How to determine if creditor knew or should have known that resolution was missing?

**Factors**:
- Creditor's due diligence efforts
- Whether creditor requested resolution documents
- Whether situation obviously required resolution (e.g., guarantee amount very large relative to company size)
- Industry practice

**Burden**: Guarantor company bears burden to prove creditor was not in good faith

**Practical Effect**: Most courts presume creditor good faith unless clear evidence otherwise → Guarantee usually valid

### 5.6 Consequences of Invalid Ultra Vires Guarantee

**If Guarantee Determined Invalid**:
- Company not liable as guarantor
- **But**: Company may bear **fault-based liability** (缔约过失责任) for creditor's losses
- Typically: Compensation for creditor's reasonable reliance losses, not to exceed guarantee amount

**In Bankruptcy**: Invalid guarantee → Not a secured claim or priority claim; may be ordinary claim (if fault liability established)

**🔗 For Detailed Guarantee Effectiveness Analysis**: See `10_guarantee_effectiveness_analysis.md` for comprehensive coverage of:
- Ultra vires guarantee validity framework (越权担保效力认定,基于九民纪要第17-19条)
- Guarantee period and statute of limitations (保证期间与诉讼时效衔接)
- Spousal joint debt determination (夫妻共同债务认定)
- Principal-subordinate contract effectiveness (主从合同效力关联)
- Counter-guarantee liability (反担保责任)
- Typical case index and ruling principles (典型案例索引与裁判要旨对照表)
- 8-step comprehensive application process (综合应用步骤)

---

## Part 6: Disguised Security (让与担保) - Title Transfer as Security

### 6.1 Definition

**Disguised Security (让与担保)**: Parties use **sales contract or property transfer form** to achieve security purpose

**Common Form**: Debtor "sells" property to creditor (title transferred), with agreement that debtor may "repurchase" upon repaying debt

**Example**:
- Borrower owes 1M yuan to lender
- Borrower "sells" house (worth 2M) to lender for 1M
- Agreement: Borrower can "buy back" house for 1M when debt paid
- **Substance**: This is security, not sale

### 6.2 Legal Treatment

**Supreme Court Position**: Recognize as security arrangement

**Civil Code Guarantee Interpretation Article 68**: Validates title transfer as security (when debtor fails to pay, property belongs to creditor) → But actually treats as security interest

**Consequence in Bankruptcy**:

**(1) Property Registered in Creditor's Name**:
- Creditor does **not** own property absolutely
- Creditor has **secured claim** (security interest in property)
- Property ownership: Remains with debtor (or estate)
- Creditor enjoys priority from property value (like mortgagee)

**(2) Property Not Registered in Creditor's Name**:
- Creditor has no perfected security interest
- Creditor has **ordinary claim** (personal guarantee nature)

### 6.3 Administrator Review

**Identification**:
- Review "sale" agreement carefully
- Look for: Loan agreement, repurchase clause, price significantly below market value, original owner retains possession
- If substance is security → Treat as security

**Classification**:
- Property registered to creditor: Secured claim
- Property not registered: Ordinary claim

---

## Part 7: Mixed Security (混合担保) - Property + Personal Guarantee

### 7.1 Situation

**Mixed Security**: Same debt secured by both:
- Property security (mortgage/pledge), AND
- Personal guarantee

**Question**: When debtor defaults, must creditor first exhaust property security before claiming guarantor? Or can creditor directly claim guarantor?

### 7.2 Legal Rule

**Civil Code Article 392**: Rules for mixed security

**(1) Parties Agreed on Sequence**:
- Follow agreement
- Example: "Creditor must first foreclose mortgage, then may claim guarantor" → Must follow

**(2) No Agreement or Agreement Unclear**:

**Sub-Rule A**: If **debtor provides property security** (自己的财产担保):
- Creditor **must** first foreclose on debtor's property
- Only after exhausting debtor's secured property may creditor claim guarantor

**Sub-Rule B**: If **third party provides property security** (第三人提供物的担保):
- Creditor may **choose** to:
  - Foreclose on third party's property, OR
  - Claim guarantor, OR
  - Both (in any order)

**After Third Party (Property Provider or Guarantor) Pays**:
- Third party has right to seek reimbursement from debtor

### 7.3 Examples

**Example 1**:
- Loan to Company A
- Company A mortgages its own factory (debtor's property)
- Company B provides personal guarantee
- No agreement on sequence
- **Result**: Creditor must first foreclose factory; if insufficient, then claim Company B

**Example 2**:
- Loan to Company A
- Company B (third party) mortgages its factory
- Company C provides personal guarantee
- No agreement on sequence
- **Result**: Creditor may choose: foreclose Company B's factory OR claim Company C OR both

### 7.4 Bankruptcy Implications

**In Bankruptcy**:
- Secured property: Creditor has secured claim
- Personal guarantee: Depends on whether guarantor has paid and declared

**Administrator Application**:
- Confirm creditor's secured claim amount (up to property value)
- Remaining amount: Ordinary claim (unless other security exists)

---

## Part 8: Security Registration and Perfection

### 8.1 Perfection Methods by Asset Type

| Asset Type | Perfection Method |
|-----------|------------------|
| Real property (land, buildings) | Registration at real property registration authority |
| Vehicles | Registration at vehicle administration |
| Movable property pledge | Delivery to creditor |
| Accounts receivable pledge | Registration at PBOC Credit Reference Center |
| Equity pledge | Registration at company registration authority (or per articles) |
| Intellectual property pledge | Registration at IP office |

### 8.2 Legal Instruments as Perfection

**Civil Code Article 229**: Property rights change may occur when **effective legal instrument** takes effect

**Application**: Court judgment or arbitration award ordering debtor to provide mortgage → Mortgage right **established upon judgment effectiveness**, without separate registration

**Administrator Review**:
- If creditor provides judgment ordering collateral: Check judgment effective date
- If judgment effective: Secured claim (even without registration)
- But: May need to complete registration to oppose third-party claims

---

## Part 9: Timing Issues and Avoidance

### 9.1 Preference Security (Personal Guarantee vs. Property)

**Bankruptcy Law Article 32**: Voiding preferences

**Situation**: Within 6 months before bankruptcy filing, debtor:
- Provided property security for **previously unsecured debt**

**Effect**: May be voidable preference; security may be invalidated

**Exception**: Simultaneous exchange (debtor provides security when receiving new loan) → Not voidable

### 9.2 Administrator Action

**If security provided within 6 months before bankruptcy**:
- Review underlying debt: Was it previously unsecured?
- If yes: Security may be voidable (subject to court determination)
- Provisionally confirm as ordinary claim; note security may be challenged

---

## Part 10: Summary Checklist

**Property Security Review**:
```
□ Mortgage/pledge contract executed?
□ Perfection achieved (registration/delivery)?
□ Security scope defined and covers claimed items?
□ Registration within preference avoidance period?
```

**Guarantee Review**:
```
□ Guarantor identity and capacity verified?
□ Guarantee period calculated and not expired?
□ Creditor took required action within guarantee period?
□ Corporate resolution provided (if company guarantor)?
□ Ultra vires guarantee exceptions analyzed?
```

**Mixed Security**:
```
□ Identified all security types for same debt?
□ Determined sequence per agreement or Civil Code 392?
□ Classified creditor's claim portions correctly?
```

**Guarantor's Bankruptcy Rights**:
```
□ Has guarantor repaid creditor? (Yes → May declare reimbursement)
□ Has creditor declared full claim? (Yes → Guarantor cannot declare)
□ If not repaid: Future reimbursement claim noted (not confirmed until payment)
```

---

**Cross-References**:
- Guarantee period calculation: `01_subject_and_evidence_standards.md` Part 5
- Secured claim priority: `debt-review-foundations` Skill
- Mixed security in specific types: `04_financial_institution_standards.md` and `05_private_lending_standards.md`
