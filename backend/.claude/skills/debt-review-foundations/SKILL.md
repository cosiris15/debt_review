---
name: debt-review-foundations
description: Foundational knowledge for debt claim review in bankruptcy proceedings. Includes legal standards, calculation formulas, common terminology, core principles, and system architecture. Essential reference for fact-checking, debt analysis, and report organization tasks.
---

# Debt Review Foundations Skill

## Overview

This skill provides foundational knowledge and common standards that underpin all debt claim review activities in bankruptcy proceedings. It serves as a shared knowledge base for fact-checking, debt analysis, and report organization.

## When to Use This Skill

- Understanding legal basis for debt review decisions
- Looking up calculation formulas and rate standards
- Clarifying debt review terminology
- Understanding core principles (就低原则, 就无原则)
- Reviewing system architecture and workflow
- Accessing common quality standards

## Core Content Areas

This skill contains three main knowledge areas:

1. **Legal Standards** (`legal_standards_reference.md`):
   - Applicable laws and regulations
   - Supreme Court interpretations
   - Legal principles for debt classification
   - Time period transition rules

2. **Calculation Standards** (`calculation_formulas_reference.md`):
   - Interest calculation formulas
   - LPR rate data and selection rules
   - Penalty caps and legal limits
   - Offset and segmentation methods

3. **Common Terminology** (`common_terms_glossary.md`):
   - Debt classification terms
   - Legal relationship types
   - Evidence hierarchy terms
   - Process and workflow terms

## Part 1: System Architecture Overview

### Three-Agent Collaborative System

**System Goal**: Establish professional, standardized debt review collaboration through three specialized agents working in sequence.

**Workflow**:
```
Raw Materials → Fact Checker → Debt Analyst → Report Organizer → Review Opinion Form
     ↓              ↓              ↓               ↓
 Declaration   Fact Finding   Amount Analysis   Integration
Classification Evidence Review Interest Calc    Template Application
                               Statute Review    File Standards
                               Output Results    Final Report
```

### Agent Responsibilities

#### Agent 1: Fact Checker (debt-fact-checker)
**Core Responsibilities**:
- Declaration information organization
- Basic factual relationship establishment
- Evidence classification and timeline creation
- Independent fact-checking report generation

**Output**: 《事实核查报告》

#### Agent 2: Debt Analyst (debt-claim-analyzer)
**Core Responsibilities**:
- Professional amount analysis
- Precise interest calculation (MUST use calculator tool)
- Statute of limitations assessment
- Execution statute analysis
- Independent debt analysis report generation

**Output**: 《债权分析报告》 + Calculation files (Excel/CSV or TXT)

#### Agent 3: Report Organizer (report-organizer)
**Core Responsibilities**:
- Report consolidation
- Client template application
- File organization and naming standardization

**Output**: 审查意见表 (Review Opinion Form) + 文件清单 (File Inventory)

### Processing Sequence (MANDATORY)

**⚠️ Critical Rule**: MUST process sequentially, ONE claim at a time through complete workflow

```
✅ CORRECT (Serial Processing):
Claim 1: Fact Check → Analysis → Organize → Complete ✓
Claim 2: Fact Check → Analysis → Organize → Complete ✓
Claim 3: Fact Check → Analysis → Organize → Complete ✓

❌ WRONG (Batch Processing):
Claims 1,2,3: All Fact Check → All Analysis → All Organize
```

**Rationale**: Each claim must complete entire workflow before starting next claim to ensure quality and independent review.

## Part 2: Core Principles

### Principle 1: 就低原则 (Lower Bound Rule)

**When**: Calculation result > Creditor's declared amount

**Action**: Use declared amount as final confirmation

**Rationale**: Respect creditor's self-limitation of claim amount

**Example**:
- Creditor declares: 10,000元 interest
- Calculation shows: 12,000元
- **Final confirmation**: 10,000元 (declared amount)

### Principle 2: 就无原则 (Non-Existence Rule)

**When**: Amount item identified in evidence but NOT declared by creditor

**Action**: Do NOT include in final confirmation

**Rationale**: Debt review is verification, not claim generation. Only review what creditor claimed.

**Example**:
- Evidence shows: 5,000元 attorney fees
- Creditor did NOT declare attorney fees
- **Final confirmation**: Do NOT include this 5,000元

**Critical Applications**:
- Don't calculate delayed performance interest if not declared
- Don't expand calculation base beyond what creditor declared
- Don't add cost items creditor didn't claim

### Principle 3: Evidence Support Rule

**Requirement**: Both declaration AND evidence required for confirmation

**Standard**:
- Creditor-declared items without evidence support → NOT confirmed
- Evidence-proven items not declared by creditor → NOT included (Rule 2 applies)

### Principle 4: Substance Over Form

**Principle**: Focus on actual legal relationships and economic substance, not just document labels

