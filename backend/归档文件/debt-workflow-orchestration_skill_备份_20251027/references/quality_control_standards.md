# Quality Control Standards

## Purpose

Comprehensive quality control checkpoints, verification procedures, and quality assurance standards for three-agent debt review workflow.

## Quality Control Philosophy

**Core Principle**: Quality over speed - systematic verification at each stage prevents compounding errors

**Zero-Tolerance Items**: Certain errors invalidate entire workflow and cannot be accepted
**Quality Gates**: Each checkpoint must pass before proceeding to next stage

## Part 1: Universal Quality Standards

### Date Verification Protocol (ALL Agents)

**⚠️ MANDATORY for EVERY agent at EVERY stage**

```
□ Pre-Work Date Verification:
  □ Read bankruptcy date from .processing_config.json
  □ Read interest stop date from .processing_config.json
  □ Verify interest_stop_date = bankruptcy_date - 1 day
  □ Record dates explicitly in output report

□ Cross-Verification (if prior reports exist):
  □ Compare dates with previous agent's report
  □ Flag any inconsistency immediately
  □ STOP work if dates do not match

□ Date Usage Verification:
  □ All calculations use correct stop date
  □ All time comparisons use correct reference date
  □ Timeline events correctly sequenced relative to bankruptcy date
```

**Why Critical**: Wrong dates invalidate all legal analysis, calculations, and conclusions. A single date error can mislead client decisions affecting millions in claims.

### Output File Management Standards

```
□ File Naming:
  □ Follows exact template from .processing_config.json
  □ No typos in creditor name
  □ Date format correct (YYYYMMDD where applicable)

□ File Location:
  □ Saved to correct subdirectory (工作底稿/, 最终报告/, 计算文件/)
  □ Never scattered in wrong locations
  □ Absolute paths used (not relative)

□ File Completeness:
  □ All required sections present
  □ No placeholder text remaining
  □ Evidence citations complete
  □ Calculations documented
```

### Evidence Citation Standards

```
□ Source Identification:
  □ Every fact cites specific evidence source
  □ Page numbers or document names provided
  □ Evidence type classified (contract, invoice, judgment, etc.)

□ Evidence Hierarchy:
  □ Conflicts resolved using hierarchy (judgment > confirmation > contract > unilateral)
  □ Higher-level evidence supersedes lower-level when contradictory

□ Evidence vs. Declaration Distinction:
  □ Evidence materials (contracts, judgments) clearly separated from declaration materials
  □ No confusion between creditor's claims and actual evidence
```

## Part 2: Checkpoint 1 - After Fact-Checker

### Date Verification (Fact-Checker Specific)

```
□ Configuration Date Reading:
  □ Bankruptcy date read from .processing_config.json
  □ Interest stop date read from .processing_config.json
  □ Both dates recorded in fact-checker report header

□ Timeline Context:
  □ All timeline events dated relative to bankruptcy date
  □ Events clearly marked as "before bankruptcy" or "after bankruptcy"
  □ Performance obligations evaluated against bankruptcy date
```

### Declaration Information Quality

```
□ Creditor Information:
  □ Full legal name (统一社会信用代码 if available)
  □ Contact information complete
  □ Declaration date recorded

□ Declared Amounts:
  □ Total declared amount accurate
  □ Breakdown by category (principal, interest, penalty, costs)
  □ Each category amount verifiable
  □ Currency specified (assumed RMB if not specified)

□ Debt Classification:
  □ Creditor's claimed classification recorded (secured/ordinary/subordinated)
  □ Basis for classification noted
  □ No premature judgment on classification validity
```

### Fact-Finding Quality

```
□ Legal Relationship Identification:
  □ Basic debt relationship type determined (loan, sales, service, etc.)
  □ Basis clearly documented (contract type, judgment description)
  □ Multiple relationships identified if applicable

□ Timeline Completeness:
  □ All key events captured:
    - Contract signing
    - Performance/payment dates
    - Default/breach dates
    - Demand/acknowledgment dates
    - Litigation dates (if applicable)
  □ Events chronologically ordered
  □ No temporal logic errors (effect before cause)

□ Contract Terms Recording:
  □ For each contract relationship, key terms documented:
    - Subject matter
    - Amount/price
    - Performance period
    - Payment terms
    - Interest/penalty terms
    - Breach consequences
  □ Clause locations cited (Article X, Section Y)
  □ No paraphrasing that changes meaning
```

