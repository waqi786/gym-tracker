"""
Main entry point for the Gym Management Tracker REST API.
Registers all routers and initializes the database on startup.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import create_tables
from routers.auth_router import auth_router
from routers.exercise_router import exercise_router
from routers.session_router import session_router
from routers.relationship_router import relationship_router
from routers.category_router import category_router

# Create the FastAPI application instance
app = FastAPI(
    title="Gym Management Tracker",
    description="REST API for tracking gym exercises and training sessions.",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    """Creates all database tables when the application starts up."""
    create_tables()



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler to ensure errors return JSON rather than a server crash.

    This returns a simple JSON payload with a 500 status code and an error message.
    """
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": str(exc)})


# Register all routers with the application
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(exercise_router)
app.include_router(session_router)
app.include_router(relationship_router)


@app.get("/")
def root():
    """Root endpoint - just confirms the API is running."""
    return {"message": "Gym Management Tracker API is running. Visit /docs for the full API documentation."}
