# Honeynet Dashboard (Frontend)

React + Tailwind dashboard for the Adaptive Deception & Detection Platform.
Connects to your FastAPI backend at `http://localhost:8000`.

## Setup

```bash
npm install
npm run dev
```

Open the URL it prints (usually http://localhost:5173).

## Before you can log in

Make sure your backend is running (`uvicorn app.main:app --reload` in the
`honeypot-platform` folder) and you've already created an admin user with
`python create_admin.py`. Use those same credentials to log into this
dashboard.

## What you'll see

- **Live Threat Terminal** — real attacker commands streaming in as your
  sensor logs them (run `python sensor/honeypot_sensor.py` and
  `python sensor/test_attacker.py` in the backend project to generate
  activity)
- **Decoy status** — shows each decoy's current mode; switches from
  low-interaction to high-interaction (in red) once adaptation triggers
- **Attack volume chart** — events per day, last 7 days
- **Alerts feed** — high-risk events, with a Resolve button
- **Top attackers** — most persistent IPs by session count

The dashboard polls the backend every 3 seconds, so leave your sensor
running and watch it update live during a demo.

## Next steps for deployment

- Deploy this with Vercel (`vercel deploy` after installing the Vercel CLI,
  or connect the GitHub repo on vercel.com)
- Before deploying, change `BASE_URL` in `src/api.js` from
  `http://localhost:8000` to your deployed backend's URL
- Update CORS in the backend's `app/main.py` to allow your deployed
  frontend's URL instead of `*`
