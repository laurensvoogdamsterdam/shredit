from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import declarative_base


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

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Table
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserRole(str, enum.Enum):
    ATHLETE = "athlete"
    TRAINER = "trainer"
    COACH = "coach"
    DIETICIAN = "dietician"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    auth0_id = Column(String, unique=True, index=True)  # Auth0 user ID
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    training_plans = relationship("TrainingPlan", back_populates="creator")
    dietary_plans = relationship("DietaryPlan", back_populates="creator")
    

subscriptions = Table(
    'subscriptions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('training_plan_id', Integer, ForeignKey('training_plans.id'), primary_key=True)
)

class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="training_plans")
    subscribers = relationship("User", secondary="subscriptions", back_populates="training_plans")


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

