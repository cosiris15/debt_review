# Claude Code 内容分类指南: Skills vs CLAUDE.md

**文档目的**: 提供通用的内容分类标准，帮助在 Claude Code 项目中正确区分哪些内容应该作为 Skills，哪些应该放在 CLAUDE.md 或其他位置。

**适用范围**: 所有使用 Claude Code Skills 架构的项目

**版本**: 1.0
**创建日期**: 2025-10-27
**基于项目**: Debt Review Skills Architecture v2.1

---

## 📚 官方参考文档

在使用本指南前，建议先阅读官方文档：

- **Skills 概述**: https://docs.claude.com/zh-CN/docs/claude-code/skills
- **Skills 最佳实践**: https://docs.claude.com/zh-CN/docs/agents-and-tools/agent-skills/best-practices

本指南基于官方最佳实践，结合实际项目经验，提供更具体的分类标准和决策流程。

---

## 🎯 核心分类原则

### 基本定义

| 类别 | CLAUDE.md | Skills |
|------|-----------|--------|
| **性质** | 控制逻辑 (Control Flow) | 领域知识 (Domain Knowledge) |
| **问题** | "系统如何运行？" | "系统知道什么？" |
| **激活** | 强制加载 (100%) | 按需激活 (上下文匹配) |
| **依赖** | 不能缺失 | 可选参考 |
| **用词** | MUST, NEVER, MANDATORY | 可以使用, 推荐参考 |

### 🔑 持续运行原则 (Continuous Operation Principle)

**核心要求**: 用户发布命令后，系统持续自主运行直到输出最终结果，**零中断、零等待、零手动干预**。

**设计目标**:
```
用户输入命令
    ↓
系统自主运行 (无中断)
    ↓
输出最终结果
```

**禁止场景**:
```
❌ 用户输入命令
    ↓
系统运行...
    ↓
⚠️ 弹窗: "是否允许执行 bash 命令 xxx？" ← 运行中断！
    ↓
❌ 等待用户点击确认... ← 用户体验差！
```

**实现要求**:
1. **提前授权**: 在 `.claude/settings.local.json` 中预先配置所有必要权限
2. **全面覆盖**: 分析项目所需的所有工具和命令，完整授权
3. **主控与子智能体**: 主控 Agent 和所有子 Agents 都需要权限授权
4. **文档强制要求**: 权限配置必须在 CLAUDE.md 中明确说明

**为什么这是 CLAUDE.md 的内容**:
- ✅ 系统架构的基础要求 (不是可选功能)
- ✅ 影响所有功能的正常运行 (100%依赖)
- ✅ 缺失会导致系统无法持续运行 (致命问题)
- ✅ 强制性配置要求 (MUST配置，不是建议)

**本原则在 CLAUDE.md 中的体现**:
- 必须有专门的"Permissions Configuration"章节
- 必须说明为什么需要这些权限
- 必须提供完整的配置示例
- 必须标注为 "CRITICAL" 或 "MANDATORY"

### 黄金判断标准

**问自己这个问题**:

> **"如果这个内容没有被激活/加载，系统会失败或产生错误结果吗？"**

- ✅ **回答"是"** → 应该在 **CLAUDE.md** (强制控制逻辑)
- ❌ **回答"否"** → 可以作为 **Skill** (可选领域知识)

**示例应用**:

| 内容 | 判断问题 | 答案 | 分类 |
|------|---------|------|------|
| 环境初始化流程 | 如果不执行初始化，能正常工作吗？ | 否，必须初始化 | CLAUDE.md |
| 质量检查点清单 | 如果跳过检查点，会产生错误吗？ | 是，会漏掉错误 | CLAUDE.md |
| 复杂利息计算公式 | 如果不知道这个公式，会失败吗？ | 否，可以使用简单方法或跳过 | Skill |
| 法律条文解释 | 如果不了解这个法律，会失败吗？ | 否，可以查询或保守处理 | Skill |

---

## 📋 详细分类标准

### 一、应该放在 CLAUDE.md 的内容

#### 1.1 系统架构与配置

**包含内容**:
- 整体架构说明 (如: 三agent协同系统)
- 目录结构定义
- **⚠️ 权限配置要求 (CRITICAL - 持续运行的基础)**
- 环境变量说明
- 依赖工具列表

**判断依据**:
- ✅ 系统启动和运行的基础
- ✅ 所有功能依赖的前置条件
- ✅ 缺失会导致系统无法运行

**本项目示例**:
```markdown
## System Architecture: Claude Code Skills

## Directory Structure

## ⚠️ CRITICAL: Permissions Configuration for Continuous Operation
**This project requires FULL pre-authorization to enable uninterrupted operation.**

### Design Principle: Zero-Interruption Workflow
The three-agent collaborative system is designed for continuous autonomous operation:
1. User issues a command
2. Main controller coordinates all sub-agents
3. Complete processing from raw materials to final deliverables
4. **NO permission prompts should interrupt the workflow**

### Current Configuration
**File**: `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

### What This Enables
- Environment initialization scripts
- Interest calculations
- File operations
- Text processing
- All sub-agent operations
- **Zero interruptions for user approval**

### Why Full Authorization
- Complex multi-step workflows requiring dozens of operations
- Listing individual permissions risks missing commands
- Defeats the purpose of autonomous operation
- All operations limited to project directory (safety)
```

**关键要点 - 权限配置的强制性**:

1. **必须说明持续运行原则**
   - 为什么需要零中断运行
   - 权限弹窗对用户体验的影响

2. **必须提供完整配置**
   - `.claude/settings.local.json` 的完整内容
   - 不能只是"建议配置"，必须是"必需配置"

3. **必须解释权限范围**
   - 哪些权限被授予
   - 为什么需要这些权限
   - 安全边界在哪里

4. **必须标注为 CRITICAL**
   - 使用 ⚠️ 符号
   - 使用 "CRITICAL", "MANDATORY" 等强制性用词
   - 放在文档前部，不能被忽略

**反面示例** (不应该在CLAUDE.md):
- ❌ 某个具体算法的详细步骤 (应该在Skill)
- ❌ 某种文档格式的详细模板 (应该在Skill的templates/)
- ❌ "建议配置权限以获得更好体验" (语气太弱，应该是强制要求)

---

#### 1.2 强制性工作流程

**包含内容**:
- 必须执行的处理步骤顺序
- Agent协调和调用规则
- 阶段间的强制依赖关系
- 不能跳过的验证流程

**判断依据**:
- ✅ 使用强制性语言 (MUST, NEVER, MANDATORY)
- ✅ 步骤顺序固定，不能改变
- ✅ 跳过任何一步会导致系统失败或错误结果
- ✅ 100%的任务都要执行这个流程

**本项目示例**:
```markdown
## Mandatory Workflow Controller
### ⚠️ Automatic Environment Initialization (TRANSPARENT TO USER)
### Processing Flow: Serial vs. Stage-Level Parallel
## Workflow Execution Details
  - Stage 1: Fact-Checking (MUST complete before Stage 2)
  - Stage 2: Debt Analysis (MUST complete before Stage 3)
  - Stage 3: Report Organization
