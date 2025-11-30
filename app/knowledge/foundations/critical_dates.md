---
id: critical_dates
name: 关键日期定义
category: foundations
version: 1.0.0
last_updated: 2024-11-29
token_estimate: 350
applicable_stages:
  - fact_check
  - analysis
  - report
---

# 关键日期定义

## 破产受理日期 (Bankruptcy Filing Date)

**数据来源**：项目配置文件 (`project_config.ini` 或 `.processing_config.json`)

**重要性**：**生命线级别** - 最高优先级

### 为何关键

- 决定所有利息计算的截止点
- 决定诉讼时效的比较基准日
- 日期错误 → 整个分析无效

### 验证协议（所有阶段必须执行）

1. 从 `.processing_config.json` 读取日期
2. 与前序报告交叉验证（如有）
3. 在输出报告中明确记录
4. 发现任何不一致立即停止

---

## 停止计息日期 (Interest Stop Date)

**计算公式**：破产受理日期 - 1 天

**示例**：
- 破产受理日期：2025-05-12
- 停止计息日期：2025-05-11

**应用**：所有利息计算必须在此日期或之前截止

---

## 日期验证清单

```
□ 从 .processing_config.json 读取破产日期
□ 与前序报告交叉验证（如适用）
□ 在输出中明确记录日期
□ 所有计算使用正确的停止计息日期
```

**警告**：一个日期错误可能导致数月工作无效，误导客户决策！
