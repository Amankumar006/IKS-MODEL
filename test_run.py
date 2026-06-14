import sys
from pathlib import Path

# Add scripts/data to path
sys.path.append(str(Path("scripts/data").resolve()))
from generate_qa_pairs import process_file

if __name__ == "__main__":
    test_file = Path("data/documents/wiki_Madhubani_painting.txt")
    print(f"Running test on {test_file}")
    process_file(test_file)