```

**关键特征**:
- 每个阶段有明确的前置条件验证
- 每个阶段有强制的后置条件检查
- 不通过验证不能进入下一阶段

**反面示例** (应该在Skill而非CLAUDE.md):
- ❌ "建议的数据分析方法" (建议性，非强制)
- ❌ "可选的优化步骤" (可选性，非强制)
- ❌ "针对特定场景的处理技巧" (场景特定，非通用)

---

#### 1.3 质量控制检查点

**包含内容**:
- 零容错的验证清单
- 关键数据的验证规则 (如: 日期一致性)
- 必须通过的质量门槛
- 错误阻断机制

**判断依据**:
- ✅ 这些检查对所有任务都适用 (100%覆盖)
- ✅ 检查失败必须阻止流程继续
- ✅ 是质量红线，不能妥协
- ✅ 错误会导致严重后果 (如: 数据错误、合规问题)

**本项目示例**:
```markdown
### Critical Quality Checkpoints
**Checkpoint 1: After Fact-Checker (MUST PASS before proceeding)**
**Checkpoint 2: After Analyzer (MUST PASS before proceeding)**

### Zero-Tolerance Items
- ❌ Wrong bankruptcy dates in any report
- ❌ Manual calculations (not using calculator tool)
- ❌ Files in wrong directories
```

**关键特征**:
- 使用 "MUST PASS", "Zero-Tolerance", "NEVER acceptable" 等强制性语言
- 明确的阻断条件
- 所有任务都要执行这些检查

**反面示例** (应该在Skill):
- ❌ "建议检查以下项目以提高质量" (建议性)
- ❌ "针对复杂案件的额外验证步骤" (场景特定)
- ❌ "优化建议清单" (优化性，非强制)

---

#### 1.4 异常处理机制

**包含内容**:
- 系统级异常的标准响应流程
- 错误升级标准
- 必须的错误恢复步骤
- 不能继续执行的情况

**判断依据**:
- ✅ 异常处理流程对所有情况适用
- ✅ 遇到异常必须按标准流程响应
- ✅ 关系到系统稳定性和数据完整性

**本项目示例**:
```markdown
### Common Exception Handling
**Exception 1: Environment Not Initialized**
- **Action**: STOP → Run initialization → Verify → Resume

**Exception 2: Date Inconsistencies**
- **Action**: STOP → Identify source → Correct → Re-run → NEVER deliver with errors

**Escalation Criteria** (STOP and report):
- Bankruptcy date cannot be determined
- Evidence appears forged
- Calculator tool fundamentally broken
```

**关键特征**:
- "STOP", "NEVER", "MUST" 等强制性动作
- 明确的升级标准
- 错误恢复的标准步骤

**反面示例** (应该在Skill):
- ❌ "针对某种特殊情况的处理技巧" (技巧性知识)
- ❌ "可选的错误预防策略" (可选性)
- ❌ "领域专家的经验分享" (经验知识)

---

#### 1.5 文件管理规范

**包含内容**:
- 文件命名标准 (强制执行)
- 目录组织规则 (固定结构)
- 路径管理规则 (如: 只用绝对路径)
- 文件存放位置要求

**判断依据**:
- ✅ 文件管理规则对所有输出文件适用
- ✅ 违反规则会导致文件丢失或混乱
- ✅ 是系统可维护性的基础

**本项目示例**:
```markdown
### File Management Standards
**Path Management Rules (MANDATORY)**:
✓ Always use absolute paths from .processing_config.json
✓ Never use relative paths
✓ Verify directory exists before writing

**Directory Organization (STRICT)**:
工作底稿/ → Technical reports
最终报告/ → Client deliverables
计算文件/ → Calculation files

**Zero-Tolerance File Errors**:
❌ Files in wrong directories
❌ Wrong file naming
```

**关键特征**:
- 标注 "MANDATORY", "STRICT", "Zero-Tolerance"
- 明确的文件归属规则
- 违反会影响系统整体组织

**反面示例** (应该在Skill的templates/):
- ❌ 某种报告的具体格式模板 (内容模板，非管理规则)
- ❌ 某个文档类型的推荐章节结构 (推荐性)

---

#### 1.6 核心业务原则

**包含内容**:
- 不可妥协的业务规则
- 适用于所有场景的通用原则
- 合规性要求
- 伦理和法律底线

**判断依据**:
- ✅ 这些原则在任何情况下都不能违背
- ✅ 违反会导致业务结果无效或违规
- ✅ 所有功能必须遵循这些原则

**本项目示例**:
```markdown
## Core Principles

### 就低原则 (Lower Bound Rule)
When calculation > creditor's declaration, use declared amount
**Rationale**: Respect creditor's self-limitation

### 就无原则 (Non-Existence Rule)
Items identified in evidence but NOT declared are NOT included
**Rationale**: Debt review is verification, not claim generation

### Evidence Hierarchy
1. Highest: Legal documents (judgments)
2. Bilateral confirmations
3. Contracts
4. Lowest: Unilateral evidence
```

**关键特征**:
- 原则普遍适用
- 有明确的业务或法律依据
- 违反会导致结果无效

**反面示例** (应该在Skill):
- ❌ "针对某类复杂情况的特殊处理方法" (特殊情况，非通用原则)
- ❌ "行业最佳实践建议" (建议性，非强制原则)

---

### 二、应该作为 Skills 的内容

#### 2.1 领域专业知识

**包含内容**:
- 行业术语和概念解释
- 专业标准和规范
- 法律法规条文
- 学术理论和模型

**判断依据**:
- ✅ 需要专业背景才能理解
- ✅ 不同场景可能使用不同的知识子集
- ✅ 知识可以独立查阅和学习
- ✅ 缺失这个知识可以通过查询补充

**本项目示例**:

**Skill: debt-review-foundations**
```markdown
## 法律标准 (Legal Standards)
- 诉讼时效制度 (Statute of Limitations)
- 执行时效制度 (Execution Statute)
- 利率上限规定 (Interest Rate Caps)

## 计算公式 (Calculation Formulas)
- LPR浮动利率计算
- 复利计算方法
- 罚息计算规则
```

**Skill: debt-review-legal-standards**
```markdown
## 复杂案件法律参考
- 越权担保认定标准
- 让与担保的法律性质
- 建设工程优先权规则
```

**关键特征**:
- 知识密集型内容
- 需要专业解释和说明
- 可以独立成章节学习

**为什么是Skill而非CLAUDE.md**:
- ❌ 不是每个任务都需要所有这些知识
- ❌ 可以按需激活 (如: 只有复杂案件才需要 debt-review-legal-standards)
- ❌ 缺失某个知识点可以查询或保守处理，不会导致系统崩溃

---

#### 2.2 方法论和工作流程

**包含内容**:
- 某项具体任务的详细执行步骤
- 分析方法和技术
- 最佳实践和技巧
- 问题解决策略

**判断依据**:
- ✅ 是"如何做"的指导，而非"必须做"的命令
- ✅ 提供方法和思路，而非强制流程
- ✅ 不同场景可以选择不同方法
- ✅ 目标是帮助提高质量，而非阻止错误

**本项目示例**:

**Skill: debt-fact-checking**
```markdown
## 事实核查工作流程
1. 申报情况表整理
2. 形式性文件核查
3. 债权发生情况查明
4. 法律关系地位识别
5. 证据关系综合分析

## 批处理机制 (针对超长材料)
当材料 >100 页时，采用批次处理：
- Batch 1: 核心合同
- Batch 2: 履约凭证
- Batch 3: 法律文书
```

**Skill: debt-claim-analysis**
```markdown
## 债权分析方法论
### 金额拆解分析
- 识别本金项目
- 识别利息项目
- 识别罚息/违约金
- 识别其他费用

