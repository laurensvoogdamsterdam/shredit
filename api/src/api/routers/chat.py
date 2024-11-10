import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from api.db.models import ChatRoom
from api.db.models import File as FileModel
from api.db.models import Message, MessageType, User, chat_members
from api.db.pool import get_db

router = APIRouter(prefix="/chats", tags=["chat"])


# Request models
class ChatRoomCreate(BaseModel):
    name: str
    description: Optional[str] = str(None)
    image: Optional[str] = str(None)
    invites: Optional[List[int]] = []


class ChatMessageCreate(BaseModel):
    content: str
    message_type: Optional[MessageType] = MessageType.TEXT


class AddUserToChatRoom(BaseModel):
    user_id: int


# Response models
class ChatRoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = str(None)
    created_at: datetime


class ChatMessageResponse(BaseModel):
    id: int
    content: str
    message_type: MessageType
    sender_id: int
    created_at: datetime


class ChatDeletedResponse(BaseModel):
    message: str


class UserAddResponse(BaseModel):
    message: str


class UserRemoveResponse(BaseModel):
    message: str


# Create a new chat room
@router.post("/create", response_model=ChatRoomResponse)
async def create_chat_room(
    room_data: ChatRoomCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    user = request.state.user_info
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_room = ChatRoom(name=room_data.name)
    user.creator = user
    if room_data.description:
        new_room.description = room_data.description
    if room_data.image:
        new_room.image_url = room_data.image
    if room_data.invites:
        inviet_list = [id for id in room_data.invites if id != user.id] + [user.id]
        result = await db.execute(select(User).where(User.id.in_(inviet_list)))
        new_room.members = result.scalars().all()

    # query user from db called creator
    result = await db.execute(select(User).where(User.id == user.id))
    creator = result.scalars().first()

    new_room.creator = creator
    new_room.admins.append(creator)
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room


# Delete a chat room
@router.delete("/{room_id}", response_model=ChatDeletedResponse)
async def delete_chat_room(
    room_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Delete a chat room.

    Args:
        room_id (int): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_
    """
    result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    user = request.state.user_info
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if (
        user.id not in [admin.id for admin in room.admins]
        and user.id != room.creator.id
    ):
        raise HTTPException(
            status_code=403, detail="User is not the creator of this chat room"
        )

    # Delete all messages associated with the chat room
    await db.execute(delete(Message).where(Message.chat_room_id == room_id))

    # Delete all entries in the chat_members table associated with this chat room
    await db.execute(delete(chat_members).where(chat_members.c.chat_room_id == room_id))

    await db.delete(room)
    await db.commit()

    return ChatDeletedResponse(message="Chat room deleted successfully")


# Add a user to a chat room
@router.post("/{room_id}/users", response_model=UserAddResponse)
async def add_user_to_chat_room(
    room_id: int,
    user_data: AddUserToChatRoom,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Add a user to a chat room.

    Args:
        room_id (int): _description_
        user_data (AddUserToChatRoom): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    # Check if room exists
    result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    user = request.state.user_info
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in room.members:
        room.members.append(user)
        await db.commit()
        return UserAddResponse(message="User added to chat room")
    else:
        return UserAddResponse(message="User already in chat room")


# Remove a user from a chat room
@router.delete("/{room_id}/users/{user_id}", status_code=204)
async def remove_user_from_chat_room(
    room_id: int, user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Remove a user from a chat room.

    Args:
        room_id (int): _description_
        user_id (int): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    result = await db.execute(
        select(ChatRoom)
        .where(ChatRoom.id == room_id)
        .options(joinedload(ChatRoom.members))
    )
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    user = request.state.user_info
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in room.admins:
        raise HTTPException(
            status_code=403, detail="User is not an admin of this chat room"
        )

    to_remove_user = next(
        (member for member in room.members if member.id == user_id), None
    )
    if user:
        room.members.remove(to_remove_user)
        await db.commit()

    return UserRemoveResponse(message="User removed from chat room")


# Send a message to a chat room
@router.post("/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: int,
    message_data: ChatMessageCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Send a message to a chat room.

    Args:
        room_id (int): _description_
        message_data (ChatMessageCreate): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    # get user from request
    sender = request.state.user_info
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")
    #  select chatromo with members
    result = await db.execute(
        select(ChatRoom)
        .where(ChatRoom.id == room_id)
        .options(
            joinedload(ChatRoom.members),
            joinedload(ChatRoom.admins),
            joinedload(ChatRoom.creator),
        )
    )
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    #  check if user is a member of the chat room
    if (
        sender.id not in [member.id for member in room.members]
        and sender.id not in [admin.id for admin in room.admins]
        and sender.id != room.creator.id
    ):
        raise HTTPException(
            status_code=403, detail="User is not a member of this chat room"
        )

    # Create message (assuming blob URLs for media if image or video)
    new_message = Message(
        content=message_data.content,
        message_type=message_data.message_type,
        sender_id=sender.id,
        chat_room_id=room_id,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


# Get messages from a chat room
@router.get("/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    room_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Get messages from a chat room.

    Args:
        room_id (int): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    user = request.state.user_info
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # get chat room
    result = await db.execute(
        select(ChatRoom)
        .where(ChatRoom.id == room_id)
        .options(
            joinedload(ChatRoom.members),
            # as now all users in a chat should belong to members, the below is nolonger needed
            # joinedload(ChatRoom.admins),
            # joinedload(ChatRoom.creator),
        )
    )
    room = result.scalars().first()
    #  ensure that user is either a member or admins or creator of the room
    if (
        user.id
        not in [member.id for member in room.members]
        # as now all users in a chat should belong to members, the below is nolonger needed
        # and user.id not in [admin.id for admin in room.admins]
        # and user.id != room.creator.id
    ):
        raise HTTPException(
            status_code=403, detail="User is not a member of this chat room"
        )

    result = await db.execute(
        select(Message)
        .where(Message.chat_room_id == room_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    if not messages:
        return []
    return messages


# Get all chat rooms a user is in
@router.get("/", response_model=List[ChatRoomResponse])
async def get_user_chat_rooms(request: Request, db: AsyncSession = Depends(get_db)):
    """Get all chat rooms a user is in.

    Args:
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = request.state.user_info
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # query fresh user with chat_rooms
    result = await db.execute(
        select(User).where(User.id == user.id).options(joinedload(User.chat_rooms))
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.chat_rooms


# In-memory connection manager for chat rooms
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]

    async def broadcast(self, room_id: int, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()


# WebSocket endpoint for real-time chat in a room
@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: int, db: AsyncSession = Depends(get_db)
):
    auth0_id = websocket.query_params.get(
        "auth0_id"
    )  # Obtain Auth0 ID from the query params

    # Verify user and chat room existence
    user = await verify_user(auth0_id, db)
    room = await verify_chat_room(room_id, db)

    # Connect user to the WebSocket room
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = MessageType(message_data.get("message_type", "text"))
            content = message_data.get("content")

            # Save message to the database
            new_message = Chat(
                content=content,
                message_type=message_type,
                sender_id=user.id,
                room_id=room_id,
            )
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)

            # Broadcast message to all connected users
            await manager.broadcast(
                room_id,
                {
                    "sender": user.username,
                    "content": content,
                    "message_type": message_type.value,
                    "created_at": new_message.created_at.isoformat(),
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)


# Helper functions to verify user and room existence
async def verify_user(auth0_id: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.auth0_id == auth0_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def verify_chat_room(room_id: int, db: AsyncSession):
    result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return room
