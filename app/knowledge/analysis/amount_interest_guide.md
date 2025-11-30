# Amount Breakdown and Interest Calculation Guide

## Purpose

This guide provides detailed methodologies for systematically breaking down debt claim amounts into independent items and calculating five types of interest using precise parameters.

## Part 1: Amount Breakdown Methodology

### Core Principles

**⚠️ Must follow "Itemized Breakdown" + "Substance Over Form" principles**

- Break down umbrella terms like "principal" and "interest" into smallest meaningful units
- Each amount item must have specific legal basis and calculation logic
- Every item must correspond to verifiable evidence

### Three-Category Breakdown Structure

```
债权总额 (Total Claim Amount)
├── 本金类项目 (Principal Items)
│   ├── XX合同项下的第N期货款
│   ├── XX项目的进度款
│   └── 质保金
│
├── 孳息/违约类项目 (Ancillary Items)
│   ├── 借贷类合同利息
│   ├── 普通合同逾期利息（含违约金）
│   └── 迟延履行期间债务利息
│
└── 费用类项目 (Cost/Expense Items)
    ├── 律师费
    ├── 案件受理费
    └── 保全费
```

## Part 2: Category-Specific Breakdown Standards

### Category 1: Principal Items (本金类项目)

**Identification Standard**: Amounts constituting the core original payment obligations, broken down by specific legal relationship.

#### Sales/Supply Relationships

