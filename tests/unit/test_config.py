import pytest
from pathlib import Path
import yaml
from iks_rag.config import load_config, save_config, RAGConfig, LoggingConfig

def test_default_config_loading(tmp_path):
    """Test that default config loads correctly when a valid file exists."""
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    config_file = config_dir / "default.yaml"
    
    sample_data = {
        "llm": {"provider": "openai", "model": "gpt-4"},
        "logging": {"level": "DEBUG"}
    }
    
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_data, f)
        
    config = load_config(config_file)
    assert config.llm.provider == "openai"
    assert config.llm.model == "gpt-4"
    assert config.logging.level == "DEBUG"

def test_invalid_log_level():
    """Test that invalid log level raises ValueError via RAGConfig validator."""
    with pytest.raises(ValueError, match="Invalid log level"):
        RAGConfig(logging=LoggingConfig(level="INVALID_LEVEL"))

def test_config_serialization(tmp_path):
    """Test saving and then loading a config file."""
    config_path = tmp_path / "test_save.yaml"
    config = RAGConfig()
    config.llm.provider = "gemini"
    
    save_config(config, config_path)
    
    loaded_config = load_config(config_path)
    assert loaded_config.llm.provider == "gemini"

def test_load_config_not_found():
    """Test that FileNotFoundError is raised if config doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_config("non_existent_file.yaml")
