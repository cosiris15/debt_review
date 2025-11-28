# 📚 债权审查系统文档导航

> **快速查找**: 按 Ctrl+F 搜索关键词

**最后更新**: 2025-11-13

---

## 🎯 快速入口

| 我想... | 推荐文档 |
|---------|----------|
| **快速开始使用系统** | [多轮系统快速入门指南](user-guides/multi-round-system/快速入门指南.md) |
| **学习大文档处理优化** | [大文档处理优化经验](best-practices/大文档处理优化经验.md) |
| **了解格式控制方法** | [模板化报告撰写实践](best-practices/模板化报告撰写实践.md) |
| **理解系统架构** | [项目结构说明](guides/PROJECT_STRUCTURE.md) |
| **配置并行处理** | [并行处理协议](protocols/PARALLEL_PROCESSING_PROTOCOL.md) |

---

## 📖 文档分类索引

### 1️⃣ 用户指南 (User Guides)

**面向使用者的操作手册和快速入门**

#### 多轮债权审查系统
- **[用户操作手册](user-guides/multi-round-system/用户操作手册.md)** ⭐ 推荐
  - 完整的操作手册（42KB）
  - 系统概述、快速开始、CLI命令参考
  - 功能详解、最佳实践、故障排除

- **[快速入门指南](user-guides/multi-round-system/快速入门指南.md)**
  - 简化版入门指南（24KB）
  - 三层架构设计、核心组件说明
  - 前提条件验证、快速上手步骤

---

### 2️⃣ 最佳实践 (Best Practices)

**跨项目可复用的技术优化经验**

- **[大文档处理优化经验](best-practices/大文档处理优化经验.md)** ⭐ 核心
  - **适用场景**: LLM Agent处理超长文档/大规模材料集
  - **核心价值**: 技术优化 + 业务逻辑 = 智能化处理
  - **三层优化框架**:
    - 第一层：强制完整性（解决二次调用问题）
    - 第二层：文档分段策略（支持150KB+文档）
    - 第三层：业务分批策略（多文档场景优化）
  - **包含**: 代码模板库、项目适配指南、快速决策参考

- **[模板化报告撰写实践](best-practices/模板化报告撰写实践.md)** ⭐ 核心
  - **核心问题**: AI Agent生成Markdown格式导致交付物不符合正式文档要求
  - **三重保障机制**:
    - 事前约束：明确禁止Markdown语法
    - 过程控制：提供纯文本格式模板
    - 事后验证：自动化格式检查（零容忍）
  - **实战成果**: 第6批债权100%格式合规率（6/6）
  - **包含**: Agent指令模板、验证脚本模板、常见问题速查

---

### 3️⃣ 实施记录 (Implementation Records)

**历史实施总结和技术设计文档（存档性质）**

- **[防编造系统实施总结](implementation-records/防编造系统实施总结.md)** (49KB)
  - **实施日期**: 2025-11-06
  - **核心原则**: "事实绝对真实，法律可以推理，推理必须标注依据"
  - **四层防护体系**: Agent层 + Skill层 + Template层 + System层
  - **成果**: 3阶段完成，10任务执行，15文件修改
  - **包含**: 紧急修复、深度加固、系统强化的完整实施过程

- **[多轮系统技术设计文档](implementation-records/多轮系统技术设计文档.md)** (23KB)
  - **版本**: v1.0
  - **状态**: 开发中
  - **包含**:
    - 轮次隔离目录结构设计
    - 元数据文件格式定义
    - 向后兼容的迁移路径
    - 技术架构说明

---

### 4️⃣ 开发指南 (Developer Guides)

**面向开发者的设计模式和项目结构说明**

- **[项目结构说明](guides/PROJECT_STRUCTURE.md)**
  - 目录组织原则
  - 文件命名规范
  - 模块职责划分

- **[内容分类指南](guides/CONTENT_CLASSIFICATION_GUIDE.md)**
  - 证据材料分类标准
  - 法律关系类型识别
  - 内容提取规则

- **[可复用设计模式](guides/REUSABLE_DESIGN_PATTERNS.md)**
  - Agent协作模式
  - Skills架构模式
  - 三阶段工作流模式

---

### 5️⃣ 操作协议 (Protocols)

**标准化操作流程和配置规范**

- **[并行处理协议](protocols/PARALLEL_PROCESSING_PROTOCOL.md)**
  - 自动模式选择（串行 vs 并行）
  - Stage-Level并行执行规范
  - 质量检查点（Checkpoint）
  - 上下文隔离要求

- **[并行质量检查清单](protocols/PARALLEL_QUALITY_CHECKLIST.md)**
  - 批量处理前置条件
  - 并行执行验证项
  - 批量质量检查标准

- **[权限配置说明](protocols/PERMISSIONS_CONFIGURATION.md)**
  - 无中断工作流的权限设计
  - `.claude/settings.local.json` 配置
  - 安全性和审计追踪

