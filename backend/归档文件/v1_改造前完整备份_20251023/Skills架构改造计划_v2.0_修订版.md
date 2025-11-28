# 债权审查系统Skills架构改造计划 v2.0（修订版）

**文档目的**: 指导债权审查系统从传统Agent模式向Skills架构迁移
**改造日期**: 2025-10-23
**参考文档**:
- `Skills架构改造指南_通用模式.md`
- Claude Code官方文档: https://docs.claude.com/zh-CN/docs/claude-code/skills
- Agent Skills最佳实践: https://docs.claude.com/zh-CN/docs/agents-and-tools/agent-skills/best-practices

**预计完成时间**: 2-3个工作日（12-18小时）

**版本变化**:
- v1.0: 初始计划（4个Skills）
- **v2.0**: 基于官方文档修订，澄清Skills机制，增加workflow-orchestration skill（5个Skills）

---

## 📊 一、现状分析

### 1.1 当前架构概览

```
传统模式:
├── 3个Agent定义文件 (180-205行/个)
│   ├── debt-fact-checker.md
│   ├── debt-claim-analyzer.md
│   └── report-organizer.md
│
├── 3个工作标准文档 (1071+1109+228=2408行，核心知识库)
│   ├── 事实核查员工作标准.md
│   ├── 债权分析员工作标准.md
│   └── 报告整理员工作标准.md
│
├── 主控制器SOP (~500行)
│   └── 智能体债权审查SOP.md
│
├── 3个模板文件 (~800行)
│   ├── 事实核查报告模板.md
│   ├── 债权分析报告模板.md
│   └── 审查意见表模板.md
│
├── 工具脚本 (3个Python文件)
│   ├── 债权处理工作流控制器.py
│   ├── 环境初始化检查器.py
│   └── universal_debt_calculator_cli.py
│
└── 配置文件
    ├── project_config.ini
    └── CLAUDE.md
```

### 1.2 核心问题识别

| 问题类型 | 具体表现 | 改造必要性 |
|---------|---------|-----------|
| **内容分散** | 工作标准文档独立于Agent定义 | ⚠️ 高 |
| **知识冗余** | Agent定义中重复引用标准文档 | ⚠️ 中 |
| **维护困难** | 更新标准时需同步修改多处 | ⚠️ 高 |
| **加载低效** | 每次调用都需加载完整标准文档(>1000行) | ⚠️ 高 |
| **主控逻辑复杂** | SOP.md有500行，难以快速理解 | ⚠️ 高 |

### 1.3 改造优势预期

✅ **渐进式揭示**: SKILL.md提供核心工作流(<500行)，详细内容按需访问
✅ **模块化管理**: 每个Skill独立维护，便于版本控制
✅ **自动发现**: Claude根据任务需求自动激活相关Skills
✅ **可复用性**: Skills可在不同项目间复用
✅ **降低token消耗**: 按需加载references，减少context占用

---

## 🎯 二、改造目标架构（修订）

### 2.1 Skills结构设计

**⚠️ 重要概念澄清**：

根据官方文档，Skills是**model-invoked**（模型调用），而非"绑定到Agent"：
- Skills在Claude Code启动时**全部加载**
- Claude根据用户请求和Skill的description**自主决定**何时使用
- Skills是**功能模块**，不是"Agent的附属品"

**修订后方案**: 5个功能模块Skill

```
Skills模式:
.claude/skills/
├── debt-fact-checking/              # 事实核查功能模块
│   ├── SKILL.md                     # 核心工作流 (~350行)
│   ├── references/
│   │   ├── declaration_extraction_guide.md      # 申报信息提取（合并）
│   │   ├── evidence_and_facts_guide.md          # 证据分类+事实关系（合并）
│   │   ├── batch_processing_guide.md            # 超长材料分批处理
│   │   └── quality_checklist.md                 # 错误防范+时间线
│   ├── templates/
│   │   └── fact_checking_report_template.md
│   └── assets/examples/
│
├── debt-claim-analysis/             # 债权分析功能模块
│   ├── SKILL.md                     # 核心工作流 (~400行)
│   ├── references/
│   │   ├── amount_and_interest_guide.md         # 金额拆解+利息计算（合并）
│   │   ├── calculator_usage_guide.md            # 计算器使用说明
│   │   ├── statute_limitations_guide.md         # 时效判断指南
│   │   └── quality_control_guide.md             # 质量控制+错误防范
│   ├── templates/
│   │   └── debt_analysis_report_template.md
│   └── assets/examples/
│
├── report-organization/             # 报告整理功能模块
│   ├── SKILL.md                     # 核心工作流 (~250行)
│   ├── references/
│   │   ├── content_and_mapping_guide.md         # 内容提取+模板映射（合并）
│   │   └── file_organization_guide.md           # 文件组织+命名规范（合并）
│   ├── templates/
│   │   └── review_opinion_template.md
│   └── assets/examples/
│
├── debt-review-foundations/         # 项目配置和基础知识
│   ├── SKILL.md                     # 项目基础知识 (~200行)
│   ├── references/
│   │   ├── project_config_guide.md              # 项目配置详解
│   │   ├── directory_structure_guide.md         # 目录结构规范
│   │   └── date_verification_protocol.md        # 日期验证协议（关键）
│   └── config/
│       └── project_config.ini (reference copy)
│
└── debt-workflow-orchestration/     # ⭐ 新增：主控智能体工作流编排
    ├── SKILL.md                     # 编排核心 (~350行)
    ├── references/
    │   ├── initialization_protocol.md           # 环境初始化协议（MANDATORY）
    │   ├── agent_coordination_guide.md          # Agent协调和顺序
    │   ├── quality_checkpoints_guide.md         # 质量检查点
    │   ├── batch_orchestration_guide.md         # 批量处理编排
    │   └── error_recovery_guide.md              # 错误恢复流程
    └── scripts/
        ├── 债权处理工作流控制器.py (reference copy)
        └── 环境初始化检查器.py (reference copy)
```

### 2.2 Skills功能映射表（修订）

| Skill名称 | 主要使用场景 | 核心职责 | SKILL.md行数 |
|----------|------------|---------|-------------|
| **debt-fact-checking** | 处理债权申报材料、组织证据 | 申报信息组织、事实关系建立 | ~350行 |
| **debt-claim-analysis** | 金额分析、利息计算、时效判断 | 金额拆解、利息计算、时效判断 | ~400行 |
| **report-organization** | 合并报告、生成审查意见表 | 报告合并、模板应用、文件组织 | ~250行 |
| **debt-review-foundations** | 项目配置、基础知识查询 | 项目配置、日期验证、目录规范 | ~200行 |
| **debt-workflow-orchestration** | ⭐ 工作流编排、质量控制 | 环境初始化、Agent协调、检查点 | ~350行 |

**⚠️ 关键变化**：
- 不再强调"Agent专属Skill"
- Skills作为功能模块，Claude自动发现并使用
- 主控智能体也有专属skill（debt-workflow-orchestration）

### 2.3 YAML Frontmatter规范（修订）

**官方限制**：
- `name`: 最大64字符，小写字母+数字+连字符
- `description`: 最大**1024字符**

**修订后示例**：

```yaml
---
name: debt-fact-checking
description: Extract and verify debt claim information from bankruptcy materials. Organizes creditor declarations, classifies evidence across 9 legal relationship types, establishes factual relationships, and creates case timelines. Use for initial debt claim review and evidence organization tasks.
---
```

**❌ 避免**：
```yaml
# 不要列举关键词
description: ... Triggers on keywords: fact-check, 事实核查, evidence organization
# 不要超过1024字符
description: [300字的长描述]
```

**✅ 推荐**：
- 自然描述功能和使用场景
- 控制在200-400字符
- 关键词自然融入描述

---

## 📋 三、详细改造步骤（修订）

### 阶段0: 准备工作 (1小时)

#### Step 0.1: 创建备份
```bash
# 创建完整备份
mkdir -p 归档文件/v1_改造前完整备份_$(date +%Y%m%d)
cp -r .claude/ 归档文件/v1_改造前完整备份_$(date +%Y%m%d)/
cp *.md *.py *.ini 归档文件/v1_改造前完整备份_$(date +%Y%m%d)/ 2>/dev/null || true
```

#### Step 0.2: 创建Skills目录结构
```bash
# 创建5个Skill包的基础目录
mkdir -p .claude/skills/debt-fact-checking/{references,templates,assets/examples}
mkdir -p .claude/skills/debt-claim-analysis/{references,templates,assets/examples}
mkdir -p .claude/skills/report-organization/{references,templates,assets/examples}
mkdir -p .claude/skills/debt-review-foundations/{references,config}
mkdir -p .claude/skills/debt-workflow-orchestration/{references,scripts}
```

