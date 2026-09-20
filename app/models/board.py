import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")

    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")

class BoardMember(Base):
    __tablename__ = "board_members"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    board_id = Column(Integer, ForeignKey("boards.id"), primary_key=True)
    role = Column(Enum(Role), nullable=False, default=Role.VIEWER)

    user = relationship("User", back_populates="board_memberships")
    board = relationship("Board", back_populates="members")
