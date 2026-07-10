import pytest
from agents.classifier import classifier_node
from agents.quality import quality_node
from agents.compliance import compliance_node
from agents.summarizer import summarizer_node


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


def test_classifier_node(sample_transcript):
    """Тест агента классификации."""
    state = {"transcript": sample_transcript}
    result = classifier_node(state)

    assert "classification" in result
    assert "topic" in result["classification"]
    assert "priority" in result["classification"]
    assert isinstance(result["classification"]["topic"], str)
    assert result["classification"]["priority"] in ["low", "medium", "high", "critical"]


def test_quality_node(sample_transcript):
    """Тест агента оценки качества (QA)."""
    state = {"transcript": sample_transcript}
    result = quality_node(state)

    assert "quality_score" in result
    assert "total" in result["quality_score"]
    assert "checklist" in result["quality_score"]
    assert isinstance(result["quality_score"]["total"], (int, float))
    assert 0 <= result["quality_score"]["total"] <= 100

    checklist = result["quality_score"]["checklist"]
    for key in ["greeting", "need_detection", "solution_provided", "farewell"]:
        assert key in checklist
        assert isinstance(checklist[key], bool)


def test_compliance_node(sample_transcript):
    """Тест агента комплаенса."""
    state = {"transcript": sample_transcript}
    result = compliance_node(state)

    assert "compliance" in result
    assert "passed" in result["compliance"]
    assert "issues" in result["compliance"]
    assert isinstance(result["compliance"]["passed"], bool)
    assert isinstance(result["compliance"]["issues"], list)


def test_summarizer_node(sample_transcript):
    """Тест агента суммаризации."""
    state = {"transcript": sample_transcript}
    result = summarizer_node(state)

    assert "summary" in result
    assert "action_items" in result
    assert isinstance(result["summary"], str)
    assert isinstance(result["action_items"], list)
