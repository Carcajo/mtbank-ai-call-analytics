from langchain_core.prompts import ChatPromptTemplate
from utils.logger import log_agent_io
from pydantic import BaseModel, Field
from agents import get_llm, AgentState


class ClassificationResult(BaseModel):
    topic: str = Field(description="Тематика обращения. Строго одно из: кредиты, карты, переводы, жалобы, другое.")
    priority: str = Field(description="Приоритет обращения: low, medium, high, critical.")


@log_agent_io("Classifier")
def classifier_node(state: AgentState) -> dict:
    print("🧠 [Agent: Classifier] Анализ тематики и приоритета...")

    transcript_data = state.get("transcript", [])
    if not transcript_data:
        print("⚠️ [Agent: Classifier] Транскрипт пуст.")
        return {"classification": {"topic": "unknown", "priority": "low"}}

    dialog_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in transcript_data])

    system_prompt = """Ты — опытный AI-супервайзер контакт-центра МТБанка. 
Твоя задача — проанализировать диалог между Оператором и Клиентом и извлечь метаданные.

ПРАВИЛА ОПРЕДЕЛЕНИЯ ПРИОРИТЕТА:
- low: обычные справочные вопросы.
- medium: заявки на услуги, стандартные операции.
- high: финансовые потери, неработающие карты, технические сбои.
- critical: открытая агрессия, угроза судом, мошенничество.

Диалог:
{dialog}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(ClassificationResult)

        chain = prompt | structured_llm
        result = chain.invoke({"dialog": dialog_text})

        print(f"   ✓ Определена тема: {result.topic} (Приоритет: {result.priority})")

        return {"classification": {"topic": result.topic, "priority": result.priority}}

    except Exception as e:
        print(f"❌ [Agent: Classifier] Ошибка LLM: {e}")
        return {"classification": {"topic": "error", "priority": "low"}}
