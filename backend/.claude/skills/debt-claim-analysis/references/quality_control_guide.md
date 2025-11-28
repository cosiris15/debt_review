# Quality Control and Error Prevention Guide

## Purpose

This guide consolidates quality control standards, common error prevention measures, and self-checking procedures to ensure high-quality debt analysis outputs.

## Part 1: Quality Control Process

### Stage 1: Pre-Analysis Checks

**Before starting debt analysis work**:

#### Critical Date Verification (MANDATORY)

**⚠️ This is a MANDATORY step - MUST execute before ANY analysis work**

```
□ Read `.processing_config.json` from creditor directory
□ Extract bankruptcy filing date (破产受理日期)
□ Calculate interest stop date (= bankruptcy date - 1 day)
□ Cross-verify with fact-checking report dates
□ Record dates clearly in report introduction
□ If inconsistency found: STOP WORK and report
```

**Output Format**:
```
✅ 破产受理日期核对完成
- 破产受理日期：2023-05-12
- 停止计息日期：2023-05-11
- 与事实核查报告一致：是
- 配置文件状态：正常
```

**Critical Importance**: Bankruptcy filing date directly determines ALL interest calculation cutoff points. Wrong dates invalidate entire analysis.

#### Fact-Checking Report Review

```
□ Fact-checking report received and complete
□ Independent debt relationships count verified
□ Evidence materials properly classified
□ Settlement/confirmation documents identified
□ No gaps or inconsistencies in timeline
```

### Stage 2: During Analysis Checks

#### Amount Breakdown Quality

```
□ All amount items broken down to smallest meaningful units
□ Each item has specific legal basis (contract, judgment, etc.)
□ No umbrella terms like "本金" without specification
□ Each item linked to evidence in fact-checking report
□ Items properly categorized (本金/利息/费用)
```

#### Interest Calculation Quality

**Universal Requirements**:
```
□ ALL calculations use universal_debt_calculator_cli.py
□ NO manual calculations performed
□ Calculation commands documented in report
□ Excel/CSV output files generated
□ Files properly named and saved to 计算文件/
```

**Parameter Verification**:
```
□ Principal amount matches evidence
□ Start date is correct (loan date, overdue date, etc.)
□ End date ≤ bankruptcy filing date - 1 day
□ Interest rate matches contract/legal standard
□ LPR term (1y vs 5y) selected based on period rules
```

**Period Assessment for LPR** (CRITICAL):
```
□ Debt period calculated: Start date → bankruptcy date - 1
□ Period length recorded clearly (days/years)
□ If period > 5 years: Reviewed 5y LPR applicability
□ If fixed rate declared but period > 5 years: Reviewed LPR floating rate
□ Selection rationale documented
```

### Stage 3: Post-Calculation Checks

#### Cross-Validation

```
□ Calculation results compared with declared amounts
□ 就低原则 applied (if calculation > declaration, use declaration)
□ 就无原则 applied (items not declared are excluded)
□ Evidence support verified for each confirmed item
□ Penalty cap verified (4× LPR maximum)
```

#### Statute of Limitations

```
□ Start date determined with clear basis
□ Period (2y or 3y) calculated using transition rule
□ ALL evidence reviewed for interruption events
□ Interruption dates are SPECIFIC (not vague)
□ Recalculation performed if interruptions exist
□ Final expiration vs. filing date compared
□ Time-barred debts marked【暂缓确认】
```

### Stage 4: Output Quality Checks

#### Report Completeness

```
□ Report follows template structure
□ All required sections present
□ Independent debt relationships correctly identified
□ Amount items properly categorized and detailed
□ Interest calculation parameters complete
□ Statute analysis thorough with reasoning
□ Final confirmation amounts clearly stated
```

#### Calculation Files

```
□ Excel/CSV files generated for ALL calculations
□ Files saved to 计算文件/ directory
□ If no calculations: TXT explanation file created
□ File inventory documented in report
```

**🔴 File Consolidation Verification (2025-11-04 New Standard)**:

