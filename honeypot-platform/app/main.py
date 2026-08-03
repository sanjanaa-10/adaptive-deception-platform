from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import Base, engine, SessionLocal
from app.routers import auth_router, decoys, events, alerts, stats
from app import models, auth

# Creates tables if they don't exist yet (fine for a project; use Alembic
# migrations later if you want to show more DB maturity)
Base.metadata.create_all(bind=engine)


def create_admin_from_env():
    """
    Creates an admin user on startup if ADMIN_USERNAME and ADMIN_PASSWORD
    env vars are set and no user with that username exists yet.
    """
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        return

    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.username == username).first()
        if not existing:
            user = models.User(username=username, password_hash=auth.hash_password(password), role="admin")
            db.add(user)
            db.commit()
            print(f"[startup] Created admin user '{username}' from environment variables.")
        else:
            print(f"[startup] Admin user '{username}' already exists, skipping creation.")
    finally:
        db.close()


create_admin_from_env()

app = FastAPI(title="Adaptive Deception & Detection Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend URL before deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(decoys.router)
app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"status": "Honeypot platform API is running"}