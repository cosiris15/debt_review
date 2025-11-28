---
name: claim-review-legal-standards
description: 复杂债权案件和疑难法律问题的进阶审查标准。适用于民事诉讼准备、尽职调查、商业谈判等场景。仅用于以下特殊情况：越权担保、保证期间与诉讼时效、夫妻共同债务、让与担保、混合担保、抵押登记效力、抵押权优先顺序、查封对抵押权的影响、金融不良债权转让、保理争议、融资租赁、建设工程优先权、诉讼时效与举证责任、抵销权争议、复杂利率计算争议。常规债权审查使用claim-analysis即可。
---

# Claim Review Legal Standards Skill
# 债权审查法律标准（进阶参考）

## ⚠️ 重要提示：本Skill适用范围

**本Skill为进阶法律标准参考手册，仅用于复杂案件和疑难法律问题。**

### ✅ 必须使用本Skill的10种情况

**适用场景**: 民事诉讼准备、尽职调查、商业谈判、债权收购评估等

如您遇到以下任一情况，本Skill将提供详细法律依据和操作标准：

#### 1. 担保类争议（secured claims disputes）
- 越权担保效力认定（公司未经决议对外担保）
- 让与担保（以房屋买卖合同等形式提供担保）
- 混合担保（物保+人保并存时的责任顺序）
- 担保物权设定争议（登记vs交付）
- 保证责任期间与诉讼时效衔接

#### 2. 金融机构债权（financial institution claims）
- 复利、罚息的计算方法和基数认定
- 金融不良债权转让后的利息计付
- 变相利息的识别和处理
- 金融借款与民间借贷的区分标准

#### 3. 民间借贷争议（private lending disputes）
- 利率上限的分段计算（2020年8月20日前后）
- 砍头息（利息预先扣除）的认定和处理
- 变相利息（服务费、咨询费等）的认定
- 复利、罚息的计算限制

#### 4. 保理业务争议（factoring disputes）
- 保理合同效力审查
- 虚构应收账款的识别
- 保理与借款的性质区分
- 回购义务的法律性质

#### 5. 融资租赁争议（financial leasing disputes）
- 售后回租的效力认定
- 租赁物价值确定方法
- 虚构租赁物导致合同无效
- 租金利息的分离计算

#### 6. 建设工程类（construction claims）
- 建设工程价款优先权的行使期限（18个月）
- 装修装饰工程是否享有优先权
- 工程款利息的起算点认定
- 质保金的到期认定

#### 7. 涉诉复杂计算（litigation-based complex calculations）
- 迟延履行期间的一般债务利息
- 迟延履行期间的加倍部分债务利息
- 加倍利息的计算基数争议（是否包含律师费、诉讼费）
- 申请执行期间的认定（2年时效）

#### 8. 程序性争议（procedural disputes）
- 诉讼时效的中断、中止和延长
- 举证责任分配的特殊规则
- 抵销权的行使条件和限制
- 管辖权异议和财产保全策略

#### 9. 特殊债权类型（special claim types）
- 劳动债权的认定和清偿顺序
- 税款、社保的滞纳金性质认定
- 违约金与损失赔偿的关系
- 诉讼费、律师费的确认条件

#### 10. 法律适用争议（legal application disputes）
- 新旧法律的衔接适用（如诉讼时效2年→3年）
- 司法解释的时间效力
- 民法典与合同法的过渡适用
- 特别法与一般法的适用顺序

---

### ❌ 不需要使用本Skill的情况

**以下常规债权直接使用 `claim-analysis` 即可，无需加载本Skill：**

- ✅ 普通买卖合同货款（证据齐全，无争议）
- ✅ 标准借款合同（利率明确，在法定范围内）
- ✅ 常规工程款（无优先权争议）
- ✅ 简单担保（有决议，已登记，无效力争议）
- ✅ 生效判决债权（执行期限内，金额明确）

