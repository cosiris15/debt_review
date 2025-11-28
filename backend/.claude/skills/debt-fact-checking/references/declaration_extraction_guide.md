# Declaration Information Extraction Guide

## Purpose

This guide provides detailed standards for extracting and organizing declaration information from creditor submission materials. It ensures accurate recording of what creditors claim in their declaration forms.

## Core Principle: EXACT COPY RULE

**⚠️ CRITICAL**: You MUST strictly copy what the creditor actually filled in the declaration form without any subjective judgment, correction, or "improvement".

### What This Means

- **Copy amounts exactly**: If creditor wrote "100,000", record "100,000" - do NOT correct to "100,000.00"
- **Use creditor's category labels**: If creditor wrote "欠款" instead of "本金", use "欠款"
- **Preserve creditor's mistakes**: If creditor made an obvious error, record it as-is
- **Mark unfilled items**: If creditor left something blank, mark "[债权人未填写]"
- **Keep creditor's categorization**: If creditor put penalty in "其他" instead of standard category, record as placed

### Why This Matters

- Debt analyst will compare declaration vs. evidence to identify discrepancies
- Modifications blur the line between what creditor claimed vs. what you concluded
- Exact copies preserve the original申报状态 for later analysis

## Creditor Basic Information Extraction

### Enterprise Creditors

**Required Fields**:

| 项目 | 提取要求 | 数据来源 |
|------|---------|---------|
| 债权人全称 | 按营业执照准确填写，不得简称 | 营业执照 |
| 企业类型 | 有限责任公司/股份有限公司/其他 | 营业执照 |
| 注册地址 | 营业执照载明地址，完整录入 | 营业执照 |
| 法定代表人 | 姓名 | 营业执照 |
| 统一社会信用代码 | 18位代码，准确无误 | 营业执照 |
| 联系信息 | 电话、邮箱等 | 申报表 |

**Output Format**:
```markdown
| 项目 | 内容 |
|------|------|
| 债权人全称 | [完整企业名称] |
| 企业类型 | [类型] |
| 注册地址 | [完整地址] |
| 法定代表人 | [姓名] |
| 统一社会信用代码 | [18位代码] |
| 联系信息 | [电话、邮箱] |
```

### Individual Creditors

**Required Fields**:

| 项目 | 提取要求 | 数据来源 |
|------|---------|---------|
| 债权人姓名 | 按身份证准确填写 | 身份证 |
| 身份证号 | 18位号码 | 身份证 |
| 联系地址 | 详细地址 | 申报表 |
| 联系信息 | 电话、邮箱等 | 申报表 |

**Output Format**:
```markdown
| 项目 | 内容 |
|------|------|
| 债权人姓名 | [姓名] |
| 身份证号 | [18位号码] |
| 联系地址 | [详细地址] |
| 联系信息 | [电话、邮箱] |
```

### Agent/Representative Information

If creditor has an agent or representative:

| 项目 | 提取要求 |
|------|---------|
| 代理人姓名 | 完整姓名 |
| 代理人身份 | 律师/职员/其他 |
| 代理权限 | 特别授权/一般授权 |
| 联系信息 | 电话、邮箱 |

## Declared Debt Amount Breakdown

### ⚠️ CRITICAL RULE: Exact Copy of Declaration Form

**You MUST**:
1. Copy amounts EXACTLY as creditor filled in declaration form
2. Use creditor's ORIGINAL category labels (even if non-standard)
3. Record items in the POSITION creditor actually filled them
4. Mark "[债权人未填写]" if creditor left blank
5. Do NOT rearrange, correct, or "improve" creditor's entries

### Standard Declaration Form Categories

Most declaration forms have these categories:

| 类别 | 说明 |
|-----|------|
| 本金 | Principal amount |
| 利息 | Interest |
| 违约金 | Penalty |
| 损害赔偿金 | Damages |
| 实现债权费用 | Collection costs |
| 其他 | Other (creditor may put various items here) |
| **合计** | Total |

### Extraction Template

```markdown
### 申报债权构成表（严格照抄原则）

⚠️ **本表必须严格按照债权人在《债权申报表》中的实际填写内容完全照抄**

| 项目 | 申报金额 | 备注 |
|------|----------|------|
| 本金 | [金额]元 | [如未填写标注"债权人未填写"] |
| 利息 | [金额]元 | [如未填写标注"债权人未填写"] |
| 违约金 | [金额]元 | [如未填写标注"债权人未填写"] |
| 损害赔偿金 | [金额]元 | [如未填写标注"债权人未填写"] |
| 实现债权费用 | [金额]元 | [如未填写标注"债权人未填写"] |
| 其他 | [金额]元 | [说明具体项目，如未填写标注"债权人未填写"] |
| **合计** | [总额]元 | |
```

### Common Scenarios and Handling

**Scenario 1: Creditor Uses Non-Standard Labels**
- Example: Creditor writes "欠款" instead of "本金"
- ✅ **Correct**: Record as creditor wrote: "欠款: XXX元"
- ❌ **Wrong**: Change to standard "本金: XXX元"

