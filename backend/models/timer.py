from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TimerEntry(BaseModel):
    id: Optional[str] = None
    project: str
    category: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int  # in seconds
    date: str  # YYYY-MM-DD format

class TimerCreate(BaseModel):
    project: str
    category: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int
    date: str  # YYYY-MM-DD format - explicit date to avoid timezone issues

class DayActivitySummary(BaseModel):
    date: str
    total_duration: int  # in seconds
    entries: list[TimerEntry]
