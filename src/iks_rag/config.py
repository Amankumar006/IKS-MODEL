"""Configuration management for IKS RAG system.

This module handles loading and validation of RAG configuration from YAML files.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """LLM configuration."""

    provider: str = Field(default="ollama", description="LLM provider")
    model: str = Field(default="gemma3:4b", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)
    request_timeout: float = Field(default=120.0, gt=0)
    system_prompt: str = Field(default="", description="System prompt for LLM")


class EmbeddingsConfig(BaseModel):
    """Embeddings model configuration."""

    model: str = Field(
        default="intfloat/multilingual-e5-large",
        description="HuggingFace model name",
    )
    device: str = Field(default="auto", description="Device: auto, cpu, cuda")
    max_length: int = Field(default=512, gt=0)
    normalize_embeddings: bool = Field(default=True)


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""

    type: str = Field(default="chroma", description="Vector store type")
    path: str = Field(default="./data/chroma_db", description="Storage path")
    collection_name: str = Field(default="iks_corpus")
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalConfig(BaseModel):
    """Retrieval configuration."""

    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    search_mode: str = Field(default="semantic")


class DocumentProcessingConfig(BaseModel):
    """Document processing configuration."""

    chunk_size: int = Field(default=512, gt=0)
    chunk_overlap: int = Field(default=50, ge=0)
    supported_extensions: list[str] = Field(
        default_factory=lambda: [".txt", ".md", ".pdf", ".html", ".json"]
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["*.tmp", "*.log", ".*"]
    )


class UIConfig(BaseModel):
    """UI configuration."""

    title: str = Field(default="IKS Assistant")
    description: str = Field(default="")
    theme: dict[str, str] = Field(default_factory=dict)
    examples: list[str] = Field(default_factory=list)


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO")
    format: str = Field(default="structured")
    log_file: str = Field(default="./logs/iks_rag.log")
    log_retrieval_times: bool = Field(default=True)
    log_generation_times: bool = Field(default=True)


class APIConfig(BaseModel):
    """API server configuration."""

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, gt=0)
    reload: bool = Field(default=False)
    cors: dict[str, Any] = Field(default_factory=dict)


class DataSourcesConfig(BaseModel):
    """Data sources configuration."""

    documents_path: str = Field(default="./data/documents")
    auto_download: dict[str, Any] = Field(default_factory=dict)


class PerformanceConfig(BaseModel):
    """Performance configuration."""

    cache_enabled: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600)
    batch_size: int = Field(default=32)
    max_workers: int = Field(default=4)


class RAGConfig(BaseSettings):
    """Main RAG configuration class.

    Loads configuration from YAML file with pydantic validation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm: LLMConfig = Field(default_factory=LLMConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    document_processing: DocumentProcessingConfig = Field(
        default_factory=DocumentProcessingConfig
    )
    ui: UIConfig = Field(default_factory=UIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    data_sources: DataSourcesConfig = Field(default_factory=DataSourcesConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    @field_validator("logging")
    @classmethod
    def validate_log_level(cls, v: LoggingConfig) -> LoggingConfig:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v.level}")
        return v


def load_config(config_path: str | Path = "configs/rag/default.yaml") -> RAGConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration YAML file

    Returns:
        Validated RAGConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid

    Example:
        >>> config = load_config("configs/rag/default.yaml")
        >>> print(config.llm.model)
        'gemma3:4b'
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    return RAGConfig(**config_dict)


def save_config(config: RAGConfig, config_path: str | Path) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration to save
        config_path: Path to save YAML file
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_dict = config.model_dump()

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


# Global config instance (lazy loading)
_config: RAGConfig | None = None


def get_config() -> RAGConfig:
    """Get or load global configuration.

    Returns:
        RAGConfig instance
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: RAGConfig) -> None:
    """Set global configuration.

    Args:
        config: Configuration to set
    """
    global _config
    _config = config
