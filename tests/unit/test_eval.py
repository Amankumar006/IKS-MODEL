import sys
from pathlib import Path

# Add scripts directory to path
SYS_PATH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS_PATH))

from scripts.eval.evaluate_constraints import count_sentences, check_constraint


def test_count_sentences():
    assert count_sentences("This is one. This is two!") == 2
    assert count_sentences("Namaste! How are you today? I am fine.") == 3
    assert count_sentences("") == 0
    assert count_sentences("   ") == 0


def test_one_word_constraint():
    passed, msg = check_constraint("one_word", "Patna")
    assert passed
    
    passed, msg = check_constraint("one_word", "Patna is great")
    assert not passed


def test_number_only_constraint():
    passed, msg = check_constraint("number_only", "42")
    assert passed
    
    passed, msg = check_constraint("number_only", "four")
    assert not passed


def test_json_only_constraint():
    passed, msg = check_constraint("json_only", '{"key": "value"}')
    assert passed
    
    passed, msg = check_constraint("json_only", "not json")
    assert not passed


def test_list_count_constraint():
    passed, msg = check_constraint("list_count_3", "1. Item one\n2. Item two\n3. Item three")
    assert passed
    
    passed, msg = check_constraint("list_count_3", "1. Item one\n2. Item two")
    assert not passed


def test_sentence_count_constraint():
    passed, msg = check_constraint("sentence_count_2", "This is sentence one. This is sentence two.")
    assert passed
    
    passed, msg = check_constraint("sentence_count_2", "This is sentence one.")
    assert not passed
