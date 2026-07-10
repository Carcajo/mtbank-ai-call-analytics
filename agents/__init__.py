import os
from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI


class AgentState(TypedDict):
    transcript: List[Dict[str, Any]]
    classification: Dict[str, str]
    quality_score: Dict[str, Any]
    compliance: Dict[str, Any]
    summary: str
    action_items: List[str]


def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("ВНИМАНИЕ: OPENROUTER_API_KEY не найден в переменных окружения!")

    return ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key,
        model_name="qwen/qwen-2.5-7b-instruct",
        temperature=0.1,
        max_tokens=500,
    )
