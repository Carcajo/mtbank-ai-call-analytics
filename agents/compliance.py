from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from utils.logger import log_agent_io
from typing import List
from agents import get_llm, AgentState


class ComplianceCheck(BaseModel):
    passed: bool = Field(
        description="Успешно ли пройден комплаенс-контроль. True - если нарушений НЕТ. False - если найдено ХОТЯ БЫ ОДНО нарушение.")
    issues: List[str] = Field(
        description="Список конкретных цитат оператора, которые нарушают правила. Если нарушений нет, список должен быть пустым.")


@log_agent_io("Compliance")
def compliance_node(state: AgentState) -> dict:
    print("🛡️ [Agent: Compliance] Проверка разговора на нарушения безопасности...")

    transcript_data = state.get("transcript", [])
    if not transcript_data:
        print("⚠️ [Agent: Compliance] Транскрипт пуст.")
        return {"compliance": {"passed": True, "issues": []}}

    dialog_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in transcript_data])

    system_prompt = """Ты — строгий офицер службы безопасности (Compliance Officer) контакт-центра МТБанка.
Твоя задача — проверить реплики Оператора на предмет грубых нарушений.
Оцениваются ТОЛЬКО слова Оператора.

КРИТИЧЕСКИЕ НАРУШЕНИЯ (КРАСНЫЕ ФЛАГИ):
1. Запрос конфиденциальных данных: ПИН-код, CVV/CVC, пароли из СМС, полный номер карты (можно спрашивать только последние 4 цифры).
2. Гарантия одобрения: Обещание, что кредит или рассрочка будут 100% одобрены.
3. Грубость или конфликт: Повышение тона, хамство, спор с клиентом.

Диалог:
{dialog}

Внимательно проанализируй диалог. Если есть нарушения, passed = false, и перечисли цитаты в issues. Если всё чисто, passed = true, а issues оставь пустым [].
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(ComplianceCheck)

        chain = prompt | structured_llm
        result = chain.invoke({"dialog": dialog_text})

        if result.passed:
            print("   ✓ Нарушений безопасности не выявлено.")
        else:
            print(f"   🚨 НАЙДЕНЫ НАРУШЕНИЯ: {len(result.issues)} шт.")

        return {
            "compliance": {
                "passed": result.passed,
                "issues": result.issues
            }
        }

    except Exception as e:
        print(f"❌ [Agent: Compliance] Ошибка LLM: {e}")
        return {"compliance": {"passed": False, "issues": [f"Системная ошибка проверки: {str(e)}"]}}
