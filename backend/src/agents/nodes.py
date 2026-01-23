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
from backend.src.models.schemas import MeetingState, Task
from backend.src.services.openai_service import chat_5_8_sentences
from backend.src.utils.json_utils import robust_json_parse
from backend.src.config.settings import logger

SYSTEM = "You convert meeting transcripts into structured outputs."

def extract_executive_summary(state: MeetingState) -> Dict[str, Any]:
    """Generate an executive summary for the meeting transcript using the LLM."""
    user = f'''Write a concise executive summary (3-6 sentences) for this meeting. Focus on the main topics, key decisions, and overall outcome. Avoid listing agenda items or action items. Use clear, professional language for an executive audience.\n\nReturn ONLY the JSON: {{"executive_summary": "..."}}\n\nTranscript:\n{state.transcript[:5000]}\n'''
    out = chat_5_8_sentences(SYSTEM, user, temperature=0.5)
    data = robust_json_parse(out)
    summary = data.get("executive_summary", "")
    logger.info(f"Executive summary extracted: {summary}")
    return {"executive_summary": summary}

def ingest_local_text(state: MeetingState) -> Dict[str, Any]:
    if not state.transcript:
        raise ValueError("Transcript missing. Provide it before invoking graph.")
    # Return the transcript to update the state
    return {"transcript": state.transcript}

def extract_title(state: MeetingState) -> Dict[str, Any]:
    # System prompt specialized for title extraction
    title_system = "You are an expert at creating concise, descriptive meeting titles that capture the essence of a discussion."
    
    user = f"""Create a clear, concise title for this meeting transcript.

Guidelines for the title:
1. Make it 3-6 words maximum
2. Focus on the main topic or purpose of the meeting
3. Be specific but concise (e.g. "Q3 Marketing Strategy Review" not "Meeting About Marketing")
4. Avoid redundancy and unnecessary words
5. Ensure it's professional and descriptive
6. DO NOT use "Meeting" or "Discussion" in the title unless absolutely necessary

Return ONLY the JSON: {{"title": "Your Concise Title Here"}}

Transcript:
{state.transcript[:5000]}
"""
    # Use a higher temperature for creative title generation
    out = chat_5_8_sentences(title_system, user, temperature=0.7)
    data = robust_json_parse(out)
    title = data.get("title")
    
    # Apply validation and fallbacks
    if not title or len(title.strip()) < 3:
        # First fallback - try a different prompt
        backup_user = f"""The previous title generation failed. Please create a short, descriptive title 
for this meeting based on its key topics or purpose (maximum 5 words).
Return JSON: {{"title": "..."}}

Transcript:
{state.transcript[:3000]}
"""
        backup_out = chat_5_8_sentences(title_system, backup_user, temperature=0.5)
        backup_data = robust_json_parse(backup_out)
        title = backup_data.get("title")
    
    # Apply final fallbacks and validation
    if not title or len(title.strip()) < 3:
        # Try to generate a title from agenda or decisions if available
        if hasattr(state, 'agenda') and state.agenda:
            # Use the first agenda item as the title
            title = state.agenda[0]
            # Truncate if needed
            if len(title) > 40:
                title = title[:37] + "..."
        elif hasattr(state, 'decisions') and state.decisions:
            # Use the first decision as the title
            title = f"Decision: {state.decisions[0]}"
            # Truncate if needed
            if len(title) > 40:
                title = title[:37] + "..."
        else:
            # Default to a generic but informative title
            title = "Product Strategy Meeting"
    elif len(title) > 60:
        # Truncate overly long titles
        title = title[:57] + "..."
    
    logger.info(f"Title extracted: {title}")
    return {"title": title}

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

def extract_participants(state: MeetingState) -> Dict[str, Any]:
    user = f"""From the transcript, identify all participants in the meeting.
Return JSON: {{"participants":["..."]}}.
Transcript:
{state.transcript}
"""
    out = chat_5_8_sentences(SYSTEM, user)
    data = robust_json_parse(out)
    participants = data.get("participants", [])
    logger.info(f"Participants extracted: {participants}")
    return {"participants": participants}

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
    title = state.title or f"Meeting Minutes — {today}"

    lines = [
        f"# {title}",
        f"Date: {today}",
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
