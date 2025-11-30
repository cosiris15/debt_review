---
id: calculator_guide
name: 计算器使用指南
category: calculations
version: 1.0.0
last_updated: 2024-11-29
token_estimate: 400
applicable_stages:
  - analysis
---

# 计算器使用指南

## 强制使用规则

**所有利息计算必须使用计算器工具，禁止手动计算**

---

## 五种计算模式

### 1. simple - 简单利息

固定利率的简单利息

**参数**：
- `principal`: 本金
- `start_date`: 起始日期
- `end_date`: 结束日期
- `rate`: 年利率（%）

### 2. lpr - LPR浮动利率

按LPR浮动的利息，自动分段计算

**参数**：
- `principal`: 本金
- `start_date`: 起始日期
- `end_date`: 结束日期
- `multiplier`: 倍数（如1.0、1.3、1.5）
- `lpr_term`: 期限（"1y"或"5y"）

### 3. delay - 迟延履行利息

固定日利率0.0175%

**参数**：
- `principal`: 本金
- `start_date`: 起始日期
- `end_date`: 结束日期

### 4. penalty - 罚息

带上限的罚息计算（上限24%）

**参数**：
- `principal`: 本金
- `start_date`: 起始日期
- `end_date`: 结束日期
- `rate`: 约定年利率（%）

### 5. compound - 复利

复利计算

**参数**：
- `principal`: 本金
- `start_date`: 起始日期
- `end_date`: 结束日期
- `rate`: 年利率（%）

---

## 在报告中请求计算

当需要计算利息时，在分析报告中使用以下格式标记：

```
【利息计算】本金: 1000000, 起始日: 2023-01-15, 类型: lpr, 倍数: 1.3
【利息计算】本金: 500000, 起始日: 2022-06-01, 类型: simple, 利率: 6.0
【利息计算】本金: 200000, 起始日: 2024-01-01, 类型: delay
```

系统将自动识别并执行计算。

---

## LPR期限选择指南

| 借款期限 | 推荐LPR期限 |
|---------|-------------|
| ≤1年 | 1年期LPR |
| 1-5年 | 根据合同约定 |
| >5年 | 5年期LPR |

**注意**：长期债务使用1年期LPR是常见错误
