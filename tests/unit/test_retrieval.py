import pytest
from unittest.mock import MagicMock, patch
from iks_rag.retrieval.embeddings import EmbeddingsManager, setup_embeddings, get_embedding_model
from iks_rag.retrieval.vector_store import IKSVectorStore
from llama_index.core import Settings
from llama_index.core.embeddings import BaseEmbedding
import sys

@patch("iks_rag.retrieval.embeddings.HuggingFaceEmbedding")
def test_embeddings_manager_initialization(mock_hf_embedding, mock_config):
    """Test EmbeddingsManager initializes with correct config."""
    manager = EmbeddingsManager(mock_config.embeddings)
    manager.initialize()
    assert manager.model is not None
    mock_hf_embedding.assert_called_once()

def test_embeddings_manager_embed_text(mock_config):
    """Test text embedding delegation."""
    manager = EmbeddingsManager(mock_config.embeddings)
    manager.model = MagicMock()
    manager.model.get_text_embedding.return_value = [0.1, 0.2]
    
    assert manager.embed_text("test") == [0.1, 0.2]
    assert manager.embed_batch(["test"]) == [[0.1, 0.2]]
    
    manager.embed_query("test")
    manager.model.get_text_embedding.assert_called_with("query: test")
    
    manager.embed_document("test")
    manager.model.get_text_embedding.assert_called_with("passage: test")

@patch("iks_rag.retrieval.embeddings.HuggingFaceEmbedding")
def test_setup_embeddings(mock_hf_embedding, mock_config):
    """Test setup_embeddings sets global Settings.embed_model."""
    mock_emb = MagicMock(spec=BaseEmbedding)
    mock_hf_embedding.return_value = mock_emb
    setup_embeddings(mock_config.embeddings)
    assert Settings.embed_model == mock_emb

@patch("iks_rag.retrieval.embeddings.HuggingFaceEmbedding")
def test_get_embedding_model_device_auto(mock_hf_embedding, mock_config):
    """Test get_embedding_model detects device correctly with auto."""
    mock_config.embeddings.device = "auto"
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    with patch.dict(sys.modules, {"torch": mock_torch}):
        get_embedding_model(mock_config.embeddings)
        mock_hf_embedding.assert_called_with(
            model_name=mock_config.embeddings.model,
            device="cuda",
            max_length=mock_config.embeddings.max_length
        )

@patch("iks_rag.retrieval.vector_store.chromadb.PersistentClient")
@patch("iks_rag.retrieval.vector_store.ChromaVectorStore")
@patch("iks_rag.retrieval.vector_store.StorageContext")
def test_vector_store_initialization(mock_storage_ctx, mock_chroma_store, mock_client_cls, mock_config):
    """Test IKSVectorStore initializes client and collection."""
    mock_client = mock_client_cls.return_value
    mock_client.get_or_create_collection.return_value = MagicMock()
    
    store = IKSVectorStore(mock_config.vector_store)
    store.initialize()
    
    assert store.client is not None
    # Test initialization guard
    store.initialize()
    assert mock_client_cls.call_count == 1

@patch("iks_rag.retrieval.vector_store.VectorStoreIndex")
def test_vector_store_errors(mock_index_cls, mock_config):
    """Test vector store raises RuntimeError when not initialized."""
    store = IKSVectorStore(mock_config.vector_store)
    
    with pytest.raises(RuntimeError, match="not initialized"):
        store.add_documents([])
    with pytest.raises(RuntimeError, match="not initialized"):
        store.create_index([])
    with pytest.raises(RuntimeError, match="not initialized"):
        store.get_index()
    with pytest.raises(RuntimeError, match="not initialized"):
        store.query("test")

def test_vector_store_clear_with_exception(mock_config):
    """Test clear handles delete_collection exceptions."""
    store = IKSVectorStore(mock_config.vector_store)
    store.client = MagicMock()
    store.client.delete_collection.side_effect = Exception("Collection not found")
    
    # Should not raise
    store.clear()
    assert store.collection is not None

def test_vector_store_count_not_initialized(mock_config):
    """Test count returns 0 if not initialized."""
    store = IKSVectorStore(mock_config.vector_store)
    assert store.count() == 0

@patch("iks_rag.retrieval.vector_store.VectorStoreIndex")
def test_vector_store_operations(mock_index_cls, mock_config):
    """Test basic store operations."""
    store = IKSVectorStore(mock_config.vector_store)
    store.storage_context = MagicMock()
    store.vector_store = MagicMock()
    
    store.add_documents([])
    store.create_index([])
    store.get_index()
    assert mock_index_cls.from_documents.call_count == 2
    assert mock_index_cls.from_vector_store.call_count == 1
