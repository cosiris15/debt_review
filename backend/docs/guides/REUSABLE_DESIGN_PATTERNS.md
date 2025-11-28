# Claude Code 企业级智能体系统设计模式参考

## 文档目的

本文档提炼了债权审查系统（Debt Review Skills）项目的核心设计模式和架构原则，供其他需要构建复杂 AI 智能体协作系统的项目参考使用。

**适用场景**：
- 需要多个 AI 智能体协同完成复杂工作流
- 涉及大量文件处理和结构化输出
- 要求高质量标准和完整审计追踪
- 需要零中断的自动化处理流程

---

## 设计模式 1: Skills Architecture（技能架构模式）

### 核心思想

**分离编排与知识**：将智能体定义（orchestration）与详细知识（domain knowledge）解耦，通过模块化的 Skills 实现知识复用和自动发现。

### 架构结构

```
.claude/
├── agents/                    # 智能体定义（轻量级编排）
│   ├── agent-1.md            # 100-300 lines: 流程协调
│   ├── agent-2.md
│   └── agent-3.md
│
└── skills/                    # 技能模块（详细知识）
    ├── skill-domain-1/
    │   ├── SKILL.md          # <500 lines: 核心工作流
    │   ├── templates/        # 输出模板
    │   │   └── template.md
    │   └── references/       # 详细参考
    │       ├── procedure-1.md
    │       └── standard-2.md
    │
    ├── skill-domain-2/
    │   └── ...
    │
    └── skill-foundations/     # 共享基础知识
        ├── SKILL.md
        └── references/
            ├── core-principles.md
            ├── glossary.md
            └── standards.md
```

### 关键设计原则

#### 1. Progressive Disclosure（渐进式展示）
- **SKILL.md**: 概览和核心流程（<500 lines）
- **references/**: 详细程序和标准（无限制）
- **templates/**: 结构化输出模板

#### 2. Automatic Discovery（自动发现）
每个 SKILL.md 包含 YAML frontmatter：
```yaml
---
name: skill-name                    # Max 64 chars
description: |                      # Max 1024 chars
  Clear description of when to use this skill.
  Include usage examples and context.
---
```

Claude Code 根据 `description` 自动加载相关技能，无需手动调用。

#### 3. Separation of Concerns（关注点分离）

**Agent 定义职责**（agents/*.md）：
- 工作流程编排（workflow orchestration）
- 前置条件检查（prerequisite verification）
- 质量检查点（quality checkpoints）
- 与其他 agent 的交接（handover protocols）

**Skill 职责**（skills/*/SKILL.md）：
- 详细工作流程（detailed procedures）
- 领域知识（domain knowledge）
- 标准和规范（standards and conventions）
- 示例和模板（examples and templates）

#### 4. Shared Foundations（共享基础）

创建一个 `xxx-foundations` 技能，包含：
- 核心原则（core principles）
- 通用术语表（glossary）
- 法律/业务标准（legal/business standards）
- 系统架构概览（system architecture overview）

**收益**：避免知识重复，确保所有 agents 使用一致的标准。

### 实施步骤

1. **识别知识域**：将系统功能分解为 3-6 个独立领域
2. **提取共享知识**：建立 foundations skill 包含通用标准
3. **创建专业技能**：每个领域一个 skill，保持 SKILL.md <500 lines
4. **简化 Agent**：Agent 文件只保留编排逻辑，引用 skills
5. **编写 YAML**：确保 description 清晰描述使用场景

### 优势对比

| 传统单文件模式 | Skills 架构模式 |
|---------------|----------------|
| Agent 定义 180-1200 lines | Agent 定义 100-300 lines |
| 知识重复，多处维护 | 知识模块化，单点维护 |
| 难以导航和查找 | 按领域组织，快速定位 |
| 手动加载所有内容 | 自动发现相关知识 |
| 大文件，Git diff 困难 | 小文件，清晰的变更追踪 |

---

## 设计模式 2: Three-Agent Collaboration（三智能体协作模式）

### 核心思想

**专业化分工 + 顺序处理**：将复杂任务分解为三个专业化阶段，强制顺序执行确保质量和一致性。

### 架构设计

```
Main Controller (orchestrator)
    ↓
Agent 1: Data Extractor          # 数据提取和验证
    → Output: raw_data_report.md
    ↓
Agent 2: Analysis Specialist     # 专业分析和计算
    → Output: analysis_report.md + calculation_files/
    ↓
Agent 3: Report Formatter        # 格式化和标准化
    → Output: final_deliverable.md + file_inventory.md
```

### 关键设计要素

#### 1. Stage Specialization（阶段专业化）

**Stage 1 - 提取验证 Agent**：
- **职责**：提取原始数据、基础验证、建立事实关系
- **输出**：结构化事实报告（technical working paper）
- **禁止**：复杂计算、法律结论、格式化处理
- **原则**：只记录事实，不做推论

**Stage 2 - 分析计算 Agent**：
- **职责**：专业分析、精确计算、法律判断
- **输入**：Stage 1 的事实报告
- **输出**：分析报告 + 计算过程文件
- **禁止**：修改事实、省略计算过程
- **原则**：完整追溯，严格工具使用

**Stage 3 - 整理输出 Agent**：
- **职责**：报告整合、模板应用、文件组织
- **输入**：Stage 1 + Stage 2 的技术报告
- **输出**：客户交付物 + 文件清单
- **禁止**：修改技术结论、简化分析内容
- **原则**：保留准确性，统一格式

#### 2. Sequential Processing（强制顺序处理）

**⚠️ 关键规则**：一次处理一个完整案例

```
✅ 正确流程（Serial）：
Case A: Stage 1 → Stage 2 → Stage 3 → Complete ✓
Case B: Stage 1 → Stage 2 → Stage 3 → Complete ✓
Case C: Stage 1 → Stage 2 → Stage 3 → Complete ✓

❌ 错误流程（Batch）：
Cases A,B,C: All Stage 1 → All Stage 2 → All Stage 3
```

