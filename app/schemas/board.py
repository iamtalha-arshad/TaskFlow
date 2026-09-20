from pydantic import BaseModel
from typing import Optional, List
from app.models.board import Role
from .user import UserRead

class BoardBase(BaseModel):
    title: str
    description: Optional[str] = ""

class BoardCreate(BoardBase):
    pass

class BoardRead(BoardBase):
    id: int

    class Config:
        from_attributes = True

class BoardMemberRead(BaseModel):
    user: UserRead
    role: Role

    class Config:
        from_attributes = True

class BoardWithMembers(BoardRead):
    members: List[BoardMemberRead] = []

class MemberAdd(BaseModel):
    username: str
    role: Role = Role.VIEWER