#### Step 0.3: 学习官方文档
- 阅读官方Skills文档
- 理解model-invoked机制
- 理解progressive disclosure原则

---

### 阶段1: Skill 1改造 - debt-fact-checking (3小时)

#### Step 1.1: 创建SKILL.md核心文件

**内容来源**:
- `事实核查员工作标准.md` (1071行) → 提取核心工作流
- `.claude/agents/debt-fact-checker.md` (180行) → 提取关键约束

**SKILL.md结构** (~350行):

```markdown
---
name: debt-fact-checking
description: Extract and verify debt claim information from bankruptcy materials. Organizes creditor declarations, classifies evidence across 9 legal relationship types, establishes factual relationships, and creates case timelines. Use for initial debt claim review and evidence organization tasks.
---

# Debt Fact-Checking Skill

## Overview
Systematic fact-checking and evidence organization for bankruptcy debt claims. This skill provides the methodology for processing creditor declaration materials, extracting structured information, and establishing factual relationships based on evidence.

## When to Use This Skill
- Processing creditor declaration materials (申报材料)
- Organizing evidence and establishing factual relationships
- Creating case timelines for debt claims
- Initial review of debt claim submissions
- Batch processing of multiple evidence items

## Core Workflow (6-Step Process)

### Step 1: Material Reception and Assessment
**Objective**: Understand the scope and complexity of materials

**Actions**:
- Count total pages and evidence items
- Identify primary legal relationship type
- Determine if batch processing is needed (>100 pages or >50 items)

**Batch Processing Trigger**: See `references/batch_processing_guide.md`

### Step 2: Declaration Information Organization
**Objective**: Extract structured creditor information

**Key Elements to Extract**:
- Creditor identification (name, type, contact)
- Declared amounts (total, principal, interest, fees)
- Claim basis summary

**Detailed extraction patterns**: See `references/declaration_extraction_guide.md`

### Step 3: Evidence Classification
**Objective**: Categorize evidence by legal relationship type

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

**Classification standards**: See `references/evidence_and_facts_guide.md`

### Step 4: Factual Relationship Establishment
**Objective**: Build evidence-based factual relationships

**Key Principle**: Distinguish between "申报材料" (declarations) and "证据" (evidence)
- Declarations: What creditor claims
- Evidence: What documents prove

**Detailed methodology**: See `references/evidence_and_facts_guide.md`

### Step 5: Timeline Creation
**Objective**: Establish chronological sequence of key events

**Timeline Table Format**:
| 序号 | 日期 | 事件描述 | 证据来源 |
|-----|------|---------|---------|
| 1   | YYYY-MM-DD | [事件] | [证据编号] |

**Timeline standards**: See `references/quality_checklist.md` § Timeline Creation

### Step 6: Report Generation
**Objective**: Produce《事实核查报告》

**Report Structure**:
- Part 1: 申报信息 (Declaration Information)
- Part 2: 事实关系 (Factual Relationships)
- Part 3: 重要时间线 (Timeline)

**Template**: See `templates/fact_checking_report_template.md`

## Batch Processing Strategy

**When to Apply**:
- Total pages > 100
- Evidence items > 50
- Multiple sub-claims within one creditor

**Strategy**: Process in chunks, then consolidate

**Full guide**: See `references/batch_processing_guide.md`

## Critical Reminders

⚠️ **Date Verification**: Always verify bankruptcy dates from `.processing_config.json` before starting

⚠️ **Evidence vs. Declaration**: Clearly distinguish what is declared vs. what is proven

⚠️ **No Legal Conclusions**: Focus on factual extraction, not legal analysis

## Error Prevention Quick Checklist

**Before Finalizing**:
- [ ] Verified bankruptcy dates from config
- [ ] All amounts extracted without addition errors
- [ ] Evidence properly classified by legal type
- [ ] Timeline chronologically ordered
- [ ] No mixing of declaration and evidence
- [ ] Report follows template structure

**Complete checklist**: See `references/quality_checklist.md`

## Quick Reference

### Common Legal Relationship Types
| 类型 | 关键证据 | 常见要素 |
|-----|---------|---------|
| 借款合同 | 借款协议、转账凭证 | 本金、利率、期限 |
| 买卖合同 | 合同、发票、送货单 | 货物、价款、交付 |
| 建设工程 | 施工合同、结算书 | 工程款、质保金 |

### Batch Processing Decision Tree
```
材料量 > 100页? ─Yes→ 分批处理
    │
    No
    ↓
证据 > 50项? ─Yes→ 分批处理
    │
    No
    ↓
正常处理
```
```

#### Step 1.2: 拆分Reference Guides（修订：4个文件）

**⚠️ 修订原则**: 按主题合并，减少碎片化（从原计划6个减少到4个）

| Reference文件 | 原内容来源 | 预估行数 | 核心内容 |
|--------------|-----------|---------|---------|
| `declaration_extraction_guide.md` | 工作标准.md §2 | 300行 | 申报信息提取标准、字段定义、提取模式 |
| `evidence_and_facts_guide.md` | 工作标准.md §3 + §3.2 | 450行 | 证据分类标准（9类）+ 事实关系建立方法（合并） |
| `batch_processing_guide.md` | 工作标准.md §4 | 250行 | 分批处理策略、触发条件、汇总方法 |
| `quality_checklist.md` | 工作标准.md §5 + 时间线规范 | 300行 | 错误防范 + 时间线创建规范（合并） |

**关键变化**:
- ✅ 从6个文件减少到4个文件
- ✅ 相关主题合并（如：证据分类+事实关系，错误防范+时间线）
- ✅ 每个文件250-450行，主题更聚焦

#### Step 1.3: 迁移模板和资源
```bash
# 模板文件迁移
cp 事实核查报告模板.md .claude/skills/debt-fact-checking/templates/fact_checking_report_template.md

# 创建示例案例目录（可选）
mkdir -p .claude/skills/debt-fact-checking/assets/examples
```

#### Step 1.4: 验证Skill完整性
```bash
# 检查SKILL.md行数
wc -l .claude/skills/debt-fact-checking/SKILL.md
# 预期: <500行

# 检查references完整性
ls -la .claude/skills/debt-fact-checking/references/
# 预期: 4个guide文件
```

---

### 阶段2: Skill 2改造 - debt-claim-analysis (3小时)

#### Step 2.1: 创建SKILL.md核心文件

**内容来源**:
- `债权分析员工作标准.md` (1109行) → 提取核心工作流
- `.claude/agents/debt-claim-analyzer.md` (187行) → 提取关键约束

**SKILL.md结构** (~400行):

```markdown
---
name: debt-claim-analysis
description: Analyze bankruptcy debt claims by breaking down amounts, calculating interest using LPR rates and legal standards, and determining statute of limitations. Produces detailed debt analysis reports with calculation process tables for precise verification.
---

# Debt Claim Analysis Skill

## Overview
Comprehensive debt claim amount analysis, interest calculation, and statute of limitations determination. This skill provides systematic methodologies for analyzing claim amounts, calculating various types of interest using the universal debt calculator tool, and producing calculation audit trails.

## When to Use This Skill
- Analyzing claim amounts and breaking down components
- Calculating interest (simple, LPR, delayed performance, compound)
- Determining statute of limitations for debt claims
- Producing final debt analysis reports with calculation files
- Quality control and cross-validation of debt amounts

## Prerequisites
- Completed fact-checking report from debt-fact-checker
- Access to `universal_debt_calculator_cli.py` tool (in project root)
- Bankruptcy dates verified from `.processing_config.json`

## Core Workflow (5-Step Process)

### Step 1: Receive Fact-Checking Report
**Objective**: Understand established facts and amounts

**Actions**:
- Read《事实核查报告》
- Verify bankruptcy dates match config
- Identify declared amounts vs. proven amounts
- Note legal relationship types

### Step 2: Amount Breakdown Analysis
**Objective**: Systematically decompose claim amounts

**Standard Breakdown Structure**:
```
债权总额
├── 本金 (Principal)
├── 利息 (Interest)
│   ├── 合同期内利息 (Contractual interest)
│   ├── 逾期利息 (Overdue interest)
│   └── 迟延履行期间债务利息 (Delayed performance interest)
├── 违约金 (Penalties)
├── 损害赔偿金 (Damages)
└── 实现债权费用 (Collection costs)
```

**Detailed breakdown methods**: See `references/amount_and_interest_guide.md`

### Step 3: Interest Calculation
**Objective**: Calculate precise interest amounts using calculator tool

**⚠️ MANDATORY**: MUST use `universal_debt_calculator_cli.py`, NEVER manual calculations

**5 Interest Types**:
1. **Simple Interest** (固定利率)
2. **LPR Floating Rate** (LPR浮动利率)
3. **Delayed Performance Interest** (迟延履行期间债务利息)
4. **Compound Interest** (复利)
5. **Penalty Interest** (罚息)

**Calculator Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**Usage Examples**:
```bash
# Simple interest
python universal_debt_calculator_cli.py simple \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --rate 4.35