**原因**：
- 避免状态混乱（context confusion）
- 确保质量检查点有效（checkpoint effectiveness）
- 便于错误定位（error isolation）
- 保证完整审计追踪（complete audit trail）

#### 3. Quality Checkpoints（质量检查点）

每个 Agent 完成后，Main Controller 验证：

```
Stage 1 Checkpoint:
□ 输出文件存在于正确目录
□ 必需数据字段已提取
□ 关键日期已验证
□ 事实来源已标注

Stage 2 Checkpoint:
□ 计算使用指定工具（非手工）
□ 计算过程文件已生成
□ 日期与 Stage 1 一致
□ 分析结论有充分依据

Stage 3 Checkpoint:
□ 模板正确应用
□ 技术结论未被修改
□ 文件命名符合规范
□ 所有文件已归档
```

#### 4. Handover Protocol（交接协议）

每个阶段结束时必须：
- **明确声明输出位置**："Report saved to `path/to/file.md`"
- **验证文件存在**：使用 `ls` 或文件检查确认
- **总结关键发现**：3-5 条核心要点供下阶段参考
- **标注异常情况**：明确指出需要下阶段特别关注的问题

### 实施建议

1. **Agent 命名规范**：使用清晰的角色名（extractor, analyzer, formatter）
2. **输出目录隔离**：每个阶段有独立输出目录（working_papers/, calculations/, final_reports/）
3. **主控编排文档**：创建专门的 orchestration skill 说明完整流程
4. **质量标准文档**：建立明确的 checkpoint checklist

---

## 设计模式 3: Zero-Interruption Automation（零中断自动化模式）

### 核心思想

**完全预授权 + 透明初始化**：通过权限配置和自动环境初始化，实现用户一次命令即可全流程运行，无需人工干预。

### 权限配置策略

#### 完全预授权配置

**文件**：`.claude/settings.local.json`

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

**含义**：授权所有 Bash 命令，无需逐个请求批准

**适用场景**：
- ✅ 本地项目环境，操作限定在项目目录内
- ✅ 复杂工作流需要数十种命令组合
- ✅ 生产环境需要无人值守运行
- ❌ 不适用：涉及系统级操作或敏感数据访问

#### 细粒度控制配置（可选）

如需严格控制，可明确列出允许的命令：

```json
{
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(python:*)",
      "Bash(python your_script.py:*)",
      "Bash(mkdir:*)",
      "Bash(mv:*)"
    ],
    "deny": [
      "Bash(rm -rf /:*)",
      "Bash(shutdown:*)"
    ]
  }
}
```

**权衡**：细粒度控制更安全但维护成本高，容易遗漏命令导致流程中断。

### 自动环境初始化

#### 设计原则

**对用户透明**：用户只需说"处理案例 X"，系统自动检测和初始化环境

#### 实现逻辑

```python
# 伪代码示例
def auto_initialize_environment(case_id):
    config_file = f"outputs/{case_id}/.processing_config.json"

    # Step 1: 检测是否已初始化
    if file_exists(config_file):
        print("Environment already initialized, proceeding...")
        return load_config(config_file)

    # Step 2: 自动初始化
    print("Initializing processing environment...")
    run_command(f"python workflow_controller.py {case_id}")

    # Step 3: 验证初始化成功
    if not file_exists(config_file):
        raise Exception("Initialization failed!")

    print("Environment initialized successfully ✓")
    return load_config(config_file)

# Main workflow
def process_case(case_id):
    # 自动初始化（对用户透明）
    config = auto_initialize_environment(case_id)

    # 执行三阶段工作流
    run_agent_1(config)
    run_agent_2(config)
    run_agent_3(config)
```

#### 初始化脚本职责

创建一个 `workflow_controller.py` 负责：
- 创建标准目录结构
- 生成配置文件（`.processing_config.json`）
- 加载项目级配置（如 `project_config.ini`）
- 设置文件命名模板
- 验证环境就绪

#### 配置文件示例

`.processing_config.json`:
```json
{
  "case_info": {
    "batch": "1",
    "number": "115",
    "name": "ABC Company",
    "processing_date": "2025-10-26"
  },
  "critical_dates": {
    "bankruptcy_filing_date": "2024-06-15",
    "interest_stop_date": "2024-06-14"
  },
  "paths": {
    "work_papers": "outputs/batch-1/115-ABC-Company/working_papers/",
    "final_reports": "outputs/batch-1/115-ABC-Company/final_reports/",
    "calculations": "outputs/batch-1/115-ABC-Company/calculations/"
  },
  "file_templates": {
    "fact_check_report": "{name}_fact_check_report.md",
    "analysis_report": "{name}_analysis_report.md",
    "final_deliverable": "PROJ2025_{name}_review_{date}.md"
  }
}
```

### 用户体验设计

**理想交互**：
```
User: "Please process Case 115"
System: [Auto-detects, auto-initializes if needed]
System: "Processing Case 115..."
System: "Stage 1: Extracting data... ✓"
System: "Stage 2: Analyzing... ✓"
System: "Stage 3: Formatting report... ✓"
System: "Complete! Final report: outputs/batch-1/115-ABC-Company/final_reports/..."
```

**用户无需知道**：
- ❌ 环境是否需要初始化
- ❌ 配置文件如何生成
- ❌ 目录结构如何创建
- ❌ 需要哪些 Bash 权限

**系统自动处理所有实现细节**

---

## 设计模式 4: Mandatory Tool Usage（强制工具使用模式）

### 核心思想

**零人工计算 + 完整审计追踪**：对于关键操作（如计算），强制使用标准化工具并保存完整过程。

### 设计要素

#### 1. 专用工具开发

