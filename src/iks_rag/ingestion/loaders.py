"""Document loaders for IKS knowledge base.

Supports PDF, Markdown, HTML, TXT, and JSON files.
"""

import json
from pathlib import Path
from typing import Any

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.readers.base import BaseReader
from llama_index.readers.file import (
    HTMLTagReader,
    MarkdownReader,
    PDFReader,
)


class DocumentLoader:
    """Main document loader for IKS documents.

    Supports multiple file formats and handles metadata extraction.
    """

    def __init__(self, documents_path: str | Path):
        """Initialize document loader.

        Args:
            documents_path: Path to documents directory
        """
        self.documents_path = Path(documents_path)
        self.supported_extensions = {".txt", ".md", ".pdf", ".html", ".json"}

    def load_all(self) -> list[Document]:
        """Load all documents from the directory.

        Returns:
            List of loaded documents with metadata
        """
        if not self.documents_path.exists():
            raise FileNotFoundError(
                f"Documents directory not found: {self.documents_path}"
            )

        # Use SimpleDirectoryReader with file extractors
        file_extractor = {
            ".pdf": PDFReader(),
            ".md": MarkdownReader(),
            ".html": HTMLTagReader(),
        }

        reader = SimpleDirectoryReader(
            input_dir=self.documents_path,
            file_extractor=file_extractor,
            recursive=True,
            filename_as_id=True,
        )

        documents = reader.load_data()

        # Add metadata
        for doc in documents:
            doc.metadata["source"] = "iks_corpus"
            doc.metadata["category"] = self._extract_category(doc.metadata.get("file_name", ""))

        return documents

    def load_single(self, file_path: str | Path) -> list[Document]:
        """Load a single document.

        Args:
            file_path: Path to document file

        Returns:
            List of documents (may be multiple for PDFs)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        suffix = file_path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {suffix}")

        # Use appropriate reader
        if suffix == ".pdf":
            reader = PDFReader()
        elif suffix == ".md":
            reader = MarkdownReader()
        elif suffix == ".html":
            reader = HTMLTagReader()
        else:
            # Default to simple text reader
            return self._load_text_file(file_path)

        documents = reader.load_data(file_path)

        # Add metadata
        for doc in documents:
            doc.metadata["file_name"] = file_path.name
            doc.metadata["file_path"] = str(file_path)
            doc.metadata["source"] = "iks_corpus"
            doc.metadata["category"] = self._extract_category(file_path.name)

        return documents

    def _load_text_file(self, file_path: Path) -> list[Document]:
        """Load a plain text file.

        Args:
            file_path: Path to text file

        Returns:
            List with single document
        """
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        doc = Document(
            text=text,
            metadata={
                "file_name": file_path.name,
                "file_path": str(file_path),
                "source": "iks_corpus",
                "category": self._extract_category(file_path.name),
            },
        )

        return [doc]

    def _extract_category(self, filename: str) -> str:
        """Extract document category from filename.

        Args:
            filename: Document filename

        Returns:
            Category name (e.g., 'philosophy', 'temples')
        """
        filename_lower = filename.lower()

        categories = {
            "philosophy": ["philosophy", "vedanta", "upani", "samkhya", "nyaya"],
            "temples": ["temple", "architecture", "chola", "dravidian", "nagara"],
            "music": ["music", "raga", "carnatic", "hindustani", "natya"],
            "dance": ["dance", "bharata", "kathak", "odissi"],
            "mathematics": ["math", "aryabhata", "zero", "geometry"],
            "history": ["history", "maurya", "chola", "empire"],
            "ayurveda": ["ayurveda", "charaka", "medicine"],
            "textiles": ["textile", "saree", "weaving"],
        }

        for category, keywords in categories.items():
            if any(kw in filename_lower for kw in keywords):
                return category

        return "general"

    def get_document_stats(self) -> dict[str, Any]:
        """Get statistics about documents in the directory.

        Returns:
            Dictionary with document counts by type and category
        """
        if not self.documents_path.exists():
            return {"error": "Documents directory not found"}

        files = list(self.documents_path.rglob("*"))
        files = [f for f in files if f.is_file()]

        stats = {
            "total_files": len(files),
            "by_extension": {},
            "by_category": {},
        }

        for file in files:
            ext = file.suffix.lower()
            stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1

            category = self._extract_category(file.name)
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        return stats