### 利息计算策略
- LPR期限选择原则
- 罚息上限验证
- 就低原则应用
```

**关键特征**:
- 提供详细的操作步骤和方法
- 有灵活性和可选择性
- 帮助执行者更好地完成任务

**为什么是Skill而非CLAUDE.md**:
- ❌ 具体步骤可能因情况而异 (如: 超长材料需要批处理，常规材料不需要)
- ❌ 是"建议的最佳方法"，而非"唯一允许的方法"
- ❌ 经验丰富的执行者可能有自己的方法

**对比CLAUDE.md中的强制流程**:
- ✅ CLAUDE.md: "MUST execute in sequence: Stage 1 → 2 → 3" (强制顺序)
- ✅ Skill: "建议按以下步骤进行事实核查..." (建议方法)

---

#### 2.3 模板和参考格式

**包含内容**:
- 文档模板
- 报告格式示例
- 表格结构
- 章节组织建议

**判断依据**:
- ✅ 提供参考样例
- ✅ 可以根据实际情况调整
- ✅ 是内容创作的辅助工具
- ✅ 不使用模板也能完成任务，只是质量可能不同

**本项目示例**:

**Skill: debt-fact-checking/templates/**
```
├── fact_check_report_template.md
├── evidence_timeline_table_template.md
└── declaration_summary_table_template.md
```

**Skill: debt-claim-analysis/templates/**
```
├── amount_breakdown_table_template.md
├── statute_analysis_template.md
└── calculation_documentation_template.md
```

**关键特征**:
- 存放在 `templates/` 子目录
- 提供结构和格式参考
- 可以根据实际情况修改

**为什么是Skill而非CLAUDE.md**:
- ❌ 模板是参考，不是强制格式
- ❌ 不同项目可能需要不同模板
- ❌ 模板可以演化和改进

**CLAUDE.md中的文件管理规范 vs Skill中的模板**:
- ✅ CLAUDE.md: "文件必须保存在工作底稿/目录" (强制位置)
- ✅ Skill模板: "建议使用以下章节结构..." (建议格式)

---

#### 2.4 参考资料和术语表

**包含内容**:
- 术语定义和解释
- 常见问题解答
- 参考链接和资源
- 案例库

**判断依据**:
- ✅ 查阅性内容
- ✅ 帮助理解，而非强制执行
- ✅ 可以在需要时查询
- ✅ 不影响系统运行

**本项目示例**:

**Skill: debt-review-foundations/references/**
```
├── legal_standards_reference.md       (法律标准参考)
├── calculation_formulas_reference.md  (计算公式参考)
└── common_terms_glossary.md          (术语表)
```

**Skill: debt-fact-checking/references/**
```
├── evidence_classification_guide.md   (证据分类指南)
└── legal_relationship_types.md       (法律关系类型)
```

**关键特征**:
- 存放在 `references/` 子目录
- 提供查阅和学习资源
- 不需要全部记住，用时查询

**为什么是Skill而非CLAUDE.md**:
- ❌ 是知识库，不是执行指令
- ❌ 按需查阅，不是强制阅读
- ❌ 内容可以扩展和更新

---

#### 2.5 特定场景的处理策略

**包含内容**:
- 针对特殊情况的解决方案
- 边缘案例的处理方法
- 复杂场景的应对策略
- 可选的优化技术

**判断依据**:
- ✅ 只在特定条件下使用
- ✅ 不是所有任务都会遇到
- ✅ 可以根据情况选择是否应用
- ✅ 缺失不会导致常规任务失败

**本项目示例**:

**Skill: debt-review-legal-standards** (整个skill都是特定场景)
```markdown
## 适用场景
⚠️ 仅用于以下特殊情况：
- 越权担保争议
- 让与担保认定
- 混合担保效力
- 金融不良债权转让
- 保理业务争议
- 融资租赁纠纷
- 建设工程优先权
- 个别清偿认定
- 抵销权争议
- 复杂利率计算争议

常规债权审查使用 debt-claim-analysis 即可。
```

**Skill: debt-fact-checking** (批处理机制是特定场景)
```markdown
## 超长材料批处理 (>100页或>50证据项)
**触发条件**: 材料量超过系统单次处理能力

**处理策略**:
- 分批处理
- 中间结果保存
- 最终合并为统一报告

**常规材料**: 不需要批处理，直接处理
```

**关键特征**:
- 明确的适用条件或触发场景
- 只有满足条件才激活
- 提供可选的处理策略

**为什么是Skill而非CLAUDE.md**:
- ❌ 不是所有任务都需要 (如: 大部分债权不涉及复杂法律问题)
- ❌ 按需激活，节省token和处理时间
- ❌ 可以单独更新和扩展，不影响主流程

**对比CLAUDE.md中的通用异常处理**:
- ✅ CLAUDE.md: "Exception 6: 超长材料" → 提供触发条件和基本响应 (所有项目都可能遇到)
- ✅ Skill: 超长材料的详细批处理策略和技术细节 (具体实施方法)

---

### 三、应该放在其他位置的内容

#### 3.1 Agent 定义文件

**位置**: `.claude/agents/`

**包含内容**:
- Agent 的角色和职责
- Agent 的主要技能引用
- Agent 的工作边界
- Agent 之间的协作说明

**本项目示例**:
```
.claude/agents/
├── debt-fact-checker.md      (事实核查员)
├── debt-claim-analyzer.md    (债权分析员)
└── report-organizer.md       (报告整理员)
```

**判断依据**:
- ✅ 描述"谁"负责做什么
- ✅ Agent是执行单元，不是知识单元
- ✅ Agent定义相对稳定，不频繁修改

**与CLAUDE.md和Skills的关系**:
- Agent定义引用 CLAUDE.md 中的工作流程要求
- Agent定义引用 Skills 中的专业知识
- CLAUDE.md 协调 Agents 的执行顺序

**为什么不是Skill**:
- ❌ Agent定义是系统组成，不是领域知识
- ❌ 不是按需激活，而是固定的系统角色

**为什么不在CLAUDE.md**:
- ❌ 保持CLAUDE.md聚焦于全局控制
- ❌ Agent定义可以独立修改和扩展
- ❌ 符合"一个文件一个关注点"原则

---

#### 3.2 工具脚本

**位置**: 项目根目录或专门的 `scripts/` 目录

**包含内容**:
- 自动化脚本
- 计算工具
- 数据处理程序
- 辅助工具

**本项目示例**:
```
/root/debt_review_skills/
├── 债权处理工作流控制器.py           (环境初始化脚本)
├── universal_debt_calculator_cli.py (计算器工具)
└── parallel_prompt_generator.py     (并行处理prompt生成器)
```

**判断依据**:
- ✅ 可执行的程序代码
- ✅ 通过命令行调用
- ✅ 提供特定功能服务
- ✅ 独立于知识和流程

**CLAUDE.md中应该如何引用**:
```markdown
## Universal Debt Calculator Tool
**Tool Location**: `/root/debt_review_skills/universal_debt_calculator_cli.py`
**MANDATORY Usage**: ALL calculations MUST use this tool

## Mandatory Workflow Controller
**Before processing EACH creditor**:
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

**为什么不是Skill**:
- ❌ 是可执行工具，不是知识文档
- ❌ 不需要"激活"，需要"调用"

**为什么不在CLAUDE.md**:
- ❌ 代码应该独立于文档
- ❌ CLAUDE.md只说明"必须使用"，工具实现独立维护

---

#### 3.3 配置文件

**位置**:
- 项目级: 项目根目录 (如 `project_config.ini`)
- 用户级: `.claude/settings.local.json`
- 系统级: `.env` 或类似

**包含内容**:
- 项目特定参数
- 用户偏好设置
- 环境变量
- API密钥 (应加密或.gitignore)

**本项目示例**:
```
project_config.ini              (项目配置: 破产日期等)
.claude/settings.local.json     (权限配置)
.processing_config.json         (每个债权人的处理配置)
```

**判断依据**:
- ✅ 参数和数据，不是逻辑和知识
- ✅ 不同项目/用户可能有不同值
- ✅ 经常需要修改和更新