**Application**:
- Break down umbrella terms ("本金", "利息") into specific items
- Each amount item must have specific legal basis
- Classify based on actual nature, not creditor's label

## Part 3: Debt Classification System

### By Priority

**优先债权 (Priority Debt)**:
- Employee wages, social security, housing fund
- Individual income tax and individual social security from tax authority claims
- Secured debts (within collateral value)

**普通债权 (Ordinary Debt)**:
- Unsecured contract debts
- Principal amounts
- Contract interest
- Costs (attorney fees, court fees as awarded)

**劣后债权 (Subordinated Debt)**:
- Delayed performance interest (加倍部分债务利息)
- Penalty interest exceeding legal limits
- Shareholder/related party claims (in some cases)

### By Nature

**本金类 (Principal Items)**:
- Core payment obligations
- Examples: Contract price, loan principal, project payment

**利息类 (Interest Items)**:
- Time-based or breach-based derivative amounts
- Examples: Loan interest, overdue interest, delayed performance interest
- **Important**: Penalties (违约金) classify as "利息", NOT "其他"

**费用类 (Cost Items)**:
- Recoverable expenses for claim realization
- Examples: Attorney fees, court filing fees, preservation fees (if awarded)

## Part 4: Legal Relationship Types

### Nine Main Categories

1. **买卖合同 (Sales Contract)**: Sale and purchase of goods
2. **借款合同 (Loan Contract)**: Lending arrangements
3. **服务/劳务合同 (Service Contract)**: Service provision
4. **建设工程合同 (Construction Contract)**: Construction and engineering projects
5. **租赁合同 (Lease Contract)**: Property or equipment rental
6. **承揽合同 (Processing Contract)**: Work for hire, processing
7. **票据关系 (Negotiable Instrument)**: Bills, notes, checks
8. **法律文书确认类 (Legal Document Confirmed)**: Based on judgment, mediation, arbitration
9. **其他法律关系 (Other Legal Relationships)**: Tort, unjust enrichment, etc.

**Importance**: Each independent legal relationship requires separate analysis.

## Part 5: Evidence Hierarchy

### Hierarchy Levels (Highest to Lowest)

**Level 1: Legal Documents with Final Effect**
- Court judgments (生效判决书)
- Mediation agreements (调解书)
- Arbitration awards (仲裁裁决书)
- **Effect**: Supersede all prior agreements/evidence

**Level 2: Bilateral Confirmation Documents**
- Settlement agreements (结算单, signed by both parties)
- Reconciliation statements (对账单, with debtor signature/seal)
- Debt confirmation letters (债权确认书)
- **Effect**: Supersede prior performance evidence

**Level 3: Contracts and Amendments**
- Main contracts
- Supplementary agreements
- Amendments
- **Effect**: Later amendments supersede earlier terms

**Level 4: Unilateral Evidence**
- Invoices (single direction)
- Delivery slips (single direction)
- Payment records
- **Effect**: Support contracts but lower probative value alone

**Application**: When conflict exists, use higher-hierarchy evidence.

## Part 6: Critical Date Definitions

### 破产受理日期 (Bankruptcy Filing Date)

**Source**: Project configuration file (`project_config.ini` or `.processing_config.json`)

**Importance**: **生命线级别** (Lifeline-level critical)

**Why Critical**:
- Determines ALL interest calculation cutoff points
- Determines statute of limitations comparison date
- Wrong date → Entire analysis invalid

**Verification Protocol** (MANDATORY for ALL agents):
1. Read from `.processing_config.json`
2. Cross-verify with prior reports (if applicable)
3. Record explicitly in output report
4. Stop immediately if any inconsistency found

### 停止计息日期 (Interest Stop Date)

**Formula**: 破产受理日期 - 1 day

**Example**:
- Bankruptcy filing date: 2025-05-12
- Interest stop date: 2025-05-11

**Application**: ALL interest calculations must end on or before this date.

## Part 7: Calculator Tool Standards

### Tool Information

**Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**Mandatory Use**: MUST use for ALL interest calculations, NEVER manual calculations

**Capabilities**:
- Five calculation modes: simple, LPR, delay, compound, penalty
- Embedded LPR rate data (2019-2025)
- Automatic Excel/CSV process table generation
- No external dependencies

**Basic Usage**:
```bash
python universal_debt_calculator_cli.py <mode> --principal <amount> --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD> [mode-specific options]
```

**Modes**:
- `simple`: Fixed rate simple interest
- `lpr`: LPR floating rate interest
- `delay`: Delayed performance interest (固定日利率0.0175%)
- `compound`: Compound interest
- `penalty`: Penalty interest

**For detailed usage**: See `calculation_formulas_reference.md`

## Part 8: Quality Standards Summary

### Universal Quality Checklist

**Date Verification** (ALL agents):
```
□ Bankruptcy dates verified from .processing_config.json
□ Dates cross-verified with prior reports (if applicable)
□ Dates recorded explicitly in output
□ All calculations use correct interest stop date
```

