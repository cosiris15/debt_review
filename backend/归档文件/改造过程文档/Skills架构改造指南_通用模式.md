# Skills架构改造指南 - 通用模式与最佳实践

**文档目的**: 总结传统Agent项目改造为Skills架构的通用模式，便于复用到其他项目
**基于案例**: 舆情法律分析系统 v1.x → v2.0 迁移
**适用场景**: 任何基于Claude Agents的多Agent协作系统
**最后更新**: 2025-10-22

---

## 📚 目录

1. [Skills架构改造本质](#1-skills架构改造本质)
2. [内容迁移模式](#2-内容迁移模式)
3. [用户交互模式变化](#3-用户交互模式变化)
4. [通用改造步骤](#4-通用改造步骤)
5. [最佳实践](#5-最佳实践)
6. [常见问题](#6-常见问题)

---

## 1. Skills架构改造本质

### 1.1 核心概念

**改造前 (传统模式)**:
- Agent定义文件包含**所有**指令（几百到上千行）
- 知识分散在多个独立的Markdown文档中
- 每次调用Agent都加载所有内容到context

**改造后 (Skills模式)**:
- Agent定义文件变为**简洁的入口**（通常<200行）
- 知识模块化为**Skills包**（独立的、可重用的知识单元）
- Agent按需加载Skills，使用**渐进式揭示**模式

### 1.2 关键变化

```
传统模式:
┌─────────────────────────────┐
│ Agent Definition (1000行)   │
│ - 所有工作流程               │
│ - 所有详细规则               │
│ - 所有示例                   │
│ - 所有错误处理               │
└─────────────────────────────┘

Skills模式:
┌─────────────────┐    ┌──────────────────────────┐
│ Agent Definition│───>│ Skill Package            │
│ (简洁入口200行) │    │ ├─ SKILL.md (核心<500行) │
│                 │    │ ├─ references/ (详细内容)│
│                 │    │ ├─ scripts/ (工具脚本)   │
│                 │    │ └─ assets/ (资源文件)    │
└─────────────────┘    └──────────────────────────┘
```

**本质**: 从"单体文档"到"模块化知识包"

---

## 2. 内容迁移模式

### 2.1 内容类型映射表

| 原内容类型 | 原载体 | 目标载体 | 目标位置 | 示例 |
|-----------|--------|---------|---------|------|
| **Agent角色定义** | Agent MD文件开头 | Agent定义文件 | 前置说明 | "You are an elite..." |
| **核心工作流** | 标准文档MD | Skill的SKILL.md | 主体工作流章节 | "8-step workflow" |
| **详细操作指南** | 标准文档MD | Skill的references/ | 独立guide文件 | `extraction_guide.md` |
| **评分规则** | 标准文档MD | Skill的references/ | 独立guide文件 | `scoring_methodology.md` |
| **JSON schema** | 标准文档MD | Skill的references/ | 独立JSON或MD | `json_schema.json` |
| **示例和模板** | 标准文档MD | Skill的references/ | 独立guide文件 | `examples_guide.md` |
| **工具脚本** | 项目根目录 | Skill的scripts/ | Python脚本 | `validate_output.py` |
| **配置说明** | 单独MD文档 | Skill的references/ | 独立guide文件 | `config_reference.md` |
| **错误处理** | 标准文档MD | Skill的references/ | 独立guide文件 | `error_recovery.md` |

### 2.2 内容迁移原则

#### 原则1: 渐进式揭示 (Progressive Disclosure)

**核心概念**: 将信息分层，用户先看核心，需要时再深入

```
层级1: SKILL.md (核心工作流)
  ├─ 简明的步骤列表
  ├─ 关键概念说明
  └─ 指向详细内容的引用

层级2: references/xxx_guide.md (详细内容)
  ├─ 深入的操作说明
  ├─ 完整的规则和示例
  └─ 边界情况处理

层级3: scripts/xxx.py (自动化工具)
  └─ 验证和辅助脚本
```

**实际案例**:
```markdown
# SKILL.md中 (简洁)
### Step 5: Calculate Scores
Use the 7-dimensional scoring formula:
- spread_score (23%)
- severity_score (20%)
- ...

**See**: `references/scoring_methodology.md` for formulas

# references/scoring_methodology.md中 (详细)
## Spread Score Calculation
```python
spread_score = min(total_count / 500, 1.0) × 100
```
### Edge Cases:
1. If total_count < 0: raise error
2. If total_count = 0: return 0
...
```

#### 原则2: 职责分离

| 文件类型 | 职责 | 行数限制 |
|---------|------|---------|
| SKILL.md | 核心工作流、快速参考 | <500行 |
| references/*.md | 详细操作指南 | 200-500行/文件 |
| scripts/*.py | 自动化验证工具 | 无限制 |

#### 原则3: 单一职责

每个reference guide应该专注于**一个主题**:

✅ **好的分割**:
- `extraction_guide.md` - 数据提取方法
- `scoring_methodology.md` - 评分公式和规则
- `professional_title_guide.md` - 标题生成规范

❌ **不好的分割**:
- `everything_about_analysis.md` - 把所有内容塞在一起

### 2.3 具体迁移映射（本案例）

#### 从 fact-analyzer标准.md (809行) → public-opinion-fact-analysis skill

```
原文件结构:                          目标Skill结构:
─────────────────────────────────────────────────────────
fact-analyzer标准.md (809行)         public-opinion-fact-analysis/
├─ 核心使命 (20行)                   ├─ SKILL.md (290行)
├─ 输入规范 (30行)            ────>  │   ├─ Overview
├─ 评分模型详解 (400行)              │   ├─ 8-step workflow (简明)
├─ 输出Schema (150行)                │   └─ Quick reference
├─ 工作流程 (80行)                   │
├─ 质量检查 (50行)                   ├─ references/
├─ 错误处理 (40行)                   │   ├─ extraction_guide.md (提取方法)
├─ 示例 (39行)                       │   ├─ scoring_engine_guide.md (评分详解)
└─ ...                               │   ├─ professional_title_guide.md (标题规范)
                                     │   ├─ json_schema.json (输出格式)
                                     │   ├─ dimension_definitions.md (维度定义)
                                     │   └─ workflow_details.md (详细流程)
                                     │
                                     └─ scripts/
                                         ├─ validate_json_output.py
                                         └─ test_scoring_config.py
```

**关键点**:
- ✅ SKILL.md只保留核心流程（290行）
- ✅ 详细内容分散到6个reference guides
- ✅ 新增2个验证脚本
- ✅ 总内容增加但更有组织（290 + 2103 + 320 = 2713行）

---

## 3. 用户交互模式变化

### 3.1 交互架构对比

#### 改造前：直接Agent调用

```
用户 ─────> Claude主控 ────> @fact-analyzer
                               ↓ (读取1000行agent定义)
                               ↓ (加载到context)
                               ↓ (执行分析)
                               结果
```

**特点**:
- 用户使用 `@agent-name` 语法
- Agent定义文件包含所有指令
- 每次调用加载全部内容

#### 改造后：Agent + Skills自动加载

```
用户 ─────> Claude主控 ────> Task tool (fact-analyzer)
                               ↓ (Agent启动)
                               ↓ (自动加载public-opinion-fact-analysis skill)
                               ↓ (SKILL.md: 290行核心内容)
                               ↓ (按需引用references/)
                               ↓ (执行分析)
                               结果
```

**特点**:
- 用户使用 Task tool
- Agent轻量级定义（入口）
- Skill自动加载，渐进式访问内容

### 3.2 用户命令对比

#### 改造前命令

```bash
# 1. 初始化环境
python 舆情分析工作流控制器.py 第1批舆情

# 2. 在Claude对话中调用Agent
"@fact-analyzer 处理批次 第1批舆情"

# 3. 在Claude对话中调用第二个Agent
"@legal-risk-assessor 处理批次 第1批舆情"
```

#### 改造后命令

```bash
# 1. 初始化环境 (不变)
python 舆情分析工作流控制器.py 第1批舆情

# 2. 在Claude对话中使用Task tool调用Agent
"使用Task工具调用fact-analyzer agent，处理批次第1批舆情"

# 或者明确说明使用Task tool:
"请用Task tool，subagent_type为fact-analyzer，处理批次第1批舆情"

# 3. 第二个Agent (同样方式)
"使用Task工具调用legal-risk-assessor agent，处理批次第1批舆情"
```

**关键变化**:
- ❌ 不再使用 `@agent-name` 语法
- ✅ 改用 Task tool方式（但用户可以用自然语言描述）
- ✅ Skill自动加载，用户无需关心

### 3.3 用户工作流对比

#### 完整对比表

| 操作步骤 | 改造前 | 改造后 | 变化 |
|---------|--------|--------|------|
| **准备数据** | 放Excel到`输入/批次/` | 放Excel到`输入/批次/` | 无变化 ✅ |
| **初始化环境** | `python 工作流控制器.py 批次名` | `python 工作流控制器.py 批次名` | 无变化 ✅ |
| **验证环境** | `python 环境检查器.py 批次名` | `python 环境检查器.py 批次名` | 无变化 ✅ |
| **调用Agent 1** | `@fact-analyzer 处理...` | `用Task工具调用fact-analyzer...` | ⚠️ 语法变化 |
| **验证输出1** | `python 环境检查器.py --check-outputs` | `python 环境检查器.py --check-outputs` | 无变化 ✅ |
| **调用Agent 2** | `@legal-risk-assessor 处理...` | `用Task工具调用legal-risk-assessor...` | ⚠️ 语法变化 |
| **验证输出2** | `python 环境检查器.py --check-outputs` | `python 环境检查器.py --check-outputs` | 无变化 ✅ |

**核心结论**:
- ✅ **Python工具使用完全不变**
- ⚠️ **Agent调用语法改变**（从@到Task tool）
- ✅ **Agent内部逻辑不变**（Skills自动加载，用户无感知）

### 3.4 主控制器使用Skills

**新增功能**: 主控制器也可以使用Skill辅助编排

```
用户: "处理批次20251022_AM"

主控制器可选操作:
1. [可选] 使用workflow-orchestration-tools skill
   - 获取完整的编排指导
   - 查看检查点要求
   - 了解错误恢复流程

2. 初始化环境 (Python工具)
3. 调用fact-analyzer (Task tool + auto-load skill)
4. 验证输出
5. 调用legal-risk-assessor (Task tool + auto-load skill)
6. 验证输出
```

**Skill调用方式**:
```
Claude: "我先使用workflow-orchestration-tools skill来了解完整流程"
(内部使用Skill tool)
```

---

## 4. 通用改造步骤

### 4.1 改造准备阶段

#### Step 1: 审查现有架构

**检查清单**:
- [ ] 识别所有Agent（通常在`.claude/agents/`）
- [ ] 找到所有标准文档（通常是长Markdown文件）
- [ ] 列出Agent依赖的配置文件
- [ ] 识别共享的工具脚本
- [ ] 检查Agent之间的依赖关系

**输出**: 架构清单文档

#### Step 2: 设计Skills结构

**决策要点**:

1. **需要几个Skills?**
   - 每个主要Agent → 1个专属Skill
   - 多个Agent共享的知识 → 1个共享Skill
   - 主控制器编排逻辑 → 1个编排Skill

2. **Skill命名规范**:
   - 使用kebab-case
   - 描述性名称
   - 示例: `public-opinion-fact-analysis`, `batch-processing-conventions`

3. **内容分配**:
   ```
   Skill 1: Agent A专属知识
   Skill 2: Agent B专属知识
   Skill 3: 共享基础知识
   Skill 4: 主控制器编排知识
   ```

**本案例设计**:
```
4个Skills:
├─ public-opinion-fact-analysis (fact-analyzer专属)
├─ legal-risk-assessment-reporting (legal-risk-assessor专属)
├─ batch-processing-conventions (共享)
└─ workflow-orchestration-tools (主控制器)
```

### 4.2 内容迁移阶段

#### Step 3: 创建Skill目录结构

```bash
.claude/skills/your-skill-name/
├── SKILL.md                    # 核心文件，YAML frontmatter + 工作流
├── references/                 # 详细指南目录
│   ├── guide1.md
│   ├── guide2.md
│   └── ...
├── scripts/                    # 工具脚本（可选）
│   ├── validate.py
│   └── ...
└── assets/                     # 资源文件（可选）
    └── ...
```

#### Step 4: 编写SKILL.md

**SKILL.md模板结构**:

```markdown
---
name: your-skill-name
description: Clear, concise description for when to use this skill. Triggers on keyword1, keyword2, keyword3.
---

# Skill Title

## Overview
Brief introduction (2-3 sentences)

## When to Use This Skill
Clear trigger scenarios with examples

## Core Workflow (N Steps)

### Step 1: Action Name
- What to do
- Key points
- **See**: `references/guide1.md` for details

### Step 2: ...
...

## Quick Reference
Summary table or checklist

## Common Issues
Top 3-5 issues and quick solutions
```

**关键规则**:
- ✅ YAML frontmatter必须包含name和description
- ✅ Description应包含trigger keywords
- ✅ 总长度<500行
- ✅ 使用"See references/"指向详细内容
- ✅ 专注于核心工作流

#### Step 5: 创建Reference Guides

**每个guide专注一个主题**:

```markdown
# Guide Title

## Purpose
Why this guide exists

## Detailed Instructions
Step-by-step with examples

## Edge Cases
Special situations and handling

## Examples
Real-world examples

## Quick Reference
Summary for quick lookup
```

**命名规范**:
- 使用snake_case
- 描述性名称
- 示例: `extraction_guide.md`, `error_recovery_guide.md`

#### Step 6: 迁移验证脚本

**脚本组织**:
```python
# scripts/validate_something.py

"""
Brief description of what this script validates
"""

def validate_input(data):
    """Validate input data"""
    pass

def validate_output(result):
    """Validate output result"""
    pass

if __name__ == "__main__":
    # CLI usage
    pass
```

### 4.3 集成更新阶段

#### Step 7: 更新Agent定义文件

**改造前** (agent.md):
```markdown
---
name: my-agent
description: ...
---

You are an expert...

## MANDATORY: Read Standards First
1. Read /path/to/standards.md
2. Follow all specifications
3. ...

## Core Mission
... (500行详细指令)

## Detailed Workflow
... (300行详细步骤)
```

**改造后** (agent.md):
```markdown
---
name: my-agent
description: ...
---

You are an expert...

## MANDATORY: Use Skills System
1. This agent automatically loads the `your-skill-name` skill
2. The skill contains detailed workflow and specifications
3. Reference skill's `references/` guides for detailed procedures

## Core Mission (brief overview)
... (50行概述)

## Quick Workflow Reference
... (50行快速参考，指向skill)
```

**改造要点**:
- ✅ 移除"READ"指令，改为"USE SKILL"说明
- ✅ 说明Skill自动加载
- ✅ 保留最精简的角色定义和核心概述
- ✅ 添加指向Skill的引用

#### Step 8: 更新项目主文档

**CLAUDE.md更新**:
```markdown
# 添加Skills说明章节
## Skills Architecture (v2.0)

**Available Skills**:
- skill-1: Purpose
- skill-2: Purpose
...

**Skills Location**: `.claude/skills/`

# 更新Agent调用说明
## Call Agents

Use Task tool with subagent_type parameter:
- fact-analyzer → auto-loads skill-1
- legal-assessor → auto-loads skill-2
```

**README.md更新**:
```markdown
# 添加Skills章节
## Skills (模块化知识库) ⭐ v2.0

- **skill-1** - Purpose
- **skill-2** - Purpose

Skills位置: `.claude/skills/`

# 更新使用说明
## Quick Start

### 调用Agent
使用Task工具调用agent，skill会自动加载...
```

#### Step 9: 归档旧文件

**建议归档结构**:
```
归档文件/
├── v1_旧标准文档/      # 被Skills取代的标准文档
├── v1_改造报告/        # Phase报告和改造记录
├── v1_配置说明/        # 旧版配置文档
└── v1_临时文件/        # 测试脚本等
```

**归档原则**:
- ✅ 保留历史文档（不删除）
- ✅ 分类清晰
- ✅ 在主README中说明归档文件位置
- ✅ 标记"仅供参考，已被X取代"

### 4.4 验证测试阶段

#### Step 10: 质量检查

**Skill结构验证**:
```bash
# 检查SKILL.md行数
wc -l .claude/skills/*/SKILL.md

# 检查YAML frontmatter
head -5 .claude/skills/*/SKILL.md

# 检查references目录
ls -R .claude/skills/*/references/
```

**路径引用验证**:
```bash
# 搜索旧路径引用
grep -r "/old/path" .claude/agents/
grep -r "/old/path" .claude/skills/

# 搜索错误的文件引用
grep -r "old_standard.md" .
```

#### Step 11: 功能测试

**测试清单**:
- [ ] 初始化环境（Python工具）
- [ ] 调用Agent 1（Task tool）
- [ ] 验证Skill自动加载
- [ ] 验证输出格式
- [ ] 调用Agent 2
- [ ] 端到端完整流程

---

## 5. 最佳实践

### 5.1 Skill设计最佳实践

#### ✅ DO (推荐)

1. **保持SKILL.md精简**
   ```markdown
   ❌ 不要把所有详细内容塞进SKILL.md
   ✅ SKILL.md只包含核心工作流 + 指向references的链接
   ```

2. **合理分割Reference Guides**
   ```
   ✅ 每个guide一个主题（200-500行）
   ❌ 一个巨大的guide包含所有内容
   ```

3. **使用清晰的引用**
   ```markdown
   ✅ **See**: `references/extraction_guide.md` for detailed patterns
   ❌ 模糊的"查看详细文档"
   ```

4. **提供快速参考**
   ```markdown
   ✅ 在SKILL.md末尾提供Quick Reference表格或清单
   ```

5. **包含实用工具**
   ```
   ✅ scripts/validate_output.py - 自动化验证
   ✅ scripts/check_format.py - 格式检查
   ```

#### ❌ DON'T (避免)

1. **不要重复内容**
   ```
   ❌ SKILL.md和references都写详细步骤
   ✅ SKILL.md概述 + references详细
   ```

2. **不要创建过多skills**
   ```
   ❌ 每个小功能都创建一个skill
   ✅ 按Agent或功能模块合理分组
   ```

3. **不要忽略YAML frontmatter**
   ```yaml
   ❌ 缺少description或triggers
   ✅ 完整的name和description，包含清晰的trigger keywords
   ```

4. **不要硬编码路径**
   ```markdown
   ❌ /root/project/file.md
   ✅ 相对路径或skill内部引用
   ```

### 5.2 Agent定义更新最佳实践

#### 改造Agent定义的Golden Rules

1. **精简但保留本质**
   ```markdown
   ✅ 保留: 角色定义、核心使命、关键约束
   ❌ 移除: 详细步骤、完整规则、大量示例
   ```

2. **明确说明Skill自动加载**
   ```markdown
   ✅ "This agent automatically loads the `skill-name` skill"
   ❌ 让用户猜测如何使用skill
   ```

3. **提供快速访问路径**
   ```markdown
   ✅ "See `references/xxx.md` in the skill for details"
   ✅ 保留最关键的提醒和警告
   ```

4. **更新所有旧路径引用**
   ```markdown
   ❌ "READ /path/to/old_standards.md"
   ✅ "USE SKILL: skill-name (auto-loaded)"
   ```

### 5.3 主文档更新最佳实践

1. **CLAUDE.md应清楚说明**:
   - Skills架构概述
   - 哪些Skills可用
   - Skills如何自动加载
   - Agent调用方式变化

2. **README.md应包含**:
   - Skills章节
   - 使用说明更新
   - 归档文件位置
   - 版本历史

3. **创建迁移文档**:
   - 改造前后对比
   - 用户操作变化
   - 故障排查更新

---

## 6. 常见问题

### Q1: 什么时候需要改造为Skills架构?

**需要改造的信号**:
- ✅ Agent定义文件>500行
- ✅ 标准文档>800行
- ✅ 内容分散在多个大文件中
- ✅ 需要重复维护相似内容
- ✅ 新加入的开发者难以快速理解

**可以不改造**:
- ❌ 系统简单，agent定义<300行
- ❌ 只有1-2个agent，无复杂协作
- ❌ 内容已经很好组织且精简

### Q2: 改造会破坏现有功能吗?

**不会，如果遵循以下原则**:
- ✅ 保留所有必要的指令内容（只是重新组织）
- ✅ 保持Python工具不变
- ✅ 保持输入输出格式不变
- ✅ 完整测试迁移后的系统

### Q3: 用户需要学习新的使用方式吗?

**部分需要**:
- ✅ Python工具使用**完全不变**
- ⚠️ Agent调用方式变化（从@到Task tool）
- ✅ Skills自动加载，用户无感知
- ✅ 输入输出格式不变

**最小化学习成本**:
- 更新README和CLAUDE.md说明
- 提供before/after对比
- 保持向后兼容（如果可能）

### Q4: 如何决定创建几个Skills?

**推荐结构**:
```
基础配置: 1个Skills (<10KB)
- 共享配置、命名规范等

每个主要Agent: 1个Skill (30-50KB)
- 专属工作流和规则

主控制器: 1个Skill (30-40KB)
- 编排逻辑和检查点
```

**避免**:
- ❌ 把所有内容塞进1个巨大的skill
- ❌ 为每个小功能创建独立skill

### Q5: Reference guides应该多详细?

**平衡原则**:
```
SKILL.md:     20% 详细度，80% 概述
References:   80% 详细度，完整说明
Scripts:      100% 自动化
```

**示例**:
```markdown
# SKILL.md
### Step 3: Extract Data
Extract timeline, spread, and engagement data.
**See**: `references/extraction_guide.md` for patterns

# references/extraction_guide.md
## Timeline Extraction
Regex patterns:
- `发布时间[:：]\s*(\d{4}-\d{2}-\d{2})`
- `(\d{4})年(\d{1,2})月(\d{1,2})日`

Edge cases:
1. Missing year → use current year
2. Invalid format → log warning, use fallback
...
```

### Q6: 改造完成后如何维护?

**维护检查清单**:
- [ ] 每次更新agent逻辑时，同步更新对应Skill
- [ ] 定期检查SKILL.md是否仍<500行
- [ ] 添加新功能时，考虑是否需要新的reference guide
- [ ] 保持文档和代码同步
- [ ] 定期运行端到端测试

---

## 7. 快速检查清单

### 改造前检查

- [ ] 已审查所有Agent定义文件
- [ ] 已列出所有标准文档和依赖
- [ ] 已设计Skills结构
- [ ] 已规划内容分配

### 改造中检查

- [ ] 每个Skill的SKILL.md<500行
- [ ] YAML frontmatter完整（name + description + triggers）
- [ ] Reference guides合理分割（200-500行/文件）
- [ ] Agent定义文件已更新，移除旧路径引用
- [ ] CLAUDE.md和README.md已更新
- [ ] 旧文件已归档并标记

### 改造后检查

- [ ] 无旧路径引用残留
- [ ] 所有Skills打包正确
- [ ] Agent调用方式文档化
- [ ] 端到端测试通过
- [ ] 用户文档完整

---

## 8. 参考案例总结

### 本案例改造统计

**改造前 (v1.x)**:
- Agent定义: 2个文件，各~1000行
- 标准文档: 3个MD，共~2300行
- 结构: 单体文档

**改造后 (v2.0)**:
- Agent定义: 2个文件，各~400行（精简）
- Skills: 4个skill包，共120KB
  - SKILL.md: 4个文件，共1294行
  - References: 20个guides，共7379行
  - Scripts: 6个工具，共1375行
- 结构: 模块化

**改进效果**:
- ✅ SKILL.md全部<500行（符合最佳实践）
- ✅ 内容总量增加（更完整详细）但更有组织
- ✅ 23/23集成测试通过（100%）
- ✅ 维护性大幅提升

---

## 附录: 工具和脚本

### A. 批量检查脚本

```bash
#!/bin/bash
# check_skill_compliance.sh - 检查Skills合规性

echo "=== Checking SKILL.md line counts ==="
for skill in .claude/skills/*/SKILL.md; do
    lines=$(wc -l < "$skill")
    if [ $lines -gt 500 ]; then
        echo "⚠️  $(basename $(dirname $skill)): $lines lines (>500)"
    else
        echo "✅ $(basename $(dirname $skill)): $lines lines"
    fi
done

echo -e "\n=== Checking YAML frontmatter ==="
for skill in .claude/skills/*/SKILL.md; do
    if head -1 "$skill" | grep -q "^---$"; then
        echo "✅ $(basename $(dirname $skill)): Has frontmatter"
    else
        echo "❌ $(basename $(dirname $skill)): Missing frontmatter"
    fi
done

echo -e "\n=== Checking for old path references ==="
if grep -r "/old/path" .claude/ 2>/dev/null; then
    echo "⚠️  Found old path references"
else
    echo "✅ No old path references"
fi
```

### B. Skill模板生成器

```python
#!/usr/bin/env python3
# create_skill_template.py - 生成Skill模板结构

import os
import sys

def create_skill_template(skill_name):
    """Create a new skill template structure"""

    base_dir = f".claude/skills/{skill_name}"

    # Create directories
    os.makedirs(f"{base_dir}/references", exist_ok=True)
    os.makedirs(f"{base_dir}/scripts", exist_ok=True)
    os.makedirs(f"{base_dir}/assets", exist_ok=True)

    # Create SKILL.md template
    skill_md = f"""---
name: {skill_name}
description: Brief description of when to use this skill. Triggers on keyword1, keyword2.
---

# {skill_name.replace('-', ' ').title()}

## Overview
Brief introduction (2-3 sentences)

## When to Use This Skill
- Scenario 1
- Scenario 2

## Core Workflow (N Steps)

### Step 1: Action Name
Description
**See**: `references/guide1.md` for details

### Step 2: ...

## Quick Reference
Summary or checklist
"""

    with open(f"{base_dir}/SKILL.md", 'w') as f:
        f.write(skill_md)

    # Create reference guide template
    ref_template = """# Guide Title

## Purpose
Why this guide exists

## Instructions
Detailed steps

## Examples
Real-world examples

## Quick Reference
Summary
"""

    with open(f"{base_dir}/references/example_guide.md", 'w') as f:
        f.write(ref_template)

    print(f"✅ Created skill template: {base_dir}")
    print(f"   - SKILL.md")
    print(f"   - references/example_guide.md")
    print(f"   - scripts/ (empty)")
    print(f"   - assets/ (empty)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_skill_template.py <skill-name>")
        sys.exit(1)

    create_skill_template(sys.argv[1])
```

---

## 总结

**Skills架构改造的核心要点**:

1. **本质**: 从单体文档到模块化知识包
2. **内容迁移**: 标准文档 → Skill包（SKILL.md + references + scripts）
3. **用户交互**: @agent → Task tool（但Python工具不变）
4. **关键规则**: SKILL.md<500行，渐进式揭示，职责分离
5. **维护性**: 大幅提升，便于更新和扩展

**复用此指南时**:
- 根据项目规模调整Skills数量
- 保持文档结构一致性
- 遵循最佳实践
- 完整测试迁移结果

---

**文档版本**: 1.0
**基于案例**: 舆情法律分析系统
**适用范围**: 所有Claude Agent多Agent项目
**最后更新**: 2025-10-22
