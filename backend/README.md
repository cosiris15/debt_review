# 债权审查系统 - Skills Architecture v2.0

基于Claude Code Skills架构的智能债权审查系统，用于破产程序中的债权申报审查和分析。

## 系统架构

**架构版本**: Skills Architecture v2.0
**迁移日期**: 2025-10-23
**核心模式**: 三Agent协作 + 五Skills知识库

## 快速开始

### 1. 项目配置

编辑 `project_config.ini` 设置破产受理日期等项目信息：

```ini
[项目基本信息]
债务人名称 = [公司名称]
项目代码 = GY2025

[关键日期]
破产受理日期 = YYYY-MM-DD
停止计息日期 = YYYY-MM-DD
```

### 2. 环境初始化（必须）

处理每个债权人前，必须执行：

```bash
python 债权处理工作流控制器.py <批次号> <债权人编号> <债权人名称>
```

### 3. 三阶段处理流程

```
Stage 1: debt-fact-checker    → 事实核查报告
Stage 2: debt-claim-analyzer  → 债权分析报告 + 计算文件
Stage 3: report-organizer     → 审查意见表 + 文件清单
```

## 并行处理模式（高级）

**版本**: v2.1 | **新增日期**: 2025-10-26

### 概述

系统支持**阶段内并行处理**，可同时处理多个债权人，大幅提升效率：

```
✅ 允许：阶段内并行（同一阶段，多个债权人同时处理）
❌ 禁止：跨阶段并行（同一债权人，多个阶段同时处理）
```

### 性能提升

| 债权人数量 | 串行耗时 | 并行耗时 | 效率提升 |
|-----------|---------|---------|---------|
| 3个       | 48分钟   | 20分钟   | 58%     |
| 5个       | 80分钟   | 18分钟   | 78%     |
| 10个      | 160分钟  | 30分钟   | 81%     |

### 适用场景

**建议使用并行**:
- 债权人数量 ≥ 3
- 同一批次多个债权人
- 债权结构相似

**建议使用串行**:
- 债权人数量 = 1-2（无效率提升）
- 债权结构极其复杂
- 首次使用系统（建议先熟悉流程）

### 快速工作流

**阶段0: 批量初始化**（串行）
```bash
for creditor in [list]; do
  python 债权处理工作流控制器.py [batch] [number] [name]
done
```

**阶段1-3: 并行执行**
1. 使用 `parallel_prompt_generator.py` 生成所有prompt
2. 在一个消息中发起所有Task调用
3. 等待全部完成
4. 执行质量检查点（使用 `PARALLEL_QUALITY_CHECKLIST.md`）
5. 全部通过后进入下一阶段

### 防污染机制

**三层验证**确保零上下文污染：
- 第一层：启动时验证债权人身份
- 第二层：文件操作前验证路径
- 第三层：完成时验证输出一致性

**自包含Prompt**：每个债权人的prompt完全独立，包含所有必需信息

### 核心文档

- **快速参考**: `PARALLEL_QUICK_REFERENCE.md`（推荐打印）
- **用户手册**: `PARALLEL_PROCESSING_USER_GUIDE.md`
- **技术协议**: `PARALLEL_PROCESSING_PROTOCOL.md`
- **质量检查**: `PARALLEL_QUALITY_CHECKLIST.md`
- **标准流程**: `PARALLEL_PROCESSING_SOP.md`

### 辅助工具

**Prompt生成器**（强烈推荐）:
```bash
python parallel_prompt_generator.py --stage 1 --batch 1 --creditors 115,118,124
```

### 质量保证

**零容忍**:
- ❌ 上下文污染（债权人信息混淆）
- ❌ 日期不一致
- ❌ 文件路径错误
- ❌ 跳过质量检查点

**强制检查**:
- ✓ 每阶段完成后执行质量检查
- ✓ 100%文件存在性验证
- ✓ 独立性抽查（无交叉引用）
- ✓ 日期全局一致性验证

### 快速上手

1. 阅读 `PARALLEL_QUICK_REFERENCE.md`（2分钟）
2. 执行批量初始化
3. 使用prompt生成器生成Stage 1 prompts
4. 向Claude Code发送并行处理请求
5. 完成后执行Checkpoint 1质量检查
6. 重复步骤3-5完成Stage 2和Stage 3

**详细操作指南**: 参考 `PARALLEL_PROCESSING_USER_GUIDE.md`

## 核心组件

### Skills（知识库）

```
.claude/skills/
├── debt-fact-checking/          事实核查工作流程
├── debt-claim-analysis/         债权分析和计算标准
├── report-organization/         报告整合和格式化
├── debt-review-foundations/     共享基础知识
└── debt-review-legal-standards/ 高级法律参考（复杂案件专用）
```

### Agents（编排器）

```
.claude/agents/
├── debt-fact-checker.md    事实核查员（Stage 1）
├── debt-claim-analyzer.md  债权分析员（Stage 2）
└── report-organizer.md     报告整理员（Stage 3）
```

