"""LLM wrapper for IKS RAG system.

Model-agnostic wrapper that supports any Ollama model.
"""

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama

from iks_rag.config import LLMConfig


class LLMWrapper:
    """Model-agnostic LLM wrapper.

    Supports any Ollama-compatible model.
    """

    def __init__(self, config: LLMConfig):
        """Initialize LLM wrapper.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.llm: Ollama | None = None

    def initialize(self) -> None:
        """Initialize the LLM."""
        if self.llm is not None:
            return

        self.llm = Ollama(
            model=self.config.model,
            request_timeout=self.config.request_timeout,
            temperature=self.config.temperature,
            additional_kwargs={
                "num_predict": self.config.max_tokens,
            },
        )

        if self.config.system_prompt:
            self.llm.system_prompt = self.config.system_prompt

    def get_llm(self) -> Ollama:
        """Get the underlying LLM instance.

        Returns:
            Configured Ollama instance
        """
        if self.llm is None:
            self.initialize()
        return self.llm

    def complete(self, prompt: str) -> str:
        """Complete a prompt.

        Args:
            prompt: Text prompt

        Returns:
            Generated text
        """
        if self.llm is None:
            self.initialize()

        response = self.llm.complete(prompt)
        return response.text

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Chat with the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Generated response
        """
        if self.llm is None:
            self.initialize()

        from llama_index.core.llms import ChatMessage

        chat_messages = [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in messages
        ]

        response = self.llm.chat(chat_messages)
        return response.message.content


def setup_llm(config: LLMConfig) -> None:
    """Set up LLM in LlamaIndex Settings.

    Args:
        config: LLM configuration
    """
    wrapper = LLMWrapper(config)
    wrapper.initialize()

    Settings.llm = wrapper.get_llm()
