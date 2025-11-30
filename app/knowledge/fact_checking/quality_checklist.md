# Quality Control Checklist and Error Prevention

## Purpose

This guide consolidates quality control standards, error prevention measures, and timeline creation specifications to ensure high-quality fact-checking outputs.

## Part 1: Timeline Creation Standards

### Mandatory Format Requirements

#### Requirement 1: Use Complete Standardized Formats

**🚨 CRITICAL**: Timeline entries MUST use the complete formats from `evidence_and_facts_guide.md`, NOT simplified descriptions

**❌ WRONG**:
```
| 2 | 2023-01-15 | Signed purchase contract, amount 200万 |
```

**✅ RIGHT**:
```
| 2 | 2023-01-15 | 根据《购销合同》（合同编号：XY-2023-001，证据第3-8页）记载：XX公司（卖方)与YY公司（买方）于2023年1月15日签订了关于钢材的《购销合同》，核心约定如下：<br>1. 标的物：Q235B钢材500吨（见合同第2条）<br>2. 合同价款：总金额为人民币200万元（含税）（见合同第3条第1款）<br>[... all 9 core clauses ...] |
```

**Why**: Timeline is core output, must be detailed enough for independent review

#### Requirement 2: Mandatory Evidence Citations

**🚨 CRITICAL**: Every timeline entry MUST cite specific evidence source

**❌ WRONG**:
```
| 3 | 2023-02-05 | Debtor paid 60万 |
```

**✅ RIGHT**:
```
| 3 | 2023-02-05 | 根据银行转账凭证（证据第9页）显示：YY公司于2023年2月5日向XX公司支付60万元，交易流水号：ICBC20230205001234 |
```

**Citation Format**: "根据[证据类型]（证据第[X]页）显示/记载/确认..."

#### Requirement 3: No Repetition Shortcuts

**🚨 CRITICAL**: Each contract must include ALL 9 clauses, NEVER use "同上"

**❌ WRONG**:
```
| 5 | 2023-03-20 | 《购销合同#002》，条款同上，金额150万 |
```

**✅ RIGHT**:
```
| 5 | 2023-03-20 | 根据《购销合同#002》（合同编号：XY-2023-002，证据第15-20页）记载：...<br>1. 标的物：...<br>2. 合同价款：...<br>[... all 9 core clauses, fully written out ...] |
```

**Why**: Each entry must be independently understandable

### Timeline Construction Process

#### Step 1: Extract All Events with Dates

Go through ALL evidence and list every event with a date:
- Contract signings
- Deliveries (per delivery slip date)
- Payments (per bank transfer date)
- Invoice issuances
- Legal document dates
- Confirmation letter dates

#### Step 2: Sort Chronologically

Arrange all events by date, earliest to latest

**Same-day events**: Apply logical order
1. Contract signing
2. Performance (delivery, payment)
3. Breach/dispute
4. Legal resolution

#### Step 3: Apply Standardized Formats

For each event, apply the complete format from Part 2 of `evidence_and_facts_guide.md`:
- Contracts: 9-clause format
- Legal documents: Complete excerpt
- Invoices: Full invoice format
- Etc.

#### Step 4: Add Evidence Citations

Every entry must specify:
- Evidence type (e.g., 合同, 发票, 银行凭证)
- Evidence location (e.g., 证据第X-X页)

#### Step 5: Verify Completeness

Check that timeline includes:
- [ ] All contracts and supplements
- [ ] All legal documents
- [ ] Key performance evidence (major invoices, payments, deliveries)
- [ ] Confirmation/settlement documents
- [ ] No gaps in chronological flow

### Timeline Output Template

```markdown
## 三、债权发生情况查明

| 序号 | 日期 | 债权发生情况 |
|------|------|-------------|
| 1. | YYYY-MM-DD | [Complete standardized format with evidence citation] |
| 2. | YYYY-MM-DD | [Complete standardized format with evidence citation] |
| 3. | YYYY-MM-DD | [Complete standardized format with evidence citation] |
| ... | ... | ... |
```

## Part 2: Common Errors and Prevention

### Category 1: Declaration Extraction Errors

#### Error 1.1: Unauthorized Corrections

**Problem**: Modifying creditor's declared content

**Examples**:
- Creditor checked "劳动债权", you change to "普通债权"
- Creditor wrote "欠款", you change to "本金"
- Creditor put penalty under "其他", you move to "违约金"