### Evidence Analysis Quality

```
□ Evidence Completeness Check:
  □ Evidence materials list complete
  □ Evidence types categorized
  □ Missing evidence identified explicitly

□ Evidence Relationships:
  □ Contracts to performance evidence mapped
  □ Payment records to obligations linked
  □ Judgment to underlying relationship connected

□ Evidence Hierarchy Applied:
  □ Conflicts between evidence items noted
  □ Higher-hierarchy evidence identified
  □ Resolution explained
```

### Fact-Checker Report Structure

```
□ Required Sections Present:
  □ 申报情况表 (Declaration Information)
  □ 形式性文件核查 (Formal Document Review)
  □ 债权发生情况查明 (Debt Relationship Fact-Finding)
  □ 法律关系地位识别 (Legal Relationship Identification)
  □ 基础债权关系类型判断 (Basic Debt Type Classification)
  □ 证据关系综合分析 (Evidence Relationship Analysis)
  □ 移交说明 (Handover Notes to Analyzer)

□ Section Quality:
  □ Each section complete (no "TBD" or placeholders)
  □ Logical flow maintained
  □ Cross-references accurate
```

### Critical Errors to Catch

**STOP and re-work if any of these present**:
- ❌ Bankruptcy date missing or incorrect
- ❌ Declaration amount breakdown missing or doesn't sum correctly
- ❌ Timeline events out of chronological order
- ❌ Evidence citations missing for key facts
- ❌ Legal relationship type unidentified or vague
- ❌ Contract terms not documented (for contract relationships)

## Part 3: Checkpoint 2 - After Debt Analyzer

### Date Verification (Analyzer Specific)

```
□ Configuration Date Reading:
  □ Bankruptcy date re-read from .processing_config.json
  □ Interest stop date re-read from .processing_config.json

□ Cross-Report Verification:
  □ Dates compared with fact-checker report
  □ Any discrepancy flagged and resolved
  □ Consistent dates documented in analysis report

□ Calculation Date Application:
  □ All interest calculations end on interest_stop_date
  □ No calculations extend past bankruptcy date
  □ Statute analysis uses bankruptcy date as reference
```

### Amount Analysis Quality

```
□ Declaration Breakdown:
  □ Declared amounts decomposed by legal basis
  □ Each amount item has specific source (contract clause, judgment paragraph)
  □ "实质重于形式" applied (substance over creditor's labels)

□ Principal Items:
  □ Core payment obligations identified
  □ Multiple tranches separated if applicable
  □ Offsets/payments deducted properly

□ Interest Items:
  □ Loan interest vs. overdue interest distinguished
  □ Penalty amounts identified separately
  □ Delayed performance interest separated if applicable
  □ Each interest type has legal basis cited
```

### Calculator Tool Usage Verification

```
□ Tool Invocation:
  □ universal_debt_calculator_cli.py used for ALL calculations
  □ NO manual calculations accepted
  □ Complete commands documented in report

□ Command Parameters:
  □ Principal amounts correct
  □ Start dates accurate (performance due date, judgment effective date, etc.)
  □ End dates correct (interest_stop_date)
  □ Rate parameters appropriate (annual rate, LPR multiplier, etc.)
  □ Mode selection correct (simple, lpr, delay, compound, penalty)

□ LPR Term Selection (if LPR mode):
  □ Debt period calculated (from obligation start to interest stop)
  □ If debt period ≤ 5 years: 1-year LPR used
  □ If debt period > 5 years: 5-year+ LPR considered and justified
  □ Selection documented in report

□ Output Files:
  □ Excel/CSV calculation file generated
  □ File saved in 计算文件/ directory
  □ Filename follows template
  □ File contains complete process table
```

### Calculation Accuracy Verification

```
□ Input Validation:
  □ Principal matches evidence-supported amount
  □ Start date matches performance deadline or judgment effective date
  □ End date is interest_stop_date (not bankruptcy date itself)
  □ Rate matches contract/law (caps applied if needed)

□ Process File Review:
  □ Calculation steps transparent
  □ Intermediate results logical
  □ Daily/monthly breakdown present (if applicable)
  □ Rounding consistent and appropriate

□ Result Verification:
  □ Final amount reasonable (sanity check)
  □ Compared with declared amount
  □ 就低原则 applied if calculation > declaration
```

