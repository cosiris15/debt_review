# Litigation-Based Claims Review Standards
# 涉诉类债权审查标准

## Purpose

This reference provides detailed standards for reviewing claims based on effective legal instruments (judgments, arbitration awards, mediation agreements). These claims have unique characteristics requiring special attention to execution periods, litigation costs, attorney fees, and delayed performance interest.

## Part 1: Verification of Effective Legal Instruments / 生效法律文书核实

### 1.1 Multi-Tier Legal Instruments

**Common Situation**: Creditor provides only first-instance judgment

**Administrator Duty**:
1. **Verify through multiple channels**:
   - Phone inquiry with creditor
   - Search China Judgments Online (中国裁判文书网)
   - Search court announcement websites
   - Check case status through court public inquiry systems

2. **Identify final effective instrument**:
   - If no appeal: First-instance judgment (after appeal period expires)
   - If appealed and affirmed: Second-instance judgment
   - If appealed and reversed: Second-instance judgment (new determination)
   - If retrial: Retrial judgment

3. **Use final instrument as basis**:
   - Principal amount per final judgment
   - Interest calculation per final judgment
   - Other obligations per final judgment

**Critical**: Never rely solely on first-instance judgment without verification

### 1.2 Effectiveness Date Determination

**General Rule**: Different instruments have different effectiveness dates

**(1) First-Instance Judgment** (without appeal):
- Effective date: Day after appeal period expires
- Appeal period: 15 days from judgment service date (for parties)
- If creditor unclear about service date: Assume judgment date is service date

**(2) Second-Instance Judgment**:
- Effective date: Service date (final, no appeal)

**(3) Arbitration Award**:
- Effective date: Award made date (generally immediate, unless specified otherwise)

**(4) Mediation Agreement**:
- Effective date: Service date or as specified in agreement

**Why Important**: Effectiveness date determines when performance period (if specified as "within X days of effectiveness") commences, which affects execution period calculation

---

## Part 2: Execution Period Review / 申请执行期间审查

### 2.1 Basic Rule

**Civil Procedure Law Article 246**: Period to apply for enforcement is **2 years**.

**Critical Principle**: Claims with effective legal instruments BUT exceeding execution period without applying for execution → **Do not confirm**

### 2.2 Detailed Calculation Rules

Already covered in `01_subject_and_evidence_standards.md` Part 5.3. Key points:

**(1) Commencement**:
- From last day of performance period specified in instrument → next day
- If no period specified: From effectiveness date → next day

**(2) Terminus**:
- Calculate to **creditor's declaration date** (or bankruptcy petition date if petitioner)
- NOT to bankruptcy filing date

**(3) Period**:
- 2 years (interruptible per statute tolling/suspension rules)

**Administrator Action**:
- If execution period appears exceeded: Require creditor to provide execution documents
- Execution documents include: Execution application, court acceptance notice, execution records, court inquiry records
- If creditor cannot provide: Do not confirm claim (execution period expired)

### 2.3 Execution Period Expiration - Confirmation Treatment

**⚠️ CRITICAL RULE**: Unlike statute of limitations expiration, execution period expiration in bankruptcy proceedings results in **claim rejection (【不予确认】)**, not merely deferred confirmation.

#### Legal Basis

1. **Supreme Court Interpretation on Bankruptcy Law (II) Article 21**:
   - Claims exceeding execution period cannot be revived in bankruptcy proceedings
   - Bankruptcy procedure is not a remedy for negligent creditors

2. **Shanghai High Court Bankruptcy Work Guidelines Article 9(2)**:
   - "超过诉讼时效或者申请执行期间的债权"不属于破产债权
   - "Claims exceeding statute of limitations OR execution period" are NOT bankruptcy claims

3. **Majority Judicial Practice**:
   - Across major bankruptcy jurisdictions in China
   - Consistent treatment: Do not confirm execution-barred claims

#### Processing Protocol

**Step 1: Identification**
```
Confirm debt is based on effective legal document:
□ Judgment (判决书)
□ Mediation agreement (调解书)
□ Arbitration award (仲裁裁决书)
□ Payment order (支付令)
```