**Prevention**:
- [ ] Copy declaration form EXACTLY
- [ ] Use creditor's ORIGINAL labels and categories
- [ ] Mark "[债权人未填写]" for blanks, don't fill in yourself
- [ ] Note discrepancies in remarks, don't "fix" them

#### Error 1.2: Merging Duplicate Entries

**Problem**: Creditor lists same item twice, you consolidate

**Example**: Creditor fills "利息5万" in both "利息" field and "其他" field, you record only once

**Prevention**:
- [ ] Record BOTH entries exactly as creditor filled
- [ ] Note in remarks: "债权人重复填写"
- [ ] Let debt analyst handle the duplication

#### Error 1.3: Calculating Unfilled Totals

**Problem**: Creditor leaves "合计" blank, you calculate and fill in

**Prevention**:
- [ ] If creditor left blank, mark "[债权人未填写]"
- [ ] Do NOT calculate totals yourself
- [ ] Record items + total exactly as creditor provided

### Category 2: Evidence Material Errors

#### Error 2.1: Mixing Declaration and Evidence

**Problem**: Using declaration form content as fact-finding basis

**Example**: "根据申报书，债权人于2023年交付货物" ← 申报书 is declaration, not evidence!

**Prevention**:
- [ ] Facts MUST be based on evidence (contracts, invoices, judgments)
- [ ] Declaration materials are THINKING CLUES only
- [ ] Every fact must cite objective evidence source

#### Error 2.2: Incomplete Contract Clauses

**Problem**: Summarizing contract instead of extracting all 9 clauses

**Example**: "双方签订采购合同，金额100万" ← Too brief!

**Prevention**:
- [ ] ALL contracts must include 9 core clauses
- [ ] Each clause must cite specific contract article (见合同第X条)
- [ ] Payment terms must be complete original wording
- [ ] Designated recipient must specify name/position

**Self-Check**: Can I reconstruct the contract relationship from this excerpt alone? If no, add more detail.

#### Error 2.3: Summarizing Legal Documents

**Problem**: Paraphrasing judgment instead of excerpting word-for-word

**Example**: "判决被告支付100万" ← Paraphrase!

**Prevention**:
- [ ] MUST excerpt ENTIRE "判决如下" section verbatim
- [ ] Use quotation marks for excerpted content
- [ ] Maintain original punctuation and formatting
- [ ] No omissions, no summarization

#### Error 2.4: Missing Settlement Documents

**Problem**: Failing to identify critical settlement/confirmation documents

**Example**: Not recognizing工程结算单 that confirms final project amount

**Prevention**:
- [ ] Search for keywords: "结算", "未支付", "应付", "确认"
- [ ] Highlight settlement documents in findings
- [ ] Note their superior effect over prior performance evidence

#### Error 2.5: Missing Evidence Citations

**Problem**: Stating facts without specifying evidence source

**Example**: "债务人支付了152,680元" ← Which evidence proves this?

**Prevention**:
- [ ] Every fact must start with "根据[证据类型]（证据第X页）"
- [ ] Cite specific page numbers
- [ ] No fact without evidence support

#### Error 2.6: Incorrect Invoice Amount Usage

**Problem**: Using 不含税金额 (tax-exclusive amount) instead of 价税合计 (tax-inclusive total)

**Example**:
- Invoice shows: 不含税金额 152,000元, 税额 19,760元, 价税合计 171,760元
- ❌ WRONG: Recording only 152,000元
- ✅ CORRECT: Recording 171,760元 (价税合计)

**Prevention**:
- [ ] For VAT invoices, ALWAYS use **价税合计** (tax-inclusive total) as the primary claimable amount
- [ ] Record 不含税金额 and 税额 for reference only, but **价税合计** is what creditor can claim
- [ ] When summarizing multiple invoices, sum the **价税合计** column
- [ ] Format: "根据增值税发票（发票号XXX），含税金额（价税合计）XXX元"
- [ ] Detection: If you write "不含税金额XXX元" as a claim amount, STOP - use 价税合计 instead

**Rationale**: In Chinese civil law, the claimable debt amount includes VAT. The debtor owes the full 价税合计, not just the tax-exclusive portion.

### Category 3: Information Identification Errors

#### Error 3.1: OCR Recognition Errors

**Problem**: Not catching obvious OCR mistakes

**Examples**:
- Amount "100,000" recognized as "10,000"
- ID number digits transposed
- Date format errors

