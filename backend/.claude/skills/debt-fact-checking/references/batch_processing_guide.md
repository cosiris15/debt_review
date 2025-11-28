# Batch Processing Guide for Large-Volume Materials

## Purpose

This guide provides detailed strategies for processing debt claim materials that exceed normal processing capacity, ensuring no evidence is lost while maintaining quality standards.

## Trigger Conditions

Activate batch processing when ANY of the following conditions are met:

1. **Total page count > 100 pages**
2. **Independent evidence items > 50**
3. **System indicates material exceeds processing window**

**Quick Assessment**:
```
Count Evidence Items:
□ Contracts (including supplements): ___ items
□ Legal documents: ___ items
□ Invoices: ___ items
□ Engineering documents: ___ items
□ Bank transfers: ___ items
□ Delivery slips: ___ items
□ Other: ___ items
Total: ___ items

If total > 50 OR total pages > 100 → Activate batch processing
```

## Basic Batching Principles

### Principle 1: Keep Related Evidence Together

**DO NOT split**:
- Main contract + its supplements/amendments
- Contract + key performance evidence directly referenced
- Settlement document + documents it summarizes

**Example**:
```
✅ GOOD Batching:
Batch 1:
- Sales Contract #001 (signed 2023-01-15)
- Supplement to Contract #001 (signed 2023-03-20)
- Settlement Document for Contract #001 (dated 2023-09-10)

❌ BAD Batching:
Batch 1: Sales Contract #001
Batch 2: Supplement to Contract #001  ← Split related documents
```

### Principle 2: Control Batch Size

**Target**: 30-50 evidence items per batch
**Maximum**: Do not exceed 60 items per batch
**Minimum**: At least 20 items per batch (unless last batch)

### Principle 3: Final Report Must Appear Unified

**The user should NOT see**:
- Section headers like "Batch 1 Results", "Batch 2 Results"
- Incomplete information with notes "see next batch"
- Disjointed timeline with gaps

**The user SHOULD see**:
- Unified timeline as if processed in one pass
- Complete evidence analysis
- Seamless narrative

## Standard Batching Order

### Batch 1: Core Contracts + Key Performance Evidence

**Include**:
- All main contracts with their complete supplement chain
- Key performance evidence DIRECTLY tied to contracts:
  - Settlement documents
  - Major confirmation letters
  - Critical engineering documents

**Reason**: Establishes foundation of debt relationship

**Size Estimate**: Usually 15-30 items

### Batch 2: Performance Evidence (Grouped by Time Period)

**Include** (grouped by time period, e.g., by quarter or month):
- Invoices (group by date range, e.g., 2023 Q1, Q2, etc.)
- Delivery slips (group by date range)
- Bank transfer records (group by date range)
- Regular engineering progress documents

**Grouping Strategy**:
```
If 60 invoices spanning 2 years:
- Batch 2A: Invoices Jan-Jun 2022 (30 items)
- Batch 2B: Invoices Jul-Dec 2022 (30 items)
- Batch 3: Invoices 2023 (30 items, combined with legal docs)
```

**Reason**: Performance evidence is voluminous but can be time-segmented

### Batch 3 (Final): Legal Documents + Final Confirmations

**Include**:
- Court judgments, mediation agreements
- Arbitration awards
- Final reconciliation statements
- Execution documents

**Reason**: Highest hierarchy evidence, often summarizes everything prior

## Processing Workflow

### Step 1: Material Assessment & Planning

**Actions**:
1. Count total evidence items by category
2. Identify logical groupings
3. Draft batching plan

**Template**:
```
## Batching Plan for [Creditor Name]

Total Evidence: ___ items across ___ pages

Batch 1: Core Contracts (Items: ___)
- List key contracts
- Estimated pages: ___

Batch 2A: Performance Evidence Q1-Q2 2022 (Items: ___)
- Invoices: ___
- Delivery slips: ___
- Bank transfers: ___
- Estimated pages: ___

Batch 2B: Performance Evidence Q3-Q4 2022 (Items: ___)
- [same structure]

Batch 3: Legal Documents + 2023 Evidence (Items: ___)
- Judgments: ___
- Confirmations: ___
- 2023 invoices: ___
- Estimated pages: ___
```

### Step 2: Process Each Batch Independently

**For Each Batch**:

1. **Extract facts per standard formats**
   - Apply same quality standards as single-batch processing
   - Use complete standardized formats for each evidence type

2. **Generate batch summary**
   ```
   ## Batch [X] Summary

   Evidence Processed: ___ items
   Key Findings:
   - [Major contracts identified]
   - [Critical facts established]
   - [Date range covered]

   Cross-Batch Notes:
   - [Any references to items in other batches]
   - [Incomplete information requiring next batch]
   ```

3. **Tag cross-batch references**
   - If evidence in this batch references evidence in another batch, note it
   - Example: "Invoice #050 (Batch 2B) references Contract #001 (Batch 1)"

### Step 3: Consolidate Into Unified Report

**Critical Consolidation Tasks**:

1. **Merge Timelines**
   - Combine all batch timelines into single chronological timeline
   - Remove batch section markers
   - Ensure continuous narrative

2. **Resolve Cross-References**
   - Where Batch 2 evidence referenced Batch 1 contracts, integrate seamlessly
   - Example: Instead of "see Contract in Batch 1", write "根据XX合同（证据第X页）"

3. **Unify Evidence Analysis**
   - Consolidate evidence hierarchy analysis
   - Present final applicable terms based on ALL evidence

4. **Quality Check**
   - Verify no evidence items were lost
   - Confirm timeline is complete and chronological
   - Ensure report reads as if single-pass processing