**Step 2: Execution Evidence Review**
```
Request creditor to provide:
□ Execution application (执行申请书)
□ Court acceptance notice (受理通知书)
□ Execution records (执行笔录)
□ Court inquiry records (查询记录)
□ Any other evidence of execution interruption
```

**Step 3: Period Calculation**
```
If creditor CANNOT provide execution evidence:
→ Calculate period: Performance deadline + 2 years
→ Check: Filing date vs. expiration date
→ If filing date > expiration date: Period exceeded
```

**Step 4: Confirmation Decision**
```
If execution period exceeded WITHOUT valid interruption:
→ Mark: 【不予确认】(Do NOT confirm)
→ Reasoning: See template below
```

#### Correct Reasoning Template

**Chinese Version** (审查报告标准表述):
```
本债权基于（案号）[判决书/调解书/仲裁裁决书]，该法律文书确定的履行期限为[日期]，
申请执行期间自[起算日]起算至[届满日]届满。

债权人于[申报日期]申报债权，已超过申请执行期间。经要求，债权人未能提供执行申请书、
法院受理通知书或其他证明存在执行时效中断事由的证据。

根据《最高人民法院关于适用〈中华人民共和国企业破产法〉若干问题的规定（二）》第二十一条
及《上海市高级人民法院破产审判工作规范指引（试行）》第九条第2款，超过申请执行期间的债权
不属于破产债权。

建议：【不予确认】
```

**English Version**:
```
This claim is based on [Judgment/Mediation/Arbitration Award] (Case No. XXX).
The legal instrument specified performance deadline of [date], and execution period
expired on [expiration date].

Creditor declared claim on [declaration date], which is after execution period expiration.
Upon request, creditor failed to provide execution application, court acceptance notice,
or other evidence of execution period interruption.

Per Supreme Court Bankruptcy Interpretation (II) Article 21 and Shanghai High Court
Guidelines Article 9(2), claims exceeding execution period are NOT bankruptcy claims.

Recommendation: 【不予确认】(Do NOT confirm)
```

#### Distinguish From Statute-Barred Claims

**Critical Difference**:

| Type | Processing | Mark | Reasoning |
|------|-----------|------|-----------|
| **Statute-Barred** (诉讼时效届满) | Deferred confirmation | 【暂缓确认】 | No judicial confirmation obtained; substantive right uncertain |
| **Execution-Barred** (执行时效届满) | **Do NOT confirm** | **【不予确认】** | **Already has legal instrument but failed to exercise rights** |

**Why Different?**
- Statute-barred: Creditor never got judicial protection → Give chance for further review
- Execution-barred: Creditor already won but negligent in execution → No second chance in bankruptcy

#### Common Errors to Avoid

**❌ WRONG** (禁止使用):
1. "执行时效届满不消灭实体债权"
2. "债权人仍可在破产程序中申报"
3. "在破产程序中应按实体内容审查"
4. Marking as 【暂缓确认】instead of 【不予确认】

**✅ CORRECT** (正确处理):
1. Clearly state execution period exceeded
2. Note lack of execution application evidence
3. Cite Supreme Court Interpretation + Court Guidelines
4. Mark 【不予确认】
5. Explain: "Not bankruptcy claim per judicial interpretations"

#### Exception Cases

**ONLY confirm if creditor provides**:
1. **Execution application** filed within period
2. **Court acceptance notice** showing execution case filed
3. **Execution records** proving enforcement attempts
4. **Other valid interruption evidence** with specific dates

If creditor provides such evidence → Execution period interrupted → Calculate new expiration → May confirm if new period not exceeded

---

## Part 3: Litigation Costs / 诉讼费

### 3.1 Types of Litigation Costs

**Case Acceptance Fee** (案件受理费): Basic court filing fee
**Preservation Fee** (保全费): Fee for property preservation
**Announcement Fee** (公告费): Fee for public announcements
**Other**: Appraisal fees, expert witness fees, translation fees (if ordered by court)

### 3.2 Confirmation Conditions

**General Principle**: Per effective legal instrument, determine whether debtor must bear litigation costs.

