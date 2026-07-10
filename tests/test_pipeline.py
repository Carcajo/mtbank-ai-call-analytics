import pytest
from agents.graph import run_agentic_analysis


def test_full_agentic_pipeline():
    mock_transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 3.0, "text": "МТБанк, Алексей, здравствуйте."},
        {"speaker": "Клиент", "start": 3.5, "end": 6.0, "text": "Скажите, какой процент по кредиту?"},
        {"speaker": "Оператор", "start": 6.5, "end": 9.0,
         "text": "У нас ставка двадцать процентов годовых. Оформляем?"},
        {"speaker": "Клиент", "start": 9.5, "end": 11.0, "text": "Нет, спасибо, я подумаю."},
        {"speaker": "Оператор", "start": 11.5, "end": 13.0, "text": "Хорошо, до свидания."}
    ]

    final_state = run_agentic_analysis(mock_transcript)

    assert isinstance(final_state, dict)
    assert final_state["transcript"] == mock_transcript

    assert "topic" in final_state["classification"]
    assert "total" in final_state["quality_score"]
    assert "passed" in final_state["compliance"]
    assert isinstance(final_state["summary"], str) and len(final_state["summary"]) > 0
    assert isinstance(final_state["action_items"], list)