```
Single Calculation Item (计算项 == 1):
□ File name: {债权人名称}_{计算类型}.xlsx
□ Single sheet in Excel file
□ Example: "张三公司_借款利息计算.xlsx"

Multiple Calculation Items (计算项 >= 2):
□ File name: {债权人名称}_计算过程.xlsx (UNIFIED)
□ Single Excel file (NOT multiple separate files)
□ Number of sheets == Number of calculation items
□ First calculation command did NOT use --append
□ Subsequent calculations all used --append
□ Sheet names are descriptive (借款利息, 违约金, 迟延履行利息, etc.)
□ Report references file with specific sheet names
□ Example: "江苏姜堰船舶_计算过程.xlsx" with 2 sheets

Verification Method:
□ Count calculation items in debt analysis report
□ Count Excel files in 计算文件/ directory
□ If items >= 2 AND files > 1: ❌ ERROR (should be 1 consolidated file)
□ If consolidated file exists, verify sheet count matches item count
□ Check report "附件" section references sheets correctly
```

## Part 2: Common Errors and Prevention

### Category 1: Debt Classification Errors

#### Error 1.1:劣后债权识别遗漏

**❌ Wrong**: Classifying delayed performance interest as ordinary debt

**✅ Right**: Delayed performance interest (加倍部分) is subordinated debt per Bankruptcy Law

**Example Case**:
- 16,688.74元 delayed performance interest → Should be 劣后债权, NOT 普通债权

**Prevention**:
```
□ Create subordinated debt checklist
□ Mark all "迟延履行" items as subordinated
□ Clearly separate ordinary vs. subordinated amounts in output
```

#### Error 1.2: Tax Authority Debt Classification

**❌ Wrong**: Classifying individual income tax and individual social security as ordinary debt

**✅ Right**: Individual income tax (个人所得税) and individual social security fees (个人社会保险费) from tax authorities are EMPLOYEE PRIORITY DEBTS

**Prevention**:
```
□ Review tax authority claims for individual tax/social security components
□ Identify individual portions separately
□ Classify as employee priority debt (职工债权)
□ List separately in review opinion table
```

#### Error 1.3: Employee Debt Verification Insufficient

**❌ Wrong**: Accepting employee debt claims without proper documentation

**✅ Right**: Strict verification standards:
- **Core materials required**: Labor contract, arbitration document, OR judgment
- **No core materials**: Mark【暂缓确认】, pending company confirmation
- **After company confirmation**: If employee → analyze amount; if labor service relation → ordinary debt

**Prevention**:
```
□ Check for labor contract/arbitration/judgment
□ If absent: Mark【暂缓确认】for company verification
□ Distinguish employee debt vs. labor service debt
□ Flag potential false employee claims
```

### Category 2: Interest Calculation Errors

#### Error 2.1: Penalty Cap Violation

**❌ Wrong**: Confirming penalty at declared amount without checking legal maximum

**✅ Right**: Penalties cannot exceed 4× LPR; apply cap BEFORE 就低原则

**Example Case**:
- Declared: 143,661.11元 penalty
- Contractual calculation: 143,661.11元
- 4× LPR cap: 47,419.84元
- **Correct confirmation**: 47,419.84元

**Prevention**:
```
□ ALL penalties undergo 4× LPR cap verification
□ Calculate: Contract penalty vs. 4× LPR cap
□ Use lesser amount, then apply 就低原则 vs. declared
□ Document cap limitation reasoning
```

#### Error 2.2: Delayed Performance Interest Base Error

**❌ Wrong**: Using only principal as delayed performance interest base

**✅ Right**: Base may include principal + interest + penalty per legal document

**Example Case**:
- Wrong base: 48,000元 (principal only)
- Correct base: 50,287元 (including penalty)

**Prevention**:
```
□ Carefully read judgment/mediation wording on debt scope
□ Identify all components: principal, interest, penalty, costs
□ Clearly list base composition in calculation parameters
□ Verify base against creditor declaration
```

#### Error 2.3: Interest Stop Date Error

**❌ Wrong**: Calculating interest beyond bankruptcy filing date

**✅ Right**: ALL interest stops at bankruptcy filing date - 1 day

**Prevention**:
```
□ Set stop date limit: bankruptcy date - 1
□ Verify in ALL calculation commands
□ Double-check Excel output end dates
□ Cross-reference with .processing_config.json
```