# LPR floating rate
python universal_debt_calculator_cli.py lpr \
  --principal 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --multiplier 1.5
```

**Complete calculator guide**: See `references/calculator_usage_guide.md`

**Calculation parameters and formulas**: See `references/amount_and_interest_guide.md`

### Step 4: Statute of Limitations Determination
**Objective**: Determine if claims are time-barred

**Key Rules**:
- General statute: 3 years from when creditor knew/should have known
- Interruption events: litigation, arbitration, acknowledgment
- Suspension events: force majeure, legal obstacles

**Detailed rules and examples**: See `references/statute_limitations_guide.md`

### Step 5: Quality Control and Report Generation
**Objective**: Validate results and produce final report

**Quality Control Steps**:
1. Cross-validate amounts against fact-checking report
2. Verify all calculations using calculator output files
3. Check date consistency (bankruptcy dates)
4. Validate report structure

**Output Requirements**:
1. 《债权分析报告》in `工作底稿/`
2. Calculation process tables (Excel/CSV) in `计算文件/`
3. No calculation files → create explanation TXT file

**Template**: See `templates/debt_analysis_report_template.md`

**QC checklist**: See `references/quality_control_guide.md`

## Critical Tools

### Universal Debt Calculator CLI
**Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`

**Key Features**:
- Embedded LPR rate data (2019-2025)
- Automatic calculation process table generation (Excel/CSV)
- Multiple interest calculation modes
- JSON input/output support

**Full documentation**: See `references/calculator_usage_guide.md`

## Error Prevention Quick Checklist

**Before Finalizing**:
- [ ] All interest calculations use calculator tool (no manual calculations)
- [ ] Bankruptcy dates verified and consistent
- [ ] Calculation process tables generated and saved to `计算文件/`
- [ ] Amounts cross-validated against fact-checking report
- [ ] Statute of limitations analysis documented with evidence
- [ ] Report follows template structure

**Complete checklist**: See `references/quality_control_guide.md`

## Quick Reference

### Interest Rate Reference (2024)
| 利率类型 | 参考值 |
|---------|-------|
| 1年期LPR | 3.45% |
| 5年期LPR | 3.95% |
| 法定利率上限 | LPR × 4 |

### Calculation File Naming
```
[债权人编号]-[债权人名称]-[类型].xlsx
例: 115-东航建筑-逾期利息计算表.xlsx
```
```

#### Step 2.2: 拆分Reference Guides（修订：4个文件）

**⚠️ 修订原则**: 按主题合并（从原计划6个减少到4个）

| Reference文件 | 原内容来源 | 预估行数 | 核心内容 |
|--------------|-----------|---------|---------|
| `amount_and_interest_guide.md` | 工作标准.md §2 + §3 | 500行 | 金额拆解方法 + 5类利息计算规则（合并） |
| `calculator_usage_guide.md` | 新建 + 工作标准.md §3.2 | 300行 | CLI工具完整使用说明、参数详解、示例 |
| `statute_limitations_guide.md` | 工作标准.md §4 | 350行 | 时效判断规则、中断/中止、案例 |
| `quality_control_guide.md` | 工作标准.md §5 + §6 | 300行 | 质量检查标准 + 错误防范（合并） |

**关键变化**:
- ✅ 金额拆解和利息计算合并（都是金额相关）
- ✅ 质量控制和错误防范合并（都是QC相关）

#### Step 2.3: 迁移模板
```bash
# 迁移模板
cp 债权分析报告模板.md .claude/skills/debt-claim-analysis/templates/debt_analysis_report_template.md
```

**⚠️ 重要变化：计算器脚本不迁移**

根据修订建议，保留计算器在根目录：
```bash
# 不执行以下命令：
# cp universal_debt_calculator_cli.py .claude/skills/debt-claim-analysis/scripts/

# 在SKILL.md和references中明确引用根目录路径：
# /root/debt_review_skills/universal_debt_calculator_cli.py
```

---

### 阶段3: Skill 3改造 - report-organization (2小时)

#### Step 3.1: 创建SKILL.md核心文件

**内容来源**:
- `报告整理员工作标准.md` (228行) → 几乎全部内容
- `.claude/agents/report-organizer.md` (205行) → 提取关键约束

**SKILL.md结构** (~250行):

```markdown
---
name: report-organization
description: Consolidate technical debt review reports into standardized client deliverables (审查意见表). Merges fact-checking and debt analysis reports, applies client-specific templates, organizes files, and creates comprehensive file inventories.
---

# Report Organization Skill

## Overview
Report consolidation and standardization for bankruptcy debt reviews. This skill provides the methodology for merging technical reports into client-ready deliverables following standardized templates and file organization conventions.

## When to Use This Skill
- Consolidating fact-checking and debt analysis reports
- Generating standardized 审查意见表 (review opinion forms)
- Organizing final deliverables and calculation files
- Creating file inventories
- Applying client-specific templates

## Prerequisites
- Completed fact-checking report in `工作底稿/`
- Completed debt analysis report in `工作底稿/`
- All calculation files in `计算文件/`

## Core Workflow (4-Step Process)

### Step 1: Report Collection
**Objective**: Gather all technical outputs

**Required Files**:
- 《事实核查报告》from `工作底稿/`
- 《债权分析报告》from `工作底稿/`
- Calculation files (Excel/CSV) from `计算文件/`
- Explanation files (TXT) if no calculations

**Validation**: Verify all files exist and follow naming conventions

### Step 2: Template Loading and Content Extraction
**Objective**: Apply standardized review opinion template

**Template Structure**:
```
审查意见表
├── 一、债权人基本情况
├── 二、申报债权情况
├── 三、事实关系
├── 四、债权金额分析
├── 五、诉讼时效
├── 六、审查意见
└── 七、附件清单
```

**Content Extraction Rules**: See `references/content_and_mapping_guide.md`

**Template Mapping Logic**: See `references/content_and_mapping_guide.md`

### Step 3: Review Opinion Form Generation
**Objective**: Produce final《审查意见表》

**Key Principles**:
- Preserve factual accuracy from source reports
- Apply consistent formatting per template
- Maintain professional tone
- Cross-reference calculation files

**Output Location**: `最终报告/[债权人编号]-[债权人名称]-审查意见表.md`

**Template**: See `templates/review_opinion_template.md`

### Step 4: File Organization and Inventory
**Objective**: Organize all deliverables and create inventory

**Standard Directory Structure**:
```
[债权人目录]/
├── 工作底稿/
│   ├── [债权人]-事实核查报告.md
│   └── [债权人]-债权分析报告.md
├── 计算文件/
│   ├── [债权人]-利息计算表.xlsx
│   └── [债权人]-计算说明.txt
└── 最终报告/
    └── [债权人]-审查意见表.md
```

**File Inventory Creation**:
Generate `文件清单.md` listing all files with:
- File name
- File type
- Location
- Brief description

**File organization standards**: See `references/file_organization_guide.md`

## Quality Checkpoints

**Before Finalizing**:
- [ ] All source reports collected
- [ ] Template applied correctly
- [ ] Content accurately extracted (no additions/deletions)
- [ ] Calculation files properly referenced
- [ ] File naming conventions followed
- [ ] File inventory complete and accurate

## Quick Reference

### Template Section Mapping
| 审查意见表章节 | 来源报告 | 对应章节 |
|-------------|---------|---------|
| 一、债权人基本情况 | 事实核查报告 | 申报信息 § 债权人信息 |
| 二、申报债权情况 | 事实核查报告 | 申报信息 § 申报金额 |
| 三、事实关系 | 事实核查报告 | 事实关系 |
| 四、债权金额分析 | 债权分析报告 | 金额拆解 |
| 五、诉讼时效 | 债权分析报告 | 时效判断 |
| 六、审查意见 | 综合 | 新生成 |

