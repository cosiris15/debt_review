"""
Knowledge Data Schemas

Defines data structures for knowledge items and modules.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class KnowledgeCategory(str, Enum):
    """Knowledge categories"""
    FOUNDATIONS = "foundations"
    CALCULATIONS = "calculations"
    FACT_CHECKING = "fact_checking"
    ANALYSIS = "analysis"
    REPORT = "report"
    LEGAL_STANDARDS = "legal_standards"


class WorkflowStage(str, Enum):
    """Workflow stages that knowledge can apply to"""
    FACT_CHECK = "fact_check"
    ANALYSIS = "analysis"
    REPORT = "report"
    ALL = "all"


@dataclass
class KnowledgeItem:
    """
    Single knowledge item loaded from a file.

    Attributes:
        id: Unique identifier for the knowledge item
        name: Human-readable name
        category: Category (foundations, calculations, etc.)
        content: The actual knowledge content (Markdown body)
        metadata: YAML frontmatter metadata
        token_estimate: Estimated token count for LLM context budgeting
        applicable_stages: Which workflow stages this knowledge applies to
        priority: Loading priority (1 = highest)
        last_loaded: When this item was last loaded from disk
        file_hash: MD5 hash of file content for change detection
    """
    id: str
    name: str
    category: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_estimate: int = 0
    applicable_stages: List[str] = field(default_factory=list)
    priority: int = 99
    last_loaded: datetime = field(default_factory=datetime.now)
    file_hash: str = ""

    def applies_to_stage(self, stage: str) -> bool:
        """Check if this knowledge applies to a workflow stage"""
        if not self.applicable_stages:
            return True  # No restriction means applies to all
        if "all" in self.applicable_stages:
            return True
        return stage in self.applicable_stages


@dataclass
class ModuleConfig:
    """
    Configuration for a knowledge module (from _index.yaml).

    Attributes:
        id: Module identifier
        name: Human-readable module name
        description: Module description
        eager_load: Whether to load at startup
        cache_enabled: Whether to enable caching
        cache_ttl: Cache time-to-live in seconds
        files: List of file configurations
    """
    id: str
    name: str
    description: str = ""
    eager_load: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 60
    files: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LPRRate:
    """LPR rate entry"""
    date: str
    lpr_1y: float
    lpr_5y: float


@dataclass
class LPRData:
    """Complete LPR data with metadata"""
    source: str
    last_updated: str
    rates: List[LPRRate] = field(default_factory=list)
