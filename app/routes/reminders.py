from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.schemas.reminder import (
    ReminderBase,
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate
)
from app.utils.auth import get_current_user
from app.models import Task, Reminder, User
from app.db.database import get_db
from datetime import datetime, timezone

router = APIRouter()

# 1. Create a reminder
@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Verify tasks exist and belong to user
    result = db.execute(
        select(Task).filter(Task.task_id == reminder.task_id, Task.user_id == user.user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db_reminder = Reminder(**reminder.model_dump(), user_id=user.user_id)
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

# 2. Get all reminders
@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = db.execute(
        select(Reminder).filter(Reminder.user_id == user.user_id)
    )
    reminders = result.scalars().all()
    return reminders

# 3. Get reminder by ID
@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # check if reminder exist
    result = db.execute(
        select(Reminder).filter(Reminder.reminder_id == reminder_id, Reminder.user_id == user.user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    return reminder

# 4. Update reminder 
@router.patch("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = db.execute(
        select(Reminder).filter(Reminder.reminder_id == reminder_id, Reminder.user_id == user.user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    update_data = reminder_update.model_dump(exclude_unset=True)
    if "task_id" in update_data:
        result = db.execute(
            select(Reminder).filter(Task.task_id == update_data["task_id"], Task.user_id == user.user_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    
    db.execute(
        update(Reminder)
        .where(Reminder.reminder_id == reminder_id)
        .values(**update_data, updated_at=datetime.now(timezone.utc))
    )
    db.commit()
    db.refresh(reminder)
    return reminder

# 5. Delete a reminder
@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = db.execute(
        select(Reminder).filter(Reminder.reminder_id == reminder_id, Reminder.user_id == user.user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    db.execute(
        delete(Reminder)
        .where(Reminder.reminder_id == reminder_id)
    )
    db.commit()
    return None