**Scenario 2: Creditor Puts Standard Item in "Other"**
- Example: Creditor puts penalty under "其他" instead of "违约金"
- ✅ **Correct**: Record under "其他" with note "债权人填写为违约金XXX元"
- ❌ **Wrong**: Move to "违约金" category

**Scenario 3: Creditor Leaves Standard Category Blank**
- Example: "利息" field is empty
- ✅ **Correct**: Mark "[债权人未填写]"
- ❌ **Wrong**: Fill in "0元" or calculate yourself

**Scenario 4: Creditor's Total Doesn't Match Sum**
- Example: Individual items sum to 100万 but creditor wrote 110万 as total
- ✅ **Correct**: Record both exactly as written, note discrepancy in备注
- ❌ **Wrong**: Correct the total to match sum

**Scenario 5: Creditor Fills Same Item Twice**
- Example: "利息" filled as 5万, and also under "其他: 利息5万"
- ✅ **Correct**: Record both exactly as creditor filled
- ❌ **Wrong**: Consolidate or remove duplicate

## Debt Classification Recording

### Standard Debt Classification Categories

Chinese bankruptcy law recognizes:

| 债权性质 | 说明 | 典型例子 |
|---------|------|---------|
| 优先债权 | Priority claims | 有财产担保的债权 |
| 普通债权 | Ordinary claims | 一般合同债权 |
| 劣后债权 | Subordinated claims | 股东借款等 |

### ⚠️ EXACT COPY RULE for Classification

**You MUST**:
1. Record EXACTLY what creditor checked on declaration form
2. If creditor checked nothing, mark "[债权人未勾选债权性质]"
3. If creditor checked multiple categories, record ALL checked boxes
4. Do NOT make your own judgment about correct classification

### Extraction Template

```markdown
### 债权性质分类表（严格照抄原则）

| 债权性质 | 申报金额 | 备注 |
|----------|----------|------|
| 优先债权 | [金额]元 | [如未勾选标注"债权人未勾选"] |
| 普通债权 | [金额]元 | [如未勾选标注"债权人未勾选"] |
| 劣后债权 | [金额]元 | [如未勾选标注"债权人未勾选"] |

说明：[如债权人在"其他"栏填写，完整摘录债权人填写内容]
```

### Common Scenarios

**Scenario 1: Creditor Checks Nothing**
```markdown
| 债权性质 | 申报金额 | 备注 |
|----------|----------|------|
| 优先债权 | [债权人未勾选] | |
| 普通债权 | [债权人未勾选] | |
| 劳动债权 | [债权人未勾选] | |
```

**Scenario 2: Creditor Checks Multiple Categories**
- Example: Creditor checks both "优先债权100万" AND "普通债权100万"
- ✅ **Correct**: Record both exactly as checked
- Note: "债权人同时勾选了两个性质，均记录"

**Scenario 3: Creditor Checks Wrong Category (in your opinion)**
- Example: You believe it's ordinary debt, but creditor checked "labor debt"
- ✅ **Correct**: Record what creditor checked with note "债权人勾选为劳动债权"
- ❌ **Wrong**: Change to what you think is correct

## Security Information Recording

### What to Extract

If creditor claims secured debt:

| 项目 | 提取内容 |
|------|---------|
| 担保类型 | 抵押/质押/保证/其他 |
| 担保物/担保人 | 具体描述 |
| 担保金额 | 金额 |
| 担保合同 | 合同编号/签订日期 |

### Recording Principle

**Copy creditor's description EXACTLY**:
- If creditor provides detailed description, copy in full
- If creditor provides vague description, copy as-is
- If creditor leaves blank, mark "[债权人未填写]"

### Example Format

```markdown
### 担保情况

根据债权人申报：[完全按照债权人填写内容摘录]

如债权人未填写担保情况，标注"[债权人未填写担保信息]"
```

## Quality Control Checklist

Before submitting declaration extraction section:

- [ ] All amounts copied EXACTLY from declaration form (no rounding, no corrections)
- [ ] All category labels use creditor's ORIGINAL wording
- [ ] Items recorded in creditor's ACTUAL placement (not rearranged)
- [ ] Blank fields marked "[债权人未填写]"
- [ ] Checked boxes recorded exactly (not adjusted based on your judgment)
- [ ] No subjective corrections or "improvements" made
- [ ] Discrepancies noted but not "fixed"
- [ ] All unique creditor descriptions preserved verbatim

## Common Mistakes to Avoid

1. **❌ "Fixing" creditor's categorization**
   - Creditor puts penalty in "other" → You move to "penalty"

2. **❌ Standardizing creditor's labels**
   - Creditor writes "欠款" → You change to "本金"

3. **❌ Calculating missing totals**
   - Creditor leaves total blank → You calculate and fill in

4. **❌ Correcting obvious errors**
   - Creditor's sum doesn't match total → You adjust one of them

5. **❌ Consolidating duplicate entries**
   - Creditor lists same item twice → You merge them

6. **❌ Removing "unreasonable" entries**
   - Creditor claims impossible amount → You reduce it

**Remember**: Your job is to record what creditor CLAIMED, not to correct or judge it. The debt analyst will later compare claims vs. evidence to identify issues.
