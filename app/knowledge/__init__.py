"""
Knowledge Management Module for Debt Review System

This module provides centralized knowledge management for the LangGraph workflow.
All legal rules, calculation parameters, and workflow guides are stored here.
"""

from app.knowledge.loader import KnowledgeManager, get_knowledge_manager

__all__ = ['KnowledgeManager', 'get_knowledge_manager']
