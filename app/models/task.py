import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    board = relationship("Board", back_populates="tasks")
    creator = relationship("User", back_populates="tasks")