#### Scenario 1: Debtor Must Bear + Creditor Paid + Court Ordered Payment to Creditor + Court Has Not Refunded

**Situation**:
- Judgment: "Debtor shall bear litigation costs of X yuan"
- Judgment further specifies: "Debtor pays directly to creditor" OR "Creditor paid; debtor shall reimburse creditor"
- Court has not refunded the costs to creditor
- Creditor declares this amount

**Administrator Action**: **Directly confirm**

**Rationale**: This is debtor's payment obligation to creditor, not to court

#### Scenario 2: Debtor Must Bear + Creditor Paid + Court Has Not Refunded + Creditor Persists in Declaring

**Situation**:
- Creditor paid costs to court
- Court has not refunded
- Creditor wants to declare as debt (to get payment from bankruptcy estate instead of court refund)

**Administrator Action**:
1. **Contact creditor promptly**: Confirm whether court has refunded
2. **If not refunded**: Suggest creditor apply for court refund first
3. **If creditor insists on declaring**: Require written commitment:

```
"Regarding Case [Case Number] ('Case'), [Creditor Name] has applied to [Court Name] for refund of litigation costs of [Amount] yuan. As of now, [Court Name] has not refunded the litigation costs. [Creditor Name] hereby commits: If [Court Name] subsequently refunds the Case litigation costs, [Creditor Name] will promptly (within 3 business days) notify the administrator, and the administrator shall lawfully reduce the relevant debt amount accordingly."
```

4. **If creditor does not provide written commitment**: Do not confirm litigation costs portion

**Rationale**: Prevent double recovery (from both court and bankruptcy estate)

#### Scenario 3: Other Situations

**Examples**:
- Debtor ordered to pay costs to court (not to creditor)
- Court already refunded costs to creditor
- Creditor did not pay costs in advance
- Judgment does not require debtor to bear costs

**Administrator Action**: Do not confirm litigation costs portion

### 3.3 Debt Classification

**If confirmed**: Litigation costs generally follow the same classification as the principal debt

**Example**:
- Secured loan principal (secured claim) + litigation costs → Litigation costs also secured (if security agreement covers "costs for realizing secured claim")
- Ordinary debt principal + litigation costs → Litigation costs also ordinary

---

## Part 4: Attorney Fees / 律师费

### 4.1 Confirmation Precondition

**Strict Rule**: Attorney fees confirmed **ONLY if**:
- Court judgment explicitly orders debtor to bear attorney fees
- Judgment specifies the amount

**If creditor claimed attorney fees in complaint but court rejected**: Do not confirm

**If creditor did not claim in complaint**: Generally do not confirm (unless special circumstances and contractual basis, see below)

### 4.2 Attorney Fees Not in Litigation Claims

**Situation**:
- Creditor did not include attorney fees in litigation claims (or claimed but not supported by court)
- But creditor declares attorney fees in bankruptcy procedure
- Claims contractual basis

**Administrator Action**:
1. **Review contract**: Check if contract stipulates attorney fees
2. **Verify actual occurrence**:
   - Attorney engagement agreement
   - Attorney fee invoices/receipts
   - Proof of payment
3. **If contract provides basis AND fees actually incurred**: May confirm
4. **Determine debt classification**:
   - If security agreement covers "costs for realizing secured claim": Secured
   - Example: Mortgage contract states "mortgaged property secures principal, interest, and costs for realizing creditor's rights" → Attorney fees may be secured
   - Otherwise: Ordinary claim

### 4.3 Debt Classification

**General Rule**: Same as litigation costs, follow principal debt classification

**Special Rule for Secured Claims**:
- Review security contract language carefully
- If security explicitly covers "realization costs" or "attorney fees": Secured
- If security only covers "principal and interest": Attorney fees are ordinary

---

## Part 5: Delayed Performance Interest / 迟延履行期间的债务利息

### 5.1 Legal Basis

**Civil Procedure Law Article 264** (formerly Article 253):
> "If obligor fails to perform monetary obligation within period specified by judgment, the obligor shall, per Civil Procedure Law Article 264, pay **delayed performance interest** in addition to the debt."

