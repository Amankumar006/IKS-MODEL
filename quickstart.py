#!/usr/bin/env python3
"""Quick start script for IKS RAG system.

This script helps you:
1. Check prerequisites (Ollama, models)
2. Download sample documents
3. Test the RAG system
4. Launch the web interface
"""

import subprocess
import sys
from pathlib import Path


def check_command(command: str, name: str) -> bool:
    """Check if a command is available."""
    try:
        subprocess.run(
            [command, "--version"],
            capture_output=True,
            check=True,
        )
        print(f"✅ {name} is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {name} is not installed")
        return False


def check_ollama_model(model: str) -> bool:
    """Check if Ollama model is available."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        if model in result.stdout:
            print(f"✅ Model '{model}' is available")
            return True
        else:
            print(f"⚠️  Model '{model}' not found")
            return False
    except subprocess.CalledProcessError:
        print("❌ Could not check Ollama models")
        return False


def setup_documents():
    """Download sample documents."""
    print("\n📚 Setting up documents...")

    script_path = Path("scripts/data/download_sample_docs.py")
    if not script_path.exists():
        print("❌ Download script not found")
        return False

    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download documents: {e}")
        return False


def test_rag_system():
    """Test the RAG system."""
    print("\n🧪 Testing RAG system...")

    test_script = """
from iks_rag.rag_system import create_rag_system

print("Initializing RAG system...")
rag = create_rag_system()

print("Loading documents...")
rag.load_documents()

print(f"Loaded {rag.get_stats()['documents_loaded']} documents")

print("\\nTesting query...")
result = rag.query("What are Melakarta ragas?")
print(f"Answer: {result['answer'][:200]}...")
print(f"Sources: {len(result['sources'])} documents")
print("\\n✅ RAG system is working!")
"""

    try:
        subprocess.run(
            [sys.executable, "-c", test_script],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ RAG test failed: {e}")
        return False


def launch_ui():
    """Launch the web interface."""
    print("\n🚀 Launching web interface...")
    print("Open your browser at: http://localhost:7860")
    print("Press Ctrl+C to stop\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "src.iks_rag.ui.gradio_app"],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch UI: {e}")


def main():
    """Main function."""
    print("=" * 60)
    print("🏛️  IKS AI Assistant - Quick Start")
    print("=" * 60)

    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        return 1

    # Check Ollama
    print("\n🔍 Checking prerequisites...")
    if not check_command("ollama", "Ollama"):
        print("\nPlease install Ollama:")
        print("  macOS: brew install ollama")
        print("  Linux: curl -fsSL https://ollama.com/install.sh | sh")
        print("  Then run: ollama serve")
        return 1

    # Check model
    if not check_ollama_model("gemma3:4b"):
        print("\n📥 Downloading model...")
        try:
            subprocess.run(["ollama", "pull", "gemma3:4b"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to download model")
            return 1

    # Setup documents
    docs_exist = any(Path("data/documents").glob("*.txt"))
    if not docs_exist:
        if not setup_documents():
            print("❌ Failed to setup documents")
            return 1
    else:
        print("✅ Documents already exist")

    # Test RAG system
    print("\n⏳ This may take a minute...")
    print("   (Downloading embedding model on first run)")

    if not test_rag_system():
        print("\n⚠️  RAG test failed, but let's try launching anyway...")

    # Launch UI
    launch_ui()

    return 0


if __name__ == "__main__":
    sys.exit(main())