### File Naming Convention
```
工作底稿: [编号]-[名称]-事实核查报告.md
         [编号]-[名称]-债权分析报告.md
计算文件: [编号]-[名称]-[类型].xlsx
最终报告: [编号]-[名称]-审查意见表.md
```
```

#### Step 3.2: 拆分Reference Guides（修订：2个文件）

**⚠️ 修订原则**: 大幅简化（从原计划4个减少到2个）

| Reference文件 | 原内容来源 | 预估行数 | 核心内容 |
|--------------|-----------|---------|---------|
| `content_and_mapping_guide.md` | 工作标准.md §2 + §3 | 300行 | 内容提取规则 + 模板映射逻辑（合并） |
| `file_organization_guide.md` | 工作标准.md §4 | 250行 | 目录结构 + 文件命名规范（合并） |

**关键变化**:
- ✅ 从4个文件减少到2个文件
- ✅ 内容提取和模板映射高度相关，合并
- ✅ 文件组织和命名规范高度相关，合并

#### Step 3.3: 迁移模板
```bash
cp 审查意见表模板.md .claude/skills/report-organization/templates/review_opinion_template.md
```

---

### 阶段4: Skill 4创建 - debt-review-foundations (2小时)

#### Step 4.1: 创建SKILL.md核心文件

**内容来源**:
- `CLAUDE.md` → 提取项目说明
- `project_config.ini` → 配置说明

**SKILL.md结构** (~200行):

```markdown
---
name: debt-review-foundations
description: Core project configuration and foundational knowledge for the debt review system. Provides bankruptcy case settings, directory structure standards, and critical date verification protocols. Use when initializing the project or looking up configuration details.
---

# Debt Review Foundations Skill

## Overview
Foundational knowledge and configuration management for the bankruptcy debt review system. This skill contains project-specific settings, directory structure standards, and the critical date verification protocol that ensures accuracy across all debt analyses.

## When to Use This Skill
- Understanding project configuration
- Looking up bankruptcy case details
- Verifying directory structure standards
- Reviewing date verification protocols
- Understanding overall system architecture

## Critical Configuration

### Project Configuration (project_config.ini)
**Location**: `/root/debt_review_skills/project_config.ini`

**Key Settings**:
```ini
[CaseInfo]
debtor_name = 某某建设集团有限公司
bankruptcy_date = 2024-06-15
interest_stop_date = 2024-06-14

[Paths]
input_dir = /root/debt_review_solution/输入
output_dir = /root/debt_review_solution/输出
```

**Full configuration reference**: See `references/project_config_guide.md`

### Date Verification Protocol ⚠️ LIFE-CRITICAL

**⚠️ 破产受理日期是债权审查的生命线！**

**Why Critical**:
- Determines all legal deadlines
- Affects all interest calculations
- Wrong dates = Invalid entire analysis

**Mandatory Verification**:
1. Read dates from `.processing_config.json` in each creditor directory
2. Cross-verify with `project_config.ini`
3. Document dates used in all reports
4. Stop immediately if any inconsistency found

**Full protocol**: See `references/date_verification_protocol.md`

## Directory Structure Standards

**Standard Structure**:
```
/root/debt_review_solution/
├── 输入/                          # Raw materials
│   ├── 第1批债权/
│   │   ├── 115.债权人名称.md
│   │   └── ...
│   └── 第2批债权/
│
├── 输出/                          # Processing results
│   ├── 第1批债权/
│   │   └── 115-债权人名称/
│   │       ├── .processing_config.json  # ⚠️ Contains bankruptcy dates
│   │       ├── 工作底稿/
│   │       ├── 计算文件/
│   │       └── 最终报告/
│   └── ...
│
├── project_config.ini            # Project configuration
└── [tool scripts]
```

**Detailed guide**: See `references/directory_structure_guide.md`

## Multi-Agent System Overview

**Three-Agent Sequential Model**:
```
1. debt-fact-checker → 事实核查报告 (to 工作底稿/)
2. debt-claim-analyzer → 债权分析报告 + 计算文件 (to 工作底稿/ + 计算文件/)
3. report-organizer → 审查意见表 + 文件清单 (to 最终报告/)
```

**Each agent must**:
- Verify bankruptcy dates from `.processing_config.json`
- Output to correct directories
- Follow file naming conventions

## Quick Reference

### Critical Dates Verification
```bash
# Check dates in creditor directory
cat 输出/第1批债权/115-债权人名称/.processing_config.json

# Verify against project config
cat project_config.ini
```

### Environment Initialization
```bash
# MANDATORY before processing each creditor
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>

# Example
python 债权处理工作流控制器.py 1 115 某某公司
```
```

#### Step 4.2: 创建Reference Guides (3个文件)

| Reference文件 | 原内容来源 | 预估行数 | 核心内容 |
|--------------|-----------|---------|---------|
| `project_config_guide.md` | CLAUDE.md + project_config.ini | 200行 | 项目配置详解、参数说明 |
| `directory_structure_guide.md` | CLAUDE.md + SOP | 200行 | 目录规范、输入输出分离 |
| `date_verification_protocol.md` | CLAUDE.md §日期验证 | 200行 | 日期验证协议详解（重点强化） |

#### Step 4.3: 复制配置文件（作为参考）
```bash
# 复制配置文件作为参考（注意：不迁移，仅复制）
cp project_config.ini .claude/skills/debt-review-foundations/config/
```

---

### 阶段5: ⭐ Skill 5创建 - debt-workflow-orchestration (3小时)

**⚠️ 新增Skill - 主控智能体专用**

#### Step 5.1: 创建SKILL.md核心文件

**内容来源**:
- `智能体债权审查SOP.md` (500行) → 提取核心流程概览
- `CLAUDE.md` §主控制者责任 → 提取编排规则

**SKILL.md结构** (~350行):

```markdown
---
name: debt-workflow-orchestration
description: Orchestrates the complete debt review workflow including environment initialization, multi-agent coordination, quality checkpoints, and batch processing. Provides the master controller with coordination protocols, mandatory initialization steps, and quality control procedures for bankruptcy debt claim processing.
---

# Debt Workflow Orchestration Skill

## Overview
Master workflow orchestration for the three-agent debt review system. This skill provides the main controller (you) with the protocols and procedures for coordinating environment initialization, agent sequencing, quality checkpoints, and batch processing across multiple debt claims.

## When to Use This Skill
- Orchestrating complete debt claim processing workflows
- Coordinating multiple agents in sequence
- Managing batch processing of multiple creditors
- Implementing quality control checkpoints
- Recovering from errors or partial failures
- Understanding the overall system workflow

## Core Responsibilities

### 1. Environment Initialization (MANDATORY) ⚠️

**Before processing ANY creditor, you MUST**:

```bash
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

**What this script does**:
- Creates standard directory structure
- Generates `.processing_config.json` with bankruptcy dates
- Sets up `工作底稿/`, `计算文件/`, `最终报告/` directories
- Validates environment readiness

**Verification**:
```bash
python 环境初始化检查器.py <批次号> <债权人编号> <债权人名称>
```

**If initialization fails**: STOP - do NOT call any agents

**Detailed protocol**: See `references/initialization_protocol.md`

### 2. Agent Coordination (Strict Sequencing) ⚠️

**Mandatory Sequence**:
```
Step 1: debt-fact-checker
  ↓ (generates 事实核查报告 to 工作底稿/)
Checkpoint: Verify report exists
  ↓
Step 2: debt-claim-analyzer
  ↓ (generates 债权分析报告 + 计算文件)
Checkpoint: Verify report + calculation files exist
  ↓
Step 3: report-organizer
  ↓ (generates 审查意见表 + 文件清单)
Checkpoint: Verify final deliverables
  ↓
DONE
```

**Never skip or reorder agents** - dependencies exist between stages

**Coordination details**: See `references/agent_coordination_guide.md`

### 3. Quality Checkpoints (After Each Agent) ⚠️

**After debt-fact-checker**:
- [ ] 事实核查报告 exists in `工作底稿/`
- [ ] Report contains: 申报信息 + 事实关系 + 时间线
- [ ] Bankruptcy dates verified

**After debt-claim-analyzer**:
- [ ] 债权分析报告 exists in `工作底稿/`
- [ ] Calculation files exist in `计算文件/` (or explanation TXT)
- [ ] Dates consistent with fact-checking report

**After report-organizer**:
- [ ] 审查意见表 exists in `最终报告/`
- [ ] 文件清单.md exists
- [ ] All files properly named and located

**Complete checklist**: See `references/quality_checkpoints_guide.md`

### 4. Batch Processing Orchestration

**Single Creditor Mode** (default):
- Process one creditor completely before moving to next
- Complete all 3 agents + checkpoints
- Verify all outputs before proceeding

**Multiple Creditors in Batch**:
```
For each creditor in batch:
  1. Initialize environment
  2. Run 3-agent sequence
  3. Complete quality checks
  4. Move to next creditor