**Evidence Standards** (Fact Checker):
```
□ Evidence distinguished from declaration materials
□ All facts cite specific evidence source
□ Timeline chronologically ordered
□ No unauthorized modifications to declaration
```

**Calculation Standards** (Debt Analyst):
```
□ ALL calculations use calculator tool
□ Calculation commands documented
□ Excel/CSV process files generated
□ LPR term selection reviewed (1y vs 5y)
□ Penalty caps verified (4× LPR maximum)
```

**Consolidation Standards** (Report Organizer):
```
□ Content accuracy preserved (no modifications)
□ Template format applied correctly
□ File naming complies with standards
□ Directory structure complete
```

## Part 9: Common Error Prevention

### High-Frequency Errors (Top 3)

**Error 1: LPR Term Selection for Long-Term Debts**
- **Problem**: Using 1-year LPR for debts >5 years without review
- **Prevention**: MUST calculate debt period and consider 5-year+ LPR if >5 years

**Error 2: Daily Rate Conversion Errors**
- **Problem**: Converting daily rates with wrong base (365 vs 360 confusion)
- **Prevention**: Use direct formula: 日利率 × 天数 × 本金 (avoid conversion)

**Error 3: Vague Statute Interruption Dates**
- **Problem**: Recording interruptions as "申报前" without specific date
- **Prevention**: MUST record specific date with evidence support

### Critical Rules to Remember

```
✅ DO:
- Verify bankruptcy dates FIRST (before any work)
- Use calculator tool for ALL calculations
- Record specific dates (not vague references)
- Apply 就低/就无 principles
- Generate calculation process files

❌ DO NOT:
- Modify calculation results
- Add items creditor didn't declare
- Calculate without calculator tool
- Use wrong LPR term for long debts
- Omit evidence citations
```

## Part 10: File and Directory Standards

### Standard Directory Structure

```
输出/第X批债权/[序号]-[债权人名称]/
├── 最终报告/                # Client deliverables
│   ├── [项目代码]_[债权人]_债权审查报告_[日期].md
│   └── 附件/
├── 工作底稿/                # Working papers (audit trail)
│   ├── [债权人]_事实核查报告.md
│   ├── [债权人]_债权分析报告.md
│   └── 原始申报材料/
└── 计算文件/                # Calculation process files
    ├── [编号]-[债权人]-[类型].xlsx
    └── [编号]-[债权人]-无计算项说明.txt (if applicable)
```

### File Naming Patterns

**Fact-checking report**: `{债权人名称}_事实核查报告.md`
**Debt analysis report**: `{债权人名称}_债权分析报告.md`
**Review opinion form**: `[项目代码]_{债权人名称}_债权审查报告_{YYYYMMDD}.md`
**Calculation files**: `[编号]-[债权人名称]-[类型].xlsx`

## Part 11: Workflow Initialization (MANDATORY)

### Pre-Processing Requirement

**⚠️ CRITICAL**: Before processing ANY creditor, MUST run:

```bash
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

**What This Does**:
- Creates standard directory structure
- Generates `.processing_config.json` with bankruptcy dates
- Prepares environment for three agents

**Verification**:
```
□ Standard directories created (工作底稿/, 最终报告/, 计算文件/)
□ .processing_config.json file exists
□ Configuration contains bankruptcy dates
```

**If NOT initialized**: DO NOT proceed with any agent work.

## Part 12: Key Reference Documents

### For Detailed Procedures

**Legal Standards**: See `legal_standards_reference.md`
- Full text of applicable laws
- Supreme Court interpretations
- Legal principle applications

**Calculation Formulas**: See `calculation_formulas_reference.md`
- All interest calculation formulas
- LPR rate data table
- Penalty caps and special rules

**Terminology**: See `common_terms_glossary.md`
- Complete glossary of debt review terms
- Chinese-English mappings
- Usage examples

## Summary

This foundations skill provides:

1. **System Architecture**: Three-agent collaborative workflow
2. **Core Principles**: 就低, 就无, evidence support, substance over form
3. **Classification Systems**: Priority, nature, legal relationship types
4. **Evidence Hierarchy**: Legal documents > Confirmations > Contracts > Unilateral
5. **Critical Dates**: Bankruptcy date (lifeline-level) and interest stop date
6. **Quality Standards**: Universal checklists and error prevention
7. **Tool Standards**: Calculator tool mandatory usage
8. **File Standards**: Directory structure and naming conventions

**Golden Rules**:
- **Date verification is MANDATORY** - First step, no exceptions
- **Use calculator for ALL calculations** - Zero manual calculations
- **Apply 就低/就无 principles** - Respect creditor's claim scope
- **Preserve evidence trail** - All work traceable to source
- **Sequential processing** - Complete one claim before starting next

**For specific workflows**: See individual agent skills (debt-fact-checking, debt-claim-analysis, report-organization)

**For detailed references**: See reference guides in `references/` directory
