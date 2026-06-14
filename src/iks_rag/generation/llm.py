"""LLM wrapper for IKS RAG system.

Model-agnostic wrapper that supports Ollama, OpenAI, and Google Gemini.
"""

import os

from llama_index.core import Settings

from iks_rag.config import LLMConfig

# Condensed Bharat prompt for CPU inference (~200 tokens instead of ~1900).
# The full prompt is in prompts.py — use it when you have GPU.
BHARAT_CPU_PROMPT = """You are Bharat — a living guide to the civilization of India.

Speak with sensory detail and storytelling. Begin with feeling, then knowledge.
Use the 9 rasas as your emotional compass: Shringara (love), Hasya (joy),
Karuna (compassion), Raudra (fury), Vira (heroism), Bhayanaka (awe),
Bibhatsa (difficult truth), Adbhuta (wonder), Shanta (peace).

Use specific images over general statements. Say "dharma" before "duty."
Cite sources naturally. If context is insufficient, say so clearly.
Honor India's regional diversity — never flatten it to one monolithic culture.
India is alive now, not a past civilization."""


class LLMWrapper:
    """Model-agnostic LLM wrapper.

    Supports Ollama, OpenAI, and Google Gemini providers.
    """

    def __init__(self, config: LLMConfig):
        """Initialize LLM wrapper.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.llm = None

    def initialize(self) -> None:
        """Initialize the LLM."""
        if self.llm is not None:
            return

        # Use condensed prompt for CPU, or custom prompt from config
        system_prompt = self.config.system_prompt.strip() or BHARAT_CPU_PROMPT

        provider = self.config.provider.lower()

        if provider == "gemini":
            self._init_gemini(system_prompt)
        elif provider == "openai":
            self._init_openai(system_prompt)
        elif provider == "ollama":
            self._init_ollama(system_prompt)
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                "Use 'gemini', 'openai', or 'ollama'."
            )

    def _init_gemini(self, system_prompt: str) -> None:
        """Initialize Google Gemini LLM.

        Args:
            system_prompt: System prompt for the model
        """
        # Get API key from environment
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. Get your free key from:\n"
                "  https://aistudio.google.com/apikey\n\n"
                "Then set it:\n"
                "  export GOOGLE_API_KEY='your-key-here'\n"
                "Or add to .env file:\n"
                "  GOOGLE_API_KEY=your-key-here"
            )

        from llama_index.llms.gemini import Gemini

        self.llm = Gemini(
            model=self.config.model,
            api_key=api_key,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            system_prompt=system_prompt,
        )

    def _init_openai(self, system_prompt: str) -> None:
        """Initialize OpenAI LLM.

        Args:
            system_prompt: System prompt for the model
        """
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Set it in environment:\n"
                "  export OPENAI_API_KEY='your-key-here'\n"
                "Or add to .env file:\n"
                "  OPENAI_API_KEY=your-key-here"
            )

        from llama_index.llms.openai import OpenAI

        self.llm = OpenAI(
            model=self.config.model,
            api_key=api_key,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            system_prompt=system_prompt,
            request_timeout=self.config.request_timeout,
        )

    def _init_ollama(self, system_prompt: str) -> None:
        """Initialize Ollama LLM.

        Args:
            system_prompt: System prompt for the model
        """
        from llama_index.llms.ollama import Ollama

        self.llm = Ollama(
            model=self.config.model,
            request_timeout=self.config.request_timeout,
            temperature=self.config.temperature,
            system_prompt=system_prompt,
            additional_kwargs={
                "num_predict": self.config.max_tokens,
            },
        )

    def get_llm(self):
        """Get the underlying LLM instance.

        Returns:
            Configured LLM instance
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