开发 CLI 工具封装复杂计算逻辑：

```python
# universal_calculator_cli.py 示例
import argparse

def calculate_interest_simple(principal, rate, start_date, end_date):
    # 实现计算逻辑
    result = ...

    # 生成过程文件（Excel/CSV）
    process_file = generate_process_table(principal, rate, start_date, end_date, result)

    return {
        "total_interest": result,
        "process_file": process_file,
        "command_used": f"python calculator.py simple --principal {principal} ..."
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["simple", "compound", "floating"])
    parser.add_argument("--principal", type=float, required=True)
    # ... other arguments

    args = parser.parse_args()
    result = calculate_interest_simple(args.principal, ...)
    print(json.dumps(result, indent=2))
```

#### 2. 强制使用规则

在 Agent 定义中明确规定：

```markdown
## ⚠️ MANDATORY: Calculator Tool Usage

**Zero-Tolerance Rule**: ALL interest calculations MUST use the calculator tool.

**Prohibited Actions**:
- ❌ Manual calculations (even for simple cases)
- ❌ Spreadsheet formulas without tool
- ❌ Estimations or approximations

**Required Process**:
1. Prepare calculation parameters
2. Execute: `python universal_calculator_cli.py [mode] [params]`
3. Document exact command used in report
4. Save generated process file to calculations/ directory
5. Reference process file in analysis report

**Quality Check**:
□ Calculator command documented
□ Process file exists in calculations/ directory
□ Results cited from tool output (not manually typed)
```

#### 3. 过程文件生成

工具必须生成可审计的过程文件：

**Excel/CSV 格式示例**：
| Date Period | Days | Principal | Rate | Daily Rate | Interest |
|-------------|------|-----------|------|------------|----------|
| 2024-01-01 to 2024-03-31 | 90 | 100,000 | 4.35% | 0.0119% | 1,071.00 |
| 2024-04-01 to 2024-06-14 | 75 | 100,000 | 3.95% | 0.0108% | 810.00 |
| **Total** | 165 | | | | **1,881.00** |

**TXT 格式示例**：
```
Interest Calculation Process
============================
Principal: 100,000.00
Start Date: 2024-01-01
End Date: 2024-06-14

Period 1: 2024-01-01 to 2024-03-31 (90 days)
Rate: 4.35% annual = 0.0119% daily
Interest: 100,000 × 0.0119% × 90 = 1,071.00

Period 2: 2024-04-01 to 2024-06-14 (75 days)
Rate: 3.95% annual = 0.0108% daily
Interest: 100,000 × 0.0108% × 75 = 810.00

Total Interest: 1,881.00
```

#### 4. 工具能力嵌入

将参考数据嵌入工具内部（如利率数据库）：

```python
# 嵌入历史利率数据
LPR_RATES = {
    "1y": {
        "2024-01-01": 3.45,
        "2024-03-20": 3.95,
        "2024-08-20": 3.35,
        # ...
    },
    "5y": {
        "2024-01-01": 4.20,
        # ...
    }
}

def get_applicable_rate(date, term):
    """根据日期自动查找适用利率"""
    return LPR_RATES[term][date]
```

**收益**：
- Agent 无需查询外部数据源
- 确保使用准确的历史数据
- 简化 Agent 的参数准备工作

### 实施检查清单

构建强制工具使用模式时：

- [ ] 开发独立 CLI 工具（不依赖复杂环境）
- [ ] 实现多种计算模式（覆盖业务场景）
- [ ] 嵌入必要的参考数据
- [ ] 生成可审计的过程文件（Excel/CSV/TXT）
- [ ] 在 Agent 文档中明确标注"MANDATORY"
- [ ] 建立质量检查点验证工具使用
- [ ] 提供工具使用示例和参数说明

---

## 设计模式 5: Date Verification Protocol（日期验证协议模式）

### 核心思想

**关键日期是生命线**：对于业务逻辑中的关键日期，建立三重验证机制和跨阶段一致性检查。

### 协议设计

#### 1. 单一可信源（Single Source of Truth）

**Project-level 配置**：
```ini
# project_config.ini
[project_info]
project_name = XYZ Bankruptcy Case

[critical_dates]
bankruptcy_filing_date = 2024-06-15
interest_stop_date = 2024-06-14  # Must be filing_date - 1
```

**Case-level 配置**：
```json
// .processing_config.json
{
  "critical_dates": {
    "bankruptcy_filing_date": "2024-06-15",  // Loaded from project_config.ini
    "interest_stop_date": "2024-06-14"
  }
}
```

#### 2. 三重验证机制

**Verification Level 1 - Environment Initialization**:
```python
def initialize_environment(case_id):
    # Load dates from project_config.ini
    project_config = load_project_config()
    filing_date = project_config["critical_dates"]["bankruptcy_filing_date"]

    # Calculate derived dates
    interest_stop_date = filing_date - timedelta(days=1)

    # Verify consistency
    if interest_stop_date != project_config["critical_dates"]["interest_stop_date"]:
        raise Exception("Date inconsistency in project configuration!")

    # Write to case config
    save_case_config(case_id, {
        "bankruptcy_filing_date": filing_date,
        "interest_stop_date": interest_stop_date
    })
```

**Verification Level 2 - Agent Stage Processing**:
```markdown
## Agent 1: Data Extractor

**Before Starting Work**:
1. Read `.processing_config.json`
2. Load `bankruptcy_filing_date` and `interest_stop_date`
3. Verify: interest_stop_date == bankruptcy_filing_date - 1 day
4. **STOP if verification fails**
5. Document dates explicitly in output report:
   - "Bankruptcy Filing Date: 2024-06-15"
   - "Interest Stop Date: 2024-06-14"
```

