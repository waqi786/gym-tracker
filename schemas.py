"""
Pydantic schemas for request validation and response serialization.
These define what data is expected in requests and what gets returned in responses.
"""

from pydantic import BaseModel, Field, constr, conint
from typing import List, Optional
from datetime import datetime


# ─── Category Schemas ────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    # Category name must not be empty
    name: constr(strip_whitespace=True, min_length=1) = Field(..., description="Category name")


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ─── Exercise Schemas ─────────────────────────────────────────────────────────

class ExerciseCreate(BaseModel):
    # Exercise name cannot be empty
    name: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    category_id: int


class ExerciseUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    category: CategoryResponse

    model_config = {"from_attributes": True}


# ─── Training Session Schemas ─────────────────────────────────────────────────

class TrainingSessionCreate(BaseModel):
    started_at: datetime
    # Duration must be greater than 0 minutes
    duration: conint(gt=0)  # in minutes


class TrainingSessionUpdate(BaseModel):
    started_at: Optional[datetime] = None
    duration: Optional[conint(gt=0)] = None


class TrainingSessionResponse(BaseModel):
    id: int
    started_at: datetime
    duration: int
    owner_username: str

    model_config = {"from_attributes": True}


# ─── Exercise-TrainingSession Relationship Schemas ────────────────────────────

class ExerciseSessionCreate(BaseModel):
    exercise_id: int
    training_session_id: int
    # Number of repetitions must be greater than 0
    num_repetitions: conint(gt=0)
    level: Optional[float] = None
    notes: Optional[str] = None


class ExerciseSessionUpdate(BaseModel):
    num_repetitions: Optional[conint(gt=0)] = None
    level: Optional[float] = None
    notes: Optional[str] = None


class ExerciseSessionResponse(BaseModel):
    id: int
    exercise_id: int
    training_session_id: int
    num_repetitions: int
    level: Optional[float]
    notes: Optional[str]

    model_config = {"from_attributes": True}


class ExerciseSummary(BaseModel):
    exercise_id: int
    exercise_name: Optional[str]
    category_id: Optional[int]
    category_name: Optional[str]
    num_repetitions: int
    level: Optional[float]
    notes: Optional[str]


class TrainingSessionSummary(BaseModel):
    session: TrainingSessionResponse
    exercises: List[ExerciseSummary]


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: constr(strip_whitespace=True, min_length=1)
    password: constr(min_length=6)
    # Role must be either 'admin' or 'basic'
    role: Optional[constr(pattern="^(admin|basic)$")] = "basic"


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str