```

**⚠️ NEVER process multiple creditors in parallel** - process sequentially

**Batch strategies**: See `references/batch_orchestration_guide.md`

## Critical Date Verification Protocol (LIFE-CRITICAL) 🚨

**Why Critical**:
破产受理日期是债权审查的生命线 - A single date error invalidates the entire analysis!

**Your Responsibilities**:
1. Verify bankruptcy dates from `project_config.ini` at project start
2. Ensure each agent reads dates from `.processing_config.json`
3. Cross-check dates are consistent across all reports
4. STOP immediately if any date inconsistency found

**Protocol details**: See `debt-review-foundations` skill § Date Verification Protocol

## Error Recovery

**Common Errors and Recovery**:

| Error | Recovery Action |
|-------|-----------------|
| Environment initialization failed | Re-run 债权处理工作流控制器.py, check parameters |
| Agent output missing | Re-run specific agent, check error logs |
| Date inconsistency | STOP, verify `project_config.ini`, check `.processing_config.json` |
| Calculation file missing | Re-run debt-claim-analyzer |
| File in wrong location | Move file, update 文件清单.md |

**Full recovery guide**: See `references/error_recovery_guide.md`

## Standard Workflow (Complete Process)

### Process Single Creditor

```
Phase 0: Preparation
└─> Load project_config.ini (get bankruptcy dates)
└─> Identify creditor materials in 输入/

Phase 1: Environment Setup
└─> Run 债权处理工作流控制器.py
└─> Verify with 环境初始化检查器.py

Phase 2: Fact-Checking
└─> Call debt-fact-checker agent (via Task tool)
└─> Checkpoint: Verify 事实核查报告 in 工作底稿/

Phase 3: Debt Analysis
└─> Call debt-claim-analyzer agent (via Task tool)
└─> Checkpoint: Verify 债权分析报告 + 计算文件

Phase 4: Report Organization
└─> Call report-organizer agent (via Task tool)
└─> Checkpoint: Verify 审查意见表 + 文件清单 in 最终报告/

Phase 5: Final Validation
└─> Review all outputs
└─> Confirm no scattered files
└─> Mark creditor as complete
```

## Tools and Scripts

### Workflow Controller
**Script**: `/root/debt_review_skills/债权处理工作流控制器.py`
**Purpose**: Initialize environment for each creditor
**When**: Before processing ANY creditor

### Environment Checker
**Script**: `/root/debt_review_skills/环境初始化检查器.py`
**Purpose**: Validate environment setup
**When**: After initialization, or for debugging

**Script details**: See `references/initialization_protocol.md`

## Quick Reference

### Standard Agent Call Pattern
```
User → Main Controller → Task tool (subagent_type=debt-fact-checker)
                       → Task tool (subagent_type=debt-claim-analyzer)
                       → Task tool (subagent_type=report-organizer)
```

### Checkpoint Decision Tree
```
Agent completed
  ↓
Expected files exist? ─No→ Re-run agent or investigate error
  ↓ Yes
Dates consistent? ─No→ STOP, verify configuration
  ↓ Yes
File naming correct? ─No→ Rename files
  ↓ Yes
Proceed to next agent
```
```

#### Step 5.2: 创建Reference Guides (5个文件)

| Reference文件 | 原内容来源 | 预估行数 | 核心内容 |
|--------------|-----------|---------|---------|
| `initialization_protocol.md` | SOP §环境初始化 + CLAUDE.md | 300行 | 环境初始化协议、脚本使用、验证步骤 |
| `agent_coordination_guide.md` | SOP §Agent协调 + CLAUDE.md | 350行 | Agent调用顺序、依赖关系、Task tool使用 |
| `quality_checkpoints_guide.md` | SOP §质量检查 + CLAUDE.md | 300行 | 详细检查清单、验证标准 |
| `batch_orchestration_guide.md` | SOP §批量处理 | 250行 | 批量处理策略、顺序处理规则 |
| `error_recovery_guide.md` | 新建 + SOP | 250行 | 常见错误、恢复流程、调试方法 |

#### Step 5.3: 复制脚本（作为参考）
```bash
# 复制脚本作为参考（注意：不迁移，仅复制）
cp 债权处理工作流控制器.py .claude/skills/debt-workflow-orchestration/scripts/
cp 环境初始化检查器.py .claude/skills/debt-workflow-orchestration/scripts/
```

---

### 阶段6: 更新Agent定义文件 (1.5小时)

**⚠️ 修订原则**：
- 不强调"Skill绑定"（Skills是自动发现的）
- 保留核心职责定义
- 移除手动READ指令
- 精简但保持独立性

#### Step 6.1: 更新debt-fact-checker.md

**改造后预期**: ~120行

```markdown
---
name: debt-fact-checker
description: Specialized agent for extracting and verifying debt claim information from bankruptcy materials in a three-stage debt review process
model: sonnet
color: yellow
---

You are a specialized Debt Fact Checker (事实核查员), the first stage in a three-stage debt claim review process.

## Core Mission

Extract and verify factual information from creditor declaration materials, organizing evidence and establishing factual relationships based on submitted documents. Your output serves as the foundation for subsequent debt analysis.

## Key Responsibilities

1. **Declaration Information Organization**: Extract structured creditor information and declared amounts
2. **Evidence Classification**: Categorize evidence by legal relationship type (9 categories)
3. **Factual Relationship Establishment**: Build evidence-based factual relationships
4. **Timeline Creation**: Establish chronological sequence of key events
5. **Report Generation**: Produce independent《事实核查报告》

## Critical Constraints

⚠️ **Date Verification MANDATORY**: Always verify bankruptcy dates from `.processing_config.json` before starting work. Wrong dates invalidate the entire analysis.

⚠️ **Evidence vs. Declaration**: Clearly distinguish between what creditor declares and what evidence proves. Never conflate the two.

⚠️ **No Legal Conclusions**: Focus on factual extraction only. Do not make legal judgments or conclusions about claim validity.

⚠️ **Batch Processing**: Apply batch processing for materials >100 pages or >50 evidence items.

## Output Requirements

Generate independent《事实核查报告》following standard structure:
- Part 1: 申报信息 (Declaration Information)
- Part 2: 事实关系 (Factual Relationships)
- Part 3: 重要时间线 (Timeline)

**Output location**: `工作底稿/[债权人编号]-[债权人名称]-事实核查报告.md`

## Workflow Reference

Follow systematic 6-step workflow for fact-checking:
1. Material Reception and Assessment
2. Declaration Information Organization
3. Evidence Classification
4. Factual Relationship Establishment
5. Timeline Creation
6. Report Generation

## Quality Standards

Before finalizing, verify:
- Bankruptcy dates match `.processing_config.json`
- All amounts extracted without calculation errors
- Evidence properly classified by legal type
- Timeline chronologically ordered
- Clear distinction between declaration and evidence
- Report follows standard template structure
```

#### Step 6.2: 更新debt-claim-analyzer.md

**改造后预期**: ~130行

```markdown
---
name: debt-claim-analyzer
description: Specialized agent for analyzing debt claim amounts, calculating interest, and determining statute of limitations in bankruptcy proceedings
model: sonnet
color: blue
---

You are a specialized Debt Claim Analyzer (债权分析员), the second stage in a three-stage debt claim review process.

## Core Mission

Perform comprehensive debt claim amount analysis, including systematic amount breakdown, precise interest calculations using the universal calculator tool, statute of limitations determination, and quality control. Your analysis builds upon the fact-checking report and produces calculation audit trails.

## Key Responsibilities

1. **Amount Breakdown Analysis**: Systematically decompose claim amounts into components
2. **Interest Calculation**: Calculate precise interest using universal_debt_calculator_cli.py (MANDATORY)
3. **Statute of Limitations Determination**: Assess whether claims are time-barred
4. **Quality Control**: Cross-validate amounts and verify calculations
5. **Report Generation**: Produce《债权分析报告》with calculation process tables

## Critical Constraints

⚠️ **Calculator Tool MANDATORY**: MUST use `universal_debt_calculator_cli.py` for ALL interest calculations. Location: `/root/debt_review_skills/universal_debt_calculator_cli.py`. NEVER perform manual calculations.

⚠️ **Date Verification MANDATORY**: Verify bankruptcy dates from `.processing_config.json` before starting. Dates must match fact-checking report.

⚠️ **Calculation Files REQUIRED**: Generate Excel/CSV calculation process tables for all interest computations. Save to `计算文件/`. If no calculations needed, create explanation TXT file.

⚠️ **Prerequisites**: Must have completed fact-checking report from debt-fact-checker. Do not proceed without it.

## Output Requirements

Generate two types of outputs:

1. **《债权分析报告》**: Comprehensive analysis report
   - Location: `工作底稿/[债权人编号]-[债权人名称]-债权分析报告.md`

2. **Calculation Process Tables**: Excel/CSV files documenting all calculations
   - Location: `计算文件/[债权人编号]-[债权人名称]-[类型].xlsx`

## Calculator Tool Reference

**Basic Usage Examples**:
```bash
# Simple interest
python universal_debt_calculator_cli.py simple --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --rate 4.35