**Breakdown Examples**:
- "XX合同项下的第N期货款" (Nth installment under XX contract)
- "订单号XXX对应的货款" (Payment for order #XXX)
- "设备采购合同尾款" (Final payment under equipment purchase contract)

**Key Points**:
- Specify contract identification (name, number, date)
- Identify specific installment or delivery phase
- Link to specific order or transaction

#### Service/Construction Relationships

**Breakdown Examples**:
- "XX合同项下的设计费尾款" (Final design fee under XX contract)
- "XX项目的进度款" (Progress payment for XX project)
- "质保金" (Quality guarantee deposit)

**Key Points**:
- Identify specific project or service scope
- Specify payment phase (progress, final, retention)
- Link to project milestones

#### Loan Relationships

**Breakdown Examples**:
- "XX借款合同项下的本金" (Principal under XX loan contract)
- "第N期借款本金" (Nth installment loan principal)

**Key Points**:
- Specify loan contract details
- Identify specific disbursement or installment
- Note original loan amount if different from outstanding balance

#### Legal Document-Based Claims

**Breakdown Examples**:
- "（案号）判决书确认的应返还款项" (Amount to be returned per judgment [case #])
- "（案号）调解书确认的工程款" (Construction payment per mediation [case #])

**Key Points**:
- Cite specific legal document (court, case number)
- Quote exact wording from judgment/mediation
- Note if amount differs from original contractual amount

### Category 2: Ancillary Items (孳息/违约类项目)

**Identification Standard**: Derivative amounts arising from principal, due to time passage or breach. Each unique calculation logic (specific principal + specific rate + specific period) = one independent item.

#### Type 2.1: Loan Contract Interest

**Legal Nature**: Interest payment is part of contractual performance obligation in loan agreements.

**Breakdown Examples**:
- "XX借款合同项下的合同利息，以借款本金500,000元为基数，按固定年利率/LPR浮动利率计算"
- "融资租赁合同项下的租金利息部分"

**Key Elements**:
- Identify loan contract
- Specify principal base
- State interest rate (fixed or LPR floating)
- Note interest period

#### Type 2.2: Overdue Interest on Ordinary Contracts (Including Penalties)

**Legal Nature**: Interest claimed by non-breaching party after contract breach, based on contractual or statutory standards.

**Breakdown Examples**:
- "基于设计费尾款132,216.00元，自合同约定付款期限届满次日起至破产受理日前一日止，按合同约定24%年利率计算的逾期付款利息"
- "基于工程款，按1年期LPR浮动利率计算的逾期利息"
- "基于货款，按合同约定计算的违约金（固定金额或比例）"

**⚠️ Critical Classification Rule**: Penalties (违约金) should be classified as "interest", NOT "other".

**Key Elements**:
- Identify principal item being breached
- Specify overdue period start (usually day after payment deadline)
- State applicable rate (contractual or LPR)
- Note calculation end date (bankruptcy filing date - 1 day)

#### Type 2.3: Delayed Performance Interest

**Legal Nature**: Interest applicable when debtor fails to perform after effective legal document deadline, to ensure enforcement effectiveness.

**Breakdown Examples**:
- "（案号）判决书确认的迟延履行期间的加倍部分债务利息，按日利率万分之1.75计算"
- "（案号）调解书确认的迟延履行期间债务利息"

**Key Elements**:
- Cite legal document (judgment, mediation, arbitration)
- Identify performance deadline
- Note fixed rate (daily rate 0.0175%)
- Specify interest start date (day after deadline expiration)

### Category 3: Cost/Expense Items (费用类项目)

**Identification Standard**: Expenses incurred to realize the claim that can be legally or contractually recovered from debtor.

**Breakdown Examples**:
- "为追索债权支出的律师费" (Attorney fees for claim recovery)
- "（案号）判决书判令由债务人承担的案件受理费" (Court filing fee as ordered by judgment)
- "（案号）判决书判令由债务人承担的保全费" (Preservation fee as ordered by judgment)

**Key Points**:
- Only include recoverable costs (must have legal or contractual basis)
- Costs must be actually incurred
- Judgment-awarded costs require specific court order

## Part 3: Interest Calculation Parameters

### Five Interest Calculation Types

#### Type 1: Simple Interest (Fixed Rate)

**Applicable Scope**: Loan contracts, financing leases where interest is part of contractual obligation.

**Calculation Characteristics**:
- **Interest start date**: Loan disbursement date or contractually specified date
- **Interest rate**: Fixed annual rate per contract
- **Calculation base**: Actual loan principal
- **Calculation period**: Per contractual interest-bearing period

**Key Parameters**:
```
- Principal (本金): Specific amount
- Start date (起息日): YYYY-MM-DD
- End date (止息日): YYYY-MM-DD (max: bankruptcy filing date - 1 day)
- Annual rate (年利率): Percentage (e.g., 4.35%)
```

#### Type 2: LPR Floating Rate Interest

**Applicable Scope**: Contracts specifying LPR-based interest rates.

**Calculation Characteristics**:
- **Interest start date**: Overdue date (day after payment deadline)
- **Interest rate**: LPR × multiplier (e.g., LPR × 1.5)
- **Calculation base**: Overdue unpaid contract amount
- **Calculation period**: From overdue date to bankruptcy filing date - 1 day

**Key Parameters**:
```
- Principal (本金): Specific amount
- Start date (起息日): YYYY-MM-DD
- End date (止息日): YYYY-MM-DD (max: bankruptcy filing date - 1 day)
- Multiplier (倍数): Number (e.g., 1.5, 4.0)
- LPR term (期限): 1y or 5y
```

**⚠️ LPR Term Selection Rules** (CRITICAL): 证据不足不得推测原则

**⚠️ 核心原则: 证据不足则停止计算,禁止推测**

LPR期限(1年期 vs 5年期以上)必须有明确证据依据,不得根据"债务期限长短"或"一般惯例"推测。

---

### 🔍 LPR期限选择严格决策协议

**情形1: 合同明确约定期限** ✅
```
合同条款明确写明:
  - "按1年期LPR计算利息"
  - "按5年期以上LPR计算利息"
  - "按贷款市场报价利率(LPR)(1年期)计算"

处理: 使用合同明确约定的LPR期限
```

**情形2: 债权人申报明确期限** ✅
```
合同未明确,但债权人在申报表注明:
  - "按1年期LPR计算利息XX元"
  - "按5年期以上LPR浮动1.5倍计算"

处理: 使用债权人申报的LPR期限
      (就低原则仍适用于计算结果vs申报金额的比较)
```

**情形3: 法律文书明确载明** ✅ (最高优先级)
```
判决书/调解书/仲裁裁决明确:
  - "按5年期以上LPR计算利息"
  - "利息按1年期LPR标准计算"

处理: 以法律文书载明的LPR期限为准(最高证据效力)
```

**情形4: 合同和申报均未明确** ❌ **停止计算**

⚠️ **最常见错误发生点 - 严禁推测**

```
证据状态:
  - 合同仅写:"按LPR计算利息" 或 "按贷款市场报价利率"
  - 申报表未注明具体LPR期限,仅写利息总额(如"利息50万元")

❌ 绝对禁止的推测行为:
  1. ❌ "借款期限8年 > 5年,所以应用5年期LPR"
     → 错误:借款期限是结果,不是利率期限的证据

  2. ❌ "一般房贷用5年期,这是购房借款,所以用5年期"
     → 错误:不能用"一般""惯例"推测合同条款

  3. ❌ "1年期算出来更低,用就低原则选1年期"
     → 错误:就低原则用于比较金额,不用于选择证据依据

  4. ❌ "两个都试算,选对债权人有利的"
     → 错误:没有证据依据的试算毫无意义

✅ 正确处理:
  1. 停止利息计算
  2. 在报告中标记:"[LPR期限未明确,无法计算]"
  3. 说明理由:
     "合同约定'按LPR计算利息',未指明1年期或5年期以上;
      债权人申报利息总额XXX元,但未说明LPR期限;
      证据不足以确定具体LPR期限,无法进行验算。"
  4. 建议处理:
     "建议要求债权人补充说明所主张的LPR期限
      (提供补充证据或补充说明),
      或根据就无原则,利息部分不予确认。"
  5. 申报金额的处理(按就低原则):
     - 如债权人申报了利息金额但未说明计算依据
     - 可选方案1:因计算依据不明,确认金额0元
     - 可选方案2:标注"待补充材料后再行确认"
```

**情形5: 合同模糊但判决明确** ✅
```
合同:"按LPR"(未明确期限)
判决:"支持利息XX元,按5年期以上LPR计算"

处理: 以判决载明的5年期以上LPR为准
```

---

### 📊 LPR期限选择决策矩阵

| 合同约定 | 债权人申报说明 | 法律文书 | 处理方式 | 禁止行为 |
|---------|--------------|---------|---------|---------|
| 明确1年期 | - | - | ✅ 使用1年期 | - |
| 明确5年期+ | - | - | ✅ 使用5年期+ | - |
| 未明确/"按LPR" | 申报说明1年期 | - | ✅ 使用1年期(申报) | - |
| 未明确/"按LPR" | 申报说明5年期+ | - | ✅ 使用5年期+(申报) | - |
| 未明确/"按LPR" | 仅申报金额,未说明期限 | - | ❌ **停止计算** | ❌ 禁止推测期限 |
| 未明确/"按LPR" | 未申报利息 | - | ❌ **不予确认**(就无原则) | ❌ 禁止主动计算 |
| 任意 | 任意 | 明确X年期 | ✅ 使用X年期(文书最高) | - |
| 明确1年期 | 申报说明5年期 | - | ⚠️ 不一致,需分析 | ❌ 禁止擅自选择 |

---

### ❌ 禁止的推测逻辑(重要)

**错误推理1: 用借款期限推断利率期限**
```
❌ "借款期限8年 > 5年,所以应该用5年期LPR"

为何错误:
  - 借款期限 = 借款合同约定的还款期限(如8年还清)
  - LPR期限 = 利率计算的基准期限(1年期 or 5年期+)
  - 两者是不同概念,不能直接对应
  - 8年期借款完全可以约定按1年期LPR浮动计息

正确做法:
  - 查合同利率条款,看是否明确约定LPR期限
  - 如未约定,停止计算,不得推测
```

**错误推理2: 用贷款类型推断利率期限**
```
❌ "这是购房贷款,房贷一般用5年期LPR,所以用5年期"
❌ "这是流动资金贷款,一般用1年期,所以用1年期"

为何错误:
  - "一般""通常""惯例"不是法律依据
  - 不能用行业惯例替代合同约定
  - 具体合同可以偏离"一般情况"

正确做法:
  - 只看具体合同条款和申报说明
  - 无明确依据则停止计算
```

**错误推理3: 用就低原则选择利率期限**
```
❌ "1年期算出利息30万,5年期算出50万,
    按就低原则选1年期(30万<50万)"

为何错误:
  - 就低原则是比较"证据计算结果"vs"债权人申报金额"
  - 不是用来在两个推测之间选择
  - 没有证据依据的计算,无论结果如何都无效

正确做法:
  - 就低原则用于:计算出80万 vs 申报50万 → 确认50万
  - 不用于:猜1年期 vs 猜5年期 → 都不对,应停止
```

**错误推理4: 参考同期其他债权**
```
❌ "该债务人其他债权都用5年期LPR,这个应该也是5年期"

为何错误:
  - 每个债权关系独立,不能类比
  - 不同合同可以有不同约定
  - 同一债务人≠统一利率标准

正确做法:
  - 单独分析本债权的合同约定
  - 不参考其他债权的情况
```

---

### ✅ 允许的期限选择(有证据依据)

**场景1: 合同明确约定**
```
合同第X条:"利息按1年期LPR浮动1.5倍计算"

处理: 使用1年期LPR,倍数1.5
Calculator命令:
  python universal_debt_calculator_cli.py lpr \
    --lpr-term 1y --multiplier 1.5 ...
```

**场景2: 债权人明确申报**
```
合同:"按LPR计息"(未明确期限)
申报表:"利息50万元,按5年期以上LPR计算"

处理: 使用5年期LPR(以申报为准)
注意: 计算结果仍需与申报金额50万比较,应用就低原则
```

**场景3: 判决书明确**
```
合同:"按LPR"(未明确)
判决:"支持利息XX元,按照贷款发放时5年期以上LPR计算"

处理: 使用5年期LPR(判决最高效力)
```

**场景4: 法定利率推定(特定情况)**
```
合同:"按法定利率计息"(未约定LPR)
适用场景:民间借贷等适用法定利率上限的情况

处理: 按照司法解释,适用LPR×4倍
      (一般用1年期LPR作为基准)
注意: 这是法律明确规定,不是推测
```

---

### 🎯 实战案例对比

**案例1: 证据充分(可计算)**
```
合同条款:"借款利息按5年期以上LPR浮动1.3倍计算"
债权人申报:"利息100万元"

分析:
  ✅ 合同明确:5年期以上LPR × 1.3
  ✅ 可以计算验证

处理:
  1. 用calculator计算:lpr-term 5y, multiplier 1.3
  2. 假设算出120万
  3. 应用就低原则:申报100万 < 计算120万 → 确认100万
```

**案例2: 证据不足(停止计算)**
```
合同条款:"借款利息按LPR计算"
债权人申报:"利息100万元"
借款期限:8年

分析:
  ❌ 合同未明确:1年期 or 5年期?
  ❌ 申报未说明:哪个期限?
  ⚠️ 借款期限8年:不能作为LPR期限依据

处理:
  1. 停止计算
  2. 标记:"[LPR期限:证据未明确,无法计算]"
  3. 说明:"合同约定'按LPR',未明确期限;债权人申报100万但未说明计算依据;建议要求补充说明"
  4. 建议确认:0元(或待补充后确认)
```

**案例3: 判决补强(可计算)**
```
合同条款:"按LPR计息"(未明确期限)
判决书:"支持本金及利息,利息按1年期LPR计算"
债权人申报:"本金+利息共200万"

分析:
  ✅ 判决明确:1年期LPR
  ✅ 可以计算验证

处理:
  1. 以判决为准,使用1年期LPR
  2. Calculator计算后与申报比较
```

---

### 📝 报告中的标准表述

**情形A: 期限明确,可计算**
```
利息计算依据:根据《XX合同》第X条,约定利息按1年期LPR浮动1.5倍计算。
债权人申报利息XX万元。
经计算(详见计算文件),利息为YY万元。
确认:XX万元(就低原则,申报<计算)。
```

**情形B: 期限不明,停止计算**
```
利息计算依据:《XX合同》第X条约定"按LPR计息",未明确1年期或5年期以上。
债权人申报利息XX万元,但未说明所主张的具体LPR期限。
[LPR期限:证据未明确,无法计算验证]
建议:要求债权人补充说明所主张的LPR期限,或提供补充证据;
      或根据就无原则(因计算依据不明),利息部分不予确认。
```

**情形C: 未申报利息**
```
利息:债权人未申报利息。
《XX合同》约定利率条款,但债权人未主张利息,根据就无原则,不予确认。
```

#### Type 3: Delayed Performance Interest (迟延履行期间债务利息)

**Applicable Scope**: ONLY for amounts confirmed by effective legal documents (judgments, mediations, arbitrations).

**Prerequisites** (ALL must be met):
1. **MUST be judgment debt**: Only applies to amounts confirmed by effective legal documents
2. **MUST verify performance period expired**:
   - Determine performance deadline from judgment/mediation
   - **Relative deadline**: Effective date + performance period
     * First-instance no appeal: Effective 15 days after delivery
     * Second-instance (including affirmation): **Effective on second-instance judgment date, NOT first-instance**
   - **Specific deadline**: Use date specified in legal document
   - **No deadline specified**: Use effective date as deadline
3. **MUST be declared by creditor**: Follow "就无原则" - don't calculate if not declared

**Calculation Characteristics**:
- **Interest start date**: Day after performance deadline expires
- **Interest rate**: Fixed daily rate 0.0175% (万分之1.75)
- **Calculation base**: Amount in delayed performance
- **End date**: Bankruptcy filing date - 1 day

**Key Parameters**:
```
- Principal (迟延履行款项): Specific amount
- Start date (起息日): Day after performance deadline
- End date (止息日): YYYY-MM-DD (usually bankruptcy filing date - 1 day)
- Rate: Fixed at 0.0175% daily (no parameter needed)
```

**⚠️ Important Legal Reminder**:
- First-instance no appeal: Effective 15 days after delivery
- Second-instance affirms first-instance: Effective date is **second-instance judgment date**, NOT first-instance effective date

#### Type 4: Compound Interest

**Applicable Scope**: Contracts explicitly providing for compound interest (interest on interest).

**Calculation Characteristics**:
- **Compounding cycle**: Per contract (e.g., monthly, quarterly, annually)
- **Interest rate**: Annual rate per contract
- **Calculation method**: Interest accrued in each cycle is added to principal for next cycle

**Key Parameters**:
```
- Principal (本金): Initial principal amount
- Start date (起息日): YYYY-MM-DD
- End date (止息日): YYYY-MM-DD
- Annual rate (年利率): Percentage
- Compounding cycle (复利周期): e.g., "每月末", "每季度末"
```

**⚠️ Legal Limitation**: Compound interest must have explicit contractual basis.

#### Type 5: Payment Offset Handling

**Applicable Condition**: Debtor made payments during the debt period (after claim arose, before bankruptcy filing).

**Strategy**: Segmented calculation + offset processing

**Step-by-Step Process**:

1. **Split periods by payment dates**
   - Identify all payment dates
   - Create calculation segments: [Start → Payment 1], [Payment 1 → Payment 2], etc.

2. **Calculate separately for each segment**:
   - Pre-payment period: Use original principal
   - Post-payment period: Use remaining principal after offset

3. **Apply offset order**:

   **For General Debts** (per Civil Code Article 561):
   ```
   Offset Order:
   1. Costs (实现债权的费用)
   2. Interest (利息)
   3. Principal (主债务/本金)
   ```

   **For Judgment Debts** (per Supreme Court interpretation):
   ```
   Offset Order:
   1. Amounts determined in legal document (判决书确定的金钱债务)
      - Includes principal, interest, costs in judgment
   2. Delayed performance interest (加倍部分债务利息)
   ```

   **Agreement Priority**: If parties agreed on different offset order, follow agreement.

4. **Sum results**: Total interest = Sum of all segments minus offset portions

**Multiple Payments**: Process sequentially by time order, each payment uses remaining amount from previous offset as new base.

**Example**:
```
Original debt: 100,000 principal + interest
Payment 1 on 2023-06-15: 20,000
Payment 2 on 2023-10-20: 15,000

Calculation segments:
- Segment 1: Interest start → 2023-06-15 (base: 100,000)
- Offset: 20,000 applied per order (costs → interest → principal)
- Segment 2: 2023-06-15 → 2023-10-20 (base: remaining principal after offset)
- Offset: 15,000 applied per order
- Segment 3: 2023-10-20 → Bankruptcy filing - 1 day (base: remaining principal)
```

## Part 4: Interest Rate Reference (2024-2025)

| 利率类型 | 参考值 | 备注 |
|---------|-------|------|
| 1年期LPR | 3.45% | 一般商事债权常用 |
| 5年期以上LPR | 3.95% | 长期贷款、超5年债权 |
| 法定利率上限 | LPR × 4 | 民间借贷利率保护上限 |
| 迟延履行利率 | 日利率0.0175% | 固定，仅适用判决债权 |

## Part 5: Core Application Rules

### Rule 1: 就低原则 (Lower Bound Rule)

**When**: Calculation result > Creditor's declared amount

**Action**: Use declared amount as final confirmation (就低)

**Example**: Creditor declares 10,000 interest, calculation shows 12,000 → Confirm 10,000

**Rationale**: Respect creditor's self-limitation of claim amount.

### Rule 2: 就无原则 (Non-Existence Rule)

**When**: Identified amount item was NOT declared by creditor

**Action**: Do NOT include this item in final confirmation (就无)

**Example**: Evidence shows 5,000 attorney fees but creditor didn't declare → Don't confirm this item

**⚠️ Important Applications**:
- Don't proactively calculate delayed performance interest if creditor didn't declare it
- Don't expand calculation base beyond what creditor declared
- Don't add cost items creditor didn't claim

**Rationale**: Debt review is verification, not claim generation. Only review what creditor claimed.

### Rule 3: Evidence Support Rule

**Requirements**:
- Creditor-declared items without evidence support → NOT confirmed
- Evidence-proven items not declared by creditor → NOT included (Rule 2 applies)

**Standard**: Both declaration AND evidence required for confirmation.

### Rule 4: Court Fee Special Rule

**Important**: Do NOT calculate delayed performance interest on court fees

**Reasons**:
- Court fees have separate performance deadlines
- Need individual assessment for deadline expiration
- Even if expired, be cautious about calculating delayed interest

**Application**: Treat court fees separately from main claim amounts.

## Part 6: Special Handling Scenarios

### Scenario 1: Segmented Calculation

**When**: Same item requires different calculation parameters for different periods (e.g., rate changes, payment offsets).

**Approach**: List calculation parameters separately for each segment.

**Example**:
```
Period 1 (2023-01-01 to 2023-06-30):
- Principal: 100,000
- Rate: 4.35% annual

Period 2 (2023-07-01 to 2023-12-31):
- Principal: 80,000 (after payment offset)
- Rate: 4.35% annual
```

### Scenario 2: Rate Changes

**When**: Interest rate changes during calculation period (e.g., LPR adjustments, contractual rate changes).

**Approach**: Clearly specify applicable rate for each time period.

**Example**:
```
2023-01-01 to 2023-06-20: LPR 3.65% × 1.5
2023-06-21 to 2023-12-31: LPR 3.45% × 1.5
```

### Scenario 3: Base Day Selection

**Standard**: Clarify whether using 360 days or 365 days as annual base.

**General Rules**:
- Commercial contracts: Usually 360 days
- Civil lending: Usually 365 days
- Follow contract terms if specified

**Consistency**: Use same base throughout all calculations for same claim.

## Part 7: Penalty Interest Calculation

### Legal Maximum for Penalties

**⚠️ Critical**: Penalties (违约金) cannot exceed 4× LPR (as annual rate).

**Calculation Process**:
1. Calculate penalty per contract terms
2. Calculate 4× LPR cap:
   - Use 1-year LPR or 5-year LPR based on period rules
   - Multiply by 4
   - Apply to principal and period
3. Compare results
4. Use lesser amount (but also apply "就低原则" against declared amount)

**Example**:
```
Contract penalty: 24% annual rate
Principal: 100,000
Period: 365 days

Contractual calculation: 100,000 × 24% × (365/365) = 24,000
4× LPR cap: 100,000 × (3.45% × 4) × (365/365) = 13,800
Creditor declared: 15,000

Final confirmation: 13,800 (4× LPR cap < declared amount < contractual)
```

## Summary

This guide establishes:
1. **Systematic breakdown** of all claim amounts into independent items
2. **Precise parameters** for five types of interest calculations
3. **Clear rules** for LPR term selection (critical for >5 year debts)
4. **Offset handling** for segmented calculations with payments
5. **Core principles** (就低, 就无) for final confirmation

**Remember**: Every amount item must have:
- Specific legal basis (contract, judgment, etc.)
- Clear calculation logic (if not fixed amount)
- Evidence support
- Creditor declaration (就无原则)

Use `universal_debt_calculator_cli.py` for ALL interest calculations - NEVER manual calculations.
