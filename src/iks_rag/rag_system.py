"""Main RAG system for IKS.

Orchestrates document ingestion, retrieval, and generation.
"""

from pathlib import Path
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.response import Response

from iks_rag.config import RAGConfig, load_config
from iks_rag.generation.llm import LLMWrapper, setup_llm
from iks_rag.ingestion.loaders import DocumentLoader
from iks_rag.retrieval.embeddings import setup_embeddings
from iks_rag.retrieval.vector_store import IKSVectorStore


class RAGSystem:
    """Main RAG system for IKS questions.

    Coordinates document loading, vector storage, retrieval, and generation.
    """

    def __init__(self, config: RAGConfig):
        """Initialize RAG system.

        Args:
            config: RAG configuration
        """
        self.config = config
        self.document_loader: DocumentLoader | None = None
        self.vector_store: IKSVectorStore | None = None
        self.llm_wrapper: LLMWrapper | None = None
        self.index: VectorStoreIndex | None = None

    def initialize(self) -> None:
        """Initialize all components."""
        # Set up embeddings
        setup_embeddings(self.config.embeddings)

        # Set up LLM
        setup_llm(self.config.llm)
        self.llm_wrapper = LLMWrapper(self.config.llm)
        self.llm_wrapper.initialize()

        # Initialize vector store
        self.vector_store = IKSVectorStore(self.config.vector_store)
        self.vector_store.initialize()

        # Initialize document loader
        self.document_loader = DocumentLoader(
            self.config.data_sources.documents_path
        )

    def load_documents(self) -> None:
        """Load documents from configured path.

        Loads all documents and creates the vector index.
        If ChromaDB already has embeddings, loads the existing index instead.
        """
        if self.document_loader is None or self.vector_store is None:
            raise RuntimeError("System not initialized. Call initialize() first.")

        # Check if ChromaDB already has data — skip re-embedding
        existing_count = self.vector_store.count()
        if existing_count > 0:
            print(f"✅ Found {existing_count} existing chunks in ChromaDB — loading cached index")
            self.index = self.vector_store.get_index()
            return

        # Load documents fresh
        documents = self.document_loader.load_all()

        if not documents:
            print(f"No documents found in {self.config.data_sources.documents_path}")
            return

        # Create index (this generates embeddings — takes ~70 min on CPU)
        self.index = self.vector_store.create_index(documents)

    def query(self, question: str) -> dict[str, Any]:
        """Query the RAG system.

        Args:
            question: User question

        Returns:
            Dictionary with answer and sources
        """
        if self.index is None:
            raise RuntimeError("No documents loaded. Call load_documents() first.")

        # Create query engine
        query_engine = self.index.as_query_engine(
            similarity_top_k=self.config.retrieval.top_k,
            response_mode="compact",
        )

        # Query
        response: Response = query_engine.query(question)

        # Format response
        sources = []
        if response.source_nodes:
            for node in response.source_nodes:
                source = {
                    "text": node.text[:500] + "..." if len(node.text) > 500 else node.text,
                    "metadata": node.metadata,
                    "score": getattr(node, "score", 0.0),
                }
                sources.append(source)

        return {
            "answer": str(response),
            "sources": sources,
            "question": question,
        }

    def chat(self, question: str, history: list[dict[str, str]]) -> dict[str, Any]:
        """Chat with the RAG system (with conversation history).

        Args:
            question: Current question
            history: List of previous messages

        Returns:
            Dictionary with answer and sources
        """
        # For now, same as query (LlamaIndex handles context)
        return self.query(question)

    def get_stats(self) -> dict[str, Any]:
        """Get system statistics.

        Returns:
            Dictionary with system stats
        """
        stats = {
            "initialized": self.vector_store is not None,
            "documents_loaded": self.vector_store.count() if self.vector_store else 0,
            "config": {
                "model": self.config.llm.model,
                "embeddings": self.config.embeddings.model,
                "vector_store": self.config.vector_store.type,
            },
        }

        if self.document_loader:
            stats["document_stats"] = self.document_loader.get_document_stats()

        return stats

    def clear_index(self) -> None:
        """Clear the document index."""
        if self.vector_store:
            self.vector_store.clear()
            self.index = None


def create_rag_system(config_path: str | Path = "configs/rag/default.yaml") -> RAGSystem:
    """Create and initialize a RAG system.

    Args:
        config_path: Path to configuration file

    Returns:
        Initialized RAGSystem

    Example:
        >>> rag = create_rag_system()
        >>> rag.load_documents()
        >>> response = rag.query("What are the 72 Melakarta ragas?")
        >>> print(response["answer"])
    """
    config = load_config(config_path)
    system = RAGSystem(config)
    system.initialize()
    return system
