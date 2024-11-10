import enum
from datetime import datetime
from typing import Generic, Iterator, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship
from api.utils.llm.config import Message as LLMMessage

Base = declarative_base()


# BUSINESS LOGIC


# Enum for User Roles
class UserRole(str, enum.Enum):
    ATHLETE = "athlete"
    TRAINER = "trainer"
    COACH = "coach"
    DIETICIAN = "dietician"


# Enum for Exercise Types
class ExerciseType(str, enum.Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"


# enum with all types of sports
class ExercisesType(str, enum.Enum):
    RUNNING = "running"
    JOGGING = "jogging"
    WALKING = "walking"
    CYCLING = "cycling"
    COMMUTING = "commuting"
    SWIMMING = "swimming"
    WEIGHTLIFTING = "weightlifting"
    YOGA = "yoga"
    PILATES = "pilates"
    HIKING = "hiking"
    DANCING = "dancing"
    BOXING = "boxing"
    AEROBICS = "aerobics"
    ROWING = "rowing"
    SKIING = "skiing"
    SNOWBOARDING = "snowboarding"
    GOLF = "golf"
    TENNIS = "tennis"
    SOCCER = "soccer"
    BASKETBALL = "basketball"
    VOLLEYBALL = "volleyball"
    ROCK_CLIMBING = "rock climbing"
    MARTIAL_ARTS = "martial arts"
    FISHING = "fishing"
    GYMNASTICS = "gymnastics"
    CROSSFIT = "crossfit"
    FENCING = "fencing"
    BADMINTON = "badminton"
    SQUASH = "squash"
    CAPOEIRA = "capoeira"
    CIRCUS_ARTS = "circus arts"
    TRAMPOLINING = "trampolining"
    POLE_DANCING = "pole dancing"
    ZUMBA = "zumba"
    MEDITATION = "meditation"


class DietaryPlanType(str, enum.Enum):
    WEIGHT_LOSS = "weight loss"
    MUSCLE_GAIN = "muscle gain"
    MAINTENANCE = "maintenance"


class TrainingPlanType(str, enum.Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    MIXED = "mixed"


class UserRole(str, enum.Enum):
    ATHLETE = "athlete"
    TRAINER = "trainer"
    COACH = "coach"
    DIETICIAN = "dietician"


subscriptions = Table(
    "subscriptions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "training_plan_id", Integer, ForeignKey("training_plans.id"), primary_key=True
    ),
)


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="training_plans")
    subscribers = relationship(
        "User", secondary="subscriptions", back_populates="training_plans"
    )


class DietaryPlan(Base):
    __tablename__ = "dietary_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="dietary_plans")

    def __repr__(self):
        return f"<DietaryPlan(id={self.id}, name={self.name})>"


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    training_plan_id = Column(Integer, ForeignKey("training_plans.id"))
    type = Column(Enum(ExerciseType), nullable=False)
    duration = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Exercise(id={self.id}, type={self.type})>"


# CORE DB MODELS


class User(Base):
    __tablename__ = "users"
    __table_args__ = {
        "extend_existing": True,
    }  # Enable extending the existing table

    id = Column(Integer, primary_key=True, index=True)
    auth_id = Column(String, unique=True, index=True)
    username = Column(String, unique=False, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    given_name = Column(String)
    family_name = Column(String)
    avatar_url = Column(String)
    role = Column(Enum(UserRole), default=UserRole.ATHLETE)
    created_at = Column(DateTime, default=datetime.utcnow)

    training_plans = relationship("TrainingPlan", back_populates="creator")
    dietary_plans = relationship("DietaryPlan", back_populates="creator")
    chat_rooms = relationship(
        "ChatRoom", secondary="chat_room_members", back_populates="members"
    )
    messages = relationship("Message", back_populates="sender")

    created_chats = relationship("ChatRoom", back_populates="creator")
    chat_admins = relationship(
        "ChatRoom", secondary="chat_room_admins", back_populates="admins"
    )
    files = relationship("File", back_populates="user")
    workflow_instances = relationship("WorkflowInstance", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

    # create asdict method to return the user as a dictionary
    def asdict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "created_at": self.created_at,
        }


#  File model for cloud storage
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, index=True)
    file_name = Column(String, index=True)
    content_type = Column(String, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # create relation with user
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, file_name={self.file_name})>"



#  LLM chat history
class Conversation(Base):
    # Chat history for llm chats
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    history = Column(JSONB, nullable=False, default=list)
    history_size = Column(Integer, default=10)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"

    # create method that converts json in history to object
    def get_history(self):
        return [LLMMessage.from_dict(msg) for msg in self.history]

    # set history from list of objects
    def set_history(self, history: Sequence[LLMMessage]):
        self.history = [msg.to_dict() for msg in history[-self.history_size :]]


#  User chat models
class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


# Chat Room Model# Association Table for Many-to-Many relationship between ChatRoom and User
chat_members = Table(
    "chat_room_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("chat_room_id", Integer, ForeignKey("chat_rooms.id"), primary_key=True),
)

chat_admins = Table(
    "chat_room_admins",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("chat_room_id", Integer, ForeignKey("chat_rooms.id"), primary_key=True),
)


# ChatRoom Model
class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    image_url = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to link users to chat rooms
    members = relationship("User", secondary=chat_members, back_populates="chat_rooms")
    admins = relationship("User", secondary=chat_admins, back_populates="chat_admins")
    creator = relationship("User", back_populates="created_chats")
    messages = relationship("Message", back_populates="chat_room")

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name={self.name})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    message_type = Column(Enum(MessageType))
    created_at = Column(DateTime, default=datetime.utcnow)

    # create relation with user
    sender = relationship("User", back_populates="messages")
    chat_room = relationship("ChatRoom", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, chat_room_id={self.chat_room_id}, sender_id={self.sender_id})>"


# WORKFLOWS


# Enum for workflow status
class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    instances = relationship("WorkflowInstance", back_populates="workflow")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name})>"


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    container_id = Column(String, nullable=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    workflow = relationship("Workflow", back_populates="instances")
    user = relationship("User", back_populates="workflow_instances")

    def __repr__(self):
        return f"<WorkflowInstance(id={self.id}, workflow_id={self.workflow_id}, user_id={self.user_id}, status={self.status})>"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)  # Stripe session ID
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Assuming a Users table exists
    user = relationship(
        "User", back_populates="payments"
    )  # Define the relationship to the User model
    amount = Column(
        Numeric(10, 2), nullable=False
    )  # Stored in dollars/cents or other currency
    currency = Column(String, nullable=False, default="usd")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment(id={self.id}, session_id={self.session_id}, amount={self.amount}, currency={self.currency}, status={self.status})>"


#  langchain models to query
class DocumentModel(BaseModel):
    key: Optional[str] = Field(None)
    page_content: Optional[str] = Field(None)
    metadata: dict = Field(default_factory=dict)

    def __repr__(self):
        return f"<DocumentModel(key={self.key}, metadata={self.metadata})>"


class SQLDocument(Base):
    __tablename__ = "docstore"
    key = Column(String, primary_key=True)
    value = Column(JSONB)

    def __repr__(self):
        return f"<SQLDocument(key='{self.key}', value='{self.value}')>"
