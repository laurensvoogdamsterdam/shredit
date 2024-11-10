from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.utils.llm.agents import AgentFlow, get_agent

from api.db.models import Conversation
from api.db.pool import get_db  # Assume this provides a session dependency

# Define the APIRouter instance
router = APIRouter(
    prefix="/llm",
    tags=["LLM Chat"],
    responses={404: {"description": "Not found"}},
)


# create conversation endpoint response
class ConversationResponse(BaseModel):
    id: int

class ConversationCreatedResponse(BaseModel):
    id: int    


class Question(BaseModel):
    role: str = "user"
    content: str = None


class ConversationDeletedResponse(BaseModel):
    message: str = "Conversation deleted successfully"


class ChatResponse(BaseModel):
    role: str
    content: str


# Define the route
@router.post("/", response_model=ConversationCreatedResponse)
async def create_conversation(request: Request, db: AsyncSession = Depends(get_db)):
    # get user from request
    user = request.state.user_info
    # create conversation
    conversation = Conversation(user_id=user.id)
    db.add(conversation)
    await db.commit()
    return ConversationCreatedResponse(id=conversation.id)


# delete conversation endpoint
@router.delete("/delete/{conversation_id}", response_model=ConversationDeletedResponse)
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    #  conversation from AsyncSession
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    await db.commit()
    return ConversationDeletedResponse()


# add message endpoint
@router.post("/{conversation_id}/ask", response_model=ChatResponse)
async def add_message(
    conversation_id: int,
    question: Question,
    request: Request,
    db: AsyncSession = Depends(get_db),
    agent: AgentFlow = Depends(get_agent),
):
    # get user from request
    user = request.state.user_info
    # get conversation from AsyncSession
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))    
    conversation = result.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if not conversation.user_id == user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # parse messages from conversation.history
    messages = conversation.get_history()   
    print(messages)
    #  get response from llm (placeholder)
    response = await agent.run({"history": messages, "question": question.content})
    # add message to conversation
    messages.append(response)
    conversation.set_history(messages)  
    await db.commit()
    return ChatResponse(role="agent", content=response.content)