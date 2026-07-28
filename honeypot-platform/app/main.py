from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth_router, decoys, events, alerts, stats

# Creates tables if they don't exist yet (fine for a project; use Alembic
# migrations later if you want to show more DB maturity)
Base.metadata.create_all(bind=engine)

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
