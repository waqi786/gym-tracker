"""
Authentication utilities using JWT (JSON Web Tokens).
Handles password hashing, token creation, and user verification.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User

# Secret key used to sign JWT tokens - in production, store this in an environment variable
SECRET_KEY = "gym-tracker-super-secret-key-2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60  # tokens expire after 1 hour

# Password hashing context using bcrypt
# Set bcrypt rounds explicitly to ensure compatibility and control cost
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# This tells FastAPI where to look for the token in requests (Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain_password: str) -> str:
    """Hash a password with bcrypt.

    Bcrypt enforces a 72-byte input limit. Truncate the password to 72 characters
    before hashing so that hashing and verification behave consistently when
    different passlib/bcrypt versions are present.
    """
    # Truncate to 72 bytes max because bcrypt has a hard limit
    truncated_password = plain_password[:72]
    return password_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against the stored bcrypt hash.

    Apply the same truncation used during hashing so both operations match.
    """
    # Apply same truncation during verification so it matches
    truncated_password = plain_password[:72]
    return password_context.verify(truncated_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token with the given payload data.
    Adds an expiry time to the token before signing it.
    """
    payload = data.copy()
    expire_time = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expire_time})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency that extracts and validates the current user from the JWT token.
    Raises 401 if the token is missing, expired, or invalid.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token and extract the username
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    # Look up the user in the database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_error

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures only admin users can access the protected route.
    Raises 403 if the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action"
        )
    return current_user
