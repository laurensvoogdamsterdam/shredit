import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


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
        "ChatRoom", secondary="chat_room_members", back_populates="admins"
    )
    files = relationship("File", back_populates="user")
    workflow_instances = relationship("WorkflowInstance", back_populates="user")

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


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    training_plan_id = Column(Integer, ForeignKey("training_plans.id"))
    type = Column(Enum(ExerciseType), nullable=False)
    duration = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)


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


#  LLM chat history
class ChatHistory(Base):
    # Chat history for llm chats
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    conversation_d = Column(Integer, ForeignKey("users.id"))
    history = Column(JSONB, nullable=False, default=list)


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
    admins = relationship("User", secondary=chat_members, back_populates="chat_admins")
    creator = relationship("User", back_populates="created_chats")
    messages = relationship("Message", back_populates="chat_room")


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