**CLAUDE.md中应该如何引用**:
```markdown
## ⚠️ CRITICAL: Project Configuration
**ALWAYS read `project_config.ini` FIRST before processing!**

[项目基本信息]
债务人名称 = [公司名称]
破产受理日期 = YYYY-MM-DD
```

**为什么不是Skill**:
- ❌ 是数据，不是知识
- ❌ 项目特定，不是通用知识

**为什么不在CLAUDE.md**:
- ❌ 配置需要独立修改，不应嵌入文档
- ❌ CLAUDE.md说明"如何使用配置"，配置本身独立存在

---

#### 3.4 文档和归档

**位置**:
- 文档: `docs/` 或 `documentation/`
- 归档: `归档文件/` 或 `archive/`
- 日志: `logs/` 或项目根目录

**包含内容**:
- 项目说明文档
- 迁移记录
- 优化日志
- 历史备份
- 参考资料

**本项目示例**:
```
归档文件/
├── v1_改造前完整备份_20251023/
├── debt-workflow-orchestration_skill_备份_20251027/
├── MIGRATION_TO_SKILLS_V2.md
├── ARCHITECTURE_OPTIMIZATION_20251027.md
└── 改造完成总结.md

项目根目录/
├── PARALLEL_PROCESSING_PROTOCOL.md
├── PARALLEL_QUALITY_CHECKLIST.md
├── PERMISSIONS_CONFIGURATION.md
└── CONTENT_CLASSIFICATION_GUIDE.md (本文档)
```

**判断依据**:
- ✅ 面向人类读者的说明文档
- ✅ 历史记录和备份
- ✅ 项目管理和沟通材料
- ✅ 不直接参与系统运行

**与CLAUDE.md和Skills的关系**:
- CLAUDE.md 可以引用这些文档作为详细说明
- Skills 不应该引用项目特定的归档文档
- 这些文档记录系统演化历史

**为什么不是Skill**:
- ❌ 不是Claude Code运行时需要的知识
- ❌ 是给人类阅读的解释性材料

**为什么不在CLAUDE.md**:
- ❌ CLAUDE.md聚焦于当前系统运行
- ❌ 历史记录和详细说明应独立维护

---

## 🔍 决策流程图

使用这个流程图来判断内容应该放在哪里：

```
开始: 你有一段内容需要分类
    ↓
问题1: 这是可执行代码吗？
    ├─ 是 → 放在 scripts/ 或项目根目录 (工具脚本)
    └─ 否 → 继续
          ↓
问题2: 这是配置参数/数据吗？
    ├─ 是 → 放在配置文件 (.ini, .json, .env等)
    └─ 否 → 继续
          ↓
问题3: 这是Agent的角色定义吗？
    ├─ 是 → 放在 .claude/agents/
    └─ 否 → 继续
          ↓
问题4: 这是给人类阅读的说明文档吗？
    ├─ 是 → 放在 docs/ 或 归档文件/
    └─ 否 → 继续
          ↓
问题5: 如果这个内容没有被加载，系统会失败吗？
    ├─ 是 → 继续到问题6
    └─ 否 → 这是可选的领域知识 → 放在 Skill
          ↓
问题6: 这个内容使用强制性语言吗 (MUST, NEVER, MANDATORY)？
    ├─ 是 → 继续到问题7
    └─ 否 → 这是建议性方法 → 放在 Skill
          ↓
问题7: 这个内容对所有任务都适用吗 (100%覆盖)？
    ├─ 是 → 继续到问题8
    └─ 否 → 这是特定场景的内容 → 放在 Skill
          ↓
问题8: 这个内容是控制"系统如何运行"吗？
    ├─ 是 → 放在 CLAUDE.md (强制控制逻辑)
    └─ 否 → 这可能是Agent定义或配置 → 重新检查问题3-4
```

---

## ✅ 快速检查清单

### 应该在 CLAUDE.md 的内容检查清单

使用这个清单验证某段内容是否应该在CLAUDE.md：

```
□ 使用强制性语言 (MUST, NEVER, MANDATORY, CRITICAL)
□ 对所有任务都适用 (100%覆盖率)
□ 缺失会导致系统失败或错误结果
□ 控制"系统如何运行"而非"系统知道什么"
□ 定义不可妥协的规则或原则
□ 是系统架构的一部分
□ 需要100%可靠地执行，不能依赖激活
```

**如果以上至少5项为✓ → 应该在 CLAUDE.md**

### 应该作为 Skill 的内容检查清单

使用这个清单验证某段内容是否应该作为Skill：

```
□ 是领域专业知识或方法论
□ 不是所有任务都需要 (按需激活)
□ 使用建议性语言 (建议, 推荐, 可以)
□ 提供"如何做"的指导而非"必须做"的命令
□ 可以独立学习和查阅
□ 缺失可以通过查询或保守处理补救
□ 是"系统知道什么"而非"系统如何运行"
```

**如果以上至少5项为✓ → 应该作为 Skill**

### 两者都不符合？

如果两个清单都不太符合，考虑：
- 是否是工具脚本？→ `scripts/` 或项目根目录
- 是否是配置数据？→ 配置文件
- 是否是Agent定义？→ `.claude/agents/`
- 是否是说明文档？→ `docs/` 或 `归档文件/`

---

## 📊 实际案例分析

### 案例1: 工作流编排 (debt-workflow-orchestration)

**原始分类**: Skill ❌ (错误)
**正确分类**: CLAUDE.md ✅

**分析过程**:

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 如果不加载会失败吗？ | ✓ 是 | 不执行工作流会导致系统完全失败 |
| 使用强制性语言吗？ | ✓ 是 | MUST, NEVER, MANDATORY大量出现 |
| 对所有任务都适用吗？ | ✓ 是 | 每个债权人都要经过完整工作流 |
| 控制系统运行吗？ | ✓ 是 | 定义了环境初始化、阶段顺序、检查点 |
| 可以按需激活吗？ | ✗ 否 | 必须100%执行，不能选择性激活 |

**结论**: 这是强制性控制逻辑，应该在CLAUDE.md

**经验教训**: 不要因为"内容很多"就做成Skill，要看性质是"控制逻辑"还是"领域知识"

---

### 案例2: 法律标准参考 (debt-review-foundations)

**原始分类**: Skill ✅ (正确)
**正确分类**: Skill ✅

**分析过程**:

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 如果不加载会失败吗？ | ✗ 否 | 可以查询其他资料或保守处理 |
| 使用强制性语言吗？ | ✗ 否 | 主要是解释和说明性语言 |
| 对所有任务都适用吗？ | ✗ 否 | 不同债权涉及不同法律条文 |
| 是领域知识吗？ | ✓ 是 | 法律条文、计算公式是专业知识 |
| 可以按需激活吗？ | ✓ 是 | 根据具体案件需要激活相关知识 |

**结论**: 这是可选的领域知识，作为Skill正确

---

### 案例3: 质量检查点 (Quality Checkpoints)

**原始分类**: 部分在Skill，部分在CLAUDE.md (混乱) ❌
**正确分类**: CLAUDE.md ✅

**分析过程**:

**核心检查点**:
| 检查项 | 结果 | 说明 |
|--------|------|------|
| Checkpoint 1: 日期验证 | CLAUDE.md | 所有任务强制执行，零容错 |
| Checkpoint 2: 计算工具使用验证 | CLAUDE.md | 所有计算强制使用工具 |
| Checkpoint 3: 报告一致性验证 | CLAUDE.md | 所有报告必须一致 |

**领域特定检查**:
| 检查项 | 结果 | 说明 |
|--------|------|------|
| 复杂担保结构验证 | Skill | 只有涉及担保的案件需要 |
| 特殊利率计算验证 | Skill | 只有特定计算类型需要 |