**Common Judgment Language**:
> "If [Debtor] fails to perform monetary obligation within the period specified in this judgment, [Debtor] shall, per Civil Procedure Law Article 264, pay delayed performance interest on double basis."

### 5.2 Two Components of Delayed Performance Interest

**Delayed Performance Interest includes TWO parts**:
1. **General delayed performance interest** (一般债务利息)
2. **Double-portion delayed performance interest** (加倍部分债务利息)

**Distinction is Critical**: Different calculation methods, different debt classifications

---

### 5.3 Part 1: General Delayed Performance Interest / 一般债务利息

#### 5.3.1 Definition

The "ordinary interest" portion that would accrue on monetary debt during delayed performance period.

#### 5.3.2 Calculation Method

**Rule**: Per effective legal instrument's determination

**Scenarios**:

**(1) Judgment Specifies Calculation Method**:
- "Pay principal X yuan, plus interest calculated at Y% from [Date] to actual payment date"
- Follow judgment's method to calculate to day before bankruptcy filing

**(2) Judgment Does Not Specify Interest Payment**:
- Do not calculate general delayed performance interest
- Reason: Court did not award this component; cannot add without legal basis

**Example**:
- Judgment: "Pay 1,000,000 yuan within 10 days of effectiveness"
- No mention of interest
- Result: Only calculate double-portion (see below), no general interest

**(3) Judgment Specifies Interest on Part of Amount**:
- Calculate interest only on the portion specified
- Example: "Pay principal 1,000,000, plus interest on 800,000 from [Date] at LPR"
- Calculate interest on 800,000 only

#### 5.3.3 Debt Classification

**General delayed performance interest** (if calculated): **Same classification as principal**

- Principal is secured → General interest is secured (if security covers interest)
- Principal is ordinary → General interest is ordinary

---

### 5.4 Part 2: Double-Portion Delayed Performance Interest / 加倍部分债务利息

#### 5.4.1 Legal Nature

**Nature**: **Subordinated claim** (劣后债权)

**Supreme Court** and majority judicial practice: Treat as penalty/punitive interest, subordinated to ordinary claims

**Bankruptcy Law Article 113** does not explicitly list, but judicial practice subordinates it after ordinary claims

#### 5.4.2 Calculation Formula

```
Double-Portion Interest = Calculation Base × 0.0175% (daily) × Delayed Performance Days
```

**Daily Rate**: **0.0175%** (万分之1.75) = **1.75 per 10,000 per day**

**Annual Rate**: 0.0175% × 365 = 6.3875%

#### 5.4.3 Calculation Base / 计算基数

**Article 264 Language**: "Double interest on monetary obligation amount"

**Critical Question**: What is "monetary obligation amount"?

**General Rule**: **Principal** as determined by judgment

**Complex Question**: Should attorney fees, litigation costs be included in base?

##### (1) Principal

**Rule**: Always included

**"Principal" defined**:
- In loan cases: Loan principal
- In sales cases: Unpaid purchase price
- In services cases: Unpaid service fees
- In judgments stating "Defendant shall pay [Amount]": That amount is principal

##### (2) Interest/Penalty Accrued Through Judgment Date

**Judgment may order**:
- "Pay principal 1,000,000"
- "Pay interest of 50,000 accrued through judgment date"
- "Pay penalty of 30,000"

**Question**: Is the 50,000 interest or 30,000 penalty part of "monetary obligation" for calculating double-portion interest?

**Rule**: **Interest OR Penalty (choose one, not both) may be included, but not both simultaneously**

**Rationale**: Avoid double-counting; both are ancillary to principal

**Beijing High Court Guidance**: If judgment separately lists interest/penalty through judgment date, it can be part of base; but typically only ONE type (interest or penalty) is recognized, not both

##### (3) Attorney Fees

**Question**: If judgment orders debtor to bear attorney fees, should it be included in calculation base?

**Rule**: **If creditor includes attorney fees in declared double-portion interest base, may accept**

**Rationale**: Attorney fees are part of monetary obligation ordered by court