#### Error 2.4: LPR Term Selection Error (High Frequency!)

**❌ Wrong**: Using 1-year LPR for >5 year debt period without review

**✅ Right**: Debts > 5 years MUST consider 5-year+ LPR

**Prevention**:
```
□ Calculate debt period: Start date → bankruptcy date - 1
□ Record period clearly (days/years)
□ If > 5 years: Seriously consider 5y LPR
□ Even if fixed rate declared: Review LPR applicability
□ Document selection rationale
```

**Example**:
```
Debt period: 2018-01-01 to 2025-05-11 = 7+ years
Wrong: Using 1y LPR by default
Right: Evaluate whether 5y LPR should apply, document reasoning
```

#### Error 2.5: Daily Rate Conversion Error (High Frequency!)

**❌ Wrong**: Converting daily rate to annual rate with wrong base (365 vs 360 inconsistency)

**✅ Right**: Use direct daily rate calculation: 日利率 × 天数 × 本金

**Prevention**:
```
□ For daily rates: Use "日利率×天数×本金" formula directly
□ Avoid annual rate conversion
□ Prevents 365/360 base confusion
□ Verify calculator uses correct method
□ Check calculation result for reasonableness
```

### Category 3: Statute of Limitations Errors

#### Error 3.1: Interruption Event Consideration Insufficient

**❌ Wrong**: Declaring time-barred without thorough interruption review

**✅ Right**: Carefully examine ALL evidence for potential interruptions

**Example Case**:
- Creditor mentioned multiple payments
- Could constitute debt acknowledgment → Statute restarts

**Prevention**:
```
□ Review all payment records
□ Check for reconciliation statements, confirmations
□ For borderline cases: Mark【暂缓确认】with evidence needs
□ List what supplemental evidence would resolve time-bar question
```

#### Error 3.2: Vague Interruption Dates (High Frequency!)

**❌ Wrong**: "债务人在申报前确认债务" (no specific date)

**✅ Right**: "债务人于2022年12月15日在对账单上签字确认债务（证据第15页）"

**Prevention**:
```
□ MUST record specific interruption date
□ MUST cite evidence supporting that date
□ MUST recalculate period from interruption date
□ MUST compare recalculated expiration with filing date
□ No vague time references allowed
```

**Example**:
```
❌ Wrong: "债权人在2025年前多次催收"
✅ Right: "债权人于2022年8月15日发送催款函（证据第20页，快递回执证明2022年8月17日送达）"
```

#### Error 3.3: Acceleration Clause Missed

**❌ Wrong**: Missing contract acceleration clauses, wrong deadline determination

**✅ Right**: Search for acceleration keywords and apply

**Keywords**: "加速到期", "提前到期", "立即到期", "全部债务到期"

**Prevention**:
```
□ Search contracts for acceleration clause keywords
□ Review breach consequences section
□ If acceleration triggered: Adjust statute start date
□ Document acceleration application
```

### Category 4: Cost Confirmation Errors

#### Error 4.1: Undecided Case Costs Confirmed

**❌ Wrong**: Confirming litigation/arbitration fees for pending cases

**✅ Right**: Pending case fees NOT confirmed in principle

**Example Case**:
- Arbitration case not yet decided
- 23,320元 arbitration fee declared
- **Correct**: Do not confirm (case pending)

**Prevention**:
```
□ Distinguish decided vs. pending cases
□ Mark pending case costs separately
□ Explain non-confirmation reasoning in report
□ Note: May be reconsidered if case concludes
```

#### Error 4.2: Pending Lawsuit Improper Handling

**❌ Wrong**: Marking entire debt【暂缓确认】if lawsuit pending

**✅ Right**: Review debt on merits; note lawsuit situation; don't暂缓 solely due to pending suit

**Handling**:
- Creditor usually withdraws prior lawsuit after bankruptcy filing
- Review debt as if no lawsuit (initial conclusion)
- Note the pending suit situation
- Await client feedback for adjustments if needed

**Prevention**:
```
□ Identify pre-filing lawsuits not yet decided
□ Review debt claim on substantive merits
□ Reach initial conclusion (don't暂缓 automatically)
□ Note special situation in opinion
□ Establish follow-up adjustment mechanism
```

