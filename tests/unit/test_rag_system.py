import pytest
from unittest.mock import MagicMock, patch
from iks_rag.rag_system import RAGSystem, create_rag_system

@patch("iks_rag.rag_system.setup_embeddings")
@patch("iks_rag.rag_system.setup_llm")
@patch("iks_rag.rag_system.IKSVectorStore")
@patch("iks_rag.rag_system.LLMWrapper")
def test_rag_system_initialization(mock_llm_cls, mock_vs_cls, mock_setup_llm, mock_setup_emb, mock_config):
    """Test RAGSystem correctly initializes its sub-components."""
    system = RAGSystem(config=mock_config)
    system.initialize()
    
    assert system.config == mock_config
    mock_llm_cls.assert_called_once()
    mock_vs_cls.assert_called_once()
    mock_setup_llm.assert_called_once()
    mock_setup_emb.assert_called_once()

@patch("iks_rag.rag_system.setup_embeddings")
@patch("iks_rag.rag_system.setup_llm")
@patch("iks_rag.rag_system.IKSVectorStore")
@patch("iks_rag.rag_system.LLMWrapper")
def test_query_success(mock_llm_cls, mock_vs_cls, mock_setup_llm, mock_setup_emb, mock_config):
    """Test the query execution flow with sources."""
    # Setup mock query engine
    mock_query_engine = MagicMock()
    mock_response = MagicMock()
    mock_response.__str__.return_value = "Bharat's response"
    
    # Mock a source node
    mock_node = MagicMock()
    mock_node.text = "Ancient text"
    mock_node.metadata = {"file_name": "source.txt"}
    mock_node.score = 0.95
    mock_response.source_nodes = [mock_node]
    
    mock_query_engine.query.return_value = mock_response
    
    mock_index = MagicMock()
    mock_index.as_query_engine.return_value = mock_query_engine
    
    system = RAGSystem(config=mock_config)
    system.index = mock_index
    
    response = system.query("Tell me about temples")
    
    assert response["answer"] == "Bharat's response"
    assert len(response["sources"]) == 1
    assert response["sources"][0]["text"] == "Ancient text"
    assert response["sources"][0]["metadata"]["file_name"] == "source.txt"

def test_query_no_index(mock_config):
    """Test query raises error if index not loaded."""
    system = RAGSystem(mock_config)
    with pytest.raises(RuntimeError, match="No documents loaded"):
        system.query("test")

@patch("iks_rag.rag_system.DocumentLoader")
@patch("iks_rag.rag_system.setup_embeddings")
@patch("iks_rag.rag_system.setup_llm")
@patch("iks_rag.rag_system.IKSVectorStore")
@patch("iks_rag.rag_system.LLMWrapper")
def test_load_documents_new(mock_llm, mock_vs_cls, mock_setup_llm, mock_setup_emb, mock_loader_cls, mock_config):
    """Test document loading into the system when no existing data."""
    mock_loader = mock_loader_cls.return_value
    mock_loader.load_all.return_value = [MagicMock()]
    
    mock_vs = mock_vs_cls.return_value
    mock_vs.count.return_value = 0
    
    system = RAGSystem(config=mock_config)
    system.initialize()
    system.load_documents()
    
    mock_loader.load_all.assert_called_once()
    mock_vs.create_index.assert_called_once()

@patch("iks_rag.rag_system.DocumentLoader")
@patch("iks_rag.rag_system.setup_embeddings")
@patch("iks_rag.rag_system.setup_llm")
@patch("iks_rag.rag_system.IKSVectorStore")
@patch("iks_rag.rag_system.LLMWrapper")
def test_load_documents_cached(mock_llm, mock_vs_cls, mock_setup_llm, mock_setup_emb, mock_loader_cls, mock_config):
    """Test document loading uses cached index if data exists."""
    mock_vs = mock_vs_cls.return_value
    mock_vs.count.return_value = 100
    
    system = RAGSystem(config=mock_config)
    system.initialize()
    system.load_documents()
    
    mock_loader_cls.return_value.load_all.assert_not_called()
    mock_vs.get_index.assert_called_once()

def test_chat_delegation(mock_config):
    """Test that chat delegates to query."""
    system = RAGSystem(mock_config)
    with patch.object(system, "query") as mock_query:
        system.chat("test", [])
        mock_query.assert_called_once_with("test")

@patch("iks_rag.rag_system.IKSVectorStore")
def test_get_stats(mock_vs_cls, mock_config):
    """Test system statistics reporting."""
    mock_vs = mock_vs_cls.return_value
    mock_vs.count.return_value = 4500
    
    system = RAGSystem(mock_config)
    system.vector_store = mock_vs
    
    stats = system.get_stats()
    assert stats["documents_loaded"] == 4500
    assert stats["config"]["model"] == mock_config.llm.model

@patch("iks_rag.rag_system.IKSVectorStore")
def test_clear_index(mock_vs_cls, mock_config):
    """Test clearing the index."""
    mock_vs = mock_vs_cls.return_value
    system = RAGSystem(mock_config)
    system.vector_store = mock_vs
    system.index = MagicMock()
    
    system.clear_index()
    mock_vs.clear.assert_called_once()
    assert system.index is None

@patch("iks_rag.rag_system.load_config")
@patch("iks_rag.rag_system.RAGSystem")
def test_create_rag_system(mock_rag_cls, mock_load_config):
    """Test the helper creation function."""
    mock_load_config.return_value = MagicMock()
    create_rag_system("test.yaml")
    mock_rag_cls.assert_called_once()
    mock_rag_cls.return_value.initialize.assert_called_once()
