"""
Direct LLM Integration Test

Tests LLM (DeepSeek) integration without full workflow.
Validates:
1. LLM connection
2. Knowledge loading
3. Prompt generation
4. Response quality
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.llm import (
    get_llm,
    get_fact_check_system,
    get_analysis_system,
    create_fact_check_prompt,
    create_analysis_prompt
)
from app.knowledge import get_knowledge_manager
from app.agents.templates import enforce_template_compliance, validate_report_format
from app.agents.checkpoints import QualityCheckpoints
from langchain_core.messages import SystemMessage, HumanMessage


# Test configuration
PROJECT_CONFIG = {
    "debtor_name": "上海欧卡罗家居有限公司",
    "bankruptcy_date": "2024-02-26",
    "interest_stop_date": "2024-02-25",
}

TEST_MATERIALS_PATH = Path("/Users/chenchu/Desktop/第1批债权")

# Creditor info from materials
MUCHEN_CREDITOR = {
    "name": "上海牧诚贸易有限公司",
    "materials_path": TEST_MATERIALS_PATH / "债权申报书-上海牧诚贸易有限公司.md",
    "declared_amounts": {
        "principal": 7610000.00,
        "interest": 342449.99,
        "court_fee": 32535.00,
        "preservation_fee": 5000.00,
        "delay_interest": 278500.92,
        "total": 8268485.91
    }
}


class TestLLMConnection:
    """Test LLM connection and basic functionality."""

    def test_llm_initialization(self):
        """Test that LLM can be initialized."""
        from app.core.config import settings

        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            pytest.skip("DEEPSEEK_API_KEY not configured")

        llm = get_llm()
        assert llm is not None
        assert llm.model_name == "deepseek-chat"

    @pytest.mark.asyncio
    async def test_simple_llm_call(self):
        """Test a simple LLM call."""
        from app.core.config import settings

        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            pytest.skip("DEEPSEEK_API_KEY not configured")

        llm = get_llm()

        messages = [
            SystemMessage(content="你是一个简洁的助手，用中文回答。"),
            HumanMessage(content="请用一句话回答：1+1等于几？")
        ]

        response = await llm.ainvoke(messages)

        assert response is not None
        assert response.content is not None
        assert "2" in response.content or "二" in response.content

        print(f"\nLLM Response: {response.content}")


class TestKnowledgeIntegration:
    """Test knowledge loading with LLM."""

    @pytest.mark.asyncio
    async def test_load_knowledge_for_prompt(self):
        """Test loading knowledge for fact-check stage."""
        km = get_knowledge_manager()

        items = await km.get_knowledge_for_stage("fact_check", token_budget=2000)

        assert len(items) > 0

        # Format for prompt
        content = km.format_for_prompt(items, format_type='full')

        assert len(content) > 100
        assert "原则" in content or "证据" in content

        print(f"\nLoaded {len(items)} knowledge items, {len(content)} chars")

    @pytest.mark.asyncio
    async def test_dynamic_system_prompt(self):
        """Test dynamic system prompt building."""
        system_prompt = await get_fact_check_system(PROJECT_CONFIG["bankruptcy_date"])

        assert PROJECT_CONFIG["bankruptcy_date"] in system_prompt
        assert "事实核查" in system_prompt

        print(f"\nSystem prompt length: {len(system_prompt)} chars")


class TestFactCheckWithLLM:
    """Test fact-check stage with actual LLM."""

    @pytest.mark.asyncio
    async def test_fact_check_single_creditor(self):
        """
        Test fact-check for 上海牧诚贸易有限公司.

        This is the core E2E test - sends materials to LLM and validates response.
        """
        from app.core.config import settings

        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            pytest.skip("DEEPSEEK_API_KEY not configured")

        # Read materials
        materials_content = MUCHEN_CREDITOR["materials_path"].read_text(encoding='utf-8')

        # Get LLM
        llm = get_llm()

        # Build prompt
        system_prompt = await get_fact_check_system(PROJECT_CONFIG["bankruptcy_date"])

        human_prompt = f"""请对以下债权人的申报材料进行事实核查：

债权人名称：{MUCHEN_CREDITOR["name"]}
债务人名称：{PROJECT_CONFIG["debtor_name"]}
破产受理日期：{PROJECT_CONFIG["bankruptcy_date"]}

=== 债权申报材料 ===