**结论**:
- 通用的、强制的、零容错的检查点 → CLAUDE.md
- 特定场景的、可选的、专业的验证方法 → Skill

---

### 案例4: 超长材料批处理

**原始分类**: 部分在Skill，触发条件在CLAUDE.md (正确) ✅

**分析过程**:

**异常触发 (CLAUDE.md)**:
```markdown
**Exception 6: Super-Long Materials (>100 pages or >50 items)**
- **Symptom**: Material volume exceeds capacity
- **Action**: Activate batch processing → Process in batches → Consolidate
```

**详细方法论 (Skill: debt-fact-checking)**:
```markdown
## 超长材料批处理机制
### 批次划分策略
- Batch 1: 核心合同和直接履约证据
- Batch 2: 大量履约凭证 (发票、银行记录)
- Batch 3: 法律文书和汇总材料

### 合并规则
- 时间线按时间顺序合并
- 证据关系整合
- 统一报告生成
```

**结论**:
- 异常识别和基本响应 → CLAUDE.md (所有项目都可能遇到超长材料)
- 具体的批处理方法和技术细节 → Skill (实施技巧，可以优化)

**为什么这样分配是正确的**:
- ✅ CLAUDE.md确保问题被识别和处理 (强制响应)
- ✅ Skill提供详细方法 (灵活实施)
- ✅ 即使Skill未激活，CLAUDE.md的基本指令也能确保不会忽略问题

---

## 🎓 常见误区和陷阱

### 误区0: "权限配置是可选的，运行时再授权也可以" ⚠️

**错误思维**: "用户可以在系统提示时点击允许，不需要提前配置"

**为什么这是最严重的错误**:
- ❌ **破坏持续运行原则**: 权限弹窗会中断自动化流程
- ❌ **用户体验极差**: 用户发布命令后还要不停点击确认
- ❌ **可能导致失败**: 如果用户不在，系统会卡住等待
- ❌ **违背自动化初衷**: 自动化系统的核心价值就是"无人值守运行"

**正确原则**: **权限配置是强制性架构要求，必须在 CLAUDE.md 中明确规定**

**实际案例对比**:

**❌ 错误做法 - 没有权限预配置**:
```
用户: "请处理5个债权人"
系统: 开始处理第1个...
系统: ⚠️ 需要权限: 是否允许执行 "python 债权处理工作流控制器.py"？
[等待用户点击...]
用户: [点击允许]
系统: 继续...
系统: ⚠️ 需要权限: 是否允许执行 "python universal_debt_calculator_cli.py"？
[等待用户点击...]
用户: [点击允许]
系统: 继续...
系统: ⚠️ 需要权限: 是否允许执行 "mkdir"？
[等待用户点击...]
用户: 😤 (被打断N次，体验极差)
```

**✅ 正确做法 - 完整权限预配置**:
```
用户: "请处理5个债权人"
系统: [自动运行，无任何中断]
  - 初始化债权人1环境... ✓
  - 事实核查债权人1... ✓
  - 债权分析债权人1... ✓
  - 报告整理债权人1... ✓
  - 初始化债权人2环境... ✓
  ...
  [80分钟后]
系统: ✅ 全部完成！所有报告已生成。
用户: 😊 (零干预，完美体验)
```

**CLAUDE.md 中必须明确说明**:
```markdown
## ⚠️ CRITICAL: Permissions Configuration for Continuous Operation

**This project requires FULL pre-authorization to enable uninterrupted operation.**

**Without proper permissions configuration, the system WILL fail** due to:
- Permission prompts interrupting multi-agent workflows
- Sub-agents unable to execute required commands
- User intervention required during autonomous operation
- Workflow timeouts waiting for manual approval

**Configuration File**: `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

**This is NOT optional** - it is a mandatory prerequisite for system operation.
```

**检查清单 - 权限配置完整性**:
```
□ CLAUDE.md 包含专门的权限配置章节
□ 标注为 CRITICAL 或 MANDATORY
□ 解释了为什么需要持续运行
□ 提供了完整的配置文件内容
□ 说明了配置文件位置和格式
□ 列出了需要的权限范围
□ 解释了安全边界
□ 警告了不配置的后果
```

**如果你的项目没有权限配置章节，立即添加！这不是可选功能，是系统基础架构。**

---

### 误区1: "内容很多就做成Skill"

**错误思维**: "CLAUDE.md不应该太长，这段内容很多，做成Skill吧"

**正确原则**: **性质决定位置，不是长度决定位置**

**示例**:
- ❌ 错误: 工作流编排内容很多 (30KB) → 做成Skill
- ✅ 正确: 工作流编排是控制逻辑 → 放在CLAUDE.md，即使很长

**经验**:
- CLAUDE.md 可以达到 500-1000行，这是合理的
- Skill 可以很短 (只有几个术语定义)，也可以很长 (详细方法论)
- 判断标准是**性质 (控制逻辑 vs 领域知识)**，不是长度

---

### 误区2: "所有方法都应该在Skill中"

**错误思维**: "任何带步骤的流程都是方法论，应该做成Skill"

**正确区分**:
- **强制流程** (必须按这个顺序) → CLAUDE.md
- **建议方法** (可以这样做) → Skill

**示例对比**:

| 内容 | 性质 | 分类 |
|------|------|------|
| "MUST execute Stage 1 before Stage 2" | 强制流程 | CLAUDE.md |
| "建议按以下步骤进行事实核查..." | 建议方法 | Skill |
| "NEVER skip environment initialization" | 强制规则 | CLAUDE.md |
| "针对复杂案件，可以采用以下分析策略..." | 可选策略 | Skill |

**判断关键**:
- 问: "可以不按这个方法做吗？"
  - 不可以 → CLAUDE.md (强制)
  - 可以 → Skill (建议)

---

### 误区3: "所有检查清单都应该在Skill中"

**错误思维**: "检查清单是工作指导，应该放在Skill的templates/中"

**正确区分**:
- **强制验证门槛** (不通过不能继续) → CLAUDE.md
- **质量改进建议清单** (帮助提高质量) → Skill

**示例对比**:

**CLAUDE.md中的强制检查点**:
```markdown
**Checkpoint 1: After Fact-Checker (MUST PASS before proceeding)**
✓ Bankruptcy date verified
✓ Dates explicitly documented
✓ Timeline events in chronological order
```

**Skill中的质量改进清单**:
```markdown
## 事实核查质量提升建议
□ 添加证据来源页码引用
□ 使用标准化术语
□ 添加关键事实交叉引用
```

**区别**:
- CLAUDE.md: "MUST PASS"，不通过则STOP
- Skill: "建议"，执行后可以提高质量

---

### 误区4: "通用的内容才放CLAUDE.md，项目特定的放Skill"

**错误思维**: "这个规则只适用于债权审查项目，应该做成Skill"

**正确原则**: **控制逻辑 vs 领域知识**，不是**通用 vs 特定**

**示例**:
- ✅ 正确: "破产日期验证" 虽然是债权审查特定的，但是强制控制逻辑 → CLAUDE.md
- ✅ 正确: "通用文件管理规范" 虽然适用所有项目，但是强制规则 → CLAUDE.md
- ✅ 正确: "债权法律条文解释" 虽然是债权审查特定的，但是领域知识 → Skill
- ✅ 正确: "Markdown语法参考" 虽然通用，但是参考知识 → Skill (如果需要的话)

**关键点**:
- CLAUDE.md 可以包含项目特定的强制规则
- Skill 可以包含通用的领域知识
- 判断标准还是: 控制逻辑 (强制) vs 领域知识 (可选)

---

### 误区5: "Skill可以引用CLAUDE.md的内容"

**错误思维**: "Skill中写: '具体流程见CLAUDE.md的工作流章节'"

**正确原则**: **单向依赖 - CLAUDE.md可以引用Skill，Skill不应引用CLAUDE.md**

**依赖关系**:
```
CLAUDE.md (控制层)
   ↓ 可以引用