# LPR floating rate
python universal_debt_calculator_cli.py lpr --principal 100000 --start-date 2024-01-01 --end-date 2024-12-31 --multiplier 1.5
```

**Supported calculation types**: Simple, LPR, Delayed Performance, Compound, Penalty

## Workflow Reference

Follow systematic 5-step workflow:
1. Receive Fact-Checking Report
2. Amount Breakdown Analysis
3. Interest Calculation (using calculator)
4. Statute of Limitations Determination
5. Quality Control and Report Generation

## Quality Standards

Before finalizing, verify:
- All calculations use calculator tool (no manual calculations)
- Bankruptcy dates verified and consistent with fact-checking report
- Calculation process tables generated and saved
- Amounts cross-validated against fact-checking report
- Statute of limitations analysis documented with evidence
- Report follows standard template structure
```

#### Step 6.3: 更新report-organizer.md

**改造后预期**: ~100行

```markdown
---
name: report-organizer
description: Specialized agent for consolidating technical debt reports into standardized client deliverables (审查意见表) in bankruptcy proceedings
model: sonnet
color: green
---

You are a specialized Report Organizer (报告整理员), the final stage in a three-stage debt claim review process.

## Core Mission

Consolidate technical reports (fact-checking and debt analysis) into standardized client-ready deliverables following established templates and file organization conventions. Your outputs are the final deliverables to clients.

## Key Responsibilities

1. **Report Collection**: Gather all technical outputs from previous stages
2. **Template Application**: Apply standardized 审查意见表 template
3. **Content Extraction**: Extract and reorganize content per template structure
4. **File Organization**: Organize all deliverables following naming conventions
5. **Inventory Creation**: Generate comprehensive file inventory

## Critical Constraints

⚠️ **Prerequisites MANDATORY**: Must have both fact-checking report AND debt analysis report before proceeding. Do not start without both.

⚠️ **Content Accuracy**: Extract content accurately from source reports. Do NOT add, delete, or modify factual content. Only reorganize per template.

⚠️ **File Organization**: Ensure all files are in correct locations with proper naming conventions. No scattered files allowed.

## Output Requirements

Generate three types of outputs:

1. **《审查意见表》**: Standardized review opinion form
   - Location: `最终报告/[债权人编号]-[债权人名称]-审查意见表.md`

2. **文件清单.md**: Comprehensive file inventory
   - Location: `最终报告/文件清单.md`

3. **Organized deliverables**: All files properly organized in standard structure

## Template Structure Reference

审查意见表 standard sections:
- 一、债权人基本情况
- 二、申报债权情况
- 三、事实关系
- 四、债权金额分析
- 五、诉讼时效
- 六、审查意见
- 七、附件清单

## Workflow Reference

Follow systematic 4-step workflow:
1. Report Collection (verify all files exist)
2. Template Loading and Content Extraction
3. Review Opinion Form Generation
4. File Organization and Inventory

## Quality Standards

Before finalizing, verify:
- All source reports collected
- Template applied correctly
- Content accurately extracted (no additions/deletions)
- Calculation files properly referenced in 附件清单
- File naming conventions followed
- File inventory complete and accurate
- No files in wrong locations
```

---

### 阶段7: 更新主文档 (1小时)

#### Step 7.1: 更新CLAUDE.md

在CLAUDE.md中添加/更新以下章节：

```markdown
## 🎨 Skills Architecture (v2.0)

This project uses Claude Code Skills for modular knowledge management.

### Available Skills

1. **debt-fact-checking** - Fact-checking and evidence organization
   - Provides methodology for extracting creditor information and establishing factual relationships
   - Location: `.claude/skills/debt-fact-checking/`

2. **debt-claim-analysis** - Amount analysis and interest calculation
   - Provides systematic amount breakdown and interest calculation methods
   - Includes universal debt calculator tool documentation
   - Location: `.claude/skills/debt-claim-analysis/`

3. **report-organization** - Report consolidation and file organization
   - Provides template application and file organization standards
   - Location: `.claude/skills/report-organization/`

4. **debt-review-foundations** - Project configuration and foundational knowledge
   - Contains project settings, directory standards, and date verification protocol
   - Location: `.claude/skills/debt-review-foundations/`

5. **debt-workflow-orchestration** - ⭐ Workflow orchestration for main controller
   - Provides coordination protocols, initialization procedures, and quality checkpoints
   - Location: `.claude/skills/debt-workflow-orchestration/`

### How Skills Work

**Automatic Discovery**: Skills are automatically loaded when Claude Code starts. Claude activates relevant skills based on the task context and skill descriptions. You don't need to manually invoke skills.

**Progressive Disclosure**: Each skill has a concise SKILL.md (<500 lines) for core workflow, with detailed guides in `references/` directory accessed as needed. This reduces context usage while maintaining access to complete information.

**No Manual Loading Required**: When you use agents via Task tool, relevant skills are automatically available. Skills are functional modules, not "bound" to specific agents.

## 📋 主控制者责任 (Updated for v2.0)

**作为债权审查流程的主控制者，你必须：**

### 1. 环境初始化责任 ⚠️ MANDATORY

**在处理每个债权人之前，必须执行：**
```bash
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

**验证初始化完成：**
- 确认标准目录结构已创建
- 确认配置文件 `.processing_config.json` 存在
- 如果环境未初始化，**禁止调用任何Agent**

💡 **Skill Support**: Use `debt-workflow-orchestration` skill for detailed initialization protocols and troubleshooting.

### 2. Agent协调责任

**严格按此顺序执行Agent（使用Task tool）：**
1. **debt-fact-checker** → 生成事实核查报告
2. **debt-claim-analyzer** → 生成债权分析报告和计算文件
3. **report-organizer** → 生成审查意见表和文件清单

💡 **Skill Support**: Use `debt-workflow-orchestration` skill for agent coordination details and quality checkpoints.

### 3. 质量监控责任

**每个Agent完成后验证：**
- 文件存在于正确目录位置
- 文件命名符合规范
- 没有文件散落在错误位置

💡 **Skill Support**: Use `debt-workflow-orchestration` skill § Quality Checkpoints for detailed checklists.

### 4. Skills使用（主控制器）

主控制器可以参考以下skills：
- **debt-workflow-orchestration** - 工作流编排、质量控制、批量处理
- **debt-review-foundations** - 项目配置、日期验证、目录结构

Skills会自动激活，无需手动调用。

## 🔄 标准处理流程 (Updated for v2.0)

The system processes debt claims sequentially:
0. **Load project_config.ini** → Get bankruptcy dates and project info
1. **⚠️ YOU MUST: Initialize environment** → Run 债权处理工作流控制器.py for each creditor
2. Raw materials → debt-fact-checker (Task tool) → structured fact extraction (to `工作底稿/`)
3. Fact report → debt-claim-analyzer (Task tool) → amount analysis & calculations (to `工作底稿/` and `计算文件/`)
4. Two technical reports → report-organizer (Task tool) → 审查意见表 (to `最终报告/` + `文件清单.md`)
5. Final output → Standardized directory structure with all files properly organized

**Important**:
- Skills automatically provide agents with necessary knowledge
- Python tools remain unchanged in root directory
- Each debt claim processed independently
```

#### Step 7.2: 创建迁移说明文档

创建新文件 `Skills架构迁移说明_v2.0.md`：

```markdown
# Skills架构迁移说明 (v1.x → v2.0)

## 主要变化

### 1. 架构模式变化

**v1.x (传统模式)**:
- Agent定义文件包含所有工作标准（180-205行）
- 独立的标准文档（1000+行）
- 需要手动READ标准文档

**v2.0 (Skills模式)**:
- Agent定义文件精简为核心职责（100-130行）
- 知识模块化为5个Skill包
- Skills自动发现和加载

### 2. Agent调用方式变化

**v1.x**:
```
@debt-fact-checker 处理批次第1批债权
```

**v2.0**:
```
使用Task工具调用debt-fact-checker agent，处理批次第1批债权
```

或直接自然语言：
```
请处理批次第1批债权的事实核查
```

### 3. Python工具使用 - 无变化 ✅

所有Python工具保持在根目录，使用方式完全不变：
```bash
# 完全相同，无需修改
python 债权处理工作流控制器.py 1 115 某某公司
python 环境初始化检查器.py 1 115 某某公司
python universal_debt_calculator_cli.py simple --principal 100000 ...
```

### 4. 文件位置变化

| 文件类型 | v1.x位置 | v2.0位置 | 变化 |
|---------|---------|---------|------|
| Agent定义 | `.claude/agents/` | `.claude/agents/` | 位置不变，内容精简 |
| 工作标准 | 根目录独立MD | `.claude/skills/*/` | 模块化为Skills |
| 模板文件 | 根目录 | `.claude/skills/*/templates/` | 集中到Skills |
| Python工具 | 根目录 | **根目录** | ✅ 无变化 |

