from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.board import Role
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.api.v1.boards import get_board_and_check_role
from app.websockets.manager import manager

router = APIRouter()

@router.get("/{board_id}/tasks", response_model=List[TaskRead])
async def list_tasks(board_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.VIEWER)
    result = await db.execute(select(Task).where(Task.board_id == board_id))
    return result.scalars().all()

@router.post("/{board_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(board_id: int, task_in: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.MEMBER)
    
    new_task = Task(
        board_id=board_id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        created_by=current_user.id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    await manager.broadcast_to_board(board_id, {
        "event": "task_created",
        "task": {"id": new_task.id, "title": new_task.title, "status": new_task.status.value}
    })
    
    return new_task

@router.put("/{board_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(board_id: int, task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.MEMBER)
    
    result = await db.execute(select(Task).where(Task.id == task_id, Task.board_id == board_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    await db.commit()
    await db.refresh(task)
    
    await manager.broadcast_to_board(board_id, {
        "event": "task_updated",
        "task": {"id": task.id, "title": task.title, "status": task.status.value}
    })
    
    return task

@router.delete("/{board_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(board_id: int, task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.MEMBER)
    
    result = await db.execute(select(Task).where(Task.id == task_id, Task.board_id == board_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    await db.delete(task)
    await db.commit()
    
    await manager.broadcast_to_board(board_id, {
        "event": "task_deleted",
        "task_id": task_id
    })
    
    return None
