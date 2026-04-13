from pydantic import BaseModel
from typing import Optional, List

class TaskSchema(BaseModel):
    title: str
    description: Optional[str] = None # Added Optional and default None
    is_completed: bool = False

class TaskResponseSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None # Match here as well
    is_completed: bool 
    user_id: int | None = 0

    # --- ADD THIS NEW SCHEMA ---
class PaginatedTaskResponse(BaseModel):
    total_tasks: int
    tasks: List[TaskResponseSchema]
    # --- ADD THESE TWO LINES ---
    total_overall: int = 0
    total_completed: int = 0