**Verification Level 3 - Cross-Stage Consistency**:
```markdown
## Agent 2: Analyzer

**Before Starting Work**:
1. Read Agent 1's output report
2. Extract dates from report:
   - Bankruptcy Filing Date: [extract from report]
   - Interest Stop Date: [extract from report]
3. Compare with `.processing_config.json`
4. **STOP if ANY inconsistency found**
5. Report inconsistency to user for manual intervention
```

#### 3. Stop-on-Inconsistency Rule

**零容忍政策**：任何日期不一致必须停止处理

```python
def verify_dates_across_stages(config_dates, report_dates):
    if config_dates["bankruptcy_filing_date"] != report_dates["bankruptcy_filing_date"]:
        raise CriticalDateInconsistencyError(
            f"Date mismatch detected!\n"
            f"Config: {config_dates['bankruptcy_filing_date']}\n"
            f"Report: {report_dates['bankruptcy_filing_date']}\n"
            f"STOPPING PROCESSING. Manual review required."
        )
```

**原因**：
- 错误的日期会导致错误的利息计算
- 错误的日期会导致错误的诉讼时效判断
- 一个日期错误可能使整个分析无效

#### 4. 明确记录要求

每个阶段的输出必须显式记录关键日期：

```markdown
# Agent 1 Output Example

## 关键日期信息

**破产受理日期**: 2024-06-15
**停止计息日期**: 2024-06-14

> 上述日期已从环境配置 `.processing_config.json` 中验证获取。
> 验证时间: 2025-10-26 10:30:00
```

### 实施检查清单

- [ ] 识别业务关键日期（破产日期、合同日期等）
- [ ] 建立 project-level 配置文件
- [ ] 环境初始化时加载并验证日期
- [ ] 每个 Agent 开始工作前验证日期
- [ ] 跨 Agent 交接时验证日期一致性
- [ ] 报告中显式记录日期来源
- [ ] 建立 stop-on-inconsistency 异常机制

---

## 设计模式 6: File Organization Standards（文件组织规范模式）

### 核心思想

**标准化目录结构 + 模板化文件命名**：通过严格的文件组织规范，确保输出的可预测性和易维护性。

### 目录结构设计

#### 标准三层结构

```
outputs/
├── batch-1/                           # Level 1: 批次/项目分组
│   ├── case-115-ABC-Company/         # Level 2: 单个案例目录
│   │   ├── .processing_config.json   # 案例配置（隐藏文件）
│   │   ├── working_papers/           # Level 3: 工作底稿
│   │   │   ├── ABC-Company_fact_check_report.md
│   │   │   └── ABC-Company_analysis_report.md
│   │   ├── calculations/             # Level 3: 计算过程文件
│   │   │   ├── ABC-Company_interest_calculation.xlsx
│   │   │   └── ABC-Company_penalty_calculation.csv
│   │   └── final_reports/            # Level 3: 最终交付物
│   │       └── PROJ2025_ABC-Company_Review_20251026.md
│   │
│   ├── case-116-XYZ-Corp/
│   └── file_inventory.md             # 批次级文件清单
│
└── batch-2/
    └── ...
```

#### 设计原则

1. **批次隔离**：不同批次/项目完全隔离，避免混淆
2. **案例自包含**：每个案例目录包含所有相关文件
3. **类型分目录**：工作底稿、计算文件、最终报告分开存放
4. **配置本地化**：`.processing_config.json` 位于案例目录根部

### 文件命名规范

#### 模板化命名

在配置文件中定义模板：

```json
{
  "file_templates": {
    "fact_check_report": "{creditor_name}_fact_check_report.md",
    "analysis_report": "{creditor_name}_analysis_report.md",
    "final_deliverable": "{project_code}_{creditor_name}_Review_{date}.md",
    "interest_calculation": "{creditor_name}_interest_calculation.xlsx",
    "penalty_calculation": "{creditor_name}_penalty_calculation.csv"
  }
}
```

#### 命名规则

1. **一致性**：同一类型文件使用相同命名模式
2. **可排序**：使用 ISO 日期格式（YYYYMMDD）或编号前缀
3. **可识别**：文件名包含案例标识符
4. **无空格**：使用连字符或下划线代替空格
5. **扩展名明确**：`.md`, `.xlsx`, `.csv`, `.json`

#### 示例

```
✅ 正确命名:
- ABC-Company_fact_check_report.md
- PROJ2025_ABC-Company_Review_20251026.md
- ABC-Company_interest_calculation_2024Q1.xlsx

❌ 错误命名:
- report.md                          # 缺少案例标识
- ABC Company Report.md              # 包含空格
- ABC-Company_report_latest.md       # "latest" 不明确
```

### 路径管理策略

#### 绝对路径优先

在配置中存储绝对路径：

```json
{
  "paths": {
    "base_dir": "/root/project/outputs/batch-1/case-115-ABC-Company/",
    "work_papers": "/root/project/outputs/batch-1/case-115-ABC-Company/working_papers/",
    "final_reports": "/root/project/outputs/batch-1/case-115-ABC-Company/final_reports/",
    "calculations": "/root/project/outputs/batch-1/case-115-ABC-Company/calculations/"
  }
}
```

**Agent 使用示例**：

```python
# 读取配置
config = load_config(".processing_config.json")

# 使用绝对路径（避免相对路径错误）
output_path = config["paths"]["work_papers"] + config["file_templates"]["fact_check_report"].format(
    creditor_name="ABC-Company"
)

# 写入文件
save_report(output_path, report_content)

# 验证文件存在
assert os.path.exists(output_path), f"File not saved: {output_path}"
```

#### 相对路径仅用于显示

向用户展示时使用相对路径（更简洁）：

```
✅ User-facing message:
"Report saved to working_papers/ABC-Company_fact_check_report.md"

✅ Internal processing:
Full path: "/root/project/outputs/batch-1/case-115-ABC-Company/working_papers/ABC-Company_fact_check_report.md"
```

### 文件清单生成

#### 自动生成 Inventory

