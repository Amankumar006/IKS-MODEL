# Local Setup Guide

## Prerequisites

**Hardware Requirements** (Flexible):
| Setup | Hardware | Recommended Model |
|-------|----------|-------------------|
| Minimum | 16GB RAM, 4GB VRAM | `mistral:7b` (4-bit) |
| Better | 32GB RAM, RTX 3060 (12GB) | `mistral:7b` |
| Best | 64GB RAM, RTX 4090 (24GB) | Mistral 7B or fine-tuned adapter |

*Note: For the Gemini API fallback, you only need internet access, as inference runs on Google's servers.*

## Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/Amankumar006/IKS-MODEL.git
cd IKS-MODEL

# 2. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Optional: Install Ollama (if using local models instead of Gemini)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral:7b

# 5. Set up API Keys
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY for Gemini

# 6. Download IKS documents
python scripts/data/download_sample_docs.py

# 7. Launch the assistant
uv run python src/iks_rag/ui/gradio_app.py
```

### Usage
- Web Interface: http://localhost:7860
- API Docs: http://localhost:8000/docs