## Quality Control for Batch Processing

### During Processing

**Batch Checklist** (for each batch):
- [ ] Related evidence kept together (not split inappropriately)
- [ ] Batch size within 30-60 items
- [ ] All evidence in batch processed per standards
- [ ] Batch summary created
- [ ] Cross-batch references tagged

### During Consolidation

**Consolidation Checklist**:
- [ ] All batch timelines merged chronologically
- [ ] No batch section markers remain in final report
- [ ] Cross-batch references resolved
- [ ] Evidence count matches: (Batch 1 + Batch 2 + ...) = Total
- [ ] Final report narrative is seamless
- [ ] Timeline has no gaps or discontinuities

### Final Verification

**Compare against original material**:
- [ ] All contracts accounted for
- [ ] All legal documents accounted for
- [ ] Invoice count matches (count from material vs. count in timeline)
- [ ] No evidence items mysteriously "lost" between batches

## Special Handling Scenarios

### Scenario 1: Contract Chain Spanning Multiple Batches

**Problem**: Main contract in Batch 1, but Supplement signed later is in Batch 2 (time-grouped)

**Solution**:
- Keep main contract + all supplements together in Batch 1
- Even if supplement is dated much later, include it with main contract
- Rationale: They form single legal relationship

### Scenario 2: Settlement Document Referencing Many Invoices

**Problem**: Settlement doc is in Batch 3, but references 50 invoices across Batches 1-2

**Solution**:
- Process settlement doc in Batch 3 as planned
- In consolidation, clearly show settlement doc summarizes prior invoices
- Use settlement amount as final confirmed amount

### Scenario 3: Judgment Partially Referencing Contract

**Problem**: Judgment in Batch 3 says "interest per original contract", contract is in Batch 1

**Solution**:
- In Batch 3 summary, note: "Judgment references original contract interest clause - see Batch 1"
- In consolidation, integrate: "判决确定利息按原合同第5条，约定年利率6%（见Batch 1证据第X页）"
- In final report, remove "Batch 1" reference, use direct page citation

### Scenario 4: Too Many Evidence Items Even for Batching

**Problem**: 200+ invoices, even batching by quarter exceeds capacity

**Solution**:
```
Apply hierarchical batching:

Batch 1: Core Contracts (standard)

Batch 2: Invoice Summaries + Samples
- Summarize invoices by month (e.g., "2022年1月：15张发票，总计XXX元")
- Include first and last invoice of each month as samples
- Note: "详细发票清单见原始材料"

Batch 3: Legal Documents + Confirmations (standard)

Rationale: If there's a confirmation letter or settlement, it likely summarizes the invoices anyway
```

## Batch Processing Documentation

### In Working Papers

Create a batch processing log (for your own reference, not in final report):

```
## Batch Processing Log - [Creditor Name]

Date: [Processing date]
Total Evidence: XXX items

Batch 1:
- Items: XXX
- Date processed: XXX
- Key contracts: [list]
- Cross-references: [note any]

Batch 2A:
- Items: XXX
- Date processed: XXX
- Evidence types: [list]
- Cross-references: [note any]

[...]

Consolidation:
- Date: XXX
- Total timeline entries: XXX
- Evidence items accounted for: XXX / XXX
- Quality checks passed: YES/NO
```

### In Final Report

**Do NOT include**:
- Batch numbers or batch section headers
- References to "processed in multiple batches"
- Any indication of batching

**DO include** (if relevant):
```
[In methodology note at beginning, if helpful:]

说明：鉴于本案证据材料较多（共XXX项证据，XXX页），事实核查采用分类整理方式，最终形成统一的时间线表格和证据分析。
```

## Common Mistakes in Batch Processing

### Mistake 1: Splitting Related Documents

❌ **Wrong**:
- Batch 1: Main Contract #001
- Batch 2: Supplement to Contract #001

✅ **Right**:
- Batch 1: Contract #001 + ALL its supplements

### Mistake 2: Leaving Batch Markers in Final Report

❌ **Wrong**:
```
## Batch 1 Results
[timeline entries]

## Batch 2 Results
[timeline entries]
```

✅ **Right**:
```
## 债权发生情况查明

| 序号 | 日期 | 债权发生情况 |
|------|------|-------------|
[single unified timeline]
```

### Mistake 3: Not Resolving Cross-References

❌ **Wrong** (in final report):
"根据Batch 3的判决书，本金为100万元"

✅ **Right**:
"根据XX法院判决书（证据第XXX页），本金为100万元"

### Mistake 4: Losing Evidence During Consolidation

**Prevention**:
- Maintain evidence item count at each stage
- Verify sum of batch items = total items
- Cross-check timeline entry count

### Mistake 5: Timeline Discontinuities

❌ **Wrong**:
```
| 5 | 2023-03-15 | Contract signed |
| 6 | 2023-09-20 | Judgment issued |  ← Gap: where's April-August?
```

**Cause**: Evidence from April-August was in different batch and lost in consolidation

**Prevention**: After merging, verify timeline continuity

## Batch Processing Efficiency Tips

1. **Use Templates**: Pre-fill batch summary templates
2. **Tag Liberally**: Better to over-tag cross-references than miss them
3. **Summarize First**: For each batch, write 2-3 sentence summary before diving into details
4. **Track Counts**: Keep running count of evidence items processed vs. total
5. **Test Merge Early**: After Batch 1 and 2, test consolidation approach before proceeding

## When NOT to Use Batch Processing

**Don't batch if**:
- Evidence items < 40
- Total pages < 80
- Materials are already well-organized by creditor
- You can process in one pass comfortably

**Batch processing adds overhead** - only use when necessary.
