# Common Terms Glossary

## Purpose

Comprehensive glossary of debt claim review terminology used in bankruptcy proceedings, with Chinese-English mappings and usage context.

## A-D

### 按期履行 (Timely Performance)
Payment or performance by the contractual deadline. Opposite of 逾期 (overdue).

### 案件受理费 (Court Filing Fee)
Fee charged by court for accepting a case. May be awarded to prevailing party in judgment.
**Note**: Generally do NOT calculate delayed performance interest on court fees.

### 暂缓确认 (Deferred Confirmation)
Status for claims that cannot be confirmed immediately.
**Reasons**: Time-barred, insufficient evidence, pending litigation, etc.
**Usage**: Mark in review opinion form instead of specific amount.

### 保全费 (Preservation Fee)
Court fee for property preservation measures. Recoverable if awarded in judgment.

### 本金 (Principal)
Core amount owed, excluding interest, penalties, and costs.
**Classification**: 本金类项目 (Principal Items)
**Examples**: Loan principal, contract price, project payment

### 破产受理日 (Bankruptcy Filing Date / Acceptance Date)
Date court accepts bankruptcy application.
**Criticality**: **生命线级别** (Lifeline-level) - determines ALL interest calculations
**Source**: `.processing_config.json` in creditor directory

### 补充协议 (Supplementary Agreement)
Agreement supplementing or amending main contract.
**Hierarchy**: Later supplement supersedes earlier terms on same subject.

###财产保全 (Property Preservation)
Court order freezing debtor assets pending litigation outcome.

### 承揽合同 (Processing Contract / Work for Hire)
Contract for processing, customization, or completing specific work.

### 出借人 (Lender)
Party providing loan. In bankruptcy context, becomes creditor if loan unpaid.

### 催款函 (Demand Letter / Collection Letter)
Written notice demanding payment.
**Effect**: May constitute statute interruption if properly delivered.

### 迟延履行 (Delayed Performance)
Failure to perform after judgment deadline expires.
**Interest**: 迟延履行期间债务利息 (delayed performance interest)

### 迟延履行期间债务利息 (Delayed Performance Interest)
Double-rate interest for judgment debts with expired deadlines.
**Rate**: Fixed daily 0.0175% (万分之1.75)
**Classification**: 劣后债权 (Subordinated Debt)
**Prerequisites**: Judgment debt + Expired deadline + Creditor declared

### 对账单 (Reconciliation Statement / Statement of Account)
Document reconciling account balances between parties.
**If signed by debtor**: Strong statute interruption evidence.
**Hierarchy**: Bilateral confirmation (higher than unilateral evidence).

### 担保债权 (Secured Claim)
Claim backed by collateral or guarantee.
**Priority**: For secured portion (within collateral value)

### 到期日 (Due Date / Maturity Date)
Date payment or performance is due.
**Start of overdue**: Day after due date.

### 调解书 (Mediation Agreement / Court Mediation)
Court-mediated settlement agreement.
**Effect**: Same as judgment once effective.
**Hierarchy**: Legal document (highest level).

### 独立债权关系 (Independent Debt Relationship)
Each independent contract, judgment, or legal basis creating separate debt.
**Importance**: Each requires separate analysis.

## F-J

### 发票 (Invoice / Fapiao)
Tax invoice documenting transaction.
**Evidence Value**: Supports contract performance, but unilateral.

### 法定代表人 (Legal Representative)
Person legally representing a company.
**Authority**: Can bind company to agreements.

### 法律文书 (Legal Document)
Court judgments, mediations, arbitrations with legal effect.
**Hierarchy**: Highest evidence level, supersedes all contracts.

### 费用类 (Cost Items)
Recoverable expenses for realizing claim.
**Examples**: Attorney fees, court fees, preservation fees (if awarded).
**Classification**: Usually ordinary debt.

### 复利 (Compound Interest)
Interest calculated on principal plus previously accrued interest.
**Requirement**: MUST have explicit contractual basis.

### 工程款 (Construction/Project Payment)
Payment for construction or engineering services.

### 共益债务 (Common Benefit Debt)
Debts benefiting all creditors in bankruptcy proceedings.
**Priority**: Before all other debts.

### 还款承诺书 (Payment Promise Letter)
Debtor's written promise to repay.
**Effect**: Statute interruption (debt acknowledgment).

### 合同 (Contract)
Agreement between parties creating legal obligations.
**Types**: Sales, loan, service, construction, lease, etc.

