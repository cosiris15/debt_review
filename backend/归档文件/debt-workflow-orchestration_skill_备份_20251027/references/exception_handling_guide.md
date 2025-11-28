# Exception Handling Guide

## Purpose

Comprehensive guide for handling exceptions, edge cases, and error scenarios in the three-agent debt review workflow. Provides resolution procedures, escalation criteria, and prevention strategies.

## Exception Handling Philosophy

**Core Principles**:
1. **Transparency**: Document all exceptions and resolution attempts
2. **No Guessing**: Never fabricate or assume missing information
3. **Conservative Approach**: When uncertain, favor safer conservative interpretation
4. **Escalation**: Know when to stop and seek clarification

## Part 1: Environment and Configuration Exceptions

### Exception 1.1: Environment Not Initialized

**Symptom**:
- `.processing_config.json` missing
- Standard directories not present
- Attempt to run agent before initialization

**Impact**: CRITICAL - Cannot proceed with any agent work

**Detection**:
```bash
# Check if environment initialized
ls -la 输出/第X批债权/[编号]-[债权人名称]/.processing_config.json
```

**Resolution Steps**:
1. **STOP all agent work immediately**
2. Verify batch number, creditor number, and creditor name
3. Run initialization script:
   ```bash
   python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
   ```
4. Verify initialization successful (check directories and config file)
5. Resume workflow from beginning (fact-checker stage)

**Prevention**:
- ALWAYS run initialization before first agent
- Check for .processing_config.json before calling any agent
- Document initialization completion

### Exception 1.2: project_config.ini Missing or Invalid

**Symptom**:
- Warning message during initialization: "项目配置文件不存在"
- `.processing_config.json` has empty bankruptcy dates
- Initialization script fails

**Impact**: CRITICAL - Cannot establish bankruptcy date context

**Resolution Steps**:
1. **STOP**: Do not proceed without valid project configuration
2. Locate or create `project_config.ini` at project root
3. Required structure:
   ```ini
   [项目基本信息]
   债务人名称 = [公司全称]
   项目代码 = GY2025

   [关键日期]
   破产受理日期 = YYYY-MM-DD
   停止计息日期 = YYYY-MM-DD
   ```
4. Populate bankruptcy dates from authoritative source (court documents)
5. Verify interest_stop_date = bankruptcy_date - 1 day
6. Re-run initialization script
7. Verify dates now present in `.processing_config.json`

**Prevention**:
- Verify project_config.ini exists before starting any batch
- Include project configuration setup in project kickoff checklist
- Document authoritative source for bankruptcy dates

### Exception 1.3: Date Inconsistencies Detected

**Symptom**:
- Different bankruptcy dates in .processing_config.json vs fact-checker report
- Different dates in fact-checker report vs analyzer report
- Interest stop date ≠ bankruptcy date - 1

**Impact**: CRITICAL - Invalid calculations and analysis

**Resolution Steps**:
1. **STOP all work immediately** - do not proceed to next stage
2. Identify authoritative source:
   - Primary: Court acceptance document (受理裁定书)
   - Secondary: project_config.ini
   - Verify: .processing_config.json should match project_config.ini
3. Trace the error source:
   - If project_config.ini wrong: Correct it from court documents
   - If .processing_config.json wrong: Re-run initialization
   - If agent report wrong: Re-run the agent
4. Verify correction across all sources
5. Re-run affected agents with correct dates
6. **NEVER deliver reports with date inconsistencies**

**Prevention**:
- Triple-verify dates: config file → fact report → analysis report
- Mandatory date cross-check at each checkpoint
- Flag date as "lifeline-level critical" in all training

### Exception 1.4: Path/Permission Errors

**Symptom**:
- "Permission denied" errors when creating files
- "No such file or directory" errors
- Files saved to unexpected locations

**Impact**: MEDIUM - Work lost or misfiled

**Resolution Steps**:
1. Verify current working directory: `pwd`
2. Check directory permissions: `ls -la 输出/`
3. Verify paths in .processing_config.json are absolute (not relative)
4. If permission issue:
   ```bash
   chmod u+w [directory]
   ```
