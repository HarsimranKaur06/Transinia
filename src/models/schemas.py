"""
DATA MODELS AND STATE MANAGEMENT
------------------------------
This file defines the data structures that track and store meeting information.
It provides:

1. Task class - A structured representation of an action item including:
   - The person assigned to the task
   - The task description
   - Due date information
   - Priority level (High/Med/Low)

2. MeetingState class - The core state object that tracks all information about
   a meeting as it flows through the processing pipeline, including:
   - The original transcript
   - Extracted agenda items
   - Identified decisions
   - Assigned tasks
   - Generated meeting minutes

These Pydantic models ensure data validation and consistent structure.
"""

from typing import List, Literal, Optional, Union, Any, Dict
from pydantic import BaseModel, Field

class Task(BaseModel):
    """Task or action item extracted from a meeting transcript."""
    owner: str = Field(default="TBD")
    task: str = Field(..., description="The task description")
    due: str = Field(default="", description="Due date in YYYY-MM-DD format")
    priority: Literal["High", "Med", "Low"] = Field(default="Med")
    completed: bool = Field(default=False, description="Whether the task is completed")
    meeting_id: Optional[str] = Field(default=None, description="ID of the meeting this task belongs to")
    
    def model_dump(self) -> Dict[str, Any]:
        """Return a dictionary representation of the task."""
        return {
            "owner": self.owner,
            "task": self.task,
            "due": self.due,
            "priority": self.priority,
            "completed": self.completed,
            "meeting_id": self.meeting_id
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like access for compatibility."""
        if hasattr(self, key):
            return getattr(self, key)
        return default
    
    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access for compatibility."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

class MeetingState(BaseModel):
    """State object that tracks information about a meeting as it flows through the processing pipeline."""
    # Source can be any string or dictionary to allow flexibility
    source: Union[str, Dict[str, Any]] = Field(default="local_text", description="Source of the meeting transcript")
    transcript: Optional[str] = Field(default=None, description="Raw meeting transcript")
    agenda: List[str] = Field(default_factory=list, description="Extracted agenda items")
    decisions: List[str] = Field(default_factory=list, description="Extracted decisions")
    tasks: List[Union[Task, Dict[str, Any]]] = Field(default_factory=list, description="Extracted action items")
    minutes_md: Optional[str] = Field(default=None, description="Generated meeting minutes in Markdown")
    outputs_uri: Optional[str] = Field(default=None, description="URI where outputs are stored")
    participants: List[str] = Field(default_factory=list, description="Meeting participants")
    date: Optional[str] = Field(default=None, description="Meeting date")
    meeting_id: Optional[str] = Field(default=None, description="Unique ID for the meeting")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Allow dictionary-like access to attributes."""
        return getattr(self, key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-like access."""
        return getattr(self, key)
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        tasks_dict = []
        for task in self.tasks:
            if isinstance(task, Task):
                tasks_dict.append(task.model_dump())
            else:
                tasks_dict.append(task)
        
        source = self.source
        if isinstance(source, dict):
            source_str = source.get('value', str(source))
        else:
            source_str = source
            
        return {
            "transcript": self.transcript,
            "source": source_str,
            "minutes_md": self.minutes_md,
            "agenda": self.agenda,
            "decisions": self.decisions,
            "tasks": tasks_dict,
            "date": self.date,
            "participants": self.participants,
            "meeting_id": self.meeting_id,
            "outputs_uri": self.outputs_uri
        }
