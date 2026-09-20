from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import jwt
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.board import BoardMember
from app.websockets.manager import manager

router = APIRouter()

async def get_user_from_token(token: str, db: AsyncSession) -> User | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None
        
    result = await db.execute(select(User).where(User.id == int(user_id)))
    return result.scalars().first()

@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Check if user is a member of the board
    result = await db.execute(
        select(BoardMember).where(
            BoardMember.board_id == board_id,
            BoardMember.user_id == user.id
        )
    )
    member = result.scalars().first()
    if not member:
        await websocket.close(code=1008, reason="Not a board member")
        return

    await manager.connect(websocket, board_id)
    try:
        while True:
            # We don't expect messages from client, but we must receive to keep connection open
            # and detect disconnects
            data = await websocket.receive_text()
            # Ignore data to enforce read-only
    except WebSocketDisconnect:
        manager.disconnect(websocket, board_id)