## 用户操作指南

### 处理单个债权人（完整流程）

```bash
# Step 1: 环境初始化 (无变化)
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>

# Step 2-4: 在Claude对话中
"请使用Task工具调用debt-fact-checker agent，处理批次第1批债权，债权人115-某某公司"
# (等待完成)

"请使用Task工具调用debt-claim-analyzer agent，处理债权人115-某某公司"
# (等待完成)

"请使用Task工具调用report-organizer agent，整理债权人115-某某公司的报告"
# (完成)
```

### 查询项目配置

```
# v2.0: 直接询问，Skills会自动激活
"破产受理日期是什么时候？"
"项目目录结构是怎样的？"
```

## 优势

✅ **更快理解**: SKILL.md <500行，快速掌握核心流程
✅ **按需深入**: 详细内容在references/，需要时才访问
✅ **更易维护**: 知识集中在Skill包内，修改更聚焦
✅ **降低token**: 渐进式加载，减少context占用
✅ **更好复用**: Skills可在不同项目间复用

## 归档文件

v1.x的标准文档已归档到：
```
归档文件/v1_标准文档_被Skills取代_YYYYMMDD/
```

这些文件仅供参考，不再被系统主动使用。
```

#### Step 7.3: 归档旧文件

```bash
# 创建归档目录
mkdir -p 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)

# 归档标准文档
mv 事实核查员工作标准.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/
mv 债权分析员工作标准.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/
mv 报告整理员工作标准.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/

# 归档模板（可选，如果不需要根目录保留）
mv 事实核查报告模板.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/
mv 债权分析报告模板.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/
mv 审查意见表模板.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/

# 可选：归档智能体债权审查SOP.md（部分内容已整合到Skills）
cp 智能体债权审查SOP.md 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/

# 创建归档说明
cat > 归档文件/v1_标准文档_被Skills取代_$(date +%Y%m%d)/README.md << 'EOF'
# v1.x 标准文档归档

**归档日期**: $(date +%Y-%m-%d)
**归档原因**: 已迁移至Skills架构 (v2.0)
**状态**: 仅供参考，已被Skills取代

## 文件映射

- `事实核查员工作标准.md` → `.claude/skills/debt-fact-checking/`
- `债权分析员工作标准.md` → `.claude/skills/debt-claim-analysis/`
- `报告整理员工作标准.md` → `.claude/skills/report-organization/`
- `智能体债权审查SOP.md` → `.claude/skills/debt-workflow-orchestration/`
- 模板文件 → 各Skill的`templates/`目录

## 重要提醒

⚠️ **这些文件不再被Agent主动使用**。所有业务逻辑已完整迁移到Skills中。

如需查看历史版本或对比内容，可参考这些文件。
EOF
```

---

### 阶段8: 验证和测试 (3小时)

#### Step 8.1: 结构验证

```bash
#!/bin/bash
# Skills架构验证脚本

echo "=== 1. 验证所有SKILL.md行数<500 ==="
for skill in .claude/skills/*/SKILL.md; do
    lines=$(wc -l < "$skill")
    skill_name=$(basename $(dirname "$skill"))
    if [ $lines -gt 500 ]; then
        echo "⚠️  $skill_name: $lines lines (>500, 需要精简)"
    else
        echo "✅ $skill_name: $lines lines"
    fi
done

echo -e "\n=== 2. 验证YAML frontmatter ==="
for skill in .claude/skills/*/SKILL.md; do
    skill_name=$(basename $(dirname "$skill"))
    if head -1 "$skill" | grep -q "^---$"; then
        # 检查是否有name和description
        if grep -q "^name:" "$skill" && grep -q "^description:" "$skill"; then
            echo "✅ $skill_name: 完整的frontmatter"
        else
            echo "⚠️  $skill_name: frontmatter缺少name或description"
        fi
    else
        echo "❌ $skill_name: 缺少frontmatter"
    fi
done

echo -e "\n=== 3. 验证references目录 ==="
for skill_dir in .claude/skills/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -d "$skill_dir/references" ]; then
        ref_count=$(find "$skill_dir/references" -name "*.md" 2>/dev/null | wc -l)
        echo "$skill_name: $ref_count reference guides"
    else
        echo "⚠️  $skill_name: 无references目录"
    fi
done

echo -e "\n=== 4. 检查旧路径引用残留 ==="
if grep -r "事实核查员工作标准.md" .claude/ 2>/dev/null; then
    echo "⚠️  发现旧路径引用"
else
    echo "✅ 无旧路径引用"
fi

if grep -r "READ.*标准.md" .claude/agents/ 2>/dev/null; then
    echo "⚠️  发现READ指令残留"
else
    echo "✅ 无READ指令残留"
fi

echo -e "\n=== 5. 验证Python工具位置 ==="
for tool in "债权处理工作流控制器.py" "环境初始化检查器.py" "universal_debt_calculator_cli.py"; do
    if [ -f "$tool" ]; then
        echo "✅ $tool 在根目录"
    else
        echo "❌ $tool 不在根目录"
    fi
done

echo -e "\n=== 验证完成 ==="
```

#### Step 8.2: 功能测试

**测试1: 初始化环境**
```bash
# 创建测试债权人
python 债权处理工作流控制器.py 测试批次 999 测试债权人

# 验证目录结构
ls -R 输出/测试批次/999-测试债权人/

# 预期输出:
# 999-测试债权人/
# ├── .processing_config.json
# ├── 工作底稿/
# ├── 计算文件/
# └── 最终报告/
```

**测试2: Skills自动加载验证**

在Claude对话中：
```
用户: "请使用Task工具调用debt-fact-checker agent，处理测试批次的债权人999-测试债权人"

预期行为:
- debt-fact-checker agent启动
- debt-fact-checking skill自动可用（无需手动加载）
- Agent能够访问skill中的工作流程和references
- 无需手动READ标准文档
```

**测试3: 端到端完整流程**

```
1. 初始化环境
   python 债权处理工作流控制器.py 测试批次 999 测试公司

2. 准备测试材料（简化版）
   创建 输入/测试批次/999.测试公司.md

3. 调用三个Agent（按顺序）
   - debt-fact-checker → 验证生成事实核查报告
   - debt-claim-analyzer → 验证生成债权分析报告+计算文件
   - report-organizer → 验证生成审查意见表+文件清单

4. 验证所有输出
   - 文件位置正确
   - 文件命名符合规范
   - 内容完整
```

**测试4: 主控智能体使用workflow-orchestration skill**

在Claude对话中：
```
用户: "我需要了解完整的债权审查流程和质量检查点"