5. If path issue: Use absolute paths from configuration
6. Regenerate affected files in correct locations
7. Clean up any files saved to wrong locations

**Prevention**:
- Always use absolute paths from .processing_config.json
- Verify directory writable before saving files
- Never use relative paths or hardcoded paths

## Part 2: Material and Evidence Exceptions

### Exception 2.1: Incomplete Materials

**Symptom**:
- Declaration mentions evidence not provided
- Key documents referenced but missing
- Evidence list incomplete

**Impact**: MEDIUM - May affect completeness of analysis

**Resolution Steps**:
1. **Do NOT fabricate or guess** missing information
2. Document specific missing items:
   - List expected but not provided
   - Impact on fact-finding noted
3. Process available materials only
4. In fact-checker report:
   - Section: "材料完整性说明"
   - List missing items explicitly
   - Note: "以下材料申报人提及但未提供..."
5. In analyzer report:
   - Note limitations: "基于现有材料..."
   - If missing material affects key calculations: Mark as "暂缓确认"
6. In final report:
   - Clearly state material limitations
   - Conclusion qualified appropriately

**Prevention**:
- Material checklist before starting processing
- Early communication with creditor if key materials missing
- Clear documentation of provided vs. required materials

### Exception 2.2: Super-Long Materials (>100 pages or >50 evidence items)

**Symptom**:
- Material file very large
- Many evidence attachments
- System context window warning
- Processing timeout or memory issues

**Impact**: MEDIUM - Risk of incomplete processing or errors

**Resolution Steps**:
1. **Activate batch processing mechanism** (fact-checker specific)
2. Assess material volume:
   - Count contracts, invoices, bank records, judgments
   - Estimate total pages
3. Design batch strategy:
   - **Batch 1**: Core contracts and direct performance evidence (foundation)
   - **Batch 2**: High-volume履约凭证 (invoices, bank records, delivery slips)
   - **Batch 3**: Legal documents and summary materials (judgments, mediation, reconciliation)
4. Process each batch:
   - Maintain evidence cross-references
   - Keep related evidence together
   - Generate intermediate results
5. Consolidate batches:
   - Merge timelines chronologically
   - Integrate evidence relationships
   - Produce single unified report (no trace of batching in final output)
6. Verify completeness:
   - All evidence items processed
   - No duplication or omission
   - Unified narrative coherent

**Prevention**:
- Early material volume assessment
- Batch processing trigger clear (>100 pages or >50 items)
- Practice batch processing for large-scale creditors

### Exception 2.3: Contradictory Evidence

**Symptom**:
- Contract says one thing, judgment says another
- Reconciliation statement conflicts with payment records
- Multiple versions of same contract with different terms

**Impact**: MEDIUM - Affects fact determination

**Resolution Steps**:
1. **Apply evidence hierarchy**:
   - Level 1 (Highest): Effective legal documents (判决书, 调解书, 仲裁裁决)
   - Level 2: Bilateral confirmations (结算单, 对账单 with debtor signature)
   - Level 3: Contracts and amendments
   - Level 4 (Lowest): Unilateral evidence (invoices, internal records)
2. In fact-checker report:
   - Document the contradiction explicitly
   - Cite evidence hierarchy principle
   - State which evidence controls
   - Explain reasoning
3. If contradiction cannot be resolved using hierarchy:
   - Mark as "need clarification"
   - List alternative interpretations
   - Recommend conservative approach
   - Escalate if impact is significant

**Prevention**:
- Train on evidence hierarchy application
- Document evidence conflicts systematically
- Apply "substance over form" principle

### Exception 2.4: Evidence in Foreign Language

**Symptom**:
- Contracts or documents in English or other foreign languages
- No translation provided
- Partial translation only

**Impact**: MEDIUM - May limit analysis depth

**Resolution Steps**:
1. **If you can understand the foreign language**: Proceed with analysis, note source language
2. **If translation provided**: Use translation, note it as creditor's translation
3. **If no translation**:
   - Identify key sections needed for analysis
   - If critical terms unclear: Note limitation
   - If affects core amounts or deadlines: Mark for client follow-up
4. In reports:
   - Note evidence language
   - If translation used: Cite as such
   - If interpretation uncertain: Flag for verification