在 Stage 3（Report Formatter）完成后，自动生成文件清单：

```markdown
# File Inventory - Batch 1

Generated: 2025-10-26 14:30:00

## Case 115: ABC Company

### Working Papers
- [x] `working_papers/ABC-Company_fact_check_report.md` (15.2 KB)
- [x] `working_papers/ABC-Company_analysis_report.md` (22.8 KB)

### Calculations
- [x] `calculations/ABC-Company_interest_calculation.xlsx` (45.3 KB)
- [x] `calculations/ABC-Company_penalty_calculation.csv` (3.1 KB)

### Final Reports
- [x] `final_reports/PROJ2025_ABC-Company_Review_20251026.md` (28.5 KB)

**Total Files**: 5
**Total Size**: 114.9 KB
**Status**: Complete ✓

---

## Case 116: XYZ Corp
...
```

#### Inventory 用途

- 快速审查输出完整性
- 文件版本追踪
- 交付物打包依据
- 存档和备份参考

### 实施检查清单

- [ ] 设计标准目录结构（批次/案例/类型）
- [ ] 定义文件命名模板
- [ ] 配置文件包含所有路径和模板
- [ ] Agent 使用绝对路径写入文件
- [ ] 每个文件写入后验证存在性
- [ ] 自动生成文件清单
- [ ] 文档化目录结构和命名规范

---

## 设计模式 7: Quality Control Framework（质量控制框架模式）

### 核心思想

**多层检查点 + 零容忍项**：在工作流的关键节点设置质量检查，对严重错误实施零容忍政策。

### 检查点架构

#### 三层检查机制

```
Layer 1: Pre-Stage Checks (前置检查)
    ↓
Layer 2: In-Stage Validations (过程验证)
    ↓
Layer 3: Post-Stage Checkpoints (完成检查)
```

#### Layer 1: Pre-Stage Checks

每个 Agent 开始工作前：

```markdown
## Pre-Stage Checklist - Agent 1

**Environment Prerequisites**:
□ Configuration file exists (.processing_config.json)
□ Critical dates verified and consistent
□ Input materials available and accessible
□ Output directories exist and writable

**Knowledge Prerequisites**:
□ Relevant skill loaded (debt-fact-checking)
□ Core principles reviewed (就低, 就无, evidence hierarchy)
□ Report template accessible

**Conditional Prerequisites**:
□ If batch processing needed: Batch protocol reviewed
□ If special case type: Advanced legal standards loaded

**Action**: ✅ Proceed if all checked | ❌ STOP and request missing prerequisites
```

#### Layer 2: In-Stage Validations

处理过程中的实时验证：

```python
# 示例：计算器使用验证
def calculate_interest(principal, rate, start, end):
    # Validation: Must use calculator tool
    if using_manual_calculation():
        raise ValidationError(
            "❌ VALIDATION FAILED: Manual calculation prohibited!\n"
            "Must use: python universal_calculator_cli.py"
        )

    # Validation: Parameters must be complete
    if not all([principal, rate, start, end]):
        raise ValidationError("❌ Missing calculation parameters")

    # Execute tool
    result = run_calculator_tool(principal, rate, start, end)

    # Validation: Process file generated
    if not os.path.exists(result["process_file"]):
        raise ValidationError("❌ Calculator did not generate process file")

    return result
```

#### Layer 3: Post-Stage Checkpoints

每个 Agent 完成后，Main Controller 执行：

```markdown
## Post-Stage Checkpoint - Agent 2

**Output Verification**:
□ Analysis report exists at expected path
□ Report file size > 0 (not empty)
□ Calculation process files exist (Excel/CSV)
□ All calculation commands documented in report

**Content Quality**:
□ Report contains all required sections
□ Interest calculations reference calculator output
□ Statute analysis includes legal basis
□ Date consistency maintained from Agent 1

**Handover Readiness**:
□ Clear summary provided for next agent
□ Abnormal findings highlighted
□ All assumptions documented

**Action**: ✅ Proceed to Agent 3 | ❌ Return to Agent 2 for fixes
```

### Zero-Tolerance Items

#### 定义零容忍清单

在系统文档中明确列出：

```markdown
## ⚠️ ZERO-TOLERANCE QUALITY ITEMS

The following errors are NEVER acceptable and MUST stop processing:

1. **Date Errors**:
   - ❌ Wrong bankruptcy filing date
   - ❌ Inconsistent dates across reports
   - ❌ Missing date verification

2. **Calculation Errors**:
   - ❌ Manual calculations (not using tool)
   - ❌ Missing calculation process files
   - ❌ Undocumented calculation commands

3. **File Management Errors**:
   - ❌ Files saved to wrong directories
   - ❌ Incorrect file naming
   - ❌ Missing required output files

4. **Process Violations**:
   - ❌ Skipping required stages
   - ❌ Batch processing multiple cases simultaneously
   - ❌ Modifying previous stage's conclusions without justification

**Consequence**: Immediate stop + manual review required
```

#### 零容忍执行机制

```python
def enforce_zero_tolerance_check(agent_output):
    violations = []

    # Check 1: Date consistency
    if not verify_date_consistency(agent_output):
        violations.append("CRITICAL: Date inconsistency detected")

    # Check 2: Calculator usage
    if not verify_calculator_used(agent_output):
        violations.append("CRITICAL: Manual calculation detected")

    # Check 3: File organization
    if not verify_file_organization(agent_output):
        violations.append("CRITICAL: File organization violation")

    if violations:
        raise ZeroToleranceViolation(
            "⚠️ ZERO-TOLERANCE VIOLATIONS DETECTED:\n" +
            "\n".join(f"  - {v}" for v in violations) +
            "\n\nProcessing STOPPED. Manual intervention required."
        )
```

### Quality Documentation

#### 质量报告模板

每个案例处理完成后生成质量报告：

