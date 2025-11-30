"""
Knowledge Loader

Core implementation of the knowledge management system.
Provides dynamic loading, caching, and formatting of knowledge for LangGraph nodes.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import logging
import yaml
import asyncio
from functools import lru_cache

from app.knowledge.schemas import KnowledgeItem, ModuleConfig, LPRRate, LPRData

logger = logging.getLogger(__name__)


class KnowledgeCache:
    """
    Knowledge cache with LRU eviction and TTL expiration.

    Supports hot-reload by detecting file changes through TTL expiration.
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 60):
        self._cache: Dict[str, KnowledgeItem] = {}
        self._access_order: List[str] = []
        self._max_size = max_size
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[KnowledgeItem]:
        """Get cached item, returns None if expired or not found"""
        if key not in self._cache:
            return None

        item = self._cache[key]

        # Check TTL expiration (enables hot-reload)
        if datetime.now() - item.last_loaded > self._ttl:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return None

        # Update access order (LRU)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return item

    def put(self, key: str, item: KnowledgeItem):
        """Add item to cache"""
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Evict least recently used
            if self._access_order:
                oldest = self._access_order.pop(0)
                self._cache.pop(oldest, None)

        self._cache[key] = item
        if key not in self._access_order:
            self._access_order.append(key)

    def invalidate(self, key: str = None):
        """Invalidate cache entry or entire cache"""
        if key:
            self._cache.pop(key, None)
            if key in self._access_order:
                self._access_order.remove(key)
        else:
            self._cache.clear()
            self._access_order.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl_seconds": self._ttl.total_seconds()
        }


