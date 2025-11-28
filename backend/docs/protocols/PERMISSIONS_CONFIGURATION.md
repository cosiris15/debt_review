# 权限配置说明文档

## 配置目的

本项目实现**持续运行的三智能体协同工作流**，要求：

1. **零中断运行**：用户发布命令后，主控智能体协调所有子智能体自动工作直到产出最终结果
2. **无需人工干预**：避免运行过程中弹出权限请求窗口打断进程
3. **完全自动化**：所有工具和命令权限在启动前预先授权

## 当前权限配置

**配置文件位置**：`.claude/settings.local.json`

**配置内容**：
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash"
    ],
    "deny": []
  }
}
```

## 配置解释

### 1. Bash 命令全授权

**配置项**：`"Bash"`（不带括号和参数）

**含义**：授权 Claude Code 执行**所有 Bash 命令**，无需逐一请求用户批准

**涵盖的命令类别**：
- **文件操作**：ls, cp, mv, rm, touch, chmod, chown, stat, file
- **目录操作**：mkdir, rmdir, cd, pwd
- **文本处理**：cat, head, tail, grep, sed, awk, cut, sort, uniq, wc, tr
- **文本编辑**：vi, vim, nano, echo, printf
- **查找搜索**：find, locate, which, whereis
- **压缩解压**：tar, zip, unzip, gzip, gunzip
- **Python 执行**：python, python3
- **包管理**：pip, pip3, apt, yum（如需要）
- **进程管理**：ps, top, kill, pkill
- **网络工具**：curl, wget（如需要）
- **Shell 控制结构**：for, while, do, done, if, then, fi, else, case, esac
- **项目专用脚本**：
  - `python 债权处理工作流控制器.py`
  - `python universal_debt_calculator_cli.py`
  - `python 环境初始化检查器.py`

### 2. 自动授权的其他工具

以下 Claude Code 核心工具**无需在 permissions 中配置**，默认可用：

- **Read**：读取任何文件
- **Write**：创建或覆盖文件
- **Edit**：精确修改文件内容
- **Glob**：文件模式匹配和查找
- **Grep**：代码内容搜索（基于 ripgrep）
- **Task**：调用子智能体（debt-fact-checker, debt-claim-analyzer, report-organizer）
- **TodoWrite**：任务列表管理
- **Skill**：技能模块调用

这些工具是 Claude Code 的核心能力，在项目工作目录范围内默认授权。

## 为什么选择全授权

### 三智能体工作流的需求

本项目的三智能体协同系统涉及复杂的文件操作和脚本执行：

```
债权处理流程：
┌─────────────────────────────────────────────────────────┐
│ 主控智能体 (Main Controller)                             │
│   ↓ 初始化环境 (python 债权处理工作流控制器.py)           │
├─────────────────────────────────────────────────────────┤
│ Agent 1: debt-fact-checker                              │
│   • 读取原始材料 (Read)                                   │
│   • 批量处理文档 (ls, find, wc)                          │
│   • 写入事实核查报告 (Write)                              │
│   • 文件验证 (cat, test, [ ])                           │
├─────────────────────────────────────────────────────────┤
│ Agent 2: debt-claim-analyzer                            │
│   • 读取核查报告 (Read)                                   │
│   • 运行计算器工具 (python universal_debt_calculator...)│
│   • 写入分析报告和计算文件 (Write, mv, cp)               │
│   • 日期计算 (date)                                       │
├─────────────────────────────────────────────────────────┤
│ Agent 3: report-organizer                               │
│   • 读取两份技术报告 (Read)                               │
│   • 整合和格式化 (sed, awk)                              │
│   • 写入最终报告 (Write)                                  │
│   • 文件组织 (mv, mkdir, cp)                            │
└─────────────────────────────────────────────────────────┘
```

**每个环节都需要多样化的 Bash 命令**，如果逐个配置：
- 需要预测并列出几十个命令模式
- 容易遗漏某个命令，导致流程中断
- 维护成本高，每次增加功能都要更新权限列表

**全授权的优势**：
1. **彻底消除中断**：无论使用什么命令，都不会弹出权限请求
2. **简化维护**：配置文件极简，一劳永逸
3. **提高灵活性**：支持未来功能扩展，无需修改权限

### 安全性考虑

**本地项目环境**：本项目运行在用户的本地文件系统，限定在项目目录内操作

**Claude Code 内置保护**：
- 默认工作目录限制在项目根目录
- 不会自动执行危险操作（如 `rm -rf /`）
- 所有文件操作都有日志记录
- 用户可以随时查看执行的命令和操作

**项目特性**：
- 债权审查是专业审计流程，不涉及系统级操作
- 所有操作限定在 `/root/debt_review_skills/` 及其子目录
- 输出文件都在 `输出/` 目录下，不影响系统文件

**结论**：对于本项目的使用场景，全授权 Bash 命令是安全且合理的选择。

## 如何修改配置（细粒度控制）

如果您需要更严格的权限控制，可以改为明确列出允许的命令：

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(python:*)",
      "Bash(python universal_debt_calculator_cli.py:*)",
      "Bash(python 债权处理工作流控制器.py:*)",
      "Bash(mkdir:*)",
      "Bash(mv:*)",
      "Bash(cp:*)",
      "Bash(rm:*)",
      "Bash(grep:*)",
      "Bash(find:*)",
      "Bash(wc:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(echo:*)",
      "Bash(date:*)",
      "Bash(test:*)"
    ],
    "deny": []
  }
}
```

