from fastapi import APIRouter, Depends, status
from src.tasks import controller, dtos
from src.utils.db import get_db
from typing import Optional
from sqlalchemy.orm import Session
from src.utils.helpers import is_authenticated
from src.users.models import UserModel


task_routes = APIRouter(prefix="/tasks")

@task_routes.post("/create", response_model=dtos.TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def create_task(body: dtos.TaskSchema, db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)):
    return controller.create_task(body, db, user)

@task_routes.get("/all_tasks", response_model=dtos.PaginatedTaskResponse, status_code=status.HTTP_200_OK)
def get_all_tasks(skip: int = 0, limit: int = 6,search: Optional[str] = None, status: Optional[str] = "all", db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)):
    # Pass the skip and limit to your controller logic
    return controller.get_tasks(db, user, skip, limit, search, status)

@task_routes.get("/get_1_task/{id}", response_model=dtos.TaskResponseSchema, status_code=status.HTTP_200_OK)
def get_task(id: int, db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)):
    return controller.get_task(id, db, user)

@task_routes.put("/update_task/{id}", response_model=dtos.TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def update_task(id: int, body: dtos.TaskSchema, db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)):
    return controller.update_task(id, body, db, user)

@task_routes.delete("/delete_task/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)):
    return controller.delete_task(id, db, user)