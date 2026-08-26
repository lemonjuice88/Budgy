from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_models
from app.routers import auth, budgets, transactions

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience only: creates tables from the models if they don't exist yet.
    # Use Alembic migrations instead of this once you move to PostgreSQL/production.
    await init_models()
    yield


app = FastAPI(title="Budgy API", version="1.0.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(budgets.router)
app.include_router(transactions.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Mounted last, at the root: API routes above always match first, anything
# else (/, /login.html, /dashboard.html, ...) falls through to the static
# frontend. Same-origin, so no CORS setup is needed between them.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