**Beijing High Court Answer on Delayed Performance Issues**: Attorney fees awarded by judgment may be included in calculation base

**Administrator Practice**:
- If creditor **actively includes** attorney fees in base: Accept
- If creditor **does not include** attorney fees in base: Administrator **does not proactively add** them

##### (4) Litigation Costs

**Question**: If judgment orders debtor to pay litigation costs directly to creditor, should it be included in calculation base?

**Rule**: **If judgment explicitly orders "debtor pays directly to creditor", may be included in base**

**Reasoning**: Direct payment to creditor makes litigation costs part of debtor's monetary obligation to creditor

**Administrator Practice**: Same as attorney fees - accept if creditor includes, do not proactively add otherwise

##### (5) General Delayed Performance Interest Itself

**Question**: Can general interest (Part 1 above) be included in double-portion interest calculation base?

**Rule**: **Absolutely NO**

**Reasoning**: Civil Procedure Law Article 264 explicitly states double interest is calculated on amounts "**除一般债务利息之外**" (EXCLUDING general delayed interest)

**Example**:
- Judgment: Pay principal 1,000,000 + interest per LPR to actual payment date
- Double-portion base: 1,000,000 (principal only)
- Double-portion base ≠ 1,000,000 + accrued LPR interest

**Exception**: If judgment **only** orders interest payment (no principal), then interest itself can be the base

##### (6) Penalty/Liquidated Damages

**Question**: If judgment orders payment of penalty or liquidated damages, should it be included?

**Rule**: **Refer to interest treatment above** - may include, but not simultaneously with interest

**Practical Application**: Usually either interest OR penalty is recognized in the base, not both

#### 5.4.4 Delayed Performance Period / 迟延履行期间

##### Start Date

**Rule**: Day after performance period specified in legal instrument expires

**Scenarios**:

**(1) Judgment Specifies Clear Performance Period**:
- "Perform within 10 days of effectiveness"
- Effectiveness date: 2020-01-17
- Performance deadline: 2020-01-27
- Delayed performance period **starts**: 2020-01-28 (day after deadline)

**(2) Judgment Does Not Specify Performance Period**:
- "Pay [Amount]" (no deadline)
- Legal instrument effective date: 2020-01-17
- Delayed performance period **starts**: 2020-01-17 (same day, deemed immediate performance obligation)

**(3) Installment Performance**:
- Each installment has its own deadline
- Calculate delayed interest separately for each overdue installment from its own deadline

##### End Date

**Rule**: **Day before bankruptcy filing date**

**Reasoning**: Bankruptcy Law Article 46 - interest stops accruing from bankruptcy filing date

**Calculation**:
- Bankruptcy filing date: 2024-05-09
- Delayed performance interest calculates to: 2024-05-08 (day before)

**Important**: Count the start date and do not count the end date's next day (stop at day before filing)

##### Day Count Formula

```
Days = End Date - Start Date + 1
```

**Example**:
- Start: 2020-01-28
- End: 2024-05-08
- Days = [calculate exact days between dates, inclusive of start date]

##### Actual Payment Does Not End Period

**Critical Rule**: If debtor makes payment during bankruptcy procedure (after filing), it does **NOT** extend delayed performance period

**Reasoning**: Interest stops at bankruptcy filing date per Bankruptcy Law Article 46; post-filing events do not affect this

---

### 5.5 Administrator's Approach to Double-Portion Interest

#### 5.5.1 Not Proactively Calculated

**Rule**: Administrator **does not proactively calculate** double-portion interest for creditors who did not declare it

**Reasoning**:
- Creditor's choice whether to claim
- Administrator role is review, not advocacy for creditors

#### 5.5.2 When Creditor Declares "Delayed Performance Interest" Without Specification

**Situation**: Creditor declares "delayed performance interest" but does not specify general vs. double-portion

**Administrator Treatment**: **Deemed to have declared delayed performance interest** (both components if applicable)

**Administrator Action**:
1. Calculate both components per standards above
2. Classify appropriately (general interest per principal classification; double-portion as subordinated)

#### 5.5.3 When Creditor Declares with Calculation

