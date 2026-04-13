from src.tasks import dtos
from src.tasks.models import TaskModel
from src.users.models import UserModel
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

# To Create The New Tasks
def create_task(body: dtos.TaskSchema, db: Session, user: UserModel):
    data = body.model_dump()
    new_task = TaskModel(
        title=data["title"],
        description=data.get("description"),
        is_completed=data["is_completed"],
        user_id=user.id  # Automatically link to logged-in user
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# To Get All The Tasks
# Inside src/tasks/controller.py

def get_tasks(db: Session, user: UserModel, skip: int = 0, limit: int = 6, search: Optional[str] = None, status: Optional[str] = "all"):
    # 1. Base query for this user
    base_query = db.query(TaskModel).filter(TaskModel.user_id == user.id)

    # --- NEW: Get overall stats for the progress bar ---
    total_overall = base_query.count()
    total_completed = base_query.filter(TaskModel.is_completed == True).count()

    # 2. Now apply filters to a clone of the query
    query = base_query
    if search:
        query = query.filter(TaskModel.title.ilike(f"%{search}%"))

    if status == "active":
        query = query.filter(TaskModel.is_completed == False)
    elif status == "completed":
        query = query.filter(TaskModel.is_completed == True)

    total_tasks = query.count()
    tasks = query.offset(skip).limit(limit).all()
    
    return {
        "total_tasks": total_tasks,
        "tasks": tasks,
        "total_overall": total_overall,      # Send to frontend
        "total_completed": total_completed   # Send to frontend
    }

# To Get 1 Task
def get_task(id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found")
    
    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    
    return task

# To Update Task
def update_task(id: int, body: dtos.TaskSchema, db: Session, user: UserModel):
    task = db.get(TaskModel, id)

    if not task:
        raise HTTPException(status_code=404, detail="Not Found")
    
    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    body_data = body.model_dump()
    for field, value in body_data.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task 

# To Delete The Task
def delete_task(id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, id)

    if not task:
        raise HTTPException(status_code=404, detail="Not Found")
    
    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    db.delete(task)
    db.commit()
    return None