import os
import pytest
from unittest.mock import MagicMock, patch

import llama_index.llms.gemini
import llama_index.llms.openai
import llama_index.llms.ollama

from iks_rag.generation.llm import LLMWrapper
from iks_rag.config import LLMConfig

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"})
@patch("llama_index.llms.gemini.Gemini")
def test_initialize_gemini(mock_gemini, mock_config):
    """Test LLMWrapper initialization for Gemini provider."""
    mock_config.llm.provider = "gemini"
    mock_config.llm.model = "models/gemini-pro"
    
    wrapper = LLMWrapper(mock_config.llm)
    wrapper.initialize()
    
    assert wrapper.config.provider == "gemini"
    mock_gemini.assert_called_once()

@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
@patch("llama_index.llms.openai.OpenAI")
def test_initialize_openai(mock_openai, mock_config):
    """Test LLMWrapper initialization for OpenAI provider."""
    mock_config.llm.provider = "openai"
    mock_config.llm.model = "gpt-4"
    
    wrapper = LLMWrapper(mock_config.llm)
    wrapper.initialize()
    
    assert wrapper.config.provider == "openai"
    mock_openai.assert_called_once()

@patch("llama_index.llms.ollama.Ollama")
def test_initialize_ollama(mock_ollama, mock_config):
    """Test LLMWrapper initialization for Ollama provider."""
    mock_config.llm.provider = "ollama"
    mock_config.llm.model = "mistral:7b"
    
    wrapper = LLMWrapper(mock_config.llm)
    wrapper.initialize()
    
    assert wrapper.config.provider == "ollama"
    mock_ollama.assert_called_once()

def test_unsupported_provider():
    """Test initialization with unsupported provider raises ValueError."""
    config = LLMConfig(provider="unsupported")
    wrapper = LLMWrapper(config)
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        wrapper.initialize()

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"})
@patch("llama_index.llms.gemini.Gemini")
def test_complete(mock_gemini_cls, mock_config):
    """Test completion call delegates to underlying model."""
    mock_gemini = mock_gemini_cls.return_value
    mock_gemini.complete.return_value = MagicMock(text="Test Response")
    
    mock_config.llm.provider = "gemini"
    wrapper = LLMWrapper(mock_config.llm)
    wrapper.initialize()
    
    response = wrapper.complete("Hello")
    assert response == "Test Response"
    mock_gemini.complete.assert_called_once()

def test_chat(mock_config):
    """Test chat call delegates to underlying model."""
    from llama_index.core.llms import ChatMessage
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"}), patch("llama_index.llms.gemini.Gemini") as mock_gemini_cls:
        mock_gemini = mock_gemini_cls.return_value
        mock_gemini.chat.return_value = MagicMock(message=MagicMock(content="Test Chat"))
        
        mock_config.llm.provider = "gemini"
        wrapper = LLMWrapper(mock_config.llm)
        wrapper.initialize()
        
        messages = [{"role": "user", "content": "Hello"}]
        response = wrapper.chat(messages)
        
        assert response == "Test Chat"
        mock_gemini.chat.assert_called_once()

def test_setup_llm(mock_config):
    """Test setup_llm properly configures global Settings.llm."""
    from iks_rag.generation.llm import setup_llm
    
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"}), patch("llama_index.llms.gemini.Gemini") as mock_gemini_cls, patch("iks_rag.generation.llm.Settings") as mock_settings:
        mock_gemini = mock_gemini_cls.return_value
        mock_config.llm.provider = "gemini"
        
        setup_llm(mock_config.llm)
        
        assert mock_settings.llm == mock_gemini