**判断标准**：如果您的案件可以通过现有Skills的标准和工具直接处理，**请勿使用本Skill**。本Skill仅在遇到法律适用疑难、需要详细司法解释依据、或涉及上述10种特殊情况时使用。

---

## Overview / 概述

### Skill定位

本Skill是现有债权审查体系的**进阶法律参考层**，提供：

1. **详细法律依据**：《民法典》、《民事诉讼法》及相关司法解释的详细条文
2. **边界案例处理**：针对争议情况的具体操作标准
3. **司法实践指引**：基于顶级律所诉讼实务经验总结的审查要点
4. **疑难问题解答**：复杂法律关系的认定标准和裁判规则

### 与现有Skills的关系

```
常规债权审查流程（90%案件）：
claim-fact-checking → claim-analysis → report-organization
          ↓                    ↓
    使用基础标准        使用基础计算和分析标准

复杂债权审查流程（10%案件）：
claim-fact-checking → claim-analysis ←→ claim-review-legal-standards
                              ↓                      ↓
                    遇到复杂问题时      提供详细法律依据和边界标准
                          ↓
                 report-organization
```

**核心原则**：本Skill是**补充参考**，不替代现有workflow。常规操作仍使用claim-analysis，仅在遇到上述10种复杂情况时，参考本Skill的详细法律标准。

---

## When to Use This Skill / 何时使用

### 使用时机判断流程

```
Step 1: 案件是否属于10种特殊情况？
        ↓ 否
        直接使用 claim-analysis

        ↓ 是

Step 2: 现有Skills的标准是否足够？
        ↓ 是
        使用现有Skills标准即可

        ↓ 否（需要更详细法律依据）

Step 3: 使用本Skill查找具体法律条文和操作标准
        ↓
        获得详细依据后，继续claim-analysis流程
```

### 典型使用场景示例

#### 场景1：担保效力争议

**问题**：提供的担保合同没有公司股东会决议，是否有效？

**处理流程**：
1. 在claim-analysis识别为"担保效力争议"
2. 调用claim-review-legal-standards查阅`06_secured_claims_standards.md`中的"越权担保"章节
3. 获得详细的判断标准（决议要求、善意相对人认定、例外情形）
4. 返回claim-analysis继续处理

#### 场景2：利率上限争议

**问题**：借款合同签订于2019年，利率为年化30%，如何分段计算？

**处理流程**：
1. 在claim-analysis识别为"民间借贷利率争议"
2. 调用claim-review-legal-standards查阅`05_private_lending_standards.md`中的"利率上限"章节
3. 获得2020年8月20日前后的分段计算标准
4. 使用universal_debt_calculator_cli.py按标准分段计算

#### 场景3：建设工程优先权

**问题**：承包人主张工程款优先受偿权，如何审查期限？

**处理流程**：
1. 在claim-analysis识别为"建设工程优先权"
2. 调用claim-review-legal-standards查阅`07_special_claims_standards.md`中的"建设工程优先权"章节
3. 获得18个月期限的起算标准、装修工程的特殊要求
4. 返回claim-analysis完成债权分类

---

## Skill Structure / 知识结构

本Skill包含**11个专题领域**，对应11个reference文件：