### 工具脚本

- `universal_debt_calculator_cli.py` - 利息计算器（必须使用）
- `债权处理工作流控制器.py` - 环境初始化脚本
- `环境初始化检查器.py` - 环境验证工具
- `parallel_prompt_generator.py` - 并行处理Prompt生成器（v2.1新增）

## 核心原则

- **就低原则**: 计算>申报时，确认申报金额
- **就无原则**: 仅确认债权人申报的项目
- **证据层级**: 法律文书 > 双方确认 > 合同 > 单方证据
- **日期验证**: 破产受理日期是"生命线级别"关键

## 目录结构

```
/root/debt_review_skills/
├── .claude/                    Claude配置
│   ├── agents/                 三个Agent定义
│   └── skills/                 五个Skills知识库
├── 输入/                       原始债权材料
├── 输出/                       处理结果输出
├── 归档文件/                   历史版本备份
├── project_config.ini          项目配置
├── universal_debt_calculator_cli.py  计算工具
├── 债权处理工作流控制器.py      环境初始化
└── 环境初始化检查器.py          环境验证
```

## 文档

### 📚 完整文档导航
**[→ 查看完整文档索引 (docs/INDEX.md)](docs/INDEX.md)** ⭐ 推荐

文档已按类型组织，包括：
- **用户指南**: 操作手册、快速入门
- **最佳实践**: 大文档处理优化、模板化报告撰写
- **实施记录**: 防编造系统、多轮系统技术设计
- **开发指南**: 项目结构、设计模式
- **操作协议**: 并行处理、权限配置
- **历史记录**: 架构迁移、改进总结

### 核心文档（根目录）
- **CLAUDE.md** - 系统主控制文档（Claude Code必读）
- **README.md** - 项目说明（本文件）

### 并行处理文档
详见 `docs/protocols/` 目录：
- **PARALLEL_PROCESSING_PROTOCOL.md** - 技术协议规范
- **PARALLEL_QUALITY_CHECKLIST.md** - 质量检查清单

## 质量标准

### 零容忍错误

❌ 破产日期错误
❌ 手工计算（必须用工具）
❌ 文件位置错误
❌ 缺少计算过程文件
❌ 报告间日期不一致

### 强制性检查点

每个阶段完成后验证：
- ✓ 文件在正确目录
- ✓ 文件命名符合规范
- ✓ 破产日期一致
- ✓ 所有计算使用工具

## 计算器工具使用

```bash
# 简单利息
python universal_debt_calculator_cli.py simple \
  --principal 100000 --start-date 2024-01-01 \
  --end-date 2024-12-31 --rate 4.35

# LPR浮动利率
python universal_debt_calculator_cli.py lpr \
  --principal 100000 --start-date 2024-01-01 \
  --end-date 2024-12-31 --multiplier 1.5 --lpr-term 1y

# 迟延履行利息
python universal_debt_calculator_cli.py delay \
  --principal 100000 --start-date 2024-01-01 \
  --end-date 2024-12-31
```

## 技术特性

**模块化**: 每个Skill专注特定知识域
**自动发现**: Skills根据上下文自动加载
**可维护**: 在一处更新知识，全体受益
**可追溯**: 完整审计追踪和计算过程
**零损失**: 100%业务逻辑保留

## 版本历史

- **v2.1.1** (2025-10-27): 架构优化 - 工作流编排迁移
  - 将debt-workflow-orchestration从Skill迁移至CLAUDE.md
  - Skills数量：6个 → 5个（控制逻辑与领域知识分离）
  - 新增CONTENT_CLASSIFICATION_GUIDE.md通用指南
  - 强化持续运行原则和权限配置规范
  - 提升系统可靠性（强制执行 vs 自主激活）

- **v2.1** (2025-10-26): 并行处理能力集成
  - 阶段内并行处理模式（Stage-Level Parallelism）
  - 三层验证防污染机制
  - 5个并行处理文档 + 3个Prompt模板
  - parallel_prompt_generator.py工具
  - 效率提升75-80%（5个债权人：80min → 18min）

- **v2.0.1** (2025-10-23): 集成高级法律标准
  - 6个模块化Skills（新增debt-review-legal-standards）
  - 34个知识文件
  - 顶级律所债权审查标准融入

- **v2.0** (2025-10-23): Skills架构迁移完成
  - 5个模块化Skills
  - 23个知识文件
  - 完整备份保障

- **v1.0**: 传统Agent模式（已归档）

## 支持与维护

**备份位置**: `归档文件/v1_改造前完整备份_20251023/`
**回滚程序**: 已验证可用
**问题反馈**: 参考 VALIDATION_TEST_REPORT.md

## License

内部使用系统 - 版权所有

---

**系统状态**: ✅ 生产就绪
**当前版本**: v2.1 (并行处理支持)
**最后更新**: 2025-10-26
