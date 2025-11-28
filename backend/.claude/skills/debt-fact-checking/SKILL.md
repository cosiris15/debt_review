---
name: debt-fact-checking
description: Extract and verify debt claim information from bankruptcy materials. Organizes creditor declarations, classifies evidence across 9 legal relationship types, establishes factual relationships, and creates case timelines. Use for initial debt claim review and evidence organization tasks.
---

# Debt Fact-Checking Skill

## Overview

Systematic fact-checking and evidence organization for bankruptcy debt claims. This skill provides the methodology for processing creditor declaration materials, extracting structured information, and establishing factual relationships based on submitted evidence documents.

## 📋 CRITICAL: Template Files Reference

**⚠️ MANDATORY READING - NON-NEGOTIABLE**

Before executing any fact-checking task, you **MUST** read the complete format template:

**Template Location**: `templates/fact_checking_report_template.md`

**Why This Is Critical**:
- Defines the EXACT format structure that clients and legal teams expect
- Contains standardized table formats used across all reports
- Specifies mandatory special markers and wording
- Provides complete examples of 9-clause contract extraction
- Ensures consistency across all debt reviews in this bankruptcy proceeding

**Template Contains**:
- Complete report structure (all required sections)
- Exact markdown heading formats (## 一、## 二、etc.)
- Declaration information table formats
- Contract extraction standardized formats
- Timeline table structures
- Evidence analysis section templates

**This is NOT optional**. The template represents established client requirements and legal professional standards. Deviating from the template format creates inconsistencies and may require report regeneration.

## When to Use This Skill

- Processing creditor declaration materials (申报材料)
- Organizing evidence and establishing factual relationships
- Creating case timelines for debt claims
- Initial review of debt claim submissions
- Batch processing of materials exceeding 100 pages or 50 evidence items

## ⚠️ MANDATORY Pre-Work Check: Date Verification

**BEFORE starting any fact-checking work, you MUST:**

1. **Read Configuration**: Extract bankruptcy filing date from `.processing_config.json` in creditor directory
2. **Validate Date**: Confirm date format is correct and reasonable
3. **Record Confirmation**: Document the dates used at the beginning of your report
4. **Handle Exceptions**: If configuration file is missing or dates are abnormal, STOP work immediately and report

**Example Output Format**:
```
✅ 破产受理日期核对完成
- 破产受理日期：2023-05-12
- 停止计息日期：2023-05-11
- 配置文件状态：正常
```

**Critical Importance**: The bankruptcy filing date is the key cutoff point for all interest calculations. Wrong dates will invalidate the entire debt review result.

## Pre-processing: Claim Structure Overview (Step 0)

**⚠️ MANDATORY for ALL debt claims - Execute BEFORE the 6-step workflow**

### Purpose

Generate a structured overview of the debt claim before detailed fact-checking. This step:
- Quickly identifies claim structure and complexity
- Provides navigation index for subsequent review
- Identifies multi-loan claims and complex guarantee relationships
- Determines whether simplified or comprehensive processing is needed

### Execution

**All claims require pre-processing. Version selection based on complexity:**

| Version | When to Use |
|---------|-------------|
| **Simplified** | Single claim, simple/no guarantee, non-financial creditor |
| **Comprehensive** | Financial institutions, multi-loan, complex guarantees, debt assignment |

### Pre-processing Workflow

```
Step 0.1: Quick material scan (5-10 minutes)
    ↓
Step 0.2: Identify claim type and complexity
    ↓
Step 0.3: Select template version (Simplified/Comprehensive)
    ↓
Step 0.4: Generate Claim Structure Overview
    ↓
Step 0.5: Generate Legal Relationship Diagram (if conditions met)
    ↓
Proceed to 6-Step Core Workflow
```

### Version Selection Criteria

**Use Comprehensive Version if ANY of the following apply:**

1. **Financial Institution Creditor**: Bank, trust, AMC, leasing company, factoring company
2. **Multi-Loan Claims**: ≥2 separate loans from same creditor
3. **Complex Guarantees**: ≥2 guarantors, ≥2 collateral, mixed guarantees
4. **Debt Assignment**: Current creditor is not original creditor
5. **Long Materials**: ≥200 pages

**Otherwise use Simplified Version.**

### Output Files

| File | Location | Purpose |
|------|----------|---------|
| `{债权人名称}_债权结构概览.md` | 工作底稿/ | Claim structure overview (always generated) |
| `{债权人名称}_法律关系图.md` | 工作底稿/ | Legal relationship diagram (if conditions met) |

### Detailed Guidance

- **Template**: See `templates/claim_structure_overview_template.md`
- **Guide**: See `references/claim_preprocessing_guide.md`
- **Diagrams**: See `references/mermaid_diagram_generation.md`

### Configuration Update (Step 0 Completion - MANDATORY)

**After completing pre-processing, you MUST update `.processing_config.json` with preprocessing_config field.**

This enables the workflow controller to validate pre-processing outputs.

**Write the following structure:**

```json
{
  "preprocessing_config": {
    "version": "comprehensive",
    "trigger_conditions": {
      "financial_institution": true,
      "multi_loan": true,
      "complex_guarantee": false,
      "debt_transfer": false,
      "high_amount": false
    },
    "diagram_required": true,
    "diagram_types": ["subject", "contract"]
  }
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | "simplified" or "comprehensive" |
| `financial_institution` | bool | Creditor is bank/trust/AMC/leasing/factoring |
| `multi_loan` | bool | ≥2 separate loans from same creditor |
| `complex_guarantee` | bool | ≥3 guarantors OR mixed guarantee types |
| `debt_transfer` | bool | Debt assignment occurred |
| `high_amount` | bool | Total claim ≥10 million yuan |
| `diagram_required` | bool | Legal relationship diagram was generated |
| `diagram_types` | array | Types generated: "subject", "contract", "transfer" |

**How to Update:**

```python
import json
config_path = Path(base_directory) / ".processing_config.json"
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
config['preprocessing_config'] = {
    "version": "comprehensive",  # or "simplified"
    "trigger_conditions": {...},
    "diagram_required": True,    # or False
    "diagram_types": [...]
}
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
```

**Why This Matters:**
- Enables automated validation of pre-processing outputs
- Records decision audit trail for quality control
- Allows batch-level verification (`--validate-batch X --stage 0`)

---

## Core Workflow (6-Step Process)

### Step 1: Material Reception and Assessment

**Objective**: Understand the scope and complexity of materials

**Actions**:
- Count total pages and evidence items
- Identify primary legal relationship type
- Determine if batch processing is needed (>100 pages or >50 items)

**Batch Processing Trigger**:
- Total pages > 100, OR
- Evidence items > 50, OR
- System prompts material exceeds processing window

**When batch processing needed**: See `references/batch_processing_guide.md`

### Step 2: Declaration Information Organization

**Objective**: Extract structured creditor information from declaration forms

**⚠️ CRITICAL PRINCIPLE: EXACT COPY RULE**

Must strictly copy what the creditor actually filled in the declaration form, including:
- Copy amounts exactly as declared by creditor
- Use creditor's original category labels
- If creditor didn't fill something, mark "[债权人未填写]"
- If creditor's categorization differs from standard, record as-is
- Do NOT make any subjective judgments or "corrections"

**Key Elements to Extract**:

1. **Creditor Information**:
   - Enterprise: Full name, type, address, legal representative, unified social credit code
   - Individual: Name, ID number, contact address

2. **Declared Amount Breakdown** (EXACT COPY):
   - Principal: [exact amount] yuan
   - Interest: [exact amount] yuan
   - Other: [exact amount] yuan
   - Total: [exact amount] yuan

3. **Debt Classification** (EXACT COPY):
   - Priority debt / Ordinary debt / Subordinated debt
   - Record exactly what creditor checked
   - If nothing checked, mark "[债权人未勾选债权性质]"

4. **Security Information**:
   - Copy creditor's description exactly

**Detailed extraction patterns and table formats**: See `references/declaration_extraction_guide.md`

### Step 3: Evidence Classification

**Objective**: Categorize evidence by legal relationship type

**🚨 CRITICAL RULE: Distinguish Evidence from Declarations**

- **Evidence materials**: Contracts, judgments, invoices, receipts → **Can be used as fact-finding basis**
- **Declaration materials**: Declaration forms, declaration letters → **Only as thinking clues, NEVER as fact-finding evidence**

**9 Legal Relationship Types**:

1. 借款合同 (Loan contracts)
2. 买卖合同 (Sales contracts)
3. 建设工程合同 (Construction contracts)
4. 担保合同 (Guarantee contracts)
5. 劳动关系 (Labor relations)
6. 侵权责任 (Tort liability)
7. 票据关系 (Negotiable instruments)
8. 生效法律文书 (Effective legal documents)
9. 其他 (Others)

**Classification Process**:
1. Count evidence materials by type
2. Determine each evidence's corresponding legal relationship
3. Identify independent debt relationships (each contract = one relationship)

**Full classification standards**: See `references/evidence_and_facts_guide.md` § Evidence Classification

**🚨 PROHIBITED - Evidence Catalog Trap**:

**CRITICAL**: Facts MUST come from actual evidence materials, NEVER from evidence catalogs/lists.

**Prohibited Sources** (仅供导航，不可作为事实依据):
- ❌ 证据目录 (evidence catalog/directory)
- ❌ 证据清单 (evidence list/index)
- ❌ 债权申报书中的证据说明 (evidence descriptions in debt declarations)
- ❌ 证据材料摘要 (evidence summaries created by creditor)

**Required Sources** (实际证据材料):
- ✅ 合同原件 (actual contracts)
- ✅ 发票原件 (actual invoices)
- ✅ 判决书原件 (actual court judgments)
- ✅ 转账凭证原件 (actual bank transfer records)
- ✅ 工程文件原件 (actual engineering documents)

**Detection Rule**: If you write "根据证据目录" or "根据证据清单", STOP immediately - you are using the wrong source.

**When Evidence Materials Are Missing**:
- Document what is missing: "债权人未提供[具体证据类型]"
- Process only the evidence actually provided
- Mark report with: "部分证据材料缺失，无法核实[具体事实]"
- ❌ DO NOT fabricate facts based on catalogs or declarations

### Step 4: Factual Relationship Establishment

**Objective**: Build evidence-based factual relationships

**Core Methodology**:

For each type of evidence, extract using standardized formats:

**Contract Evidence** - Must include 9 core clauses:
1. Subject matter
2. Contract price
3. Performance period
4. Delivery and acceptance
5. Payment terms (COMPLETE original wording required)
6. Breach liability
7. Invoice requirements
8. Dispute resolution
9. Designated recipient clause (specific name/position)

**Legal Documents** - Must complete verbatim excerpt:
- MUST excerpt ENTIRE "判决如下" section word-for-word
- Use quotation marks for excerpted content
- Maintain original punctuation and formatting

**Other Evidence Types**:
- Invoices: Record invoice number, amount, date, parties
- Engineering documents: Record project, amount, signatures
- Bank transfers: Record amount, date, parties, purpose
- Delivery slips: Record goods, quantity, recipient signature

**⚠️ Special Attention**:
- Settlement documents (工程结算单, 结算协议) are KEY - highlight in findings
- Confirmation letters (债权确认书, 对账单) override previous details

**Detailed format standards for each evidence type**: See `references/evidence_and_facts_guide.md` § Classified Fact-Finding Standards

### Step 5: Timeline Creation

**Objective**: Establish chronological sequence of key events

**🚨 MANDATORY FORMAT REQUIREMENTS**:

1. **Use Complete Formats**: Each timeline entry MUST use the complete standardized format from Step 4, NOT simplified descriptions
2. **Evidence Citation Required**: Every fact MUST cite specific evidence (e.g., "根据XXX证据第X页")
3. **No Repetition Omissions**: Each contract MUST include all 9 clauses even if identical to others - NEVER use "同上"

**Timeline Table Format**:

| 序号 | 日期 | 债权发生情况 |
|------|------|-------------|
| 1.   | YYYY-MM-DD | [Complete standardized format from Step 4] |
| 2.   | YYYY-MM-DD | [Complete standardized format from Step 4] |

**Sorting Principles**:
- Chronological order by event occurrence date
- Multiple events on same day: logical order (signing → performance → breach)
- Legal documents: use document creation date
- Performance facts: use actual occurrence date

**Timeline creation standards**: See `references/quality_checklist.md` § Timeline Creation

### Step 6: Report Generation

**Objective**: Produce independent《事实核查报告》

**Report Must Include**:

1. **Report Title**: "[债权人名称]事实核查报告"
2. **Declaration Information**: Exact copy of creditor declarations
3. **Formal Document Checklist**: Complete file verification status
4. **Debt Facts Timeline** (CORE): Detailed timeline table
5. **Legal Relationship Identification**: Debt types and quantities
6. **Evidence Relationship Analysis**: Analyze evidence hierarchy
7. **Handover Notes to Analyst**: Key points and reminders
8. **Batch Processing Notes** (if applicable): Explain batching method

**Report Structure**:
```markdown
# [债权人名称]事实核查报告

## 一、申报情况
[Exact copy of declaration materials]

## 二、形式性文件核查
[Checklist table]

## 三、债权发生情况查明（核心内容）
| 序号 | 日期 | 债权发生情况 |
|------|------|-------------|
[Complete timeline]

## 四、债权基础法律关系识别
[Identification results]

## 五、证据关系综合分析
[Preliminary analysis]

## 六、向债权分析员的移交说明
[Key reminders]
```

**Complete template**: See `templates/fact_checking_report_template.md`

## Batch Processing Strategy

**Trigger Conditions**:
- Total pages > 100 pages, OR
- Evidence items > 50 items, OR
- System indicates material exceeds processing capacity

**Basic Batching Principles**:
- Keep related evidence in same batch
- Control each batch to 30-50 evidence items
- Final report should NOT show batching traces

**Standard Batching Order**:
1. **Batch 1**: Core contracts + supplements + key performance evidence
2. **Batch 2**: Performance evidence grouped by time period (invoices, delivery slips, transfers)
3. **Batch 3**: Legal documents + confirmation documents

**Processing Workflow**:
```
Assess material volume → Create batching plan
↓
Process each batch → Generate batch summaries
↓
Consolidate → Output unified complete report
```

**Quality Control**:
- Maintain relevance across batches
- Ensure cross-batch consistency
- Verify completeness after consolidation
- Final report should appear as single-pass processing

**Complete batching strategy and examples**: See `references/batch_processing_guide.md`

## Evidence Relationship Analysis

**Purpose**: After completing timeline, analyze evidence hierarchy to determine final applicable terms

**Evidence Hierarchy** (highest to lowest):
1. Effective legal documents (判决书, 调解书, 仲裁裁决)
2. Bilateral confirmation documents (债权确认书, 对账单, 结算单)
3. Supplementary/amendment agreements
4. Original contracts
5. Unilateral performance evidence (invoices, delivery slips)
6. Unilateral declaration materials

**Key Analysis Points**:

1. **Coverage Relationships**: Which original agreements are modified by subsequent documents
2. **Final Applicable Terms**: For each key element, identify final basis:
   - Debt amount: Based on which document
   - Interest calculation: Which standard applies
   - Breach liability: Any changes or judicial confirmations
   - Payment deadline: Latest agreement or judgment requirement

3. **Complex Reference Relationships**:
   - Judgment partially references contract: e.g., "利息按合同约定" - must trace back to original contract
   - Multi-layer modifications: Original contract → Supplement 1 → Supplement 2 → Confirmation letter
   - Cross-references: When documents reference each other

**Output Format**:
```
### 证据关系综合分析

#### 1. 最终债权确定
Based on all evidence, final debt is determined per [document name]...

#### 2. 证据效力关系分析
According to evidence hierarchy, [highest document] has supreme effect because...

#### 3. 需要特别关注的事项
[Special reminders if any]

#### 4. 为债权分析员提供的重点提示
[Key points for debt analyst]
```

**Detailed analysis methods**: See `references/evidence_and_facts_guide.md` § Evidence Relationship Analysis

## Critical Reminders

⚠️ **Date Verification**: ALWAYS verify bankruptcy dates from `.processing_config.json` before starting

⚠️ **Evidence vs. Declaration**: Clearly distinguish what is declared vs. what is proven by evidence

⚠️ **No Legal Conclusions**: Focus on factual extraction only, not legal analysis

⚠️ **Complete Format Required**: Timeline must use complete standardized formats, no simplification

⚠️ **Evidence Citation Mandatory**: Every fact must cite specific evidence source and page number

## Error Prevention Quick Checklist

**Before Finalizing**:
- [ ] Verified bankruptcy dates from config file
- [ ] All declaration amounts copied exactly as creditor filled (no corrections)
- [ ] Evidence strictly distinguished from declaration materials
- [ ] Every contract includes all 9 core clauses (no "同上" shortcuts)
- [ ] Legal documents completely excerpted word-for-word (entire judgment section)
- [ ] Every fact cites specific evidence source and page number
- [ ] Timeline chronologically ordered
- [ ] No mixing of declaration and evidence content
- [ ] Report follows template structure
- [ ] Settlement documents (if any) highlighted in findings

**Complete checklist**: See `references/quality_checklist.md`

## Quick Reference

### Common Legal Relationship Types

| 类型 | 关键证据 | 常见要素 |
|-----|---------|---------|
| 借款合同 | 借款协议、转账凭证 | 本金、利率、期限 |
| 买卖合同 | 合同、发票、送货单 | 货物、价款、交付 |
| 建设工程 | 施工合同、结算书 | 工程款、质保金 |
| 生效法律文书 | 判决书、调解书 | 判决主文、生效日期 |

### Batch Processing Decision Tree

```
材料量 > 100页? ─Yes→ 启动分批处理
    │
    No
    ↓
证据 > 50项? ─Yes→ 启动分批处理
    │
    No
    ↓
正常单批处理
```

### Contract Core Clauses (Must Include All 9)

1. 标的物 (Subject matter)
2. 合同价款 (Contract price)
3. 履行期限 (Performance period)
4. 交付与验收 (Delivery and acceptance)
5. 付款方式 (Payment terms - COMPLETE wording)
6. 违约责任 (Breach liability)
7. 发票要求 (Invoice requirements)
8. 争议解决 (Dispute resolution)
9. 签收/其他关键约定 (Receipt/other key terms)
