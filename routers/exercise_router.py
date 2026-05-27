"""
Router for exercise-related endpoints.
Only admin users can create, update, or delete exercises.
Anyone authenticated can read the list.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Exercise, Category, User
from schemas import ExerciseCreate, ExerciseUpdate, ExerciseResponse
from auth import get_current_user, require_admin

exercise_router = APIRouter(prefix="/exercises", tags=["Exercises"])


@exercise_router.get("/", response_model=List[ExerciseResponse])
def get_all_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # any logged-in user can view
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None
):
    """Returns a paginated list of exercises. Optionally filter by category using `?category_id=...`."""
    query = db.query(Exercise)
    if category_id is not None:
        query = query.filter(Exercise.category_id == category_id)

    exercises = query.offset(skip).limit(limit).all()
    return exercises


@exercise_router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a single exercise by its ID."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise


@exercise_router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # only admins can create exercises
):
    """Creates a new exercise. Requires admin role."""
    # Make sure the referenced category actually exists
    category = db.query(Category).filter(Category.id == exercise_data.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    new_exercise = Exercise(
        name=exercise_data.name,
        description=exercise_data.description,
        category_id=exercise_data.category_id
    )
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise


@exercise_router.put("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # only admins can update exercises
):
    """Updates an existing exercise. Requires admin role."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    # If category_id is being changed, verify the new category exists
    if exercise_data.category_id is not None:
        category = db.query(Category).filter(Category.id == exercise_data.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Only update fields that were actually provided in the request
    update_fields = exercise_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return exercise


@exercise_router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # only admins can delete exercises
):
    """Deletes an exercise by its ID. Requires admin role."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    db.delete(exercise)
    db.commit()