Skills (知识层)
   ↑ 不应引用
```

**为什么**:
- ✅ CLAUDE.md 是"主控"，协调和引用各种知识
- ❌ Skill 是"知识模块"，应该独立和可复用
- ❌ 如果Skill引用CLAUDE.md，就失去了模块化和可移植性

**正确做法**:
- ✅ CLAUDE.md: "For detailed analysis methods, see **debt-claim-analysis** skill"
- ✅ Skill: 包含完整的方法论，不引用CLAUDE.md
- ❌ 错误: Skill写 "流程见CLAUDE.md" → 应该把必要的内容复制到Skill中

**例外情况**:
- Skill可以说 "本方法符合CLAUDE.md中定义的XX原则" (提及，不是依赖)
- Skill可以说 "使用本方法时，仍需遵循系统的质量标准" (提醒，不是引用具体内容)

---

## 🛠️ 实用工具和模板

### 新增内容分类决策表

当你要添加新内容时，使用这个表格做决策：

| 问题 | 回答 | 分数 |
|------|------|------|
| 1. 使用强制性语言 (MUST/NEVER/MANDATORY) 吗？ | 是/否 | 是+2 / 否-2 |
| 2. 对所有任务都适用 (100%覆盖) 吗？ | 是/否 | 是+2 / 否-1 |
| 3. 缺失会导致系统失败或错误结果吗？ | 是/否 | 是+3 / 否-2 |
| 4. 控制"系统如何运行"而非"系统知道什么"吗？ | 是/否 | 是+2 / 否-1 |
| 5. 是可执行代码或工具吗？ | 是/否 | 是→脚本 / 否+0 |
| 6. 是配置数据吗？ | 是/否 | 是→配置文件 / 否+0 |
| 7. 是领域专业知识吗？ | 是/否 | 是-2 / 否+1 |
| 8. 可以按需激活吗？ | 是/否 | 是-2 / 否+2 |

**计分结果**:
- **≥ 6分**: 应该在 **CLAUDE.md**
- **0-5分**: 需要进一步判断，检查是否是脚本/配置/Agent定义
- **< 0分**: 应该作为 **Skill**

---

### Skill 创建模板

当你确认要创建新Skill时，使用这个结构：

```
.claude/skills/your-skill-name/
├── SKILL.md                    # 主文件 (必需)
├── templates/                  # 模板目录 (可选)
│   ├── template1.md
│   └── template2.md
├── references/                 # 参考资料 (可选)
│   ├── reference1.md
│   └── reference2.md
└── examples/                   # 示例 (可选)
    └── example1.md
```

**SKILL.md 基本结构**:
```markdown
---
name: your-skill-name
description: 简短描述这个skill的用途和适用场景 (1-2句话)
---

# Skill名称

## 概述
简要说明这个skill包含什么知识

## 何时使用此Skill
- 场景1
- 场景2
- 场景3

## 核心内容

### 第一部分: XXX
[详细内容]

### 第二部分: XXX
[详细内容]

## 参考资料
- 相关文档链接
- 外部资源

## 示例
[实际应用示例]
```

---

### CLAUDE.md 内容组织建议

**推荐章节结构**:

```markdown
# CLAUDE.md

## System Architecture
- 整体架构说明
- Skills列表和说明
- 目录结构

## Critical Configuration
- 权限配置
- 环境要求
- 关键配置文件

## Mandatory Workflow
- 强制性工作流程
- Agent协调规则
- 阶段依赖关系

## Workflow Execution Details
- 详细的执行要求
- 质量检查点
- 异常处理机制

## Core Principles
- 不可妥协的业务原则
- 通用规则
- 合规要求

## File Management Standards
- 文件命名规范
- 目录组织规则
- 路径管理要求

## Tools and Scripts
- 工具说明
- 使用方法
- 强制要求

## Quality Standards
- 零容错清单
- 验证协议

## Reference Documents
- Skills引用
- 外部文档链接

## Migration Notes / History
- 版本历史
- 重要变更记录
```

**长度控制建议**:
- 小型项目 (<3 agents): 300-500行
- 中型项目 (3-5 agents): 500-800行
- 大型项目 (>5 agents): 800-1200行
- 超过1200行: 考虑是否有内容应该移到Skills或独立文档

---

## 📈 评估和改进

### 定期审查清单

每个季度或重大变更后，审查架构分类：

```
□ 检查CLAUDE.md是否包含非强制性内容 → 移到Skill
□ 检查Skills是否包含强制性控制逻辑 → 移到CLAUDE.md
□ 检查是否有内容重复 → 合并或建立引用关系
□ 检查Skills之间是否有循环依赖 → 重构为独立模块
□ 检查CLAUDE.md长度是否超过1500行 → 评估是否过度详细
□ 检查是否有未使用的Skills → 删除或归档
□ 检查新增内容是否遵循分类标准 → 重新分类
```

### 常见问题诊断

**症状1: CLAUDE.md越来越长**
- 原因: 可能包含了过多详细的方法论
- 解决: 将"如何做"的详细步骤移到Skills，只保留"必须做"的要求

**症状2: Skills很少被激活**
- 原因: 可能Skill中的内容应该在CLAUDE.md (因为每次都需要)
- 解决: 评估是否应该将常用内容移到CLAUDE.md

**症状3: 经常需要修改CLAUDE.md**
- 原因: 可能包含了易变的领域知识
- 解决: 将频繁变化的知识移到Skills，CLAUDE.md只保留稳定的控制逻辑

**症状4: Skills之间内容重复**
- 原因: 共享知识未抽取到foundations skill
- 解决: 创建或扩展 foundations skill，其他skills引用

---

## 🔐 权限配置实战指南

### 为什么权限配置如此重要

**持续运行原则的核心**: 用户发布命令后，系统应该像"一键启动的自动化工厂"一样持续运行到最终结果，而不是像"需要人工干预的半自动生产线"。

**权限弹窗的致命影响**:
```
场景: 用户晚上10点发布命令"处理这批50个债权人"，期望第二天早上看到结果

❌ 没有权限配置:
22:00 - 用户发布命令，去睡觉
22:01 - 系统处理第1个，弹窗请求权限
22:01-08:00 - 系统卡住等待用户点击...
08:00 - 用户起床，发现只处理了1个，其余49个都在等待
结果: 浪费8小时，任务失败

✅ 有权限配置:
22:00 - 用户发布命令，去睡觉
22:00-06:00 - 系统自动处理全部50个债权人
06:00 - 全部完成
08:00 - 用户起床，看到完整结果
结果: 完美的无人值守运行
```

### 如何分析项目所需权限

**第一步: 列举所有自动化操作**

基于你的工作流程，列出系统会执行的所有操作：

**本项目示例**:
```
1. 环境初始化:
   - python 债权处理工作流控制器.py
   - mkdir (创建目录)
   - touch (创建配置文件)

2. 数据处理:
   - python universal_debt_calculator_cli.py
   - python parallel_prompt_generator.py

3. 文件操作:
   - mv (移动文件)
   - cp (复制文件)
   - rm (删除临时文件)

4. 文本处理:
   - grep (搜索内容)
   - sed (文本替换)
   - cat (读取文件 - 通过Read工具更高效)

5. 状态检查:
   - ls (列出文件)
   - find (查找文件)
   - wc (统计行数)

