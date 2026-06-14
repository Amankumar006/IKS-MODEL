# Deployment Guide

This guide covers deploying the IKS AI Assistant to HuggingFace Spaces.

## Architecture
```
User → HuggingFace Spaces (free CPU)
          ↓
     ChromaDB (4,516 chunks, stored in Space)
          ↓
     Google Gemini API (free, 1,500 req/day)
          ↓
     Beautiful IKS answer with citations
```

## HuggingFace Spaces Deployment

### Prerequisites
- HuggingFace account (free)
- Google Gemini API key
- Local testing completed

### Step 1: Create HF Space
1. Go to: https://huggingface.co/new-space
2. Name: `iks-ai-assistant`
3. SDK: **Gradio**
4. Hardware: **CPU (free)**
5. Click "Create Space"

### Step 2: Add Gemini Key as Secret
1. Go to your Space → Settings → Variables and secrets
2. Click "New secret"
3. Name: `GOOGLE_API_KEY`
4. Value: `AIza...your-key-here`
5. Save

### Step 3: Prepare Files
```bash
# Create app.py for HF Spaces
cd /Users/amankumar/Aman/IKS-Model

# Create requirements.txt for HF
cat > requirements.txt << EOF
llama-index>=0.12.0
llama-index-llms-gemini>=0.4.0
llama-index-embeddings-huggingface>=0.5.0
llama-index-vector-stores-chroma>=0.4.0
llama-index-readers-file>=0.1.0
chromadb>=0.6.0
sentence-transformers>=3.0.0,<4.0.0
transformers<4.42.0
numpy>=1.26.0,<2.0.0
gradio>=5.0.0
google-generativeai>=0.8.0
EOF

# Clone your HF Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/iks-ai-assistant
cd iks-ai-assistant

# Copy files
cp -r ../src ./
cp -r ../configs ./
cp -r ../data/documents ./data/
cp ../requirements.txt ./

# Create app.py (entry point for HF Spaces)
cat > app.py << 'EOF'
import os
import sys
sys.path.insert(0, "src")

from iks_rag.ui.gradio_app import create_interface

# Get Gemini key from HF secrets
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")

demo = create_interface()
demo.launch()
EOF

# Push to HF
git add .
git commit -m "Deploy IKS AI Assistant with Gemini"
git push
```

### Step 4: Verify Deployment
1. Go to your Space URL
2. Wait for build to complete (2-5 minutes)
3. Test query: "What are Melakarta ragas?"
4. Verify response uses Bharat persona