```markdown
# Quality Assurance Report - Case 115

**Case**: ABC Company
**Processing Date**: 2025-10-26
**Status**: ✅ PASSED ALL CHECKS

## Pre-Stage Checks
- [x] Environment initialized
- [x] Dates verified
- [x] Materials assessed

## Stage 1: Fact Checking
- [x] All pre-checks passed
- [x] Evidence classified correctly
- [x] Timeline created
- [x] Report saved correctly

## Stage 2: Analysis
- [x] Calculator tool used for all calculations
- [x] Process files generated: 2 files
- [x] Dates consistent with Stage 1
- [x] Report saved correctly

## Stage 3: Report Formatting
- [x] Template applied correctly
- [x] Technical conclusions preserved
- [x] File naming standards followed
- [x] File inventory generated

## Zero-Tolerance Check
✅ No violations detected

## Summary
**Total Checks**: 18
**Passed**: 18
**Failed**: 0
**Quality Score**: 100%
```

### 实施建议

1. **Checklist 嵌入 Agent 文档**：每个 Agent 定义包含详细 checklist
2. **自动化检查优先**：能自动化的检查（文件存在性、日期一致性）必须自动化
3. **人工审查保留**：复杂的内容质量需要人工采样审查
4. **记录所有检查**：生成质量报告供审计使用
5. **渐进式改进**：根据发现的常见错误扩充零容忍清单

---

## 设计模式 8: Configuration Management（配置管理模式）

### 核心思想

**分层配置 + 继承覆盖**：使用项目级和案例级配置，实现通用设置与特定设置的合理分离。

### 配置层次架构

```
Level 1: Project-Level Config (项目级配置)
    ↓ inherits
Level 2: Batch-Level Config (批次级配置, optional)
    ↓ inherits
Level 3: Case-Level Config (案例级配置)
```

#### Level 1: Project-Level Configuration

**文件**: `project_config.ini`

**用途**: 整个项目的通用设置

```ini
[project_info]
project_name = XYZ Bankruptcy Case
project_code = PROJ2025
client_name = XYZ Corporation
reviewer_name = John Doe

[critical_dates]
bankruptcy_filing_date = 2024-06-15
interest_stop_date = 2024-06-14
review_start_date = 2025-01-01

[paths]
input_base = /root/project/inputs/
output_base = /root/project/outputs/

[standards]
default_lpr_term = 1y
default_lpr_multiplier = 1.0
currency = CNY
```

#### Level 2: Batch-Level Configuration (Optional)

**文件**: `outputs/batch-1/batch_config.json`

**用途**: 某批次特定的设置（如不同的审查标准）

```json
{
  "batch_info": {
    "batch_number": "1",
    "batch_description": "First batch - financial institutions",
    "special_rules": ["financial_institution_standards"]
  },
  "review_standards": {
    "apply_stricter_evidence_rules": true,
    "require_legal_opinion": true
  }
}
```

#### Level 3: Case-Level Configuration

**文件**: `.processing_config.json` (案例目录下)

**用途**: 单个案例的特定配置，继承并覆盖上层配置

```json
{
  "case_info": {
    "batch": "1",
    "number": "115",
    "name": "ABC Company",
    "case_type": "financial_claim",
    "processing_date": "2025-10-26"
  },
  "critical_dates": {
    "bankruptcy_filing_date": "2024-06-15",     // Inherited from project
    "interest_stop_date": "2024-06-14"          // Inherited from project
  },
  "paths": {
    "base_dir": "/root/project/outputs/batch-1/case-115-ABC-Company/",
    "work_papers": "/root/project/outputs/batch-1/case-115-ABC-Company/working_papers/",
    "final_reports": "/root/project/outputs/batch-1/case-115-ABC-Company/final_reports/",
    "calculations": "/root/project/outputs/batch-1/case-115-ABC-Company/calculations/"
  },
  "file_templates": {
    "fact_check_report": "{name}_fact_check_report.md",
    "analysis_report": "{name}_analysis_report.md",
    "final_deliverable": "{project_code}_{name}_Review_{date}.md"
  },
  "case_specific_settings": {
    "requires_legal_document_verification": true,
    "complex_calculation_required": false
  }
}
```

### 配置加载策略

#### 继承和覆盖机制

```python
def load_complete_config(case_dir):
    """加载并合并多层配置"""

    # Level 1: Project config
    project_config = load_ini_config("project_config.ini")

    # Level 2: Batch config (if exists)
    batch_dir = os.path.dirname(case_dir)
    batch_config = {}
    if os.path.exists(f"{batch_dir}/batch_config.json"):
        batch_config = load_json_config(f"{batch_dir}/batch_config.json")

    # Level 3: Case config
    case_config = load_json_config(f"{case_dir}/.processing_config.json")

    # Merge with priority: Case > Batch > Project
    final_config = {}
    final_config.update(project_config)
    final_config.update(batch_config)
    final_config.update(case_config)

    return final_config
```

#### 配置验证

```python
def validate_config(config):
    """验证配置完整性和一致性"""

    # Required fields check
    required_fields = [
        "case_info.batch",
        "case_info.number",
        "case_info.name",
        "critical_dates.bankruptcy_filing_date",
        "critical_dates.interest_stop_date",
        "paths.base_dir",
        "paths.work_papers",
        "paths.final_reports"
    ]

    for field in required_fields:
        if not get_nested_value(config, field):
            raise ConfigValidationError(f"Missing required field: {field}")

    # Consistency check
    filing_date = parse_date(config["critical_dates"]["bankruptcy_filing_date"])
    stop_date = parse_date(config["critical_dates"]["interest_stop_date"])

    if stop_date != filing_date - timedelta(days=1):
        raise ConfigValidationError(
            f"Interest stop date must be bankruptcy filing date - 1 day\n"
            f"Filing: {filing_date}, Stop: {stop_date}"
        )

    # Path existence check
    for path_key in ["base_dir", "work_papers", "final_reports", "calculations"]:
        path = config["paths"][path_key]
        if not os.path.exists(path):
            raise ConfigValidationError(f"Path does not exist: {path}")
```