{materials_content[:15000]}  # Limit content length

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

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        print("\n正在调用 DeepSeek API 进行事实核查...")
        print(f"材料长度: {len(materials_content)} 字符")

        # Call LLM
        response = await llm.ainvoke(messages)

        assert response is not None
        assert response.content is not None

        report = response.content

        print(f"\n=== 事实核查报告 ===")
        print(f"报告长度: {len(report)} 字符")
        print(f"\n{report[:2000]}...")  # Print first 2000 chars

        # Validate content
        assert "上海牧诚贸易有限公司" in report
        assert "7,610,000" in report or "761万" in report or "7610000" in report

        # Check format compliance
        validation = validate_report_format(report)
        print(f"\n格式验证: {'通过' if validation.passed else '未通过'}")
        if not validation.passed:
            print(f"违规项: {len(validation.violations)}")
            for v in validation.violations[:3]:
                print(f"  - {v.violation_type.value}: {v.content[:50]}")

        # Apply template enforcement
        compliant_report, _ = enforce_template_compliance(report)
        print(f"\n格式转换后长度: {len(compliant_report)} 字符")

        # Checkpoint validation
        checkpoints = QualityCheckpoints(
            bankruptcy_date=PROJECT_CONFIG["bankruptcy_date"],
            interest_stop_date=PROJECT_CONFIG["interest_stop_date"]
        )

        # Check for inference words
        inference_word = checkpoints._check_for_inference_words(compliant_report)
        if inference_word:
            print(f"\n警告: 发现推理词汇 '{inference_word}'")
        else:
            print("\n反编造检查: 通过")


class TestAnalysisWithLLM:
    """Test analysis stage with actual LLM."""

    @pytest.mark.asyncio
    async def test_analysis_with_fact_check_report(self):
        """
        Test analysis stage using a mock fact-check report.
        """
        from app.core.config import settings

        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            pytest.skip("DEEPSEEK_API_KEY not configured")

        # Mock fact-check report (simplified)
        fact_check_report = """一、基本信息

债权人：上海牧诚贸易有限公司
债务人：上海欧卡罗家居有限公司
统一社会信用代码：91310117MA1J273L7T

二、申报金额概况

申报债权总额：8,268,485.91元
其中：
本金：7,610,000.00元（预付货款）
利息：342,449.99元（按LPR1.5倍计算）
诉讼费：32,535.00元
保全费：5,000.00元
迟延履行利息：278,500.92元

三、证据材料清单

1. (2023)沪0118民初14562号民事判决书
2. (2023)沪0118执10429号执行裁定书
3. (2024)沪03破152号民事裁定书

四、法律关系分析

基础法律关系：买卖合同纠纷（采购合同）
债权人预付货款后，债务人未按约定供货，双方协商解除合同。
经法院判决确认债务人应返还预付款7,610,000元及相应利息。

五、时间线

2021-11-13：签订《采购合同》
2023-04-25：债权人起诉
2023-06-12：法院判决
2023-12-25：终结执行
2024-02-26：破产受理

六、初步发现

1. 已有生效判决，债权金额较为明确
2. 需验证利息计算是否符合破产停止计息规则
3. 迟延履行利息需核实计算期间是否超过破产受理日
"""

        # Get LLM
        llm = get_llm()

        # Build analysis prompt
        system_prompt = await get_analysis_system(PROJECT_CONFIG["bankruptcy_date"])

        declared_amounts = MUCHEN_CREDITOR["declared_amounts"]
        amounts_str = f"""- 本金：{declared_amounts['principal']:,.2f}元
- 利息：{declared_amounts['interest']:,.2f}元
- 合计：{declared_amounts['total']:,.2f}元"""

        human_prompt = f"""请对以下债权进行详细分析：

债权人名称：{MUCHEN_CREDITOR["name"]}
破产受理日期：{PROJECT_CONFIG["bankruptcy_date"]}
停止计息日期：{PROJECT_CONFIG["interest_stop_date"]}

申报金额：
{amounts_str}

事实核查报告：
{fact_check_report}

请按照以下结构输出债权分析报告：

一、债权金额分解
（逐项分析本金、利息、违约金等）

二、利息计算验证
（说明计算方法和结果）

三、诉讼时效分析
（判断是否超过诉讼时效）

四、担保情况分析
（如有担保，分析担保效力）

五、审查结论
（给出各项金额的确认/暂缓/不予确认建议）

六、确认金额汇总
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        print("\n正在调用 DeepSeek API 进行债权分析...")

        # Call LLM
        response = await llm.ainvoke(messages)

        assert response is not None

        report = response.content

        print(f"\n=== 债权分析报告 ===")
        print(f"报告长度: {len(report)} 字符")
        print(f"\n{report[:2000]}...")

        # Basic validation
        assert "本金" in report
        assert "利息" in report
        assert "确认" in report or "审查" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
