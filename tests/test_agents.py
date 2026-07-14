import pytest
import os
from unittest.mock import patch, MagicMock
from agents.classifier import classifier_node, ClassificationResult
from agents.quality import quality_node, QualityChecklist
from agents.compliance import compliance_node, ComplianceCheck
from agents.summarizer import summarizer_node


os.environ["OPENROUTER_API_KEY"] = "dummy_test_key"
os.environ["HF_TOKEN"] = "dummy_test_key"


@pytest.fixture
def sample_transcript():
    """Фикстура с тестовым диалогом для передачи агентам."""
    return [
        {"speaker": "Оператор", "start": 0.0, "end": 4.0,
         "text": "Добрый день, МТБанк, меня зовут Алексей. Чем могу помочь?"},
        {"speaker": "Клиент", "start": 4.5, "end": 8.0,
         "text": "Здравствуйте, я хочу отключить СМС-оповещения по карте."},
        {"speaker": "Оператор", "start": 8.5, "end": 12.0,
         "text": "Хорошо, услугу мы успешно отключили. Всего доброго, до свидания!"}
    ]


PATCH_TARGET = "langchain_core.runnables.RunnableSequence.invoke"


@patch(PATCH_TARGET)
def test_classifier_node(mock_invoke, sample_transcript):
    """Тест агента классификации."""
    mock_invoke.return_value = ClassificationResult(topic="кредиты", priority="medium")

    state = {"transcript": sample_transcript}
    result = classifier_node(state)

    assert "classification" in result
    assert result["classification"]["topic"] == "кредиты"
    assert mock_invoke.called


@patch(PATCH_TARGET)
def test_quality_node(mock_invoke, sample_transcript):
    """Тест агента оценки качества (QA)."""
    mock_invoke.return_value = QualityChecklist(
        greeting=True, need_detection=True, solution_provided=True, farewell=True
    )

    state = {"transcript": sample_transcript}
    result = quality_node(state)

    assert "quality_score" in result
    assert result["quality_score"]["total"] == 100


@patch(PATCH_TARGET)
def test_compliance_node(mock_invoke, sample_transcript):
    """Тест агента комплаенса."""
    mock_invoke.return_value = ComplianceCheck(passed=True, issues=[])

    state = {"transcript": sample_transcript}
    result = compliance_node(state)

    assert "compliance" in result
    assert result["compliance"]["passed"] is True


@patch(PATCH_TARGET)
def test_summarizer_node(mock_invoke, sample_transcript):
    """Тест агента суммаризации."""
    mock_res = MagicMock()
    mock_res.summary = "Клиент отключил СМС-оповещения."
    mock_res.action_items = ["Отключить услугу"]
    mock_res.model_dump.return_value = {"summary": "Клиент отключил СМС-оповещения.",
                                        "action_items": ["Отключить услугу"]}

    mock_invoke.return_value = mock_res

    state = {"transcript": sample_transcript}
    result = summarizer_node(state)

    assert "summary" in result
    assert isinstance(result["summary"], str)
