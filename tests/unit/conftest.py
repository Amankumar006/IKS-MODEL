import pytest
from unittest.mock import MagicMock
from pathlib import Path
from iks_rag.config import RAGConfig, LLMConfig, EmbeddingsConfig, VectorStoreConfig

@pytest.fixture
def mock_config():
    """Provides a base RAGConfig for testing."""
    return RAGConfig(
        llm=LLMConfig(provider="gemini", model="models/gemini-2.5-flash"),
        embeddings=EmbeddingsConfig(model="mock-embedding-model"),
        vector_store=VectorStoreConfig(path="./data/test_chroma_db", collection_name="test_collection")
    )

@pytest.fixture
def temp_doc_dir(tmp_path):
    """Creates a temporary directory with some mock documents."""
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    (doc_dir / "test_philosophy.txt").write_text("Vedanta philosophy is ancient.", encoding="utf-8")
    (doc_dir / "chola_temple.md").write_text("# Chola Temples\nBeautiful architecture.", encoding="utf-8")
    return doc_dir

@pytest.fixture
def mock_llm():
    """Mock for LlamaIndex LLM."""
    mock = MagicMock()
    mock.complete.return_value = MagicMock(text="Mocked LLM response")
    return mock

@pytest.fixture
def mock_vector_store():
    """Mock for ChromaVectorStore."""
    return MagicMock()

@pytest.fixture
def mock_embedding_model():
    """Mock for HuggingFaceEmbedding."""
    mock = MagicMock()
    mock.get_text_embedding.return_value = [0.1] * 1024
    return mock
