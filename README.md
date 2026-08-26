# Budgy

A shared budget and savings-goal planner. Multiple people can join the same
budget and contribute together, add money in different currencies, log
savings, and track progress toward the goal with a live chart.

**Live demo:** https://budgy-r3vf.onrender.com

## Features

- Email + username registration, JWT authentication
- Create budgets, join one by invite code or budget ID (many-to-many membership)
- Contribute in any supported currency (TRY, EUR, USD, GBP, CHF) — automatically
  converted at the live exchange rate via the [Frankfurter API](https://frankfurter.dev)
- "I saved" feature: log money you didn't spend as a positive contribution
- Animated progress chart and a detailed contribution history table
- Mark a budget complete or delete it; completed goals live in their own tab

## Tech stack

- **Backend:** FastAPI, SQLAlchemy (async), Pydantic, JWT (PyJWT), bcrypt
- **Database:** SQLite in development, PostgreSQL in production (swap `DATABASE_URL`, no code changes)
- **Frontend:** Vanilla HTML/CSS/JS (no build step), Chart.js — served by the backend from the same origin

## Local setup

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env
.venv/Scripts/uvicorn app.main:app --reload
```

Open `http://localhost:8000/`.

## Project structure

```
app/
  main.py            FastAPI app; wires up the routers and the static frontend
  models.py          SQLAlchemy models (User, Budget, BudgetMember, Transaction)
  schemas.py         Pydantic schemas
  auth.py            JWT issuance/verification and password hashing
  database.py        Async engine/session, DATABASE_URL normalization
  currency.py        Live exchange-rate conversion
  budget_access.py   Shared membership/ownership checks
  routers/           auth, budgets, and transactions endpoints
frontend/
  *.html, css/, js/  Static pages (login, dashboard, budget detail)
```
