"""
Router for authentication endpoints.
Handles user registration and login (JWT token generation).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from auth import hash_password, verify_password, create_access_token

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user with a username, password, and role.
    Role can be 'basic' (default) or 'admin'.
    """
    # Check if the username is already taken
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Validate that the role is one of the allowed values
    if user_data.role not in ("admin", "basic"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'admin' or 'basic'"
        )

    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth_router.post("/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Logs in a user and returns a JWT access token.
    Send this token in the Authorization header as: Bearer <token>
    """
    # Look up the user by username
    user = db.query(User).filter(User.username == login_data.username).first()

    # Verify the user exists and the password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create a token that carries the username as the subject
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return TokenResponse(access_token=access_token, token_type="bearer")