**Prevention**:
- Request translations early in material submission
- Identify key foreign-language terms that need translation
- Have reference materials for common legal terms in English/Chinese

## Part 3: Calculation and Technical Exceptions

### Exception 3.1: Calculator Tool Error

**Symptom**:
- universal_debt_calculator_cli.py fails to run
- Error messages from calculator
- Unexpected output format
- Tool returns invalid results

**Impact**: HIGH - Cannot proceed without valid calculations

**Resolution Steps**:
1. **Verify command syntax**:
   ```bash
   python universal_debt_calculator_cli.py <mode> --help
   ```
2. **Check input parameters**:
   - Principal: Positive number, reasonable magnitude
   - Start date: YYYY-MM-DD format, valid date
   - End date: YYYY-MM-DD format, after start date
   - Rate: Appropriate for mode (annual % for simple, multiplier for LPR)
   - Mode: One of {simple, lpr, delay, compound, penalty}
3. **Common parameter errors**:
   - Wrong date format (e.g., MM-DD-YYYY instead of YYYY-MM-DD)
   - End date before start date
   - Negative principal
   - Rate as decimal instead of percentage (4.35 not 0.0435)
4. **Retry with corrected parameters**
5. **If tool persists in error**:
   - Document exact command and error message
   - Check tool version and Python version
   - Test with simple known case
   - If tool fundamentally broken: **STOP and escalate** (do NOT use manual calculations)

**Prevention**:
- Test calculator tool at project start
- Maintain reference test cases
- Document exact command syntax for each mode
- Keep calculator tool script backed up

### Exception 3.2: Calculation Result Seems Unreasonable

**Symptom**:
- Interest exceeds principal significantly
- Result is negative
- Result wildly different from declared amount

**Impact**: MEDIUM - May indicate input error

**Resolution Steps**:
1. **Verify input parameters** (most common cause):
   - Principal amount correct from evidence
   - Start date is actual obligation start (not contract signing date)
   - End date is interest_stop_date (not today, not bankruptcy date)
   - Rate matches contract terms (check units: annual vs. monthly vs. daily)
2. **Check calculation period**:
   - Is period reasonable? (e.g., 10 years might be correct for old debt)
   - Any payment offsets applied?
3. **Review LPR term selection** (if LPR mode):
   - Long-term debt may need 5-year+ LPR
   - Check if using 1-year LPR for 10-year debt
4. **Compare with declared amount**:
   - If calculation >> declaration: Check if creditor applied offsets or caps
   - Document difference and reasoning
5. **Apply 就低原则** if calculation > declaration
6. **If truly unreasonable**: Double-check with second calculation, review evidence

**Prevention**:
- Sanity-check all calculation results
- Compare with declaration as cross-check
- Document reasoning for large differences

### Exception 3.3: Multiple Calculation Bases (Payment Offsets)

**Symptom**:
- Creditor made partial payments during performance
- Multiple tranches of principal with different start dates
- Unclear which payments offset which obligations

**Impact**: MEDIUM - Complex calculation required

**Resolution Steps**:
1. **Establish timeline**:
   - List all principal amounts with due dates
   - List all payments with dates and amounts
2. **Apply offset rules** (see references/calculation_formulas_reference.md):
   - Payments offset: first costs, then interest, then principal
   - If multiple principal tranches: offset earliest due first
3. **Use calculator for each segment**:
   - Calculate interest on each principal segment from due date to payment date
   - Recalculate on reduced principal after payment
4. **Document process**:
   - Segmentation table in report
   - Multiple calculator commands for each segment
   - Aggregate results
5. **Verify total** against declared amount

**Prevention**:
- Identify payment offsets early in fact-checking
- Use detailed timeline table
- Reference offset rules explicitly

### Exception 3.4: Compound Interest Calculation Required

**Symptom**:
- Contract specifies "利滚利" or compound interest
- Interest accrual on interest explicitly agreed

**Impact**: MEDIUM - Requires explicit contractual basis

**Resolution Steps**:
1. **Verify contractual basis** (MANDATORY):
   - Compound interest MUST have explicit contract clause
   - If no explicit clause: Reject compound interest, use simple interest
