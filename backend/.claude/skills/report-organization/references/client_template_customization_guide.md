# Client Template Customization Guide

## Purpose

This guide explains how to work with client-specific review opinion form templates, understand their requirements, and adapt debt review content to match different client preferences and formats.

## Part 1: Understanding Template Architecture

### Template Components

A complete review opinion form template typically contains:

1. **Metadata Section**:
   - Template version
   - Client name/code
   - Applicable project
   - Update date

2. **Structure Definition**:
   - Required sections (必填章节)
   - Optional sections (可选章节)
   - Section hierarchy and numbering

3. **Content Mapping Table**:
   - Which source report sections map to which template sections
   - What information goes where

4. **Format Specifications**:
   - Table formats
   - Heading styles
   - Numbering schemes
   - Writing style guidelines

5. **Example Content** (often):
   - Sample filled sections
   - Formatting examples
   - Terminology examples

### Template Types

**Type A: Detailed Analytical Template**:
- Includes extensive analysis sections
- Requires detailed reasoning for each determination
- May include full evidence timeline
- Often used for complex cases or litigation support

**Type B: Executive Summary Template**:
- Focuses on conclusions and key findings
- Minimal process description
- Highlights risks and recommendations
- Often used for board reports or senior management

**Type C: Standardized Checklist Template**:
- Structured as yes/no checklist items
- Systematic coverage of all review points
- Brief explanatory notes
- Often used for high-volume processing

## Part 2: Reading and Interpreting Templates

### Step 1: Locate Template File

**Standard Location**: `templates/review_opinion_form_template.md`

**File Naming Pattern**:
- Single client: `review_opinion_form_template.md`
- Multiple clients: `[ClientCode]_review_opinion_form_template.md`

### Step 2: Extract Template Metadata

**Look for**:
```markdown
---
template_version: 2.1
client: [客户名称]
project: [项目名称]
last_updated: 2025-09-15
---
```

**Or in header**:
```markdown
# 债权审查意见表模板

**适用客户**: XX破产管理人
**模板版本**: v2.1
**更新日期**: 2025-09-15
```

### Step 3: Identify Section Structure

**Required Sections** (marked with ⭐ or "必填"):
```markdown
## ⭐ 一、债权人基本情况 (必填)
## ⭐ 二、申报债权情况 (必填)
## ⭐ 三、审查确认情况 (必填)
```

**Optional Sections** (marked with  ○ or "可选"):
```markdown
## ○ 四、特殊事项说明 (可选)
## ○ 五、风险提示 (可选)
```

### Step 4: Understand Content Mapping

**Content Mapping Table Example**:

| 模板章节 | 数据来源 | 具体取值 | 备注 |
|---------|---------|---------|------|
| 一、债权人基本情况 | 事实核查报告 | 第一节"债权人信息" | 完整抄录 |
| 二、申报债权情况 | 事实核查报告 | 第二节"申报情况" | 保持原始申报分类 |
| 三、金额分析 | 债权分析报告 | 第二节"金额项目拆解" | 以分析结论为准 |
| 四、审查确认情况 | 债权分析报告 | 第七节"审查确认情况" | 最终确认数据 |

**Flexible Mapping**: If template doesn't provide explicit mapping, use standard mapping from `report_consolidation_guide.md`.

### Step 5: Note Format Requirements

**Table Format Example**:
```markdown
**格式要求**:
- 表格标题：三号黑体
- 表头：四号宋体加粗
- 表格内容：小四号宋体
- 金额：右对齐，千位分隔符
- 日期：YYYY-MM-DD格式
```

**Heading Format Example**:
```markdown
**标题层级**:
一级标题：一、债权人基本情况
二级标题：（一）企业信息
三级标题：1. 企业名称
```

### Step 6: Understand Writing Style

**Style Guidelines Example**:
```markdown
**写作风格**:
- 语气：客观、专业、简洁
- 人称：第三人称（本案债权人、债务人）
- 术语：法律专业术语优先，必要时附简要说明
- 结论：明确、肯定（确认/暂缓确认）
```

## Part 3: Template Adaptation Strategies

### Strategy 1: Section Mapping

**When template structure differs from standard reports**:

**Example**:
```
Standard Report Structure:
├── 债权关系确认
├── 金额项目分析
├── 利息计算
└── 诉讼时效

Client Template Structure:
├── 债权基础
│   ├── 法律关系 (maps to: 债权关系确认)
│   └── 证据材料 (extract from fact-checking)
├── 金额确认
│   ├── 本金分析 (extract from 金额项目 - principal items)
│   ├── 利息计算 (maps to: 利息计算)
│   └── 费用审查 (extract from 金额项目 - cost items)
└── 法律风险
    └── 时效判断 (maps to: 诉讼时效)
```

**Approach**: Create mapping table, then extract and reorganize content accordingly.