### 加倍部分 (Double Portion)
The additional interest portion in delayed performance interest (beyond regular interest).
**Classification**: Subordinated debt.

### 加速到期 (Acceleration)
Contract clause allowing creditor to demand immediate full payment upon breach.
**Effect on Statute**: May change statute start date to earlier.

### 建设工程 (Construction Engineering)
Construction projects and engineering work.

### 借款合同 (Loan Contract / Loan Agreement)
Contract where one party lends money to another.
**Interest**: Usually contractual obligation, not penalty.

### 结算单 (Settlement Statement)
Document settling final amounts owed.
**Hierarchy**: Bilateral confirmation, supersedes prior performance evidence.
**Effect**: Often conclusive on amount if signed by both parties.

### 就低原则 (Lower Bound Rule)
When calculation > declaration, use declared amount.
**Rationale**: Respect creditor's self-limitation.

### 就无原则 (Non-Existence Rule)
Items not declared by creditor are NOT included in confirmation.
**Rationale**: Debt review is verification, not claim generation.

## L-P

### 劣后债权 (Subordinated Debt)
Debts repaid last, after ordinary claims satisfied.
**Examples**: Delayed performance interest (加倍部分), excessive penalties, shareholder claims.

### 利息 (Interest)
Derivative amounts based on principal, time, or breach.
**Types**: Loan interest, overdue interest, delayed performance interest.
**Classification**: 利息类项目 (Interest Items).
**Note**: 违约金 (penalties) classify as interest, NOT "other".

### 履行期限 (Performance Period / Deadline)
Time limit for fulfilling contractual obligations.
**Importance**: Determines overdue start date, statute start date.

### LPR (Loan Prime Rate / 贷款市场报价利率)
Market-based benchmark interest rate in China.
**Terms**: 1-year LPR, 5-year+ LPR.
**Selection**: Based on debt period (≤5y → 1y; >5y → 5y+).

### 律师费 (Attorney Fees)
Legal fees for pursuing claim.
**Recoverability**: Only if contractually agreed or awarded by judgment.

### 买卖合同 (Sales Contract / Purchase Agreement)
Contract for sale and purchase of goods.

### 民事调解书 (Civil Mediation Agreement)
See 调解书.

### 普通债权 (Ordinary Debt / Unsecured Claim)
Standard bankruptcy claims without priority or subordination.
**Examples**: Unsecured contract debts, principal, interest, costs.

### 票据 (Negotiable Instrument)
Bills, notes, checks with negotiable nature.

### 破产费用 (Bankruptcy Costs / Administration Costs)
Costs of bankruptcy proceedings.
**Priority**: Before all other debts.

## Q-Z

### 确认书 (Confirmation Letter / Acknowledgment Letter)
Letter confirming debt existence and amount.
**If signed by debtor**: Statute interruption (debt acknowledgment).

### 仁裁裁决 (Arbitration Award)
Arbitration tribunal's decision.
**Effect**: Same as judgment once effective.
**Hierarchy**: Legal document (highest level).

### 融资租赁 (Finance Lease / Financial Leasing)
Lease arrangement with financing component.
**Interest**: Implicit interest in lease payments.

### 申报债权 (Declared Claim / Filed Claim)
Amount and categories creditor claims in bankruptcy.
**Source**: Creditor's declaration form.
**Verification**: Debt review process verifies declared claims.

### 生效法律文书 (Effective Legal Document)
Judgment, mediation, or arbitration that has legal effect.
**Effective Date**: When document becomes legally binding.

### 实质重于形式 (Substance Over Form)
Focus on economic reality, not just document labels.
**Application**: Amount breakdown, relationship classification.

### 时效 (Statute of Limitations / Prescription)
Time limit for enforcing legal rights.
**Types**: 诉讼时效 (general statute), 执行时效 (execution statute).

### 诉讼时效 (Statute of Limitations for Litigation)
Period for filing lawsuit.
**Periods**: 2 years (old law) or 3 years (new law), use transition rule.

### 停止计息日 (Interest Stop Date)
Date interest calculation stops.
**Formula**: Bankruptcy filing date - 1 day.
**Example**: Filing = 2025-05-12 → Stop = 2025-05-11.

### 统一社会信用代码 (Unified Social Credit Code)
18-digit identifier for Chinese enterprises.