6. Sub-Agent调用:
   - Task tool (启动 debt-fact-checker)
   - Task tool (启动 debt-claim-analyzer)
   - Task tool (启动 report-organizer)
```

**第二步: 确定最小权限集**

Claude Code 的权限类型：
- **Bash**: 所有 bash 命令执行权限
- **Read**: 读取文件 (通常默认允许)
- **Write**: 写入文件 (通常默认允许)
- **Edit**: 编辑文件 (通常默认允许)
- **Grep**: 搜索文件 (通常默认允许)

**判断**:
- 如果需要执行任何 Python 脚本 → 需要 `Bash` 权限
- 如果需要文件系统操作 (mkdir, mv, cp, rm) → 需要 `Bash` 权限
- 如果需要启动 Sub-Agents → 不需要额外权限 (Task tool 自动处理)

**本项目结论**: 需要 `Bash` 权限（涵盖所有脚本执行和文件操作）

**第三步: 配置权限文件**

创建或修改 `.claude/settings.local.json`:

**推荐配置 (最大兼容性)**:
```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

**说明**:
- `"allow": ["Bash"]` - 预先授权所有 Bash 命令
- `"deny": []` - 不拒绝任何权限
- 这是"宽松模式"，适合复杂的自动化项目

**保守配置 (如果需要更严格控制)**:
```json
{
  "permissions": {
    "allow": ["Bash:python", "Bash:mkdir", "Bash:mv", "Bash:cp"],
    "deny": ["Bash:rm -rf"]
  }
}
```

**说明**:
- 只允许特定命令
- 拒绝危险命令 (如 `rm -rf`)
- 但这需要列举所有可能用到的命令，维护成本高

**建议**: 对于自动化项目，使用宽松模式 + 项目目录隔离来保证安全

### 安全考虑

**问题**: "允许所有 Bash 命令不会有安全风险吗？"

**答案**: 合理的安全边界设计可以降低风险：

**安全措施**:

1. **项目目录隔离**
   ```markdown
   ## Safety
   - All operations limited to project directory (`/root/debt_review_skills/`)
   - Output files strictly organized in `输出/` directory
   - No system-level operations required
   - Full audit trail via command logging
   ```

2. **明确操作范围**
   - 在 CLAUDE.md 中明确说明系统只在项目目录内操作
   - 禁止访问系统目录 (如 `/etc/`, `/usr/`, `/var/`)
   - 禁止网络操作 (除非明确需要)

3. **代码审查**
   - 工具脚本应该经过审查
   - 避免使用用户输入直接拼接命令
   - 使用参数化命令而非字符串拼接

4. **审计追踪**
   - 所有命令执行都有日志
   - 可以事后审计操作记录
   - 异常行为可以被检测

**权限配置的安全原则**:
```
允许范围: Bash 命令
安全边界: 项目目录内
审计机制: 完整日志
风险评估: 低 (无系统级操作，无网络访问)
```

### CLAUDE.md 中的权限配置模板

**完整示例** (复制到你的项目):

```markdown
## ⚠️ CRITICAL: Permissions Configuration for Continuous Operation

**This project requires FULL pre-authorization to enable uninterrupted operation.**

### Design Principle: Zero-Interruption Workflow

The [描述你的系统，如: three-agent collaborative system] is designed for **continuous autonomous operation**:
1. User issues a command
2. [主控智能体] coordinates all sub-agents
3. Complete processing from [输入] to [最终结果]
4. **NO permission prompts should interrupt the workflow**

**Without proper permissions, the workflow WILL be interrupted** by permission dialogs requiring manual user approval at each step.

### Current Configuration

**File**: `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

**Meaning**: Full authorization for all Bash commands without individual permission requests.

### What This Enables

**Automatic Operations**:
- [列出你的系统会执行的操作，如:]
- Environment initialization (`python 初始化脚本.py`)
- Data processing (`python 数据处理脚本.py`)
- File operations (mkdir, mv, cp, rm)
- Text processing (grep, sed, awk)
- [其他操作...]
- **All sub-agent operations**

**No Interruptions**: All agents can perform their tasks autonomously without waiting for user approval at each step.

### Why Full Authorization

**Complex Multi-Step Workflows**: Each [任务单位] involves dozens of [操作类型] across [N个] agents. Listing individual permissions would:
- Risk missing commands → workflow interruption
- High maintenance cost → need to update permissions for each new feature
- Defeat the purpose of autonomous operation

**Safety**:
- All operations limited to project directory (`/path/to/your/project/`)
- Output files strictly organized in `输出/` directory
- No system-level operations required
- Full audit trail via command logging

**For detailed permission documentation**, see: `PERMISSIONS_CONFIGURATION.md` (if you have one)

### Troubleshooting

**If you see permission prompts during operation**:
1. Verify `.claude/settings.local.json` exists in project root
2. Check file content matches the configuration above
3. Restart Claude Code to reload settings
4. If issue persists, check Claude Code documentation
```

### 权限配置检查清单

**项目启动前检查**:
```
□ 创建了 .claude/settings.local.json 文件
□ 配置内容正确 (allow: ["Bash"])
□ 文件位置正确 (.claude/ 目录下)
□ JSON 格式有效 (无语法错误)
□ CLAUDE.md 包含权限配置章节
□ 权限章节标注为 CRITICAL
□ 解释了为什么需要这些权限
□ 说明了安全边界
```

**首次运行后验证**:
```
□ 运行一个完整流程
□ 观察是否出现权限弹窗
□ 如果出现弹窗，检查配置文件
□ 确认 sub-agents 也能正常执行命令
□ 记录日志验证操作范围
```

### 常见问题 FAQ

**Q1: 是否每个子智能体都需要单独配置权限？**

A: 不需要。`.claude/settings.local.json` 是项目级配置，对主控智能体和所有通过 Task tool 启动的子智能体都生效。

**Q2: 如果我只列出部分命令权限会怎样？**

A: 系统会在遇到未授权命令时弹窗请求权限，打断自动化流程。除非你能100%确定列举了所有可能用到的命令，否则不推荐。

**Q3: "allow": ["Bash"] 会允许所有危险命令吗？**

A: 理论上是的，但结合项目目录隔离和代码审查，实际风险可控。你也可以使用 "deny" 明确禁止某些危险命令（如 `rm -rf /`）。

**Q4: 权限配置可以动态修改吗？**

A: 可以修改文件，但需要重启 Claude Code 才能生效。建议在项目初期就配置完整。

**Q5: 其他项目可以复用这个配置吗？**

A: 可以。如果你的多个项目都是自动化项目，可以使用相同的宽松配置。如果某个项目安全要求更高，可以单独调整。

### 权限配置的演化

**阶段1: 初期开发**
- 使用宽松配置 (`"allow": ["Bash"]`)
- 快速迭代，不被权限问题打断

**阶段2: 功能稳定**
- 记录实际使用的命令
- 如果需要，可以收紧为精确命令列表
- 但对于复杂项目，宽松配置仍是最佳选择

**阶段3: 生产部署**
- 审查所有工具脚本的安全性
- 确认项目目录隔离有效
- 建立审计日志机制
- 保持宽松配置 + 严格的安全边界

---

## 🎯 总结：记住这些关键点

### 四句话总结 (新增第0条)

0. **权限配置 = 持续运行的基础 = CRITICAL = 必须在 CLAUDE.md 中明确说明**
   - 预先授权所有必要权限
   - 避免运行时权限弹窗
   - 实现零中断的自动化运行

1. **CLAUDE.md = 控制逻辑 = "系统如何运行" = 强制执行 = 100%加载**
   - 工作流程、质量检查点、异常处理、文件管理规范、**权限配置**

2. **Skills = 领域知识 = "系统知道什么" = 按需激活 = 可选参考**
   - 专业知识、方法论、模板、术语表、特定场景策略

3. **判断标准: "如果这个内容没被加载，系统会失败吗？" - 是→CLAUDE.md，否→Skill**

### 设计原则卡片

打印或保存这张卡片，做架构决策时参考：

```
╔════════════════════════════════════════════════════════════════╗
║           Claude Code 内容分类决策卡片                        ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  ⚠️ 优先级0: 权限配置 (CRITICAL)                              ║
║  ✓ 必须在 CLAUDE.md 中明确说明                                ║
║  ✓ 提供完整的 .claude/settings.local.json 配置                ║
║  ✓ 解释持续运行原则 (Zero-Interruption Workflow)              ║
║  ✓ 说明安全边界和审计机制                                     ║
║                                                                ║
║  缺失后果: 运行时权限弹窗 → 中断自动化 → 任务失败             ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  CLAUDE.md (强制控制层)                                       ║
║  ✓ 控制"系统如何运行"                                         ║
║  ✓ 使用 MUST/NEVER/MANDATORY                                 ║
║  ✓ 100%任务都需要                                             ║
║  ✓ 缺失会导致失败                                             ║
║                                                                ║
║  必须包含:                                                     ║
║  • 权限配置 (Zero-Interruption 的基础)                        ║
║  • 工作流程、检查点、异常处理                                 ║
║  • 文件规范、核心原则                                         ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Skills (可选知识层)                                          ║
║  ✓ 描述"系统知道什么"                                         ║
║  ✓ 使用 建议/推荐/可以                                        ║
║  ✓ 按需激活                                                   ║
║  ✓ 缺失可以补救                                               ║
║                                                                ║
║  包含: 领域知识、方法论、模板、术语表、特定场景策略           ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  黄金判断标准:                                                 ║
║  "如果这个内容没被加载，系统会失败吗？"                       ║
║     是 → CLAUDE.md                                            ║
║     否 → Skill                                                ║
║                                                                ║
║  特殊: 权限配置永远在 CLAUDE.md (自动化系统的生命线)          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