### Penalty Cap Verification

```
□ Penalty Identification:
  □ All penalty items identified (违约金, 罚息, etc.)
  □ Contractual rates extracted

□ LPR Cap Application:
  □ 4× LPR cap rate determined
  □ Penalty rate compared to cap
  □ Excess portion calculated if applicable
  □ Excess classified as subordinated debt

□ Documentation:
  □ Cap calculation shown
  □ Adjustment explained if applied
  □ Classification result documented
```

### Statute of Limitations Analysis

```
□ Obligation Start Date:
  □ Performance deadline identified from contract/judgment
  □ Start date of statute period determined

□ Interruption Events:
  □ All interruption events identified:
    - Demand letters (with delivery evidence)
    - Debt acknowledgments (signed by debtor)
    - Lawsuit filings
  □ Each event dated specifically (not "申报前")
  □ Evidence for each event cited

□ Statute Periods Applied:
  □ Transition rule applied correctly (2-year vs 3-year based on Oct 1, 2017)
  □ Calculation from each interruption shown
  □ Final determination as of bankruptcy date

□ Conclusion:
  □ Clear statement: within limitations or time-barred
  □ Reasoning explained
  □ Impact on confirmation stated
```

### Execution Statute Analysis (if applicable)

```
□ Applicability Check:
  □ Only for debts based on judgment/mediation/arbitration
  □ Non-judgment debts skip this section

□ Judgment Effective Date:
  □ Date identified from legal document
  □ Execution application window determined (2 years from effective date)

□ Execution Status:
  □ Application filed or not
  □ Interruption events (if any)
  □ Status as of bankruptcy date

□ Conclusion:
  □ Within execution statute or expired
  □ Impact on confirmation
```

### Report Completeness

```
□ Required Sections:
  □ 债权基础法律关系分析 (Legal Relationship Analysis)
  □ 金额项目拆解清单 (Amount Breakdown)
  □ 履行期限判断表 (Performance Deadline Determination)
  □ 利息计算过程 (Interest Calculation Process with commands)
  □ 诉讼时效分析 (Statute of Limitations Analysis)
  □ 执行时效分析 (Execution Statute Analysis, if applicable)
  □ 审查确认情况 (Review Confirmation Summary)
  □ 审查结论 (Review Conclusion)

□ File Outputs:
  □ Analysis report in 工作底稿/
  □ Calculation files in 计算文件/ (or explanation TXT if no calculations)
  □ All files properly named
```

### Critical Errors to Catch

**STOP and re-work if any of these present**:
- ❌ Dates inconsistent with fact-checker report
- ❌ Manual calculations used (no calculator tool)
- ❌ LPR term selection not justified for long-term debts
- ❌ Calculation files missing for calculation items
- ❌ Penalty caps not applied when contractual rate > 4× LPR
- ❌ Statute interruption dates vague ("申报前")
- ❌ 就低原则 not applied when calculation > declaration
- ❌ Items not declared by creditor included in confirmation (violates 就无原则)

## Part 4: Checkpoint 3 - After Report Organizer

### Date Verification (Organizer Specific)

```
□ Triple-Source Verification:
  □ Dates from .processing_config.json
  □ Dates from fact-checker report
  □ Dates from analyzer report
  □ ALL THREE SOURCES MUST MATCH

□ Final Report Date Accuracy:
  □ Bankruptcy date in final report correct
  □ Interest stop date referenced correctly
  □ Calculation cutoff dates consistent
```

### Content Consolidation Quality

```
□ Information Extraction:
  □ All key facts from fact-checker report captured
  □ All analysis conclusions from analyzer report captured
  □ No critical information omitted

□ Content Accuracy:
  □ No modifications to technical conclusions
  □ Amounts transcribed exactly
  □ Legal analysis preserved accurately
  □ Evidence citations retained

□ Logical Flow:
  □ Information reorganized according to template
  □ Narrative flows coherently
  □ Cross-references valid
```

### Template Compliance

```
□ Template Structure:
  □ Client template correctly identified and loaded
  □ All required sections present
  □ Section order matches template
  □ Formatting consistent with template style

□ Language Standards:
  □ Professional legal language
  □ Complete sentences (not bullet points, except where template allows)
  □ Terminology consistent with client preferences
  □ Chinese legal terms used appropriately
```

### Report Formatting

