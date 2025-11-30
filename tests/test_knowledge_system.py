"""
Tests for the Knowledge Management System

Validates:
1. KnowledgeManager singleton and registry
2. Knowledge file loading and caching
3. LPR data integration
4. Dynamic prompt building
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.knowledge import get_knowledge_manager
from app.knowledge.loader import KnowledgeManager
from app.knowledge.schemas import KnowledgeItem, LPRData


class TestKnowledgeManager:
    """Tests for KnowledgeManager core functionality."""

    def test_singleton_pattern(self):
        """Verify KnowledgeManager is a singleton."""
        km1 = get_knowledge_manager()
        km2 = get_knowledge_manager()
        assert km1 is km2, "KnowledgeManager should be a singleton"

    def test_registry_populated(self):
        """Verify registry is populated with expected modules."""
        km = get_knowledge_manager()
        categories = km.list_categories()

        expected_categories = [
            'foundations',
            'calculations',
            'fact_checking',
            'analysis',
            'report',
            'legal_standards'
        ]

        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"

    def test_list_knowledge_foundations(self):
        """Verify foundations module has expected files."""
        km = get_knowledge_manager()
        items = km.list_knowledge('foundations')

        assert len(items) > 0, "Foundations should have knowledge items"

        # Check for core_principles
        ids = [item['id'] for item in items]
        assert 'core_principles' in ids, "core_principles should exist"

    def test_cache_stats(self):
        """Verify cache statistics are available."""
        km = get_knowledge_manager()
        stats = km.get_cache_stats()

        assert 'size' in stats
        assert 'max_size' in stats
        assert 'ttl_seconds' in stats


class TestKnowledgeLoading:
    """Tests for knowledge file loading."""

    @pytest.mark.asyncio
    async def test_load_single_knowledge(self):
        """Test loading a single knowledge item."""
        km = get_knowledge_manager()
        knowledge = await km.get_knowledge('foundations', 'core_principles')

        assert knowledge is not None, "Should load core_principles"
        assert knowledge.id == 'core_principles'
        assert knowledge.category == 'foundations'
        assert len(knowledge.content) > 0, "Content should not be empty"

    @pytest.mark.asyncio
    async def test_load_knowledge_for_stage(self):
        """Test loading knowledge for a workflow stage."""
        km = get_knowledge_manager()

        # Load for analysis stage
        items = await km.get_knowledge_for_stage(
            stage='analysis',
            token_budget=3000,
            include_advanced=False
        )

        assert len(items) > 0, "Should load some knowledge for analysis stage"

        # All items should be applicable to analysis
        for item in items:
            assert item.applies_to_stage('analysis'), \
                f"{item.id} should apply to analysis stage"

    @pytest.mark.asyncio
    async def test_token_budget_respected(self):
        """Test that token budget limits are respected."""
        km = get_knowledge_manager()

        # Load with very small budget
        items_small = await km.get_knowledge_for_stage(
            stage='analysis',
            token_budget=500,
            include_advanced=False
        )

        # Load with larger budget
        items_large = await km.get_knowledge_for_stage(
            stage='analysis',
            token_budget=5000,
            include_advanced=False
        )

        # Smaller budget should load fewer or equal items
        assert len(items_small) <= len(items_large), \
            "Smaller budget should not load more items"

    @pytest.mark.asyncio
    async def test_force_reload(self):
        """Test force reload bypasses cache."""
        km = get_knowledge_manager()

        # Load once
        knowledge1 = await km.get_knowledge('foundations', 'core_principles')

        # Load again with force reload
        knowledge2 = await km.get_knowledge(
            'foundations',
            'core_principles',
            force_reload=True
        )

        assert knowledge1 is not None
        assert knowledge2 is not None
        # Content should be same (assuming file didn't change)
        assert knowledge1.content == knowledge2.content


class TestLPRData:
    """Tests for LPR data loading."""

    @pytest.mark.asyncio
    async def test_load_lpr_rates(self):
        """Test loading LPR rates from YAML."""
        km = get_knowledge_manager()
        lpr_data = await km.get_lpr_rates()

        assert lpr_data is not None
        assert isinstance(lpr_data, LPRData)
        assert len(lpr_data.rates) > 0, "Should have LPR rates"

    @pytest.mark.asyncio
    async def test_lpr_rate_structure(self):
        """Test LPR rate data structure."""
        km = get_knowledge_manager()
        lpr_data = await km.get_lpr_rates()

        # Check first rate entry
        if lpr_data.rates:
            first_rate = lpr_data.rates[0]
            assert first_rate.date is not None
            assert first_rate.lpr_1y > 0
            assert first_rate.lpr_5y > 0

    def test_calculator_uses_yaml_lpr(self):
        """Test that calculator loads LPR from YAML."""
        from app.tools.calculator import LPR_DATA, load_lpr_data_from_yaml

        # LPR_DATA should be loaded from YAML
        yaml_data = load_lpr_data_from_yaml()

        assert len(yaml_data) > 0, "Should load LPR data"
        assert len(LPR_DATA) == len(yaml_data), "Module LPR_DATA should match"


class TestPromptBuilding:
    """Tests for dynamic prompt building."""

    @pytest.mark.asyncio
    async def test_build_system_prompt(self):
        """Test building system prompt with dynamic knowledge."""
        try:
            from app.agents.llm import build_system_prompt
        except ImportError:
            pytest.skip("langchain_openai not installed")

        prompt = await build_system_prompt(
            stage='analysis',
            bankruptcy_date='2024-01-15',
            token_budget=2000,
            include_advanced=False
        )

        assert len(prompt) > 0, "Prompt should not be empty"
        assert '2024-01-15' in prompt, "Bankruptcy date should be in prompt"
        assert '审查知识库' in prompt, "Knowledge section header should be present"

    @pytest.mark.asyncio
    async def test_fact_check_prompt_async(self):
        """Test async fact-check prompt creation."""
        try:
            from app.agents.llm import create_fact_check_prompt_async
        except ImportError:
            pytest.skip("langchain_openai not installed")

        messages = await create_fact_check_prompt_async(
            creditor_name='测试债权人',
            materials_path='/test/path',
            bankruptcy_date='2024-01-15',
            debtor_name='测试债务人',
            use_dynamic_knowledge=True
        )

        assert len(messages) == 2, "Should have system and human messages"
        assert messages[0].content is not None
        assert messages[1].content is not None

    @pytest.mark.asyncio
    async def test_analysis_prompt_async(self):
        """Test async analysis prompt creation."""
        try:
            from app.agents.llm import create_analysis_prompt_async
        except ImportError:
            pytest.skip("langchain_openai not installed")

        messages = await create_analysis_prompt_async(
            creditor_name='测试债权人',
            fact_check_report='测试事实核查报告内容',
            bankruptcy_date='2024-01-15',
            interest_stop_date='2024-01-14',
            declared_amounts={'principal': 100000, 'interest': 5000},
            use_dynamic_knowledge=True
        )

        assert len(messages) == 2
        # Analysis should have knowledge loaded
        assert len(messages[0].content) > 500, "Should have substantial knowledge content"


class TestKnowledgeFormatting:
    """Tests for knowledge formatting."""

    @pytest.mark.asyncio
    async def test_format_full(self):
        """Test full format output."""
        km = get_knowledge_manager()
        items = await km.get_knowledge_for_stage('analysis', token_budget=1000)

        formatted = km.format_for_prompt(items, format_type='full')

        assert len(formatted) > 0
        assert '###' in formatted, "Full format should have headers"

    @pytest.mark.asyncio
    async def test_format_structured(self):
        """Test structured format output."""
        km = get_knowledge_manager()
        items = await km.get_knowledge_for_stage('analysis', token_budget=1000)

        formatted = km.format_for_prompt(items, format_type='structured')

        assert len(formatted) > 0
        assert '[' in formatted, "Structured format should have brackets"


class TestModuleIntegrity:
    """Tests for module file integrity."""

    def test_all_index_files_exist(self):
        """Verify all module _index.yaml files exist."""
        knowledge_dir = Path(__file__).parent.parent / 'app' / 'knowledge'

        expected_modules = [
            'foundations',
            'calculations',
            'fact_checking',
            'analysis',
            'report',
            'legal_standards'
        ]

        for module in expected_modules:
            index_path = knowledge_dir / module / '_index.yaml'
            assert index_path.exists(), f"Missing _index.yaml for {module}"

    def test_lpr_rates_file_exists(self):
        """Verify LPR rates YAML file exists."""
        lpr_path = Path(__file__).parent.parent / 'app' / 'knowledge' / 'calculations' / 'lpr_rates.yaml'
        assert lpr_path.exists(), "LPR rates file should exist"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
