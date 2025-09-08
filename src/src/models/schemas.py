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