2. **If valid compound interest clause**:
   - Identify compounding cycle (monthly, quarterly, yearly)
   - Use calculator compound mode:
     ```bash
     python universal_debt_calculator_cli.py compound --principal [X] --start-date [Y] --end-date [Z] --rate [R] --cycle "[月末/季末/年末]"
     ```
3. **Apply penalty caps** even to compound interest
4. **Document**:
   - Contract clause justifying compound interest
   - Compounding cycle
   - Calculation command
   - Cap application if needed

**Prevention**:
- Flag compound interest requirements during fact-checking
- Never assume compound interest without contract basis
- Document contract clause explicitly

## Part 4: Statute and Legal Exceptions

### Exception 4.1: Vague or Missing Interruption Dates

**Symptom**:
- Creditor claims "申报前催收" without specific date
- Demand letter exists but undated or delivery date unclear
- Acknowledgment letter signed but no date

**Impact**: MEDIUM - Affects statute determination

**Resolution Steps**:
1. **Search for specific dates**:
   - Check document date stamps
   - Check envelopes for postmarks
   - Check email timestamps
   - Check delivery receipts
2. **If date determinable**: Use specific date
3. **If date range known**: Use conservative date (earlier in range)
4. **If no date determinable**:
   - **Do NOT assume** interruption occurred
   - Note in report: "声称的中断事件无法确认具体日期"
   - Perform statute analysis assuming no interruption
   - Mark conclusion as "基于现有证据..."
5. **Never use vague temporal references**: Reject "申报前", "受理前", "大约XX年" without evidence

**Prevention**:
- Require specific dates for all interruption claims
- Evidence must support date
- Escalate vague claims during material review

### Exception 4.2: Statute Transition Period Ambiguity

**Symptom**:
- Obligation started before Oct 1, 2017
- Performance deadline crossed Oct 1, 2017
- Unclear whether 2-year or 3-year statute applies

**Impact**: MEDIUM - Determines time-bar conclusion

**Resolution Steps**:
1. **Apply transition rule** (from legal_standards_reference.md):
   - **Key date**: October 1, 2017 (new Civil Code effective)
   - **If statute began before Oct 1, 2017**: Use 2-year limitation
   - **If statute began on/after Oct 1, 2017**: Use 3-year limitation
2. **Determine statute start date**:
   - Contract debt: Day after performance deadline
   - Installment debt: Day after each installment due
   - Judgment debt: N/A (execution statute applies instead)
3. **Calculate from correct start with correct period**
4. **Document reasoning** in report

**Prevention**:
- Clear transition rule reference
- Always determine statute start date explicitly
- Document which period (2y or 3y) applies and why

### Exception 4.3: Execution Statute vs. Litigation Statute Confusion

**Symptom**:
- Judgment debt analyzed using litigation statute
- Contract debt analyzed using execution statute
- Mixed up 2-year execution period with 3-year litigation period

**Impact**: HIGH - Wrong statute type applied

**Resolution Steps**:
1. **Distinguish debt basis**:
   - **Judgment/mediation/arbitration**: Execution statute applies (固定2年)
   - **Contract/tort (no judgment)**: Litigation statute applies (2年或3年 depending on transition)
2. **For judgment debts**:
   - Analyze execution statute only
   - Start from judgment effective date
   - Period is 2 years (NOT 3, regardless of transition rule)
3. **For contract debts**:
   - Analyze litigation statute only
   - Start from day after performance deadline
   - Apply transition rule (2y vs 3y)
4. **Correct the analysis** if wrong statute type used

**Prevention**:
- Clear debt type classification in fact-checking
- Analyst checks debt basis before statute analysis
- Reference guides distinguish the two statute types

### Exception 4.4: Statute Conclusion Affects Confirmation

**Symptom**:
- Statute analysis concludes debt is time-barred
- Uncertain how to reflect in confirmation

**Impact**: MEDIUM - Affects final recommendation

**Resolution Steps**:
1. **Understand time-bar effect**:
   - Time-barred ≠ debt ceases to exist
   - Time-barred = loss of litigation protection
   - In bankruptcy: May affect confirmation or classification
2. **In analysis report**:
   - Clear statement: "该债权已过诉讼时效"
   - Explain: Creditor lost right to compel payment through litigation
