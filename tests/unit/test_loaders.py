import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from iks_rag.ingestion.loaders import DocumentLoader

def test_extract_category():
    """Test the category extraction logic based on filenames."""
    loader = DocumentLoader(documents_path="./data/docs")
    
    assert loader._extract_category("Upanishad_Isha.pdf") == "philosophy"
    assert loader._extract_category("Chola_Empire_Architecture.md") == "temples"
    assert loader._extract_category("Ragas_Carnatic.txt") == "music"
    assert loader._extract_category("Bharatanatyam_Guide.html") == "music"  # 'natya' matches music in code
    assert loader._extract_category("Random_File.pdf") == "general"

def test_load_text_file(tmp_path):
    """Test loading a plain text file."""
    loader = DocumentLoader(documents_path=tmp_path)
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello IKS", encoding="utf-8")
    
    docs = loader._load_text_file(file_path)
    assert len(docs) == 1
    assert docs[0].text == "Hello IKS"
    assert docs[0].metadata["file_name"] == "test.txt"
    assert docs[0].metadata["category"] == "general"

@patch("iks_rag.ingestion.loaders.SimpleDirectoryReader")
def test_load_all(mock_reader_cls, temp_doc_dir):
    """Test load_all method by mocking SimpleDirectoryReader."""
    mock_reader = mock_reader_cls.return_value
    mock_reader.load_data.return_value = [MagicMock(metadata={})]
    
    loader = DocumentLoader(documents_path=temp_doc_dir)
    docs = loader.load_all()
    
    assert len(docs) == 1
    assert docs[0].metadata["source"] == "iks_corpus"
    mock_reader_cls.assert_called_once()

def test_load_single_not_found():
    """Test load_single raises FileNotFoundError if file missing."""
    loader = DocumentLoader(documents_path="./")
    with pytest.raises(FileNotFoundError):
        loader.load_single("non_existent.pdf")

def test_load_single_unsupported_format(tmp_path):
    """Test load_single raises ValueError for unsupported formats."""
    loader = DocumentLoader(documents_path=tmp_path)
    file_path = tmp_path / "test.exe"
    file_path.write_text("binary", encoding="utf-8")
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        loader.load_single(file_path)
