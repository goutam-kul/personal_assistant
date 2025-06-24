from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ReminderBase(BaseModel):
    task_id: int
    reminder_time: datetime
    method: str

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(ReminderBase):
    task_id: Optional[int] = None
    reminder_time: Optional[datetime] = None
    method: Optional[str] = None

class ReminderResponse(ReminderBase):
    reminder_id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

