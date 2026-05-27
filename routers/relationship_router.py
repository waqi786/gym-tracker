"""
Router for managing the relationship between exercises and training sessions.
Users can only manage relationships that belong to their own training sessions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import ExerciseTrainingSession, TrainingSession, Exercise, User
from schemas import ExerciseSessionCreate, ExerciseSessionUpdate, ExerciseSessionResponse
from auth import get_current_user

relationship_router = APIRouter(prefix="/exercise-sessions", tags=["Exercise-Session Relationships"])


def verify_session_ownership(session_id: int, current_user: User, db: Session) -> TrainingSession:
    """
    Helper function that verifies the training session exists and belongs to the current user.
    Returns the session if valid, raises an error otherwise.
    """
    training_session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()

    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    if training_session.owner_username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return training_session


@relationship_router.get("/session/{session_id}", response_model=List[ExerciseSessionResponse])
def get_exercises_in_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    """Returns a paginated list of exercises linked to a specific training session."""
    verify_session_ownership(session_id, current_user, db)

    exercise_links = db.query(ExerciseTrainingSession).filter(
        ExerciseTrainingSession.training_session_id == session_id
    ).offset(skip).limit(limit).all()
    return exercise_links


@relationship_router.get("/{link_id}", response_model=ExerciseSessionResponse)
def get_exercise_session_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a single exercise-session link by its ID."""
    link = db.query(ExerciseTrainingSession).filter(
        ExerciseTrainingSession.id == link_id
    ).first()

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    # Make sure this link belongs to the current user's session
    verify_session_ownership(link.training_session_id, current_user, db)

    return link


@relationship_router.post("/", response_model=ExerciseSessionResponse, status_code=status.HTTP_201_CREATED)
def add_exercise_to_session(
    link_data: ExerciseSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adds an exercise to a training session with repetitions, level, and notes.
    The training session must belong to the current user.
    """
    # Verify ownership of the training session
    verify_session_ownership(link_data.training_session_id, current_user, db)

    # Make sure the exercise actually exists
    exercise = db.query(Exercise).filter(Exercise.id == link_data.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    # Create the relationship entry
    new_link = ExerciseTrainingSession(
        exercise_id=link_data.exercise_id,
        training_session_id=link_data.training_session_id,
        num_repetitions=link_data.num_repetitions,
        level=link_data.level,
        notes=link_data.notes
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link


@relationship_router.put("/{link_id}", response_model=ExerciseSessionResponse)
def update_exercise_in_session(
    link_id: int,
    link_data: ExerciseSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the details of an exercise in a training session (repetitions, level, notes).
    The training session must belong to the current user.
    """
    link = db.query(ExerciseTrainingSession).filter(
        ExerciseTrainingSession.id == link_id
    ).first()

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    # Verify ownership before allowing updates
    verify_session_ownership(link.training_session_id, current_user, db)

    # Only update the fields that were actually sent in the request
    update_fields = link_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(link, field, value)

    db.commit()
    db.refresh(link)
    return link


@relationship_router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_exercise_from_session(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Removes an exercise from a training session.
    The training session must belong to the current user.
    """
    link = db.query(ExerciseTrainingSession).filter(
        ExerciseTrainingSession.id == link_id
    ).first()

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    # Only allow deletion if the session belongs to the current user
    verify_session_ownership(link.training_session_id, current_user, db)

    db.delete(link)
    db.commit()