**Prevention**:
- [ ] Review amounts for reasonableness (does 10元 make sense for a construction contract?)
- [ ] Check ID numbers are exactly 18 digits
- [ ] Verify date formats (YYYY-MM-DD)
- [ ] When in doubt, mark "需核实原件"

#### Error 3.2: Incorrect Relationship Count

**Problem**: Miscounting independent debt relationships

**Example**: 6 separate contracts counted as 1 relationship

**Prevention**:
- [ ] Each independent contract = 1 independent relationship
- [ ] Supplements/amendments don't create new relationships
- [ ] Judgment confirming contract doesn't create new relationship
- [ ] List all relationships explicitly

#### Error 3.3: Timeline Out of Order

**Problem**: Events not in chronological sequence

**Prevention**:
- [ ] Sort all events by date before finalizing
- [ ] Same-day events in logical order (sign → perform → breach)
- [ ] No jumps backward in time

### Category 4: Evidence Hierarchy Errors

#### Error 4.1: Ignoring Superior Evidence

**Problem**: Using original contract when settlement document exists

**Example**: Calculating amount per contract when settlement letter confirms different amount

**Prevention**:
- [ ] Identify highest-hierarchy evidence (judgment > confirmation > contract)
- [ ] Note which evidence is superseded
- [ ] Use final applicable terms in analysis section

#### Error 4.2: Missing Reference Relationships

**Problem**: Judgment references "per contract" but you don't trace back

**Example**: "Judgment: interest per contract" but you don't cite which contract article

**Prevention**:
- [ ] Identify reference phrases ("按原合同", "依据协议")
- [ ] Trace back to referenced document
- [ ] Quote both judgment AND referenced clause

#### Error 4.3: Incomplete Multi-Layer Analysis

**Problem**: Not tracking modification chain through supplements

**Example**: Contract → Supplement 1 → Supplement 2, but you only apply Supplement 1

**Prevention**:
- [ ] Trace complete modification chain
- [ ] Apply latest applicable term for each element
- [ ] Document the modification history in analysis

### Category 5: Batch Processing Errors

#### Error 5.1: Splitting Related Documents

**Problem**: Main contract in Batch 1, supplement in Batch 2

**Prevention**:
- [ ] Keep contract + ALL supplements in same batch
- [ ] Keep settlement document with contracts it summarizes

#### Error 5.2: Leaving Batch Markers

**Problem**: Final report shows "Batch 1 Results", "Batch 2 Results"

**Prevention**:
- [ ] Remove all batch section headers in final report
- [ ] Merge timelines into single continuous table
- [ ] Report should appear as single-pass processing

#### Error 5.3: Losing Evidence in Consolidation

**Problem**: Some evidence from Batch 2 not in final timeline

**Prevention**:
- [ ] Count evidence items: Batch 1 + Batch 2 + ... = Total
- [ ] Verify all key evidence appears in final timeline
- [ ] Check for gaps in timeline dates

## Part 3: Pre-Submission Checklist

### Declaration Section

- [ ] All amounts copied EXACTLY from declaration form
- [ ] Creditor's original category labels used (not standardized)
- [ ] Blank fields marked "[债权人未填写]"
- [ ] Checked boxes recorded exactly (not adjusted)
- [ ] No unauthorized corrections made

### Evidence Section

- [ ] All facts based on evidence materials, NOT declaration materials
- [ ] Every contract includes ALL 9 core clauses
- [ ] No "同上" or省略 shortcuts used
- [ ] Legal documents completely excerpted word-for-word
- [ ] Every fact cites specific evidence and page number

### Timeline Section

- [ ] All events in chronological order
- [ ] Each entry uses complete standardized format (not summarized)
- [ ] Each entry cites specific evidence source
- [ ] No gaps in chronological flow
- [ ] Settlement documents highlighted

### Analysis Section

- [ ] Evidence hierarchy correctly identified
- [ ] Superior evidence effects noted (覆盖/修改/确认)
- [ ] Reference relationships explained
- [ ] Final applicable terms clearly stated
- [ ] Handover notes for debt analyst provided

### Batch Processing (if applicable)

- [ ] Related evidence kept together
- [ ] All batch timelines merged
- [ ] No batch section markers remain
- [ ] Evidence count verified
- [ ] Final report appears unified

### Date Verification

- [ ] Bankruptcy dates verified from `.processing_config.json`
- [ ] Dates recorded in report introduction
- [ ] Stop-interest date correctly calculated (bankruptcy date - 1 day)

