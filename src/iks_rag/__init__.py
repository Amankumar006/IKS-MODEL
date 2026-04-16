"""IKS RAG (Retrieval-Augmented Generation) System.

This package provides the core RAG functionality for the Indian Knowledge Systems
AI Assistant. It includes document ingestion, retrieval, and generation components.

Example:
    >>> from iks_rag import create_rag_system
    >>> rag = create_rag_system(config_path="configs/rag/default.yaml")
    >>> response = rag.query("What are the 72 Melakarta ragas?")
    >>> print(response.answer)
    >>> print(response.sources)

Phase: 1 (RAG Foundation)
Status: In Development
"""

__version__ = "0.1.0"
__author__ = "Amankumar"
__license__ = "MIT"

from iks_rag.config import RAGConfig, load_config
from iks_rag.rag_system import RAGSystem, create_rag_system

__all__ = [
    "RAGConfig",
    "load_config",
    "RAGSystem",
    "create_rag_system",
]
