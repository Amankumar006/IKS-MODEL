"""Vector store interface for IKS documents.

Wraps ChromaDB with a clean interface for document storage and retrieval.
"""

from pathlib import Path
from typing import Any

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStore
from llama_index.vector_stores.chroma import ChromaVectorStore

from iks_rag.config import VectorStoreConfig


class IKSVectorStore:
    """Vector store for IKS documents.

    Manages document embeddings and similarity search.
    """

    def __init__(self, config: VectorStoreConfig):
        """Initialize vector store.

        Args:
            config: Vector store configuration
        """
        self.config = config
        self.client: chromadb.Client | None = None
        self.collection: chromadb.Collection | None = None
        self.vector_store: VectorStore | None = None
        self.storage_context: StorageContext | None = None

    def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        if self.client is not None:
            return  # Already initialized

        # Create persistence directory
        db_path = Path(self.config.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize client
        self.client = chromadb.PersistentClient(path=str(db_path))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            metadata=self.config.metadata,
        )

        # Create LlamaIndex vector store wrapper
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

        # Create storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

    def add_documents(self, documents: list[Any]) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of LlamaIndex Document objects
        """
        if self.storage_context is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context,
        )

    def create_index(self, documents: list[Any]) -> VectorStoreIndex:
        """Create a new index from documents.

        Args:
            documents: List of LlamaIndex Document objects

        Returns:
            VectorStoreIndex for querying
        """
        if self.storage_context is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        return VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            show_progress=True,
        )

    def get_index(self) -> VectorStoreIndex:
        """Get existing index from vector store.

        Returns:
            VectorStoreIndex for querying
        """
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        return VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
        )

    def query(
        self,
        query_text: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Query the vector store for similar documents.

        Args:
            query_text: Query text
            top_k: Number of results to return

        Returns:
            List of result dictionaries with text and metadata
        """
        if self.collection is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

        # Format results
        documents = []
        for i in range(len(results["documents"][0])):
            documents.append(
                {
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                }
            )

        return documents

    def count(self) -> int:
        """Get total number of documents in the store.

        Returns:
            Document count
        """
        if self.collection is None:
            return 0

        return self.collection.count()

    def clear(self) -> None:
        """Clear all documents from the store."""
        if self.client is None:
            return

        # Delete and recreate collection
        try:
            self.client.delete_collection(self.config.collection_name)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            metadata=self.config.metadata,
        )

        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics.

        Returns:
            Dictionary with store statistics
        """
        return {
            "collection_name": self.config.collection_name,
            "path": self.config.path,
            "document_count": self.count(),
            "initialized": self.client is not None,
        }