### General Quality

- [ ] All key information accurate (amounts, dates, names)
- [ ] No OCR errors in critical fields
- [ ] Report follows template structure
- [ ] Independent debt relationships correctly identified
- [ ] Report is complete and can stand alone

## Part 4: Quality Improvement Process

### Self-Review Technique

After drafting fact-checking report, review each section asking:

**Declaration Section**:
- "Did I change ANYTHING from what creditor wrote?" → If yes, revert to exact copy

**Timeline Section**:
- "Can I verify this fact from the cited evidence?" → If no, add better citation
- "Does this contract include all 9 clauses?" → If no, add missing clauses
- "Did I excerpt this judgment completely?" → If no, add full excerpt

**Analysis Section**:
- "Is this the highest-hierarchy evidence?" → If no, revise to use superior evidence
- "Did I trace back references?" → If no, find and cite referenced clauses

### Peer Review Points (if available)

If another person reviews your work, ask them to check:
- [ ] Can they understand each timeline entry without seeing the original evidence?
- [ ] Are there any facts without evidence citations?
- [ ] Do contracts have complete 9-clause excerpts?
- [ ] Are judgment excerpts complete and verbatim?

### Common Red Flags

**If you see these, something is likely wrong**:

- Timeline entry with no evidence citation
- Contract described in <5 lines (too brief!)
- Use of "同上" or "如前所述" in timeline
- Legal document summarized instead of excerpted
- Gap in timeline (e.g., Jan → Sep with nothing in between)
- Declaration amounts that look "too neat" (you may have rounded or corrected)
- Fact stated without "根据XX证据" prefix

## Part 5: Error Correction Protocol

### If You Discover an Error

**During Work**:
1. Pause immediately
2. Locate the error
3. Identify root cause (which principle violated?)
4. Correct following proper standard
5. Check similar sections for same error type

**After Submission** (if caught in review):
1. Acknowledge the error type
2. Understand why it occurred
3. Implement prevention measure for future
4. Update internal checklist to catch this error type

### Learning from Errors

Keep personal error log (for improvement only):
```
Error Type: [e.g., Missing evidence citation]
Occurrence: [Date, creditor name]
Root Cause: [e.g., Rushed, forgot to check]
Prevention: [e.g., Added to pre-submission checklist]
```

**Goal**: Each error type should only occur once - prevent recurrence through systematic checks.

## Part 6: Special Quality Standards

### For Contracts

**Minimum Acceptable Standard**:
- ✅ All 9 core clauses present
- ✅ Each clause cites contract article (第X条)
- ✅ Payment terms quote complete original wording
- ✅ Evidence source and page cited

**Gold Standard**:
- Above PLUS:
- Any special conditions noted (e.g., "所有权保留")
- Cross-reference to related supplements
- Note if contract terms were later modified

### For Legal Documents

**Minimum Acceptable Standard**:
- ✅ Entire judgment section excerpted verbatim
- ✅ Quotation marks used
- ✅ Original punctuation maintained
- ✅ Source cited (court, case number)

**Gold Standard**:
- Above PLUS:
- Effective date noted
- Any reference relationships identified (e.g., judgment references contract)
- Execution status noted (if execution documents exist)

### For Settlement/Confirmation Documents

**Minimum Acceptable Standard**:
- ✅ Confirmed amount clearly stated
- ✅ As-of date noted (截至XX日期)
- ✅ Parties identified
- ✅ Evidence source cited

**Gold Standard**:
- Above PLUS:
- Amount breakdown if provided
- Comparison with previous claims
- Note superior effect over prior performance evidence

### For Timeline as a Whole

**Minimum Acceptable Standard**:
- ✅ Chronological order
- ✅ All major events included
- ✅ Complete formats used
- ✅ Evidence citations throughout

**Gold Standard**:
- Above PLUS:
- No gaps in chronology
- Narrative flow between events
- Settlement documents clearly flagged as key
- Ready for debt analyst without questions

## Conclusion

Quality fact-checking requires:
1. **Discipline**: Follow standards even when tempted to shortcut
2. **Attention to Detail**: Every amount, date, citation matters
3. **Objectivity**: Record what evidence shows, not what you think
4. **Completeness**: No omissions, no shortcuts like "同上"
5. **Verification**: Check your work before submitting

**Remember**: Debt analyst relies on your fact-checking. Any errors here propagate through the entire debt review process. Quality here = Quality throughout.
