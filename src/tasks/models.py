from sqlalchemy import Column, Integer,String,Boolean, ForeignKey
from src.utils.db import Base

class TaskModel(Base):
    __tablename__ = "user_tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(100), nullable=True)
    is_completed = Column(Boolean, default = False)

    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE", onupdate="CASCADE"))
