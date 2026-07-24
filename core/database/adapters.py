from typing import Protocol, Any, List, Optional
from core.config.settings import DatabaseSettings
from core.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseAdapter(Protocol):
    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        ...

    async def fetch_one(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        ...

    async def fetch_all(self, query: str, *args: Any, **kwargs: Any) -> List[Any]:
        ...

    async def health_check(self) -> bool:
        ...


class SQLiteAdapter:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._engine = None

    async def connect(self) -> None:
        from sqlalchemy.ext.asyncio import create_async_engine
        self._engine = create_async_engine(f"sqlite+aiosqlite:///{self.dsn}", echo=False)
        logger.info("SQLite adapter connected", dsn=self.dsn)

    async def disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(text(query), kwargs or {})
            await session.commit()
            return result

    async def fetch_one(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(text(query), kwargs or {})
            return result.mappings().first()

    async def fetch_all(self, query: str, *args: Any, **kwargs: Any) -> List[Any]:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(text(query), kwargs or {})
            return list(result.mappings().all())

    async def health_check(self) -> bool:
        try:
            await self.fetch_one("SELECT 1")
            return True
        except Exception:
            return False


class PostgreSQLAdapter:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._engine = None

    async def connect(self) -> None:
        from sqlalchemy.ext.asyncio import create_async_engine
        self._engine = create_async_engine(self.dsn, echo=False, pool_size=10, max_overflow=20)
        async with self._engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL adapter connected")

    async def disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(text(query), kwargs or {})
            await session.commit()
            return result

    async def fetch_one(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(text(query), kwargs or {})
            return result.mappings().first()

    async def fetch_all(self, query: str, *args: Any, **kwargs: Any) -> List[Any]:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(text(query), kwargs or {})
            return list(result.mappings().all())

    async def health_check(self) -> bool:
        try:
            await self.fetch_one("SELECT 1")
            return True
        except Exception:
            return False


def get_database_adapter(settings: DatabaseSettings) -> DatabaseAdapter:
    if settings.postgres_url:
        return PostgreSQLAdapter(settings.postgres_url)
    return SQLiteAdapter(settings.sqlite_fallback)