**语法说明**：
- `Bash(command:*)` - 允许特定命令的所有参数
- `Bash(command arg)` - 仅允许特定命令和特定参数
- `Bash` - 允许所有 Bash 命令（当前配置）

## 验证配置有效性

运行以下命令验证权限配置是否正常工作：

```bash
# 验证配置文件语法
cat .claude/settings.local.json

# 测试基本命令
echo "权限测试成功"
ls -la

# 测试 Python 脚本
python --version

# 测试项目专用脚本（需要提供参数）
python 债权处理工作流控制器.py --help 2>/dev/null || echo "控制器脚本存在"
```

## 配置变更历史

| 日期 | 变更内容 | 原因 |
|------|----------|------|
| 2025-10-24 | 简化为 `"Bash"` 全授权 | 实现持续运行工作流，消除权限弹窗中断 |
| 之前 | 逐个列出 30+ 个命令模式 | 初始配置，覆盖已知的常用命令 |

## 相关文档

- **项目说明**：`CLAUDE.md` - 债权审查系统架构和工作流说明
- **配置文件**：`.claude/settings.local.json` - 实际权限配置
- **智能体定义**：`.claude/agents/*.md` - 三个智能体的详细说明
- **技能模块**：`.claude/skills/*/SKILL.md` - 各技能模块的知识库

## 常见问题

### Q1: 为什么不用 `Bash(*)`？
A: Claude Code 的权限语法要求使用不带括号的 `Bash` 表示全授权，`Bash(*)` 是无效语法。

### Q2: 是否需要授权 Read、Write、Edit 等工具？
A: 不需要。这些是 Claude Code 的核心文件操作工具，在项目目录范围内默认授权。

### Q3: 如何禁止某些危险命令？
A: 使用 `deny` 列表：
```json
{
  "permissions": {
    "allow": ["Bash"],
    "deny": [
      "Bash(rm -rf /:*)",
      "Bash(shutdown:*)",
      "Bash(reboot:*)"
    ]
  }
}
```

### Q4: 配置修改后需要重启吗？
A: 是的。修改 `.claude/settings.local.json` 后需要重启 Claude Code 会话以使配置生效。

### Q5: 子智能体的权限是否继承？
A: 是的。通过 Task 工具调用的子智能体（debt-fact-checker, debt-claim-analyzer, report-organizer）继承主控智能体的权限配置，无需额外配置。

---

**配置所有者**：Debt Review Skills 项目团队
**最后更新**：2025-10-24
**版本**：v2.0（持续运行架构）
