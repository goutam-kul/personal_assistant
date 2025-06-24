from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models import Task, User
from app.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.db.database import get_db
from app.utils.auth import get_current_user
from datetime import datetime, timezone

router = APIRouter()

# Create new task
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if task.priority is None or not (1 <= task.priority <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority must be between 1 to 5"
        )
    db_task = Task(**task.model_dump(), user_id=user.user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# List all tasks
@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.execute(select(Task).filter(Task.user_id==user.user_id))
    tasks = result.scalars().all()
    return tasks


# Get task by ID
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
): 
    result = db.execute(
        select(Task).filter(Task.task_id == task_id, Task.user_id == user.user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

# Update Task
@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Task).filter(Task.task_id == task_id, Task.user_id == user.user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    if "priority" in update_data and not (1<= update_data["priority"] <=5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority must be between 1-5"
        )
    
    db.execute(
        update(Task)
        .where(Task.task_id ==  task_id)
        .values(**update_data, updated_at=datetime.now(timezone.utc))
    )
    db.commit()
    db.refresh(task)

    return task

# Delete task 
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Task).filter(Task.task_id == task_id, Task.user_id == user.user_id)
    )

    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.execute(delete(Task).where(Task.task_id == task_id))
    db.commit()

    return None