预期行为:
- Claude自动激活debt-workflow-orchestration skill
- 提供完整流程概览
- 说明质量检查点
- 无需用户手动指定skill
```

#### Step 8.3: 性能对比验证

| 指标 | v1.x | v2.0 | 验证方法 |
|-----|------|------|---------|
| Agent定义行数 | 180-205行 | 100-130行 | `wc -l .claude/agents/*.md` |
| 首次加载内容 | ~1000行标准文档 | ~300-400行SKILL.md | 观察Token使用 |
| References访问 | 全部加载 | 按需加载 | 观察文件读取次数 |
| 知识模块化 | 6个独立MD文件 | 5个Skill包 | 目录结构对比 |

---

## 🎯 四、改造质量检查清单（修订）

### 改造前检查
- [ ] 已创建完整备份
- [ ] 已阅读Claude Code Skills官方文档
- [ ] 已理解model-invoked机制
- [ ] 已规划5个Skills结构

### 改造中检查（每个Skill）
- [ ] SKILL.md <500行
- [ ] YAML frontmatter完整（name + description）
- [ ] Description <1024字符，自然描述使用场景
- [ ] Reference guides按主题合并（避免过度碎片化）
- [ ] 使用相对路径引用references
- [ ] 模板文件正确放置在templates/
- [ ] Python工具脚本**保留在根目录**
- [ ] 无硬编码绝对路径

### Agent定义更新检查
- [ ] 移除所有"READ标准文档"指令
- [ ] **不强调Skill绑定**（Skills自动发现）
- [ ] 保留核心职责定义和关键约束
- [ ] 提供workflow reference（指向skill）
- [ ] 精简至100-130行
- [ ] 无旧路径引用残留

### 主文档更新检查
- [ ] CLAUDE.md添加Skills Architecture章节
- [ ] 说明Skills自动发现机制
- [ ] 更新主控制者责任章节
- [ ] 创建迁移说明文档
- [ ] 说明Python工具使用不变

### 归档检查
- [ ] 旧标准文档已归档
- [ ] 归档目录包含README说明
- [ ] 说明文件映射关系
- [ ] 标记"仅供参考"

### 验证测试检查
- [ ] 所有SKILL.md行数<500
- [ ] 所有YAML frontmatter有效（name + description <1024字符）
- [ ] 无旧路径引用残留
- [ ] Python工具在根目录且可用
- [ ] 环境初始化脚本可用
- [ ] debt-fact-checker agent调用成功
- [ ] debt-claim-analyzer agent调用成功
- [ ] report-organizer agent调用成功
- [ ] Skills自动激活（无需手动加载）
- [ ] 端到端测试通过（初始化→三Agent→生成报告）

---

## 📊 五、改造效果预期（修订）

### 定量指标

| 指标 | v1.x | v2.0预期 | 改进 |
|-----|------|---------|------|
| **Agent定义文件** | 180-205行/个 | 100-130行/个 | -45% |
| **首次加载内容** | ~1000行标准文档 | ~300-400行SKILL.md | -65% |
| **知识模块化程度** | 6个独立MD文件 | 5个Skill包 | 集中化 |
| **Reference guides数量** | 0（全在标准文档） | ~18个（分主题） | 更细粒度 |
| **Skill数量** | 0 | 5个 | 新增 |
| **总SKILL.md行数** | N/A | ~1550行 | 5个skill之和 |
| **维护复杂度** | 高（多文件同步） | 低（Skill内聚） | ⬇️ |

### 定性改进

✅ **用户体验**:
- Skills自动发现，无需手动加载
- Agent调用更自然（Task tool）
- Python工具使用完全不变

✅ **开发维护**:
- 知识集中在Skill包内
- 更新只需修改对应Skill
- 新增Agent更容易（创建新Skill）

✅ **性能优化**:
- 渐进式内容加载
- 减少无效context占用
- References按需访问

✅ **知识管理**:
- 模块化、可复用
- 版本控制友好
- 便于团队协作

### 潜在风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| **业务逻辑丢失** | 高 | 改造前完整备份；逐Skill验证内容完整性 |
| **Skills未正确激活** | 高 | YAML语法验证；description <1024字符检查 |
| **用户学习成本** | 中 | 创建迁移说明；Python工具保持不变 |
| **首次调试复杂** | 中 | 详细测试清单；测试债权人验证 |

---

## 🚀 六、执行建议（修订）

### 执行顺序建议

**推荐方式**: 逐Skill迁移，每个完成后立即测试

```
阶段0 (准备) → 阶段1 (Skill1: debt-fact-checking) → 测试Skill1
              → 阶段2 (Skill2: debt-claim-analysis) → 测试Skill2
              → 阶段3 (Skill3: report-organization) → 测试Skill3
              → 阶段4 (Skill4: debt-review-foundations) → 测试Skill4
              → 阶段5 (Skill5: debt-workflow-orchestration) → 测试Skill5
              → 阶段6 (更新Agent定义) → 集成测试
              → 阶段7 (文档归档) → 最终验证
              → 阶段8 (完整测试)
```

### 时间规划（修订）

| 阶段 | 预计耗时 | 可并行 | 优先级 |
|-----|---------|--------|--------|
| 阶段0: 准备 | 1小时 | ❌ | P0 |
| 阶段1: debt-fact-checking | 3小时 | ❌ | P0 |
| 阶段2: debt-claim-analysis | 3小时 | 与阶段3可并行 | P0 |
| 阶段3: report-organization | 2小时 | 与阶段2可并行 | P0 |
| 阶段4: debt-review-foundations | 2小时 | 与阶段5可并行 | P1 |
| 阶段5: debt-workflow-orchestration | 3小时 | 与阶段4可并行 | P0 |
| 阶段6: 更新Agent定义 | 1.5小时 | ❌ | P0 |
| 阶段7: 文档归档 | 1小时 | ❌ | P1 |
| 阶段8: 验证测试 | 3小时 | ❌ | P0 |
| **总计** | **18.5小时** | | |

**建议分配**: 2-3个工作日完成，每天6-8小时

### 关键成功因素（修订）

1. ✅ **理解Skills机制**: Skills是model-invoked，不是"Agent专属"
2. ✅ **严格遵循<500行规则**: SKILL.md必须保持简洁
3. ✅ **控制description长度**: <1024字符，自然描述
4. ✅ **合理合并references**: 按主题合并，避免过度碎片化
5. ✅ **完整性验证**: 每个Skill迁移后对照原标准文档检查
6. ✅ **YAML语法正确**: frontmatter错误会导致Skill加载失败
7. ✅ **逐步测试**: 不要等全部完成再测试
8. ✅ **保留备份**: 改造过程随时可以回滚

---

## 📝 七、附录

### A. v1.0 vs v2.0 主要变化

| 方面 | v1.0计划 | v2.0修订 | 修订原因 |
|-----|---------|---------|---------|
| **Skills数量** | 4个 | **5个** | 增加workflow-orchestration skill |
| **Skills定位** | Agent专属 | **独立功能模块** | 澄清model-invoked机制 |
| **Description写法** | 列举关键词 | **自然描述场景** | 符合官方规范 |
| **Reference文件数** | 6+6+4+4=20个 | **4+4+2+3+5=18个** | 按主题合并，减少碎片化 |
| **Agent定义更新** | 强调Skill绑定 | **保持独立性** | Skills自动发现 |
| **脚本位置** | 迁移到Skills内 | **保留根目录** | 避免破坏兼容性 |
| **Description长度限制** | 未明确 | **<1024字符** | 官方规范 |

### B. 常见问题（补充）

**Q1: 为什么需要5个Skills而不是4个？**

原计划4个Skills：
- debt-fact-checking
- debt-claim-analysis
- report-organization
- debt-review-foundations

v2.0增加第5个：
- **debt-workflow-orchestration** - 主控智能体专用

原因：
1. 智能体债权审查SOP.md有500行，内容复杂
2. 主控智能体职责关键：环境初始化、Agent协调、质量监控
3. 日期验证协议是"生命线"级别，需要专门强化
4. 参考同类项目（舆情分析系统）也有workflow-orchestration skill

**Q2: Skills如何自动激活？**

官方机制：
- Skills在Claude Code启动时全部加载
- Claude根据用户请求和Skill的description自主决定使用哪个Skill
- 用户无需手动指定或调用Skill

**Q3: 为什么Python工具不迁移到Skills内？**

理由：
1. 避免破坏向后兼容性
2. 用户已熟悉根目录路径
3. 脚本在根目录更易发现和使用
4. Skills中可以引用根目录路径

**Q4: Reference guides如何决定合并还是拆分？**

原则：
- **合并**：高度相关的主题（如：证据分类+事实关系）
- **拆分**：独立的功能模块（如：计算器使用指南）
- 每个guide 250-500行为宜
- 避免过度碎片化（6个→4个）

### C. 参考资源

- **官方文档**:
  - https://docs.claude.com/zh-CN/docs/claude-code/skills
  - https://docs.claude.com/zh-CN/docs/agents-and-tools/agent-skills/best-practices
- **改造指南**: `Skills架构改造指南_通用模式.md`
- **本项目文档**:
  - `CLAUDE.md` (更新后)
  - 各Skill的`SKILL.md`
  - `Skills架构迁移说明_v2.0.md`

---

## ✅ 结语

本改造计划v2.0基于官方文档和最佳实践修订，确保：

1. ✅ **正确理解Skills机制**: model-invoked，自动发现
2. ✅ **符合官方规范**: YAML frontmatter限制、progressive disclosure
3. ✅ **业务完整性**: 所有业务逻辑完整迁移
4. ✅ **向后兼容**: Python工具使用方式不变
5. ✅ **模块化管理**: 5个Skill包，知识集中
6. ✅ **性能优化**: 渐进式加载，降低token消耗
7. ✅ **可测试性**: 每个阶段独立验证
8. ✅ **可回滚**: 完整备份，随时恢复

**与v1.0的关键改进**:
- ✅ 澄清Skills是功能模块，不是"Agent专属"
- ✅ 优化description写法，符合<1024字符限制
- ✅ 减少references碎片化（18个 vs 20个）
- ✅ 增加workflow-orchestration skill（主控智能体）
- ✅ 保留Python工具在根目录（避免破坏兼容性）
- ✅ Agent定义不强调Skill绑定

**下一步**: 获得确认后，按阶段0开始执行改造。

---

**计划版本**: 2.0 (修订版)
**制定日期**: 2025-10-23
**预计完成**: 2-3个工作日 (18.5小时)
**状态**: 待确认执行

**修订说明**: 基于Claude Code官方文档和Skills最佳实践，修正v1.0中对Skills机制的理解偏差，优化改造方案。
