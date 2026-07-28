# Adaptive Deception & Detection Platform

A full-stack cybersecurity honeypot platform that lures attackers into fake
services, logs and scores their behavior in real time, and **adapts its
deception strategy** based on how malicious an attacker's actions look —
switching from a bare-bones fake shell to one that surfaces convincing fake
sensitive data once an attacker is detected doing something dangerous.

Built to explore how deception-based defense (honeypots) can be made
adaptive rather than static, using real-time risk scoring to drive behavior
changes instead of a fixed, easily-fingerprinted decoy.

## What it does

1. A fake SSH service (`honeypot-platform/sensor`) accepts real connections
   and logs every login attempt and command an attacker runs
2. Each action is scored for risk using rule-based heuristics (weak
   credentials, recon commands, destructive/exfiltration commands)
3. High-risk behavior automatically triggers two things:
   - An **alert** in the backend
   - The decoy **adapting** into a higher-interaction mode, surfacing fake
     sensitive files to keep the attacker engaged and gather more intel
4. A live dashboard (`honeypot-dashboard`) visualizes all of this in real
   time — a streaming terminal of attacker activity, decoy status, an
   attack-volume chart, and an alerts feed

## Architecture
sensor/ (fake SSH honeypot, Python)
│ logs connections, scores risk
▼
backend/ (FastAPI + PostgreSQL)
│ stores decoys, sessions, events, alerts
│ exposes REST API + JWT auth
▼
frontend/ (React + Tailwind)
live dashboard, polls backend every 3s
**Stack:** FastAPI, PostgreSQL, SQLAlchemy, JWT auth · React, Tailwind CSS,
Recharts · Docker (Postgres)

## Why this matters

Most honeypots are static — once an attacker fingerprints them, they're
useless. This project's core idea is that a decoy's behavior should change
based on *what the attacker is doing*, using the same signal (risk scoring)
to both alert defenders and adjust deception in real time.

## Project structure

- [`honeypot-platform/`](./honeypot-platform) — backend API, database
  models, and the honeypot sensor. See its README for setup instructions.
- [`honeypot-dashboard/`](./honeypot-dashboard) — the live monitoring
  dashboard. See its README for setup instructions.

## Running it locally

See the README in each subfolder for full setup steps. Quick summary:

\`\`\`bash
# 1. Backend
cd honeypot-platform
docker compose up -d          # starts Postgres
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python create_admin.py
uvicorn app.main:app --reload

# 2. Sensor (separate terminal)
python sensor/honeypot_sensor.py

# 3. Frontend (separate terminal)
cd ../honeypot-dashboard
npm install
npm run dev
\`\`\`

## Possible next steps

- Move risk scoring from rule-based heuristics to a trained ML classifier
- Support multiple simultaneous decoy types (HTTP, FTP, not just SSH)
- Deploy publicly (Render/Railway for backend, Vercel for frontend)