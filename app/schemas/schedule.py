from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ScheduleBase(BaseModel):
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    calendar_id: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    title: Optional[str] = None
    start_time: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    event_id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