### Strategy 2: Content Granularity Adjustment

**Detailed Template** (requires expansion):
```
Template requires: "详细说明利息计算的法律依据、计算公式、分段计算过程"

From debt analysis report (summary):
"以XXX元为基数，按LPR×1.5计算，结果XXX元"

Expanded for template:
"法律依据：《最高人民法院关于审理民间借贷案件适用法律若干问题的规定》
计算公式：利息 = 本金 × 日利率 × 天数
分段计算过程：
- 期间1（2023-01-01至2023-06-20）：适用LPR 3.65% × 1.5 = ...
- 期间2（2023-06-21至2025-05-11）：适用LPR 3.45% × 1.5 = ...
合计利息：XXX元"
```

**Summary Template** (requires condensation):
```
Template requires: "利息计算结果"

From debt analysis report (detailed):
[Multiple paragraphs with calculation steps]

Condensed for template:
"利息计算：基数XXX元，期间XXX至XXX，按LPR×1.5，结果XXX元。详见计算文件。"
```

### Strategy 3: Terminology Alignment

**When client uses specific terminology**:

| Standard Term | Client A Term | Client B Term |
|--------------|--------------|--------------|
| 债权人 | 申报人 | 债权申报方 |
| 确认金额 | 认定金额 | 审定金额 |
| 普通债权 | 一般债权 | 无担保债权 |
| 劣后债权 | 次级债权 | 后顺位债权 |

**Approach**: Use template's terminology consistently throughout the report, even if it differs from technical reports.

### Strategy 4: Format Standardization

**Table Format Adaptation**:

**Standard Table**:
```markdown
| 项目 | 申报金额 | 确认金额 |
|------|----------|----------|
| 本金 | 100,000 | 100,000 |
```

**Client Template A** (vertical layout):
```markdown
**本金审查**
- 申报金额：100,000元
- 确认金额：100,000元
- 确认依据：[...]
```

**Client Template B** (detailed table):
```markdown
| 序号 | 项目类别 | 项目明细 | 申报金额(元) | 证据支持 | 确认金额(元) | 差异说明 |
|------|---------|---------|-------------|---------|-------------|---------|
| 1 | 本金 | XX合同货款 | 100,000 | 充分 | 100,000 | 无差异 |
```

**Approach**: Restructure data to fit client's table format.

## Part 4: Client-Specific Requirements

### Requirement Type 1: Risk Alert Emphasis

**Some clients require prominent risk flagging**:

**Standard Approach**:
```
审查意见：经审查，确认债权XXX元。

特别说明：该债权已超过诉讼时效...
```

**Client Requirement**:
```
⚠️ 重大风险提示 ⚠️

该债权存在以下风险：
1. 已超过诉讼时效
2. 风险等级：高
3. 建议：暂缓确认

审查意见：[...]
```

**Adaptation**: Add dedicated risk section at beginning, use visual markers.

### Requirement Type 2: Comparative Analysis

**Some clients require declared vs. confirmed comparison**:

**Standard Approach**:
```
确认金额：XXX元
```

**Client Requirement**:
```
申报与确认对比：

| 类别 | 申报金额 | 确认金额 | 差异 | 差异率 | 原因 |
|------|----------|----------|------|--------|------|
| 本金 | 100,000 | 100,000 | 0 | 0% | 完全确认 |
| 利息 | 50,000 | 45,000 | -5,000 | -10% | 计算调整 |
| 合计 | 150,000 | 145,000 | -5,000 | -3.3% | |
```

**Adaptation**: Calculate differences and percentages, add explanatory column.

### Requirement Type 3: Legal Citation Standards

**Some clients require specific citation formats**:

**Standard Approach**:
```
根据《企业破产法》规定...
```

**Client Requirement A** (full citation):
```
根据《中华人民共和国企业破产法》（2006年8月27日第十届全国人民代表大会常务委员会第二十三次会议通过）第四十八条规定...
```

**Client Requirement B** (footnote style):
```
根据《企业破产法》¹规定...

---
¹《中华人民共和国企业破产法》第四十八条
```

**Adaptation**: Follow client's citation style guide.

### Requirement Type 4: Signature and Seal Sections

**Some templates include signature areas**:

```markdown
---

**审查人员**：_______________   **日期**：_______

**复核人员**：_______________   **日期**：_______

**负责人**：_________________   **日期**：_______

（本页以下空白）
```

**Handling**:
- Include in template as specified
- Leave signature lines blank in digital version
- Note if physical signatures required for delivery

## Part 5: Template Customization Workflow

### Step-by-Step Process

**Step 1: Template Analysis**
```
□ Read template file completely
□ Identify all required sections
□ Note optional sections
□ Extract content mapping table
□ Understand format specifications
□ Note writing style requirements
```

