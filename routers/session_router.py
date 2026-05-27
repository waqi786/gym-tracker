"""
Router for training session endpoints.
Basic users can create, update, and delete their own training sessions.
Users cannot touch sessions that belong to other users.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import and_

from database import get_db
from models import TrainingSession, User, ExerciseTrainingSession, Exercise
from schemas import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessionResponse,
    TrainingSessionSummary,
)
from auth import get_current_user

session_router = APIRouter(prefix="/training-sessions", tags=["Training Sessions"])


@session_router.get("/", response_model=List[TrainingSessionResponse])
def get_my_training_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    date: Optional[date] = None
):
    """Returns a paginated list of the current user's training sessions.

    Optionally filter by `date` (YYYY-MM-DD) to return sessions that started on that date.
    """
    query = db.query(TrainingSession).filter(TrainingSession.owner_username == current_user.username)

    if date is not None:
        # filter sessions that started on the provided date (between 00:00 and next day 00:00)
        start_dt = datetime.combine(date, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
        query = query.filter(and_(TrainingSession.started_at >= start_dt, TrainingSession.started_at < end_dt))

    sessions = query.offset(skip).limit(limit).all()
    return sessions


@session_router.get("/{session_id}", response_model=TrainingSessionResponse)
def get_training_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a single training session by ID. Users can only see their own sessions."""
    training_session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id
    ).first()

    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    # Make sure the user is only accessing their own session
    if training_session.owner_username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return training_session


@session_router.post("/", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_training_session(
    session_data: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new training session for the currently logged-in user."""
    new_session = TrainingSession(
        started_at=session_data.started_at,
        duration=session_data.duration,
        owner_username=current_user.username  # automatically set to the current user
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@session_router.put("/{session_id}", response_model=TrainingSessionResponse)
def update_training_session(
    session_id: int,
    session_data: TrainingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates an existing training session. Users can only edit their own sessions."""
    training_session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id
    ).first()

    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    # Prevent users from editing sessions owned by other users
    if training_session.owner_username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Only update the fields that were provided
    update_fields = session_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(training_session, field, value)

    db.commit()
    db.refresh(training_session)
    return training_session


@session_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes a training session by ID. Users can only delete their own sessions."""
    training_session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id
    ).first()

    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    # Prevent users from deleting sessions they don't own
    if training_session.owner_username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(training_session)
    db.commit()


@session_router.get("/{session_id}/summary", response_model=TrainingSessionSummary)
def get_training_session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a session summary including session details and all exercises performed in it."""
    training_session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    if training_session.owner_username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Fetch all exercise links for this session and include exercise details
    links = db.query(ExerciseTrainingSession).filter(ExerciseTrainingSession.training_session_id == session_id).all()
    exercises_summary = []
    for link in links:
        exercise = db.query(Exercise).filter(Exercise.id == link.exercise_id).first()
        category_name = None
        category_id = None
        if exercise and hasattr(exercise, 'category_id'):
            category_id = exercise.category_id
            # attempt to read category name if relationship available
            if hasattr(exercise, 'category') and exercise.category is not None:
                category_name = exercise.category.name
            else:
                # fallback: query category table for name
                from models import Category
                cat = db.query(Category).filter(Category.id == category_id).first()
                category_name = cat.name if cat else None

        exercises_summary.append({
            "exercise_id": link.exercise_id,
            "exercise_name": exercise.name if exercise else None,
            "category_id": category_id,
            "category_name": category_name,
            "num_repetitions": link.num_repetitions,
            "level": link.level,
            "notes": link.notes
        })

    return {
        "session": {
            "id": training_session.id,
            "started_at": training_session.started_at,
            "duration": training_session.duration,
            "owner_username": training_session.owner_username
        },
        "exercises": exercises_summary
    }
