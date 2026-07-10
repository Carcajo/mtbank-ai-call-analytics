from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from utils.logger import log_agent_io
from agents import get_llm, AgentState


class QualityChecklist(BaseModel):
    greeting: bool = Field(description="Поздоровался ли оператор (назвал банк и свое имя).")
    need_detection: bool = Field(
        description="Выявил ли оператор потребность или проблему клиента (запросил данные, задал уточняющие вопросы).")
    solution_provided: bool = Field(
        description="Предложил ли оператор конкретное решение проблемы или ответил ли на вопрос.")
    farewell: bool = Field(
        description="Попрощался ли оператор в конце разговора (пожелал хорошего дня, сказал до свидания).")


@log_agent_io("Quality")
def quality_node(state: AgentState) -> dict:
    print("⭐ [Agent: Quality] Оценка работы оператора по чеклисту...")

    transcript_data = state.get("transcript", [])
    if not transcript_data:
        print("⚠️ [Agent: Quality] Транскрипт пуст.")
        return {"quality_score": {"total": 0, "checklist": {}}}

    dialog_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in transcript_data])

    system_prompt = """Ты — строгий, но справедливый QA-инженер контакт-центра МТБанка. 
Твоя задача — оценить работу Оператора по заданному чеклисту на основе транскрипта звонка.
Анализируй только реплики со спикером 'Оператор'. Клиент не оценивается.

Диалог:
{dialog}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(QualityChecklist)

        chain = prompt | structured_llm
        result = chain.invoke({"dialog": dialog_text})

        checklist_dict = result.model_dump()

        total_score = sum([25 for passed in checklist_dict.values() if passed])

        print(f"   ✓ Оценка завершена. Итоговый балл: {total_score}/100")

        return {
            "quality_score": {
                "total": total_score,
                "checklist": checklist_dict
            }
        }

    except Exception as e:
        print(f"❌ [Agent: Quality] Ошибка LLM: {e}")
        return {"quality_score": {"total": 0, "checklist": {}}}
