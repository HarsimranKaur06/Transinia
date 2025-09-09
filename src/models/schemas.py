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

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

SourceType = Literal["local_text", "s3"]

class Task(BaseModel):
    owner: str = Field(default="TBD")
    task: str
    due: str = Field(default="")
    priority: Literal["High", "Med", "Low"] = Field(default="Med")

class MeetingState(BaseModel):
    source: SourceType = "local_text"
    transcript: Optional[str] = None
    agenda: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    minutes_md: Optional[str] = None
    outputs_uri: Optional[str] = None
