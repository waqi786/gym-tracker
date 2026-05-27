"""
Seed script to populate the database with sample users, categories, and exercises.
Run: `python seed.py` from the project folder.
"""
from database import create_tables, SessionLocal
from auth import hash_password
from models import User, Category, Exercise, TrainingSession, ExerciseTrainingSession
from datetime import datetime


def seed():
    """Create tables and seed initial data."""
    create_tables()
    db = SessionLocal()
    try:
        # Create admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(username="admin", hashed_password=hash_password("admin123"), role="admin")
            db.add(admin)

        # Create a basic user
        user1 = db.query(User).filter(User.username == "user1").first()
        if not user1:
            user1 = User(username="user1", hashed_password=hash_password("user123"), role="basic")
            db.add(user1)

        db.commit()

        # Create categories
        categories = ["Chest", "Back", "Legs", "Arms", "Cardio"]
        created_categories = {}
        for cat_name in categories:
            cat = db.query(Category).filter(Category.name == cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.add(cat)
                db.commit()
                db.refresh(cat)
            created_categories[cat_name] = cat.id

        # Create sample exercises (10) across categories
        sample_exercises = [
            ("Bench Press", "Barbell bench press for chest", "Chest"),
            ("Push Ups", "Bodyweight push ups", "Chest"),
            ("Pull Ups", "Wide-grip pull ups", "Back"),
            ("Deadlift", "Conventional deadlift", "Back"),
            ("Squat", "Barbell back squat", "Legs"),
            ("Lunges", "Walking lunges", "Legs"),
            ("Bicep Curl", "Dumbbell curls", "Arms"),
            ("Tricep Dip", "Bodyweight dips", "Arms"),
            ("Treadmill", "Treadmill running", "Cardio"),
            ("Rowing", "Rowing machine", "Cardio"),
        ]

        for name, desc, cat_name in sample_exercises:
            existing = db.query(Exercise).filter(Exercise.name == name).first()
            if not existing:
                exercise = Exercise(name=name, description=desc, category_id=created_categories[cat_name])
                db.add(exercise)

        db.commit()

        # Create two sample training sessions for user1 on fixed dates
        user_obj = db.query(User).filter(User.username == "user1").first()
        if user_obj:
            session_dates = [
                (datetime(2026, 5, 27, 10, 0), 45),
                (datetime(2026, 5, 26, 15, 30), 30)
            ]
            created_sessions = []
            for started_at_value, duration_value in session_dates:
                existing_session = db.query(TrainingSession).filter(
                    TrainingSession.owner_username == user_obj.username,
                    TrainingSession.started_at == started_at_value
                ).first()
                if not existing_session:
                    existing_session = TrainingSession(
                        started_at=started_at_value,
                        duration=duration_value,
                        owner_username=user_obj.username
                    )
                    db.add(existing_session)
                    db.commit()
                    db.refresh(existing_session)
                created_sessions.append(existing_session)

            # Add exercise-session links with repetitions, levels, and notes
            exercise_map = {exercise.name: exercise for exercise in db.query(Exercise).all()}
            links = [
                ("Bench Press", created_sessions[0].id, 8, 60.0, "Felt strong"),
                ("Bicep Curl", created_sessions[0].id, 12, 12.5, "Slow negatives"),
                ("Squat", created_sessions[1].id, 5, 80.0, "Working on depth"),
                ("Deadlift", created_sessions[1].id, 3, 120.0, "Heavy triples")
            ]

            for exercise_name, session_id, repetitions, level_value, notes_text in links:
                exercise_obj = exercise_map.get(exercise_name)
                if not exercise_obj:
                    continue
                existing_link = db.query(ExerciseTrainingSession).filter(
                    ExerciseTrainingSession.exercise_id == exercise_obj.id,
                    ExerciseTrainingSession.training_session_id == session_id
                ).first()
                if not existing_link:
                    link = ExerciseTrainingSession(
                        exercise_id=exercise_obj.id,
                        training_session_id=session_id,
                        num_repetitions=repetitions,
                        level=level_value,
                        notes=notes_text
                    )
                    db.add(link)
            db.commit()

        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
