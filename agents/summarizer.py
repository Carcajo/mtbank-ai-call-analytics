from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from utils.logger import log_agent_io
from typing import List
from agents import get_llm, AgentState


class SummaryResult(BaseModel):
    summary: str = Field(description="Краткое содержание диалога в 2-3 предложениях. О чем договорились.")
    action_items: List[str] = Field(
        description="Список конкретных действий (Action Items) по итогам звонка. Если действий не требуется, верни пустой список [].")


@log_agent_io("Summarizer")
def summarizer_node(state: AgentState) -> dict:
    print("📝 [Agent: Summarizer] Подготовка резюме и списка задач...")

    transcript_data = state.get("transcript", [])
    if not transcript_data:
        print("⚠️ [Agent: Summarizer] Транскрипт пуст.")
        return {"summary": "Транскрипт отсутствует.", "action_items": []}

    dialog_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in transcript_data])

    system_prompt = """Ты — помощник супервайзера контакт-центра МТБанка.
    Твоя задача — составить очень краткое саммари диалога и выделить конкретные задачи (action items).

    СТРОГИЕ ПРАВИЛА:
    1. summary: МАКСИМУМ 2-3 предложения. Только суть проблемы и итог. Никаких рассуждений.
    2. action_items: Выпиши списком только реальные действия для сотрудников банка (если они нужны). Если действий нет, верни пустой список.

    ВАЖНОЕ ПРАВИЛО: 
    Отвечай СТРОГО на русском языке. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать китайские иероглифы, английский язык или писать технические комментарии. Только чистый русский текст.

    Диалог:
    {dialog}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(SummaryResult)

        chain = prompt | structured_llm
        result = chain.invoke({"dialog": dialog_text})

        print(f"   ✓ Резюме готово. Action items: {len(result.action_items)} шт.")

        return {
            "summary": result.summary,
            "action_items": result.action_items
        }

    except Exception as e:
        print(f"❌ [Agent: Summarizer] Ошибка LLM: {e}")
        return {"summary": "Ошибка генерации резюме.", "action_items": []}