### Category 5: Principle Application Errors

#### Error 5.1: Proactive Item Addition (就无原则 Violation)

**❌ Wrong**: Creditor didn't declare item, analyst calculates and includes it

**✅ Right**: 就无原则 - Items not declared are NOT confirmed

**Examples**:
- Creditor didn't declare delayed performance interest → Don't calculate
- Evidence shows attorney fees, creditor didn't claim → Don't confirm

**Prevention**:
```
□ Create declaration item checklist
□ Mark "债权人未申报" for identified but unclaimed items
□ Before calculating: Verify creditor declared this item
□ Never expand claim scope beyond declaration
```

#### Error 5.2: Calculation Base Expansion

**❌ Wrong**: Expanding calculation base beyond creditor's declaration

**✅ Right**: Strictly follow creditor's declared calculation base

**Example**:
- Creditor calculated delayed interest on judgment principal only
- Analyst adds costs to base without creditor declaring
- **Wrong**: Don't expand base

**Prevention**:
```
□ Identify creditor's declared calculation base
□ Do not add components creditor didn't include
□ Especially: Don't calculate delayed interest on court fees unless declared
```

## Part 3: High-Frequency Error Checklist

**⚠️ Based on actual case analysis - These errors occur MOST frequently**

### Error Type A: 5-Year+ Debt LPR Term Selection

```
□ Period calculated: From start date to bankruptcy date - 1
□ Period recorded: ___ days / ___ years
□ If period > 5 years: Evaluated 5y LPR applicability
□ Even if fixed rate declared: Reviewed LPR floating option
□ Selection rationale clearly documented
```

**Why Critical**: Using 1y LPR for 7-year debt can cause significant calculation error.

### Error Type B: Daily Rate Calculation Base Conversion

```
□ Daily rate calculations use direct formula: 日利率×天数×本金
□ No annual rate conversion performed
□ Avoided 365/360 base inconsistency
□ Formula expression accurate in report
□ Result verified for reasonableness
```

**Why Critical**: Conversion errors compound over long periods.

### Error Type C: Statute Interruption Date Vagueness

```
□ All interruption events have SPECIFIC dates
□ Dates supported by evidence citations
□ Recalculation from interruption date performed
□ Recalculated expiration vs. filing date compared
□ No vague time references (e.g., "申报前", "2025年前")
□ Conclusion consistent with calculation
```

**Why Critical**: Vague dates make statute determination unreliable.

## Part 4: Pre-Submission Self-Check

### Comprehensive Checklist

**Date Verification**:
```
□ Bankruptcy dates verified from .processing_config.json
□ Dates recorded in report introduction
□ Interest stop date = bankruptcy date - 1
□ All calculations end on or before stop date
```

**Amount Analysis**:
```
□ All items broken down to smallest units
□ Each item has legal basis and evidence
□ Proper categorization (本金/利息/费用)
□ Independent debt relationships correctly identified
```

**Interest Calculations**:
```
□ ALL calculations use universal_debt_calculator_cli.py
□ NO manual calculations
□ Calculation commands documented
□ Excel/CSV files generated and saved
□ Parameters verified (principal, dates, rates)
□ LPR term selection reviewed for >5 year debts
□ Penalties capped at 4× LPR
□ Delayed performance interest prerequisites verified
```

**Statute Analysis**:
```
□ Start date determined with basis
□ Period (2y/3y) calculated via transition rule
□ All interruption events identified with specific dates
□ Recalculation performed if interruptions exist
□ Final expiration vs. filing date compared
□ Time-barred debts marked【暂缓确认】
```

**Principle Application**:
```
□ 就低原则 applied (calculation vs. declaration)
□ 就无原则 applied (undeclared items excluded)
□ Evidence support verified for all items
□ No proactive expansion of claim scope
```

**Output Quality**:
```
□ Report follows template structure
□ All sections complete
□ Calculation files properly named
□ Files in correct directories (工作底稿/, 计算文件/)
□ File inventory documented
□ Logic clear and consistent throughout
```

