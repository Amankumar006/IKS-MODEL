# Contributing to IKS AI Assistant

Thank you for your interest in contributing to the Indian Knowledge Systems AI Assistant! This document provides guidelines for contributing.

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- [Ollama](https://ollama.com/) (for local LLM inference)
- Git

### Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/IKS-MODEL.git
   cd IKS-MODEL
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

5. **Run tests** to ensure everything works:
   ```bash
   uv run pytest tests/ -v
   ```

## Development Workflow

### Branching Strategy

We use a simplified GitFlow:

```
main          # Production-ready code
  ↑
develop       # Integration branch
  ↑
feature/*     # Feature branches
bugfix/*      # Bug fix branches
hotfix/*      # Emergency fixes
```

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests and linting:
   ```bash
   uv run pytest tests/ -v
   uv run ruff check src/
   uv run ruff format src/
   uv run mypy src/ --strict
   ```

4. Commit with conventional format (see below)

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request to `develop`

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or correcting tests
- `chore`: Maintenance tasks (dependencies, build process, etc.)

Scopes:
- `ingestion`: Document loading
- `retrieval`: Vector store, embeddings
- `generation`: LLM, prompts
- `ui`: Gradio interface
- `api`: FastAPI endpoints
- `config`: Configuration
- `docs`: Documentation

Examples:
```
feat(ingestion): add PDF OCR support

fix(retrieval): resolve ChromaDB timeout on large queries

docs(readme): add model configuration section

test(embedding): add multilingual-e5 unit tests

refactor(api): extract query validation logic
```

## Code Standards

### Python Style

- **Formatter**: ruff (configured in `pyproject.toml`)
- **Line length**: 100 characters
- **Type hints**: Required for all public functions
- **Docstrings**: Google style

### Type Hints

```python
from typing import List, Optional

def process_documents(
    paths: List[Path],
    chunk_size: int = 512,
    overlap: Optional[int] = None
) -> List[Document]:
    """Process documents into chunks.
    
    Args:
        paths: List of document paths
        chunk_size: Maximum tokens per chunk
        overlap: Token overlap between chunks
    
    Returns:
        List of processed documents
    """
    ...
```

### Testing

- Write unit tests for all new features
- Maintain 80%+ code coverage
- Use descriptive test names
- Mock external dependencies

```python
def test_load_pdf_document():
    """Test loading a PDF document."""
    loader = PDFLoader()
    docs = loader.load("test.pdf")
    assert len(docs) > 0
    assert docs[0].text is not None
```

## Areas for Contribution

### High Priority

- **Document Collection**: Add IKS documents to knowledge base
- **Retrieval Improvements**: Better chunking, re-ranking
- **UI Enhancements**: Better Gradio interface, mobile support
- **Testing**: Increase test coverage
- **Documentation**: Tutorials, examples, API docs

### Medium Priority

- **Multi-language Support**: Sanskrit, Hindi, Tamil, Kannada
- **Visual Understanding**: Image-based queries
- **Performance**: Caching, optimization
- **Monitoring**: Logging, metrics

### Future (Phase 2+)

- **Data Curation**: Expert review of training data
- **Fine-tuning**: Training scripts, evaluation
- **Production**: Deployment, scaling

## Documentation

- Update `README.md` if you change setup instructions
- Update `CHANGELOG.md` under `[Unreleased]`
- Create ADR if you make architectural decisions
- Add docstrings to all public functions

## Code Review

All PRs require:
1. At least 1 review
2. All CI checks passing
3. No merge conflicts
4. Documentation updated

## Reporting Issues

Use GitHub Issues with these templates:

### Bug Report
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details

### Feature Request
- Problem statement
- Proposed solution
- Phase (1, 2, or 3)
- Alternatives considered

## Questions?

- Open a [GitHub Discussion](https://github.com/Amankumar006/IKS-MODEL/discussions)
- Email: your-email@example.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🙏