**Situation**: Creditor provides amount and calculation method/process

**Administrator Action**:
1. Review calculation for correctness
2. Compare with administrator's own calculation
3. **Confirm the lower amount** between creditor's calculation and administrator's calculation

**Rationale**: Benefit of doubt to estate if calculation dispute; creditor bears burden of accurate calculation

#### 5.5.4 Payment Allocation

**Rule**: For payments made by debtor, allocation order (unless specified otherwise):
1. Costs for realizing claims
2. Interest
3. Principal

**Special Rule**: Do **not** preferentially deduct double-portion interest; treat as part of "interest" category

**Civil Code Article 561**: Payment insufficient for full performance shall be allocated per: (1) Costs for realizing claim; (2) Interest; (3) Principal

---

### 5.6 Practical Example - Comprehensive Calculation

**Case Facts**:
- First-instance judgment date: 2020-01-01
- Judgment: "Within 10 days of effectiveness, pay principal 1,000,000, plus interest per LPR 1-year from 2019-06-01 to actual payment; bear case acceptance fee 15,000 and attorney fees 30,000."
- Judgment served to both parties on 2020-01-01
- No appeal; effective 2020-01-17 (after 15-day appeal period expires)
- Bankruptcy filed: 2024-05-09
- Creditor declaration date: 2024-08-01

**Calculation**:

**(1) Principal**: 1,000,000 ✓

**(2) General Delayed Performance Interest**:
- Base: 1,000,000
- Start: 2019-06-01 (per judgment)
- End: 2024-05-08 (day before bankruptcy filing)
- Rate: LPR 1-year (assume 3.85% during period for simplicity; in practice, apply segmented LPR rates)
- Interest = 1,000,000 × [total days] × 3.85% / 360
- Classification: Same as principal

**(3) Double-Portion Delayed Performance Interest**:
- Base: 1,000,000 (principal only; general interest explicitly excluded)
- Start: 2020-01-27 (performance deadline per judgment) + 1 day = 2020-01-28
- End: 2024-05-08 (day before bankruptcy filing)
- Days: 1562 days (example)
- Double-portion interest = 1,000,000 × 0.0175% × 1,562 = 273,350
- Classification: **Subordinated claim**

**(4) Attorney Fees**: 30,000 (per judgment) ✓
- Classification: Same as principal (or secured if security covers realization costs)

**(5) Case Acceptance Fee**: 15,000 (per judgment) ✓
- Classification: Same as principal

**(6) Execution Period Check**:
- Execution period starts: 2020-01-28 (day after performance deadline)
- Declaration date: 2024-08-01
- Elapsed: Over 4 years → **Exceeds 2-year execution period**
- Require execution documents; if not provided, do not confirm

---

## Part 6: Summary / 总结

Litigation-based claims have **procedural advantages** (effective legal instruments) but also **procedural risks** (execution periods):

**Key Review Points**:
1. **Verify final effective instrument** (not just first-instance judgment)
2. **Check execution period** (2 years; strict; requires execution documents if exceeded)
3. **Litigation costs**: Confirm only if court ordered payment to creditor AND court hasn't refunded (or creditor commits to return if refunded)
4. **Attorney fees**: Confirm only if explicitly awarded by court (or contractual basis + actual occurrence for non-litigated fees)
5. **General delayed performance interest**: Per judgment determination; same classification as principal
6. **Double-portion delayed performance interest**: Fixed 0.0175% daily rate; calculate on principal (and possibly attorney fees/costs if creditor includes); classify as **subordinated claim**

**Critical Errors to Avoid**:
- ❌ Accepting expired execution period claims without execution documents
- ❌ Confirming litigation costs that court may refund without creditor commitment
- ❌ Including general interest in double-portion interest calculation base
- ❌ Classifying double-portion interest as ordinary claim (must be subordinated)
- ❌ Calculating double-portion interest to bankruptcy filing date instead of day before

**Cross-References**:
- Execution period rules: `01_subject_and_evidence_standards.md` Part 5.3
- Interest calculation principles: `03_interest_calculation_standards.md`
- Debt classification: `debt-review-foundations` Skill
