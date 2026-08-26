from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _prepare_database_url(url: str) -> tuple[str, dict]:
    if "sqlite" in url:
        return url, {"check_same_thread": False}

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    connect_args = {}
    if query.pop("sslmode", None) == "require":
        connect_args["ssl"] = "require"
    clean_url = urlunsplit(parts._replace(query=urlencode(query)))

    return clean_url, connect_args


database_url, connect_args = _prepare_database_url(settings.database_url)
engine = create_async_engine(database_url, connect_args=connect_args, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
