"""
AI PROCESSING FUNCTIONS FOR MEETING ANALYSIS
-------------------------------------------
This file implements the individual AI processing functions that extract information
from meeting transcripts. Each function has a specific purpose:

- ingest_local_text: Validates and prepares the transcript for processing
- extract_agenda: Identifies and lists key agenda items from the transcript
- extract_decisions: Finds formal decisions that were made during the meeting
- assign_tasks: Recognizes action items and who they were assigned to
- draft_minutes: Creates a formatted summary of the meeting in Markdown

Each function uses AI prompts to intelligently extract specific information types
from natural language text, then returns structured data for the next step.
"""

from datetime import date
from typing import Dict, Any, List
from src.models.schemas import MeetingState, Task
from src.services.openai_service import chat_5_8_sentences
from src.utils.json_utils import robust_json_parse
from src.config.settings import logger

SYSTEM = "You convert meeting transcripts into structured outputs."

def ingest_local_text(state: MeetingState) -> Dict[str, Any]:
    if not state.transcript:
        raise ValueError("Transcript missing. Provide it before invoking graph.")
    # Return the transcript to update the state
    return {"transcript": state.transcript}

def extract_agenda(state: MeetingState) -> Dict[str, Any]:
    user = f"""From this transcript, list concise agenda bullets (max 8).
Return JSON: {{"agenda": ["..."]}}.
Transcript:
{state.transcript}
"""
    out = chat_5_8_sentences(SYSTEM, user)
    data = robust_json_parse(out)
    agenda = data.get("agenda", [])
    logger.info(f"Agenda extracted: {agenda}")
    return {"agenda": agenda}

def extract_decisions(state: MeetingState) -> Dict[str, Any]:
    user = f"""From the transcript, list explicit decisions. 
Return JSON: {{"decisions":["..."]}}.
Transcript:
{state.transcript}
"""
    out = chat_5_8_sentences(SYSTEM, user)
    data = robust_json_parse(out)
    decisions = data.get("decisions", [])
    logger.info(f"Decisions extracted: {decisions}")
    return {"decisions": decisions}

def assign_tasks(state: MeetingState) -> Dict[str, Any]:
    user = f"""Extract action items with owner, task, due (YYYY-MM-DD if mentioned; else empty), 
and priority (High/Med/Low).
Return JSON: {{"tasks":[{{"owner":"","task":"","due":"","priority":""}}]}} 
Transcript:
{state.transcript}
"""
    out = chat_5_8_sentences(SYSTEM, user)
    data = robust_json_parse(out)
    raw_tasks = data.get("tasks", [])
    tasks: List[Task] = []
    for t in raw_tasks:
        # Normalize priority to match our enum
        priority = (t.get("priority") or "Med").strip()
        if priority.lower() == "medium":
            priority = "Med"
        elif priority.lower() == "high":
            priority = "High"
        elif priority.lower() == "low":
            priority = "Low"
        else:
            priority = "Med"  # Default
            
        tasks.append(Task(
            owner=(t.get("owner") or "TBD").strip(),
            task=(t.get("task") or "").strip(),
            due=(t.get("due") or "").strip(),
            priority=priority
        ))
    logger.info(f"Tasks extracted: {[t.model_dump() for t in tasks]}")
    return {"tasks": [t.model_dump() for t in tasks]}

def draft_minutes(state: MeetingState) -> Dict[str, Any]:
    today = date.today().isoformat()
    agenda = state.agenda or ["(none)"]
    decisions = state.decisions or ["(none)"]
    tasks = state.tasks or []

    lines = [
        f"# Meeting Minutes — {today}",
        "## Agenda",
        *[f"- {a}" for a in agenda],
        "\n## Decisions",
        *[f"- {d}" for d in decisions],
        "\n## Action Items",
    ]
    if tasks:
        for t in tasks:
            # Access Task attributes directly, not using get() method
            lines.append(
                f"- **{t.owner}**: {t.task}"
                f" (Due: {t.due or 'TBD'}, Priority: {t.priority})"
            )
    else:
        lines.append("- (none)")

    md = "\n".join(lines)
    logger.info("Minutes drafted.")
    return {"minutes_md": md}