---

### 6️⃣ 历史记录 (History)

**系统演进历史和重要改进记录**

- **[Skills架构迁移记录](history/MIGRATION_TO_SKILLS_V2.md)**
  - 从传统Agent模式到Skills架构的迁移
  - 迁移日期：2025-10-23
  - 完整备份位置

- **[阶段1改进总结](history/PHASE1_IMPROVEMENT_SUMMARY.md)**
  - 初期系统建设成果

- **[系统改进完成报告](history/SYSTEM_IMPROVEMENTS_COMPLETED_20251028.md)**
  - 2025-10-28前完成的系统改进汇总

- **[验证测试报告](history/VALIDATION_TEST_REPORT.md)**
  - 系统功能验证测试结果

---

## 🔍 按主题索引

### 技术优化类
- [大文档处理优化经验](best-practices/大文档处理优化经验.md)
- [并行处理协议](protocols/PARALLEL_PROCESSING_PROTOCOL.md)

### 质量控制类
- [模板化报告撰写实践](best-practices/模板化报告撰写实践.md)
- [防编造系统实施总结](implementation-records/防编造系统实施总结.md)
- [并行质量检查清单](protocols/PARALLEL_QUALITY_CHECKLIST.md)

### 架构设计类
- [项目结构说明](guides/PROJECT_STRUCTURE.md)
- [可复用设计模式](guides/REUSABLE_DESIGN_PATTERNS.md)
- [多轮系统技术设计文档](implementation-records/多轮系统技术设计文档.md)

### 用户操作类
- [多轮系统用户操作手册](user-guides/multi-round-system/用户操作手册.md)
- [多轮系统快速入门指南](user-guides/multi-round-system/快速入门指南.md)

### 配置规范类
- [权限配置说明](protocols/PERMISSIONS_CONFIGURATION.md)
- [内容分类指南](guides/CONTENT_CLASSIFICATION_GUIDE.md)

---

## 📝 文档层级关系

```
核心系统文档 (根目录)
├── CLAUDE.md ...................... 🎯 主控制文档（Claude Code必读）
└── README.md ...................... 📖 项目说明

扩展文档 (docs/)
├── user-guides/ ................... 👤 用户视角（如何使用）
├── best-practices/ ................ ⭐ 可复用经验（跨项目）
├── implementation-records/ ........ 📋 实施存档（历史记录）
├── guides/ ........................ 🛠️ 开发者视角（如何开发）
├── protocols/ ..................... 📏 标准流程（如何执行）
└── history/ ....................... 🕰️ 演进历史（变更记录）
```

---

## 🎓 学习路径推荐

### 路径1：新用户上手
1. [多轮系统快速入门指南](user-guides/multi-round-system/快速入门指南.md)
2. [项目结构说明](guides/PROJECT_STRUCTURE.md)
3. [并行处理协议](protocols/PARALLEL_PROCESSING_PROTOCOL.md)

### 路径2：技术优化学习
1. [大文档处理优化经验](best-practices/大文档处理优化经验.md)
2. [模板化报告撰写实践](best-practices/模板化报告撰写实践.md)
3. [可复用设计模式](guides/REUSABLE_DESIGN_PATTERNS.md)

### 路径3：系统深度理解
1. [多轮系统用户操作手册](user-guides/multi-round-system/用户操作手册.md)
2. [多轮系统技术设计文档](implementation-records/多轮系统技术设计文档.md)
3. [防编造系统实施总结](implementation-records/防编造系统实施总结.md)

### 路径4：配置和部署
1. [权限配置说明](protocols/PERMISSIONS_CONFIGURATION.md)
2. [并行质量检查清单](protocols/PARALLEL_QUALITY_CHECKLIST.md)
3. [内容分类指南](guides/CONTENT_CLASSIFICATION_GUIDE.md)

---

## 💡 文档使用建议

### 查找文档的最佳方式

1. **快速查找**: 使用本页顶部的"快速入口"表格
2. **分类浏览**: 按6大分类查找相关文档
3. **主题检索**: 使用"按主题索引"快速定位
4. **关键词搜索**: Ctrl+F 搜索关键词

### 文档维护规范

**添加新文档时**:
1. 确定文档分类（user-guides/best-practices/implementation-records/guides/protocols/history）
2. 放入对应目录
3. 更新本索引文件
4. 更新主README.md（如适用）

**修改现有文档时**:
- 更新文档内的"最后更新"日期
- 如有重大变更，更新本索引中的描述

---

## 📞 反馈与改进

如果你发现：
- 文档链接失效
- 文档描述不准确
- 缺少重要文档索引
- 有更好的分类建议

请在项目issue中反馈或直接修改本索引文件。

---

**维护者**: Claude Code System
**文档索引版本**: v1.0
**索引创建日期**: 2025-11-13
