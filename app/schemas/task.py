from typing import Optional
from pydantic import BaseModel, field_validator, Field, ConfigDict
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int
    status: Optional[str] = "pending"

class TaskCreate(TaskBase):
    # user_id: str  # foreign key
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    task_id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class config:
        from_attributes = True
    