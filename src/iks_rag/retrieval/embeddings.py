"""Embedding configuration for IKS documents.

Uses multilingual-e5 for multilingual support including Indian languages.
"""

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from iks_rag.config import EmbeddingsConfig


def setup_embeddings(config: EmbeddingsConfig) -> None:
    """Set up embedding model in LlamaIndex Settings.

    Args:
        config: Embeddings configuration

    Example:
        >>> from iks_rag.config import load_config
        >>> config = load_config()
        >>> setup_embeddings(config.embeddings)
    """
    # Determine device
    device = config.device
    if device == "auto":
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Create embedding model
    embed_model = HuggingFaceEmbedding(
        model_name=config.model,
        device=device,
        max_length=config.max_length,
    )

    # Set in LlamaIndex global settings
    Settings.embed_model = embed_model


def get_embedding_model(config: EmbeddingsConfig) -> HuggingFaceEmbedding:
    """Get configured embedding model.

    Args:
        config: Embeddings configuration

    Returns:
        Configured HuggingFaceEmbedding instance
    """
    device = config.device
    if device == "auto":
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"

    return HuggingFaceEmbedding(
        model_name=config.model,
        device=device,
        max_length=config.max_length,
    )


class EmbeddingsManager:
    """Manager for embeddings operations."""

    def __init__(self, config: EmbeddingsConfig):
        """Initialize embeddings manager.

        Args:
            config: Embeddings configuration
        """
        self.config = config
        self.model: HuggingFaceEmbedding | None = None

    def initialize(self) -> None:
        """Initialize the embedding model."""
        self.model = get_embedding_model(self.config)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        return self.model.get_text_embedding(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        return [self.model.get_text_embedding(text) for text in texts]

    def embed_query(self, query: str) -> list[float]:
        """Embed a query (uses query-specific preprocessing).

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        # For multilingual-e5, queries should start with "query:"
        # Documents should start with "passage:"
        formatted_query = f"query: {query}"
        return self.model.get_text_embedding(formatted_query)

    def embed_document(self, document: str) -> list[float]:
        """Embed a document (uses document-specific preprocessing).

        Args:
            document: Document text

        Returns:
            Embedding vector
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        formatted_doc = f"passage: {document}"
        return self.model.get_text_embedding(formatted_doc)