3. **In confirmation**:
   - **Option A** (conservative): Mark as "暂缓确认" pending client policy
   - **Option B** (if client policy clear): Confirm as subordinated or reject
   - **Document basis** for approach chosen
4. **Escalate if unclear**: Client's policy on time-barred claims may vary

**Prevention**:
- Clarify client policy on time-barred claims at project start
- Document policy in standards
- Consistent application across all creditors

## Part 5: Workflow and Agent Exceptions

### Exception 5.1: Agent Output File Missing

**Symptom**:
- Expected report file not found in designated directory
- Agent claims to have generated file but file absent
- File generated but in wrong location

**Impact**: HIGH - Cannot proceed to next stage

**Resolution Steps**:
1. **Verify expected location and filename**:
   - Check `.processing_config.json` for correct path and filename template
   - Example: `{paths.work_papers}/{file_templates.fact_check_report}`
2. **Search for misplaced file**:
   ```bash
   find 输出/ -name "*{债权人名称}*事实核查报告*"
   ```
3. **If file found in wrong location**:
   - Move to correct location:
     ```bash
     mv [wrong_path] [correct_path]
     ```
   - Verify file integrity (not corrupted)
4. **If file truly missing**:
   - **Re-run the agent** that should have generated it
   - Verify agent completes successfully
   - Verify file now exists in correct location
5. **DO NOT proceed to next stage** without required input file

**Prevention**:
- Agents use absolute paths from configuration
- Verify file saved successfully after write
- Checkpoint file existence before proceeding

### Exception 5.2: Agent Workflow Out of Sequence

**Symptom**:
- Analyzer called before fact-checker completes
- Organizer called before analyzer completes
- Multiple agents running in parallel

**Impact**: HIGH - Invalid workflow, compromised quality

**Resolution Steps**:
1. **STOP immediately**
2. **Identify correct sequence**:
   - Stage 1: debt-fact-checker (must complete first)
   - Stage 2: debt-claim-analyzer (requires fact-checker output)
   - Stage 3: report-organizer (requires both technical reports)
3. **Verify fact-checker completion**:
   - Report exists in 工作底稿/
   - Report complete and valid
4. **If analyzer already ran without fact-checker**:
   - Discard analyzer output
   - Run fact-checker first
   - Then re-run analyzer
5. **Enforce sequential processing** going forward

**Prevention**:
- Main controller enforces sequence
- Each agent verifies prerequisite outputs exist
- Clear workflow diagram and checklist

### Exception 5.3: Batch Processing Attempted (Multiple Creditors in Parallel)

**Symptom**:
- Multiple creditors being processed simultaneously
- Attempt to run all fact-checking first, then all analysis
- Cross-creditor file confusion

**Impact**: HIGH - Violates sequential processing standard, quality at risk

**Resolution Steps**:
1. **STOP batch processing immediately**
2. **Identify completed vs. in-progress creditors**:
   - Completed: All three reports generated and verified
   - In-progress: Partially complete
   - Not started: No reports yet
3. **For in-progress creditors**:
   - Complete current creditor fully (through all three stages)
   - Verify outputs before starting next creditor
4. **Adopt serial processing**:
   - Creditor 1: Initialize → fact-check → analyze → organize → verify → complete
   - Creditor 2: Initialize → fact-check → analyze → organize → verify → complete
   - ...

**Prevention**:
- Clear SOP: Serial processing mandatory
- Main controller enforces one-at-a-time
- Training on why serial processing required (quality, traceability)

### Exception 5.4: Report Content Contradictions Between Stages

**Symptom**:
- Analyzer report contradicts fact-checker report
- Final report has different amounts than analysis report
- Legal relationship type changes between stages

**Impact**: HIGH - Consistency error, credibility issue

**Resolution Steps**:
1. **Identify the contradiction**:
   - Specific fact or conclusion that differs
   - Which two reports contradict
2. **Determine authoritative source**:
   - Fact-finding: Fact-checker is authoritative (unless new evidence found)
   - Calculations: Analyzer is authoritative
   - Consolidation: Should match technical reports exactly