**Step 2: Content Preparation**
```
□ Extract all required content from source reports
□ Organize content per mapping table
□ Prepare any additional content needed for optional sections
□ Calculate any derived metrics (differences, percentages, etc.)
```

**Step 3: Structure Creation**
```
□ Create report skeleton per template structure
□ Add all section headings
□ Include placeholder tables
□ Set up numbering scheme
```

**Step 4: Content Population**
```
□ Fill required sections systematically
□ Add optional sections where relevant
□ Apply format specifications
□ Use template terminology consistently
```

**Step 5: Style Application**
```
□ Apply heading formats
□ Format tables per specifications
□ Apply writing style guidelines
□ Use specified citation formats
```

**Step 6: Quality Check**
```
□ All required sections completed
□ Format matches template
□ Terminology consistent
□ Data accurate
□ No template placeholders remaining
```

## Part 6: Managing Multiple Client Templates

### Template Repository Organization

**Directory Structure**:
```
templates/
├── review_opinion_form_template.md (default)
├── ClientA_review_opinion_form_template.md
├── ClientB_review_opinion_form_template.md
└── template_comparison.md (optional)
```

### Template Selection Logic

**Selection Criteria**:
1. Check for project-specific template in config
2. Check for client-specific template
3. Fall back to default template

**Example**:
```python
# Pseudocode
project = load_config('.processing_config.json')
client_code = project['client']

if exists(f'{client_code}_review_opinion_form_template.md'):
    template = load(f'{client_code}_review_opinion_form_template.md')
else:
    template = load('review_opinion_form_template.md')  # default
```

### Template Version Control

**Track template changes**:
```markdown
## 模板更新记录

### v2.1 (2025-09-15)
- 新增"风险提示"必填章节
- 调整表格格式要求
- 更新利息计算说明要求

### v2.0 (2025-08-01)
- 重构章节结构
- 简化内容映射表
- 新增写作风格指南
```

### Cross-Template Consistency

**When working with multiple clients**:
- Maintain content accuracy across all templates
- Adapt presentation, not substance
- Keep calculation methodologies consistent
- Ensure legal conclusions remain unchanged

## Part 7: Error Prevention

### Common Template Mistakes

**Mistake 1: Using Wrong Template**
- ❌ Using Client A's template for Client B's project
- ✅ Verify client code and select corresponding template

**Mistake 2: Omitting Required Sections**
- ❌ Skipping sections marked "必填"
- ✅ Complete ALL required sections, even if brief

**Mistake 3: Format Inconsistency**
- ❌ Mixing formats (some tables per template, some not)
- ✅ Apply template format consistently throughout

**Mistake 4: Terminology Mixing**
- ❌ Using "债权人" when template uses "申报人"
- ✅ Use template's terminology consistently

**Mistake 5: Ignoring Style Guidelines**
- ❌ Using first person when template requires third person
- ✅ Follow template's writing style exactly

### Quality Assurance Checklist

**Pre-Application**:
```
□ Correct template selected
□ Template version verified
□ All requirements understood
```

**During Application**:
```
□ All required sections filled
□ Format specifications followed
□ Terminology consistent with template
□ Writing style matches template
```

**Post-Application**:
```
□ All sections complete
□ No template placeholders remain
□ Format validation passed
□ Content accuracy preserved
```

## Part 8: Template Troubleshooting

### Issue 1: Template Requirements Exceed Source Data

**Problem**: Template requires detailed breakdown not in source reports.

**Solution**:
- Use available data
- Mark missing items: "【数据不可得】"
- Provide reasonable explanation
- Continue processing

### Issue 2: Template Structure Incompatible with Content

**Problem**: Source reports have 3 debt relationships, template assumes single relationship.

**Solution**:
- Adapt template structure (add subsections)
- Or use consolidated tables
- Maintain all content
- Note adaptation in report

### Issue 3: Template Format Conflicts with Best Practices

**Problem**: Template requires format that reduces clarity.

**Solution**:
- **Priority**: Follow template (client preference)
- Add clarifying notes if needed
- Suggest template improvement to client (separate communication)
- Never deviate without authorization

### Issue 4: Template Version Outdated

**Problem**: Template references old legal standards or procedures.

**Solution**:
- Use current legal standards in content
- Follow template structure
- Note discrepancy to client
- Suggest template update

## Summary

**Template Customization Principles**:
1. **Client First**: Client template requirements override default practices
2. **Accuracy Preserved**: Adapt presentation, never change substance
3. **Complete Compliance**: Follow ALL template specifications
4. **Consistency**: Use template terminology and style throughout
5. **Traceability**: Maintain clear connection to source reports

**Golden Rule**: When in doubt, consult template documentation. If still unclear, ask client for clarification rather than guessing.

**For consolidation procedures**: See `report_consolidation_guide.md`
