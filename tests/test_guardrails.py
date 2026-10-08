import pytest
from src.guardrails.scope_guard import ScopeGuard
from src.guardrails.relevance_check import RelevanceChecker

def test_medical_blocked():
    guard = ScopeGuard()
    assert guard.is_out_of_scope("Can you diagnose my rash?") == True

def test_calorie_blocked():
    guard = ScopeGuard()
    assert guard.is_out_of_scope("How many calories should I eat daily?") == True

def test_weight_blocked():
    guard = ScopeGuard()
    assert guard.is_out_of_scope("What's a good BMI for my age?") == True

def test_valid_diet_question():
    guard = ScopeGuard()
    assert guard.is_out_of_scope("What does WHO say about salt intake?") == False

def test_valid_storage_question():
    guard = ScopeGuard()
    assert guard.is_out_of_scope("How long can I keep beef in the fridge?") == False

def test_relevance_check_filters_low_score():
    checker = RelevanceChecker()
    # Mocking chroma results with distances
    # RELEVANCE_THRESHOLD is 0.6, meaning distance <= 0.4
    mock_results = {
        "distances": [[0.3, 0.8, 0.35]],
        "documents": [["doc1", "doc2", "doc3"]],
        "metadatas": [[{"id": 1}, {"id": 2}, {"id": 3}]]
    }
    
    relevant = checker.check_relevance(mock_results)
    
    assert len(relevant) == 2
    assert relevant[0]["text"] == "doc1"
    assert relevant[1]["text"] == "doc3"
    
def test_relevance_check_empty_if_none_pass():
    checker = RelevanceChecker()
    mock_results = {
        "distances": [[0.8, 0.9, 0.75]],
        "documents": [["doc1", "doc2", "doc3"]],
        "metadatas": [[{"id": 1}, {"id": 2}, {"id": 3}]]
    }
    relevant = checker.check_relevance(mock_results)
    assert len(relevant) == 0