class KnowledgeManager:
    """
    Central knowledge management system.

    Features:
    - Singleton pattern for global access
    - Supports Markdown (with YAML frontmatter) and pure YAML files
    - Caching with TTL for hot-reload support
    - Token budget management for LLM context
    - Stage-based knowledge filtering

    Usage:
        km = get_knowledge_manager()
        knowledge = await km.get_knowledge("foundations", "core_principles")
        items = await km.get_knowledge_for_stage("analysis", token_budget=3000)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._knowledge_dir = Path(__file__).parent
        self._cache = KnowledgeCache(max_size=100, ttl_seconds=60)
        self._registry: Dict[str, ModuleConfig] = {}
        self._initialized = True
        self._lpr_cache: Optional[LPRData] = None
        self._lpr_cache_time: Optional[datetime] = None

        # Scan and build registry
        self._scan_registry()

    def _scan_registry(self):
        """Scan all module directories and build registry from _index.yaml files"""
        for module_dir in self._knowledge_dir.iterdir():
            if not module_dir.is_dir():
                continue
            if module_dir.name.startswith('_') or module_dir.name.startswith('.'):
                continue
            if module_dir.name == '__pycache__':
                continue

            index_file = module_dir / '_index.yaml'
            if index_file.exists():
                try:
                    with open(index_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)

                    module_info = config_data.get('module', {})
                    loading = config_data.get('loading_strategy', {})

                    self._registry[module_dir.name] = ModuleConfig(
                        id=module_info.get('id', module_dir.name),
                        name=module_info.get('name', module_dir.name),
                        description=module_info.get('description', ''),
                        eager_load=loading.get('eager', False),
                        cache_enabled=loading.get('cache', True),
                        cache_ttl=loading.get('cache_ttl', 60),
                        files=config_data.get('files', [])
                    )
                    logger.info(f"Registered knowledge module: {module_dir.name}")
                except Exception as e:
                    logger.error(f"Failed to load index for {module_dir.name}: {e}")

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of file content for change detection"""
        if not file_path.exists():
            return ""
        try:
            return hashlib.md5(file_path.read_bytes()).hexdigest()
        except Exception:
            return ""

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from Markdown content.

        Returns:
            Tuple of (metadata dict, body content)
        """
        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        try:
            metadata = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return metadata or {}, body
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse frontmatter: {e}")
            return {}, content

    def _get_file_path(self, category: str, knowledge_id: str) -> Optional[Path]:
        """Get the file path for a knowledge item"""
        if category not in self._registry:
            return None

        module_config = self._registry[category]
        for file_config in module_config.files:
            if file_config.get('id') == knowledge_id:
                return self._knowledge_dir / category / file_config.get('path', '')

        # Fallback: try direct path
        direct_path = self._knowledge_dir / category / f"{knowledge_id}.md"
        if direct_path.exists():
            return direct_path

        return None

    def _load_knowledge_sync(self, category: str, knowledge_id: str) -> Optional[KnowledgeItem]:
        """Synchronously load knowledge from file"""
        file_path = self._get_file_path(category, knowledge_id)
        if not file_path or not file_path.exists():
            logger.warning(f"Knowledge file not found: {category}/{knowledge_id}")
            return None

        try:
            content = file_path.read_text(encoding='utf-8')
            metadata, body = self._parse_frontmatter(content)

            # Get file config for additional metadata
            file_config = {}
            if category in self._registry:
                for fc in self._registry[category].files:
                    if fc.get('id') == knowledge_id:
                        file_config = fc
                        break

            item = KnowledgeItem(
                id=knowledge_id,
                name=metadata.get('name', knowledge_id),
                category=category,
                content=body,
                metadata=metadata,
                token_estimate=metadata.get('token_estimate', len(body) // 4),
                applicable_stages=metadata.get('applicable_stages', []),
                priority=file_config.get('priority', metadata.get('priority', 99)),
                last_loaded=datetime.now(),
                file_hash=self._compute_file_hash(file_path)
            )

            # Cache if enabled
            cache_key = f"{category}/{knowledge_id}"
            self._cache.put(cache_key, item)

            return item

        except Exception as e:
            logger.error(f"Failed to load knowledge {category}/{knowledge_id}: {e}")
            return None

    async def get_knowledge(
        self,
        category: str,
        knowledge_id: str,
        force_reload: bool = False
    ) -> Optional[KnowledgeItem]:
        """
        Get a single knowledge item.

        Args:
            category: Knowledge category (foundations, calculations, etc.)
            knowledge_id: Knowledge item ID
            force_reload: Force reload from disk, bypassing cache

        Returns:
            KnowledgeItem or None if not found
        """
        cache_key = f"{category}/{knowledge_id}"

        # Check cache
        if not force_reload:
            cached = self._cache.get(cache_key)
            if cached:
                # Verify file hasn't changed
                file_path = self._get_file_path(category, knowledge_id)
                if file_path and self._compute_file_hash(file_path) == cached.file_hash:
                    return cached

        # Load from file (run in thread pool for async compatibility)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._load_knowledge_sync,
            category,
            knowledge_id
        )

    async def get_knowledge_for_stage(
        self,
        stage: str,
        token_budget: int = 4000,
        include_advanced: bool = False,
        categories: List[str] = None
    ) -> List[KnowledgeItem]:
        """
        Get all knowledge applicable to a workflow stage within token budget.

        Args:
            stage: Workflow stage (fact_check, analysis, report)
            token_budget: Maximum total tokens to load
            include_advanced: Include legal_standards (advanced knowledge)
            categories: Specific categories to include (overrides default)

        Returns:
            List of KnowledgeItem sorted by priority
        """
        knowledge_items = []
        total_tokens = 0

        # Default categories to load
        if categories is None:
            categories = ['foundations', 'calculations', 'fact_checking', 'analysis', 'report']
            if include_advanced:
                categories.append('legal_standards')

        for category in categories:
            if category not in self._registry:
                continue

            module_config = self._registry[category]

            # Sort by priority
            sorted_files = sorted(
                module_config.files,
                key=lambda x: x.get('priority', 99)
            )

            for file_config in sorted_files:
                knowledge_id = file_config.get('id')
                if not knowledge_id:
                    continue

                knowledge = await self.get_knowledge(category, knowledge_id)
                if not knowledge:
                    continue

                # Check stage applicability
                if not knowledge.applies_to_stage(stage):
                    continue

                # Check token budget
                if total_tokens + knowledge.token_estimate > token_budget:
                    logger.debug(
                        f"Token budget ({token_budget}) reached at {total_tokens}. "
                        f"Skipping: {knowledge_id}"
                    )
                    continue

                knowledge_items.append(knowledge)
                total_tokens += knowledge.token_estimate

        # Sort by priority
        return sorted(knowledge_items, key=lambda x: x.priority)

    async def get_lpr_rates(self) -> LPRData:
        """
        Get LPR rate data.

        Uses separate caching with 5-minute TTL for LPR data.
        """
        # Check cache
        if (self._lpr_cache is not None and
            self._lpr_cache_time is not None and
            datetime.now() - self._lpr_cache_time < timedelta(minutes=5)):
            return self._lpr_cache

        lpr_path = self._knowledge_dir / 'calculations' / 'lpr_rates.yaml'

        if not lpr_path.exists():
            logger.error(f"LPR rates file not found: {lpr_path}")
            return LPRData(source="", last_updated="", rates=[])

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: lpr_path.read_text(encoding='utf-8')
            )
            data = yaml.safe_load(content)

            metadata = data.get('metadata', {})
            rates = []
            for rate_entry in data.get('rates', []):
                rates.append(LPRRate(
                    date=rate_entry.get('date', ''),
                    lpr_1y=float(rate_entry.get('lpr_1y', 0)),
                    lpr_5y=float(rate_entry.get('lpr_5y', 0))
                ))

            lpr_data = LPRData(
                source=metadata.get('source', ''),
                last_updated=metadata.get('last_updated', ''),
                rates=rates
            )

            # Update cache
            self._lpr_cache = lpr_data
            self._lpr_cache_time = datetime.now()

            return lpr_data

        except Exception as e:
            logger.error(f"Failed to load LPR rates: {e}")
            return LPRData(source="", last_updated="", rates=[])

    def format_for_prompt(
        self,
        knowledge_items: List[KnowledgeItem],
        format_type: str = 'full'
    ) -> str:
        """
        Format knowledge items for inclusion in LLM prompt.

        Args:
            knowledge_items: List of knowledge items to format
            format_type: 'full' (complete content), 'summary' (brief), 'structured' (indexed)

        Returns:
            Formatted string for prompt inclusion
        """
        if not knowledge_items:
            return ""

        if format_type == 'full':
            sections = []
            for item in knowledge_items:
                sections.append(f"### {item.name}\n\n{item.content}")
            return "\n\n---\n\n".join(sections)

        elif format_type == 'structured':
            return "\n".join([
                f"[{item.category}:{item.id}] {item.name}"
                for item in knowledge_items
            ])

        else:  # summary
            return "\n".join([
                f"- {item.name}: {item.metadata.get('description', '')[:100]}"
                for item in knowledge_items
            ])

    def list_categories(self) -> List[str]:
        """List all registered knowledge categories"""
        return list(self._registry.keys())

    def list_knowledge(self, category: str) -> List[Dict[str, Any]]:
        """List all knowledge items in a category"""
        if category not in self._registry:
            return []

        return [
            {
                'id': f.get('id'),
                'path': f.get('path'),
                'priority': f.get('priority', 99),
                'required': f.get('required', False)
            }
            for f in self._registry[category].files
        ]

    def refresh_registry(self):
        """Refresh the registry by re-scanning all modules"""
        self._registry.clear()
        self._cache.invalidate()
        self._lpr_cache = None
        self._lpr_cache_time = None
        self._scan_registry()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._cache.stats()


# Singleton accessor
_knowledge_manager: Optional[KnowledgeManager] = None


def get_knowledge_manager() -> KnowledgeManager:
    """Get the global KnowledgeManager instance"""
    global _knowledge_manager
    if _knowledge_manager is None:
        _knowledge_manager = KnowledgeManager()
    return _knowledge_manager
