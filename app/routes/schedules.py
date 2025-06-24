from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.schemas.schedule import (
    ScheduleBase,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate
)
from app.models import User, Schedule
from app.utils.auth import get_current_user
from app.db.database import get_db
from datetime import datetime, timezone

router = APIRouter()


# 1. Create a schedule 
@router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_schedule = Schedule(**schedule.model_dump(), user_id=user.user_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# 2. Get all schedules
@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
): 
    result = db.execute(
        select(Schedule).filter(Schedule.user_id == user.user_id)
    )
    schedules = result.scalars().all()
    return schedules

# 3. Get schedule by ID
@router.get("/schedules/{event_id}", response_model=ScheduleResponse)
async def get_schedule(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
): 
    result = db.execute(
        select(Schedule).filter(Schedule.event_id == event_id, Schedule.user_id == user.user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return schedule

# 4. Update schedule 
@router.patch("/schedules/{event_id}", response_model=ScheduleResponse)
async def update_schedule(
    event_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = db.execute(
        select(Schedule).filter(Schedule.event_id == event_id, Schedule.user_id == user.user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    update_data = schedule_update.model_dump(exclude_unset=True)
    db.execute(
        update(Schedule)
        .where(Schedule.event_id == event_id)
        .values(**update_data, updated_at=datetime.now(timezone.utc))
    )
    db.commit()
    db.refresh(schedule)
    return schedule

# 5. Delete an event
@router.delete("/schedules/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = db.execute(
        select(Schedule).filter(Schedule.event_id == event_id, Schedule.user_id == user.user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    db.execute(
        delete(Schedule)
        .where(Schedule.event_id == event_id)
    )
    db.commit()
    return None
