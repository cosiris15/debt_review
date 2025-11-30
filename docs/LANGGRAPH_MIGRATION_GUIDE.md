# Claude Code Agent 到 LangGraph 改造指南

## 文档信息

- **项目**: 债权审查系统 (Debt Review System)
- **改造时间**: 2024年11月
- **原方案**: Claude Code Agent (Skills架构)
- **目标方案**: LangGraph + Vercel 部署

---

## 目录

1. [改造概述](#改造概述)
2. [Phase 1: 基础架构搭建](#phase-1-基础架构搭建)
3. [Phase 2: 核心问题修复](#phase-2-核心问题修复)
4. [Phase 3: Prompt工程优化](#phase-3-prompt工程优化)
5. [关键技术差异对比](#关键技术差异对比)
6. [遇到的主要问题及解决方案](#遇到的主要问题及解决方案)
7. [待完成工作](#待完成工作)
8. [最佳实践总结](#最佳实践总结)

---

## 改造概述

### 改造目标

将基于 Claude Code Agent 的债权审查系统改造为 LangGraph 框架，以实现：
- 前后端分离部署（Vercel前端 + LangGraph后端）
- 标准化工作流管理
- 更好的可观测性和调试能力
- 支持并行处理和状态持久化

### 架构对比

```
【原方案: Claude Code Agent】
┌─────────────────────────────────────┐
│  Claude Code + Skills Architecture  │
│  ├── .claude/skills/ (知识库)       │
│  ├── .claude/agents/ (代理定义)     │
│  └── 直接文件系统访问               │
└─────────────────────────────────────┘

【目标方案: LangGraph】
┌─────────────────────────────────────┐
│  Frontend (Vercel/Next.js)          │
├─────────────────────────────────────┤
│  LangGraph Workflow                 │
│  ├── app/agents/workflow.py         │
│  ├── app/agents/nodes.py            │
│  ├── app/agents/llm.py              │
│  └── app/knowledge/ (知识库)        │
├─────────────────────────────────────┤
│  Supabase (状态持久化)              │
└─────────────────────────────────────┘
```

---

## Phase 1: 基础架构搭建

### 1.1 项目结构创建

```
debt_review/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── workflow.py      # LangGraph 工作流定义
│   │   ├── nodes.py         # 各阶段节点实现
│   │   ├── llm.py           # LLM调用和Prompt管理
│   │   ├── state.py         # 状态定义 (TypedDict)
│   │   ├── parallel.py      # 并行处理逻辑
│   │   ├── checkpoints.py   # 检查点管理
│   │   ├── templates.py     # 报告模板
│   │   └── material_reader.py  # 材料读取 (新增)
│   └── knowledge/           # 知识库文件
│       ├── fact_check_knowledge.md
│       ├── analysis_knowledge.md
│       └── report_knowledge.md
├── langgraph.json           # LangGraph配置
├── pyproject.toml           # 依赖管理
└── outputs/                 # 输出目录
```

### 1.2 状态定义 (state.py)

**关键设计决策**：
- 使用 `TypedDict` 定义状态类型
- 分离 `InputState`（用户输入）和 `WorkflowState`（内部状态）
- 支持多债权人批量处理

```python
class InputState(TypedDict):
    """用户提供的输入"""
    debtor_name: str
    bankruptcy_date: str
    creditors: List[CreditorInput]

class WorkflowState(TypedDict):
    """完整的内部状态"""
    # 基本信息
    debtor_name: str
    bankruptcy_date: str
    interest_stop_date: str

    # 进度追踪
    current_stage: WorkflowStage
    current_creditor_index: int
    total_creditors: int
    completed_creditors: int

    # 债权人列表
    creditors: List[CreditorState]

    # 报告内容 (存储在creditors[i]中)
    # fact_check_report, analysis_report, final_report
```

### 1.3 工作流定义 (workflow.py)

**工作流结构**：
```
[init] → [fact_check] → [analysis] → [report] → [validation]
                                                      │
                                                      ▼
                                             [route_after_validation]
                                                  /        \
                                                 ▼          ▼
                                        [next_creditor]  [complete]
                                                 │
                                                 ▼
                                            [init] (loop)
```

**关键代码**：
```python
def build_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState, input=InputState)

    # 添加节点
    workflow.add_node("init", init_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("report", report_node)
    workflow.add_node("validation", validation_node)

    # 线性流程
    workflow.add_edge("init", "fact_check")
    workflow.add_edge("fact_check", "analysis")
    workflow.add_edge("analysis", "report")
    workflow.add_edge("report", "validation")

    # 条件路由
    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {"next_creditor": "next_creditor", "complete": "complete"}
    )

    workflow.set_entry_point("init")
    return workflow
```

---

## Phase 2: 核心问题修复

### 2.1 问题：LLM无法读取材料文件

**症状**：
- LLM生成的报告包含虚构数据（假合同号、假金额）
- 报告长度极短（约1,600字符 vs 原方案16,000+字符）

**根因分析**：
```
【原方案 Claude Code Agent】
- Claude Code 有直接文件系统访问权限
- LLM 可以直接读取 materials_path 指向的文件

【LangGraph 方案】
- LLM 只收到 materials_path 字符串
- LLM 无法访问文件系统
- 导致 LLM 只能"虚构"内容
```

**解决方案**：创建 `material_reader.py` 模块

```python
# app/agents/material_reader.py

from pathlib import Path
from typing import Tuple, Dict, Any

MAX_CONTENT_LENGTH = 30000  # Token预算

async def read_materials(materials_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    读取材料文件内容，返回文本和元数据。

    支持：
    - 单个文件读取
    - 目录批量读取
    - UTF-8 和 GBK 编码
    - 内容截断（超过token预算时）
    """
    path = Path(materials_path)

    if not path.exists():
        return f"材料路径不存在: {materials_path}", {"error": True}

    if path.is_file():
        return await _read_single_file(path)
    elif path.is_dir():
        return await _read_directory(path)

async def _read_single_file(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """读取单个文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = file_path.read_text(encoding='gbk')

    # 截断过长内容
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "\n\n[内容已截断...]"

    return content, {"total_chars": len(content)}
```

**节点中的调用**（nodes.py）：

```python
async def fact_check_node(state: WorkflowState) -> WorkflowState:
    creditor = state["creditors"][state["current_creditor_index"]]
    materials_path = creditor["materials_path"]

    # ===== 关键修复：读取材料内容 =====
    materials_content, materials_meta = await read_materials(materials_path)

    # 将内容传递给Prompt
    prompt = await create_fact_check_prompt_async(
        creditor_name=creditor["creditor_name"],
        materials_path=materials_path,
        bankruptcy_date=state["bankruptcy_date"],
        debtor_name=state["debtor_name"],
        materials_content=materials_content,  # 传入实际内容！
    )
```

### 2.2 问题：知识库未正确加载

**症状**：
- LLM 未遵循专业债权审查规范
- 报告格式不符合模板要求

**根因分析**：
```
【原方案】
- Skills 架构自动发现并加载 .claude/skills/ 目录
- SKILL.md 文件包含500+行详细指导

【LangGraph方案】
- 需要显式读取知识文件
- 需要将知识内容嵌入到 System Prompt 中
```

**解决方案**：动态知识加载

```python
# app/agents/llm.py

# 知识文件路径
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

async def get_fact_check_system(bankruptcy_date: str) -> str:
    """动态加载事实核查知识"""
    knowledge_file = KNOWLEDGE_DIR / "fact_check_knowledge.md"

    if knowledge_file.exists():
        knowledge = knowledge_file.read_text()
    else:
        knowledge = ""  # 降级到默认

    return f"""你是专业的债权事实核查员。

项目关键日期：
- 破产受理日期：{bankruptcy_date}
- 停止计息日期：{bankruptcy_date}的前一日

{knowledge}
"""
```

---

## Phase 3: Prompt工程优化

### 3.1 问题：报告质量远低于原方案

**症状对比**：
| 指标 | 原方案 | 初始LangGraph | 差距 |
|------|--------|---------------|------|
| 事实核查报告长度 | 16,758字符 | 1,659字符 | 10% |
| 债权分析报告 | 完整8章结构 | 简单6点 | 结构不完整 |
| 文件核查表 | 12项详细表格 | 无 | 缺失 |

**根因分析**：
```
【原方案 SKILL.md】
- 500+ 行详细指导
- 完整的输出格式模板
- 禁止事项清单
- 示例和边界情况

【初始LangGraph Prompt】
- ~50 行简单指令
- 缺少格式模板
- 缺少禁止事项
```

### 3.2 解决方案：增强Prompt

**事实核查Prompt增强**（从~50行增至~200行）：

```python
human = f"""请对以下债权申报材料进行事实核查：

债权人名称：{creditor_name}
破产受理日期：{bankruptcy_date}
...

# 材料内容
{materials_content}

# 报告输出格式（必须严格遵循）

## 一、申报情况
### 1.1 债权人基本信息
（详细格式要求...）

## 二、形式性文件核查
| 文件类型 | 齐 | 缺 | 无需 | 备注 |
|---------|----|----|------|------|
| 债权申报材料目录 | | | | |
| 债权申报表 | | | | |
（完整12项表格...）

## 三、债权发生情况查明
（时间线表格格式...）

## 四、判决/调解书摘录
（逐字摘录要求...）

## 五、证据关系分析
（分析框架...）

## 六、向分析员移交说明
### 重点提示：
1. **法律文书效力**：...
2. **债权金额确定**：...
...
10. **债权确认建议的初步判断**：...
"""
```

**债权分析Prompt增强**（从~30行增至~170行）：

```python
human = f"""请对以下债权进行详细分析：
...

# ⚠️ 关键原则

## 就低原则
当计算结果 > 债权人申报金额时，以申报金额为准确认

## 就无原则
债权人未申报的项目，即使证据支持也不予确认

## Calculator 工具强制使用
所有利息/违约金计算必须使用 Calculator 工具

# 报告输出格式（必须严格遵循8章结构）

## 一、债权基础法律关系确认
## 二、金额项目拆解分析
## 三、履行期限判断
## 四、利息计算过程
### 4.2 利息计算标记（系统将自动识别并计算）
【利息计算】本金: [金额], 起始日: YYYY-MM-DD, 类型: [lpr/simple/delay]
## 五、诉讼时效分析
## 六、执行时效分析
## 七、审查确认情况
## 八、审查结论

# ⚠️ 禁止事项
1. **禁止手工计算**
2. **禁止推测参数**
3. **禁止估算**
4. **禁止添加未申报项**
5. **禁止虚构数据**
"""
```

### 3.3 增强效果

| 指标 | 增强前 | 增强后 | 提升 |
|------|--------|--------|------|
| 事实核查报告 | 1,659字符 | 5,111字符 | 3.1x |
| 债权分析报告 | ~1,500字符 | 3,584字符 | 2.4x |
| 文件核查表 | 无 | 完整12项 | ✓ |
| 利息计算标记 | 无 | 自动识别 | ✓ |

---

## 关键技术差异对比

### 工作流控制方法

| 方面 | Claude Code Agent | LangGraph |
|------|-------------------|-----------|
| 流程定义 | 隐式（Agent自主决策） | 显式（StateGraph定义） |
| 阶段切换 | Agent判断 | 边(Edge)和条件路由 |
| 并行处理 | Task工具并发 | `run_parallel_batch()` |
| 状态管理 | 会话上下文 | TypedDict + Checkpointer |
| 错误处理 | Agent自处理 | 专用error_handler_node |

### 知识库维护

| 方面 | Claude Code Agent | LangGraph |
|------|-------------------|-----------|
| 知识位置 | `.claude/skills/SKILL.md` | `app/knowledge/*.md` |
| 加载方式 | 自动发现 | 显式读取 |
| 模板文件 | `templates/` 目录 | 嵌入Prompt或单独文件 |
| 更新方式 | 直接编辑文件 | 编辑后需重启服务 |

### LLM调用

| 方面 | Claude Code Agent | LangGraph |
|------|-------------------|-----------|
| API调用 | 内置 | langchain-anthropic |
| 文件读取 | 直接访问 | 需预读取传入Prompt |
| 工具调用 | 内置工具 | 需单独实现或集成 |
| 上下文 | 自动管理 | 显式状态传递 |

---

## 遇到的主要问题及解决方案

### 问题1：LLM虚构数据

**错误现象**：
```
# LLM生成的报告
合同编号：MC2023031501（虚构）
合同金额：800,000元（虚构）
```

**根本原因**：
LLM只收到文件路径字符串，无法访问实际文件内容。

**解决方案**：
创建 `material_reader.py`，在节点中预读取材料内容，传入Prompt。

**修复代码**：
```python
# nodes.py
materials_content, _ = await read_materials(materials_path)
prompt = await create_fact_check_prompt_async(
    ...,
    materials_content=materials_content,  # 关键！
)
```

---

### 问题2：报告格式不符合规范

**错误现象**：
```
# 简陋的报告结构
一、债权金额分解
（简单几行描述）

二、利息计算验证
（缺少详细格式）
```

**根本原因**：
Prompt缺少详细的输出格式模板。

**解决方案**：
将原方案SKILL.md中的模板要求嵌入Prompt。

**关键增强**：
- 添加12项文件核查表模板
- 添加8章节完整结构
- 添加利息计算标记格式
- 添加禁止事项清单

---

### 问题3：知识库未生效

**错误现象**：
- LLM不知道"就低原则"、"就无原则"
- 不知道如何计算迟延履行利息

**根本原因**：
知识文件存在但未被加载到System Prompt。

**解决方案**：
```python
async def get_analysis_system(bankruptcy_date: str) -> str:
    knowledge_file = KNOWLEDGE_DIR / "analysis_knowledge.md"
    if knowledge_file.exists():
        knowledge = knowledge_file.read_text()
    return f"你是专业债权分析员...\n\n{knowledge}"
```

---

### 问题4：利息计算集成

**挑战**：
原方案LLM可以直接调用Calculator CLI工具，LangGraph中如何实现？

**解决方案**：
1. LLM输出特殊标记格式
2. 后处理步骤解析标记并执行计算
3. 将计算结果附加到报告

```python
# LLM输出格式
【利息计算】本金: 7610000, 起始日: 2023-04-25, 类型: lpr, 倍数: 1.5

# 后处理解析
def process_interest_calculations(report: str) -> str:
    pattern = r'【利息计算】本金: (\d+), 起始日: ([\d-]+), 类型: (\w+)'
    matches = re.findall(pattern, report)

    results = []
    for principal, start_date, calc_type in matches:
        result = calculate_interest(principal, start_date, calc_type)
        results.append(result)

    return report + "\n\n=== 利息计算结果 ===\n" + format_results(results)
```

---

### 问题5：测试时模块导入失败

**错误现象**：
```
ModuleNotFoundError: No module named 'app.agents.graph'
```

**根本原因**：
- 工作目录不正确
- Python路径未包含项目根目录

**解决方案**：
```python
import sys
sys.path.insert(0, '/path/to/debt_review')

# 或在测试脚本开头
import os
os.chdir('/path/to/debt_review')
```

---

### 问题6：后台进程积累

**现象**：
多次测试后有大量langgraph dev后台进程。

**解决方案**：
```bash
pkill -f "langgraph dev"
```

---

## 待完成工作

### 高优先级

1. **报告阶段Prompt增强**
   - 当前report_node的Prompt尚未优化
   - 需要添加最终报告模板格式

2. **利息计算器完整集成**
   - 实现完整的Calculator工具调用
   - 支持所有计算类型（lpr, simple, delay, compound, penalty）

3. **知识库完整迁移**
   - 将所有SKILL.md内容迁移到app/knowledge/
   - 确保法律标准、计算公式等完整

### 中优先级

4. **Supabase集成测试**
   - 验证检查点持久化
   - 验证任务状态同步

5. **并行处理优化**
   - 测试多债权人并行处理
   - 优化并行批次大小

6. **前端集成**
   - Vercel部署配置
   - API端点测试

### 低优先级

7. **日志和监控**
   - 添加结构化日志
   - 添加性能指标收集

8. **错误恢复机制**
   - 实现从检查点恢复
   - 添加重试逻辑

---

## 最佳实践总结

### 1. 材料处理

```
✅ 正确做法：
- 在节点中预读取材料文件
- 将内容作为参数传入Prompt生成函数
- 处理编码问题（UTF-8, GBK）
- 设置内容长度上限避免超token

❌ 错误做法：
- 只传递文件路径给LLM
- 假设LLM能访问文件系统
```

### 2. Prompt工程

```
✅ 正确做法：
- 提供完整的输出格式模板
- 包含禁止事项清单
- 使用示例说明预期输出
- 定义特殊标记格式（如利息计算）

❌ 错误做法：
- 只给简单的任务描述
- 假设LLM知道领域规范
- 输出格式模糊不清
```

### 3. 知识库管理

```
✅ 正确做法：
- 显式读取知识文件
- 嵌入到System Prompt
- 版本化管理知识文件
- 提供降级默认值

❌ 错误做法：
- 假设自动发现
- 硬编码知识内容
- 不处理文件不存在情况
```

### 4. 状态设计

```
✅ 正确做法：
- 使用TypedDict定义明确类型
- 分离Input/Internal/Output状态
- 在状态中保存中间报告
- 设计支持多债权人

❌ 错误做法：
- 使用普通dict
- 状态字段含义模糊
- 中间结果不保存
```

### 5. 测试策略

```
✅ 正确做法：
- 分层测试（Prompt → 节点 → 工作流）
- 使用真实材料测试
- 对比原方案输出质量
- 保存测试结果便于对比

❌ 错误做法：
- 只做端到端测试
- 使用虚构测试数据
- 不量化质量指标
```

---

## 附录

### A. 关键文件修改清单

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `app/agents/material_reader.py` | 新增 | 材料文件读取模块 |
| `app/agents/llm.py` | 修改 | 增强Prompt，添加知识加载 |
| `app/agents/nodes.py` | 修改 | 添加材料读取调用 |
| `app/knowledge/*.md` | 新增 | 知识库文件 |

### B. 测试命令

```bash
# 测试Prompt生成
python -c "
from app.agents.llm import create_fact_check_prompt_async
import asyncio
prompt = asyncio.run(create_fact_check_prompt_async(...))
print(len(prompt[1].content))
"

# 运行完整工作流测试
python -c "
from app.agents.workflow import get_workflow_app
from app.agents.state import create_initial_state
import asyncio

async def test():
    app = get_workflow_app()
    state = create_initial_state(...)
    result = await app.ainvoke(state, config)
    print(result)

asyncio.run(test())
"

# 清理后台进程
pkill -f 'langgraph dev'
```

### C. 参考资源

- LangGraph文档: https://langchain-ai.github.io/langgraph/
- 原方案Skills架构: `backend/.claude/skills/`
- 原方案SKILL.md模板: `backend/.claude/skills/debt-fact-checking/SKILL.md`

---

**文档版本**: v1.0
**最后更新**: 2024-11-30
**作者**: Claude Code 协助生成