| 专题 | Reference文件 | 核心内容 |
|------|--------------|----------|
| 1. 主体、举证、时效 | `01_subject_and_evidence_standards.md` | 主体资格、举证责任、诉讼/执行时效、除斥期间 |
| 2. 涉诉类债权 | `02_litigation_claims_standards.md` | 生效法律文书、诉讼费、律师费、迟延履行利息 |
| 3. 利息计算 | `03_interest_calculation_standards.md` | 利息审查原则、计算方法、复利罚息规则 |
| 4. 金融机构债权 | `04_financial_institution_standards.md` | 持牌机构识别、复利罚息、不良债权转让 |
| 5. 民间借贷 | `05_private_lending_standards.md` | 利率上限分段、砍头息、变相利息认定 |
| 6. 担保类债权 | `06_secured_claims_standards.md` | 越权担保、让与担保、混合担保、保证期间 |
| 7. 特殊债权类型 | `07_special_claims_standards.md` | 融资租赁、保理、建设工程优先权 |
| 8. 劳动债权 | `08_employee_claims_standards.md` | 劳动债权认定、清偿顺序、诉讼时效 |
| 9. 其他事项 | `09_other_matters_standards.md` | 抵销权、管辖权异议、税款社保滞纳金 |
| 10. 保证担保效力深度分析 | `10_guarantee_effectiveness_analysis.md` | 越权担保效力、保证期间、夫妻共同债务、主从合同效力、反担保、九民纪要适用 |
| 11. 抵押权效力深度分析 | `11_mortgage_effectiveness_analysis.md` | 抵押登记效力、优先顺序规则、查封影响、抵押物瑕疵、在建工程抵押、期待权抵押 |

**详细内容请查阅对应reference文件**。

---

## Core Principles / 核心原则

1. **法律依据优先**：所有结论必须有明确法律条文、司法解释或最高院意见
2. **证据层级意识**：生效法律文书 > 双方确认 > 合同约定 > 单方证据
3. **时效期间管理**：诉讼时效（3年，可中断）vs 除斥期间（不可中断）
4. **实体程序分离**：程序瑕疵不影响实体权利存在，但可能影响实现
5. **利益平衡**：债权人vs债务人、个别vs全体、担保vs普通、职工vs其他

---

## Integration / 与其他Skills的协同

- **与claim-analysis**: 遇复杂问题时查阅本Skill获取法律依据，然后返回继续处理
- **与claim-review-foundations**: foundations提供基础概览，本Skill提供进阶深度

**使用提醒**：
- ✅ 使用前确认：属于10种特殊情况、现有Skills无法解决、需详细法律依据
- ✅ 使用后记录：具体法律条文、在报告中注明依据、返回正常流程

**知识来源**：顶级律所诉讼实务经验，涵盖《民法典》《民事诉讼法》及司法解释（截至2025年）

---

## Quick Reference / 快速查找

| 问题类型 | 查找文件 |
|---------|---------|
| 担保无决议/让与担保/混合担保 | 06_secured_claims |
| 越权担保效力/保证期间/夫妻共同债务/九民纪要 | 10_guarantee_effectiveness_analysis |
| 抵押登记效力/优先顺序/查封影响/在建工程抵押 | 11_mortgage_effectiveness_analysis |
| 民间借贷利率分段/砍头息 | 05_private_lending |
| 迟延履行加倍利息 | 02_litigation_claims |
| 工程优先权/保理/融资租赁 | 07_special_claims |
| 诉讼时效/执行时效/举证责任 | 01_subject_and_evidence |
| 金融借款复利罚息 | 04_financial_institution |
| 抵销权/管辖权异议 | 09_other_matters |
| 利息计算方法 | 03_interest_calculation |
| 劳动债权/诉讼时效 | 08_employee_claims |

---

## Summary / 总结

本Skill是债权审查体系的**进阶法律参考层**，专为复杂案件和疑难问题设计：

**核心价值**：
- 提供详细法律条文依据（民法典、民事诉讼法及司法解释）
- 提供边界案例处理标准
- 提供司法实践操作指引

**使用原则**：
- 仅用于10种特殊情况
- 常规案件使用claim-analysis
- 获取法律依据后返回正常流程

**知识结构**：
- 9个专题领域
- 9个详细reference文件
- 涵盖所有主要法律争议类型

**适用场景**：
- 民事诉讼准备（诉前债权评估、证据审查）
- 尽职调查（债权收购、资产评估）
- 商业谈判（债务重组、和解方案）

**记住**：本Skill是补充参考，不替代现有workflow。90%的常规案件无需使用本Skill，直接使用claim-analysis即可高效完成。

如有任何疑问，请优先查阅各reference文件的详细说明。
