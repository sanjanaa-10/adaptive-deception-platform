# Adaptive Deception & Detection Platform — Backend

FastAPI + PostgreSQL backend for the honeypot dashboard. This is a working
scaffold: real endpoints, real DB models, JWT auth — plug your existing
detection logic into `app/routers/events.py`.

## 1. Setup

```bash
# start Postgres
docker compose up -d

# create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# copy env file and edit SECRET_KEY
cp .env.example .env

# create your first admin login
python create_admin.py

# run the API
uvicorn app.main:app --reload
```

API docs (auto-generated, great for demos): http://localhost:8000/docs

## 2. Project structure

```
app/
  main.py          # FastAPI app, mounts all routers
  database.py      # DB connection/session
  models.py        # SQLAlchemy tables (decoys, sessions, events, alerts...)
  schemas.py       # Pydantic request/response validation
  auth.py          # password hashing + JWT
  routers/
    auth_router.py # POST /auth/login
    decoys.py      # CRUD for honeypot decoys + /adapt trigger
    events.py      # POST /events (your sensors push here) + sessions
    alerts.py       # list/resolve alerts
    stats.py       # dashboard overview + timeseries for charts
```

## 3. Where YOUR existing honeypot logic plugs in

- Your detection/logging code should call `POST /events` whenever it sees a
  connection attempt, command, or file access — pass `decoy_id`,
  `attacker_ip`, `event_type`, `payload`, and a `risk_score` (0.0–1.0).
- If `risk_score >= 0.7`, an alert is auto-created. Tune this threshold or
  replace it with your own ML/rule-based scoring in `app/routers/events.py`.
- The adaptive part lives in `POST /decoys/{id}/adapt` — this is intentionally
  a stub. Fill it with your actual "how the decoy changes" logic (e.g.
  switch from low-interaction to high-interaction mode when recon is
  detected).

## 4. Next steps (use Claude Code for these, one at a time)

1. "Connect my existing honeypot Python script to call `POST /events` when it
   detects a connection."
2. "Add pagination to the `/events` and `/sessions` endpoints."
3. "Add a `require_auth` dependency that protects `/decoys`, `/alerts`, and
   `/stats` routes with the JWT from `/auth/login`."
4. "Build a React dashboard that shows `/stats/overview` as cards, a live
   table from `/events`, and a chart from `/stats/timeseries`."
5. "Write a Dockerfile for this FastAPI app so I can deploy it to Render."

## 5. Deployment (once it works locally)

- Push this repo to GitHub.
- Deploy Postgres + this API on Render or Railway (free tier).
- Point your React frontend (deployed on Vercel) at the live API URL.
- Update the `CORS` origins in `app/main.py` to your real frontend URL.
