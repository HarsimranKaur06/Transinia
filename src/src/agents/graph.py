from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.models.schemas import MeetingState
from src.agents.nodes import (
    ingest_local_text, extract_agenda, extract_decisions, assign_tasks, draft_minutes
)

def build_app():
    graph = StateGraph(MeetingState)

    graph.add_node("ingest_local_text", ingest_local_text)
    graph.add_node("extract_agenda", extract_agenda)
    graph.add_node("extract_decisions", extract_decisions)
    graph.add_node("assign_tasks", assign_tasks)
    graph.add_node("draft_minutes", draft_minutes)

    graph.set_entry_point("ingest_local_text")
    graph.add_edge("ingest_local_text", "extract_agenda")
    graph.add_edge("extract_agenda", "extract_decisions")
    graph.add_edge("extract_decisions", "assign_tasks")
    graph.add_edge("assign_tasks", "draft_minutes")
    graph.add_edge("draft_minutes", END)

    app = graph.compile(checkpointer=MemorySaver())
    return app