## Part 5: Specific Item Checks

### Delayed Performance Interest Verification

**Before confirming**:
```
□ Is this a judgment/mediation/arbitration debt?
□ Has performance deadline been determined?
□ Has performance deadline EXPIRED?
□ Did creditor DECLARE this interest?
□ Is calculation base correctly identified (may include principal+interest+penalty)?
```

**If ANY answer is "No"**: Do NOT confirm delayed performance interest.

### Court Fees Special Check

```
□ Identified court fees separately
□ Did NOT calculate delayed performance interest on fees
□ Noted separate performance deadline
□ Exercised caution on time-bar determination
```

### Penalty Interest Special Check

```
□ Calculated contractual penalty per terms
□ Calculated 4× LPR cap
□ Used lesser of: (contractual, 4× LPR cap, declared amount)
□ Documented cap limitation if applied
□ Classified as "利息" not "其他"
```

### Tax Authority Debt Special Check

```
□ Identified individual income tax component
□ Identified individual social security component
□ Separated these as employee priority debt
□ Listed clearly in review opinion table
□ Classified remaining tax/social security appropriately
```

## Part 6: Error Documentation and Learning

### Error Recording Format

When error discovered:
```
Error Type: [e.g., LPR term selection error]
Case: [Creditor name, date]
What Happened: [Brief description]
Correct Approach: [What should have been done]
Prevention Added: [Checklist item added]
```

### Continuous Improvement

**Update triggers**:
- New error type discovered
- Legal/regulatory changes
- Judicial interpretation updates
- Systematic pattern identified in case reviews

**Version control**:
- Document each update
- Record specific errors addressed
- Maintain historical versions
- Evaluate prevention effectiveness

## Part 7: Quality Metrics

### Acceptable Standards

**Minimum Requirements**:
- ✅ All calculations use calculator tool
- ✅ All dates verified and consistent
- ✅ Calculation files generated
- ✅ LPR terms reviewed for long-term debts
- ✅ Penalties capped at 4× LPR
- ✅ Statute analysis thorough
- ✅ 就低/就无 principles applied
- ✅ Report structure complete

**Gold Standards**:
- Above PLUS:
- Zero calculation errors
- All edge cases identified and handled
- Comprehensive statute analysis with all interruptions considered
- Clear documentation of all judgment rationale
- Proactive risk identification

### Red Flags

**If you see these, something is likely wrong**:
- Calculation without calculator tool usage
- Interest calculation ending after bankruptcy date
- 1-year LPR for 7+ year debt without review explanation
- Penalty >4× LPR without cap notation
- Vague interruption dates ("申报前", "2025年前")
- Time-barred debt with specific confirmation amount (should be【暂缓确认】)
- Delayed performance interest without judgment basis
- Court fees with delayed performance interest calculated

## Summary

### Quality Assurance Core Principles

1. **Date Verification is MANDATORY** - First step, non-negotiable
2. **Use Calculator for ALL Calculations** - Zero exceptions
3. **Period-Based LPR Selection** - >5 years requires 5y LPR review
4. **Specific Dates Always** - No vague time references
5. **Evidence-Based Decisions** - Every determination has proof
6. **Conservative Approach** - When in doubt, flag for review

### Critical Error Prevention Focus

**Top 3 High-Frequency Errors**:
1. **LPR term selection** for long-term debts (>5 years)
2. **Daily rate conversion** base errors
3. **Statute interruption** date vagueness

**Must-Check Items**:
- Bankruptcy date verification (pre-work)
- Interest stop date (= bankruptcy date - 1)
- LPR term for >5 year debts
- Penalty 4× LPR cap
- Specific interruption dates
- Calculator tool usage for ALL calculations
- 就低/就无 principle application

### Self-Check Before Submission

**Ask yourself**:
- Did I verify bankruptcy dates from config file?
- Did I use calculator for every calculation?
- Did I review LPR term for any debt >5 years?
- Are all my interruption dates specific with evidence?
- Did I generate calculation files?
- Did I apply就低/就无 principles?
- Would this analysis stand up to scrutiny?

**Remember**: Quality here = Quality throughout. Debt analysis is the critical technical backbone of the entire review process.