3. **Trace the error**:
   - Review evidence basis
   - Check if misunderstanding vs. new interpretation
4. **Correct the erroneous report**:
   - If fact-checker wrong: Re-run with correct facts
   - If analyzer misunderstood facts: Re-run analyzer
   - If organizer transcribed incorrectly: Re-run organizer
5. **Verify consistency after correction**

**Prevention**:
- Analyzer cross-checks with fact-checker report
- Organizer preserves technical reports accurately
- Checkpoints verify consistency

## Part 6: Escalation Criteria

### When to Stop and Escalate

**STOP and escalate to human supervisor** if:

**Critical Date Issues**:
- Bankruptcy date cannot be determined from available sources
- Fundamental contradiction in bankruptcy dates across authoritative sources
- Interest stop date calculation unclear due to special circumstances

**Fundamental Evidence Issues**:
- Core evidence appears forged or fraudulent
- Evidence directly contradicts other evidence at same hierarchy level
- Evidence is in language you cannot understand and affects critical conclusions

**Legal Interpretation Ambiguities**:
- Statute determination unclear even after applying standards
- Novel legal relationship type not covered in classification system
- Legal principle application unclear or conflicting

**Technical Tool Failures**:
- Calculator tool fundamentally broken and cannot be fixed
- Calculation required beyond tool's capabilities
- Technical infrastructure issues preventing work completion

**Workflow Conflicts**:
- Agent work standards contradict on critical point
- Client policy unclear on key decision
- SOP does not cover the specific scenario encountered

### Escalation Documentation

**When escalating, provide**:
1. **Issue Description**: Specific problem encountered
2. **Context**: Creditor, batch, workflow stage
3. **Resolution Attempts**: Steps taken to resolve
4. **References Consulted**: Which standards/references checked
5. **Alternative Interpretations**: If applicable
6. **Impact Assessment**: How it affects conclusions
7. **Recommendation**: Suggested resolution path

### Escalation Response

**After escalation**:
1. Document supervisor guidance received
2. Apply guidance to current creditor
3. Update standards if applicable to future creditors
4. Note exception handling in final report if relevant

## Part 7: Exception Prevention Strategies

### Proactive Measures

**At Project Start**:
- Verify all infrastructure (tools, configurations, access)
- Clarify client policies on edge cases
- Update standards with lessons learned from prior projects

**At Batch Start**:
- Review materials for common issues
- Identify high-risk creditors (complex, incomplete materials)
- Plan for anticipated exceptions

**During Processing**:
- Early detection through checkpoints
- Document exceptions as they arise
- Share learnings across team

### Exception Tracking

**Maintain exception log**:
- Creditor identifier
- Exception type
- Resolution steps
- Time to resolve
- Prevention notes

**Review periodically**:
- Identify patterns
- Update standards
- Improve training

## Part 8: Common Exception Scenarios Quick Reference

| Exception | Impact | First Step | Can Proceed? |
|-----------|--------|------------|-------------|
| Environment not initialized | Critical | Run initialization script | No - must initialize first |
| Bankruptcy date wrong | Critical | Verify from court documents, correct config | No - must fix dates first |
| Materials incomplete | Medium | Document missing items | Yes - process available materials |
| Calculator tool error | High | Verify command syntax | No - must fix tool first |
| Vague statute interruption date | Medium | Search for specific date evidence | Yes - analyze conservatively |
| Agent output missing | High | Search for file, re-run agent if needed | No - must have prerequisite outputs |
| Batch processing attempted | High | Stop, adopt serial processing | No - complete current creditor first |
| Evidence contradictory | Medium | Apply evidence hierarchy | Yes - with documented reasoning |

## Summary

Effective exception handling:
- **Transparent**: Document all exceptions and resolutions
- **Systematic**: Follow established procedures
- **Conservative**: When uncertain, favor safer approach
- **Escalate**: Know when to seek guidance

**Golden Rules**:
- Never guess or fabricate information
- Never proceed with unresolved critical issues (dates, calculations)
- Always document exception handling in reports
- Learn from exceptions to prevent recurrence

**Remember**: Exceptions are opportunities to strengthen the process. Proper handling builds confidence and credibility. Hasty improvisation introduces risk.