```
□ Amount Formatting:
  □ Numbers use Arabic numerals
  □ Two decimal places for currency (e.g., 100,000.00元)
  □ Consistent thousand separators if used

□ Date Formatting:
  □ Format: YYYY年MM月DD日
  □ Consistency throughout document

□ Entity Names:
  □ Full names on first mention
  □ Abbreviations defined and used consistently
  □ Legal document citations complete (full case numbers)
```

### File Organization Quality

```
□ Final Report:
  □ Saved in 最终报告/ directory
  □ Filename: GY2025_{债权人名称}_债权审查报告_{YYYYMMDD}.md
  □ Date in filename matches processing date

□ File Inventory:
  □ 文件清单.md created in base directory
  □ Lists all files across all three directories
  □ File sizes and dates included
  □ Purpose of each file explained

□ Directory Integrity:
  □ No files in wrong directories
  □ No orphan files
  □ All referenced files exist
```

### Critical Errors to Catch

**STOP and re-work if any of these present**:
- ❌ Dates inconsistent across three reports
- ❌ Technical conclusions modified or misrepresented
- ❌ Amounts transcription errors
- ❌ Template structure not followed
- ❌ Final report in wrong directory
- ❌ File inventory missing or incomplete

## Part 5: Aggregate Quality Metrics

### Completeness Metrics

For each creditor, verify:
```
□ Three reports generated (fact-checker, analyzer, final)
□ All required sections in each report
□ Calculation files present (or explanation if none)
□ File inventory complete
```

### Consistency Metrics

Across all three reports, verify:
```
□ Dates identical
□ Creditor name consistent
□ Declared amounts identical
□ Legal relationship type consistent
□ Conclusion amounts traceable from declaration through analysis to final
```

### Evidence Traceability

For any conclusion, verify:
```
□ Traceable to analyzer report
□ Traceable to fact-checker report
□ Traceable to original evidence
□ Chain of reasoning clear
```

## Part 6: Common Quality Issues and Prevention

### Issue 1: Date Propagation Errors

**Symptom**: Different dates in different reports

**Prevention**:
- ALWAYS read from .processing_config.json (never from memory)
- Cross-verify with previous reports
- Document dates in every report header

### Issue 2: Calculation Without Tool

**Symptom**: Interest amounts with no calculator command documented

**Prevention**:
- Enforce mandatory calculator usage
- Require command documentation
- Verify calculation files exist

### Issue 3: LPR Term Selection Errors

**Symptom**: 1-year LPR used for 10-year debt without justification

**Prevention**:
- Calculate total debt period explicitly
- Document LPR term selection reasoning
- Flag long-term debts for special review

### Issue 4: Vague Statute Interruption Dates

**Symptom**: "申报前" instead of specific date

**Prevention**:
- Require specific dates for all interruption events
- Require evidence citation for each interruption
- Reject vague temporal references

### Issue 5: 就低原则 Not Applied

**Symptom**: Confirmation > declaration when calculation > declaration

**Prevention**:
- Explicit comparison of calculation vs declaration
- Document application of 就低原则
- Final amounts never exceed declaration

### Issue 6: File Location Errors

**Symptom**: Reports scattered across directories

**Prevention**:
- Use absolute paths from configuration
- Verify file location after each write
- Cross-check against configuration templates

## Part 7: Quality Control Workflow

### Sequential Quality Gates

```
Gate 1: After Initialization
  → Verify environment before any agent work

Gate 2: After Fact-Checker
  → Verify fact report before analyzer starts

Gate 3: After Analyzer
  → Verify analysis and calculations before organizer starts

Gate 4: After Organizer
  → Verify final deliverable before marking complete
```

### Gate Passing Criteria

**Each gate must pass ALL checkpoints** before proceeding

**If gate fails**: STOP, identify issue, correct, re-verify

### Documentation of Quality Checks

For audit trail, document:
- Which checkpoints were verified
- Date/time of verification
- Any issues found and resolved
- Sign-off on quality approval

## Summary

Quality control is **non-negotiable** in debt review:
- Systematic verification at each stage
- Zero tolerance for date errors, manual calculations, file location errors
- Consistency and traceability throughout

**Quality Mindset**: "Measure twice, cut once" - thorough verification prevents costly rework and protects client interests.

**Remember**: Quality issues in debt review can have million-yuan consequences for clients. Time spent on quality control is an investment in accuracy and professional credibility.
