from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from src.database import Base
import enum
from datetime import datetime

# Enum for User Roles
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

    # Relationships
    athletes = relationship("Athlete", back_populates="trainer")
    dieticians = relationship("Dietician", back_populates="coach")

class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trainer_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    trainer = relationship("User", foreign_keys=[trainer_id])

class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")

class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    athletes = relationship("Athlete", back_populates="trainer")

class Dietician(Base):
    __tablename__ = "dieticians"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    coach = relationship("Coach", back_populates="dieticians")

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"))
    date = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer)  # Duration in minutes
    notes = Column(String)

    athlete = relationship("Athlete")

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    dietician_id = Column(Integer, ForeignKey("dieticians.id"))
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    dietician = relationship("Dietician")
