import pytest
from unittest.mock import MagicMock, patch
import gradio as gr
from iks_rag.ui.gradio_app import create_interface, handle_response, format_examples, main

def test_format_examples(mock_config):
    """Test example formatting."""
    mock_config.ui.examples = ["Question 1", "Question 2"]
    md = format_examples(mock_config)
    assert "Question 1" in md
    assert "Question 2" in md

def test_handle_response_success(mock_config):
    """Test successful response handling."""
    mock_rag = MagicMock()
    mock_rag.query.return_value = {
        "answer": "Answer here",
        "sources": [{"metadata": {"file_name": "source.pdf"}}]
    }
    
    history = []
    msg, new_history = handle_response("Hello", history, mock_rag)
    assert msg == ""
    assert len(new_history) == 2

def test_handle_response_error(mock_config):
    """Test error handling in response generation."""
    mock_rag = MagicMock()
    mock_rag.query.side_effect = Exception("System down")
    
    history = []
    msg, new_history = handle_response("Hello", history, mock_rag)
    assert "Error: System down" in new_history[1]["content"]

def test_create_interface(mock_config):
    """Test that create_interface returns a Gradio Blocks instance."""
    mock_rag = MagicMock()
    mock_rag.get_stats.return_value = {
        "documents_loaded": 10,
        "config": {"model": "m", "embeddings": "e"}
    }
    
    with patch("iks_rag.ui.gradio_app.load_config", return_value=mock_config):
        demo = create_interface(mock_rag)
        assert isinstance(demo, gr.Blocks)

@patch("argparse.ArgumentParser.parse_args")
@patch("iks_rag.rag_system.create_rag_system")
@patch("iks_rag.ui.gradio_app.create_interface")
def test_main(mock_create_ui, mock_create_rag, mock_parse_args):
    """Test the main entry point."""
    mock_args = MagicMock()
    mock_args.config = "test.yaml"
    mock_args.host = "127.0.0.1"
    mock_args.port = 7860
    mock_args.share = False
    mock_parse_args.return_value = mock_args
    
    mock_rag = mock_create_rag.return_value
    mock_rag.get_stats.return_value = {"documents_loaded": 5}
    
    mock_demo = mock_create_ui.return_value
    
    with patch("builtins.print"):
        main()
        
    mock_create_rag.assert_called_once_with("test.yaml")
    mock_rag.load_documents.assert_called_once()
    mock_demo.launch.assert_called_once()
