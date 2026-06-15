"""Gradio web interface for IKS RAG system.

Provides a chat interface for students to ask IKS questions.
"""

# Load .env FIRST — must happen before iks_rag imports so API keys are available
try:
    from dotenv import load_dotenv

    load_dotenv()  # loads from .env in cwd (project root)
except ImportError:
    pass

import gradio as gr

from iks_rag.config import RAGConfig, load_config
from iks_rag.rag_system import RAGSystem


def format_examples(config: RAGConfig) -> str:
    """Format example questions.

    Args:
        config: RAG configuration

    Returns:
        Formatted markdown string
    """
    examples = config.ui.examples
    md = "### Example Questions\n\n"
    for i, ex in enumerate(examples, 1):
        md += f"{i}. {ex}\n\n"
    return md


def handle_response(message: str, chat_history: list, rag_system: RAGSystem) -> tuple[str, list]:
    """Process user message and generate response.

    Args:
        message: User input message
        chat_history: Current chat history
        rag_system: RAG system instance

    Returns:
        Tuple of (empty string, updated chat history)
    """
    if not message.strip():
        return "", chat_history

    # Add user message (Gradio 6.0 message format)
    chat_history.append({"role": "user", "content": message})

    try:
        # Query RAG system
        result = rag_system.query(message)
        answer = result["answer"]

        # Format sources
        sources_text = "\n\n**Sources:**\n"
        for i, source in enumerate(result["sources"][:3], 1):
            file_name = source["metadata"].get("file_name", "Unknown")
            sources_text += f"\n{i}. {file_name}"

        full_response = f"{answer}{sources_text}"

        chat_history.append({"role": "assistant", "content": full_response})
        return "", chat_history

    except Exception as e:
        error_msg = (
            f"❌ Error: {str(e)}\n\nPlease ensure:\n- API keys are set\n- Documents are loaded"
        )
        chat_history.append({"role": "assistant", "content": error_msg})
        return "", chat_history


def create_interface(rag_system: RAGSystem) -> gr.Blocks:
    """Create Gradio interface.

    Args:
        rag_system: Initialized RAG system

    Returns:
        Configured Gradio Blocks interface
    """
    config = load_config()

    css = """
    .gradio-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .source-box {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
    }
    .answer-box {
        background-color: #fff7e6;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ff8c00;
    }
    """

    with gr.Blocks(css=css, title=config.ui.title) as demo:
        gr.Markdown(f"# {config.ui.title}")
        gr.Markdown(config.ui.description)

        # System status
        with gr.Row(), gr.Column(scale=1):
            stats = rag_system.get_stats()
            status_text = f"📚 **Documents**: {stats['documents_loaded']}\n\n"
            status_text += f"🤖 **Model**: {stats['config']['model']}\n\n"
            status_text += f"🔤 **Embeddings**: {stats['config']['embeddings'].split('/')[-1]}"
            gr.Markdown(status_text)

        # Chat interface
        chatbot = gr.Chatbot(
            label="IKS Assistant",
            height=400,
        )

        with gr.Row():
            msg = gr.Textbox(
                label="Ask a question about Indian Knowledge Systems",
                placeholder="What are the 72 Melakarta ragas?",
                scale=10,
            )
            submit = gr.Button("Ask", variant="primary", scale=1)

        with gr.Row():
            clear = gr.Button("Clear Chat")
            examples_btn = gr.Button("Show Examples")

        # Examples section (hidden by default)
        examples_md = gr.Markdown(visible=False)

        def respond(message: str, chat_history: list):
            return handle_response(message, chat_history, rag_system)

        def clear_chat():
            """Clear chat history."""
            return []

        def toggle_examples():
            """Toggle examples visibility."""
            return gr.update(visible=True, value=format_examples(config))

        # Event handlers
        submit.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(clear_chat, None, chatbot)
        examples_btn.click(toggle_examples, None, examples_md)

        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "**Note**: This system retrieves information from curated IKS documents. "
            "Answers include source citations for verification."
        )

    return demo


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="IKS RAG Assistant")
    parser.add_argument(
        "--config",
        default="configs/rag/default.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to bind to",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create public shareable link",
    )

    args = parser.parse_args()

    print("🚀 Initializing IKS RAG System...")

    # Create RAG system
    from iks_rag.rag_system import create_rag_system

    rag_system = create_rag_system(args.config)

    # Load documents
    print("📚 Loading documents...")
    rag_system.load_documents()

    stats = rag_system.get_stats()
    print(f"✅ Loaded {stats['documents_loaded']} documents")

    # Create interface
    demo = create_interface(rag_system)

    print(f"🌐 Starting server on http://{args.host}:{args.port}")

    # Launch
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True,
    )


if __name__ == "__main__":
    main()
