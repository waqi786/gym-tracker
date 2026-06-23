# Gym Tracker API

A professional FastAPI-based REST API for managing gym training data. This project tracks categories, exercises, user sessions, and exercise-to-session relationships.

## Quickstart:

1. Create and activate a Python virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
# or
.venv\Scripts\activate.bat  # Command Prompt
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the database and run the app:

```bash
python -c "from database import create_tables; create_tables()"
uvicorn main:app --reload
```

4. Seed sample data (optional)

```bash
python seed.py
```

## Seeded accounts

- `admin` / `admin123` (admin)
- `user1` / `user123` (basic user)

## API Overview

### Authentication
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login and receive a JWT access token

### Categories
- `GET /categories/` — List categories (`?skip=&limit=`)
- `POST /categories/` — Create a category (admin only)
- `DELETE /categories/{id}` — Delete a category (admin only)

### Exercises
- `GET /exercises/` — List exercises (`?skip=&limit=&category_id=`)
- `GET /exercises/{id}` — Get exercise details
- `POST /exercises/` — Create an exercise (admin only)
- `PUT /exercises/{id}` — Update an exercise (admin only)
- `DELETE /exercises/{id}` — Delete an exercise (admin only)

### Training Sessions
- `GET /training-sessions/` — List current user's sessions (`?skip=&limit=&date=YYYY-MM-DD`)
- `GET /training-sessions/{id}` — Get a session (owner only)
- `POST /training-sessions/` — Create a session
- `PUT /training-sessions/{id}` — Update a session (owner only)
- `DELETE /training-sessions/{id}` — Delete a session (owner only)
- `GET /training-sessions/{id}/summary` — Session details with exercises and notes

### Exercise-Session Relationships
- `GET /exercise-sessions/session/{session_id}` — List exercises in a session
- `GET /exercise-sessions/{id}` — Get exercise-session link
- `POST /exercise-sessions/` — Add exercise to a session
- `PUT /exercise-sessions/{id}` — Update exercise data
- `DELETE /exercise-sessions/{id}` — Remove exercise from a session

## Notes

- Use JWT bearer token from `/auth/login` in `Authorization: Bearer <token>`.
- Input validation is enforced via Pydantic schemas.
- Errors return consistent JSON responses.

## Dependencies

See `requirements.txt` and install with:

```bash
pip install -r requirements.txt
```

## License

MIT