### 配置使用最佳实践

#### 1. 集中读取，全局使用

Agent 启动时一次性加载配置：

```python
class Agent:
    def __init__(self, case_dir):
        self.config = load_complete_config(case_dir)
        validate_config(self.config)

    def process(self):
        # Use config throughout processing
        output_path = self.config["paths"]["work_papers"] + \
                      self.config["file_templates"]["fact_check_report"]

        report = generate_report(self.config)
        save_report(output_path, report)
```

#### 2. 避免硬编码

❌ 错误做法：
```python
# 硬编码路径和文件名
output_file = "outputs/batch-1/case-115/working_papers/report.md"
```

✅ 正确做法：
```python
# 从配置读取
output_file = config["paths"]["work_papers"] + \
              config["file_templates"]["fact_check_report"].format(
                  name=config["case_info"]["name"]
              )
```

#### 3. 配置文档化

在 `CLAUDE.md` 或 `README.md` 中说明配置结构：

```markdown
## Configuration Files

### `project_config.ini`
Project-level settings shared across all cases.

**Critical sections**:
- `[critical_dates]`: Bankruptcy dates - MUST be set before processing
- `[project_info]`: Project metadata
- `[standards]`: Default calculation standards

**Must edit before starting**: YES

### `.processing_config.json`
Case-level settings, auto-generated by workflow controller.

**Generated by**: `python workflow_controller.py [batch] [number] [name]`

**Must edit manually**: NO (auto-generated)
```

### 实施检查清单

- [ ] 设计分层配置架构（项目/批次/案例）
- [ ] 定义必需和可选配置项
- [ ] 实现配置继承和覆盖逻辑
- [ ] 添加配置验证机制
- [ ] 文档化所有配置字段和用途
- [ ] 提供配置示例模板
- [ ] 在 Agent 中集中加载配置

---

## 综合应用示例：构建一个文档审查系统

假设需要构建一个合同审查系统，应用上述设计模式：

### 1. 技能架构（Skills Architecture）

```
.claude/
├── agents/
│   ├── contract-extractor.md
│   ├── clause-analyzer.md
│   └── compliance-checker.md
│
└── skills/
    ├── contract-extraction/
    │   ├── SKILL.md
    │   ├── templates/extraction_report.md
    │   └── references/
    │       ├── party_identification.md
    │       └── clause_classification.md
    │
    ├── legal-analysis/
    │   ├── SKILL.md
    │   └── references/
    │       ├── risk_assessment.md
    │       └── statute_reference.md
    │
    └── contract-foundations/
        ├── SKILL.md
        └── references/
            ├── contract_law_basics.md
            └── compliance_standards.md
```

### 2. 三智能体协作（Three-Agent Collaboration）

```
Contract Files → Extractor Agent → Analyzer Agent → Compliance Checker → Review Report
                      ↓                  ↓                    ↓
                  Extract parties    Assess risks       Check compliance
                  Identify clauses   Rate severity      Apply standards
                  Create timeline    Find conflicts     Generate summary
```

### 3. 零中断自动化（Zero-Interruption Automation）

**权限配置**：
```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": []
  }
}
```

**自动初始化**：
```python
# contract_workflow_controller.py
def auto_initialize_contract_review(contract_id):
    config_file = f"outputs/{contract_id}/.processing_config.json"

    if not file_exists(config_file):
        print("Initializing contract review environment...")
        create_directories(contract_id)
        generate_config(contract_id)
        print("✓ Environment ready")

    return load_config(config_file)
```

### 4. 强制工具使用（Mandatory Tool Usage）

**工具**：`contract_risk_scorer_cli.py`

**强制使用**：
```markdown
## ⚠️ MANDATORY: Risk Scoring Tool

ALL risk assessments MUST use: `python contract_risk_scorer_cli.py`

**Process**:
1. Extract contract clauses
2. Execute: `python contract_risk_scorer_cli.py --contract [file] --standard [type]`
3. Save generated risk matrix to calculations/
4. Document tool command in analysis report
```

### 5. 日期验证协议（Date Verification Protocol）

**关键日期**：
- Contract Effective Date
- Termination Date
- Review Date

**三重验证**：
1. Environment init: Load from project config
2. Extractor agent: Verify and document
3. Analyzer agent: Cross-verify with Extractor output

### 6. 文件组织（File Organization）

```
outputs/
└── batch-contracts-2025Q1/
    ├── contract-001-ABC-Agreement/
    │   ├── .processing_config.json
    │   ├── extraction/
    │   │   └── ABC-Agreement_extraction_report.md
    │   ├── analysis/
    │   │   └── ABC-Agreement_risk_analysis.md
    │   ├── compliance/
    │   │   └── ABC-Agreement_compliance_check.md
    │   └── final/
    │       └── ABC-Agreement_Final_Review_20251026.md
    └── file_inventory.md
```

### 7. 质量控制（Quality Control）

**Checkpoints**：
```markdown
Stage 1 Checkpoint (Extraction):
□ All parties identified
□ All clauses classified
□ Timeline created
□ Effective date verified

Stage 2 Checkpoint (Analysis):
□ Risk scorer tool used
□ Risk matrix generated
□ All high-risk items flagged
□ Dates consistent with Stage 1

Stage 3 Checkpoint (Compliance):
□ All standards checked
□ Template applied correctly
□ No modifications to analysis conclusions
□ File inventory generated
```

### 8. 配置管理（Configuration Management）

**project_config.ini**：
```ini
[project_info]
project_name = Contract Review 2025
compliance_standard = ISO-9001

[review_standards]
risk_threshold = high
require_legal_opinion = true
```