### 违约金 (Penalty / Liquidated Damages)
Amount payable for contract breach.
**Cap**: Cannot exceed 4× LPR.
**Classification**: 利息 (interest), NOT "其他" (other).

### 无担保债权 (Unsecured Claim)
Claim without collateral backing. Synonym: 普通债权.

### 物权担保 (Property Lien / Security Interest)
Right in property securing debt repayment.

### 希望债权 (Priority Debt / Preferred Claim)
Debt with statutory priority in bankruptcy.
**Examples**: Employee wages, individual tax/insurance, secured claims.

### 欠款 (Amount Owed / Outstanding Debt)
General term for unpaid amounts.

### 欠条 (IOU / Promissory Note)
Written acknowledgment of debt.
**Evidence Value**: Strong if debtor signed, especially for statute interruption.

### 租赁合同 (Lease Contract)
Contract for renting property or equipment.

### 执行时效 (Execution Statute / Enforcement Statute)
Time limit for applying to enforce judgment.
**Period**: 2 years (fixed, not 3).
**Applicable to**: Only judgment/mediation/arbitration debts.

### 质保金 (Quality Guarantee Deposit / Retention Money)
Amount retained to ensure work quality.
**Nature**: Principal (part of contract price).

### 中断 (Interruption)
Event causing statute period to restart.
**Events**: Demand, acknowledgment, lawsuit filing.

### 中止 (Suspension)
Event pausing statute period.
**Conditions**: Force majeure in last 6 months.
**Effect**: Period extends by duration of suspension.

### 证据 (Evidence)
Materials proving facts.
**Types**: Contracts, invoices, judgments, statements, bank records.

### 债权 (Claim / Debt)
Right to payment from debtor.

### 债权人 (Creditor)
Party owed money.

### 债务人 (Debtor)
Party owing money. In bankruptcy: the bankrupt enterprise.

### 真实性 (Authenticity)
Genuineness of evidence or information.

### 追偿权 (Right of Recourse)
Right to recover from another after payment.

## Abbreviations and Acronyms

**LPR**: Loan Prime Rate (贷款市场报价利率)
**1y LPR**: 1-year LPR (1年期LPR)
**5y LPR**: 5-year+ LPR (5年期以上LPR)

## Key Term Classifications

### By Debt Priority
- 优先债权 (Priority Debt)
- 普通债权 (Ordinary Debt)
- 劣后债权 (Subordinated Debt)

### By Debt Nature
- 本金类 (Principal Items)
- 利息类 (Interest Items)
- 费用类 (Cost Items)

### By Legal Relationship
- 买卖合同 (Sales Contract)
- 借款合同 (Loan Contract)
- 建设工程合同 (Construction Contract)
- 服务/劳务合同 (Service Contract)
- 租赁合同 (Lease Contract)
- 票据关系 (Negotiable Instrument)
- 法律文书确认类 (Legal Document Confirmed)
- 其他 (Other)

### Evidence Hierarchy Levels
1. 生效法律文书 (Effective Legal Documents)
2. 双方确认文件 (Bilateral Confirmations)
3. 合同及补充协议 (Contracts and Amendments)
4. 单方证据 (Unilateral Evidence)

## Usage Notes

**Chinese-English Variations**:
- Multiple English terms may translate same Chinese term (e.g., 债权 = claim/debt/receivable)
- Context determines appropriate English translation
- Legal terms should preserve technical accuracy

**Professional Usage**:
- Use precise legal terminology
- Maintain consistency within documents
- Explain complex terms when first mentioned
- Follow client's preferred terminology

**Common Errors**:
- Classifying 违约金 as "其他" instead of "利息"
- Confusing 普通债权 with 优先债权
- Mixing 诉讼时效 and 执行时效
- Using 债权人 when should use 申报人 (client preference)

## Quick Reference

**Critical Dates**:
- 破产受理日期: Bankruptcy filing date (lifeline-level critical)
- 停止计息日期: Interest stop date (= filing date - 1)

**Core Principles**:
- 就低原则: Lower Bound Rule
- 就无原则: Non-Existence Rule
- 实质重于形式: Substance Over Form

**Interest Types**:
- 借款利息: Loan interest (contractual)
- 逾期利息: Overdue interest
- 迟延履行利息: Delayed performance interest (劣后)
- 复利: Compound interest (requires explicit basis)

**Rate Caps**:
- Private lending: 4× LPR maximum
- Delayed performance: 0.0175% daily (fixed)

**For detailed definitions and applications**: See other reference guides in this skill.
