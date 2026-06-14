# Code Conventions — IKS AI Assistant

## Python Style

- **Formatter**: `ruff`
- **Linter**: `ruff`
- **Type Checker**: `mypy` (strict mode)
- **Line Length**: 100 characters
- **Docstrings**: Google style

## Import Order

```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third-party
import torch
from llama_index import VectorStoreIndex

# 3. Local
from iks_rag.config import Settings
```

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code change
- `test`: Adding or correcting tests
- `chore`: Maintenance tasks

**Scopes**:
- `ingestion`: Document loading
- `retrieval`: Vector store, embeddings
- `generation`: LLM, prompts
- `ui`: Gradio interface
- `api`: FastAPI endpoints
- `config`: Configuration
- `docs`: Documentation

**Examples**:
```
feat(ingestion): add PDF OCR support
fix(retrieval): resolve ChromaDB connection timeout
docs(readme): add model configuration section
test(embedding): add multilingual-e5 unit tests
```

## Testing Strategy

### Test Pyramid
- **80% Unit Tests**: Fast, isolated, mock external dependencies
- **15% Integration Tests**: Test component interactions
- **5% E2E Tests**: Full user scenarios

### Coverage Target
- Minimum: 80%
- Optimal: 90%
