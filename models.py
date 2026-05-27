"""
Database models for the gym management tracker.
Defines Exercise, Category, TrainingSession, and their relationship table.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Category(Base):
    """Represents a category that groups exercises together (e.g., Chest, Legs, Cardio)."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # One category can have many exercises
    exercises = relationship("Exercise", back_populates="category")


class Exercise(Base):
    """Represents a gym exercise with a name, description, and belonging category."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Each exercise belongs to exactly one category
    category = relationship("Category", back_populates="exercises")

    # An exercise can appear in multiple training sessions via the relationship table
    training_session_links = relationship("ExerciseTrainingSession", back_populates="exercise")


class TrainingSession(Base):
    """Represents a training session done by a user, with start time and duration."""
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration = Column(Integer, nullable=False)  # duration in minutes
    owner_username = Column(String(100), nullable=False)  # tracks which user owns this session

    # A training session can include multiple exercises via the relationship table
    exercise_links = relationship("ExerciseTrainingSession", back_populates="training_session")


class ExerciseTrainingSession(Base):
    """
    Junction table that links exercises and training sessions.
    Also stores extra info: number of repetitions, level/weight, and any notes.
    """
    __tablename__ = "exercise_training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)

    num_repetitions = Column(Integer, nullable=False)  # number of repetitions done
    level = Column(Float, nullable=True)               # weight in kg or number of abs per repetition
    notes = Column(Text, nullable=True)                # any additional notes

    # Back references to both sides of the relationship
    exercise = relationship("Exercise", back_populates="training_session_links")
    training_session = relationship("TrainingSession", back_populates="exercise_links")


class User(Base):
    """Represents a user with a role: either 'admin' or 'basic'."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="basic")  # 'admin' or 'basic'
