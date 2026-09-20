from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.board import Board, BoardMember, Role
from app.schemas.board import BoardCreate, BoardRead, BoardWithMembers, MemberAdd

router = APIRouter()

async def get_board_and_check_role(board_id: int, user_id: int, db: AsyncSession, min_role: Role = Role.VIEWER) -> tuple[Board, BoardMember]:
    result = await db.execute(select(BoardMember).where(BoardMember.board_id == board_id, BoardMember.user_id == user_id))
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role_hierarchy = {Role.VIEWER: 1, Role.MEMBER: 2, Role.OWNER: 3}
    if role_hierarchy[member.role] < role_hierarchy[min_role]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    result = await db.execute(select(Board).options(selectinload(Board.members).selectinload(BoardMember.user)).where(Board.id == board_id))
    board = result.scalars().first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
        
    return board, member

@router.get("/", response_model=List[BoardRead])
async def list_boards(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Board).join(BoardMember).where(BoardMember.user_id == current_user.id)
    )
    return result.scalars().all()

@router.post("/", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(board_in: BoardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_board = Board(title=board_in.title, description=board_in.description)
    db.add(new_board)
    await db.flush() # To get the new_board.id
    
    member = BoardMember(user_id=current_user.id, board_id=new_board.id, role=Role.OWNER)
    db.add(member)
    await db.commit()
    await db.refresh(new_board)
    return new_board

@router.get("/{board_id}", response_model=BoardWithMembers)
async def get_board(board_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    board, _ = await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.VIEWER)
    return board

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    board, _ = await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.OWNER)
    await db.delete(board)
    await db.commit()
    return None

@router.post("/{board_id}/members", response_model=BoardWithMembers)
async def add_member(board_id: int, member_in: MemberAdd, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    board, _ = await get_board_and_check_role(board_id, current_user.id, db, min_role=Role.OWNER)
    
    result = await db.execute(select(User).where(User.username == member_in.username))
    user_to_add = result.scalars().first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User to add not found")
        
    result = await db.execute(select(BoardMember).where(BoardMember.board_id == board_id, BoardMember.user_id == user_to_add.id))
    existing_member = result.scalars().first()
    if existing_member:
        existing_member.role = member_in.role
    else:
        new_member = BoardMember(user_id=user_to_add.id, board_id=board_id, role=member_in.role)
        db.add(new_member)
        
    await db.commit()
    await db.refresh(board)
    return board
