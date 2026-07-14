import pytest
import os

from unittest.mock import patch, MagicMock
from agents.graph import run_agentic_analysis
from agents.classifier import ClassificationResult
from agents.quality import QualityChecklist
from agents.compliance import ComplianceCheck


os.environ["OPENROUTER_API_KEY"] = "dummy_test_key"
os.environ["HF_TOKEN"] = "dummy_test_key"

PATCH_TARGET = "langchain_core.runnables.RunnableSequence.invoke"


@patch(PATCH_TARGET)
def test_full_agentic_pipeline(mock_invoke):
    mock_summary = MagicMock()
    mock_summary.summary = "Тестовое резюме"
    mock_summary.action_items = []
    mock_summary.model_dump.return_value = {"summary": "Тестовое резюме", "action_items": []}

    mock_invoke.side_effect = [
        ClassificationResult(topic="кредиты", priority="medium"),
        QualityChecklist(greeting=True, need_detection=True, solution_provided=True, farewell=True),
        ComplianceCheck(passed=True, issues=[]),
        mock_summary
    ]

    mock_transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 3.0, "text": "МТБанк, Алексей, здравствуйте."},
        {"speaker": "Клиент", "start": 3.5, "end": 6.0, "text": "Скажите, какой процент по кредиту?"},
        {"speaker": "Оператор", "start": 6.5, "end": 9.0, "text": "У нас ставка двадцать процентов годовых. Оформляем?"},
        {"speaker": "Клиент", "start": 9.5, "end": 11.0, "text": "Нет, спасибо, я подумаю."},
        {"speaker": "Оператор", "start": 11.5, "end": 13.0, "text": "Хорошо, до свидания."}
    ]

    final_state = run_agentic_analysis(mock_transcript)

    assert isinstance(final_state, dict)
    assert final_state["transcript"] == mock_transcript
    assert "topic" in final_state["classification"]
    assert "total" in final_state["quality_score"]
    assert mock_invoke.call_count == 4