### 避免的最大错误

0. ❌ **第0大错误 (最致命)**: 没有配置权限或权限配置不在 CLAUDE.md
   - 后果: 运行时权限弹窗 → 中断自动化 → 无人值守失败 → 项目价值归零
   - 修复: 立即在 CLAUDE.md 添加完整的权限配置章节

1. ❌ **第1大错误**: 将控制逻辑做成Skill (如: workflow orchestration)
   - 后果: 激活失败 → 系统崩溃

2. ❌ **第2大错误**: 将所有内容都放CLAUDE.md
   - 后果: 文件过长，token浪费，失去模块化优势

3. ❌ **第3大错误**: 用长度判断位置而非性质
   - 后果: 架构混乱，边界不清

4. ❌ **第4大错误**: Skills之间循环依赖
   - 后果: 无法独立使用，失去可移植性

5. ❌ **第5大错误**: Skill引用CLAUDE.md内容
   - 后果: 打破单向依赖，失去模块独立性

---

## 附录：本项目的最终架构

作为参考，这是经过优化后的债权审查项目架构：

### CLAUDE.md 内容 (674行)

**强制控制层**:
1. System Architecture (50行) - 架构说明
2. Permissions Configuration (55行) - 权限配置
3. Date Verification Protocol (20行) - 日期验证
4. Three-Agent System (40行) - Agent协调
5. **Workflow Orchestration (210行)** - 工作流编排
   - Three-Stage Execution Requirements
   - Critical Quality Checkpoints
   - Common Exception Handling
   - File Management Standards
6. Universal Calculator Tool (30行) - 工具要求
7. Core Principles (25行) - 核心原则
8. Directory Structure (60行) - 目录结构
9. Standard Workflow (35行) - 流程概述
10. Quality Standards (30行) - 质量要求
11. Migration Notes (30行) - 历史记录

### Five Skills (知识层)

1. **debt-fact-checking** - 事实核查方法论
   - 申报信息整理方法
   - 证据分类和关系分析
   - 时间线构建技巧
   - 超长材料批处理策略

2. **debt-claim-analysis** - 债权分析方法论
   - 金额拆解方法
   - LPR期限选择原则
   - 诉讼时效分析方法
   - 罚息上限计算

3. **report-organization** - 报告整理方法论
   - 报告合并技巧
   - 模板应用方法
   - 文件清单生成

4. **debt-review-foundations** - 共享基础知识
   - 法律标准参考
   - 计算公式库
   - 通用术语表

5. **debt-review-legal-standards** - 复杂案件法律参考
   - 越权担保
   - 让与担保
   - 建设工程优先权
   - 个别清偿认定
   - (仅在复杂案件时激活)

### 工具层

- `债权处理工作流控制器.py` - 环境初始化脚本
- `universal_debt_calculator_cli.py` - 通用计算器
- `parallel_prompt_generator.py` - 并行处理辅助工具

### Agent层

- `.claude/agents/debt-fact-checker.md` - 事实核查员
- `.claude/agents/debt-claim-analyzer.md` - 债权分析员
- `.claude/agents/report-organizer.md` - 报告整理员

这个架构实现了：
- ✅ 清晰的控制逻辑 vs 领域知识边界
- ✅ 强制执行 vs 可选参考的明确区分
- ✅ 模块化和可维护性
- ✅ 高可靠性和性能

---

---

## 🚀 快速启动检查清单

当你开始一个新的 Claude Code Skills 项目时，按这个顺序检查：

### 第一步: 权限配置 (最高优先级) ⚠️

```
□ 创建 .claude/settings.local.json
□ 配置内容: {"permissions": {"allow": ["Bash"], "deny": []}}
□ 在 CLAUDE.md 中添加权限配置章节
□ 标注为 CRITICAL
□ 解释持续运行原则
□ 说明安全边界
□ 测试: 运行一次完整流程，确保无权限弹窗
```

**如果这一步没做好，后面的工作都白费！**

### 第二步: CLAUDE.md 架构设计

```
□ 系统架构说明
□ 权限配置 (已在第一步完成)
□ 工作流程 (强制性)
□ 质量检查点 (强制性)
□ 异常处理机制
□ 文件管理规范
□ 核心业务原则
```

### 第三步: Skills 规划

```
□ 列出需要的领域知识
□ 每个 Skill 明确适用场景
□ 使用建议性语言 (不是强制性)
□ 设计独立可复用的模块
□ 避免 Skills 之间循环依赖
```

### 第四步: 验证架构

```
□ 用"黄金判断标准"检查每个内容的位置
□ 确保 CLAUDE.md 不包含领域知识细节
□ 确保 Skills 不包含强制性控制逻辑
□ 检查权限配置完整性
□ 运行完整流程验证
```

---

**文档版本**: 2.0 (增加持续运行原则和权限配置指南)
**最后更新**: 2025-10-27
**适用项目**: 所有使用 Claude Code Skills 架构的自动化项目
**核心原则**: 持续运行 (Continuous Operation) + 内容分类 (Control vs Knowledge)
**维护者**: Architecture Team

**⚠️ 重要提醒**:
- **权限配置是自动化项目的生命线**，缺失会导致系统无法持续运行
- 在开始任何新项目时，第一步就是配置权限，而不是最后才想起来
- CLAUDE.md 中必须包含完整的权限配置章节，标注为 CRITICAL

**建议**:
1. 将本文档添加到新项目的初始化清单中
2. 在架构设计阶段参考"决策流程图"和"快速检查清单"
3. 使用"权限配置实战指南"设置持续运行环境
4. 定期用"评估和改进"章节审查架构质量
