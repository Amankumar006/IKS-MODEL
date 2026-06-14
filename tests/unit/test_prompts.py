from iks_rag.generation import prompts

def test_prompts_exist():
    """Ensure prompts constants are defined."""
    assert hasattr(prompts, "SYSTEM_PROMPT")
    assert hasattr(prompts, "QUERY_TEMPLATE")
    assert "Bharat" in prompts.SYSTEM_PROMPT
