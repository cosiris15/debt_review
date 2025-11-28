"""
LLM Configuration and Prompt Templates

Configures DeepSeek (OpenAI-compatible) as the LLM backend.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_llm() -> ChatOpenAI:
    """
    Get configured LLM instance.

    Uses DeepSeek API with OpenAI-compatible interface.
    """
    return ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_BASE_URL,
        temperature=0.1,  # Low temperature for consistent output
        max_tokens=8000,  # Enough for detailed reports
    )


# ============== System Prompts ==============

SYSTEM_PROMPT_BASE = """你是一位专业的破产债权审查专家。你的任务是协助审查债权人提交的债权申报材料。

核心原则：
1. 就低原则：当计算结果 > 申报金额时，以申报金额为准
2. 就无原则：债权人未申报的项目不予确认
3. 证据层级：法律文书 > 双方确认文件 > 合同 > 单方证据

关键日期：
- 破产受理日期：{bankruptcy_date}
- 停止计息日期：破产受理日前一日

注意事项：
- 严格基于材料内容进行分析，不得编造信息
- 金额计算必须精确，使用四舍五入
- 日期格式统一使用 YYYY-MM-DD
"""


FACT_CHECK_SYSTEM = SYSTEM_PROMPT_BASE + """

你当前的任务是【事实核查】阶段。

工作内容：
1. 提取债权申报书中的基本信息（债权人、债务人、申报金额）
2. 整理证据材料清单
3. 建立基本法律关系（借款、货款、担保等）
4. 梳理时间线

输出格式要求：
- 使用中文数字标题（一、二、三...）
- 不使用 Markdown 标题语法（## ）
- 金额使用逗号分隔（如：1,234,567.89元）
"""


ANALYSIS_SYSTEM = SYSTEM_PROMPT_BASE + """

你当前的任务是【债权分析】阶段。

工作内容：
1. 分析各项债权金额（本金、利息、违约金等）
2. 验证计算过程
3. 确定诉讼时效状态
4. 给出确认/暂缓/不予确认的建议

分析原则：
- 利息计算必须使用计算器工具，禁止手动计算
- 适用就低原则和就无原则
- 长期借款使用5年期LPR，短期借款使用1年期LPR

【重要】利息计算请求格式：
当需要计算利息时，请在报告中使用以下格式标记计算请求，系统将自动调用计算器执行：

【利息计算】本金: 金额, 起始日: YYYY-MM-DD, 类型: lpr/simple/delay, 倍数: 1.0

支持的计算类型：
- lpr: LPR浮动利率计算（需指定倍数，如1.0、1.3、1.5）
- simple: 固定利率计算（需指定利率，如: 利率: 4.35）
- delay: 迟延履行利息（自动使用1.75倍LPR）
- penalty: 罚息计算（需指定利率，上限24%）

示例：
【利息计算】本金: 1000000, 起始日: 2023-01-15, 类型: lpr, 倍数: 1.3
【利息计算】本金: 500000, 起始日: 2022-06-01, 类型: simple, 利率: 6.0

输出格式要求：
- 使用中文数字标题（一、二、三...）
- 包含详细的计算过程说明
- 明确列出确认金额和不予确认金额
"""


REPORT_SYSTEM = SYSTEM_PROMPT_BASE + """

你当前的任务是【报告整理】阶段。

工作内容：
1. 整合事实核查报告和债权分析报告
2. 生成标准化的审查意见表
3. 确保格式合规

格式要求（零容忍）：
- 不使用 Markdown 标题语法（## ）- 使用中文数字（一、二、三）
- 不使用 bullet 列表（- ）- 使用完整句子
- 不使用加粗语法（** ）
- 报告应读起来像正式法律文书
"""


# ============== Prompt Creators ==============

def create_fact_check_prompt(
    creditor_name: str,
    materials_path: str,
    bankruptcy_date: str,
    debtor_name: str
) -> list:
    """Create prompt for fact-checking stage."""

    system = FACT_CHECK_SYSTEM.format(bankruptcy_date=bankruptcy_date)

    human = f"""请对以下债权人的申报材料进行事实核查：

债权人名称：{creditor_name}
债务人名称：{debtor_name}
材料路径：{materials_path}
破产受理日期：{bankruptcy_date}

请按照以下结构输出事实核查报告：

一、基本信息
（债权人、债务人、联系方式等）

二、申报金额概况
（本金、利息、违约金分项列明）

三、证据材料清单
（按时间顺序列明所有材料）

四、法律关系分析
（识别基础法律关系类型）

五、时间线梳理
（重要事件按时间排列）

六、初步发现
（需要在分析阶段重点关注的问题）
"""

    return [
        SystemMessage(content=system),
        HumanMessage(content=human)
    ]


def create_analysis_prompt(
    creditor_name: str,
    fact_check_report: str,
    bankruptcy_date: str,
    interest_stop_date: str,
    declared_amounts: Dict[str, Optional[float]]
) -> list:
    """Create prompt for analysis stage."""

    system = ANALYSIS_SYSTEM.format(bankruptcy_date=bankruptcy_date)

    amounts_str = ""
    if declared_amounts.get("principal"):
        amounts_str += f"- 本金：{declared_amounts['principal']:,.2f}元\n"
    if declared_amounts.get("interest"):
        amounts_str += f"- 利息：{declared_amounts['interest']:,.2f}元\n"
    if declared_amounts.get("total"):
        amounts_str += f"- 合计：{declared_amounts['total']:,.2f}元\n"

    human = f"""请对以下债权进行详细分析：

债权人名称：{creditor_name}
破产受理日期：{bankruptcy_date}
停止计息日期：{interest_stop_date}

申报金额：
{amounts_str if amounts_str else "（待从材料中提取）"}

事实核查报告：
{fact_check_report}

请按照以下结构输出债权分析报告：

一、债权金额分解
（逐项分析本金、利息、违约金等）

二、利息计算验证
（说明计算方法和结果，注明需使用计算器工具）

三、诉讼时效分析
（判断是否超过诉讼时效）

四、担保情况分析
（如有担保，分析担保效力）

五、审查结论
（给出各项金额的确认/暂缓/不予确认建议）

六、确认金额汇总
| 项目 | 申报金额 | 确认金额 | 差异说明 |
"""

    return [
        SystemMessage(content=system),
        HumanMessage(content=human)
    ]


def create_report_prompt(
    creditor_name: str,
    fact_check_report: str,
    analysis_report: str,
    debtor_name: str,
    bankruptcy_date: str
) -> list:
    """Create prompt for report organization stage."""

    system = REPORT_SYSTEM.format(bankruptcy_date=bankruptcy_date)

    human = f"""请整合以下两份报告，生成标准化的债权审查意见表：

债权人名称：{creditor_name}
债务人名称：{debtor_name}
破产受理日期：{bankruptcy_date}

=== 事实核查报告 ===
{fact_check_report}

=== 债权分析报告 ===
{analysis_report}

请按照以下格式生成最终审查意见表：

【格式要求】
- 不使用 ## 标题语法，使用中文数字（一、二、三）
- 不使用 - 列表，使用完整句子
- 不使用 ** 加粗
- 像正式法律文书一样书写

一、债权人基本情况

二、债权申报情况

三、证据材料审查情况

四、债权审查意见
（明确列出各项金额的确认意见）

五、特别说明
（如有需要特别说明的事项）

审查日期：{bankruptcy_date}
"""

    return [
        SystemMessage(content=system),
        HumanMessage(content=human)
    ]