**.processing_config.json**：
```json
{
  "contract_info": {
    "id": "001",
    "name": "ABC Agreement",
    "type": "service_contract"
  },
  "critical_dates": {
    "effective_date": "2024-01-01",
    "termination_date": "2026-12-31",
    "review_date": "2025-10-26"
  },
  "paths": {
    "extraction": "/outputs/batch-contracts-2025Q1/contract-001-ABC-Agreement/extraction/",
    "analysis": "/outputs/batch-contracts-2025Q1/contract-001-ABC-Agreement/analysis/",
    "compliance": "/outputs/batch-contracts-2025Q1/contract-001-ABC-Agreement/compliance/",
    "final": "/outputs/batch-contracts-2025Q1/contract-001-ABC-Agreement/final/"
  }
}
```

---

## 实施路线图

### Phase 1: 架构设计（1-2 周）
- [ ] 识别业务流程和任务分解点
- [ ] 设计 Skills 架构（3-6 个 skills）
- [ ] 设计三智能体分工（或 2-5 个 agents）
- [ ] 定义配置文件结构
- [ ] 设计目录和文件命名规范

### Phase 2: 基础设施（1-2 周）
- [ ] 创建 `.claude/` 目录结构
- [ ] 编写 workflow controller 脚本
- [ ] 实现配置加载和验证逻辑
- [ ] 设置权限配置（`.claude/settings.local.json`）
- [ ] 开发必要的 CLI 工具

### Phase 3: Skills 开发（2-4 周）
- [ ] 编写 foundations skill（共享知识）
- [ ] 编写各专业 skills（每个 <500 lines）
- [ ] 创建 references/ 详细文档
- [ ] 准备 templates/ 输出模板
- [ ] 验证 YAML frontmatter

### Phase 4: Agents 开发（2-3 周）
- [ ] 编写 Agent 定义（orchestration）
- [ ] 嵌入 pre-stage checklists
- [ ] 实现 post-stage checkpoints
- [ ] 测试 Agent 间交接协议
- [ ] 验证 Skills 自动发现

### Phase 5: 质量体系（1-2 周）
- [ ] 定义零容忍清单
- [ ] 实现日期验证协议
- [ ] 开发质量检查脚本
- [ ] 创建质量报告模板
- [ ] 编写异常处理流程

### Phase 6: 文档和测试（1-2 周）
- [ ] 编写 CLAUDE.md（系统指南）
- [ ] 编写 README.md（用户指南）
- [ ] 准备测试案例
- [ ] 端到端测试
- [ ] 性能和准确性验证

**总时长估计**：8-15 周（根据复杂度调整）

---

## 关键成功因素

1. **清晰的分工边界**：每个 Agent 有明确的职责，不重叠不遗漏
2. **强制顺序处理**：绝不允许并行批量处理，确保状态一致性
3. **配置驱动**：所有路径、文件名、日期从配置读取，零硬编码
4. **完全自动化**：用户一次命令即可完成，无需人工干预
5. **质量为先**：零容忍清单严格执行，发现问题立即停止
6. **完整追溯**：所有计算和决策有完整过程文件和依据
7. **渐进式披露**：Skills 核心简洁，详细信息分层提供

---

## 常见陷阱与规避

### 陷阱 1: Agent 职责不清
**症状**：Agent 之间功能重复，或某些功能无人负责
**规避**：用动词明确定义每个 Agent 的核心动作（Extract, Analyze, Format）

### 陷阱 2: 批量处理导致混乱
**症状**：处理多个案例时状态混乱，输出文件错位
**规避**：强制顺序处理，Main Controller 严格控制流程

### 陷阱 3: 配置硬编码
**症状**：路径和文件名写死在代码中，难以维护
**规避**：一切从配置读取，使用模板化命名

### 陷阱 4: 忽略日期验证
**症状**：不同阶段使用不同日期，导致计算错误
**规避**：实施三重验证协议，stop-on-inconsistency

### 陷阱 5: 权限配置不足
**症状**：工作流运行到一半弹出权限请求
**规避**：预先授权所有必需命令（或使用 `"Bash"` 全授权）

### 陷阱 6: Skills 文件过大
**症状**：SKILL.md 超过 500 lines，加载慢
**规避**：核心内容保持简洁，详细信息放入 references/

### 陷阱 7: 质量检查流于形式
**症状**：有 checklist 但不执行
**规避**：自动化所有可自动化的检查，手动检查也要留痕

---

## 总结

本文档提炼了 8 个核心设计模式：

1. **Skills Architecture**：分离编排与知识，模块化可复用
2. **Three-Agent Collaboration**：专业化分工，强制顺序处理
3. **Zero-Interruption Automation**：完全预授权，透明初始化
4. **Mandatory Tool Usage**：零人工计算，完整审计追踪
5. **Date Verification Protocol**：三重验证，零容忍一致性
6. **File Organization Standards**：标准化目录，模板化命名
7. **Quality Control Framework**：多层检查点，零容忍清单
8. **Configuration Management**：分层配置，继承覆盖

这些模式共同构成了一个**企业级 AI 智能体协作系统**的完整架构，适用于需要高质量、可追溯、自动化的复杂工作流场景。

**核心理念**：
- **模块化**：知识和功能模块化，易维护易扩展
- **标准化**：流程、配置、输出全面标准化
- **自动化**：零人工干预，完全自动执行
- **质量为先**：多重验证，零容忍关键错误

---

**文档版本**: v1.0
**提炼自**: Debt Review Skills Project (Skills Architecture v2.0)
**最后更新**: 2025-10-26
**适用领域**: 文档审查、数据分析、合规检查、财务审核等需要多阶段协作的 AI 系统

---

**License**: 本设计模式参考文档基于实际项目经验提炼，可自由用于任何项目的架构设计参考。
