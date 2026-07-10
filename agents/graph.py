from langgraph.graph import StateGraph, END
from agents import AgentState
from agents.classifier import classifier_node
from agents.quality import quality_node
from agents.compliance import compliance_node
from agents.summarizer import summarizer_node


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("quality", quality_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.set_entry_point("classifier")
    workflow.add_edge("classifier", "quality")
    workflow.add_edge("quality", "compliance")
    workflow.add_edge("compliance", "summarizer")
    workflow.add_edge("summarizer", END)

    return workflow.compile()


app_graph = build_graph()


def run_agentic_analysis(transcript: list) -> dict:
    print("\n🚀 [Graph] Запуск multi-agent конвейера...")

    initial_state = {
        "transcript": transcript,
        "classification": {},
        "quality_score": {},
        "compliance": {},
        "summary": "",
        "action_items": []
    }

    final_state = app_graph.invoke(initial_state)

    print("✅ [Graph] Анализ успешно завершен!\n")

    return final_state
