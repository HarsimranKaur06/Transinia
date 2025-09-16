"""
WORKFLOW DEFINITION AND ORCHESTRATION
-----------------------------------
This file configures the LangGraph workflow that organizes the analysis steps.
Specifically, it:

1. Creates a directed graph of processing steps
2. Defines the exact sequence of operations
3. Connects the nodes in the correct order
4. Sets up checkpointing for reliability
5. Compiles the graph into an executable application

The create_graph() function returns a compiled workflow that can process
meeting transcripts through the complete analysis pipeline in the right order.
"""

from langgraph.graph import StateGraph, END
from src.models.schemas import MeetingState
from src.agents.nodes import (
    ingest_local_text, extract_title, extract_agenda, extract_decisions, 
    extract_participants, assign_tasks, draft_minutes
)

def create_graph():
    """
    Create the LangGraph workflow for meeting processing.
    This creates a directed graph of nodes that process the meeting transcript.
    """
    # Create state graph with MeetingState
    graph = StateGraph(MeetingState)

    # Add processing nodes
    graph.add_node("ingest_local_text", ingest_local_text)
    graph.add_node("extract_title", extract_title)
    graph.add_node("extract_agenda", extract_agenda)
    graph.add_node("extract_decisions", extract_decisions)
    graph.add_node("extract_participants", extract_participants)
    graph.add_node("assign_tasks", assign_tasks)
    graph.add_node("draft_minutes", draft_minutes)

    # Connect nodes in sequence
    graph.set_entry_point("ingest_local_text")
    graph.add_edge("ingest_local_text", "extract_title")
    graph.add_edge("extract_title", "extract_agenda")
    graph.add_edge("extract_agenda", "extract_decisions")
    graph.add_edge("extract_decisions", "extract_participants")
    graph.add_edge("extract_participants", "assign_tasks")
    graph.add_edge("assign_tasks", "draft_minutes")
    graph.add_edge("draft_minutes", END)

    # Compile graph without any extra parameters
    app = graph.compile()
    return app
